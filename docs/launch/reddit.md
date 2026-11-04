# Reddit drafts

Drafts for the maintainer to post by hand. Nothing here has been posted.

General rules for all of them:

- Post from your own account, one subreddit per day at most, never cross-post the same text.
- Read the sidebar and pinned posts the day you post. Rules below were checked from mod posts and mirrors in November 2026 and may have changed.
- Stay in the thread for the first 2-3 hours and answer every comment, including critical ones.
- Do not ask for stars or upvotes in any post.
- Put the repo link at the end, once.
- Replace every `[...]` placeholder with something real from your own apps, or delete the sentence. Do not invent numbers.

---

## r/ClaudeAI

**Rules to check:** Showcase posts (Rule 7) must say you built it, that it was built with Claude or Claude Code, what it does, and specifically how Claude was used. A one-line "built with Claude Code" gets removed. Feed-level showcase posts have needed 50+ karma; otherwise use the "Built with Claude" megathread. Use the Showcase flair.

**Title:** I built a Claude Code skill that does ASO for my mobile apps, and the hard part was stopping it from inventing numbers

**Body:**

I'm an indie mobile developer and I kept doing the same loop by hand: look up where my apps rank, copy competitor titles into a doc, ask Claude for a new subtitle, paste it into App Store Connect, forget whether it went live. So I built MarketingHub, a local dashboard plus a Claude Code skill that runs that loop.

**What it does**

- A Python scanner (stdlib only) reads public App Store and Google Play pages: keyword rankings in several countries, competitor listings, a tag matrix of which words competitors use in their titles.
- A local HTML panel turns that into tabs: radar, metadata audit, localization audit, screenshot renderer, history.
- Claude Code, through a skill in the repo, reads the scan and writes the store copy, per-market localization packs and dated recommendations into a JSON file the panel displays.

**How Claude was used, specifically**

1. [Say honestly how much of the scanner, rule engine and panel Claude Code wrote and what you did yourself. Rule 7 requires this detail.]
2. More interesting: Claude is also the *runtime* for the copywriting. The skill (`skills/marketinghub/SKILL.md` plus seven reference files) is the method I would want a human ASO consultant to follow, written so Claude follows it.

**What I learned writing the skill**

- **Split measurement from writing, hard.** The scanner never writes copy; Claude never edits the scan file. When both were mixed, Claude would "improve" numbers it didn't like.
- **Name the trap.** Volume and difficulty here are estimates from rating mass. Unless the skill says "never present these as search volume", the output drifts into "this keyword gets 12k searches". Now the skill says it plainly and tells Claude to say "I can't measure that here" when that's the answer.
- **Every recommendation needs a data hook.** "Post more on TikTok" is banned. "No video asset while 6 of 8 competitors have one" is allowed. That one rule removed most generic ASO advice.
- **Read back before you claim.** Claude used to report metadata as "updated". Now nothing counts as published until the next scan reads it from the live store. The iOS keyword field can't be read publicly, so it is marked unverifiable instead of silently skipped.
- **Make it say what it didn't do.** Each session ends with Done / Findings / Needs the user. Omissions read as claims otherwise.

**Try it**

There's a demo with a fictional app, no config: clone, then `demo.bat` / `./demo.command` (or `python -m http.server 8137` and open `localhost:8137/?demo=1`). The skill also installs as a plugin: `/plugin marketplace add talhasoyludev/aso-marketinghub`.

Free, MIT, no API keys, your data stays in a git-ignored folder. Honest limits: no real search volume, no Play rankings (Google has no public API for them), and scans are slow because they're rate-limited.

I'd like feedback on the skill structure in particular: what would you change in how the phases and rules are written?

https://github.com/talhasoyludev/aso-marketinghub

---

## r/iOSProgramming

**Rules to check:** App promotion is limited to "App Saturday" (Saturday in your local time zone), one app once per year, with a karma minimum. This is a dev tool rather than an app, but post it on a Saturday anyway to be safe, or ask the mods first. Lead with technical content.

**Title:** What I learned tracking App Store keyword rankings across countries with only the public iTunes endpoints

**Body:**

I wanted to know where my apps rank for a set of keywords in several App Store countries, every week, without paying for an ASO subscription. Notes from building that, in case they help anyone doing the same:

- **The iTunes Search API is enough for rank tracking**, within limits. `itunes.apple.com/search?term=...&country=..&entity=software` returns ranked results per storefront. Your position in that list is a good proxy for your rank for that term in that country. It won't always match what a given device shows, so treat it as a trend line, not gospel.
- **Rate limits are real.** The search endpoint tolerates roughly 20 requests a minute before requests start failing. I space requests 3 seconds apart and back off for 25 seconds and retry once on failure. 20 keywords × 5 countries is a 5-minute scan; that's fine weekly.
- **The subtitle isn't in the lookup API.** You have to read it from the public `apps.apple.com` page HTML.
- **The keyword field can't be verified from outside.** No public endpoint exposes it. I mark it "unverifiable" rather than pretend.
- **Volume is the thing you can't get for free.** I estimate a 0-100 score from the rating counts and title usage of the apps ranking for a term. It's useful for comparing your own phrases against each other and useless as an absolute number. Apple Search Ads' keyword suggestions are the closest free source of real popularity.
- **Read back after you publish.** The most useful feature turned out to be the dumbest: after you change metadata, the next scan compares the live listing to what you meant to ship. It caught [describe a real mismatch you hit, or delete this line].

