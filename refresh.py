# -*- coding: utf-8 -*-
"""
ASO Radar data collector
=========================================
Run:  python refresh.py   (or double-click refresh.bat / refresh.command)

What it does:
 1. Fetches App Store / Google Play data for your app and your competitors
    (rating, rating count, install range, title, description).
 2. Runs a tag-frequency analysis over competitor copy and compares it with
    your metadata -> flags opportunity tags.
 3. Measures where you rank in iTunes search for every tracked keyword
    (iOS keyword rank tracking).
 4. Appends each run's measurements to the history in data.json; the panel
    shows it as an automatic report.

Settings come from workspace/config.json (competitors, keywords, countries).
Console and rule-engine text follow config.json > lang ("en" / "tr"; the
MARKETINGHUB_LANG environment variable overrides it) — see mh_text.py.
"""
import json
import math
import re
import sys
import time
import urllib.request
import urllib.parse
from datetime import date, datetime
from html import unescape
from pathlib import Path

from mh_text import t, t_lang

# Windows konsolu (cp1254) Unicode karakterlerde patlamasın
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")   # sys.exit() messages
except Exception:
    pass

# ================== AYARLAR (config.json'dan okunur) ==================
BASE = Path(__file__).resolve().parent
# Kullanıcıya ait her şey workspace/ altında durur: kod ağacı (repo) ile kişisel
# veri (config, tarama çıktısı, görseller) bilerek ayrılmıştır — repo herkese
# açık paylaşılabilir, workspace/ paylaşılmaz.
WS = BASE / "workspace"
if not (WS / "config.json").exists():
    sys.exit(t("r.no_config"))
_cfg_all = json.loads((WS / "config.json").read_text(encoding="utf-8"))
_cfg = _cfg_all["apps"][_cfg_all["activeApp"]]

COUNTRY = _cfg.get("country", "us")
COUNTRIES = _cfg.get("countries") or [COUNTRY]
RATE_SLEEP = _cfg.get("rateLimitSeconds", 3)   # iTunes API ~20 istek/dk sınırı için
MY_NAME = _cfg["name"]
MY_IOS_ID = _cfg.get("iosId")
MY_PLAY_ID = _cfg.get("playId")
DOWNLOAD_ASSETS = _cfg.get("downloadAssets", False)
KEYWORDS = _cfg.get("keywords", [])

def _norm_ios(v):
    if v in (None, "", 0):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None

# Rakip listesi: boş string id'leri None yap, aynı uygulamayı iki kez tarama
COMPETITORS = []
_seen = set()
for _c in _cfg.get("competitors", []):
    ios, play = _norm_ios(_c.get("ios_id")), (_c.get("play_id") or None)
    if not ios and not play:
        continue
    key = (ios, play)
    if key in _seen:
        continue
    _seen.add(key)
    COMPETITORS.append({"name": _c["name"], "ios_id": ios, "play_id": play})

# Ülke -> mağaza dili eşlemesi (lokalizasyon önerileri için)
COUNTRY_LANG = {"tr": "TR", "us": "EN", "gb": "EN", "de": "DE", "fr": "FR", "pl": "PL",
                "br": "PT", "sa": "AR", "ae": "AR", "eg": "AR", "es": "ES", "mx": "ES",
                "it": "IT", "ru": "RU", "jp": "JA", "kr": "KO", "id": "ID", "in": "EN", "nl": "NL"}
# =======================================================================

OUT = WS / "data.json"
ASSETS = WS / "assets"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}

def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def get_json(url):
    return json.loads(get(url))

def log(msg):
    print(f"  {msg}")

