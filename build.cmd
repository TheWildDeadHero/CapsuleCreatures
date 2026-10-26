@echo off
rem Builds the engine with one of its CMake presets (engine\CMakePresets.json; build folder engine\build\<preset>),
rem then, with --test, runs that preset's tests.
setlocal
set "preset="
set "run_tests=0"
:args
if "%~1"=="" goto run
if "%~1"=="-h" goto help
if "%~1"=="--help" goto help
if "%~1"=="--test" (
   set "run_tests=1"
) else (
   set "preset=%~1"
)
shift
goto args
:run
if not exist "%~dp0engine\CMakePresets.json" (
   echo error: engine\ is not checked out; run: git submodule update --init --recursive 1>&2
   exit /b 1
)
if "%preset%"=="" set "preset=windows-debug"
pushd "%~dp0engine"
cmake --preset %preset% || goto failed
cmake --build --preset %preset% || goto failed
if "%run_tests%"=="1" ctest --preset %preset% || goto failed
popd
exit /b 0
:failed
popd
exit /b 1
:help
echo usage: build.cmd [PRESET] [--test]
echo Configures and builds engine\ with a CMake preset, default windows-debug; --test runs its ctest preset.
echo Presets: windows-debug windows-release gba-debug gba-release dc-debug dc-release headless
exit /b 0
