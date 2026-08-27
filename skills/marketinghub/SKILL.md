---
name: marketinghub
description: Run the full ASO/growth analysis for a mobile app inside a MarketingHub checkout — set up config.json, run the store scan, and produce workspace/advisor.json (store metadata, per-market localization pack, dated recommendations, tag groups) that the panel reads. Use when the user says "do the ASO for my app", "analyse my store listing", "set up MarketingHub", "refresh my keywords", "localize my store page", "why is my app invisible in search", or points at a MarketingHub folder and asks what to do next.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - AskUserQuestion
---

# MarketingHub — produce the analysis the panel displays

MarketingHub is a local panel plus a scanner. It **measures** on its own; it does
**not** write the copy or the strategy. Everything the panel shows as text —
store metadata, the localization pack, dated recommendations — comes from
`workspace/advisor.json`, and that file is yours to produce. This skill is how.

Split of responsibility, and it is strict:

| Produced by | What | Where |
|---|---|---|
| `refresh.py` (engine) | rankings, volume/difficulty estimates, competitor tags, opportunity tags, store change plan, tag/video sets, history | `workspace/data.json` |
| **You (Claude)** | store copy, per-market localization, dated recommendations, tag groups | `workspace/advisor.json` |
| The user | config, decisions, publishing to the stores | `workspace/config.json`, the store consoles |

The engine deliberately does not generate store copy: that needs brand and
nuance judgement. Never bypass this by hand-editing `data.json`.

## Phases

Run in order for a new app; jump to the one asked for otherwise. **Read the
reference file before starting a phase** — this page is the map, not the ground.

| Phase | Does | Reference |
|---|---|---|
| 0 SETUP | config.json, store IDs, first scan | `reference/setup.md` |
| 1 READ | read data.json properly; what the numbers mean and don't | `reference/keyword-research.md` |
| 2 METADATA | title / subtitle / keyword field / descriptions | `reference/metadata.md` |
| 3 LOCALIZE | per-market packs, not translations | `reference/localization.md` |
| 4 VERIFY | publish verification, what can never be verified | `reference/verification.md` |
| 5 MAINTAIN | keep advisor.json and playbook.json from rotting | `reference/playbook-maintenance.md` |

The exact shape of every field you write: `reference/advisor-schema.md`. Read it
before your first write, and validate with `python setup.py --check` after.

## Laws that hold in every phase

1. **Write to `workspace/`, never to the code tree.** `workspace/` is
   git-ignored personal data. The repo must stay publishable at all times.
2. **The panel's language follows `config.json > lang`.** Write
   `advisor.json` content in that language — recommendations, reasons, screen
   headings. Do not mix languages inside one file.
3. **Never invent a measurement.** Volume and difficulty in `data.json` are
   *estimates* derived from the rating mass and title usage of the apps ranking
   for a term — the panel says so, and so must you. If you need real search
   volume, say plainly that this tool cannot provide it and name what would
   (Apple Search Ads' own suggestions, an ASO data tool).
4. **A recommendation without a data hook is noise.** Every item you add to
   `recommendations` must point at something observable: a rank, a missing
   locale, a competitor tag, a rating count, a live listing field. "Post on
   TikTok more" is not a recommendation; "no video asset exists while 6 of 8
   competitors have one" is.
5. **Nothing frozen.** Do not add generic ASO-101 content anywhere. If a fact is
   true for every mobile app, it does not belong in this app's files — the
   playbook holds methods, and even there, only ones still awaiting a decision.
6. **Read back before you claim.** A metadata change is published when the scan
   reads it live from the store, not when the user says they pasted it. See
   `reference/verification.md`.
7. **Say what you did not do.** If a locale is unverified, a keyword is a guess,
   or a field could not be checked, list it explicitly. An omission reads as a
   claim.

## Working loop

```bash
python setup.py --check        # what is missing, before anything else
python refresh.py              # store scan → workspace/data.json (minutes, rate-limited)
python export_metadata.py      # advisor.json → per-locale store-ready text files
```

Then open the panel (`start.bat` / `start.command`) and check three surfaces:
**Publish Verification** (ASO Center), **Localization Audit** (Localization),
and the **Advisor** tab. Anything red there is your next task.

## Reporting

End a session with three short sections: **Done** (what changed, verified),
**Findings** (what the data actually says, including what it can't say), and
**Needs the user** (store-console steps only they can take — publishing,
screenshots, age rating, privacy survey). Keep it outcome-level. Never report a
metadata change as live; report it as written to `advisor.json` and pending
publication.
