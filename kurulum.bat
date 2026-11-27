@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Vardiya Takip kurulumu basliyor...
where python >nul 2>nul || (echo Python bulunamadi. https://www.python.org adresinden Python 3.11+ kurun ve "Add to PATH" kutusunu isaretleyin. & pause & exit /b 1)
if not exist venv python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py ornek_kullanicilar
echo.
echo Kurulum tamam. Simdi baslat.bat ile uygulamayi acin.
pause
