@echo off
REM ============================================================
REM Lanceur propre - Auto-Ecole Manager (sans console persistante)
REM ============================================================

cd /d "%~dp0"

REM Lancer avec pythonw.exe (sans console)
start "" pythonw.exe launch_app.pyw

REM Alternative si pythonw n'existe pas
if errorlevel 1 (
    start "" python.exe src\main_gui.py
)

exit
