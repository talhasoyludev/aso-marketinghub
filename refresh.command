#!/bin/bash
# macOS: Mağazalardan güncel veriyi çeker ve data.json'ı günceller (~6 dk).
# Bittiğinde açık siteyi tarayıcıda yenile.
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then echo "Python bulunamadı. python.org veya 'brew install python' ile kur."; read -n1; exit 1; fi
"$PY" refresh.py
echo ""
echo "Bitti. Tarayıcıda siteyi yenile."
read -n1 -p "Kapatmak için bir tuşa bas..."
