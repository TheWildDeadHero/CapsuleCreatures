# Workspace layout (D-37)

Every CapsuleCreatures repository is checked out twice, side by side, directly
in the workspace folder (today `~/Documents/Projects/CapsuleCreatures/`): a
read-only reference clone `<Repo>/` and an editable work clone `<Repo>-work/`
(D-37 section 3, answer 4). Changes are made in the work clone, reviewed by a
human, then committed and pushed from it; the developer pulls them into the
reference clone by hand.

```
<workspace>/
   CapsuleCreatures/                     umbrella, read-only reference
      engine/                            submodule CapsuleCreatures_Engine
      toolkit/                           submodule CapsuleCreatures_Toolkit
   CapsuleCreatures-work/                umbrella, editable (engine/ and toolkit/ edited in place and pushed)
      engine/
      toolkit/                           holds the one toolkit environment, toolkit/.venv (D-35)
   CapsuleCreatures_PocketProject/       and CapsuleCreatures_PocketProject-work/
      rules/                             the reference rules (tier 1)
      data/ titles/ tools/ reports/ schema/   garnet's game data and its tools (tier 3)
      extensions/ framework/             studio extensions (D-35) and the game parts as data (D-36)
      build/                             git-ignored: garnet.sqlite, build/titles/<title>/data exports
      .local/scraper/                    git-ignored: the scraper's run copy and its cache
   CapsuleCreatures_Pret_Importer/       and CapsuleCreatures_Pret_Importer-work/
      ref_submodules/                    the pret decompilation clones (submodules, read only)
      assets-imported/ .local/ build*/   git-ignored: imported content, the legal acknowledgment, builds
   CapsuleCreatures_Tileset_Builder/     and CapsuleCreatures_Tileset_Builder-work/
   mgba/ DEPRECATED_REFERENCE/ ProjectHeliodor/ (resources)   outside every repository
```

## Repositories and tiers

| Repository | Visibility | Tier | Holds |
|---|---|---|---|
| `CapsuleCreatures` | public | 0 | this umbrella: `engine/`, `toolkit/`, the launchers, this document |
| `CapsuleCreatures_Engine` | public | 0 | the engine; `submodules/libgba`; no decompilation, no game content |
| `CapsuleCreatures_Toolkit` | public | 0 | the studio and editors, the installers, `toolkit/env.py` (the one Python environment) |
| `CapsuleCreatures_PocketProject` | private | 1 and 3 | `rules/` (tier 1: the Gen-3 reference rules, invented content) beside garnet's proprietary game data and text (tier 3), the framework and its studio extensions |
| `CapsuleCreatures_Pret_Importer` | private | 3 | the pret importer and the Emerald target; the decompilation clones as its `ref_submodules/` |
| `CapsuleCreatures_Tileset_Builder` | private | — | the tileset builder tool (D-11), not written yet |

Nothing from a private repository is ever copied into a public one. Never
committed anywhere: `assets-imported/`, `.local/`, build folders, `.venv`, the
scraper cache, `garnet.sqlite`, packed PySide parts, `_to_delete/`.

## How the repositories find each other

Only relative paths, from each repository's own folder; an environment
variable overrides each search. Editable copies are tried first.

| Who | Looks for | Order |
|---|---|---|
| toolkit (`editor/capsule_studio/core/engine.py`) | the engine | `CAPSULE_ENGINE`; `../engine` (inside the umbrella); `../CapsuleCreatures_Engine-work`, `../CapsuleCreatures_Engine` |
| toolkit (`editor/capsule_studio/core/templates.py`) | the reference rules | `CAPSULE_REFERENCE`; `../../CapsuleCreatures_PocketProject-work/rules`, `../../CapsuleCreatures_PocketProject/rules`; the same one folder up (a standalone toolkit clone) |
| PocketProject `rules/` (`CMakeLists.txt`, `tools/engine_paths.py`) | the engine | `-DCAPSULE_ENGINE` / `CAPSULE_ENGINE`; `../../CapsuleCreatures-work/engine`, `../../CapsuleCreatures/engine`, `../../CapsuleCreatures_Engine-work`, `../../CapsuleCreatures_Engine` |
| importer (`CMakeLists.txt`, `importer/paths.py`) | the engine | `-DCAPSULE_ENGINE` / `CAPSULE_ENGINE`; `../CapsuleCreatures-work/engine`, `../CapsuleCreatures/engine`, `../CapsuleCreatures_Engine-work`, `../CapsuleCreatures_Engine` |
| importer | the reference rules | `-DCAPSULE_REFERENCE` / `CAPSULE_REFERENCE`; `../CapsuleCreatures_PocketProject-work/rules`, `../CapsuleCreatures_PocketProject/rules` |
| importer | the pret clone | named explicitly with `--pret` (usually `ref_submodules/pokeemerald`); its checks against the clone use `CAPSULE_PRET` |
| umbrella launchers | the toolkit and the engine | `toolkit/` and `engine/` beside the launcher |

The toolkit environment is `toolkit/.venv` of the umbrella checkout (or
`CAPSULE_STUDIO_VENV`). D-35's shared-environment locator for the other
repositories is a later package; until then they run with `python3`.

## First-time setup on a machine

```
git clone --recurse-submodules https://github.com/TheWildDeadHero/CapsuleCreatures.git CapsuleCreatures-work
git clone --recurse-submodules https://github.com/TheWildDeadHero/CapsuleCreatures.git CapsuleCreatures
git clone https://github.com/TheWildDeadHero/CapsuleCreatures_PocketProject.git CapsuleCreatures_PocketProject-work
git clone https://github.com/TheWildDeadHero/CapsuleCreatures_Pret_Importer.git CapsuleCreatures_Pret_Importer-work
git -C CapsuleCreatures_Pret_Importer-work submodule update --init ref_submodules/pokeemerald
CapsuleCreatures-work/setup
```

(and the read-only reference clone of each private repository the same way,
without `-work`). The old folders (`CapsuleCreatures Engine/`,
`CapsuleCreatures Studio/`, `CapsuleCreatures Reference/`,
`CapsuleCreatures Import/`, `ProjectGarnet/garnet-data*`) are retired only
after the new layout is confirmed to work (D-37 section 4 step 5).
