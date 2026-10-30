#!/usr/bin/env bash
# Copies the licence and third-party notice files that ship with every release download into one folder.
# Run from the umbrella's root by release.yml. The engine's licence is required (D-40 gate 2): without it the
# release stops here. Third-party notices are copied when they exist (RD writes them) and warned about otherwise.
# Windows programs link MinGW-w64's winpthreads statically (-static), and its MIT-style licence asks for its
# copyright and permission notice with every copy: for windows-x64 the file MSYS2's package installs is copied as
# COPYING.winpthreads.txt (run in the MSYS2 shell; the release stops when it is missing). Run this before
# package_sample.py, which checks that a Windows download carries it.
# $1: the download's folder; $2: the platform (release.yml's names; optional, only windows-x64 adds a file)
set -euo pipefail

dest=${1:?usage: copy_notices.sh DEST_DIR [PLATFORM]}
platform=${2:-}
mkdir -p "$dest"

# The arguments that are existing files (a pattern that matched nothing stays literal and is dropped). Plain loops,
# no mapfile: macOS's /bin/bash is 3.2.
licences=()
for f in engine/LICENSE engine/LICENSE.* engine/COPYING*; do
   if [ -f "$f" ]; then
      licences+=("$f")
   fi
done
notices=()
for f in engine/THIRD_PARTY* engine/NOTICE* engine/docs/THIRD_PARTY*; do
   if [ -f "$f" ]; then
      notices+=("$f")
   fi
done

if [ "${#licences[@]}" -eq 0 ]; then
   echo "::error::engine/LICENSE is missing; a release download must carry the engine's licence (D-40 gate 2)"
   exit 1
fi
cp -- "${licences[@]}" "$dest/"
if [ "${#notices[@]}" -eq 0 ]; then
   echo "::warning::no third-party notice file in engine/ (THIRD_PARTY* or NOTICE*); the download ships without one"
else
   cp -- "${notices[@]}" "$dest/"
fi

if [ "$platform" = windows-x64 ]; then
   prefix=${MINGW_PREFIX:?windows-x64 needs the MSYS2 shell (MINGW_PREFIX names its prefix, e.g. /ucrt64)}
   winpthreads=""
   # The licence folder is named after the package; MSYS2 has shipped winpthreads under both names.
   for f in "$prefix/share/licenses/winpthreads/COPYING" "$prefix/share/licenses/libwinpthread/COPYING"; do
      if [ -z "$winpthreads" ] && [ -f "$f" ]; then
         winpthreads=$f
      fi
   done
   if [ -z "$winpthreads" ] && command -v pacman > /dev/null; then
      # Otherwise ask pacman: the package that owns the static library, then the licence file in its list.
      owner=$(pacman -Qoq "$prefix/lib/libwinpthread.a" 2> /dev/null || true)
      if [ -n "$owner" ]; then
         winpthreads=$(pacman -Qlq "$owner" | grep -E '/share/licenses/[^/]+/COPYING' | head -n 1 || true)
      fi
   fi
   if [ -z "$winpthreads" ] || [ ! -f "$winpthreads" ]; then
      echo "::error::winpthreads' COPYING not found under $prefix/share/licenses (Windows downloads must ship it)"
      exit 1
   fi
   cp -- "$winpthreads" "$dest/COPYING.winpthreads.txt"
fi
ls -l "$dest"
