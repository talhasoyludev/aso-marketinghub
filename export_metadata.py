#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Turns the language pack in advisor.json into a file tree you can enter in the stores.

Why: the copy otherwise lives only in the browser panel. The tree produced here is
(a) the single source to copy from, language by language, when entering it by hand,
and (b) the layout App Store Connect API / fastlane deliver expect for automated upload.

    python export_metadata.py            # writes to workspace/export/
    python export_metadata.py --check    # writes nothing, only checks limits

Output:
    export/asc/<apple-locale>/{name,subtitle,keywords,description,
                               promotional_text,_screenshot_headings}.txt
    export/play/<play-locale>/{title,short_description,full_description}.txt

Exit code is 1 if any field exceeds its limit — the store would reject it anyway.
Console output follows config.json > lang (MARKETINGHUB_LANG overrides it).
"""
import json
import sys
from pathlib import Path

from mh_text import t

# Keep Windows consoles (cp1254 etc.) from crashing on Unicode — same guard as refresh.py
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
    # hub code: (Apple locale, Play locale, display name)
    "en":    ("en-US", "en-US", t("e.lang.en")),
    "tr":    ("tr",    "tr-TR", t("e.lang.tr")),
    "de":    ("de-DE", "de-DE", t("e.lang.de")),
    "pl":    ("pl",    "pl-PL", t("e.lang.pl")),
    "ar":    ("ar-SA", "ar",    t("e.lang.ar")),
    "es":    ("es-ES", "es-ES", t("e.lang.es")),
    "pt-BR": ("pt-BR", "pt-BR", t("e.lang.pt-BR")),
    "fr":    ("fr-FR", "fr-FR", t("e.lang.fr")),
    "ru":    ("ru",    "ru-RU", t("e.lang.ru")),
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
            print(t("e.no_mapping", code=code))
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
    if not (WS / "advisor.json").exists():
        print(t("e.no_advisor"))
        return 1

    print(t("e.title") + (t("e.check_only") if check_only else ""))
    print(f"{t('e.col_lang'):16} {'name':>7} {'subtitle':>9} {'keywords':>9} {'short':>7} {'long':>7}")
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
        print(t("e.written", n=written, path=EXPORT))
    if missing:
        print(t("e.missing", n=len(missing)))
        for m in sorted(set(missing)):
            print("   ·", m)
    if problems:
        print(t("e.over_limit"))
        for p in problems:
            print("   ·", p)
        return 1
    print(t("e.ok"))
    print(t("e.privacy_note"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
