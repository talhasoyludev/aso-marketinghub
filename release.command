#!/bin/bash
# macOS: Yayın kopyasını üretir ve YENİ KULLANICI gibi açar (port 8138).
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then echo "Python bulunamadı."; read -n1; exit 1; fi
"$PY" make_release.py --run
