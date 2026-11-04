# Where to list MarketingHub

Every entry below was checked to exist on 2026-11-04, with its submission rules read from the repo's README or CONTRIBUTING file. Star counts are as of that date. Rules change; reread them before submitting.

Submit one at a time, by hand, from your own account. Several lists say AI-written submissions or bulk submissions get closed. Several also have a star or age threshold, so the order below matters: submit the ones without a threshold first, and the rest once the repo has some stars.

Repo facts the lists ask about: first commit 2026-08-27 (older than 14 days), MIT license file at the root, `skills/marketinghub/SKILL.md` present.

## Submit now (no star threshold)

### Anthropic community plugin directory
- **URL:** https://github.com/anthropics/claude-plugins-community (read-only mirror, about 4.8k stars)
- **How:** submit via the form at https://clau.de/plugin-directory-submission. PRs to the repo are closed automatically; approved plugins pass automated security scanning and get synced in. Requires the plugin marketplace manifest in this repo to be in place.
- **Ready text (one line description):**
  `Local ASO dashboard for iOS and Android apps: store scanner, rule engine, and a skill that writes store copy and localizations from the scan.`

### skills.sh (Vercel skills leaderboard)
- **URL:** https://skills.sh
- **How:** no submission. Skills appear automatically through anonymous telemetry when people run `npx skills add talhasoyludev/aso-marketinghub`, ranked by installs. Make sure that command is in the README (it is) and works.
- **Ready text:** none needed.

### Claude Marketplaces
- **URL:** https://claudemarketplaces.com (independent directory, not affiliated with Anthropic)
- **How:** sign in with GitHub at https://claudemarketplaces.com/submit and submit the repo as a skill repo / plugin marketplace. Free; there is an optional paid priority review, which you don't need. Crawlers also discover listings and refresh stars on their own.
- **Ready text:**
  `MarketingHub: free, local ASO dashboard for mobile apps. Tracks App Store rankings across countries and competitor keywords; Claude writes and verifies store copy.`

### Awesome-ASO (rafaecheve)
- **URL:** https://github.com/rafaecheve/Awesome-ASO (about 50 stars, active)
- **How:** PR adding one line to the **Tools** section, keeping it alphabetical: MarketingHub goes just before "Marteso". Copy the number prefix the neighbouring lines use. Commit message format: `Add MarketingHub`. Name + description under 100 characters, no marketing language.
- **Ready line (list uses numbered items):**
  `1. [MarketingHub](https://github.com/talhasoyludev/aso-marketinghub) - Open-source local ASO dashboard and Claude Code skill. iOS, Android. Free.`

### BehiSecc/awesome-claude-skills
- **URL:** https://github.com/BehiSecc/awesome-claude-skills (about 10.3k stars)
- **How:** fork, add the line, open a PR. No stated threshold. Best section: **Data & Analysis** (there is no marketing section).
- **Ready line:**
  `- [marketinghub](https://github.com/talhasoyludev/aso-marketinghub) - ASO for mobile apps: scans App Store and Play listings, writes store copy and localization packs, verifies what went live.`

### karanb192/awesome-claude-skills
- **URL:** https://github.com/karanb192/awesome-claude-skills (about 580 stars)
- **How:** fork, add a row to the matching table in `README.md`, PR titled `Add marketinghub to [category]`. Read its CONTRIBUTING.md quality criteria first. No star threshold stated.
- **Ready row (table format):**
  `| [marketinghub](https://github.com/talhasoyludev/aso-marketinghub/tree/main/skills/marketinghub) | Run App Store and Google Play ASO from a local scan: metadata, localization, publish checks. |`

### ComposioHQ/awesome-claude-skills
- **URL:** https://github.com/ComposioHQ/awesome-claude-skills (about 78.7k stars)
- **How:** PR. The CONTRIBUTING guide is written for skills added as folders in their repo, but the **Business & Marketing** section also lists external repos with an author credit. Follow that external format. They want a real use case and examples, so link the demo in the PR description.
- **Ready line:**
  `- [MarketingHub](https://github.com/talhasoyludev/aso-marketinghub) - Local ASO dashboard for iOS and Android apps. Scans the stores, then Claude writes store copy and per-market localization and checks what went live. *By [@talhasoyludev](https://github.com/talhasoyludev)*`

