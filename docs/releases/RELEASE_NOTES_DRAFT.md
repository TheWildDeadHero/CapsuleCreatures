# CapsuleCreatures YYYY.MM.DD.MMMM

The first public release of CapsuleCreatures: an engine and toolkit for
monster-capture games that run on the Game Boy Advance and on Linux, Windows
and macOS. The engine, the toolkit and this repository are licensed under the
Mozilla Public License 2.0.

New here? Read [Getting started](https://github.com/TheWildDeadHero/CapsuleCreatures/blob/main/docs/GETTING_STARTED.md).

## What's in it

- **The engine** (`CapsuleCreatures_Engine`): one C++20 codebase that builds
  GBA ROMs and desktop programs which show the same picture. Tile maps,
  encounters, map events and objects, scripts, sequences, data-driven
  battles with the game's own rules, the bag and saves, growth, audio on the
  GBA's sound hardware. No third-party game content.
- **The Starter sample**: a small battle game with its own creatures, moves,
  rules and simple-shape art, which new games copy.
- **The Studio** (`CapsuleCreatures_Toolkit`): every editor in one window
  (world and maps, assets, scripts, battle data, project settings, audio),
  the `capsule-studio` command line, extensions, and installers for the
  GBA and desktop toolchains.
- **Two sample programs**, built for every platform:
  - **Starter Battle**: battles against rivals and unowned creatures,
    recruiting, the bag and the storage boxes;
  - **Map Sandbox**: the overworld, with maps, people, signs, warps and
    field actions.

The full lists are in the changelogs: [umbrella](https://github.com/TheWildDeadHero/CapsuleCreatures/blob/main/CHANGELOG.md),
[engine](https://github.com/TheWildDeadHero/CapsuleCreatures_Engine/blob/main/CHANGELOG.md),
[toolkit](https://github.com/TheWildDeadHero/CapsuleCreatures_Toolkit/blob/main/CHANGELOG.md).

## Downloads

| Platform | The Studio | The samples |
|---|---|---|
| Linux x86_64 | `capsule-studio-YYYY.MM.DD.MMMM-linux-x86_64.tar.gz` | `capsule-samples-YYYY.MM.DD.MMMM-linux-x86_64.tar.gz` |
| Windows x64 | `capsule-studio-YYYY.MM.DD.MMMM-windows-x64.zip` | `capsule-samples-YYYY.MM.DD.MMMM-windows-x64.zip` |
| macOS (Apple silicon and Intel) | `capsule-studio-YYYY.MM.DD.MMMM-macos-universal2.zip` | `capsule-samples-YYYY.MM.DD.MMMM-macos-universal.zip` |
| Game Boy Advance | | `capsule-samples-YYYY.MM.DD.MMMM-gba.zip` |

`SHA256SUMS` lists the checksum of every file. The source of all three
repositories is tagged `YYYY.MM.DD.MMMM`.

Each download has a README with how to start it. The notices that come
with them:

- every download: `LICENSE` (MPL-2.0) and `THIRD_PARTY_NOTICES.md`;
- the samples: `THIRD_PARTY_NOTICES.newlib.txt` (the GBA's C library) and,
  for Windows, `COPYING.winpthreads.txt`;
- the Studio: `notices/QT_LGPL_NOTICE.md` (Qt and PySide6 under the LGPL-3.0,
  and how to replace them), `notices/qt/` (Qt's third-party parts),
  `notices/PYTHON-LICENSE.txt` and `notices/PYINSTALLER.md`.

The GBA builds are based in part on the work of devkitPro
(https://devkitpro.org). The desktop builds use SDL2 (https://libsdl.org).

## Opening unsigned apps

The downloads are not code-signed, so the system asks once:

- **Windows**: SmartScreen says "Windows protected your PC". Click **More
  info**, then **Run anyway**.
- **macOS**: the first open is refused. Close the message, open **System
  Settings > Privacy & Security** and click **Open Anyway** next to the
  app's name. If macOS says the app "is damaged", unzip the download with
  Finder, or run `xattr -dr com.apple.quarantine` on the app in Terminal.
- **Linux**: if a double-click does nothing, allow the file to run as a
  program (**Properties > Permissions**) or run `chmod +x` on it.

## System requirements

| | Linux | Windows | macOS |
|---|---|---|---|
| The samples | x86_64 with glibc 2.28 or newer (Debian 10, Ubuntu 20.04, Fedora 29, RHEL 8 or newer), X11 or Wayland | Windows 10 or 11, 64-bit | macOS 10.15 or newer, Apple silicon or Intel |
| The Studio | x86_64 with glibc 2.34 or newer (Ubuntu 22.04, Debian 12, Fedora 35, RHEL / AlmaLinux / Rocky Linux 9, current Arch-based systems), X11 or Wayland; on X11, the `xcb-util-cursor` library | Windows 10 or 11, 64-bit | Apple silicon or Intel, on a macOS that Qt 6.11 supports |
| Building from source | CMake 3.24+, Python 3.10+, a C/C++ compiler, devkitPro's devkitARM; `./setup` installs them | the same in MSYS2's UCRT64 environment; `setup.cmd` installs them | the same with Xcode's command-line tools and Homebrew |

The GBA ROMs run on mGBA and other accurate emulators, and on GBA hardware
from a flash cartridge (8 MB or larger; the samples do not save).

## Known limits

- **Windows and macOS are proven by CI only.** Their programs and Studio
  downloads are built and checked by the release workflow, but nobody has
  used them by hand on those systems yet. Please report what you find.
- The installers (`./setup`, `setup.cmd`) are new; each system's status is in
  `toolkit/install/SUPPORT.md`.
- **Haiku** has no Studio (there is no Qt for Python there); the installer
  sets up the desktop tools and the command line only.
- **Dreamcast** is in the source only: its presets build, but this release
  has no Dreamcast downloads.
- The next battle features (battle scripts, the battle controller and the
  scene effects kit) are not in this release; they come in a later one.
- The Studio downloads play sounds through the system's player (Qt
  Multimedia is not bundled). Building, the battle bench, audio rendering
  and GBA memory reports need the full install.
- The Studio adds a world to a game (**Studio > Add world to game...**,
  Getting started, A4), but not yet a scripts or audio file: add that key to
  the game's `reference/project.json` by hand.
