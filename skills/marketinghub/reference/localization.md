# Phase 3 — Localization packs

Fill `localization[]` in `workspace/advisor.json`. Each entry is a complete
store listing for one market, plus that market's screenshot headings.

## The one rule everything follows from

**A locale is a separate keyword research job, not a translation.** Germans do
not search a translated version of your English phrase; they search what Germans
type. Translating your metadata word-for-word produces fluent copy that ranks
for nothing.

In practice, per market: look at what the apps ranking there actually call
themselves (their titles on that storefront), the local everyday word for the
category, and the local phrasing of the user's core benefit. Then build the
title / subtitle / keyword field from *those* words.

## Choosing the markets

Pick from evidence in `data.json`, not from a list of big economies:

- countries where `keywordRanks[*].countries[cc].myRank` already shows a
  beatable position;
- countries in `config.json > countries` where `myApp.ios.languages` has no
  local listing — the entire market is currently served an English page;
- markets where the top 3 for a target term have weak rating mass.

Write the evidence into `why`. A pack without a data reason is filler.

## Field rules per locale

Limits are the same as the source language: `iosTitle` 30 · `iosSub` 30 ·
`iosKw` 100 · `gpShort` 80 · `gpLong` 4000. German, Finnish, Turkish, Hungarian
and the Indic languages expand compounds — a 28-character English title often
does not fit, so re-phrase rather than truncate.

- **Brand name stays.** Keep it byte-identical in Latin-script locales. In
  non-Latin scripts you may transliterate it — but decide once and be consistent
  across every field of that locale; the audit checks the brand is present in
  the title.
- **Adapt the keyword field, never invent.** Same concept list as the source
  language, expressed in words that market searches. If a concept has no local
  equivalent, drop it and spend the characters on the next concept — do not pad
  with geo terms ("calorie tracker germany").
- **No repetition** across title/subtitle/keywords, exactly as in the source
  language. The Localization Audit flags every locale where the keyword field
  repeats a word already in the title — that is wasted budget in every market at
  once, and it is the most common finding.
- **Verbatim atoms survive untouched**: URLs, email addresses, Apple product
  names, product codes, numbers with units. A translated support address is a
  dead mailbox; a translated URL is a 404.
- **`screens`** must match `config.json > screenHeadings` in count and order.
  Headings are marketing copy, not UI strings: translate for meaning and search
  value. ALL-CAPS mirrors only into scripts that have case — drop it for CJK,
  Arabic, Hebrew, Thai and Indic. Keep them short: agglutinative languages force
  the renderer to shrink the font.
- **RTL**: Arabic and Hebrew are laid out automatically by Creative Studio's
  renderer. Do not add directional marks by hand.

## Do all locales in one pass, then audit

Never do one locale, ask the user to review it, and generalise from that. Nobody
can review 40 languages, and reviewing one proves nothing about the other 39.
Write the whole set, then let the panel's **Localization Audit** check it:

character limits per field · brand name preserved · fields identical to the
source language (i.e. untranslated) · keyword-field spacing, duplicates and
overlap with the title · Latin-script leakage in non-Latin locales · screen
heading count · unused keyword-field characters.

Then spot-read 2-3 entries yourself, including one non-Latin script, and say in
your report which locales are unverified guesses.

## Export

```bash
python export_metadata.py          # writes workspace/export/asc/… and /play/…
python export_metadata.py --check  # limits only
```

Apple and Google want different locale codes for the same language (Apple: `tr`,
`pl`, `ru`, but `ar-SA`, `pt-BR`, `de-DE`; Play: `tr-TR`, `ru-RU`, but `ar`).
The mapping lives in `export_metadata.py > LOCALES`; a locale missing from it is
skipped with a warning, so add the code there when you add a new market.

Per-locale **privacy policy URL is mandatory** for App Store submission and this
tool does not generate one — list it as a manual step for the user.
