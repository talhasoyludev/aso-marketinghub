# -*- coding: utf-8 -*-
"""
ASO Radar veri toplayıcı
=========================================
Çalıştır:  python refresh.py   (veya refresh.bat'a çift tıkla)

Ne yapar:
 1. Senin uygulamanın ve rakiplerin App Store / Google Play verilerini çeker
    (puan, puan sayısı, indirme aralığı, başlık, açıklama).
 2. Rakip metinlerinden etiket (tag) frekans analizi çıkarır ve senin
    metadata'nla kıyaslar -> fırsat etiketleri işaretler.
 3. Takip listesindeki her anahtar kelime için iTunes aramasında kaçıncı
    sırada olduğunu ölçer (iOS keyword rank tracking).
 4. Her çalıştırmada ölçümleri data.json'daki history'ye ekler; site bunu
    otomatik rapor olarak gösterir.

Ayarlar aşağıda — rakip eklemek için COMPETITORS listesine satır ekle.
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

# Windows konsolu (cp1254) Unicode karakterlerde patlamasın
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ================== AYARLAR (config.json'dan okunur) ==================
BASE = Path(__file__).resolve().parent
# Kullanıcıya ait her şey workspace/ altında durur: kod ağacı (repo) ile kişisel
# veri (config, tarama çıktısı, görseller) bilerek ayrılmıştır — repo herkese
# açık paylaşılabilir, workspace/ paylaşılmaz.
WS = BASE / "workspace"
if not (WS / "config.json").exists():
    sys.exit("workspace/config.json yok — önce `python setup.py` çalıştır "
             "(şablonu kopyalar ve doldurman gereken alanları söyler).")
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
            log(f"iOS {app_id}: bulunamadı")
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
        log(f"iOS  ✓ {info['title']}  ({info['ratingCount']} puan)")
        return info
    except Exception as e:
        log(f"iOS {app_id}: HATA {e}")
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
        log(f"Play {pkg}: HATA {e}")
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
    log(f"Play ✓ {info['title'] or pkg}  ({info['installs'] or '?'} indirme, {info['ratingCount'] or '?'} puan)")
    return info

# ---------- iOS keyword sıralaması (çoklu ülke) ----------
def search_itunes(term, country, retry=True):
    q = urllib.parse.urlencode({"term": term, "country": country, "entity": "software", "limit": 200})
    try:
        return get_json("https://itunes.apple.com/search?" + q)
    except Exception as e:
        if retry:
            log(f"  {country}: hız limiti/hata — 25 sn bekleyip tekrar denenecek")
            time.sleep(25)
            return search_itunes(term, country, retry=False)
        log(f"  {country}: HATA {e}")
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
                            else "hiçbir ülkede ilk 200'de değil"))
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

def build_recommendations(my_ios, my_play, ranks, tags, history):
    recs, plan = [], []
    def add(area, prio, title, detail):
        recs.append({"id": f"auto-{date.today().isoformat()}-{len(recs)}",
                     "source": "kural motoru", "area": area,
                     "priority": prio, "title": title, "detail": detail})
    def plan_add(store, field, action, reason, prio=2):
        plan.append({"id": "plan-" + re.sub(r"\W+", "-", action.lower())[:45].strip("-"),
                     "store": store, "field": field, "action": action,
                     "reason": reason, "priority": prio})

    # --- kelime bazlı analiz ---
    flat = []   # (kw, country, cinfo)
    for r in ranks:
        for c, v in r.get("countries", {}).items():
            flat.append((r["kw"], c, v))
    ranked = [(kw, c, v) for kw, c, v in flat if v.get("myRank")]

    if KEYWORDS and flat and not ranked:
        add("aso", 1, f"{len(COUNTRIES)} ülkenin hiçbirinde indekslenmemişsin",
            "Taranan tüm ülkelerde, tüm kelimelerde ilk 200 dışındasın. Tek çözüm: ASO "
            "Merkezi'ndeki metadata'yı mağazaya YAYINLAMAK. Yayın sonrası indeksleme 7-14 gün "
            "sürer; günlük tarama ile değişimi izle.")
        plan_add("both", "metadata", "ASO Merkezi'ndeki başlık/alt başlık/keywords/açıklama setini olduğu gibi yayınla",
                 "Hiçbir ülkede hiçbir kelimede indeksin yok — diğer her aksiyon bunun arkasında beklemeli.", 1)
    elif ranked:
        best = min(ranked, key=lambda x: x[2]["myRank"])
        add("aso", 2, f'En iyi konumun: "{best[0]}" — {best[1].upper()} #{best[2]["myRank"]}',
            "En güçlü olduğun kelime/ülke ikilisine yüklen: o kelimeyi görünür alanlara taşı, "
            "o ülkenin dilinde listing aç, içerik üret.")

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
            plan_add("ios", "keywords (gizli alan)",
                     f'"{kw}" MARKA adıdır: görünür metne yazma; gizli keywords alanında parçalarını tut',
                     f"Tahmini hacim {vol}/100 ama marka hakkı riski var (görünür kullanımı Google politikası + telif ihlali). "
                     "Gizli alan + o kelimede sıralanmak için puan kütlesi/indirme hızı artır.", 2)
            continue
        if not covered:
            plan_add("both", "başlık/alt başlık/açıklama",
                     f'"{kw}" öbeğini görünür metadata\'na ekle (öncelik: {top_c.upper()})',
                     f"Tahmini hacim {vol}/100, zorluk {dif}/100, sen {'ilk 200 dışında' if not best_my else '#%d' % best_my} — "
                     "kelime görünür metinlerinde HİÇ geçmiyor, indekslenmen imkansız.", 1)
        else:
            plan_add("ios", "keywords/alt başlık",
                     f'"{kw}" için ağırlığı artır: kelimeyi alt başlığa/başlığa yaklaştır',
                     f"Kelime metinlerinde var ama sıralaman {'yok' if not best_my else '#%d' % best_my}. "
                     f"Hacim {vol}/100, zorluk {dif}/100 — alan içi konum (başlık>alt başlık>açıklama) ağırlığı belirler.", 2)

    # Rakip tehdidi: benim rakiplerim hangi kelimelerde ilk 10'da?
    threats = {}
    for kw, c, v in flat:
        for comp, cr in (v.get("compRanks") or {}).items():
            if cr <= 10:
                threats.setdefault(comp, []).append((kw, c, cr))
    for comp, hits in sorted(threats.items(), key=lambda x: -len(x[1]))[:3]:
        ex = ", ".join(f'"{k}" {c.upper()} #{r}' for k, c, r in hits[:3])
        add("radar", 2, f"{comp} senin kelimelerinde ilk 10'da ({len(hits)} yerde)",
            f"Örnek: {ex}. Bu niş dolmaya başlamış — aynı kelimelere metadata + puan kütlesiyle yüklenmezsen boşluğu onlar kapatır.")

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
        add("aso", 1, f'Kırılabilir zirve: "{kw}" {c.upper()} — sen #{my}, ilk 3 zayıf',
            f"Bu kelimede ilk 3'teki en güçlü uygulamanın yalnızca {strongest} puanı var (hacim {vol}/100). "
            f"{COUNTRY_LANG.get(c, 'yerel')} dilinde listing + 50-100 gerçek puan + o ülkeye içerik = ilk 3 gerçekçi hedef.")

    # Lokalizasyon: hacimli ülkede dil desteğin yoksa
    langs = set((my_ios or {}).get("languages") or [])
    for c in COUNTRIES:
        need = COUNTRY_LANG.get(c)
        if not need or need in langs:
            continue
        c_vols = [v["volume"] for kw, cc, v in flat if cc == c]
        if c_vols and sum(c_vols) / len(c_vols) >= 30:
            plan_add("both", "lokalizasyon",
                     f"{c.upper()} için {need} dilinde mağaza sayfası aç",
                     f"{c.upper()} ortalama kelime hacmi {round(sum(c_vols)/len(c_vols))}/100 ama uygulaman {need} dilini desteklemiyor — o ülkenin kendi dilindeki aramalarda görünmüyorsun.", 2)

    # Hareket: önceki taramaya göre sıçrama/düşüş
    moves = [(kw, c, v["prev"], v["myRank"]) for kw, c, v in flat
             if v.get("prev") and v.get("myRank") and abs(v["prev"] - v["myRank"]) >= 10]
    for kw, c, p, n in sorted(moves, key=lambda m: m[2] - m[3], reverse=True)[:3]:
        if n < p:
            add("radar", 3, f'Yükseliş: "{kw}" {c.upper()} #{p} → #{n}',
                "Momentum var — bu kelimeye içerik ve görünür metadata ağırlığı ver.")
        else:
            add("radar", 3, f'Düşüş: "{kw}" {c.upper()} #{p} → #{n}',
                "Rakip hamlesi veya indeks güncellemesi olabilir; metadata'da bu kelimenin ağırlığını koru.")

    # --- uygulama sağlığı ---
    if my_ios:
        if (my_ios.get("ratingCount") or 0) < 50:
            add("roadmap", 1, f"iOS puan sayısı çok düşük ({my_ios.get('ratingCount', 0)})",
                "Puan kütlesi sıralamanın yakıtıdır: aynı metadata ile bile puanı artan uygulama yükselir. "
                "In-app review prompt'u yüksek duygu anına bağla; ilk 100 puanı topla.")
        if str(my_ios.get("version", "")).startswith("0."):
            add("roadmap", 1, f"Sürüm hâlâ {my_ios.get('version')} — 1.0 sinyali ver",
                "0.x sürümü kullanıcıya ve editörlere 'bitmemiş' der. 1.0.0'ı lansman güncellemesi olarak çıkar.")
    if my_play and (my_play.get("ratingCount") or 0) < 100:
        add("roadmap", 2, "Play puan sayısı 100 altında",
            "Play'de yorum sayısı ve hızı sıralama sinyalidir. In-App Review API + yorumlara yanıt.")

    if len(history) >= 2:
        prev, cur = history[-2], history[-1]
        for key, label in (("iosRatingCount", "iOS puan sayısı"), ("playRatingCount", "Play puan sayısı")):
            a, b = prev.get(key), cur.get(key)
            if a is not None and b is not None and b > a:
                add("radar", 3, f"{label} arttı: {a} → {b}",
                    "Büyüme sinyali — hangi aksiyonun işe yaradığını not et ve tekrarla.")

    plan_add("ios", "keywords (gizli alan)",
             "Gizli keywords alanını dışarıdan doğrulayamam — ASO Merkezi'ndeki 100 karakterlik setle birebir aynı olduğundan emin ol",
             "iTunes API görünür alanları verir; gizli alan yalnızca App Store Connect'te görünür.", 3)
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
        print("   ! playbook.json'da olmayan odak id atlandı: " +
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
    tag_group = {"group": f"📡 Radar otomatik — {date.today():%d.%m.%Y}",
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
        focus.append({"id": "pb-aso-2", "why": f"Hacim olan {len(missing)} ülkede ({', '.join(missing[:6])}) yerel listing yok"})
    if (my_ios and (my_ios.get("ratingCount") or 0) < 50) or (my_play and (my_play.get("ratingCount") or 0) < 100):
        focus.append({"id": "pb-aso-3", "why": "Puan kütlesi kritik düşük — sıralama yakıtın bu"})
    any_ranked = any(v.get("myRank") for r in ranks for v in r.get("countries", {}).values())
    if any_ranked:
        focus.append({"id": "pb-meas-1", "why": "Sıralamalar oluşmaya başladı — günlük Δ takibi şart"})
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
    log(f"{n} görsel workspace/assets/ klasörüne indirildi")

# ---------- ana akış ----------
def main():
    n_search = len(KEYWORDS) * len(COUNTRIES)
    print(f"ASO Radar — {datetime.now():%Y-%m-%d %H:%M}")
    print(f"Ülkeler: {', '.join(c.upper() for c in COUNTRIES)} · {len(KEYWORDS)} kelime × "
          f"{len(COUNTRIES)} ülke = {n_search} arama (~{n_search * RATE_SLEEP // 60 + 1} dk sürer)\n")

    old_data = None
    if OUT.exists():
        try:
            old_data = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            pass
    prev_map = build_prev_map(old_data)

    print("Kendi uygulaman:")
    my_ios = fetch_ios(MY_IOS_ID)
    my_play = fetch_play(MY_PLAY_ID)

    print(f"\nRakipler ({len(COMPETITORS)}):")
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

    print(f"\niOS keyword sıralamaları ({len(COUNTRIES)} ülke):")
    ranks = []
    for i, kw in enumerate(KEYWORDS, 1):
        print(f" [{i}/{len(KEYWORDS)}] {kw}")
        ranks.append(keyword_rank_all(kw, comp_ids, prev_map))

    print("\nEtiket analizi...")
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
    log(f"{len(tags)} etiket, {len([t for t in tags if t['opportunity']])} fırsat bulundu")
    if opp:
        log("İlk fırsatlar: " + ", ".join(opp))

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
    log(f"{len(recs)} öneri + {len(aso_plan)} plan maddesi + otomatik içerik "
        f"({len(auto['videoTags'])} video tag, {len(auto['playbookFocus'])} playbook odağı) üretildi. "
        f"ASO metadata metni motor tarafından üretilmiyor — advisor.json (Claude) esastır.")

    if DOWNLOAD_ASSETS:
        print("\nGörseller indiriliyor...")
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
    print(f"\n✓ {OUT.name} yazıldı — siteyi yenile, Rakip Radar sekmesine bak.")

if __name__ == "__main__":
    main()
