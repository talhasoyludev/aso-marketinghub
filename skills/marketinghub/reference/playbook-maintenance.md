# Phase 5 — Keeping the files from rotting

Two files accumulate if nobody prunes them, and both then start lying: the
playbook fills with methods nobody will ever run, and `advisor.json` fills with
recommendations that were done months ago.

## playbook.json — methods still awaiting a decision

`workspace/playbook.json` (seeded from `templates/playbook.json`) is a list of
growth **methods**, not a knowledge base and not an archive.

**Add** a method only if all three hold:

1. It is applicable to *this* app — not "any mobile app".
2. Nobody has decided about it yet.
3. It is not already an item in `advisor.json > recommendations`.

**Delete** a method when any of these happen:

- it became a dated recommendation in `advisor.json` (the recommendation is now
  the single source — a copy in the playbook creates drift);
- it was implemented, or explicitly rejected;
- it is "low impact + low effort" — that combination is list padding.

Also delete generic ASO-101 entries on sight ("optimise your metadata", "reply
to reviews"). If it is true for every app in the store, it teaches this user
nothing and pushes the real items down the page.

Item shape:

```json
{"id": "pb-xxx-N", "title": "…", "impact": "düşük|orta|yüksek",
 "effort": "düşük|orta|yüksek", "desc": "…", "steps": ["…"]}
```

`refresh.py` marks some items as "do this now" via `data.json >
auto.playbookFocus`, keyed by `id`. Those ids are referenced in
`refresh.py > build_auto_content`; if you delete an item that is referenced
there, `_keep_existing_playbook_ids()` drops the stale focus and prints a
warning on the next scan — check that warning and update the engine's mapping
rather than leaving it dangling.

## advisor.json — recommendations

Every session:

1. Re-read the open recommendations before adding new ones. If the data now
   contradicts one, delete or rewrite it — do not stack a contradicting item on
   top.
2. Never reuse or renumber an `id`: the panel stores the user's completion
   ticks against it.
3. Keep P1 scarce. If everything is critical, the tab is a wall and the user
   reads none of it.
4. Set `updated` only when copy actually changed — it forces the panel to
   overwrite the ASO fields.

## The panel is your review

Before ending a session, look at three surfaces and make sure you did not create
work for the user without telling them:

- **Publish Verification** — did anything you wrote go live? (Almost certainly
  not yet; say so.)
- **Localization Audit** — did a new pack add warnings?
- **Advisor** — how many open items are there now versus when you started? A
  session that only adds is a session that made the tool heavier, not better.
