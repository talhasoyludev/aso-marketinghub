# X (Twitter) drafts

Post by hand. Check that the personal claims (e.g. "tools cost more than my apps earn") are true for you before posting. Attach `docs/media/demo.gif` to tweet 1. Keep the repo link out of tweet 1 (link posts get less reach); put it in the last tweet and in a reply.

## Thread (EN, 7 tweets)

**1/**
I make small mobile apps. Search is the only growth channel I can afford, and ASO tools cost more than my apps earn.

So I built a free, local ASO dashboard that Claude Code runs for me.

Here's how it works and what I learned.

[attach demo.gif]

**2/**
It's three parts, kept strictly apart:

- a scanner that measures (rankings, competitor keywords, your live listing)
- a panel that turns it into decisions
- Claude, which writes the store copy

The scanner never writes copy. Claude never touches the numbers.

**3/**
The scanner reads public App Store and Play pages. No API keys, no account.

- keyword rankings in every country you track
- which words competitors put in their titles
- history across every scan

Python standard library only. No pip install.

**4/**
The feature I use most is the dumbest one: read-back.

After you paste new metadata into the console, the next scan reads the live listing and diffs it.

Nothing counts as "published" until the store shows it. The iOS keyword field can't be read, so it's marked unverifiable.

**5/**
Claude writes the copy through a Claude Code skill, not a one-off prompt.

The rules that mattered most:
- volume is an estimate, never call it search volume
- every recommendation must cite something in the data
- end by listing what you didn't do

**6/**
Honest limits:

- no real search volume (paid tools are good at that)
- no Play rankings, Google has no public API
- scans are slow on purpose, rate-limited

It's for everything around those numbers: tracking, localizing, writing, verifying.

**7/**
Free, MIT, data stays on your machine.

Try the demo with a fictional app, no setup:
git clone, then demo.bat / ./demo.command

github.com/talhasoyludev/aso-marketinghub

## Standalone tweets (EN)

**A**
ASO tip for small apps: a keyword where the top 3 results have six-figure rating counts is not winnable this quarter.

Look for terms where you rank 10-60 and the apps above you are weak.

I built a free local tool that finds those for you: github.com/talhasoyludev/aso-marketinghub

**B**
If a competitor puts a word in their 30-character App Store title, they think people search for it.

Count that across 10 competitors and you have a free demand signal.

MarketingHub builds that tag matrix automatically. Free, local, MIT.
github.com/talhasoyludev/aso-marketinghub

**C**
The rule that made my Claude Code ASO skill useful:

"A recommendation without a data hook is noise."

"Post more on TikTok" is banned.
"No preview video while 6 of 8 competitors have one" is allowed.

The whole skill is open source: github.com/talhasoyludev/aso-marketinghub

## Kısa Türkçe versiyon (3 tweet)

**1/**
Küçük mobil uygulamalar geliştiriyorum. ASO araçlarının aylık ücreti, uygulamalarımın kazancından fazla.

Ben de yerelde çalışan, ücretsiz bir ASO paneli yaptım; analizi Claude Code yürütüyor.

[demo.gif ekle]

**2/**
Tarayıcı ölçüyor: ülke ülke sıralamalar, rakiplerin başlıkta kullandığı kelimeler, canlı mağaza metnin.
Claude yazıyor: mağaza metni, dil paketleri, tarihli öneriler.
Panel doğruluyor: mağazadan geri okunmayan hiçbir şey "yayında" sayılmıyor.

**3/**
API anahtarı yok, üyelik yok, verin bilgisayarında kalıyor. MIT lisanslı.

Kurgusal bir uygulamayla demoyu tek komutla açabilirsin:
github.com/talhasoyludev/aso-marketinghub
