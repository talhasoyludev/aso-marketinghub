#!/bin/bash
# macOS: demo mode — opens the panel with FICTIONAL sample data from demo/; no setup, no scan.
# Your own workspace/ is never read or changed. Close the Terminal window to stop the server.
# First run, if needed:  chmod +x demo.command   (then double-click it in Finder)
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then echo "Python not found. Install it from python.org or with 'brew install python'."; read -n1; exit 1; fi
( sleep 1; open "http://localhost:8137/?demo=1" ) &
"$PY" -m http.server 8137
