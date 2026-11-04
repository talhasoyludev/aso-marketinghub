@echo off
rem Pulls fresh ASO Radar data from the stores and updates workspace/data.json.
cd /d "%~dp0"
python refresh.py
echo.
pause
