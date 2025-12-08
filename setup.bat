@echo off
echo ================================================================================
echo  SETUP - Auto-Ecole Manager
echo ================================================================================
echo.

echo [1/2] Initialisation de la base de donnees...
python setup_database.py
if %errorlevel% neq 0 (
    echo.
    echo ERREUR: L'initialisation a echoue
    pause
    exit /b 1
)

echo.
echo [2/2] Base de donnees prete!
echo.
echo ================================================================================
echo  SETUP TERMINE AVEC SUCCES!
echo ================================================================================
echo.
echo Lancez l'application avec: python src/main_gui.py
echo.
pause
