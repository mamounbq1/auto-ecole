@echo off
REM ============================================================
REM Lanceur sécurisé - Auto-Ecole Manager
REM Bloque matplotlib pour éviter les crashes
REM ============================================================

cd /d "%~dp0"

python start_safe.py

if errorlevel 1 (
    echo.
    echo [ERREUR] L'application s'est terminee avec des erreurs
    pause
)
