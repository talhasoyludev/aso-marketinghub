# workspace/advisor.json — the exact shape

Everything the panel renders as *your* output lives here. `templates/advisor.json`
carries the same schema inline; this file explains what makes each field good.

Write in the language set by `config.json > lang`. Validate after writing:

```bash
python setup.py --check
python export_metadata.py --check    # character limits across every locale
```

## Top level

```json
{
  "updated": "2026-08-27 (what this session did)",
  "recommendations": [],
  "asoSuggestions": [],
  "localization": [],
  "tagGroups": []
}
```

`updated` doubles as a cache key: when its value changes, the panel refreshes
the ASO fields from `asoSuggestions`, overwriting the user's unsaved edits in
those fields. So change `updated` only when you actually changed copy.

## recommendations[]

```json
{
  "id": "adv-20260827-01",
  "area": "roadmap|aso|video|tags|radar|playbook|i18n|campaign|general",
  "priority": 1,
  "title": "One line, imperative, specific",
  "detail": "Why now + how. Anchor it to the data that triggered it.",
  "source": "Claude — 27 Aug 2026, keyword matrix"
}
```

- `id` must be unique and date-stamped; the panel stores completion state
  against it, so **never reuse or renumber an existing id** — a user's ticked
  items would silently move to different tasks.
- `priority` 1 means "everything else waits on this". Use it sparingly: more
  than three or four P1s at once means you have not decided anything.
- `area` routes it: `roadmap` items become tasks on the Roadmap tab, everything
  else surfaces as an advice box above its own tab.
- `detail` is where the data hook goes. Name the rank, the count, the locale,
  the competitor. A reader must be able to disagree with you using the same file.

Removing an item is a real edit: if a recommendation is done or was wrong,
delete it (or leave it and let the user tick it). Do not accumulate.

## asoSuggestions[]

```json
{ "field": "iosTitle", "value": "final text to paste", "reason": "why this, and what you rejected" }
```

Fields and hard limits: `iosTitle` 30 · `iosSub` 30 · `iosKw` 100 ·
`iosPromo` 170 · `iosDesc` 4000 · `iosWhatsNew` 4000 · `gpShort` 80 ·
`gpLong` 4000. The panel counts characters live and the store rejects the write
over the limit — count before you write.

`reason` is not decoration. Write down the alternative you rejected and why;
the next session (or the next model) otherwise re-litigates the same choice and
flip-flops the listing. Rules for the copy itself: `reference/metadata.md`.

## localization[]

```json
{
  "lang": "de", "name": "Almanca", "flag": "🇩🇪", "country": "DE", "priority": 1,
  "why": "Data reason this market is worth a pack",
  "iosTitle": "…", "iosSub": "…", "iosKw": "…", "gpShort": "…", "gpLong": "…",
  "screens": ["HEADING 1", "HEADING 2", "…"]
}
```

`lang` must match the code used in `export_metadata.py`'s `LOCALES` map, or the
export skips the locale with a warning. `screens` must have the same number of
entries as `config.json > screenHeadings`, in the same order — Creative Studio
renders them positionally. Rules: `reference/localization.md`.

## tagGroups[]

```json
{ "group": "🧠 Advisor — 27 Aug 2026 findings", "tags": ["term", "term"] }
```

Shown in the Tag Bank next to the radar's automatic groups. Only add a group
when it carries something the radar did not already surface; a group that
repeats `data.json > auto.tagGroup` is noise.

## What never goes in this file

- Generic ASO advice true of any app (that is what the playbook is for, and even
  there only if a decision is pending).
- Anything the engine already produces: rankings, tag matrices, the store change
  plan, video tag sets. Duplicating them creates two sources that drift.
- Secrets: API keys, service-account paths, ad-account IDs. `workspace/` is
  git-ignored, but treat it as one wrong `git add -f` away from public.
