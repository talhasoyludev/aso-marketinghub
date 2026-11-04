# Contributing to MarketingHub

Thanks for helping. Issues and pull requests are welcome — small, focused
changes are the easiest to review.

## Run it locally

You need Python 3.9+ and a browser. Nothing to install.

```bash
python setup.py --check   # health check, writes nothing
python setup.py           # seeds workspace/ from templates/
python refresh.py         # store scan → workspace/data.json (minutes; rate-limited)
```

Open the panel with `start.bat` (Windows) or `./start.command` (macOS), not by
double-clicking `index.html` — `file://` cannot read the JSON files.

No app of your own? Run `demo.bat` / `./demo.command`, or open the panel with
`?demo=1`, to see it with sample data.

Before opening a PR, run what CI runs:

```bash
python -m py_compile *.py
python setup.py --check   # must finish without a traceback
```

## Principles

These are the project's rules, not suggestions. PRs that break them will be
asked to change.

- **Nothing hardcoded, nothing frozen.** No hand-written keyword lists,
  checklists, example copy or app-specific values in the code. Every list is
  derived from `config.json`, the scan, or `advisor.json`.
- **Read back before claiming.** The panel never reports text as published
  until the scan has read that exact value back from the store. Anything that
  cannot be read back is labelled unverifiable, not silently skipped.
- **The engine measures; it does not write copy.** Store text comes from
  `workspace/advisor.json`, produced by Claude via the skill.
- **`workspace/` is never committed.** It holds personal data and is
  git-ignored. Do not add files from it to a PR, and do not commit real store
  IDs, keywords or analyses in examples.
- **Standard library only, Python 3.9+.** No `pip install`, no third-party
  packages. Keep the code runnable on Windows and macOS.

## Add a panel language

1. Copy `i18n/tr.json` to `i18n/<code>.json` (e.g. `de.json`).
2. Fill `ui` with `"<Turkish source string>": "<your translation>"` pairs.
3. Translate `prompts` and `briefs`.
4. Add the code to `LANGS` in `index.html`.

Missing keys fall back to Turkish rather than breaking, so a partial
translation is still a useful PR. If you speak the language, a playbook
template (`templates/playbook.<code>.json`) is welcome too.

## Good first issues

- A new panel language (see above).
- New store countries for the ranking scan, with their storefront quirks.
- Clearer error messages when a store request fails or is throttled.
- Panel accessibility and small-screen layout fixes.
- Documentation: screenshots, a walkthrough of a first analysis.

## Reporting bugs

Use the bug report form. Include your OS, Python version, which store (App
Store / Google Play), the steps, and the full console output. Remove anything
personal from the output first.

## License

By contributing you agree that your contributions are licensed under the
[MIT License](LICENSE).
