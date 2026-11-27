@echo off
chcp 65001 >nul
cd /d "%~dp0"
net session >nul 2>&1 || (echo Yonetici olarak calistirin. & pause & exit /b 1)
echo Sunucu yeniden baslatiliyor (guncelleme sonrasi kullanin)...
schtasks /end /tn "Vardiya Takip\Sunucu" >nul 2>&1
timeout /t 3 >nul
venv\Scripts\python.exe -m pip install -r requirements.txt >nul
schtasks /run /tn "Vardiya Takip\Sunucu" >nul
echo Tamam. Birkac saniye sonra http://localhost:8000 acilir.
timeout /t 5 >nul
start "" http://localhost:8000
