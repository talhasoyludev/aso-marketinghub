@echo off
rem Opens the panel with the EXISTING data - does NOT scan (data.json is kept).
rem When you want fresh data, run refresh.bat separately, then reload the browser.
cd /d "%~dp0"
start "" http://localhost:8137
python -m http.server 8137
