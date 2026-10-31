# Contributor layout

The public CapsuleCreatures release is three repositories: this umbrella and
its two submodules.

| Repository | Path in the umbrella | Holds |
|---|---|---|
| `CapsuleCreatures` | (this one) | the launchers (`setup`, `studio`, the editors, `build`, `check`), `scripts/`, `docs/` (this document, the getting-started guide, release notes) |
| `CapsuleCreatures_Engine` | `engine/` | the engine (C++20, CMake), its compilers, tests and the Starter sample; no third-party game content |
| `CapsuleCreatures_Toolkit` | `toolkit/` | the studio and its editors, the machine installers, `toolkit/env.py` (the one Python environment) |

Clone the umbrella with its submodules and run the installer:

```
git clone --recurse-submodules https://github.com/TheWildDeadHero/CapsuleCreatures.git
cd CapsuleCreatures
./setup --dry-run        # see every step first; then ./setup (setup.cmd on Windows)
```

```
CapsuleCreatures/
   engine/          submodule CapsuleCreatures_Engine
   toolkit/         submodule CapsuleCreatures_Toolkit; holds the toolkit environment, toolkit/.venv
   setup, studio, build, check, the editor launchers (.cmd twins for Windows)
   scripts/common.sh
```

Never committed anywhere: build folders, `.venv`, `assets-imported/` (any
importer's output), `.local/`, `_to_delete/`.

## Working on the code

Changes to the engine or the toolkit are made inside `engine/` or `toolkit/`
and committed in that submodule; the umbrella then records the new submodule
commits. A second, read-only checkout of the umbrella beside the one you edit
is a convenient way to compare against the last reviewed state; nothing
requires it.

## How the parts find each other

Only relative paths, from each repository's own folder; an environment
variable overrides each search.

| Who | Looks for | Order |
|---|---|---|
| toolkit (`editor/capsule_studio/core/engine.py`) | the engine | `CAPSULE_ENGINE`; `../engine` (inside the umbrella); a standalone `../CapsuleCreatures_Engine` clone |
| toolkit (`editor/capsule_studio/core/templates.py`) | optional battle templates from a reference-ruleset repository | `CAPSULE_REFERENCE` only |
| a game or rules repository's CMake | the engine | `-DCAPSULE_ENGINE=<path>` / `CAPSULE_ENGINE` (the engine works as a subproject) |
| umbrella launchers | the toolkit and the engine | `toolkit/` and `engine/` beside the launcher |

The toolkit environment is `toolkit/.venv` of the umbrella checkout (or
`CAPSULE_STUDIO_VENV`).

Private repositories (game data, reference rules) may live beside the
umbrella on a developer's machine; none of them is part of this release, and
nothing from them is copied into a public repository.
