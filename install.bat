@echo off
echo ========================================
echo Installation des packages Python
echo ========================================
echo.

echo [1/6] Mise a jour de pip...
python -m pip install --upgrade pip setuptools wheel
echo.

echo [2/6] Installation de NumPy...
pip install numpy>=1.24.0
echo.

echo [3/6] Installation de Flask...
pip install Flask==3.0.0 flask-cors==4.0.0 Werkzeug==3.0.1
echo.

echo [4/6] Installation de Matplotlib...
pip install matplotlib>=3.7.0
echo.

echo [5/6] Installation de ReportLab et Pillow...
pip install reportlab>=4.0.0 Pillow>=10.0.0
echo.

echo [6/6] Installation des utilitaires...
pip install pandas>=2.0.0 pydantic>=2.5.0 python-dotenv==1.0.0 requests>=2.31.0
echo.

echo ========================================
echo Installation terminee!
echo ========================================
echo.

echo Verification de l'installation...
python -c "import flask, numpy, matplotlib, reportlab, PIL; print('✓ Tous les packages sont installes!')"
echo.

pause