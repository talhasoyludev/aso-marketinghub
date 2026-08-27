# Phase 4 — Verification

The rule: **text in the panel is not published**. A metadata change counts as
live only when the scan reads that exact value back from the store.

## How the panel does it

`refresh.py` scrapes the live listing into `data.json > myApp`. The ASO Center's
**Publish Verification** panel compares each field with what the panel holds:

| Verdict | Meaning |
|---|---|
| ✓ live | the store's value matches the panel exactly |
| ! drift | the store has different text — either not published, or edited elsewhere |
| ✕ missing | the store field is empty, or the scan could not read it |
| ? unverifiable | it cannot be read from outside at all |

Only one field is permanently unverifiable: the **iOS keywords field**. Apple
never exposes it publicly. Nothing can check it — say so, and tell the user to
confirm it by eye in App Store Connect. Never let an unverifiable field be
reported as done.

## Rules for you

1. **Never report copy as published.** You wrote it to `advisor.json`; the user
   publishes it; the next scan proves it. Those are three separate events and
   two of them are not yours.
2. **Re-scan before claiming anything changed.** `data.json` is a snapshot with
   a timestamp — check `generated` before you reason about "current" state.
3. **Store propagation is not instant.** A published metadata change appears in
   the listing within hours, but *ranking* effects take 7-14 days. Do not read a
   flat rank two days after publishing as failure.
4. **Version-gated fields.** On iOS, name, subtitle, keywords and description
   only change with a new app version; promo text is the only field editable in
   place. If the user "published" and verification still shows drift, this is
   usually why — ask whether a new version was submitted.
5. **If the scan cannot read a field, fix the scan or say so.** Two fields —
   the iOS subtitle and the Play short description — are scraped from HTML, so
   store redesigns break them silently. If either reads as missing while the
   user insists it is set, check the page yourself before writing a
   recommendation about it.

## What else the panel measures (and you should read)

Under the verification rows: scan date, app version, live store languages vs the
localization pack you drafted, iOS screenshot count, rating mass on both stores.
These are measured facts, not opinions — use them as the data hook for
recommendations.

## Things only the user can do

Collect these into an explicit list at the end of a session; a first release
never has an empty one:

- publish the metadata (and submit a version if iOS fields are version-gated)
- upload screenshots, app preview video, Play feature graphic
- the App Privacy survey (UI-only, blocks first submission)
- age rating questionnaire — confirm no question is left blank
- attach in-app purchases to the first version (web UI only) and upload IAP
  review screenshots
- per-locale privacy policy URL
- submit for review

Report each as MANUAL, never silently omit one. An item you did not do and did
not mention reads as an item that is done.
