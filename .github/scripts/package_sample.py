#!/usr/bin/env python3
"""!Puts one platform's sample download together and checks what goes in it (D-40 RS).

release.yml builds the samples' targets with one preset, then runs this from the umbrella's root:

   package_sample.py --platform P --build-dir engine/build/PRESET --version V --out dist/NAME
                     --target capsule_starter_battle --target capsule_sandbox_map [--icon-png FILE]

Per platform, for every target:
- gba: copies <target>.gba and checks its header (gbafix's complement check and fixed byte, the title, game code and
  maker of the game's reference/project.json) and its size against the manifest's cartridge target (rom.cart_mb,
  D-5; the build checks it too, cmake/gba_rom_size.cmake);
- linux-x86_64: copies the program and checks that it needs no C++ runtime library (libstdc++, libgcc_s) and no
  glibc symbol newer than --glibc-max (objdump and readelf from binutils);
- windows-x64: copies <target>.exe and checks its PE header: the GUI subsystem (no console window) and imports
  from Windows' own DLLs only (no MinGW or SDL DLL beside it); and checks that the download carries winpthreads'
  notice (WINDOWS_NOTICES: the programs link winpthreads statically, and its licence asks for the notice);
- macos-universal: makes "<Display Name>.app" (Contents/MacOS/<target>, Info.plist, an icon of simple shapes drawn
  here) and signs it ad hoc with codesign when that exists (an unsigned bundle shows as "damaged" on Apple silicon).
Then it writes README.txt from .github/release/SAMPLES_README.txt for the platform. The licence and notices come
from copy_notices.sh, which release.yml runs first (so the Windows check above sees them); the archive from
release.yml.

Exit status 0 when every check passes, 1 when one fails (each failure is printed as a GitHub error line).
Standard library only; Python 3.10.
"""
from __future__ import annotations

import argparse
import json
import math
import plistlib
import re
import shutil
import struct
import subprocess
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

## The platforms a download is made for (release.yml's matrix names).
PLATFORMS = ("gba", "linux-x86_64", "windows-x64", "macos-universal")
## The README template, relative to the umbrella's root.
README_TEMPLATE = Path(".github") / "release" / "SAMPLES_README.txt"
## The engine checkout, relative to the umbrella's root.
ENGINE = Path("engine")
## Exit status when a check fails.
EXIT_FAILED = 1

## @name Display names of the sample targets (the .app names; the README uses the same)
## @{
DISPLAY_NAMES = {"capsule_starter_battle": "Starter Battle", "capsule_sandbox_map": "Map Sandbox"}
## @}

## @name GBA cartridge header (GBATEK "GBA Cartridge Header")
## @{
GBA_TITLE = slice(0xA0, 0xAC)      ## game title, 12 bytes, upper case, zero-padded
GBA_CODE = slice(0xAC, 0xB0)       ## game code, 4 bytes
GBA_MAKER = slice(0xB0, 0xB2)      ## maker code, 2 bytes
GBA_FIXED_OFFSET = 0xB2            ## must hold GBA_FIXED_VALUE
GBA_FIXED_VALUE = 0x96
GBA_CHECKED = slice(0xA0, 0xBD)    ## the bytes the complement check sums
GBA_CHECK_OFFSET = 0xBD            ## the complement check byte
GBA_CHECK_BIAS = 0x19              ## check = -(sum + 0x19) & 0xFF
GBA_HEADER_BYTES = 0xC0
BYTE_MASK = 0xFF
BYTES_PER_MB = 1 << 20
## The D-5 cartridge sizes (MB) and the one a manifest without rom.cart_mb gets (the GBA's ROM window).
GBA_CART_SIZES_MB = (8, 16, 32)
GBA_DEFAULT_CART_MB = 32
## @}

## @name Linux checks
## @{
## The newest glibc symbol version a release program may need (the build container's glibc, manylinux_2_28).
DEFAULT_GLIBC_MAX = "2.28"
## Shared libraries a release program must not need (the C++ runtime is linked in: -static-libstdc++ -static-libgcc).
LINUX_FORBIDDEN = ("libstdc++", "libgcc_s")
## @}

