@echo off
REM ============================================================
REM Script d'installation de la base de données Auto-École
REM ============================================================

echo.
echo ============================================================
echo   SETUP - Auto-Ecole Manager
echo ============================================================
echo.

REM Vérifier que nous sommes dans le bon répertoire
if not exist "src\main_gui.py" (
    echo [ERREUR] Ce script doit etre execute depuis le repertoire racine
    echo          Repertoire actuel : %CD%
    echo          Fichier attendu : src\main_gui.py
    echo.
    pause
    exit /b 1
)

echo [1/3] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo          Veuillez installer Python 3.8+ depuis python.org
    pause
    exit /b 1
)
python --version
echo       OK - Python installe

echo.
echo [2/3] Verification des dependances...
python -c "import sqlalchemy; import PySide6; import reportlab" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation des dependances...
    python -m pip install --quiet sqlalchemy PySide6 reportlab matplotlib seaborn
)
echo       OK - Dependances installees

echo.
echo [3/3] Initialisation de la base de donnees...
echo.

REM Appeler directement le script d'initialisation Python
python src\init_db.py

if errorlevel 1 (
    echo.
    echo [ERREUR] L'initialisation a echoue
    echo          Voir les messages ci-dessus pour plus de details
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Installation terminee avec succes !
echo ============================================================
echo.
echo   Lancez l'application :
echo   1. Double-cliquez sur : launch_app.bat
echo   2. OU tapez : python src\main_gui.py
echo.
echo   Compte admin :
echo     Username : admin
echo     Password : Admin123!
echo.
pause
