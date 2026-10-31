@echo off
rem Sets up this machine for CapsuleCreatures (GBA and desktop toolchains, the toolkit's Python environment): runs
rem the toolkit's installer, toolkit\install\install.ps1, with the options given. The installer stays in the toolkit.
if "%~1"=="-h" goto help
if "%~1"=="--help" goto help
if not exist "%~dp0toolkit\install\install.ps1" (
   echo error: toolkit\ is not checked out; run: git submodule update --init --recursive 1>&2
   exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0toolkit\install\install.ps1" %*
exit /b %errorlevel%
:help
echo usage: setup.cmd [installer options: -DryRun, -GbaOnly, -DesktopOnly, ...]
echo Runs toolkit\install\install.ps1 (machine setup and the toolkit environment).
exit /b 0
