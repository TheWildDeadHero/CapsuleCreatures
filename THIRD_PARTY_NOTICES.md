# Third-party notices: CapsuleCreatures

This umbrella, the engine (`engine/`) and the toolkit (`toolkit/`) are licensed
under the Mozilla Public License 2.0 (`LICENSE`). Each submodule lists the
third-party parts it uses in its own notices file:

- `engine/THIRD_PARTY_NOTICES.md` (and `engine/THIRD_PARTY_NOTICES.newlib.txt`):
  SDL2 (zlib), libgba (LGPL with a static-linking exception), devkitARM's
  startup code (MPL-2.0), newlib, the GCC and MinGW-w64 runtimes, KallistiOS
  (Dreamcast builds) and mGBA (installed as a tool, not shipped);
- `toolkit/THIRD_PARTY_NOTICES.md`: Qt for Python / Qt 6 (PySide6, LGPL-3.0,
  with what the one-folder studio downloads must ship), Python, the bundler, and
  the toolchains and tools the installers set up (devkitPro, mGBA, SDL2).

| Part | Licence | Where it matters |
|---|---|---|
| SDL2 | zlib | desktop builds (linked statically) |
| libgba (devkitPro) | LGPL with a static-linking exception | every GBA ROM: state "based in part on the work of devkitPro (https://devkitpro.org)" |
| newlib | BSD-style notices | every GBA ROM |
| KallistiOS | KOS License (BSD-style) | Dreamcast builds |
| PySide6 / Qt 6 | LGPL-3.0 | the studio; the prebuilt one-folder downloads |
| mGBA | MPL-2.0 | installed by the installers to run ROMs; not shipped |

The GBA builds are based in part on the work of devkitPro (https://devkitpro.org).
