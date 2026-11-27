@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist venv (echo Once kurulum.bat calistirin. & pause & exit /b 1)
call venv\Scripts\activate
python manage.py migrate --noinput >nul
start "" http://localhost:8000
echo Uygulama calisiyor: http://localhost:8000  (kapatmak icin bu pencereyi kapatin)
python manage.py runserver 0.0.0.0:8000
