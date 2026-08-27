@echo off
rem Yayin kopyasini uretir ve YENI KULLANICI gibi acar (port 8138).
rem Kendi panelin etkilenmez: start.bat 8137'de kendi verilerinle acilir.
cd /d "%~dp0"
python make_release.py --run
pause
