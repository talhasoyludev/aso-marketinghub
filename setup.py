#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""First-run setup and health check.

    python setup.py            # creates missing files from templates, reports status
    python setup.py --check    # writes nothing, only reports status

Personal data (config, scan output, analyses, images) lives under workspace/
and stays out of git, so the code tree can be shared publicly.
Output language follows config.json > lang (MARKETINGHUB_LANG overrides it).
"""
import json
import shutil
import sys
from pathlib import Path

import mh_text
from mh_text import t

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = Path(__file__).resolve().parent
WS = BASE / "workspace"
TPL = BASE / "templates"

# files seeded from templates: (workspace name, template name, required?)
# — the playbook template is picked by language
SEED = [("config.json", "config.json", True),
        ("advisor.json", "advisor.json", False),
        ("playbook.json", None, False)]


def playbook_template(lang):
    """Playbook template for the language pack; English if there is none."""
    for name in (f"playbook.{lang}.json", "playbook.en.json"):
        if (TPL / name).exists():
            return name
    return "playbook.en.json"

PASS, WARN, FAIL = "  ✓", "  ! ", "  ✗"


def main():
    check_only = "--check" in sys.argv
    problems = []

    WS.mkdir(exist_ok=True)

    # Move files left in the repo root by the old layout into workspace/
    for name, _, _ in SEED:
        old = BASE / name
        if old.exists() and not (WS / name).exists():
            if check_only:
                print(WARN + t("s.root_found", name=name))
            else:
                shutil.move(str(old), str(WS / name))
                print(PASS + t("s.moved", name=name))

    # config may have just moved into workspace/ — re-read the language
    mh_text.set_lang(mh_text.detect_lang(BASE))
    lang = mh_text.raw_lang(BASE)

    for name, tpl, required in SEED:
        tpl = tpl or playbook_template(lang)
        target, source = WS / name, TPL / tpl
        if target.exists():
            print(PASS + f" workspace/{name}")
            continue
        if check_only:
            (problems if required else []).append(t("s.ws_missing", name=name))
            print((FAIL if required else WARN) + " " + t("s.ws_missing", name=name)
                  + (t("s.template_hint", tpl=tpl) if source.exists() else ""))
            continue
        if source.exists():
            shutil.copy(str(source), str(target))
            print(PASS + t("s.created", name=name))
        else:
            problems.append(t("s.tpl_missing", tpl=tpl))

    cfg_path = WS / "config.json"
    if not cfg_path.exists():
        problems.append(t("s.no_config"))
    else:
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            app = (cfg.get("apps") or {}).get(cfg.get("activeApp")) or {}
            if not app:
                problems.append(t("s.bad_active"))
            else:
                if app.get("name") in (None, "", "My App"):
                    problems.append(t("s.name_tpl"))
                if not app.get("iosId") and not app.get("playId"):
                    problems.append(t("s.need_id"))
                if not app.get("keywords"):
                    problems.append(t("s.no_keywords"))
                if app.get("playId") == "com.example.myapp":
                    problems.append(t("s.play_example"))
        except json.JSONDecodeError as e:
            problems.append(t("s.config_bad_json", e=e))

    data = WS / "data.json"
    print((PASS if data.exists() else WARN) +
          (t("s.data_ok") if data.exists() else t("s.data_missing")))

    adv = WS / "advisor.json"
    if adv.exists():
        try:
            a = json.loads(adv.read_text(encoding="utf-8"))
            n = len(a.get("recommendations") or []) + len(a.get("asoSuggestions") or [])
            print((PASS if n else WARN) +
                  (t("s.adv_count", n=n) if n else t("s.adv_empty")))
        except json.JSONDecodeError as e:
            problems.append(t("s.adv_bad_json", e=e))

    print()
    if problems:
        print(t("s.problems"))
        for p in problems:
            print("   ·", p)
        print(t("s.fix_hint"))
        return 1

    print(t("s.done"))
    print(t("s.step1"))
    print(t("s.step2"))
    print(t("s.step3"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
