# Launch checklist

An ordered plan. Every post is made by hand by the maintainer; drafts live in this folder.

## Pre-launch (before day 1)

### Media
- [ ] Record `docs/media/demo.gif` from the demo (`?demo=1`), about 20 seconds: Radar → ASO Center publish verification → Localization audit → Creative Studio batch render. 1280 px wide, under 10 MB so GitHub renders it inline.
- [ ] Capture `docs/media/radar.png`, `aso-center.png`, `localization.png`, `creative-studio.png` from the demo at the same window size.
- [ ] Make the social preview image (spec in `docs/github-settings.md`) and upload it under Settings → General → Social preview.
- [ ] Export the GIF as MP4 for X, LinkedIn and Product Hunt.

### Demo and install paths
- [ ] Fresh clone on Windows: `demo.bat` opens the panel with the sample app.
- [ ] Fresh clone on macOS: `./demo.command` works (check the executable bit survives the clone).
- [ ] Linux: `python -m http.server 8137` + `/?demo=1` works.
- [ ] `/plugin marketplace add talhasoyludev/aso-marketinghub` and `/plugin install marketinghub@marketinghub` work in a clean Claude Code session.
- [ ] `npx skills add talhasoyludev/aso-marketinghub` works.
- [ ] Real setup on one of your own apps, end to end, with `lang` set to `en`: setup → refresh → panel → Claude analysis. Fix anything that confuses you; a stranger will be more confused.
- [ ] Every link and image path in README.md and README.tr.md resolves.

### Repo
- [ ] Apply `docs/github-settings.md`: description, website, topics, Discussions categories.
- [ ] CHANGELOG.md and CONTRIBUTING.md are in place and linked from the README.
- [ ] Add issue templates for "bug" and "store page changed" (scanner breakages will be the most common report).
- [ ] Open and pin the roadmap issue (text idea in `docs/github-settings.md`).
- [ ] Label 3-5 small issues `good first issue` (for example: a new panel language, a new audit rule).
- [ ] Merge the launch branch to `main`, tag `v0.2.0`, publish the release with the notes from `docs/github-settings.md` and attach the GIF.

### Accounts
- [ ] Reddit account has enough karma for r/ClaudeAI (showcase posts have needed 50+) and r/iOSProgramming App Saturday.
- [ ] Product Hunt maker profile is complete. Schedule the launch, don't post it live at a random hour.
- [ ] HN account exists and has some history of normal comments.

## Launch week

Spread posts out. One channel per day lets you answer every comment, and each audience sees a post written for them.

| Day | Channel | Notes |
|---|---|---|
| Mon | r/ClaudeAI | Showcase flair, "how Claude was used" in detail. Submit the Anthropic community plugin form and Claude Marketplaces the same day. |
| Tue | Show HN | Weekday morning US Eastern. Post the first comment right away. Stay for 3-4 hours. |
| Wed | X thread + LinkedIn (TR) | GIF on tweet 1. Link in the first reply / first comment. |
| Thu | Product Hunt | 00:01 Pacific. Maker comment immediately. Share the PH link with people who already know the project; don't ask for upvotes. |
| Fri | r/androiddev (showcase/weekly thread if unsure) + r/SideProject | Different text for each. |
| Sat | r/iOSProgramming | App Saturday only. |
| Sun | r/indiehackers + awesome-list PRs | PRs to the lists marked "Submit now" in `directories.md`, one per list. |

Every day:
- [ ] Answer every comment and issue the same day.
- [ ] Write down every question people ask. The repeats go into the README FAQ the following week.
- [ ] Fix small bugs reported during launch week fast and ship them as `v0.2.x`. A visible fix within a day earns more trust than any post.

## After launch

- [ ] Respond to every new issue and PR within 24 hours, even if only to say "seen, will look this week".
- [ ] Weekly changelog post: every week something ships, add it to CHANGELOG.md and post one short update (X, plus Discussions → Announcements). Skip the week if nothing shipped; don't pad.
- [ ] When the repo passes about 20 stars, submit to `heilcheng/awesome-agent-skills`. Later, with real usage, to VoltAgent and travisvn (see `directories.md`).
- [ ] After a month, review what drove traffic (GitHub → Insights → Traffic → Referring sites) and repeat what worked.
- [ ] When a store page change breaks the scanner, fix it first; that is the most common reason a tool like this gets abandoned.
- [ ] Write the case study below once you have the numbers, then use it as the next post.

## Case study (fill in with your own numbers)

Do not publish this section until every value is real and from your own apps. Never estimate or round up.

- **App:** [name, platform, category]
- **Period:** [start date] to [end date]
- **Before:**
  - Tracked keywords ranked in top 50: [n of N] in [countries]
  - Live store locales: [n]
  - Ratings count: [n]
  - Monthly organic downloads / impressions (from App Store Connect / Play Console): [n]
- **What changed:** [title, subtitle, keyword field, new locales, screenshots; dates each one went live, as confirmed by publish verification]
- **After:**
  - Tracked keywords ranked in top 50: [n of N]
  - Live store locales: [n]
  - Ratings count: [n]
  - Monthly organic downloads / impressions: [n]
- **What didn't work:** [be specific]
- **Caveats:** [seasonality, other marketing that ran at the same time, small sample]
