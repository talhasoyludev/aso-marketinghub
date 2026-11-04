#!/bin/bash
# macOS: pulls fresh data from the stores and updates data.json (~6 min).
# When it finishes, reload the panel in your browser.
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then echo "Python not found. Install it from python.org or with 'brew install python'."; read -n1; exit 1; fi
"$PY" refresh.py
echo ""
echo "Done. Reload the panel in your browser."
read -n1 -p "Press any key to close..."
