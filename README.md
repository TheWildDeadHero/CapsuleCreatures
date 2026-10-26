# CapsuleCreatures

An engine and toolkit for monster-capture games that run on modern systems
and on the Game Boy Advance. This umbrella repository brings the two
together and gives them easy launchers:

| Path | What |
|---|---|
| `engine/` | the runtime engine, submodule [`CapsuleCreatures_Engine`](https://github.com/TheWildDeadHero/CapsuleCreatures_Engine) (C++20 on CMake; GBA, desktop, headless, Dreamcast) |
| `toolkit/` | the studio, its editors, the machine installers and the toolkit's Python environment, submodule [`CapsuleCreatures_Toolkit`](https://github.com/TheWildDeadHero/CapsuleCreatures_Toolkit) |
| `setup`, `studio`, the editors, `build`, `check` | launchers for Linux and macOS (`.cmd` twins for Windows) that call into `toolkit/` and `engine/` |
| `scripts/common.sh` | what the shell launchers share |
| `docs/WORKSPACE.md` | the workspace layout: every repository, its tier and its two checkouts |

The engine and the toolkit hold no third-party game content and need none
(D-3). Private repositories (the reference rules and game data, the
decompilation importer) live beside this one, never inside it; see
`docs/WORKSPACE.md`.

## Getting it

```
git clone --recurse-submodules https://github.com/TheWildDeadHero/CapsuleCreatures.git
# or, in an existing clone:
git submodule update --init --recursive
```

## Launchers

Run them from anywhere; they find the submodules beside themselves.

```
./setup [--dry-run]        # machine setup: toolchains and the toolkit environment (toolkit/install/install.sh)
./studio [project.json]    # the Studio, every editor in one window
./map-editor world.json    # one editor on its own (also scene-editor, battle-editor, battle-structure,
                           #   battle-logic, encounter-editor, event-editor, object-editor, location-editor,
                           #   script-editor, project-settings)
./capsule-studio --help    # the command-line tools
./build [PRESET] [--test]  # the engine with a CMake preset (default desktop-debug), optionally its tests
./check                    # the engine's and the toolkit's static checks (principles, style, code maps)
```

On Windows use `setup.cmd` (the PowerShell installer), `studio.cmd`,
`map-editor.cmd`, ..., `build.cmd` (default preset `windows-debug`) and
`check.cmd` (the principle check needs Git Bash or MSYS2's `bash`).

The editor launchers run `toolkit/toolkit/env.py run <tool>`: the first run
creates the toolkit's Python environment (`toolkit/.venv`) from its pinned
requirements, so a fresh checkout needs no manual step. The installers and
the environment script stay in the toolkit; these launchers only call them.
Each launcher prints its usage with `--help` (the editors pass `--help` to
the tool).

## Working copies

This repository is checked out twice in the workspace folder:
`CapsuleCreatures-work/` (editable: changes are made and pushed from there,
in the submodules too, after a human has reviewed every change) and
`CapsuleCreatures/` (read-only reference, updated by hand with `git pull`
and `git submodule update`). See `docs/WORKSPACE.md`.
