# Shared by the umbrella's root launchers (sourced, not run): the folders, the submodules' presence check and the
# Python that starts the toolkit. Everything is found relative to the launcher, so the checkout can live anywhere.
# shellcheck shell=sh

root=$(cd "$(dirname "$0")" && pwd)
toolkit="$root/toolkit"
engine="$root/engine"

# Stops with a hint when a submodule is not checked out.
# $1: the submodule's folder, $2: a file it must hold
need_submodule() {
   if [ ! -f "$root/$1/$2" ]; then
      echo "error: $1/ is not checked out; run: git submodule update --init --recursive" >&2
      exit 1
   fi
}

# Prints a Python 3 command to start the toolkit with (toolkit/env.py hands over to a newer one when needed).
find_python() {
   for py in python3 python; do
      if command -v "$py" >/dev/null 2>&1; then
         echo "$py"
         return 0
      fi
   done
   echo "error: Python 3.10 or later is needed; run ./setup" >&2
   return 1
}

# Prints the toolkit environment's interpreter (D-35: one environment for every script), else a system Python 3.
check_python() {
   if [ -x "$toolkit/.venv/bin/python" ]; then
      echo "$toolkit/.venv/bin/python"
   else
      find_python
   fi
}

# Runs one of the toolkit's tools in its environment (toolkit/env.py run; the first run creates it).
# $1: the tool's name (toolkit/env.py TOOLS), then its arguments
toolkit_run() {
   need_submodule toolkit toolkit/env.py
   py=$(find_python) || exit 1
   tool=$1
   shift
   exec "$py" "$toolkit/toolkit/env.py" run "$tool" "$@"
}
