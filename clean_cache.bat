@echo off
REM ============================================================
REM Nettoyer le cache Python (.pyc et __pycache__)
REM ============================================================

echo.
echo ============================================================
echo   Nettoyage du cache Python
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/3] Suppression des fichiers .pyc...
del /s /q *.pyc 2>nul
echo       OK

echo.
echo [2/3] Suppression des dossiers __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo       OK

echo.
echo [3/3] Suppression des fichiers .pyo...
del /s /q *.pyo 2>nul
echo       OK

echo.
echo ============================================================
echo   Cache nettoye avec succes !
echo ============================================================
echo.
echo   Vous pouvez maintenant lancer l'application :
echo   python start_safe.py
echo.
pause
