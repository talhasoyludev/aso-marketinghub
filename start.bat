@echo off
rem Siteyi MEVCUT verilerle açar — tarama YAPMAZ (data.json korunur).
rem Yeni veri istediğinde ayrıca refresh.bat çalıştır, sonra tarayıcıyı yenile.
cd /d "%~dp0"
start "" http://localhost:8137
python -m http.server 8137