I packaged it as MarketingHub: a local dashboard (Python stdlib + one HTML file) with a Claude Code skill that writes the metadata and localizations from the scan. Free, MIT, no account, data stays on your machine. There's a demo with a fictional app if you want to look before configuring anything.

https://github.com/talhasoyludev/aso-marketinghub

Happy to answer questions about the scraping side.

---

## r/androiddev

**Rules to check:** Self-promotion posts need a substantive write-up on why the work matters to other developers, and source code where possible (this is open source, so that helps). Low-effort or auto-generated-looking posts are removed. Closed-source or "looking for feedback" posts go in the weekly thread; there is also a monthly showcase thread. If in doubt, use the showcase thread.

**Title:** Optimizing a Play Store listing without ranking data: an open-source tag-matrix approach

**Body:**

Google Play has no public API for search rankings, which makes ASO on Android mostly guesswork for small developers. I built a local tool for my own apps and the Play side ended up working differently from the iOS side. Sharing the approach, since it's useful even if you never use the tool.

**Instead of positions, measure what competitors bet on**

- Pick 5-10 real competitors (apps your users would install instead of yours).
- Read their public listings: title, short description, full description.
- Count every word and two-word phrase. For each, record how many competitors use it and how many put it **in the title**.
- A word that many competitors put in their 30-character title is evidence people search for it; developers don't spend title space on words nobody types.
- Compare against your own listing. Words most competitors use and you don't are your cheapest additions.

**Then verify, because the console lies by omission**

After you edit the listing in Play Console, the change can sit in review, apply to one locale and not another, or get truncated. Re-reading the public listing and diffing it against what you intended catches that.

**What the tool does**

MarketingHub runs the above automatically, alongside App Store rank tracking if you also ship on iOS. It's a Python scanner (standard library only), a local HTML panel, and a Claude Code skill that writes the copy and localization packs from the scan. It also audits every locale for character limits, untranslated fields and brand terms in visible text.

Limits: no Play rankings (no API), keyword volume is an estimate, scans are slow because they're rate-limited. Free, MIT, nothing leaves your machine except requests to the public store pages.

Source: https://github.com/talhasoyludev/aso-marketinghub

If you've found a better proxy for Play keyword demand, I'd like to hear it.

---

## r/SideProject

**Rules to check:** Self-promotion of side projects is the point of the sub, but low-effort link drops get ignored or removed. Read the current sidebar for flair and format requirements.

**Title:** I got tired of paying for ASO tools for apps that make almost nothing, so I built a free local one

**Body:**

I'm a solo mobile developer with a few small apps. ASO subscriptions cost more per month than some of my apps earn, and a single chat prompt for "write me a better subtitle" never knew what my competitors were doing.

So I built **MarketingHub**:

- A scanner that reads the public App Store and Play pages for my apps and competitors: rankings across countries, competitor keyword usage, my live listing text.
- A local dashboard with 12 tabs: radar, metadata audit, localization audit, screenshot renderer, campaign links, history.
- A Claude Code skill that reads the scan and writes the store copy and translations, following a written method instead of improvising.

**What I'd do differently**

- Ship the demo first. For a long time nobody could try it without configuring their own app. Now there's a fictional sample app that opens with one command.
- Write the limits down early. No real search volume, no Play rankings: saying that up front saves everyone time.

[Edit these two lessons so they match your actual experience, or replace them.]

**Stack:** Python standard library, one HTML file, JSON files on disk. No backend, no accounts, no API keys. MIT.

Demo: clone, then `demo.bat` / `./demo.command`, or `python -m http.server 8137` and open `localhost:8137/?demo=1`.

https://github.com/talhasoyludev/aso-marketinghub

Feedback welcome, especially from anyone who has tried to grow a small app through search alone.

---

## r/indiehackers

**Rules to check:** The sub is strict about promotion that adds nothing; posts that share a lesson or numbers do much better than announcements. Check the sidebar for any self-promo day or megathread before posting.

**Title:** ASO for apps with no budget: what actually moved, and the free tool I built around it

**Body:**

I make small mobile apps on my own. Search is the only acquisition channel I can afford, so App Store Optimization matters more to me than ads ever will. A few things I learned the slow way:

1. **Rating count caps everything.** Under roughly 50 ratings on iOS, no keyword work gets you far. Fix the review prompt before you touch metadata.
2. **Localization beats keyword tweaks.** One live language with eight translations sitting in a drafts folder is a bigger gap than any keyword. Each store locale is extra indexed text.
3. **Fight where you can win.** A term where the top three apps have six-figure rating counts is not winnable this quarter. Look for terms where you rank 10-60 and the apps above you are weak.
4. **Check that your change actually went live.** A metadata edit can sit in review, apply to one locale and not another, or get truncated. Re-read the live listing after every change. [Add a real example if you have one.]

[Case study placeholder: one before/after from your own app, with real dates and numbers. Delete this line if you don't have one yet.]

I turned my process into a free, local tool: **MarketingHub**. A scanner measures rankings and competitor keywords from the public stores, a local dashboard shows what to fix, and a Claude Code skill writes the copy. No signup, no API keys, MIT licensed, your data stays on your machine.

It doesn't give you real search volume (that's what paid tools are actually good for) and Google Play has no public ranking data. It covers everything around those numbers.

https://github.com/talhasoyludev/aso-marketinghub

What's your main acquisition channel for small apps, and has ASO been worth the time for you?
