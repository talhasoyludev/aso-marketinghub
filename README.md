# MarketingHub

**A local ASO & growth cockpit for mobile apps, driven by Claude Code.**

🇹🇷 [Türkçe README](README.tr.md)

MarketingHub is two things that stay strictly separated:

- a **scanner** (`refresh.py`) that measures your app and your competitors from
  the public stores — rankings across countries, competitor tag matrix,
  opportunity tags, live listing text, history over time;
- a **panel** (`index.html`) that turns that data into decisions — and never
  invents text of its own.

Everything the panel shows as *copy* — store metadata, per-market localization
packs, dated recommendations — is produced by Claude in an analysis session and
written to `workspace/advisor.json`. The method for producing it ships with the
repo as a Claude Code skill, so anyone can reproduce the whole analysis for
their own app.

No signup, no SaaS, no API keys required. Python 3 and a browser.

---

## Quick start

```bash
python setup.py       # seeds workspace/ from templates, tells you what is missing
```

Then fill in `workspace/config.json` (store IDs, keywords, competitors — every
field is documented inside the file), and:

```bash
python refresh.py     # store scan → workspace/data.json (minutes; rate-limited)
```

Open the panel with `start.bat` (Windows) or `start.command` (macOS) — **not** by
double-clicking `index.html`; `file://` cannot read the JSON files.

Finally, in Claude Code, from the project folder:

```
do the ASO analysis for my app
```

Claude loads `skills/marketinghub/`, reads the scan, and writes
`workspace/advisor.json` — the store copy, the localization pack and the dated
recommendations the panel then displays.

## What the panel gives you

| Tab | What it does |
|---|---|
| **Roadmap** | Tasks generated from the advisor's recommendations + the scanner's store plan. No hand-written phase list. |
| **Advisor** | Two sources: the rule engine (data-driven, every scan) and Claude's dated analyses. |
| **Competitor Radar** | Rankings per country with deltas, competitor comparison, tag matrix, opportunity tags. |
| **ASO Center** | The metadata fields with live character counters, a **publish verification** panel that reads your live listing back from the store, and an automatic metadata audit. |
| **Video SEO** | YouTube title templates and tag sets generated from the scan's keywords. |
| **Tag Bank** | Keyword groups derived from the radar, opportunity tags, and per-language keyword sets. |
| **Localization** | The per-market packs plus an **automatic audit**: character limits, brand preservation, untranslated fields, keyword hygiene, script contamination. |
| **Campaigns** | UTM link builder, campaign log, CPI verdict, and where to look in Firebase. |
| **Playbook** | Growth methods still awaiting a decision — pruned, not accumulated. |
| **Creative Studio** | Store screenshot renderer (real store resolutions, RTL-aware, batch across every language) and AI video ad briefs. |
| **Claude Prompts** | Prompt templates filled with your app's own data. |
| **Reports & KPI** | Automatic history from every scan + optional manual console data. |

Two principles are enforced by the tool, not by discipline:

- **Nothing frozen.** No hand-written keyword lists, checklists or example copy
  live in the code. Every list is derived from `config.json`, the scan, or the
  advisor file.
- **Read back or it didn't happen.** Text in the panel is never reported as
  published; the scan has to read that exact value back from the store first.
  What cannot be read (the hidden iOS keywords field) is labelled unverifiable
  rather than silently skipped.

## Two separate flows

| What you want | Command | Port | Which data |
|---|---|---|---|
| **See your own work** | `start.bat` / `start.command` | 8137 | `workspace/` — your config, scans and analyses |
| **Test the published version** | `release.bat` / `release.command` | 8138 | a clean copy with a template workspace — exactly what someone cloning the repo sees |

`release.bat` copies the code tree to `../MarketingHub-release` (excluding
`workspace/`, `.git/`, `__pycache__/`), audits it for personal-data leaks, runs
`setup.py` and serves the panel on 8138. It never touches your own folder, so
you can keep both open at once.

To produce the archive you would publish:

```bash
python make_release.py --zip
```

## Layout

```
index.html              the panel (12 tabs), reads the JSON files below
refresh.py              store scanner + rule engine → workspace/data.json
setup.py                first-run setup and health check
export_metadata.py      advisor.json → per-locale, store-ready text files
i18n/                   panel languages (tr, en) — add your own
templates/              seed files copied into workspace/ on first run
skills/marketinghub/    the Claude Code skill: how to produce the analysis
make_release.py         builds a clean, publishable copy (no personal data)
workspace/              YOUR data — git-ignored, never committed
```

`workspace/` holds `config.json`, `data.json`, `advisor.json`, `playbook.json`,
downloaded store assets and the metadata export. It is in `.gitignore` by
design: fork the repo, keep your own analysis private.

## Language

The panel ships in Turkish and English; pick one from the selector in the header
(stored per browser, defaults to `config.json > lang`).

To add a language: copy `i18n/tr.json`, fill `ui` with
`"<Turkish source string>": "<your translation>"` pairs, translate `prompts` and
`briefs`, save as `i18n/<code>.json`, and add the code to `LANGS` in
`index.html`. Missing keys fall back to Turkish rather than breaking.

Note: the Python scripts still print their progress in Turkish. That is the
remaining gap.

## Requirements

- Python 3.9+ (standard library only — no pip install)
- A browser
- Claude Code for the analysis phases (optional but this is the point of it)

Store data is scraped from public pages; there are no API keys and no accounts.
Play does not expose a public ranking API, so the Play side is optimised through
the tag matrix and the change plan instead of positions.

## License

MIT — see [LICENSE](LICENSE).
