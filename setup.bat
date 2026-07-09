@echo off
REM One-command setup for the Agents Bootcamp on Windows.
REM Run from the repo root, in Command Prompt or PowerShell:  setup.bat
setlocal

echo.
echo === Agents Bootcamp setup (Windows) ===
echo.

REM Find Python: prefer the "py" launcher, then "python".
set "PYCMD="
where py >nul 2>nul && set "PYCMD=py"
if not defined PYCMD where python >nul 2>nul && set "PYCMD=python"
if not defined PYCMD (
  echo Python 3.10+ was not found on your PATH.
  echo Install it from https://www.python.org/downloads/ and tick
  echo    "Add python.exe to PATH" during installation, then run setup.bat again.
  exit /b 1
)

echo [1/3] Creating virtual environment (.venv)...
%PYCMD% -m venv .venv || goto :fail

echo [2/3] Installing the harness and all dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
".venv\Scripts\python.exe" -m pip install -e . || goto :fail

echo [3/3] Verifying your setup...
".venv\Scripts\python.exe" check_setup.py

echo.
echo Setup complete.
echo If a .env file was just created, open it, paste your keys, then run:
echo     .venv\Scripts\python.exe check_setup.py
echo.
echo To work on the assignments, activate the environment in each new terminal:
echo     .venv\Scripts\activate
exit /b 0

:fail
echo.
echo Setup failed. Read the message above, fix it, and run setup.bat again.
exit /b 1
