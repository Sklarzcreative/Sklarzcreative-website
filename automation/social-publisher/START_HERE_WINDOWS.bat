@echo off
setlocal
cd /d "%~dp0"
echo Sklarz Social Publisher - Windows setup
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\bootstrap_windows.ps1"
echo.
pause
