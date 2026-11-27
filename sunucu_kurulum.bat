@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Vardiya Takip - Sunucu kurulumu

net session >nul 2>&1
if errorlevel 1 (
  echo Bu dosyayi SAG TIK ^> "Yonetici olarak calistir" ile acin.
  pause & exit /b 1
)

echo [1/6] Python kontrol ediliyor...
where python >nul 2>nul || (echo Python bulunamadi. python.org adresinden Python 3.11+ kurun, "Add to PATH" isaretli olsun. & pause & exit /b 1)

echo [2/6] Gerekli paketler kuruluyor...
if not exist venv python -m venv venv
call venv\Scripts\python.exe -m pip install --upgrade pip >nul
call venv\Scripts\python.exe -m pip install -r requirements.txt || (echo Paketler kurulamadi. & pause & exit /b 1)

echo [3/6] Veritabani hazirlaniyor...
set VARDIYA_DEBUG=0
call venv\Scripts\python.exe manage.py migrate --noinput || (pause & exit /b 1)

echo [4/6] Admin hesabi
call venv\Scripts\python.exe -c "import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings');django.setup();from hesaplar.models import Kullanici;exit(0 if Kullanici.objects.filter(is_superuser=True).exists() else 1)"
if errorlevel 1 (
  echo Ilk admin hesabini olusturun ^(kullanici adi ve sifre isteyecek^):
  call venv\Scripts\python.exe manage.py createsuperuser
) else (
  echo Admin hesabi zaten var, atlandi.
)

echo [5/6] Guvenlik duvarinda 8000 portu aciliyor...
netsh advfirewall firewall delete rule name="Vardiya Takip" >nul 2>&1
netsh advfirewall firewall add rule name="Vardiya Takip" dir=in action=allow protocol=TCP localport=8000 profile=domain,private >nul

echo [6/6] Otomatik baslama ve gunluk yedek ayarlaniyor...
schtasks /create /f /tn "Vardiya Takip\Sunucu" /tr "\"%~dp0sunucu_baslat.bat\"" /sc onstart /ru SYSTEM /rl HIGHEST >nul
schtasks /create /f /tn "Vardiya Takip\Gunluk yedek" /tr "\"%~dp0yedek_al.bat\"" /sc daily /st 02:00 /ru SYSTEM /rl HIGHEST >nul
schtasks /run /tn "Vardiya Takip\Sunucu" >nul

echo.
echo ============================================================
echo  Kurulum tamam. Sunucu arka planda calisiyor ve bilgisayar
echo  her acildiginda kendiliginden baslayacak.
echo  Diger bilgisayarlardan tarayicida su adres acilir:
echo     http://%COMPUTERNAME%:8000
echo  Yedekler her gece 02:00'de "yedekler" klasorune alinir.
echo ============================================================
start "" http://localhost:8000
pause
