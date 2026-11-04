@echo off
rem Demo mode: opens the panel with FICTIONAL sample data from demo/ — no setup, no scan.
rem Your own workspace/ is never read or changed. Close this window to stop the server.
cd /d "%~dp0"
start "" "http://localhost:8137/?demo=1"
python -m http.server 8137
