#!/bin/bash
# macOS: Siteyi MEVCUT verilerle açar — tarama YAPMAZ (data.json korunur).
# İlk kullanımda çalıştırılabilir yap:  chmod +x start.command refresh.command
# Sonra Finder'dan çift tıkla (veya Terminal'de ./start.command).
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then echo "Python bulunamadı. python.org veya 'brew install python' ile kur."; read -n1; exit 1; fi
( sleep 1; open http://localhost:8137 ) &
"$PY" -m http.server 8137