### hesreallyhim/awesome-claude-code
- **URL:** https://github.com/hesreallyhim/awesome-claude-code (about 57k stars)
- **How:** only through the issue form: https://github.com/hesreallyhim/awesome-claude-code/issues/new?template=recommend-resource.yml. **Do not open a PR** (risk of being restricted). Must be 14+ days old with ongoing commits, or 100+ stars: this repo qualifies on age. One resource at a time. The recommendation must be filed by a human, not via `gh`. Style: a description, not a pitch; one line; no emoji; don't address the reader. The maintainer says plainly that listing is selective and not a launch strategy, so treat it as a bonus.
- **Category:** Skills.
- **Ready description:**
  `A local ASO dashboard for iOS and Android apps with a skill that turns a public-store scan into store metadata, per-market localization packs and dated recommendations, and only marks copy as published after reading it back from the live listing.`

## Submit once the repo has traction

### heilcheng/awesome-agent-skills
- **URL:** https://github.com/heilcheng/awesome-agent-skills (about 6.3k stars)
- **Threshold:** at least 20 stars and older than 14 days. A SKILL.md is required. Read its AGENTS.md (full rules) before submitting.
- **How:** PR appending one line to the end of the best-fitting category under Community Skills (**Marketing**). Issues are not reviewed. An automated check comments on the PR.
- **Ready line (description under 100 characters):**
  `- [talhasoyludev/aso-marketinghub](https://github.com/talhasoyludev/aso-marketinghub) - Local ASO for iOS/Android: store scan, metadata, localization, publish verification`

### VoltAgent/awesome-agent-skills
- **URL:** https://github.com/VoltAgent/awesome-agent-skills (about 36.8k stars)
- **Threshold:** "real community usage". Brand-new skills are not accepted. Wait for stars and some issues from real users.
- **How:** PR titled `Add skill: talhasoyludev/marketinghub`, appended to the end of **Community Skills > Marketing**. Description must be 10 words or fewer.
- **Ready line:**
  `- **[talhasoyludev/marketinghub](https://github.com/talhasoyludev/aso-marketinghub/tree/main/skills/marketinghub)** - Local ASO dashboard: store scans, metadata, localization, publish verification`

### travisvn/awesome-claude-skills
- **URL:** https://github.com/travisvn/awesome-claude-skills (about 15.7k stars)
- **Threshold:** "social proof", meaning enough GitHub stars to be considered. Strictly non-promotional; no SaaS funnels (MarketingHub has none, which helps).
- **How:** fork, add to the **Community Skills > Individual Skills** table, PR.
- **Ready row:**
  `| **[marketinghub](https://github.com/talhasoyludev/aso-marketinghub)** | App Store and Google Play ASO from a local store scan: metadata, localization, and publish verification |`

## Low fit or not accepting submissions

Checked and skipped. Listed so you don't spend time on them.

- **jqueryscript/awesome-claude-code** (https://github.com/jqueryscript/awesome-claude-code, about 540 stars): entries sorted by star count, contribution guidelines marked "Under Construction". It appears to pick up projects by stars; revisit later.
- **quemsah/awesome-claude-plugins** (https://github.com/quemsah/awesome-claude-plugins): auto-generated top 100 by stars. No submission.
- **composio-community/awesome-claude-plugins** (https://github.com/composio-community/awesome-claude-plugins): expects plugins added as folders inside their repo. Not a fit for a link entry.
- **thedaviddias/indie-dev-toolkit** (https://github.com/thedaviddias/indie-dev-toolkit, about 300 stars): not accepting PRs; suggestions via GitHub Discussions only. A short suggestion under Marketing & Growth is fine once the repo has traction.
- **mezod/awesome-indie** (https://github.com/mezod/awesome-indie) and **johackim/awesome-indiehackers** (https://github.com/johackim/awesome-indiehackers): resource lists (blogs, podcasts, books), not tool lists. Skip.
- **SkillsMP** (https://skillsmp.com): referenced by other lists as a skills marketplace; the site blocked automated checks, so the submission process is unverified. Look it up yourself.

I did not find an established awesome list for iOS/Android ASO beyond Awesome-ASO.
