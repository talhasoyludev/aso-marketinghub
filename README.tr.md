# MarketingHub

**Mobil uygulamalar için yerel ASO & büyüme paneli — analizini Claude Code üretir.**

🇬🇧 [English README](README.md)

MarketingHub birbirinden kesin çizgiyle ayrılmış iki parçadır:

- **tarayıcı** (`refresh.py`): uygulamanı ve rakiplerini herkese açık mağaza
  sayfalarından ölçer — ülke ülke sıralamalar, rakip etiket matrisi, fırsat
  etiketleri, canlı mağaza metinleri, zaman içindeki geçmiş;
- **panel** (`index.html`): bu veriyi karara çevirir — ve kendi başına metin
  uydurmaz.

Panelde *metin* olarak gördüğün her şey — mağaza metadata'sı, pazar bazlı
lokalizasyon paketleri, tarihli öneriler — bir analiz oturumunda Claude
tarafından üretilir ve `workspace/advisor.json`'a yazılır. Bunu üretme yöntemi
repoda bir Claude Code skill'i olarak gelir; böylece herkes aynı analizi kendi
uygulaması için baştan yaptırabilir.

Üyelik yok, SaaS yok, API anahtarı gerekmiyor. Python 3 ve bir tarayıcı yeter.

---

## Hızlı başlangıç

```bash
python setup.py       # workspace/'i şablonlardan oluşturur, eksikleri söyler
```

Sonra `workspace/config.json`'u kendi uygulamanla doldur (mağaza kimlikleri,
kelimeler, rakipler — her alanın açıklaması dosyanın içinde) ve:

```bash
python refresh.py     # mağaza taraması → workspace/data.json (dakikalar sürer)
```

Paneli `start.bat` (Windows) ya da `start.command` (macOS) ile aç — `index.html`
dosyasına **çift tıklama**; `file://` üzerinden JSON dosyaları okunamaz.

Son olarak Claude Code'da, proje klasöründen:

```
bu uygulamanın ASO analizini yap
```

Claude `skills/marketinghub/` skill'ini yükler, taramayı okur ve panelin
gösterdiği mağaza metinlerini, lokalizasyon paketini ve tarihli önerileri
`workspace/advisor.json`'a yazar.

## Panel ne veriyor

| Sekme | Ne yapar |
|---|---|
| **Yol Haritası** | Görevler, danışman önerileri + tarayıcının mağaza planından üretilir. Elle yazılmış faz listesi yok. |
| **Danışman** | İki kaynak: kural motoru (her taramada veriden) ve Claude'un tarihli analizleri. |
| **Rakip Radar** | Ülke bazlı sıralamalar ve değişimler, rakip karşılaştırması, etiket matrisi, fırsat etiketleri. |
| **ASO Merkezi** | Canlı karakter sayaçlı metadata alanları, mağazadan **geri okuyan yayın doğrulama** paneli ve otomatik metadata denetimi. |
| **Video SEO** | Taramanın kelimelerinden üretilen YouTube başlık şablonları ve tag setleri. |
| **Tag Bankası** | Radardan, fırsat etiketlerinden ve dil paketlerinden türeyen kelime grupları. |
| **Lokalizasyon** | Pazar bazlı paketler + **otomatik denetim**: karakter limitleri, marka korunması, çevrilmemiş alanlar, keyword hijyeni, script karışması. |
| **Kampanya** | UTM link üretici, kampanya kaydı, CPI yorumu ve Firebase'de nereye bakılacağı. |
| **Playbook** | Hâlâ karar bekleyen büyütme yöntemleri — biriktirilmez, budanır. |
| **Kreatif Stüdyo** | Mağaza görseli üretici (gerçek çözünürlükler, RTL uyumlu, tüm dillerde toplu üretim) ve AI video brief'leri. |
| **Claude Desteği** | Kendi uygulamanın verisiyle doldurulmuş prompt şablonları. |
| **Rapor & KPI** | Her taramadan otomatik geçmiş + opsiyonel el girişi konsol verisi. |

