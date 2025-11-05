@echo off
cls
echo ======================================================================
echo                   MARKET STUDY - Demarrage
echo ======================================================================
echo.

REM Verifier si venv existe
if not exist "venv\" (
    echo [ERREUR] Environnement virtuel non trouve!
    echo.
    echo Veuillez d'abord executer install.bat
    echo.
    pause
    exit /b 1
)

REM Activer l'environnement
echo [1/3] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Verifier que Flask est installe
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [ERREUR] Flask n'est pas installe!
    echo.
    echo Veuillez executer: pip install Flask
    echo.
    pause
    exit /b 1
)

echo [2/3] Verification des packages...
python -c "import flask, numpy, matplotlib, reportlab; print('OK')" 2>nul
if errorlevel 1 (
    echo [ATTENTION] Certains packages semblent manquants
    echo Tentative d'installation...
    pip install Flask flask-cors numpy matplotlib reportlab Pillow pandas
)

echo [3/3] Demarrage du serveur...
echo.
echo ======================================================================
echo   Serveur demarre sur: http://localhost:5000
echo   Appuyez sur Ctrl+C pour arreter
echo ======================================================================
echo.

REM Lancer l'application
python app.py

pause