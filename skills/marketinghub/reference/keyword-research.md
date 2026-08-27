# Phase 1 — Read the data before you write anything

`workspace/data.json` is the only measurement you have. Read it fully, know what
each number is worth, and let it set the agenda.

## What is in there

| Key | What it is | Trust |
|---|---|---|
| `myApp.ios` / `myApp.play` | the **live** listing, scraped: title, subtitle, description, rating count, version, languages, screenshots | high — this is ground truth |
| `keywordRanks[]` | per keyword, per country: `myRank`, `total`, `top[]`, `compRanks`, `volume`, `difficulty`, `prev` | ranks: high · volume/difficulty: estimates |
| `tags[]` | tag matrix across competitors: `usedBy`, `inTitles`, `score`, `mine`, `opportunity` | high — it is counted, not modelled |
| `auto.keywordScores` | `vol × (100−dif)` ranking of your tracked phrases | derived |
| `asoPlan[]` | engine's store change plan, priority-sorted | high signal, generic wording |
| `recommendations[]` | rule-engine output | high signal |
| `history[]` | one row per scan | the only trend data that exists |

## The four numbers that decide the agenda

1. **Is anything indexed at all?** `keywordRanks[*].countries[*].myRank` all
   null means the listing is invisible: nothing else matters until metadata is
   published and 7-14 days pass. Say exactly that; do not hand over a content
   plan.
2. **Rating mass.** `myApp.ios.ratingCount` under ~50, or Play under ~100, caps
   how far any keyword can climb. Ranking work has a ceiling until this moves.
3. **Locale coverage.** `myApp.ios.languages` versus the localization pack.
   One live language while eight are drafted is a bigger gap than any keyword.
4. **Beatable positions.** In `keywordRanks`, look for terms where the user
   ranks 10-60 *and* the `top[]` apps have weak rating mass. Those are the only
   fights worth starting; a term where the top 3 have six-figure rating counts
   is not winnable this quarter, whatever its volume.

## What volume and difficulty are, exactly

Both are 0-100 estimates the engine derives from the rating mass and title usage
of the apps ranking for a term. They are directionally useful for *comparing
your own tracked phrases* and worthless as absolute numbers. Never present them
as search volume. If the user needs real volume, tell them plainly: Apple Search
Ads' keyword suggestions (free, needs an account) or a paid ASO tool. Saying "I
can't measure that here" is a correct answer.

## Choosing what to target

- **Intent over volume.** A term is relevant only if the person typing it wants
  *this* app. Two failure classes look attractive because volume is high:
  too-generic single words ("tracker", "jump"), and adjacent-but-wrong intent
  (a term whose searchers want a different category). Ask of every candidate:
  how many people typing this want *this* app? "Some, indirectly" means cut it.
- **Winnable before big.** Prefer a mid-volume term where the top 3 are weak
  over a head term owned by an incumbent.
- **Use the tag matrix as demand evidence.** `tags[]` with high `inTitles`
  means many developers bet their title slot on that word — that is evidence
  people search it. `opportunity: true` means competitors use it and the user
  does not: those are the cheapest additions.
- **Brand terms are keyword-field only.** A competitor's brand can live in the
  hidden iOS keywords field but never in visible text on either store. The
  panel's metadata audit enforces this from `config.json > brandTerms`.

## Per market, not per translation

Ranks are already per country in `keywordRanks`. A term that is strong in one
market may not exist in another, and the local-language equivalent is rarely a
translation of the English phrase. When you propose a locale's keyword set,
derive it from that market's own search behaviour (competitor titles on that
storefront, the local word people actually use) and mark anything unverified as
unverified.

## Output of this phase

A short written read of the data before any copy is written: what is indexed,
what is beatable, what is capped by rating mass, what is missing entirely.
Everything you write in phases 2 and 3 must trace back to a line in this read.
