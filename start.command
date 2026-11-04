#!/bin/bash
# macOS: opens the panel with the EXISTING data - does NOT scan (data.json is kept).
# First time only, make it executable:  chmod +x start.command refresh.command
# Then double-click it in Finder (or run ./start.command in Terminal).
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then echo "Python not found. Install it from python.org or with 'brew install python'."; read -n1; exit 1; fi
( sleep 1; open http://localhost:8137 ) &
"$PY" -m http.server 8137
