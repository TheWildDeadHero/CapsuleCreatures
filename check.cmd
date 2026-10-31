@echo off
rem Runs the static checks of both submodules: the engine's principle, style and code map checks (engine\tools\ci\)
rem and the toolkit's style and code map checks. The tests run in build.cmd PRESET --test.
setlocal
if "%~1"=="-h" goto help
if "%~1"=="--help" goto help
if not exist "%~dp0engine\tools\ci\check_principles.sh" goto missing
if not exist "%~dp0toolkit\toolkit\check_style.py" goto missing
set "py=python"
where py >nul 2>nul && set "py=py -3"
if exist "%~dp0toolkit\.venv\Scripts\python.exe" set "py="%~dp0toolkit\.venv\Scripts\python.exe""
set "status=0"
set "engine=%~dp0engine"
set "toolkit=%~dp0toolkit"
echo == engine principles
where bash >nul 2>nul
if %errorlevel%==0 (
   bash "%engine%\tools\ci\check_principles.sh" || set "status=1"
) else (
   echo warning: bash not found: the principle check needs Git Bash or MSYS2; skipped
)
echo == engine style
%py% "%engine%\tools\ci\check_style.py" "%engine%\src" "%engine%\include" "%engine%\apps" "%engine%\tests" "%engine%\tools" "%engine%\cmake" "%engine%\CMakeLists.txt" || set "status=1"
echo == engine code map
%py% "%engine%\tools\ci\code_map.py" check --root "%engine%" || set "status=1"
echo == toolkit style
%py% "%toolkit%\editor\tests\test_style.py" || set "status=1"
echo == toolkit code map
%py% "%toolkit%\toolkit\code_map.py" check --root "%toolkit%" || set "status=1"
if "%status%"=="0" echo all checks passed
exit /b %status%
:missing
echo error: engine\ or toolkit\ is not checked out; run: git submodule update --init --recursive 1>&2
exit /b 1
:help
echo usage: check.cmd
echo Engine: tools\ci\check_principles.sh (needs bash), tools\ci\check_style.py, tools\ci\code_map.py check.
echo Toolkit: editor\tests\test_style.py, toolkit\code_map.py check.
exit /b 0