## @name PE (Windows executable) header
## @{
PE_LFANEW_OFFSET = 0x3C            ## DOS header: offset of the PE signature
PE_SIGNATURE = b"PE\0\0"
COFF_BYTES = 20                    ## the COFF file header after the signature
COFF_SECTIONS_FIELD = 2            ## its NumberOfSections
COFF_OPTIONAL_FIELD = 16           ## its SizeOfOptionalHeader
SECTION_SIZES_FIELD = 8            ## a section header's VirtualSize (after the 8-byte name)
PE32_PLUS_MAGIC = 0x20B            ## optional header magic of a 64-bit program
SUBSYSTEM_OFFSET = 68              ## in the optional header
SUBSYSTEM_GUI = 2                  ## IMAGE_SUBSYSTEM_WINDOWS_GUI
SUBSYSTEM_CONSOLE = 3              ## IMAGE_SUBSYSTEM_WINDOWS_CUI
DATA_DIRS_OFFSET_PLUS = 112        ## PE32+: the data directories in the optional header
IMPORT_DIR_INDEX = 1               ## data directory 1: the import table
DATA_DIR_BYTES = 8
SECTION_BYTES = 40
IMPORT_DESCRIPTOR_BYTES = 20
IMPORT_NAME_FIELD = 12             ## the descriptor's Name RVA
## Windows' own DLLs a release program may import (lower case); "api-ms-win-*" (the UCRT) is allowed too.
WINDOWS_SYSTEM_DLLS = frozenset((
   "kernel32.dll", "user32.dll", "gdi32.dll", "shell32.dll", "ole32.dll", "oleaut32.dll", "advapi32.dll",
   "imm32.dll", "winmm.dll", "version.dll", "setupapi.dll", "cfgmgr32.dll", "msvcrt.dll", "ucrtbase.dll",
   "uuid.dll", "dinput8.dll", "dxgi.dll", "d3d9.dll", "d3d11.dll", "d3d12.dll", "xinput1_4.dll", "hid.dll",
   "dwmapi.dll", "shcore.dll", "comdlg32.dll", "ws2_32.dll", "bcrypt.dll", "ntdll.dll"))
API_SET_PREFIX = "api-ms-win-"
## @}

## Notice files a Windows download must carry (copy_notices.sh copies them): the programs link winpthreads
## statically (-static), and its MIT-style licence asks for its copyright and permission notice with every copy.
WINDOWS_NOTICES = ("COPYING.winpthreads.txt",)
## Text every such notice holds (lower case; a copyright line).
NOTICE_MARK = "copyright"

## @name macOS bundle
## @{
MACOS_MINIMUM = "10.15"            ## the engine's deployment target (CMakeLists.txt)
BUNDLE_ID_PREFIX = "io.github"     ## <prefix>.<repository owner>.capsulecreatures.<target>
## ICNS entries holding PNG images: (type, pixel size).
ICNS_ENTRIES = (("icp4", 16), ("icp5", 32), ("icp6", 64), ("ic07", 128), ("ic08", 256), ("ic09", 512),
                ("ic10", 1024), ("ic11", 32), ("ic12", 64), ("ic13", 256), ("ic14", 512))
ICNS_HEADER_BYTES = 8              ## 4-byte type + 4-byte big-endian length
## @}

