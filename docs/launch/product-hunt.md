# Product Hunt draft

Post by hand. Launch at 00:01 Pacific time on a Tuesday, Wednesday or Thursday. Do not ask people to upvote; ask them to look and leave feedback. Product Hunt penalises vote-ring patterns.

## Name

MarketingHub

## Tagline (56 characters, limit 60)

```
Free, local ASO dashboard for mobile apps, run by Claude
```

Alternatives:

```
ASO for indie apps: measured locally, written by Claude
Track App Store rankings and fix your listing, for free
```

## Description (246 characters, limit 260)

```
Open-source ASO dashboard that runs on your machine. A scanner tracks App Store rankings across countries and competitor keywords; Claude Code writes your store copy and translations; nothing counts as published until it's read back. No API keys.
```

## Topics

Developer Tools, Marketing, Open Source, Artificial Intelligence, iOS, Android

## Links

- Website: https://github.com/talhasoyludev/aso-marketinghub
- Pricing: Free

## Maker's first comment

Hi Product Hunt, I'm Talha, an indie mobile developer.

Search is the main way small apps get found, but ASO tools are priced for companies, and asking an AI for a new subtitle doesn't tell it what your competitors are doing. MarketingHub is the tool I built for my own apps to close that gap.

**What it does**

- **Measures** from the public stores: your keyword rankings in every App Store country you track, your competitors' listings, and which words they put in their titles. Every scan is kept, so you see trends.
- **Audits** your listing in a local dashboard: character limits, untranslated locales, competitor brand names in visible text, missing opportunity keywords.
- **Writes** the copy through Claude Code: store metadata, per-market localization packs and dated recommendations, following a documented method. Every recommendation has to point at something in the data.
- **Verifies**: after you publish, the next scan reads the live listing back. Nothing is marked live until the store shows it.

**What it doesn't do**

It doesn't give you real search volume (the scores are estimates), Google Play has no public ranking data, and scans are deliberately slow to respect rate limits.

**Try it in 30 seconds**

Clone the repo and run `demo.bat` or `./demo.command`. It opens with a fictional sample app, no setup.

It's free and MIT licensed, with no account. Your data stays on your computer.

I'd like to hear what you'd want it to measure next.

## Gallery shot list (1270×760)

Capture from the demo (`?demo=1`) so no real app data appears.

1. **Hero:** the panel overview with the app header and tab bar visible. Overlay text: "Free, local ASO dashboard. No API keys."
2. **Competitor Radar:** rankings table across countries with up/down deltas visible. Overlay: "Keyword rankings in every country you track."
3. **Tag matrix:** competitor tag matrix with opportunity tags highlighted. Overlay: "See which words competitors bet their titles on."
4. **ASO Center:** metadata fields with character counters and the publish verification panel showing one verified and one pending field. Overlay: "Nothing counts as published until it's read back."
5. **Localization:** the audit with a mix of passing and flagged locales. Overlay: "Audit every locale: limits, brand terms, untranslated fields."
6. **Creative Studio:** a batch of rendered store screenshots in several languages, including one RTL. Overlay: "Store screenshots at real resolutions, every language."
7. **Claude Code:** a terminal showing the "do the ASO analysis for my app" prompt and the Done / Findings / Needs the user summary. Overlay: "Claude writes the copy, following a documented method."
8. **Video (optional):** `docs/media/demo.gif` re-exported as MP4, under 60 seconds.
