@echo off
rem Starts the scene editor from the toolkit submodule (toolkit\toolkit\env.py run scene-editor).
rem The first run sets up the toolkit's Python environment (toolkit\.venv).
if not exist "%~dp0toolkit\toolkit\env.py" (
   echo error: toolkit\ is not checked out; run: git submodule update --init --recursive 1>&2
   exit /b 1
)
where py >nul 2>nul
if %errorlevel%==0 (
   py -3 "%~dp0toolkit\toolkit\env.py" run scene-editor %*
) else (
   python "%~dp0toolkit\toolkit\env.py" run scene-editor %*
)
exit /b %errorlevel%
