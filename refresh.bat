@echo off
rem ASO Radar verilerini mağazalardan çeker ve data.json'ı günceller.
cd /d "%~dp0"
python refresh.py
echo.
pause