İki ilke araca gömülüdür, disipline bırakılmamıştır:

- **Donmuş içerik yok.** Kodda elle yazılmış kelime listesi, kontrol listesi ya
  da örnek metin durmaz. Her liste `config.json`'dan, taramadan ya da advisor
  dosyasından türetilir.
- **Geri okunmadıysa yayınlanmamıştır.** Paneldeki metin asla "yayında" diye
  raporlanmaz; önce taramanın o değeri mağazadan birebir okuması gerekir.
  Okunamayan alan (iOS'un gizli keywords alanı) sessizce atlanmaz,
  "doğrulanamaz" olarak işaretlenir.

## İki ayrı akış

| Ne yapmak istiyorsun | Komut | Port | Hangi veri |
|---|---|---|---|
| **Kendi çalışmanı görmek** | `start.bat` / `start.command` | 8137 | `workspace/` — senin config, tarama ve analizlerin |
| **Yayın halini denemek** | `release.bat` / `release.command` | 8138 | temiz kopya, şablon workspace — repoyu klonlayan biri ne görüyorsa o |

`release.bat` şunu yapar: kod ağacını `../MarketingHub-release` klasörüne kopyalar
(`workspace/`, `.git/`, `__pycache__/` hariç), kişisel veri sızmadığını denetler,
`setup.py`'yi çalıştırır ve paneli 8138'de açar. Kendi klasörüne dokunmaz —
ikisini aynı anda açık tutabilirsin.

Yayınlanacak arşivi üretmek için:

```bash
python make_release.py --zip
```

## Dosya düzeni

```
index.html              panel (12 sekme), aşağıdaki JSON'ları okur
refresh.py              mağaza tarayıcı + kural motoru → workspace/data.json
setup.py                ilk kurulum ve sağlık kontrolü
export_metadata.py      advisor.json → dil dil, mağazaya girilebilir metin dosyaları
i18n/                   panel dilleri (tr, en) — kendi dilini ekleyebilirsin
templates/              ilk çalıştırmada workspace/'e kopyalanan şablonlar
skills/marketinghub/    Claude Code skill'i: analizin nasıl üretileceği
make_release.py         yayınlanabilir temiz kopya üretir (kişisel veri yok)
workspace/              SENİN verin — git'e girmez, paylaşılmaz
```

`workspace/` altında `config.json`, `data.json`, `advisor.json`,
`playbook.json`, indirilen mağaza görselleri ve metadata dışa aktarımı durur.
`.gitignore`'da olması bilinçlidir: repoyu fork'la, analizin sende kalsın.

## Dil

Panel Türkçe ve İngilizce gelir; başlıktaki seçiciden değiştirilir (tarayıcıda
saklanır, varsayılanı `config.json > lang`).

Yeni dil eklemek için: `i18n/tr.json`'u kopyala, `ui` altına
`"<Türkçe metin>": "<çeviri>"` çiftlerini yaz, `prompts` ve `briefs`'i çevir,
`i18n/<kod>.json` olarak kaydet ve kodu `index.html`'deki `LANGS` listesine
ekle. Sözlükte olmayan metin bozulmaz, Türkçe kalır.

Not: Python betikleri ilerleme çıktısını hâlâ Türkçe basıyor; kalan eksik bu.

## Gereksinimler

- Python 3.9+ (yalnızca standart kütüphane — pip install yok)
- Bir tarayıcı
- Analiz fazları için Claude Code (opsiyonel ama aracın asıl amacı bu)

Mağaza verisi herkese açık sayfalardan çekilir; API anahtarı ve hesap gerekmez.
Play herkese açık sıralama API'si vermediği için Play tarafı, sıralama yerine
etiket matrisi ve değişiklik planı üzerinden optimize edilir.

## Lisans

MIT — bkz. [LICENSE](LICENSE).