## @name The icon: a two-colour capsule with two eyes on a rounded square (simple shapes, signed distances)
## @{
ICON_BACKGROUND = (0x1D, 0x2B, 0x4F)      ## deep blue tile
ICON_LEFT = (0xF2, 0x8C, 0x28)            ## the capsule's orange half
ICON_RIGHT = (0x2E, 0xC4, 0xB6)           ## its teal half
ICON_SHINE = (0xFF, 0xFF, 0xFF)           ## the highlight
ICON_TILE_INSET = 0.06                    ## tile margin, of the size (macOS icons leave a margin)
ICON_TILE_RADIUS = 0.2                    ## tile corner radius, of the size
ICON_CAPSULE_HALF_LENGTH = 0.3            ## capsule: half its length, of the size (axis)
ICON_CAPSULE_RADIUS = 0.15                ## its radius, of the size
ICON_TILT = (0.8, -0.6)                   ## capsule axis direction (cos, sin): rising to the right
ICON_SHINE_OFFSET = 0.06                  ## highlight: offset across the axis, of the size
ICON_SHINE_HALF_LENGTH = 0.16             ## its half length, of the size
ICON_SHINE_RADIUS = 0.025                 ## its radius, of the size
ICON_SHINE_ALPHA = 0.55                   ## its opacity
ICON_EYE_ALONG = 0.16                     ## the creature's two eyes on the teal half: along the axis, of the size
ICON_EYE_APART = 0.055                    ## half the distance between them, along the axis, of the size
ICON_EYE_LIFT = 0.03                      ## how far above the axis they sit, of the size
ICON_EYE_RADIUS = 0.028                   ## their radius, of the size
OPAQUE = 255
HALF = 0.5                                ## half a pixel / half the icon (the centre)
RGB = 3                                   ## colour channels before alpha
ALPHA = 3                                 ## the alpha channel's index
RGBA_BYTES = 4                            ## bytes of one RGBA pixel
SHORT_VERSION_PARTS = 3                   ## CFBundleShortVersionString: three numbers
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_RGBA = 6                              ## colour type: truecolour with alpha
PNG_DEPTH = 8
PNG_FILTER_NONE = b"\0"
PNG_COMPRESSION = 9
## @}


@dataclass
class Checks:
   """!The failures found so far."""

   failures: int = 0

   def fail(self, text: str) -> None:
      """!Prints one failure as a GitHub error line and counts it.
      @param text  what is wrong
      """
      print(f"::error::{text}")
      self.failures += 1

   def ok(self, text: str) -> None:
      """!Prints a passed check.
      @param text  what was checked
      """
      print(f"ok: {text}")


