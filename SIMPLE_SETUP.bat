@echo off
REM ============================================================
REM SETUP SIMPLE - Auto-Ecole Manager
REM Ce script initialise la base de donnees en une seule commande
REM ============================================================

echo.
echo ============================================================
echo   AUTO-ECOLE MANAGER - INSTALLATION SIMPLE
echo ============================================================
echo.

REM Aller dans le repertoire du script
cd /d "%~dp0"

REM Verifier que nous sommes au bon endroit
if not exist "src\main_gui.py" (
    echo [ERREUR] Fichiers du projet introuvables
    echo          Verifiez que vous etes dans le bon dossier
    pause
    exit /b 1
)

REM Creer le dossier data
if not exist "data" mkdir data

REM Lancer l'initialisation
echo Initialisation de la base de donnees...
echo.
python src\init_db.py

if errorlevel 1 (
    echo.
    echo [ERREUR] Initialisation echouee
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   INSTALLATION TERMINEE !
echo ============================================================
echo.
echo   Lancez l'application : launch_app.bat
echo   Ou tapez : python src\main_gui.py
echo.
echo   Login : admin / Admin123!
echo.
pause
