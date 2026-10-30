#!/usr/bin/env python3
"""!Checks a release tag against D-10's calendar version format.

A release tag is the version itself: YYYY.MM.DD.MMMM, the UTC date and the
minutes since 00:00 UTC (0000-1439), zero-padded (2026.10.31.0930). The rule
is the toolkit's own (toolkit/editor/capsule_studio/plugins/versions.py,
parse()); this script loads that one file by path, so the release workflow and
the studio can never disagree on what a version is.

Usage: check_version_tag.py TAG [--toolkit TOOLKIT_ROOT]

Prints the version and exits 0 when the tag is valid; prints why and exits 1
when it is not. With GITHUB_OUTPUT set, also writes `version=<tag>` there.
Standard library only.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

## The versions module inside the toolkit checkout.
VERSIONS_FILE = Path("editor") / "capsule_studio" / "plugins" / "versions.py"
## Exit status of a malformed tag.
EXIT_MALFORMED = 1
## Exit status when the toolkit's versions module is missing.
EXIT_NO_TOOLKIT = 2


def load_versions(toolkit: Path) -> ModuleType:
   """!Loads the toolkit's versions module from its file (not its package, which imports the rest of the studio).
   @param toolkit  the toolkit checkout's root
   @return the module
   """
   path = toolkit / VERSIONS_FILE
   if not path.is_file():
      print(f"error: {path} not found; check out the submodules (git submodule update --init)", file=sys.stderr)
      sys.exit(EXIT_NO_TOOLKIT)
   spec = importlib.util.spec_from_file_location("capsule_versions", path)
   module = importlib.util.module_from_spec(spec)
   spec.loader.exec_module(module)
   return module


def main(argv: list[str] | None = None) -> int:
   """!Command-line entry point; see the module docstring.
   @param argv  arguments without the program name, or None for sys.argv
   @return exit status
   """
   p = argparse.ArgumentParser(description="Check a release tag (D-10 calendar version).")
   p.add_argument("tag", help="the tag, e.g. 2026.10.31.0930 (refs/tags/ is stripped)")
   p.add_argument("--toolkit", default="toolkit", help="the toolkit checkout (default: toolkit/)")
   args = p.parse_args(argv)

   tag = args.tag.removeprefix("refs/tags/")
   versions = load_versions(Path(args.toolkit))
   try:
      versions.parse(tag)
   except versions.VersionError as e:
      print(f"error: tag {tag!r} is not a release version: {e}", file=sys.stderr)
      return EXIT_MALFORMED
   print(tag)
   output = os.environ.get("GITHUB_OUTPUT")
   if output:
      with open(output, "a", encoding="utf-8") as f:
         f.write(f"version={tag}\n")
   return 0


if __name__ == "__main__":
   sys.exit(main())
