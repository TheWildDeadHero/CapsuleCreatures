# Changelog

All notable changes to the CapsuleCreatures umbrella repository. Versions are
calendar versions, `YYYY.MM.DD.MMMM` (the UTC date and the minutes since
midnight); a release tags the umbrella, the engine and the toolkit with the
same version.

## YYYY.MM.DD.MMMM: first public release

- The engine and the toolkit as submodules, with launchers for every tool
  (`setup`, `studio`, the editors, `build`, `check`; `.cmd` twins for
  Windows). `./build PRESET --game FOLDER` builds a game made with the
  Studio's New game into its own `build/<preset>/` folder.
- [Getting started](docs/GETTING_STARTED.md): from the downloads or a clean
  clone to the samples on a GBA emulator, a flash cart and the desktop, and
  (A6) a sample opened in the Studio as a project of your own, which the
  same `./build PRESET --game FOLDER` builds.
- A release workflow that builds the sample downloads (GBA, Linux x86_64,
  Windows x64, macOS universal) and the Studio downloads on a version tag.
- `LICENSE` (MPL-2.0) and `THIRD_PARTY_NOTICES.md`.

The engine's and the toolkit's changes are in
[`engine/CHANGELOG.md`](https://github.com/TheWildDeadHero/CapsuleCreatures_Engine/blob/main/CHANGELOG.md)
and [`toolkit/CHANGELOG.md`](https://github.com/TheWildDeadHero/CapsuleCreatures_Toolkit/blob/main/CHANGELOG.md).
