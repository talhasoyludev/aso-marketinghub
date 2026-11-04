# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Demo mode: open the panel with sample data and no setup — `demo.bat`
  (Windows) / `./demo.command` (macOS), or append `?demo=1` to the panel URL.
- Install as a Claude Code plugin: the repository is now its own plugin
  marketplace (`/plugin marketplace add talhasoyludev/aso-marketinghub`, then
  `/plugin install marketinghub@marketinghub`). The skill also installs with
  `npx skills add talhasoyludev/aso-marketinghub`.
- Continuous integration on Ubuntu and Windows with Python 3.9 and 3.12:
  byte-compiles every script, checks that every JSON file parses, and runs
  `python setup.py --check` against the templates.
- Contribution docs: `CONTRIBUTING.md`, issue forms, and a pull request template.

### Changed

- The engine and CLI scripts (`setup.py`, `refresh.py`, `export_metadata.py`)
  print their output, and write their rule-engine recommendations, in the
  language set by `config.json > lang` (`en` or `tr`, default `en`). The
  `MARKETINGHUB_LANG` environment variable overrides it. Recommendation and
  plan ids are identical in both languages, so ticked items survive a switch.
- **Upgrading Turkish users:** if your `workspace/config.json` has no `lang`
  key, engine output is now English. Add `"lang": "tr"` to keep Turkish.
- The panel's number and date formatting and remaining Turkish-only strings
  now follow the selected panel language.
- `templates/config.json` and `templates/advisor.json` use English placeholders
  and field help as the international default.

## [0.1.0] - 2026-08-27

First public version.

### Added

- `refresh.py` store scanner and rule engine: App Store rankings across
  countries, competitor tag matrix, opportunity tags, live listing read-back,
  store change plan, and scan history, written to `workspace/data.json`.
- `index.html` panel with 12 tabs (Roadmap, Advisor, Competitor Radar,
  ASO Center, Video SEO, Tag Bank, Localization, Campaigns, Playbook,
  Creative Studio, Claude Prompts, Reports & KPI), in English and Turkish.
- Claude Code skill (`skills/marketinghub/`) describing how to produce
  `workspace/advisor.json`: store metadata, per-market localization packs,
  dated recommendations and tag groups.
- `setup.py` first-run setup and health check (`--check`), and
  `export_metadata.py` for store-ready, per-locale text files.
- Personal data kept in a git-ignored `workspace/`; seed files in `templates/`.

[Unreleased]: https://github.com/talhasoyludev/aso-marketinghub/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/talhasoyludev/aso-marketinghub/releases/tag/v0.1.0
