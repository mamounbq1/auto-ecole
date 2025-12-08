@echo off
REM ============================================================
REM Lanceur d'application Auto-École Manager
REM ============================================================

echo.
echo ============================================================
echo   Auto-École Manager - Démarrage
echo ============================================================
echo.

REM Vérifier que nous sommes dans le bon répertoire
if not exist "src\main_gui.py" (
    echo [ERREUR] Ce script doit être exécuté depuis le répertoire racine
    echo          Répertoire actuel : %CD%
    pause
    exit /b 1
)

REM Vérifier que la base de données existe
if not exist "data\autoecole.db" (
    echo [ATTENTION] La base de données n'existe pas !
    echo.
    echo   Voulez-vous l'initialiser maintenant ?
    echo   (Cela créera la base avec des données de démonstration)
    echo.
    choice /C ON /M "Appuyez sur O pour initialiser, N pour annuler"
    if errorlevel 2 goto :cancel
    if errorlevel 1 goto :setup
)

:run
echo [OK] Lancement de l'application...
echo.
python src\main_gui.py
goto :end

:setup
echo.
echo Initialisation de la base de données...
call setup_database.bat
goto :run

:cancel
echo.
echo Annulé par l'utilisateur
pause
exit /b 0

:end
if errorlevel 1 (
    echo.
    echo [ERREUR] L'application s'est terminée avec des erreurs
    pause
)
