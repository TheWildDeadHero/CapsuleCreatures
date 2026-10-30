# CapsuleCreatures

An engine and toolkit for monster-capture games that run on modern systems
and on the Game Boy Advance. One codebase builds a GBA ROM and desktop
programs for Linux, Windows and macOS, and they all show the same picture.
The Studio edits a game's worlds, maps, scripts, sprites, sounds and battle
rules in one window.

The project holds no third-party game content and needs none. It comes with
the **Starter** sample: a small battle game with its own creatures, numbers
and simple-shape art, which new games copy.

**New here? Read [Getting started](docs/GETTING_STARTED.md).** It goes from a
download or a clean clone to the samples running on a GBA emulator, a flash
cart and your desktop.

![The Studio's World page](docs/images/studio_world.png)

## The three repositories

| Repository | Path here | What it holds |
|---|---|---|
| [`CapsuleCreatures`](https://github.com/TheWildDeadHero/CapsuleCreatures) | this one | launchers for every tool, the getting-started guide, the release workflow |
| [`CapsuleCreatures_Engine`](https://github.com/TheWildDeadHero/CapsuleCreatures_Engine) | `engine/` | the runtime engine (C++20 on CMake; GBA, desktop, headless, Dreamcast), its asset compilers, tests and the Starter sample |
| [`CapsuleCreatures_Toolkit`](https://github.com/TheWildDeadHero/CapsuleCreatures_Toolkit) | `toolkit/` | the Studio and its editors, the command-line tools, the machine installers and the toolkit's Python environment |

`engine/` and `toolkit/` are git submodules: clone with
`--recurse-submodules`.

## Downloads

Each release on the
[Releases page](https://github.com/TheWildDeadHero/CapsuleCreatures/releases)
has:

| Download | Linux x86_64 | Windows x64 | macOS (universal) | GBA |
|---|---|---|---|---|
| The Studio, ready to run | `capsule-studio-<version>-linux-x86_64.tar.gz` | `capsule-studio-<version>-windows-x64.zip` | `capsule-studio-<version>-macos-universal2.zip` | |
| The samples (Starter Battle, Map Sandbox) | `capsule-samples-<version>-linux-x86_64.tar.gz` | `capsule-samples-<version>-windows-x64.zip` | `capsule-samples-<version>-macos-universal.zip` | `capsule-samples-<version>-gba.zip` |

The downloads are not code-signed; [Getting started](docs/GETTING_STARTED.md#a2-open-the-studio)
says how to open them. Building your own changes needs the full install
(`./setup`), also in the guide.

## Where to start

| I want to... | Read |
|---|---|
| try it without installing anything | [Getting started, route A](docs/GETTING_STARTED.md#route-a-the-prebuilt-downloads) |
| build for GBA and desktop | [Getting started, route B](docs/GETTING_STARTED.md#route-b-the-full-install) |
| learn the Studio and its editors | [Toolkit user guide](https://github.com/TheWildDeadHero/CapsuleCreatures_Toolkit/blob/main/docs/USER_GUIDE.md) |
| read about the engine's formats and systems | [Engine documentation](https://github.com/TheWildDeadHero/CapsuleCreatures_Engine/blob/main/README.md#documentation) |
| see what changed | [CHANGELOG.md](CHANGELOG.md) |

## Launchers

Run them from anywhere; they find the submodules beside themselves.

```
./setup [--dry-run]        # machine setup: toolchains and the toolkit environment (toolkit/install/install.sh)
./studio [project.json]    # the Studio, every editor in one window
./map-editor world.json    # one editor on its own (also scene-editor, battle-editor, battle-structure,
                           #   battle-logic, encounter-editor, event-editor, object-editor, location-editor,
                           #   script-editor, project-settings, audio-editor)
./capsule-studio --help    # the command-line tools
./build [PRESET] [--test]  # the engine with a CMake preset (default desktop-debug), optionally its tests
./build PRESET --game DIR  # a game (DIR/reference/project.json, e.g. a New game) into DIR/build/PRESET/
./check                    # the engine's and the toolkit's static checks (principles, style, code maps)
```

On Windows use `setup.cmd` (the PowerShell installer), `studio.cmd`,
`map-editor.cmd`, ..., `build.cmd` (default preset `windows-debug`) and
`check.cmd` (the principle check needs Git Bash or MSYS2's `bash`). Build
from the MSYS2 UCRT64 shell, which has the compilers.

The editor launchers run `toolkit/toolkit/env.py run <tool>`: the first run
creates the toolkit's Python environment (`toolkit/.venv`) from its pinned
requirements, so a fresh checkout needs no manual step. The installers and
the environment script stay in the toolkit; these launchers only call them.
Each launcher prints its usage with `--help` (the editors pass `--help` to
the tool).

## Contributing

Changes to the engine or the toolkit are made and committed inside `engine/`
or `toolkit/`; [docs/WORKSPACE.md](docs/WORKSPACE.md) shows how the three
repositories fit together. Before sending a change, run `./check` and
`./build headless --test`. The engine's
[contributing notes](https://github.com/TheWildDeadHero/CapsuleCreatures_Engine/blob/main/docs/CONTRIBUTING.md)
give the code conventions.

## Licence and credits

CapsuleCreatures (this umbrella, the engine and the toolkit) is licensed
under the Mozilla Public License 2.0: see [`LICENSE`](LICENSE).
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) lists the third-party parts
the builds and the studio use, with their licences.

The GBA builds are based in part on the work of devkitPro
(https://devkitpro.org): they link libgba and devkitARM's startup code.
Desktop builds link SDL2 (https://libsdl.org); the studio uses Qt for Python
(PySide6, LGPL-3.0).
