# -*- coding: utf-8 -*-
"""Message catalog for the Python side (refresh.py, setup.py, export_metadata.py).

Every console line and every rule-engine text written into data.json lives here
in English and Turkish. The language is chosen once at import:

    1. MARKETINGHUB_LANG environment variable, if set
    2. workspace/config.json > lang
    3. templates/config.json > lang
    4. "en"

Anything other than "en" / "tr" falls back to "en".

Usage:  from mh_text import t;  t("key", name=value)
`t_lang("tr", key, ...)` renders a specific language regardless of the active
one — refresh.py uses it to derive language-independent ids from the Turkish
text, so ids stay identical to what earlier (Turkish-only) versions produced.

Stdlib only, Python 3.9+.
"""
import json
import os
from pathlib import Path

SUPPORTED = ("en", "tr")
DEFAULT = "en"
BASE = Path(__file__).resolve().parent


def _config_lang(base):
    """Raw `lang` value from workspace/config.json, then templates/config.json."""
    for p in (base / "workspace" / "config.json", base / "templates" / "config.json"):
        try:
            v = json.loads(p.read_text(encoding="utf-8")).get("lang")
        except Exception:
            continue
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def raw_lang(base=BASE):
    """Requested language as written (env override, then config) — not normalised.
    setup.py uses it to pick a playbook template for languages beyond en/tr."""
    env = os.environ.get("MARKETINGHUB_LANG", "").strip()
    return env or _config_lang(base) or DEFAULT


def normalize(lang):
    lang = (lang or "").strip().lower()
    return lang if lang in SUPPORTED else DEFAULT


def detect_lang(base=BASE):
    return normalize(raw_lang(base))


LANG = detect_lang()


def set_lang(lang):
    """Switch the active language (setup.py after migrating config; tests)."""
    global LANG
    LANG = normalize(lang)
    return LANG


def t_lang(lang, key, /, **kw):
    # positional-only so placeholders may themselves be called "lang" / "key"
    entry = MESSAGES[key]
    text = entry.get(normalize(lang)) or entry[DEFAULT]
    return text.format(**kw) if kw else text


def t(key, /, **kw):
    return t_lang(LANG, key, **kw)


