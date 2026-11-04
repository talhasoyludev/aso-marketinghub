# Show HN draft

Post by hand. Best window is a weekday morning US Eastern time. Link the GitHub repo directly. Stay in the thread for the first few hours and reply to every comment, including the critical ones.

HN guidelines to keep in mind: no asking for upvotes, no voting rings, the title should say what it is plainly, and the first comment should explain the background.

## Title (78 characters, limit 80)

```
Show HN: MarketingHub – Local, free ASO dashboard for mobile apps, Claude Code
```

Alternatives:

```
Show HN: Local ASO dashboard where Claude writes copy and a scanner checks it
Show HN: Free App Store and Play keyword tracking with Python stdlib and Claude
```

## URL

https://github.com/talhasoyludev/aso-marketinghub

## First comment

Hi HN, I'm Talha, an indie mobile developer from Turkey. I built this for my own apps.

ASO (App Store Optimization) for a small app usually means one of three things: a paid subscription that costs more than the app earns, a spreadsheet, or asking an LLM for a subtitle that ignores what your competitors are doing. I wanted something in between that ran locally and didn't require an account.

MarketingHub has three parts that are kept strictly apart:

- A scanner (`refresh.py`, Python standard library only) that reads public App Store and Google Play pages: keyword rankings per country via the iTunes search endpoint, your live listing, competitor listings, and a tag matrix of which words competitors use and how many put them in their title. Each run appends to a history.
- A panel (one `index.html`, served locally) that turns this into an audit: character limits, brand terms in visible text, untranslated locales, opportunity keywords.
- A Claude Code skill that reads the scan and writes the store copy and per-market localization packs into a JSON file. The scanner never writes copy, and Claude never edits measurements.

Two design decisions I'd like feedback on:

1. **Read-back verification.** Nothing is shown as published until the next scan reads that exact text from the live store. The iOS keyword field can't be read publicly, so it is labelled unverifiable instead.
2. **The skill as a written method.** Instead of a single prompt, the skill is a set of phases and rules: never present the volume estimate as search volume, every recommendation must cite something observable in the scan, end each session by listing what wasn't done.

What it can't do: real search volume (the 0-100 volume/difficulty scores are estimates from rating counts and title usage), Play rankings (no public API), and fast scans (it's rate-limited on purpose, about 3 seconds per request).

There's a demo with a fictional app: clone and run `python -m http.server 8137`, then open `localhost:8137/?demo=1` (or `demo.bat` / `./demo.command`).

MIT licensed. Your config and scans stay in a git-ignored folder; the only outbound requests go to the public store pages.

Happy to answer questions about the scraping, the skill structure, or ASO for small apps.
