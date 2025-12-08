@echo off
REM ============================================================
REM Script d'installation de la base de données Auto-École
REM ============================================================

echo.
echo ============================================================
echo   Installation de la base de données Auto-École
echo ============================================================
echo.

REM Vérifier que nous sommes dans le bon répertoire
if not exist "src\main_gui.py" (
    echo [ERREUR] Ce script doit être exécuté depuis le répertoire racine du projet
    echo          Répertoire actuel : %CD%
    echo          Fichier attendu : src\main_gui.py
    echo.
    pause
    exit /b 1
)

echo [1/4] Création du répertoire data...
if not exist "data" (
    mkdir data
    echo       OK - Répertoire créé
) else (
    echo       OK - Répertoire existe déjà
)

echo.
echo [2/4] Vérification de l'installation Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installé ou pas dans le PATH
    echo          Veuillez installer Python 3.8+ depuis python.org
    pause
    exit /b 1
)
python --version
echo       OK - Python installé

echo.
echo [3/4] Vérification des dépendances...
python -c "import sqlalchemy" >nul 2>&1
if errorlevel 1 (
    echo [ATTENTION] SQLAlchemy non installé
    echo             Installation des dépendances...
    python -m pip install sqlalchemy PySide6 reportlab
)
echo       OK - Dépendances installées

echo.
echo [4/4] Initialisation de la base de données...
python src\init_db.py

if errorlevel 1 (
    echo.
    echo [ERREUR] L'initialisation a échoué
    echo          Voir les messages d'erreur ci-dessus
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Installation terminée avec succès !
echo ============================================================
echo.
echo   Vous pouvez maintenant lancer l'application :
echo   1. Double-cliquez sur : launch_app.bat
echo   2. OU tapez : python src\main_gui.py
echo.
echo   Comptes disponibles :
echo     - Admin : admin / Admin123!
echo     - Caissier : caissier / Caisse123!
echo.
pause