# ---------- App Store ----------
def fetch_ios(app_id):
    if not app_id:
        return None
    try:
        data = get_json(f"https://itunes.apple.com/lookup?id={app_id}&country={COUNTRY}")
        if not data.get("results"):
            log(t("r.ios_not_found", id=app_id))
            return None
        r = data["results"][0]
        info = {
            "id": app_id,
            "title": r.get("trackName"),
            "subtitle": None,
            "description": r.get("description", ""),
            "rating": round(r.get("averageUserRating") or 0, 2),
            "ratingCount": r.get("userRatingCount", 0),
            "genre": r.get("primaryGenreName"),
            "version": r.get("version"),
            "url": r.get("trackViewUrl", "").split("?")[0],
            "icon": r.get("artworkUrl512") or r.get("artworkUrl100"),
            "screenshots": (r.get("screenshotUrls") or [])[:4],
            "languages": r.get("languageCodesISO2A") or [],
        }
        # Alt başlık API'de yok -> mağaza sayfasından dene (başarısızsa sorun değil)
        try:
            info["subtitle"] = _ios_subtitle(get(info["url"], timeout=20), info["title"])
        except Exception:
            pass
        log(t("r.ios_ok", title=info['title'], n=info['ratingCount']))
        return info
    except Exception as e:
        log(t("r.ios_error", id=app_id, e=e))
        return None

def _ios_subtitle(html, title):
    """Alt başlık iTunes API'sinde YOK; mağaza sayfasından çıkarılır.

    Sayfadaki `serialized-server-data` JSON'unda uygulamanın kendi düğümü
    (`lockup`) alt başlığı taşır — ama aynı JSON'da "benzer uygulamalar" rafı da
    subtitle alanlarıyla dolu. Bu yüzden ADI eşleşen düğüm seçilir; yoksa None
    döner. Yanlış uygulamanın alt başlığını yayın doğrulamasına sokmak, hiç
    okuyamamaktan kötüdür."""
    m = re.search(r'<script[^>]*id="serialized-server-data"[^>]*>(.*?)</script>', html, re.S)
    if m:
        try:
            found = []

            def walk(o):
                if isinstance(o, dict):
                    st = o.get("subtitle")
                    if isinstance(st, str) and st.strip():
                        found.append(((o.get("name") or o.get("title") or ""), st.strip()))
                    for v in o.values():
                        walk(v)
                elif isinstance(o, list):
                    for v in o:
                        walk(v)

            walk(json.loads(unescape(m.group(1))))
            want = (title or "").strip().lower()
            for name, st in found:
                if want and str(name).strip().lower() == want:
                    return st
        except Exception:
            pass
    # eski sayfa yapısı için yedek
    m = re.search(r'class="product-header__subtitle[^"]*"[^>]*>\s*(.*?)\s*<', html, re.S)
    return unescape(m.group(1)).strip() if m else None


