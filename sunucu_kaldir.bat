@echo off
chcp 65001 >nul
net session >nul 2>&1 || (echo Yonetici olarak calistirin. & pause & exit /b 1)
schtasks /end /tn "Vardiya Takip\Sunucu" >nul 2>&1
schtasks /delete /f /tn "Vardiya Takip\Sunucu" >nul 2>&1
schtasks /delete /f /tn "Vardiya Takip\Gunluk yedek" >nul 2>&1
netsh advfirewall firewall delete rule name="Vardiya Takip" >nul 2>&1
echo Otomatik baslama, gunluk yedek ve guvenlik duvari kurali kaldirildi. Veriler ve yedekler silinmedi.
pause
