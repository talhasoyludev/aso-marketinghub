## What and why

<!-- What does this change, and which problem does it solve? Link the issue: Fixes #123 -->

## How I tested it

<!-- Commands you ran, OS / Python version, screenshots for panel changes. -->

## Checklist

- [ ] Nothing hardcoded or frozen: lists and copy derive from `config.json`, the scan, or `advisor.json`
- [ ] Nothing from `workspace/` and no real personal store data is included
- [ ] Python stays standard-library only and runs on 3.9+
- [ ] `python -m py_compile` passes on every changed `.py` file, and `python setup.py --check` runs without a traceback
- [ ] New or changed panel strings are added to `i18n/` (if applicable)
- [ ] `CHANGELOG.md` has an entry under "Unreleased" (if user-facing)
