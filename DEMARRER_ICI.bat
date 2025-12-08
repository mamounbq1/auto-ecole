@echo off
chcp 65001 >nul
cls

echo ============================================================
echo          AUTO-ECOLE MANAGER - Demarrage automatique
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] Mise a jour du code depuis GitHub...
git pull origin main
if errorlevel 1 (
    echo.
    echo [ATTENTION] Mise a jour impossible - Code actuel sera utilise
    echo.
    timeout /t 3 >nul
)

echo.
echo [2/3] Verification de la base de donnees...
if not exist "data\autoecole.db" (
    echo      Base de donnees manquante - Creation...
    python src\init_db.py
)

echo.
echo [3/3] Lancement de l'application...
echo.
echo ============================================================
echo   L'application va demarrer dans quelques secondes...
echo   Login: admin
echo   Password: Admin123!
echo ============================================================
echo.

python start_safe.py

if errorlevel 1 (
    echo.
    echo [ERREUR] L'application a rencontre une erreur
    echo.
    pause
)
