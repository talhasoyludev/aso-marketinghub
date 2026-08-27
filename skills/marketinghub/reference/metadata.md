# Phase 2 — Store metadata

Write `asoSuggestions[]` in `workspace/advisor.json`. The panel applies them to
the ASO Center fields, counts characters live, and audits them.

## The three indexed surfaces (iOS)

Apple indexes the **title** (30), the **subtitle** (30) and the hidden
**keywords field** (100) — and it indexes them *combined*, building phrases
across the fields. Two consequences drive every rule below:

- A word spent twice across those surfaces buys nothing. Repetition is the most
  common way indie listings waste their 160 characters.
- You do not need to write the phrase "tower climbing game" anywhere as a whole
  if "tower", "climbing" and "game" each appear once across the three fields.

Google Play is different: **every visible text is indexed** (title 30, short 80,
long 4000), there is no hidden field, and the long description's natural
repetition (2-3 times) is the weighting mechanism.

## Rules

1. **Lead with the keyword, not the brand.** `Calorie Tracker — Glow Up` beats
   `Glow Up — Calorie Tracker`: position weight is real and almost nobody
   searches an unknown brand. If the user insists on brand-first, make it a
   conscious trade and record it in `reason`.
2. **The subtitle is the second keyword, not a slogan.** "Endless tower, epic
   combos" is a subtitle. "Feel amazing every day" is 30 wasted characters.
3. **No repetition across title / subtitle / keywords.** The panel's metadata
   audit flags it. When trimming, drop the duplicate from the keyword field —
   never from the title.
4. **Keyword field hygiene**: comma-separated, **no space after commas** (each
   space costs one of your 100 characters), no duplicates, no plural of a word
   already there, no word already in the title or subtitle.
5. **Single tokens vs whole phrases**: Apple builds combinations across fields,
   so single tokens maximise combination count; complete phrases read as real
   searches and are what some ASO schools recommend. Both are defensible — pick
   one deliberately, write the reasoning into `reason`, and don't silently flip
   between them across sessions.
6. **No Apple product names in title or subtitle** (guideline 5.2.5) — "for
   Apple Watch" in a subtitle gets the metadata rejected. In the keyword field
   it is fine and valuable if the app really has a Watch app.
7. **No competitor brand in visible text.** Hidden keywords field only, and even
   there it can trip Apple 2.3.7 — keep a replacement pair ready.
8. **Never mention price, "free", or discounts** in the description or promo
   text of anything paywalled — recurring rejection class. Never promise an
   unreleased feature ("multiplayer coming soon") — same.
9. **Promo text (170) is the only field that updates without review.** Use it
   for events and launches; do not put evergreen copy there.
10. **The iOS description is not indexed.** It is pure conversion copy: the
    first 2-3 lines are what shows before "more". The Play long description *is*
    indexed — write them differently, and do not paste one into the other.

## Working method

1. Start from the **live** listing in `data.json > myApp`, never from a local
   file or memory. That is what is actually published.
2. Draft the title and subtitle from the phase-1 read: the strongest winnable
   term leads the title, the second leads the subtitle.
3. Fill the keyword field with what the first two do not already cover, until
   the 100 characters are spent. Count them.
4. Write `gpShort` (80) as a readable sentence that carries two or three target
   phrases; write `gpLong` with those phrases appearing naturally 2-3 times.
5. Write each `reason` with the rejected alternative in it.
6. Check the result in the panel: **ASO Center → Metadata Audit** must come back
   clean, and **coverage** should improve, not just change.

## What the panel checks for you

Brand leakage into visible fields · title↔subtitle repetition · keyword-field
spacing, duplicates and overlap with the title · every field against its store
limit · risky phrases ("monetized with ads", "coming soon", "beta", "cheat") ·
share of radar target keywords present in the iOS metadata.

Run `python export_metadata.py --check` for the same limit check across every
locale at once.
