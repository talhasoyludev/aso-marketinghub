#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""advisor.json'daki dil paketini mağazaya girilebilir dosya ağacına çevirir.

Neden: metinler şu an yalnızca tarayıcı panosunda duruyor. Buradan çıkan ağaç
(a) elle giriş yaparken dil dil kopyalanacak tek kaynak, (b) ileride App Store
Connect API / fastlane deliver ile otomatik yüklemenin beklediği düzen.

    python export_metadata.py            # export/ klasörüne yazar
    python export_metadata.py --check    # yazmaz, yalnızca limitleri denetler

Çıktı:
    export/asc/<apple-locale>/{name,subtitle,keywords,description,
                               promotional_text,_screenshot_headings}.txt
    export/play/<play-locale>/{title,short_description,full_description}.txt

Limit aşan alan varsa çıkış kodu 1 olur — mağaza zaten o yazımı reddeder.
"""
import json
import sys
from pathlib import Path

# Windows konsolu (cp1254) Unicode karakterlerde patlamasın — refresh.py ile aynı koruma
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
WS = BASE / "workspace"          # kişisel veri kod ağacının dışında
EXPORT = WS / "export"

# Apple ve Google aynı dil için farklı kod ister; yanlış kod = sessizce yok sayılan
# ya da reddedilen yazım. Apple bazı dilleri ülke ekiyle ister (ar-SA, pt-BR),
# bazılarını çıplak (tr, pl, ru); Play'de Arapça çıplak "ar", Türkçe "tr-TR".
LOCALES = {
    # hub kodu: (Apple locale, Play locale, görünen ad)
    "en":    ("en-US", "en-US", "İngilizce (kaynak)"),
    "tr":    ("tr",    "tr-TR", "Türkçe"),
    "de":    ("de-DE", "de-DE", "Almanca"),
    "pl":    ("pl",    "pl-PL", "Lehçe"),
    "ar":    ("ar-SA", "ar",    "Arapça"),
    "es":    ("es-ES", "es-ES", "İspanyolca"),
    "pt-BR": ("pt-BR", "pt-BR", "Portekizce (BR)"),
    "fr":    ("fr-FR", "fr-FR", "Fransızca"),
    "ru":    ("ru",    "ru-RU", "Rusça"),
}

ASC_LIMITS = {"name": 30, "subtitle": 30, "keywords": 100,
              "promotional_text": 170, "description": 4000}
PLAY_LIMITS = {"title": 30, "short_description": 80, "full_description": 4000}


def load(name):
    return json.loads((WS / name).read_text(encoding="utf-8"))


def en_source():
    """en-US kaynağı: Claude'un denetlenmiş önerileri; advisor'da olmayan alanlar
    (Play başlığı/uzun açıklaması) mağazadan okunan CANLI değerden alınır."""
    adv = load("advisor.json")
    src = {s["field"]: s["value"] for s in adv.get("asoSuggestions", [])}
    try:
        live = load("data.json")["myApp"]
    except Exception:
        live = {}
    ios, play = live.get("ios") or {}, live.get("play") or {}
    return {
        "iosTitle": src.get("iosTitle") or ios.get("title"),
        "iosSub":   src.get("iosSub") or ios.get("subtitle"),
        "iosKw":    src.get("iosKw"),
        "iosDesc":  src.get("iosDesc") or ios.get("description"),
        "iosPromo": src.get("iosPromo"),
        "gpTitle":  play.get("title") or src.get("iosTitle"),
        "gpShort":  src.get("gpShort") or play.get("short"),
        "gpLong":   play.get("description"),
        "screens":  None,   # EN başlıkları index.html'de duruyor, dışa aktarılmaz
    }


def rows():
    """(hub kodu, ad, alanlar) — en-US önce, sonra paketteki diller."""
    adv = load("advisor.json")
    out = [("en", LOCALES["en"][2], en_source())]
    for loc in adv.get("localization", []):
        code = loc.get("lang")
        if code not in LOCALES:
            print(f"  ! {code}: Apple/Play kod eşlemesi yok, atlandı")
            continue
        out.append((code, loc.get("name") or code, {
            "iosTitle": loc.get("iosTitle"),
            "iosSub":   loc.get("iosSub"),
            "iosKw":    loc.get("iosKw"),
            # Dil paketinde iOS'a özel açıklama yok; Play uzun açıklaması
            # her iki mağaza için de kullanılıyor (aynı metin, aynı dil).
            "iosDesc":  loc.get("gpLong"),
            "iosPromo": None,
            "gpTitle":  loc.get("iosTitle"),
            "gpShort":  loc.get("gpShort"),
            "gpLong":   loc.get("gpLong"),
            "screens":  loc.get("screens"),
        }))
    return out


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main():
    check_only = "--check" in sys.argv
    problems, written, missing = [], 0, []

    print("Dil paketi dışa aktarımı" + (" (yalnızca denetim)" if check_only else ""))
    print(f"{'dil':16} {'name':>7} {'subtitle':>9} {'keywords':>9} {'short':>7} {'long':>7}")
    print("-" * 60)

    for code, name, f in rows():
        asc_loc, play_loc, _ = LOCALES[code]
        asc = {
            "name": f["iosTitle"], "subtitle": f["iosSub"], "keywords": f["iosKw"],
            "description": f["iosDesc"], "promotional_text": f["iosPromo"],
        }
        play = {
            "title": f["gpTitle"], "short_description": f["gpShort"],
            "full_description": f["gpLong"],
        }

        for field, limit in ASC_LIMITS.items():
            v = asc.get(field)
            if not v:
                missing.append(f"{code}/asc/{field}")
                continue
            if len(v) > limit:
                problems.append(f"{code} asc/{field}: {len(v)}/{limit}")
        for field, limit in PLAY_LIMITS.items():
            v = play.get(field)
            if not v:
                missing.append(f"{code}/play/{field}")
                continue
            if len(v) > limit:
                problems.append(f"{code} play/{field}: {len(v)}/{limit}")

        def n(x):
            return len(x) if x else 0
        print(f"{name[:16]:16} {n(asc['name']):>7} {n(asc['subtitle']):>9} "
              f"{n(asc['keywords']):>9} {n(play['short_description']):>7} "
              f"{n(play['full_description']):>7}")

        if check_only:
            continue
        for field, v in asc.items():
            if v:
                write(EXPORT / "asc" / asc_loc / f"{field}.txt", v)
                written += 1
        if f.get("screens"):
            write(EXPORT / "asc" / asc_loc / "_screenshot_headings.txt",
                  "\n".join(f["screens"]))
            written += 1
        for field, v in play.items():
            if v:
                write(EXPORT / "play" / play_loc / f"{field}.txt", v)
                written += 1

    print("-" * 60)
    if not check_only:
        print(f"✓ {written} dosya yazıldı → {EXPORT}")
    if missing:
        print(f"\nBoş alanlar ({len(missing)}) — mağazada elle doldurulacak ya da "
              f"advisor.json'a eklenecek:")
        for m in sorted(set(missing)):
            print("   ·", m)
    if problems:
        print("\n✗ LİMİT AŞIMI — mağaza bu yazımı reddeder:")
        for p in problems:
            print("   ·", p)
        return 1
    print("\n✓ Tüm alanlar karakter limitleri içinde.")
    print("Not: Gizlilik politikası URL'i her locale için ZORUNLU (App Store "
          "gönderiminde locale başına hata verir) — bu araç URL üretmez, "
          "ASC'de dil dil gir.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