# ---------- Google Play ----------
def fetch_play(pkg):
    if not pkg:
        return None
    url = f"https://play.google.com/store/apps/details?id={pkg}&hl=en&gl=US"
    try:
        html = get(url)
    except Exception as e:
        log(t("r.play_error", id=pkg, e=e))
        return None
    info = {"id": pkg, "title": None, "short": None, "description": None,
            "rating": None, "ratingCount": None, "installs": None, "url": url}
    m = re.search(r'itemprop="name"[^>]*>\s*(?:<[^>]+>)*([^<]+)', html)
    if m:
        info["title"] = unescape(m.group(1)).strip()
    if not info["title"]:
        m = re.search(r"<title[^>]*>(.*?)(?:\s*-\s*(?:Apps|Android Apps) on Google Play)?</title>", html, re.S)
        if m:
            info["title"] = unescape(m.group(1)).strip()
    # Kısa açıklama iki meta etiketinde birden duruyor; ikisi de attribute sırası
    # değişimine dayanıklı yazıldı (eski regex name/content arasına giren
    # property="og:description" yüzünden sessizce None döndürüyordu).
    m = (re.search(r'<meta[^>]*itemprop="description"[^>]*content="([^"]*)"', html)
         or re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', html))
    if m:
        info["short"] = unescape(m.group(1)).strip()
    m = re.search(r'data-g-id="description"[^>]*>(.*?)</div>', html, re.S)
    if m:
        info["description"] = unescape(re.sub(r"<[^>]+>", " ", m.group(1))).strip()
    # ld+json içinden puanlar
    m = re.search(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
    if m:
        try:
            ld = json.loads(m.group(1))
            agg = ld.get("aggregateRating") or {}
            if agg.get("ratingValue") is not None:
                info["rating"] = round(float(agg["ratingValue"]), 2)
            if agg.get("ratingCount") is not None:
                info["ratingCount"] = int(agg["ratingCount"])
        except Exception:
            pass
    # İndirme aralığı ("50+", "1M+" gibi) — birkaç desen dene
    for pat in (r'>([\d.,]+[KMB]?\+)</div>\s*<div[^>]*>\s*Downloads',
                r'\[\[\["([\d.,]+[KMB]?\+)"\]\]',
                r'"([\d.,]+[KMB]?\+)"[^"]{0,80}[Dd]ownloads'):
        m = re.search(pat, html)
        if m:
            info["installs"] = m.group(1)
            break
    log(t("r.play_ok", title=info['title'] or pkg, installs=info['installs'] or '?',
          n=info['ratingCount'] or '?'))
    return info

# ---------- iOS keyword sıralaması (çoklu ülke) ----------
def search_itunes(term, country, retry=True):
    q = urllib.parse.urlencode({"term": term, "country": country, "entity": "software", "limit": 200})
    try:
        return get_json("https://itunes.apple.com/search?" + q)
    except Exception as e:
        if retry:
            log(t("r.search_retry", c=country))
            time.sleep(25)
            return search_itunes(term, country, retry=False)
        log(t("r.search_error", c=country, e=e))
        return None

def estimate_metrics(results, term):
    """Arama hacmi ve zorluk TAHMİNİ (0-100).
    Gerçek hacim verisi halka açık değildir (App Radar/AppTweak de tahmin eder).
    Sinyaller: o kelimede sıralanan ilk 10 uygulamanın toplam puan kütlesi (talep göstergesi;
    mağaza, çok aranan kelimelerde popüler uygulamaları öne koyar) + kelimenin
    başlıklarda birebir geçme oranı (geliştiriciler hacimli kelimeyi başlığa taşır)."""
    top10 = results[:10]
    counts = sorted((r.get("userRatingCount") or 0) for r in top10)
    total = sum(counts)
    volume = min(100, round(math.log10(total + 1) / 7.5 * 100)) if total else 0
    t = term.lower()
    title_hits = sum(1 for r in top10 if t in (r.get("trackName") or "").lower())
    volume = min(100, volume + title_hits * 3)
    med = counts[len(counts) // 2] if counts else 0
    difficulty = min(100, round(math.log10(med + 1) / 6.5 * 100)) if med else 0
    return volume, difficulty

def keyword_rank_all(term, comp_ids, prev_map):
    """Bir kelimeyi tüm ülkelerde tarar: benim sıram, önceki sıram (delta için),
    tahmini hacim/zorluk, rakiplerin sıraları, ilk 3 uygulama."""
    entry = {"kw": term, "countries": {}}
    for c in COUNTRIES:
        data = search_itunes(term, c)
        time.sleep(RATE_SLEEP)
        if not data:
            continue
        results = data.get("results", [])
        my, comp_ranks = None, {}
        for i, r in enumerate(results, 1):
            tid = r.get("trackId")
            if tid == MY_IOS_ID and my is None:
                my = i
            if i <= 50 and tid in comp_ids and comp_ids[tid] not in comp_ranks:
                comp_ranks[comp_ids[tid]] = i
        volume, difficulty = estimate_metrics(results, term)
        entry["countries"][c] = {
            "myRank": my,
            "prev": (prev_map.get(term) or {}).get(c),
            "total": data.get("resultCount", 0),
            "volume": volume, "difficulty": difficulty,
            "top": [{"name": r.get("trackName"), "id": r.get("trackId"),
                     "ratings": r.get("userRatingCount") or 0} for r in results[:3]],
            "compRanks": comp_ranks,
        }
    ranked = {c: v["myRank"] for c, v in entry["countries"].items() if v["myRank"]}
    log(f'kw "{term}": ' + (", ".join(f"{c}#{r}" for c, r in ranked.items()) if ranked
                            else t("r.kw_unranked")))
    return entry

def build_prev_map(old_data):
    """Önceki data.json'dan kelime->ülke->sıra haritası (delta hesabı için).
    Eski tek ülkeli format da desteklenir."""
    m = {}
    for r in (old_data or {}).get("keywordRanks", []):
        if "countries" in r:
            m[r["kw"]] = {c: v.get("myRank") for c, v in r["countries"].items()}
        else:
            m[r["kw"]] = {(old_data or {}).get("country", "us"): r.get("myRank")}
    return m

# ---------- Etiket analizi ----------
STOP = set("""the a an and or of to in on for with your you our this that is are it as at
by from now new get will can all more most how its be has have was were we us my me they
them their than then so do does not no into over about also just like one two every each
any some when while where who what why if but too very much many off only via let lets
using use used way ways make makes made even still yet per out up down""".split())

def tokens(text):
    if not text:
        return []
    return [w for w in re.findall(r"[a-z]+", text.lower()) if len(w) > 2 and w not in STOP]

def bigrams(text):
    t = tokens(text)
    return [f"{a} {b}" for a, b in zip(t, t[1:])]

def tag_set(parts, with_bigrams=True):
    """Her metin parçasını AYRI tokenize eder — parçalar arası sahte bigram oluşmaz."""
    s = set()
    for p in parts:
        if not p:
            continue
        s |= set(tokens(p))
        if with_bigrams:
            s |= set(bigrams(p))
    return s

def build_tag_matrix(my_parts, comp_apps):
    """comp_apps: [(name, title_parts:list, all_parts:list)]"""
    my_set = tag_set(my_parts)
    scores = {}
    for name, title_parts, all_parts in comp_apps:
        title_set = tag_set(title_parts)
        seen = tag_set(all_parts, with_bigrams=False) | title_set
        for tag in seen:
            e = scores.setdefault(tag, {"tag": tag, "apps": [], "titleApps": []})
            e["apps"].append(name)
            if tag in title_set:
                e["titleApps"].append(name)
    rows = []
    for e in scores.values():
        n, t = len(e["apps"]), len(e["titleApps"])
        score = n + t * 2                       # başlıkta geçen etiket daha değerli
        if n < 2 and t == 0:
            continue                            # tek uygulamada, başlıkta bile değil -> gürültü
        rows.append({"tag": e["tag"], "usedBy": n, "inTitles": t, "score": score,
                     "apps": e["apps"], "mine": e["tag"] in my_set,
                     "opportunity": (e["tag"] not in my_set) and score >= 3})
    rows.sort(key=lambda r: (-r["score"], r["tag"]))
    return rows[:60]

# ---------- otomatik öneri kural motoru + ASO değişiklik planı ----------
def _my_visible_words(my_ios, my_play):
    """Mağazada GÖRÜNEN metinlerimin kelime kümesi (gizli iOS keywords alanı
    dışarıdan okunamaz — plan bunu ayrıca not eder)."""
    parts = []
    for app in (my_ios, my_play):
        if app:
            parts += [app.get("title"), app.get("subtitle"), app.get("short"), app.get("description")]
    return wordSetPy(" ".join(p for p in parts if p))

def wordSetPy(txt):
    s = set()
    for w in re.findall(r"[a-z]+", (txt or "").lower()):
        s.add(w)
        if len(w) > 4 and w.endswith("ing"):
            s.add(w[:-3])
        if len(w) > 3 and w.endswith("s"):
            s.add(w[:-1])
    return s

def _covers(term, words):
    ok = 0
    for w in term.lower().split():
        if w in words or (w.endswith("s") and w[:-1] in words) or (w + "s") in words \
           or (w.endswith("ing") and w[:-3] in words):
            ok += 1
    return ok == len(term.split())

def plan_id(key, **params):
    """Language-independent asoPlan id. The panel stores the user's ticks against
    it, so it must not change with the output language: it is ALWAYS derived from
    the Turkish action text (the only language earlier versions wrote), which keeps
    ids identical to theirs and existing ticks alive."""
    action_tr = t_lang("tr", f"plan.{key}.action", **params)
    return "plan-" + re.sub(r"\W+", "-", action_tr.lower())[:45].strip("-")


def build_recommendations(my_ios, my_play, ranks, tags, history):
    recs, plan = [], []
    def add(area, prio, title, detail):
        # id is positional (date + order), never text-derived -> same in every language
        recs.append({"id": f"auto-{date.today().isoformat()}-{len(recs)}",
                     "source": t("rec.source"), "area": area,
                     "priority": prio, "title": title, "detail": detail})
    def plan_add(store, field, key, reason, prio=2, **params):
        """key: stable item key (plan.<key>.action in mh_text); params fill the text."""
        plan.append({"id": plan_id(key, **params),
                     "store": store, "field": t(f"field.{field}"),
                     "action": t(f"plan.{key}.action", **params),
                     "reason": reason, "priority": prio})

    # --- kelime bazlı analiz ---
    flat = []   # (kw, country, cinfo)
    for r in ranks:
        for c, v in r.get("countries", {}).items():
            flat.append((r["kw"], c, v))
    ranked = [(kw, c, v) for kw, c, v in flat if v.get("myRank")]

    if KEYWORDS and flat and not ranked:
        add("aso", 1, t("rec.not_indexed.title", n=len(COUNTRIES)),
            t("rec.not_indexed.detail"))
        plan_add("both", "metadata", "publish", t("plan.publish.reason"), 1)
    elif ranked:
        best = min(ranked, key=lambda x: x[2]["myRank"])
        add("aso", 2, t("rec.best.title", kw=best[0], c=best[1].upper(), rank=best[2]["myRank"]),
            t("rec.best.detail"))

    my_words = _my_visible_words(my_ios, my_play)

    # Fırsat kelimeleri: hacim yüksek, zorluk makul, ben yokum/kötüyüm
    opps = []
    for r in ranks:
        cs = r.get("countries", {})
        if not cs:
            continue
        vols = [v["volume"] for v in cs.values()]
        difs = [v["difficulty"] for v in cs.values()]
        avg_vol = sum(vols) / len(vols)
        avg_dif = sum(difs) / len(difs)
        best_my = min((v["myRank"] for v in cs.values() if v.get("myRank")), default=None)
        score = avg_vol * (100 - avg_dif) / 100
        if (best_my is None or best_my > 30) and avg_vol >= 35:
            opps.append((score, r["kw"], round(avg_vol), round(avg_dif), best_my, cs))
    opps.sort(reverse=True)

    brand_terms = set(t.lower() for t in _cfg.get("brandTerms", []))
    for score, kw, vol, dif, best_my, cs in opps[:5]:
        covered = _covers(kw, my_words)
        top_c = max(cs.items(), key=lambda x: x[1]["volume"])[0]
        if kw.lower() in brand_terms:
            plan_add("ios", "hidden_kw", "brand", t("plan.brand.reason", vol=vol), 2, kw=kw)
            continue
        if not covered:
            pos = t("plan.add_visible.unranked") if not best_my else "#%d" % best_my
            plan_add("both", "visible", "add_visible",
                     t("plan.add_visible.reason", vol=vol, dif=dif, pos=pos), 1,
                     kw=kw, c=top_c.upper())
        else:
            pos = t("plan.boost.unranked") if not best_my else "#%d" % best_my
            plan_add("ios", "kw_sub", "boost",
                     t("plan.boost.reason", vol=vol, dif=dif, pos=pos), 2, kw=kw)

    # Rakip tehdidi: benim rakiplerim hangi kelimelerde ilk 10'da?
    threats = {}
    for kw, c, v in flat:
        for comp, cr in (v.get("compRanks") or {}).items():
            if cr <= 10:
                threats.setdefault(comp, []).append((kw, c, cr))
    for comp, hits in sorted(threats.items(), key=lambda x: -len(x[1]))[:3]:
        ex = ", ".join(f'"{k}" {c.upper()} #{r}' for k, c, r in hits[:3])
        add("radar", 2, t("rec.threat.title", comp=comp, n=len(hits)),
            t("rec.threat.detail", ex=ex))

    # Kırılabilir zirve: iyi konumda olduğum bir kelimede ilk 3 uygulama zayıfsa
    # (düşük puan kütlesi), yerel listing + puan itmesiyle ilk 3 gerçekçi hedeftir.
    weak_tops = []
    for r in ranks:
        for c, v in r.get("countries", {}).items():
            top = v.get("top") or []
            ratings = [t.get("ratings") for t in top if isinstance(t, dict)]
            if not ratings or any(x is None for x in ratings):
                continue  # eski format verisi — sıradaki taramada dolar
            if v.get("myRank") and v["myRank"] <= 30 and max(ratings) < 100 and (v.get("volume") or 0) >= 40:
                weak_tops.append((v["volume"], r["kw"], c, v["myRank"], max(ratings)))
    for vol, kw, c, my, strongest in sorted(weak_tops, reverse=True)[:2]:
        add("aso", 1, t("rec.weak_top.title", kw=kw, c=c.upper(), my=my),
            t("rec.weak_top.detail", strongest=strongest, vol=vol,
              lang=COUNTRY_LANG.get(c) or t("rec.weak_top.local")))

    # Lokalizasyon: hacimli ülkede dil desteğin yoksa
    langs = set((my_ios or {}).get("languages") or [])
    for c in COUNTRIES:
        need = COUNTRY_LANG.get(c)
        if not need or need in langs:
            continue
        c_vols = [v["volume"] for kw, cc, v in flat if cc == c]
        if c_vols and sum(c_vols) / len(c_vols) >= 30:
            plan_add("both", "localization", "localize",
                     t("plan.localize.reason", c=c.upper(), need=need,
                       avg=round(sum(c_vols) / len(c_vols))), 2,
                     c=c.upper(), need=need)

    # Hareket: önceki taramaya göre sıçrama/düşüş
    moves = [(kw, c, v["prev"], v["myRank"]) for kw, c, v in flat
             if v.get("prev") and v.get("myRank") and abs(v["prev"] - v["myRank"]) >= 10]
    for kw, c, p, n in sorted(moves, key=lambda m: m[2] - m[3], reverse=True)[:3]:
        if n < p:
            add("radar", 3, t("rec.rise.title", kw=kw, c=c.upper(), p=p, n=n),
                t("rec.rise.detail"))
        else:
            add("radar", 3, t("rec.drop.title", kw=kw, c=c.upper(), p=p, n=n),
                t("rec.drop.detail"))

    # --- uygulama sağlığı ---
    if my_ios:
        if (my_ios.get("ratingCount") or 0) < 50:
            add("roadmap", 1, t("rec.ios_ratings.title", n=my_ios.get('ratingCount', 0)),
                t("rec.ios_ratings.detail"))
        if str(my_ios.get("version", "")).startswith("0."):
            add("roadmap", 1, t("rec.version.title", v=my_ios.get('version')),
                t("rec.version.detail"))
    if my_play and (my_play.get("ratingCount") or 0) < 100:
        add("roadmap", 2, t("rec.play_ratings.title"), t("rec.play_ratings.detail"))

    if len(history) >= 2:
        prev, cur = history[-2], history[-1]
        for key in ("iosRatingCount", "playRatingCount"):
            a, b = prev.get(key), cur.get(key)
            if a is not None and b is not None and b > a:
                add("radar", 3, t("rec.growth.title", label=t("rec.label." + key), a=a, b=b),
                    t("rec.growth.detail"))

    plan_add("ios", "hidden_kw", "hidden_kw", t("plan.hidden_kw.reason"), 3)
    return recs, plan

# ---------- OTOMATİK İÇERİK DERLEYİCİ ----------
# Analizi sekme içeriğine çevirir: tag grupları, video tag seti, playbook öncelikleri.
# NOT: Mağaza METNİ (başlık/alt başlık/keywords/açıklama) üretimi bilerek KALDIRILDI —
# o metinler nüans ve marka/telif yargısı gerektirir; Claude'un advisor.json'daki denetimli
# önerileri ASO Merkezi'nin tek kaynağıdır. Motor burada yalnızca ham veri toplar.
def _phrase_scores(ranks):
    out = []
    for r in ranks:
        cs = r.get("countries", {})
        if not cs:
            continue
        vol = sum(v["volume"] for v in cs.values()) / len(cs)
        dif = sum(v["difficulty"] for v in cs.values()) / len(cs)
        best = min((v["myRank"] for v in cs.values() if v.get("myRank")), default=None)
        score = vol * (100 - dif) / 100 + (15 if best and best <= 50 else 0)
        out.append({"kw": r["kw"], "vol": round(vol), "dif": round(dif),
                    "best": best, "score": round(score, 1)})
    out.sort(key=lambda x: -x["score"])
    return out

def _keep_existing_playbook_ids(focus):
    """playbook.json'dan silinmiş yöntemlere odak işareti üretme. Playbook budandığında
    (madde advisor.json'a taşındı ya da kullanılmadığı için atıldı) burası sessizce
    ölü id üretmesin diye her taramada doğrulanır."""
    try:
        pb = json.loads((WS / "playbook.json").read_text(encoding="utf-8"))
    except Exception:
        return focus
    alive = {i["id"] for c in pb.get("categories", []) for i in c.get("items", [])}
    kept, dropped = [], []
    for f in focus:
        (kept if f["id"] in alive else dropped).append(f)
    if dropped:
        print(t("r.pb_dropped") +
              ", ".join(d["id"] for d in dropped))
    return kept


def build_auto_content(my_ios, my_play, ranks, tags):
    ps = _phrase_scores(ranks)

    # ASO metadata metni ARTIK ÜRETİLMİYOR (bkz. yukarıdaki not). ASO Merkezi'ndeki
    # öneriler yalnızca advisor.json'dan (Claude'un denetimli setinden) gelir.
    sugg = []

    # --- TAG BANKASI grubu + VIDEO SEO seti
    # "group" eski sürümlerle uyum için kalıyor; panel varsa "date" alanını kullanıp
    # etiketi kendi dilinde üretir (motorun çıktısı panelin dilini belirlemesin).
    tag_group = {"group": t("auto.tag_group", d=f"{date.today():%d.%m.%Y}"),
                 "date": f"{date.today():%d.%m.%Y}",
                 "tags": [p["kw"] for p in ps[:6]] +
                         [t["tag"] for t in tags if t.get("opportunity")][:6]}
    video_tags = list(dict.fromkeys(
        [MY_NAME.lower(), f"{MY_NAME.lower()} gameplay"] +
        [p["kw"] for p in ps[:8]] +
        [t["tag"] for t in tags if t.get("opportunity") and " " in t["tag"]][:4]))

    # --- PLAYBOOK odak işaretleri (veri koşulu -> yöntem)
    focus = []
    langs = set((my_ios or {}).get("languages") or [])
    missing = [c.upper() for c in COUNTRIES if COUNTRY_LANG.get(c) and COUNTRY_LANG[c] not in langs]
    if missing:
        focus.append({"id": "pb-aso-2", "why": t("focus.missing_langs", n=len(missing), cs=", ".join(missing[:6]))})
    if (my_ios and (my_ios.get("ratingCount") or 0) < 50) or (my_play and (my_play.get("ratingCount") or 0) < 100):
        focus.append({"id": "pb-aso-3", "why": t("focus.low_ratings")})
    any_ranked = any(v.get("myRank") for r in ranks for v in r.get("countries", {}).values())
    if any_ranked:
        focus.append({"id": "pb-meas-1", "why": t("focus.ranking")})
    # İndeks yokken ayrıca playbook odağı işaretlenmiyor: aynı sinyal zaten P1 öneri
    # ("hiçbir ülkede indekslenmemişsin") + P1 asoPlan maddesi olarak üretiliyor.
    focus = _keep_existing_playbook_ids(focus)

    return {"asoSuggestions": sugg, "tagGroup": tag_group,
            "videoTags": video_tags, "playbookFocus": focus,
            "keywordScores": ps}

# ---------- kreatif stüdyo için görsel indirme ----------
def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "app").lower()).strip("-")

def download(url, path):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r, open(path, "wb") as f:
            f.write(r.read())
        return True
    except Exception:
        return False

def download_assets(my_ios, comps):
    """İkonları ve iOS ekran görüntülerini assets/ klasörüne indirir —
    Kreatif Stüdyo'da referans/AI girdisi olarak kullanılır."""
    n = 0
    jobs = [("_benim", my_ios)] + [(c["name"], c["ios"]) for c in comps]
    for name, ios in jobs:
        if not ios:
            continue
        d = ASSETS / slugify(name)
        d.mkdir(parents=True, exist_ok=True)
        if ios.get("icon") and download(ios["icon"], d / "icon.jpg"):
            n += 1
        for i, s in enumerate(ios.get("screenshots") or [], 1):
            if download(s, d / f"ss{i}.jpg"):
                n += 1
    log(t("r.assets_done", n=n))

# ---------- ana akış ----------
def main():
    n_search = len(KEYWORDS) * len(COUNTRIES)
    print(t("r.header", dt=f"{datetime.now():%Y-%m-%d %H:%M}"))
    print(t("r.plan_line", cs=", ".join(c.upper() for c in COUNTRIES), k=len(KEYWORDS),
            c=len(COUNTRIES), n=n_search, m=n_search * RATE_SLEEP // 60 + 1))

    old_data = None
    if OUT.exists():
        try:
            old_data = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            pass
    prev_map = build_prev_map(old_data)

    print(t("r.my_app"))
    my_ios = fetch_ios(MY_IOS_ID)
    my_play = fetch_play(MY_PLAY_ID)

    print(t("r.competitors", n=len(COMPETITORS)))
    comps = []
    comp_ids = {}
    for c in COMPETITORS:
        print(f" {c['name']}")
        ios = fetch_ios(c["ios_id"])
        play = fetch_play(c["play_id"])
        if ios or play:
            comps.append({"name": c["name"], "ios": ios, "play": play})
            if c["ios_id"]:
                comp_ids[c["ios_id"]] = c["name"]
        time.sleep(1)

    print(t("r.kw_section", n=len(COUNTRIES)))
    ranks = []
    for i, kw in enumerate(KEYWORDS, 1):
        print(f" [{i}/{len(KEYWORDS)}] {kw}")
        ranks.append(keyword_rank_all(kw, comp_ids, prev_map))

    print(t("r.tag_section"))
    my_parts = []
    for app in (my_ios, my_play):
        if app:
            my_parts += [app.get("title"), app.get("subtitle"), app.get("short"), app.get("description")]
    comp_texts = []
    for c in comps:
        title_parts, all_parts = [], []
        for app in (c["ios"], c["play"]):
            if app:
                title_parts += [app.get("title"), app.get("subtitle")]
                all_parts += [app.get("title"), app.get("subtitle"),
                              app.get("short"), app.get("description")]
        comp_texts.append((c["name"], title_parts, all_parts))
    tags = build_tag_matrix(my_parts, comp_texts)
    opp = [t["tag"] for t in tags if t["opportunity"]][:10]
    log(t("r.tags_found", n=len(tags), o=len([x for x in tags if x["opportunity"]])))
    if opp:
        log(t("r.top_opps") + ", ".join(opp))

    # önceki history'yi koru
    history = (old_data or {}).get("history", [])
    all_ranks = [v["myRank"] for r in ranks for v in r["countries"].values() if v.get("myRank")]
    ranked_kws = sum(1 for r in ranks if any(v.get("myRank") for v in r["countries"].values()))
    snap = {
        "date": date.today().isoformat(),
        "iosRating": my_ios and my_ios["rating"],
        "iosRatingCount": my_ios and my_ios["ratingCount"],
        "playRating": my_play and my_play["rating"],
        "playRatingCount": my_play and my_play["ratingCount"],
        "playInstalls": my_play and my_play["installs"],
        "bestRank": min(all_ranks) if all_ranks else None,
        "rankedKeywords": ranked_kws,
        "ranks": {r["kw"]: {c: v.get("myRank") for c, v in r["countries"].items()}
                  for r in ranks},
    }
    history = [h for h in history if h.get("date") != snap["date"]] + [snap]

    recs, aso_plan = build_recommendations(my_ios, my_play, ranks, tags, history)
    auto = build_auto_content(my_ios, my_play, ranks, tags)
    log(t("r.summary", r=len(recs), p=len(aso_plan), v=len(auto["videoTags"]),
          f=len(auto["playbookFocus"])))

    if DOWNLOAD_ASSETS:
        print(t("r.downloading"))
        download_assets(my_ios, comps)

    data = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "country": COUNTRY,
        "countries": COUNTRIES,
        "myApp": {"name": MY_NAME, "ios": my_ios, "play": my_play},
        "competitors": comps,
        "keywordRanks": ranks,
        "tags": tags,
        "recommendations": recs,
        "asoPlan": aso_plan,
        "auto": auto,
        "history": history,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(t("r.written", name=OUT.name))

if __name__ == "__main__":
    main()