# key: {"en": ..., "tr": ...}  — placeholders use str.format names.
MESSAGES = {
    # ------------------------------------------------------------ refresh.py
    "r.no_config": {
        "en": "workspace/config.json not found — run `python setup.py` first "
              "(it copies the template and tells you which fields to fill in).",
        "tr": "workspace/config.json yok — önce `python setup.py` çalıştır "
              "(şablonu kopyalar ve doldurman gereken alanları söyler).",
    },
    "r.ios_not_found": {"en": "iOS {id}: not found", "tr": "iOS {id}: bulunamadı"},
    "r.ios_ok": {"en": "iOS  ✓ {title}  ({n} ratings)", "tr": "iOS  ✓ {title}  ({n} puan)"},
    "r.ios_error": {"en": "iOS {id}: ERROR {e}", "tr": "iOS {id}: HATA {e}"},
    "r.play_error": {"en": "Play {id}: ERROR {e}", "tr": "Play {id}: HATA {e}"},
    "r.play_ok": {
        "en": "Play ✓ {title}  ({installs} installs, {n} ratings)",
        "tr": "Play ✓ {title}  ({installs} indirme, {n} puan)",
    },
    "r.search_retry": {
        "en": "  {c}: rate limit/error — waiting 25 s, then retrying",
        "tr": "  {c}: hız limiti/hata — 25 sn bekleyip tekrar denenecek",
    },
    "r.search_error": {"en": "  {c}: ERROR {e}", "tr": "  {c}: HATA {e}"},
    "r.kw_unranked": {
        "en": "not in the top 200 in any country",
        "tr": "hiçbir ülkede ilk 200'de değil",
    },
    "r.pb_dropped": {
        "en": "   ! skipped focus ids not found in playbook.json: ",
        "tr": "   ! playbook.json'da olmayan odak id atlandı: ",
    },
    "r.assets_done": {
        "en": "{n} images downloaded to workspace/assets/",
        "tr": "{n} görsel workspace/assets/ klasörüne indirildi",
    },
    "r.header": {"en": "ASO Radar — {dt}", "tr": "ASO Radar — {dt}"},
    "r.plan_line": {
        "en": "Countries: {cs} · {k} keywords × {c} countries = {n} searches (takes ~{m} min)\n",
        "tr": "Ülkeler: {cs} · {k} kelime × {c} ülke = {n} arama (~{m} dk sürer)\n",
    },
    "r.my_app": {"en": "Your app:", "tr": "Kendi uygulaman:"},
    "r.competitors": {"en": "\nCompetitors ({n}):", "tr": "\nRakipler ({n}):"},
    "r.kw_section": {
        "en": "\niOS keyword rankings ({n} countries):",
        "tr": "\niOS keyword sıralamaları ({n} ülke):",
    },
    "r.tag_section": {"en": "\nTag analysis...", "tr": "\nEtiket analizi..."},
    "r.tags_found": {
        "en": "{n} tags, {o} opportunities found",
        "tr": "{n} etiket, {o} fırsat bulundu",
    },
    "r.top_opps": {"en": "Top opportunities: ", "tr": "İlk fırsatlar: "},
    "r.summary": {
        "en": "Generated {r} recommendations + {p} plan items + auto content "
              "({v} video tags, {f} playbook focus items). The engine does not write "
              "ASO metadata copy — advisor.json (Claude) is the source of truth.",
        "tr": "{r} öneri + {p} plan maddesi + otomatik içerik "
              "({v} video tag, {f} playbook odağı) üretildi. "
              "ASO metadata metni motor tarafından üretilmiyor — advisor.json (Claude) esastır.",
    },
    "r.downloading": {"en": "\nDownloading images...", "tr": "\nGörseller indiriliyor..."},
    "r.written": {
        "en": "\n✓ {name} written — reload the panel and open the Competitor Radar tab.",
        "tr": "\n✓ {name} yazıldı — siteyi yenile, Rakip Radar sekmesine bak.",
    },

    # ---- rule engine: values written into data.json
    "rec.source": {"en": "rule engine", "tr": "kural motoru"},
    "rec.not_indexed.title": {
        "en": "Not indexed in any of your {n} countries",
        "tr": "{n} ülkenin hiçbirinde indekslenmemişsin",
    },
    "rec.not_indexed.detail": {
        "en": "You're outside the top 200 for every keyword in every scanned country. "
              "The only fix: PUBLISH the metadata from the ASO Center to the store. "
              "Indexing takes 7-14 days after release; watch the change with daily scans.",
        "tr": "Taranan tüm ülkelerde, tüm kelimelerde ilk 200 dışındasın. Tek çözüm: ASO "
              "Merkezi'ndeki metadata'yı mağazaya YAYINLAMAK. Yayın sonrası indeksleme 7-14 gün "
              "sürer; günlük tarama ile değişimi izle.",
    },
    "rec.best.title": {
        "en": 'Your best position: "{kw}" — {c} #{rank}',
        "tr": 'En iyi konumun: "{kw}" — {c} #{rank}',
    },
    "rec.best.detail": {
        "en": "Double down on your strongest keyword/country pair: move that keyword into "
              "visible fields, open a listing in that country's language, create content for it.",
        "tr": "En güçlü olduğun kelime/ülke ikilisine yüklen: o kelimeyi görünür alanlara taşı, "
              "o ülkenin dilinde listing aç, içerik üret.",
    },
    "rec.threat.title": {
        "en": "{comp} is top 10 for your keywords ({n} spots)",
        "tr": "{comp} senin kelimelerinde ilk 10'da ({n} yerde)",
    },
    "rec.threat.detail": {
        "en": "For example: {ex}. This niche is filling up — if you don't push the same keywords "
              "with metadata and rating mass, they'll take the gap.",
        "tr": "Örnek: {ex}. Bu niş dolmaya başlamış — aynı kelimelere metadata + puan kütlesiyle "
              "yüklenmezsen boşluğu onlar kapatır.",
    },
    "rec.weak_top.title": {
        "en": 'Beatable top 3: "{kw}" {c} — you\'re #{my}, the top 3 are weak',
        "tr": 'Kırılabilir zirve: "{kw}" {c} — sen #{my}, ilk 3 zayıf',
    },
    "rec.weak_top.detail": {
        "en": "The strongest app in this keyword's top 3 has only {strongest} ratings (volume {vol}/100). "
              "A {lang}-language listing + 50-100 real ratings + content for that country = "
              "a realistic shot at the top 3.",
        "tr": "Bu kelimede ilk 3'teki en güçlü uygulamanın yalnızca {strongest} puanı var (hacim {vol}/100). "
              "{lang} dilinde listing + 50-100 gerçek puan + o ülkeye içerik = ilk 3 gerçekçi hedef.",
    },
    "rec.weak_top.local": {"en": "local", "tr": "yerel"},
    "rec.rise.title": {
        "en": 'Rising: "{kw}" {c} #{p} → #{n}',
        "tr": 'Yükseliş: "{kw}" {c} #{p} → #{n}',
    },
    "rec.rise.detail": {
        "en": "There's momentum — give this keyword content and more weight in visible metadata.",
        "tr": "Momentum var — bu kelimeye içerik ve görünür metadata ağırlığı ver.",
    },
    "rec.drop.title": {
        "en": 'Falling: "{kw}" {c} #{p} → #{n}',
        "tr": 'Düşüş: "{kw}" {c} #{p} → #{n}',
    },
    "rec.drop.detail": {
        "en": "Could be a competitor move or an index update; keep this keyword's weight in your metadata.",
        "tr": "Rakip hamlesi veya indeks güncellemesi olabilir; metadata'da bu kelimenin ağırlığını koru.",
    },
    "rec.ios_ratings.title": {
        "en": "Very few iOS ratings ({n})",
        "tr": "iOS puan sayısı çok düşük ({n})",
    },
    "rec.ios_ratings.detail": {
        "en": "Rating mass is what fuels rankings: with the same metadata, the app whose ratings grow "
              "climbs. Tie the in-app review prompt to a high-emotion moment and collect your first 100 ratings.",
        "tr": "Puan kütlesi sıralamanın yakıtıdır: aynı metadata ile bile puanı artan uygulama yükselir. "
              "In-app review prompt'u yüksek duygu anına bağla; ilk 100 puanı topla.",
    },
    "rec.version.title": {
        "en": "Still on version {v} — signal 1.0",
        "tr": "Sürüm hâlâ {v} — 1.0 sinyali ver",
    },
    "rec.version.detail": {
        "en": "A 0.x version tells users and editors 'unfinished'. Ship 1.0.0 as your launch update.",
        "tr": "0.x sürümü kullanıcıya ve editörlere 'bitmemiş' der. 1.0.0'ı lansman güncellemesi olarak çıkar.",
    },
    "rec.play_ratings.title": {
        "en": "Fewer than 100 Play ratings",
        "tr": "Play puan sayısı 100 altında",
    },
    "rec.play_ratings.detail": {
        "en": "On Play, review count and velocity are ranking signals. Use the In-App Review API and reply to reviews.",
        "tr": "Play'de yorum sayısı ve hızı sıralama sinyalidir. In-App Review API + yorumlara yanıt.",
    },
    "rec.growth.title": {"en": "{label} up: {a} → {b}", "tr": "{label} arttı: {a} → {b}"},
    "rec.growth.detail": {
        "en": "Growth signal — note which action worked and repeat it.",
        "tr": "Büyüme sinyali — hangi aksiyonun işe yaradığını not et ve tekrarla.",
    },
    "rec.label.iosRatingCount": {"en": "iOS rating count", "tr": "iOS puan sayısı"},
    "rec.label.playRatingCount": {"en": "Play rating count", "tr": "Play puan sayısı"},

    # ---- ASO change plan (asoPlan). "field" values are badges, also translated.
    "field.metadata": {"en": "metadata", "tr": "metadata"},
    "field.hidden_kw": {"en": "keywords (hidden field)", "tr": "keywords (gizli alan)"},
    "field.visible": {"en": "title/subtitle/description", "tr": "başlık/alt başlık/açıklama"},
    "field.kw_sub": {"en": "keywords/subtitle", "tr": "keywords/alt başlık"},
    "field.localization": {"en": "localization", "tr": "lokalizasyon"},

    "plan.publish.action": {
        "en": "Publish the title/subtitle/keywords/description set from the ASO Center as is",
        "tr": "ASO Merkezi'ndeki başlık/alt başlık/keywords/açıklama setini olduğu gibi yayınla",
    },
    "plan.publish.reason": {
        "en": "You're not indexed for any keyword in any country — every other action waits on this.",
        "tr": "Hiçbir ülkede hiçbir kelimede indeksin yok — diğer her aksiyon bunun arkasında beklemeli.",
    },
    "plan.brand.action": {
        "en": '"{kw}" is a BRAND name: keep it out of visible copy; keep its parts in the hidden keywords field',
        "tr": '"{kw}" MARKA adıdır: görünür metne yazma; gizli keywords alanında parçalarını tut',
    },
    "plan.brand.reason": {
        "en": "Estimated volume {vol}/100, but there's a trademark risk (visible use breaks Google policy "
              "and infringes the mark). Use the hidden field, and grow rating mass/download velocity to rank for it.",
        "tr": "Tahmini hacim {vol}/100 ama marka hakkı riski var (görünür kullanımı Google politikası + telif ihlali). "
              "Gizli alan + o kelimede sıralanmak için puan kütlesi/indirme hızı artır.",
    },
    "plan.add_visible.action": {
        "en": 'Add "{kw}" to your visible metadata (priority: {c})',
        "tr": '"{kw}" öbeğini görünür metadata\'na ekle (öncelik: {c})',
    },
    "plan.add_visible.reason": {
        "en": "Estimated volume {vol}/100, difficulty {dif}/100, you're {pos} — "
              "the phrase appears NOWHERE in your visible copy, so you can't get indexed for it.",
        "tr": "Tahmini hacim {vol}/100, zorluk {dif}/100, sen {pos} — "
              "kelime görünür metinlerinde HİÇ geçmiyor, indekslenmen imkansız.",
    },
    "plan.add_visible.unranked": {"en": "outside the top 200", "tr": "ilk 200 dışında"},
    "plan.boost.action": {
        "en": 'Give "{kw}" more weight: move it closer to the subtitle/title',
        "tr": '"{kw}" için ağırlığı artır: kelimeyi alt başlığa/başlığa yaklaştır',
    },
    "plan.boost.reason": {
        "en": "The keyword is in your copy, but your rank is {pos}. Volume {vol}/100, difficulty {dif}/100 — "
              "where it sits (title > subtitle > description) sets its weight.",
        "tr": "Kelime metinlerinde var ama sıralaman {pos}. "
              "Hacim {vol}/100, zorluk {dif}/100 — alan içi konum (başlık>alt başlık>açıklama) ağırlığı belirler.",
    },
    "plan.boost.unranked": {"en": "none", "tr": "yok"},
    "plan.localize.action": {
        "en": "Open a {need}-language store listing for {c}",
        "tr": "{c} için {need} dilinde mağaza sayfası aç",
    },
    "plan.localize.reason": {
        "en": "{c} has an average keyword volume of {avg}/100, but your app doesn't support {need} — "
              "you're invisible in searches in that country's own language.",
        "tr": "{c} ortalama kelime hacmi {avg}/100 ama uygulaman {need} dilini desteklemiyor — "
              "o ülkenin kendi dilindeki aramalarda görünmüyorsun.",
    },
    "plan.hidden_kw.action": {
        "en": "I can't verify the hidden keywords field from outside — make sure it matches "
              "the 100-character set in the ASO Center exactly",
        "tr": "Gizli keywords alanını dışarıdan doğrulayamam — ASO Merkezi'ndeki 100 karakterlik "
              "setle birebir aynı olduğundan emin ol",
    },
    "plan.hidden_kw.reason": {
        "en": "The iTunes API returns the visible fields; the hidden field is only visible in App Store Connect.",
        "tr": "iTunes API görünür alanları verir; gizli alan yalnızca App Store Connect'te görünür.",
    },

    # ---- auto content
    "auto.tag_group": {"en": "📡 Radar automatic — {d}", "tr": "📡 Radar otomatik — {d}"},
    "focus.missing_langs": {
        "en": "No local listing in {n} countries with volume ({cs})",
        "tr": "Hacim olan {n} ülkede ({cs}) yerel listing yok",
    },
    "focus.low_ratings": {
        "en": "Rating mass is critically low — it's what fuels your rankings",
        "tr": "Puan kütlesi kritik düşük — sıralama yakıtın bu",
    },
    "focus.ranking": {
        "en": "Rankings are starting to form — track the daily Δ",
        "tr": "Sıralamalar oluşmaya başladı — günlük Δ takibi şart",
    },

    # ------------------------------------------------------------ setup.py
    "s.root_found": {
        "en": "{name} is in the repo root — `python setup.py` moves it to workspace/",
        "tr": "{name} kök dizinde — `python setup.py` workspace'e taşır",
    },
    "s.moved": {
        "en": " {name} → moved to workspace/ (from the old layout)",
        "tr": " {name} → workspace/ taşındı (eski yerleşimden)",
    },
    "s.ws_missing": {"en": "workspace/{name} missing", "tr": "workspace/{name} yok"},
    "s.template_hint": {"en": " — template: templates/{tpl}", "tr": " — şablon: templates/{tpl}"},
    "s.created": {
        "en": " workspace/{name} created from template",
        "tr": " workspace/{name} şablondan oluşturuldu",
    },
    "s.tpl_missing": {"en": "templates/{tpl} not found", "tr": "templates/{tpl} bulunamadı"},
    "s.no_config": {"en": "config.json missing", "tr": "config.json yok"},
    "s.bad_active": {
        "en": "config.json: activeApp doesn't point to a block under apps",
        "tr": "config.json: activeApp, apps içindeki bir bloğa işaret etmiyor",
    },
    "s.name_tpl": {
        "en": "config.json: apps.<app>.name is still the template value",
        "tr": "config.json: apps.<app>.name hâlâ şablon değerinde",
    },
    "s.need_id": {
        "en": "config.json: at least one of iosId or playId is required",
        "tr": "config.json: iosId veya playId'den en az biri gerekli",
    },
    "s.no_keywords": {
        "en": "config.json: keywords list is empty — the radar has nothing to measure",
        "tr": "config.json: keywords listesi boş — radar ölçecek bir şey bulamaz",
    },
    "s.play_example": {
        "en": "config.json: playId is still the example value",
        "tr": "config.json: playId hâlâ örnek değerinde",
    },
    "s.config_bad_json": {
        "en": "config.json is not valid JSON: {e}",
        "tr": "config.json geçerli JSON değil: {e}",
    },
    "s.data_ok": {"en": " workspace/data.json", "tr": " workspace/data.json"},
    "s.data_missing": {
        "en": " workspace/data.json missing — no scan yet",
        "tr": " workspace/data.json yok — henüz tarama yapılmadı",
    },
    "s.adv_count": {
        "en": " workspace/advisor.json — {n} entries",
        "tr": " workspace/advisor.json — {n} kayıt",
    },
    "s.adv_empty": {
        "en": " workspace/advisor.json is empty — no Claude analysis yet",
        "tr": " workspace/advisor.json boş — henüz Claude analizi yapılmadı",
    },
    "s.adv_bad_json": {
        "en": "advisor.json is not valid JSON: {e}",
        "tr": "advisor.json geçerli JSON değil: {e}",
    },
    "s.problems": {"en": "Missing:", "tr": "Eksikler:"},
    "s.fix_hint": {
        "en": "\nNext step: fill in workspace/config.json with your own app "
              "(field notes are inside the file), then run this script again.",
        "tr": "\nSıradaki adım: workspace/config.json'u kendi uygulamanla doldur "
              "(alan açıklamaları dosyanın içinde), sonra bu betiği tekrar çalıştır.",
    },
    "s.done": {"en": "Setup complete. Next steps:", "tr": "Kurulum tamam. Sıradaki adımlar:"},
    "s.step1": {
        "en": "   1. python refresh.py        → store scan, writes workspace/data.json",
        "tr": "   1. python refresh.py        → mağaza taraması, workspace/data.json üretir",
    },
    "s.step2": {
        "en": "   2. start.bat / start.command → open the panel",
        "tr": "   2. start.bat / start.command → paneli aç",
    },
    "s.step3": {
        "en": "   3. In Claude Code: \"do the ASO analysis for my app\" "
              "(loads skills/marketinghub and writes advisor.json)",
        "tr": "   3. Claude Code'da: \"bu uygulamanın ASO analizini yap\" "
              "(skills/marketinghub yükleyip advisor.json'u üretir)",
    },

    # ------------------------------------------------------- export_metadata.py
    "e.lang.en": {"en": "English (source)", "tr": "İngilizce (kaynak)"},
    "e.lang.tr": {"en": "Turkish", "tr": "Türkçe"},
    "e.lang.de": {"en": "German", "tr": "Almanca"},
    "e.lang.pl": {"en": "Polish", "tr": "Lehçe"},
    "e.lang.ar": {"en": "Arabic", "tr": "Arapça"},
    "e.lang.es": {"en": "Spanish", "tr": "İspanyolca"},
    "e.lang.pt-BR": {"en": "Portuguese (BR)", "tr": "Portekizce (BR)"},
    "e.lang.fr": {"en": "French", "tr": "Fransızca"},
    "e.lang.ru": {"en": "Russian", "tr": "Rusça"},
    "e.no_mapping": {
        "en": "  ! {code}: no Apple/Play locale mapping, skipped",
        "tr": "  ! {code}: Apple/Play kod eşlemesi yok, atlandı",
    },
    "e.title": {"en": "Language pack export", "tr": "Dil paketi dışa aktarımı"},
    "e.no_advisor": {"en": "workspace/advisor.json not found — run `python setup.py`, then the Claude analysis, before exporting.",
                     "tr": "workspace/advisor.json bulunamadı — dışa aktarmadan önce `python setup.py` ve ardından Claude analizini çalıştır."},
    "e.check_only": {"en": " (check only)", "tr": " (yalnızca denetim)"},
    "e.col_lang": {"en": "language", "tr": "dil"},
    "e.written": {"en": "✓ {n} files written → {path}", "tr": "✓ {n} dosya yazıldı → {path}"},
    "e.missing": {
        "en": "\nEmpty fields ({n}) — fill them in the store by hand or add them to advisor.json:",
        "tr": "\nBoş alanlar ({n}) — mağazada elle doldurulacak ya da advisor.json'a eklenecek:",
    },
    "e.over_limit": {
        "en": "\n✗ OVER LIMIT — the store will reject this copy:",
        "tr": "\n✗ LİMİT AŞIMI — mağaza bu yazımı reddeder:",
    },
    "e.ok": {
        "en": "\n✓ All fields are within the character limits.",
        "tr": "\n✓ Tüm alanlar karakter limitleri içinde.",
    },
    "e.privacy_note": {
        "en": "Note: a privacy policy URL is REQUIRED for every locale (App Store submission "
              "fails per locale without it) — this tool doesn't generate one; enter it in ASC "
              "for each language.",
        "tr": "Not: Gizlilik politikası URL'i her locale için ZORUNLU (App Store "
              "gönderiminde locale başına hata verir) — bu araç URL üretmez, "
              "ASC'de dil dil gir.",
    },
}
