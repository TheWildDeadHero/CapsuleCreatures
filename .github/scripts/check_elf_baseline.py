#!/usr/bin/env python3
"""!Checks that every ELF file of an unpacked Linux download runs on the release's glibc baseline (D-40 RX).

studio-bundles.yml runs it on the Linux studio bundle, built in the manylinux_2_28 container:

   check_elf_baseline.py FOLDER --glibc-max 2.28 --base-lib /usr/lib64/libstdc++.so.6 --base-lib /lib64/libgcc_s.so.1

For each ELF file below FOLDER (executables, shared libraries, Python extension modules, Qt plugins) it reads the
version needs (readelf's .gnu.version_r section) and fails when one needs
- a glibc symbol version (GLIBC_x.y) newer than --glibc-max, or glibc's private symbols (GLIBC_PRIVATE);
- a symbol version of a --base-lib library that the base's copy does not define: for the C++ runtime
  (libstdc++.so.6: GLIBCXX_*, CXXABI_*) and libgcc_s.so.1 (GCC_*), "the base" is the copy in the build container,
  the oldest one the download supports (the bundle leaves both to the user's system, as the PySide6 wheels do).

Exit status 0 when every file passes, 1 when one fails (each failure printed as a GitHub error line). Standard
library and binutils' readelf only; Python 3.10.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

## Exit status when a file fails.
EXIT_FAILED = 1
## The first bytes of an ELF file.
ELF_MAGIC = b"\x7fELF"
## glibc's symbol versions: GLIBC_2.28 and the like.
GLIBC_VERSION = re.compile(r"GLIBC_([0-9]+(?:\.[0-9]+)+)")
## glibc's private symbol version (only glibc's own libraries may need it: they are tied to one exact glibc).
GLIBC_PRIVATE = "GLIBC_PRIVATE"
## A readelf -V line naming the file a block of version needs comes from ("000000: Version: 1  File: libc.so.6").
NEED_FILE = re.compile(r"\bFile:\s+(\S+)")
## A readelf -V line naming one version ("Name: GLIBC_2.17" in needs, "... Index: 2  Cnt: 1  Name: GCC_3.0" in
## definitions).
VERSION_NAME = re.compile(r"\bName:\s+(\S+)")
## The section header lines of readelf -V.
NEEDS_SECTION = "Version needs section"
## The version definitions section header of readelf -V.
DEFINITIONS_SECTION = "Version definition section"
## Any other section header of readelf -V (the symbol version table).
SYMBOLS_SECTION = "Version symbols section"


def version_key(text: str) -> tuple[int, ...]:
   """!Orders dotted versions numerically.
   @param text  "2.28" (or "3.4.25")
   @return (2, 28)
   """
   return tuple(int(part) for part in text.split("."))


def readelf_versions(path: Path) -> tuple[list[tuple[str, str]], set[str]]:
   """!A file's version needs and version definitions.
   @param path  an ELF file
   @return ([(needed file, version name)], {defined version names})
   """
   text = subprocess.run(["readelf", "-V", "-W", str(path)], capture_output=True, text=True, check=True).stdout
   needs: list[tuple[str, str]] = []
   defined: set[str] = set()
   section = None
   current_file = None
   for line in text.splitlines():
      if line.startswith(NEEDS_SECTION):
         section = NEEDS_SECTION
         continue
      if line.startswith(DEFINITIONS_SECTION):
         section = DEFINITIONS_SECTION
         continue
      if line.startswith(SYMBOLS_SECTION):
         section = None
         continue
      name = VERSION_NAME.search(line)
      if section == NEEDS_SECTION:
         found = NEED_FILE.search(line)
         if found:
            current_file = found.group(1)
         elif name and current_file:
            needs.append((current_file, name.group(1)))
      elif section == DEFINITIONS_SECTION and name and "Parent" not in line:
         defined.add(name.group(1))
   return needs, defined


def elf_files(folder: Path) -> list[Path]:
   """!Every regular ELF file below a folder (symbolic links are checked through their targets).
   @param folder  the unpacked download
   @return sorted paths
   """
   out = []
   for path in sorted(folder.rglob("*")):
      if path.is_symlink() or not path.is_file():
         continue
      with path.open("rb") as f:
         if f.read(len(ELF_MAGIC)) == ELF_MAGIC:
            out.append(path)
   return out


def base_definitions(libs: list[Path]) -> dict[str, set[str]]:
   """!The symbol versions each base library defines, by its file name.
   @param libs  the base libraries (the build container's libstdc++.so.6, libgcc_s.so.1)
   @return {file name: {version names}}
   """
   out = {}
   for lib in libs:
      real = lib.resolve()
      _needs, defined = readelf_versions(real)
      if not defined:
         raise SystemExit(f"::error::{lib}: no version definitions (not a shared library?)")
      out[lib.name] = defined
   return out


def check(folder: Path, glibc_max: str, bases: dict[str, set[str]]) -> int:
   """!Checks every ELF file below a folder.
   @param folder     the unpacked download
   @param glibc_max  the newest glibc symbol version allowed
   @param bases      base_definitions()
   @return exit status
   """
   files = elf_files(folder)
   if not files:
      print(f"::error::{folder}: no ELF files (wrong folder?)")
      return EXIT_FAILED
   failures = 0
   newest_glibc = "0"
   newest_base: dict[str, str] = {}
   for path in files:
      shown = path.relative_to(folder)
      needs, _defined = readelf_versions(path)
      for needed_file, name in needs:
         glibc = GLIBC_VERSION.fullmatch(name)
         if glibc:
            if version_key(glibc.group(1)) > version_key(newest_glibc):
               newest_glibc = glibc.group(1)
            if version_key(glibc.group(1)) > version_key(glibc_max):
               print(f"::error::{shown}: needs {name} from {needed_file} (newer than glibc {glibc_max})")
               failures += 1
            continue
         if name == GLIBC_PRIVATE:
            print(f"::error::{shown}: needs {GLIBC_PRIVATE} from {needed_file} (tied to one exact glibc)")
            failures += 1
            continue
         defined = bases.get(needed_file)
         if defined is None:
            continue
         if name not in defined:
            print(f"::error::{shown}: needs {name} from {needed_file}, which the base's copy does not define")
            failures += 1
         else:
            newest_base[needed_file] = max(newest_base.get(needed_file, name), name, key=suffix_key)
   print(f"{len(files)} ELF files; newest glibc symbol needed: GLIBC_{newest_glibc} (at most {glibc_max})")
   for lib, name in sorted(newest_base.items()):
      print(f"newest {lib} version needed: {name} (defined by the base)")
   if failures:
      print(f"::error::{failures} version needs are newer than the baseline")
      return EXIT_FAILED
   return 0


def suffix_key(name: str) -> tuple[str, tuple[int, ...]]:
   """!Orders version names by family, then number ("GLIBCXX_3.4.9" before "GLIBCXX_3.4.25").
   @param name  e.g. "GLIBCXX_3.4.25"
   @return (family, numbers)
   """
   family, _sep, number = name.partition("_")
   digits = tuple(int(p) for p in number.split(".") if p.isdigit())
   return family, digits


def main(argv: list[str] | None = None) -> int:
   """!Command line.
   @param argv  arguments (default: sys.argv[1:])
   @return exit status
   """
   parser = argparse.ArgumentParser(description="Check an unpacked Linux download against a glibc baseline.")
   parser.add_argument("folder", type=Path, help="the unpacked download")
   parser.add_argument("--glibc-max", required=True, help="newest glibc symbol version allowed, e.g. 2.28")
   parser.add_argument("--base-lib", type=Path, action="append", default=[],
                       help="a library the user's system provides, as the build container has it (repeat)")
   args = parser.parse_args(argv)
   return check(args.folder.resolve(), args.glibc_max, base_definitions(args.base_lib))


if __name__ == "__main__":
   sys.exit(main())
