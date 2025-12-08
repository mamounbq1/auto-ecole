@echo off
REM ============================================================
REM Lanceur propre - Auto-Ecole Manager
REM Supprime les messages d'erreur matplotlib dans la console
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo   AUTO-ECOLE MANAGER
echo ============================================================
echo.
echo   Demarrage de l'application...
echo.

REM Lancer l'application en redirigeant les erreurs
python src\main_gui.py 2>nul

if errorlevel 1 (
    echo.
    echo [ERREUR] L'application s'est terminee avec des erreurs
    echo.
    pause
)
