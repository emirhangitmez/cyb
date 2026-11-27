@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist logs mkdir logs
set VARDIYA_DEBUG=0
venv\Scripts\python.exe sunucu.py >> logs\sunucu.log 2>&1
