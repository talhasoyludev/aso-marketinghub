# LinkedIn gönderisi (TR)

Elle paylaşılacak. `docs/media/demo.gif` ya da ASO Merkezi ekran görüntüsünü ekle. Linki gönderinin içine değil, ilk yoruma koymak erişimi genelde artırıyor. Kendi deneyiminle örtüşmeyen cümleleri değiştir; sayı uydurma.

---

Küçük mobil uygulamalar geliştiren biri olarak en büyük sorunum hep aynıydı: uygulamayı yapıyorsun, mağazaya koyuyorsun ve kimse bulamıyor.

Bağımsız geliştirici için en uygun büyüme kanalı mağaza araması. Ama ASO araçları şirket bütçesine göre fiyatlanıyor. Yapay zekâya "daha iyi bir alt başlık yaz" demek de yetmiyor; rakiplerinin ne yaptığını, hangi ülkede kaçıncı sırada olduğunu bilmiyor.

Bu yüzden kendi uygulamalarım için MarketingHub'ı geliştirdim ve açık kaynak olarak paylaştım.

Nasıl çalışıyor:

→ Bir tarayıcı, herkese açık App Store ve Google Play sayfalarını okuyor: takip ettiğin her ülkede kelime sıralamaların, rakiplerin başlıklarında kullandığı kelimeler, canlı mağaza metnin. Her tarama geçmişe ekleniyor.

→ Yerelde çalışan bir panel bunu karara çeviriyor: karakter limitleri, çevrilmemiş diller, görünür metinde rakip marka adı, kaçırılan fırsat kelimeleri.

→ Mağaza metnini, dil paketlerini ve tarihli önerileri Claude Code yazıyor; ama tek seferlik bir prompt'la değil, repoda belgelenmiş bir yöntemle. Her öneri veride gözlenebilen bir şeye dayanmak zorunda.

→ Yayınladıktan sonraki taramada canlı sayfa geri okunuyor. Mağazada görünmeyen hiçbir şey "yayında" sayılmıyor.

Neyi yapmadığını da açıkça yazdım: gerçek arama hacmi vermiyor (skorlar tahmin), Google Play'in herkese açık sıralama verisi yok, tarama hız sınırı yüzünden bilerek yavaş.

Ücretsiz, MIT lisanslı, API anahtarı ya da üyelik gerektirmiyor; verin kendi bilgisayarında kalıyor. Kurgusal bir örnek uygulamayla demoyu tek komutla açabilirsin.

Mobil uygulama geliştiren, ASO ile uğraşan ya da Claude Code ile iş akışı kuran biriyseniz geri bildiriminizi çok isterim.

Link ilk yorumda.

#ASO #MobilUygulama #BağımsızGeliştirici #AçıkKaynak #ClaudeCode #iOS #Android

---

**İlk yorum:**

GitHub: https://github.com/talhasoyludev/aso-marketinghub
Türkçe README: https://github.com/talhasoyludev/aso-marketinghub/blob/main/README.tr.md
