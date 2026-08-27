#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""İlk kurulum ve sağlık kontrolü.

    python setup.py            # eksik dosyaları şablondan oluşturur, durumu yazar
    python setup.py --check    # hiçbir şey yazmaz, yalnızca durumu raporlar

Kişisel veri (config, tarama çıktısı, analizler, görseller) workspace/ altında
durur ve git'e girmez; kod ağacı herkese açık paylaşılabilir kalır.
"""
import json
import shutil
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
WS = BASE / "workspace"
TPL = BASE / "templates"

# şablondan kopyalanacak dosyalar: (workspace adı, şablon adı, zorunlu mu)
# (workspace adı, şablon adı, zorunlu mu) — playbook dile göre seçilir
SEED = [("config.json", "config.json", True),
        ("advisor.json", "advisor.json", False),
        ("playbook.json", None, False)]


def playbook_template(lang):
    """Dil paketine uygun playbook şablonu; yoksa İngilizce."""
    for name in (f"playbook.{lang}.json", "playbook.en.json"):
        if (TPL / name).exists():
            return name
    return "playbook.en.json"

PASS, WARN, FAIL = "  ✓", "  ! ", "  ✗"


def main():
    check_only = "--check" in sys.argv
    problems = []

    WS.mkdir(exist_ok=True)

    # Kök dizinde eski yerleşimden kalan dosya varsa workspace'e taşı
    for name, _, _ in SEED:
        old = BASE / name
        if old.exists() and not (WS / name).exists():
            if check_only:
                print(WARN + f"{name} kök dizinde — `python setup.py` workspace'e taşır")
            else:
                shutil.move(str(old), str(WS / name))
                print(PASS + f" {name} → workspace/ taşındı (eski yerleşimden)")

    lang = "en"
    try:
        lang = json.loads((WS / "config.json").read_text(encoding="utf-8")).get("lang", "en")
    except Exception:
        try:
            lang = json.loads((TPL / "config.json").read_text(encoding="utf-8")).get("lang", "en")
        except Exception:
            pass

    for name, tpl, required in SEED:
        tpl = tpl or playbook_template(lang)
        target, source = WS / name, TPL / tpl
        if target.exists():
            print(PASS + f" workspace/{name}")
            continue
        if check_only:
            (problems if required else []).append(f"workspace/{name} yok")
            print((FAIL if required else WARN) + f" workspace/{name} yok"
                  + (f" — şablon: templates/{tpl}" if source.exists() else ""))
            continue
        if source.exists():
            shutil.copy(str(source), str(target))
            print(PASS + f" workspace/{name} şablondan oluşturuldu")
        else:
            problems.append(f"templates/{tpl} bulunamadı")

    cfg_path = WS / "config.json"
    if not cfg_path.exists():
        problems.append("config.json yok")
    else:
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            app = (cfg.get("apps") or {}).get(cfg.get("activeApp")) or {}
            if not app:
                problems.append("config.json: activeApp, apps içindeki bir bloğa işaret etmiyor")
            else:
                if app.get("name") in (None, "", "My App"):
                    problems.append("config.json: apps.<app>.name hâlâ şablon değerinde")
                if not app.get("iosId") and not app.get("playId"):
                    problems.append("config.json: iosId veya playId'den en az biri gerekli")
                if not app.get("keywords"):
                    problems.append("config.json: keywords listesi boş — radar ölçecek bir şey bulamaz")
                if app.get("playId") == "com.example.myapp":
                    problems.append("config.json: playId hâlâ örnek değerinde")
        except json.JSONDecodeError as e:
            problems.append(f"config.json geçerli JSON değil: {e}")

    data = WS / "data.json"
    print((PASS if data.exists() else WARN) +
          (" workspace/data.json" if data.exists()
           else " workspace/data.json yok — henüz tarama yapılmadı"))

    adv = WS / "advisor.json"
    if adv.exists():
        try:
            a = json.loads(adv.read_text(encoding="utf-8"))
            n = len(a.get("recommendations") or []) + len(a.get("asoSuggestions") or [])
            print((PASS if n else WARN) +
                  (f" workspace/advisor.json — {n} kayıt" if n
                   else " workspace/advisor.json boş — henüz Claude analizi yapılmadı"))
        except json.JSONDecodeError as e:
            problems.append(f"advisor.json geçerli JSON değil: {e}")

    print()
    if problems:
        print("Eksikler:")
        for p in problems:
            print("   ·", p)
        print("\nSıradaki adım: workspace/config.json'u kendi uygulamanla doldur "
              "(alan açıklamaları dosyanın içinde), sonra bu betiği tekrar çalıştır.")
        return 1

    print("Kurulum tamam. Sıradaki adımlar:")
    print("   1. python refresh.py        → mağaza taraması, workspace/data.json üretir")
    print("   2. start.bat / start.command → paneli aç")
    print("   3. Claude Code'da: \"bu uygulamanın ASO analizini yap\" "
          "(skills/marketinghub yükleyip advisor.json'u üretir)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