def manifest_of(target: str) -> dict:
   """!Reads a sample target's game manifest.
   @param target  the CMake target (capsule_<name>)
   @return engine/apps/<name>/reference/project.json, parsed
   """
   name = target.removeprefix("capsule_")
   return json.loads((ENGINE / "apps" / name / "reference" / "project.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------------------------- GBA


def check_gba(rom: Path, target: str, checks: Checks) -> None:
   """!Checks a ROM's header against its manifest and its size against the cartridge target.
   @param rom     the .gba file
   @param target  its CMake target
   @param checks  the failures
   """
   data = rom.read_bytes()
   if len(data) < GBA_HEADER_BYTES:
      checks.fail(f"{rom.name}: {len(data)} B is shorter than a cartridge header")
      return
   rom_cfg = manifest_of(target)["rom"]
   expect_check = -(sum(data[GBA_CHECKED]) + GBA_CHECK_BIAS) & BYTE_MASK
   if data[GBA_FIXED_OFFSET] != GBA_FIXED_VALUE or data[GBA_CHECK_OFFSET] != expect_check:
      checks.fail(f"{rom.name}: header not fixed (fixed byte 0x{data[GBA_FIXED_OFFSET]:02X}, check "
                  f"0x{data[GBA_CHECK_OFFSET]:02X}, expected 0x{expect_check:02X}); did gbafix run?")
   title = data[GBA_TITLE].rstrip(b"\0").decode("ascii", "replace")
   code = data[GBA_CODE].decode("ascii", "replace")
   maker = data[GBA_MAKER].decode("ascii", "replace")
   if (title, code, maker) != (rom_cfg["title"], rom_cfg["code"], rom_cfg["maker"]):
      checks.fail(f"{rom.name}: header {title!r} {code} {maker}, manifest {rom_cfg['title']!r} {rom_cfg['code']} "
                  f"{rom_cfg['maker']}")
   cart_mb = int(rom_cfg.get("cart_mb", GBA_DEFAULT_CART_MB))
   if cart_mb not in GBA_CART_SIZES_MB:
      checks.fail(f"{rom.name}: rom.cart_mb {cart_mb} is not a D-5 cartridge size {GBA_CART_SIZES_MB}")
   elif len(data) > cart_mb * BYTES_PER_MB:
      checks.fail(f"{rom.name}: {len(data)} B is over its {cart_mb} MB cartridge target (D-5)")
   else:
      checks.ok(f"{rom.name}: header {title!r} {code} {maker} fixed; {len(data)} B of {cart_mb} MB")


# -------------------------------------------------------------------------------------------------------- Linux


def version_key(text: str) -> tuple[int, ...]:
   """!Orders dotted versions numerically.
   @param text  "2.28"
   @return (2, 28)
   """
   return tuple(int(part) for part in text.split("."))


def check_linux(program: Path, glibc_max: str, checks: Checks) -> None:
   """!Checks a Linux program's shared libraries and glibc symbol versions.
   @param program    the executable
   @param glibc_max  the newest glibc version it may need
   @param checks     the failures
   """
   dynamic = subprocess.run(["readelf", "-d", str(program)], capture_output=True, text=True, check=True).stdout
   needed = re.findall(r"\(NEEDED\)\s+Shared library: \[([^\]]+)\]", dynamic)
   bad = [lib for lib in needed if lib.startswith(LINUX_FORBIDDEN)]
   if bad:
      checks.fail(f"{program.name}: needs {', '.join(bad)} (link with -static-libstdc++ -static-libgcc)")
   symbols = subprocess.run(["objdump", "-T", str(program)], capture_output=True, text=True, check=True).stdout
   versions = sorted(set(re.findall(r"GLIBC_([0-9]+(?:\.[0-9]+)+)", symbols)), key=version_key)
   newest = versions[-1] if versions else "none"
   if versions and version_key(newest) > version_key(glibc_max):
      checks.fail(f"{program.name}: needs glibc {newest} (newer than the release baseline {glibc_max})")
   else:
      checks.ok(f"{program.name}: needs {', '.join(needed)}; newest glibc symbol {newest} (at most {glibc_max})")


# ------------------------------------------------------------------------------------------------------ Windows


def rva_to_offset(rva: int, sections: list[tuple[int, int, int]]) -> int:
   """!Maps a relative virtual address to its file offset.
   @param rva       the address
   @param sections  (virtual address, virtual size, raw data offset) of every section
   @return the file offset
   """
   for address, size, raw in sections:
      if address <= rva < address + size:
         return raw + rva - address
   raise ValueError(f"RVA 0x{rva:X} is in no section")


def read_c_string(data: bytes, offset: int) -> str:
   """!Reads a zero-terminated ASCII string.
   @param data    the file
   @param offset  where it starts
   @return the string
   """
   return data[offset:data.index(b"\0", offset)].decode("ascii", "replace")


def pe_info(data: bytes) -> tuple[int, list[str]]:
   """!Reads a 64-bit PE program's subsystem and imported DLLs.
   @param data  the .exe
   @return (subsystem, DLL names)
   """
   pe = struct.unpack_from("<I", data, PE_LFANEW_OFFSET)[0]
   if data[pe:pe + len(PE_SIGNATURE)] != PE_SIGNATURE:
      raise ValueError("no PE signature")
   coff = pe + len(PE_SIGNATURE)
   section_count = struct.unpack_from("<H", data, coff + COFF_SECTIONS_FIELD)[0]
   optional_bytes = struct.unpack_from("<H", data, coff + COFF_OPTIONAL_FIELD)[0]
   optional = coff + COFF_BYTES
   if struct.unpack_from("<H", data, optional)[0] != PE32_PLUS_MAGIC:
      raise ValueError("not a 64-bit (PE32+) program")
   subsystem = struct.unpack_from("<H", data, optional + SUBSYSTEM_OFFSET)[0]
   import_rva = struct.unpack_from("<I", data, optional + DATA_DIRS_OFFSET_PLUS
                                   + IMPORT_DIR_INDEX * DATA_DIR_BYTES)[0]
   sections = []
   table = optional + optional_bytes
   for i in range(section_count):
      entry = table + i * SECTION_BYTES
      # Name (8), VirtualSize, VirtualAddress, SizeOfRawData, PointerToRawData
      size, address, _raw_size, raw = struct.unpack_from("<IIII", data, entry + SECTION_SIZES_FIELD)
      sections.append((address, size, raw))
   dlls = []
   if import_rva:
      descriptor = rva_to_offset(import_rva, sections)
      while True:
         name_rva = struct.unpack_from("<I", data, descriptor + IMPORT_NAME_FIELD)[0]
         if name_rva == 0:
            break
         dlls.append(read_c_string(data, rva_to_offset(name_rva, sections)))
         descriptor += IMPORT_DESCRIPTOR_BYTES
   return subsystem, dlls


def check_windows_notices(out: Path, checks: Checks) -> None:
   """!Checks that a Windows download carries the notices of what its programs link statically (copy_notices.sh).
   @param out     the download's folder
   @param checks  the failures
   """
   for name in WINDOWS_NOTICES:
      notice = out / name
      text = notice.read_text(encoding="utf-8", errors="replace") if notice.is_file() else ""
      if NOTICE_MARK not in text.lower():
         checks.fail(f"{name}: missing or without a copyright line (copy_notices.sh DEST windows-x64 copies it)")
      else:
         checks.ok(f"{name}: present")


def check_windows(program: Path, checks: Checks) -> None:
   """!Checks a Windows program's subsystem and imports.
   @param program  the .exe
   @param checks   the failures
   """
   try:
      subsystem, dlls = pe_info(program.read_bytes())
   except (ValueError, struct.error) as err:
      checks.fail(f"{program.name}: unreadable PE header ({err})")
      return
   if subsystem != SUBSYSTEM_GUI:
      kind = "console" if subsystem == SUBSYSTEM_CONSOLE else str(subsystem)
      checks.fail(f"{program.name}: subsystem {kind}, not GUI (a Release build links with -mwindows)")
   foreign = [d for d in dlls if d.lower() not in WINDOWS_SYSTEM_DLLS and not d.lower().startswith(API_SET_PREFIX)]
   if foreign:
      checks.fail(f"{program.name}: imports {', '.join(foreign)} (not part of Windows: link statically)")
   if subsystem == SUBSYSTEM_GUI and not foreign:
      checks.ok(f"{program.name}: GUI subsystem; imports {', '.join(sorted(dlls, key=str.lower))}")


# -------------------------------------------------------------------------------------------------------- macOS


def capsule_distance(px: float, py: float, ax: float, ay: float, bx: float, by: float, radius: float) -> float:
   """!Signed distance to a capsule (a segment thickened by a radius).
   @param px, py  the point
   @param ax, ay  the segment's first end
   @param bx, by  its second end
   @param radius  the thickness
   @return negative inside
   """
   dx, dy = bx - ax, by - ay
   t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
   qx, qy = px - (ax + t * dx), py - (ay + t * dy)
   return math.hypot(qx, qy) - radius


def rounded_square_distance(px: float, py: float, half: float, radius: float) -> float:
   """!Signed distance to a square with rounded corners, centred on the origin.
   @param px, py  the point
   @param half    half the side
   @param radius  the corner radius
   @return negative inside
   """
   qx, qy = abs(px) - half + radius, abs(py) - half + radius
   outside = math.hypot(max(qx, 0.0), max(qy, 0.0))
   return outside + min(max(qx, qy), 0.0) - radius


def blend(under: tuple[float, ...], colour: tuple[int, int, int], alpha: float) -> tuple[float, ...]:
   """!Draws a colour over a premultiplied RGBA pixel.
   @param under   the pixel (r, g, b, a), premultiplied, 0..1
   @param colour  the colour, 0..255
   @param alpha   its coverage, 0..1
   @return the new pixel
   """
   keep = 1.0 - alpha
   rgb = tuple(u * keep + c / OPAQUE * alpha for u, c in zip(under[:RGB], colour))
   return rgb + (under[ALPHA] * keep + alpha,)


def coverage(distance: float, pixel: float) -> float:
   """!Antialiased coverage of a shape at a pixel from its signed distance.
   @param distance  the signed distance (negative inside)
   @param pixel     one pixel's size in the same units
   @return 0..1
   """
   return max(0.0, min(1.0, HALF - distance / pixel))


def icon_png(size: int) -> bytes:
   """!Draws the icon at one size.
   @param size  width and height, pixels
   @return the PNG file
   """
   pixel = 1.0 / size
   cos_t, sin_t = ICON_TILT
   ax, ay = -ICON_CAPSULE_HALF_LENGTH * cos_t, -ICON_CAPSULE_HALF_LENGTH * sin_t
   bx, by = -ax, -ay
   # the highlight: a thin capsule along the upper side of the left half
   nx, ny = sin_t, -cos_t           # the normal pointing up (screen y grows down)
   if ny > 0:
      nx, ny = -nx, -ny
   ex, ey = nx * ICON_SHINE_OFFSET, ny * ICON_SHINE_OFFSET
   sx, sy = ex - cos_t * ICON_SHINE_HALF_LENGTH, ey - sin_t * ICON_SHINE_HALF_LENGTH
   rows = []
   for row in range(size):
      line = bytearray(PNG_FILTER_NONE)
      py = (row + HALF) * pixel - HALF
      for col in range(size):
         px = (col + HALF) * pixel - HALF
         out: tuple[float, ...] = (0.0, 0.0, 0.0, 0.0)
         tile = rounded_square_distance(px, py, HALF - ICON_TILE_INSET, ICON_TILE_RADIUS)
         out = blend(out, ICON_BACKGROUND, coverage(tile, pixel))
         body = capsule_distance(px, py, ax, ay, bx, by, ICON_CAPSULE_RADIUS)
         # the side of the capsule's middle (across its axis) chooses the half
         along = px * cos_t + py * sin_t
         out = blend(out, ICON_LEFT, coverage(max(body, along), pixel))
         out = blend(out, ICON_RIGHT, coverage(max(body, -along), pixel))
         for side in (-1.0, 1.0):
            cx = cos_t * (ICON_EYE_ALONG + ICON_EYE_APART * side) + nx * ICON_EYE_LIFT
            cy = sin_t * (ICON_EYE_ALONG + ICON_EYE_APART * side) + ny * ICON_EYE_LIFT
            eye = capsule_distance(px, py, cx, cy, cx, cy + pixel, ICON_EYE_RADIUS)
            out = blend(out, ICON_BACKGROUND, coverage(eye, pixel))
         shine = capsule_distance(px, py, sx, sy, ex, ey, ICON_SHINE_RADIUS)
         out = blend(out, ICON_SHINE, coverage(shine, pixel) * ICON_SHINE_ALPHA)
         alpha = out[ALPHA]
         if alpha > 0.0:
            line += bytes(round(min(1.0, c / alpha) * OPAQUE) for c in out[:RGB]) + bytes((round(alpha * OPAQUE),))
         else:
            line += bytes(RGBA_BYTES)
      rows.append(bytes(line))

   def chunk(kind: bytes, body: bytes) -> bytes:
      """!One PNG chunk."""
      return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

   header = struct.pack(">IIBBBBB", size, size, PNG_DEPTH, PNG_RGBA, 0, 0, 0)
   return (PNG_SIGNATURE + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(b"".join(rows), PNG_COMPRESSION))
           + chunk(b"IEND", b""))


def icns(pngs: dict[int, bytes]) -> bytes:
   """!Packs PNG images into an Apple icon file.
   @param pngs  PNG file by pixel size
   @return the .icns file
   """
   body = b"".join(kind.encode("ascii") + struct.pack(">I", ICNS_HEADER_BYTES + len(pngs[px])) + pngs[px]
                   for kind, px in ICNS_ENTRIES)
   return b"icns" + struct.pack(">I", ICNS_HEADER_BYTES + len(body)) + body


def make_app(program: Path, target: str, out: Path, version: str, owner: str, icon: bytes, checks: Checks) -> None:
   """!Makes a macOS application bundle around a program and signs it ad hoc.
   @param program  the universal executable
   @param target   its CMake target
   @param out      the download's folder
   @param version  the release version (YYYY.MM.DD.MMMM)
   @param owner    the repository owner (for the bundle identifier)
   @param icon     the .icns file
   @param checks   the failures
   """
   name = DISPLAY_NAMES.get(target, target)
   app = out / f"{name}.app"
   macos = app / "Contents" / "MacOS"
   resources = app / "Contents" / "Resources"
   macos.mkdir(parents=True)
   resources.mkdir()
   shutil.copy2(program, macos / target)
   (resources / "AppIcon.icns").write_bytes(icon)
   short = ".".join(version.split(".")[:SHORT_VERSION_PARTS])
   info = {
      "CFBundleDevelopmentRegion": "en",
      "CFBundleDisplayName": name,
      "CFBundleExecutable": target,
      "CFBundleIconFile": "AppIcon",
      "CFBundleIdentifier": f"{BUNDLE_ID_PREFIX}.{owner.lower()}.capsulecreatures.{target.replace('_', '-')}",
      "CFBundleInfoDictionaryVersion": "6.0",
      "CFBundleName": name,
      "CFBundlePackageType": "APPL",
      "CFBundleShortVersionString": short,
      "CFBundleVersion": version,
      "LSApplicationCategoryType": "public.app-category.games",
      "LSMinimumSystemVersion": MACOS_MINIMUM,
      "NSHighResolutionCapable": True,
   }
   with open(app / "Contents" / "Info.plist", "wb") as f:
      plistlib.dump(info, f)
   if shutil.which("codesign") is None:
      print(f"::warning::codesign not found: {app.name} is not signed (only a macOS runner can sign)")
      return
   # "-s -" is an ad-hoc signature: no identity, but a sealed, valid bundle (Apple silicon refuses unsigned code).
   subprocess.run(["codesign", "--force", "--sign", "-", "--timestamp=none", str(app)], check=True)
   verify = subprocess.run(["codesign", "--verify", "--strict", "--verbose=2", str(app)], capture_output=True,
                           text=True)
   if verify.returncode != 0:
      checks.fail(f"{app.name}: codesign --verify failed: {verify.stderr.strip()}")
   else:
      checks.ok(f"{app.name}: bundle made and signed ad hoc")


# ------------------------------------------------------------------------------------------------------- README


def render_readme(template: str, platform: str, version: str) -> str:
   """!Keeps the template's lines for one platform.
   @param template  .github/release/SAMPLES_README.txt
   @param platform  one of PLATFORMS
   @param version   the release version
   @return README.txt's text
   """
   lines = []
   keep = True
   for line in template.splitlines():
      if line.startswith("@#"):
         continue
      if line.startswith("@only "):
         keep = platform in line.split()[1:]
         continue
      if line == "@end":
         keep = True
         continue
      if keep:
         lines.append(line.replace("{version}", version))
   return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
   """!Puts the download together.
   @param argv  the arguments (default: sys.argv)
   @return the exit status
   """
   parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
   parser.add_argument("--platform", required=True, choices=PLATFORMS)
   parser.add_argument("--build-dir", required=True, type=Path, help="the preset's build folder")
   parser.add_argument("--version", required=True, help="the release version (names nothing; goes in README)")
   parser.add_argument("--out", required=True, type=Path, help="the download's folder (made)")
   parser.add_argument("--target", action="append", required=True, help="a sample target (repeat)")
   parser.add_argument("--glibc-max", default=DEFAULT_GLIBC_MAX, help="Linux: newest glibc symbol version allowed")
   parser.add_argument("--owner", default="capsulecreatures", help="macOS: repository owner for bundle ids")
   parser.add_argument("--icon-png", type=Path, help="also write the 1024 px icon here (for review)")
   args = parser.parse_args(argv)

   checks = Checks()
   args.out.mkdir(parents=True, exist_ok=True)
   icon = None
   if args.platform == "macos-universal" or args.icon_png:
      pngs = {px: icon_png(px) for px in sorted({px for _kind, px in ICNS_ENTRIES})}
      icon = icns(pngs)
      if args.icon_png:
         args.icon_png.write_bytes(pngs[max(pngs)])
   for target in args.target:
      if args.platform == "gba":
         rom = args.build_dir / f"{target}.gba"
         shutil.copy2(rom, args.out / rom.name)
         check_gba(args.out / rom.name, target, checks)
      elif args.platform == "linux-x86_64":
         shutil.copy2(args.build_dir / target, args.out / target)
         check_linux(args.out / target, args.glibc_max, checks)
      elif args.platform == "windows-x64":
         exe = args.build_dir / f"{target}.exe"
         shutil.copy2(exe, args.out / exe.name)
         check_windows(args.out / exe.name, checks)
      else:
         make_app(args.build_dir / target, target, args.out, args.version, args.owner, icon, checks)
   if args.platform == "windows-x64":
      check_windows_notices(args.out, checks)
   readme = render_readme(README_TEMPLATE.read_text(encoding="utf-8"), args.platform, args.version)
   (args.out / "README.txt").write_text(readme, encoding="utf-8", newline="\r\n" if args.platform == "windows-x64"
                                        else "\n")
   checks.ok(f"README.txt for {args.platform}")
   return EXIT_FAILED if checks.failures else 0


if __name__ == "__main__":
   sys.exit(main())
