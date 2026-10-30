@echo off
rem Builds the engine with one of its CMake presets (engine\CMakePresets.json; build folder engine\build\<preset>),
rem then, with --test, runs that preset's tests. With --game FOLDER it builds that game instead (a folder with
rem reference\project.json, such as one the Studio's New game made): the engine library and the game only, with the
rem same preset, in FOLDER\build\<preset>\ (the engine's CAPSULE_GAMES; its own tests and apps are left out).
setlocal
set "preset="
set "run_tests=0"
set "game="
:args
if "%~1"=="" goto run
if "%~1"=="-h" goto help
if "%~1"=="--help" goto help
if "%~1"=="--test" (
   set "run_tests=1"
) else if "%~1"=="--game" (
   if "%~2"=="" (
      echo error: --game needs the game's folder ^(try --help^) 1>&2
      exit /b 2
   )
   set "game=%~f2"
   shift
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
rem a trailing backslash would escape the closing quote of -DCAPSULE_GAMES="..."
if not "%game%"=="" if "%game:~-1%"=="\" set "game=%game:~0,-1%"
if not "%game%"=="" goto game
pushd "%~dp0engine"
cmake --preset %preset% || goto failed
cmake --build --preset %preset% || goto failed
if "%run_tests%"=="1" ctest --preset %preset% || goto failed
popd
exit /b 0
:game
rem A game: its folder made absolute (CMake reads it from the engine's folder), its own build folder.
if "%run_tests%"=="1" (
   echo error: --test runs the engine's tests; a --game build has none 1>&2
   exit /b 2
)
if "%preset%"=="headless" goto no_games
if "%preset%"=="big-endian-check" goto no_games
if not exist "%game%\reference\project.json" (
   echo error: %game% is not a game folder ^(it has no reference\project.json^) 1>&2
   exit /b 1
)
set "out=%game%\build\%preset%"
rem A desktop build reuses the SDL2 source the engine's own build of the preset downloaded, if there is one.
set "sdl2="
if exist "%~dp0engine\build\%preset%\_deps\sdl2-src\CMakeLists.txt" (
   set "sdl2=-DFETCHCONTENT_SOURCE_DIR_SDL2=%~dp0engine\build\%preset%\_deps\sdl2-src"
)
pushd "%~dp0engine"
cmake --preset %preset% -B "%out%" "-DCAPSULE_GAMES=%game%" -DCAPSULE_ENGINE_TESTS=OFF %sdl2% || goto failed
cmake --build "%out%" || goto failed
popd
echo built %game% in %out%
exit /b 0
:no_games
echo error: the %preset% preset builds no games; pick a windows, gba or dc preset 1>&2
exit /b 2
:failed
popd
exit /b 1
:help
echo usage: build.cmd [PRESET] [--test] [--game FOLDER]
echo Configures and builds engine\ with a CMake preset, default windows-debug; --test runs its ctest preset.
echo --game FOLDER builds that game ^(FOLDER\reference\project.json^) with the preset instead, into
echo FOLDER\build\PRESET\ ^(capsule_^<name^>.exe, and capsule_^<name^>.gba on the GBA^).
echo Presets: windows-debug windows-release gba-debug gba-release dc-debug dc-release headless
exit /b 0
