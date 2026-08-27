# Phase 0 — Setup

Goal: `workspace/config.json` describes the real app, and `workspace/data.json`
exists from a real scan. Nothing downstream is meaningful before both are true.

## Step 1 — bootstrap the workspace

```bash
python setup.py            # copies templates/ → workspace/ where missing
python setup.py --check    # reports only, writes nothing
```

`setup.py` also migrates files left in the repo root from an older layout. If it
reports missing pieces, fix those before scanning — a scan against a template
config wastes minutes and produces a `data.json` that looks real.

## Step 2 — fill in config.json

Ask the user for the app, then find the IDs yourself rather than making them
type them:

- **App Store**: search the store page, take the numeric id from the URL
  (`apps.apple.com/…/id123456789` → `123456789`). If the app is not on iOS, set
  `iosId` to `0`.
- **Google Play**: the package name from `play.google.com/store/apps/details?id=…`.
  If not on Play, leave `playId` empty.
- Confirm the app you found is theirs — same developer name, same icon — before
  writing it. Scanning the wrong app produces a confident, wrong report.

Fields that decide the quality of everything downstream:

| Field | How to choose it |
|---|---|
| `keywords` | 8-12 **phrases a person would actually type**, not single words. Mix: one head term, two or three mid-tail phrases, one or two brand-adjacent terms. These are what the radar measures — a bad list means a blind radar. |
| `competitors` | 10-25 apps that *actually rank* for those phrases, not the market leaders you admire. Include the small ones ranking above the user — those are the beatable positions. |
| `brandTerms` | Competitor brand names the audit must keep out of visible text (Apple 2.3.7 / Play brand policy). Also what the Trend Wave prompt watches. |
| `countries` | Only markets the user could plausibly serve. Every extra country lengthens the scan. |
| `screenHeadings` | Source-language screenshot band headings. Creative Studio renders these per locale. |
| `goal` | The install target the Reports tab counts toward. |
| `lang` | Panel language, and the language you write `advisor.json` in. |

Seed `keywords` from evidence, not intuition: the competitors' own titles and
subtitles, App Store search suggestions for the app's core noun, and the words
the user's own description already leans on. Say which are guesses.

## Step 3 — first scan

```bash
python refresh.py
```

It is rate-limited on purpose (`rateLimitSeconds`) and takes minutes for a
multi-country config. Run it in the foreground, let it finish, then read
`workspace/data.json`.

If the scan reports the app as not found: the store ID is wrong, the app is not
available in the configured `country`, or the listing is not live yet. Fix the
cause; do not fall back to writing recommendations without data.

## Step 4 — hand off to the panel

Tell the user to open the panel (`start.bat` / `start.command`, never by
double-clicking `index.html` — `file://` cannot read the JSON files) and point
them at the three surfaces that now have something to say: Radar, Advisor, and
Publish Verification.

Then continue with phase 1.
