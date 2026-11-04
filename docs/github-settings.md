# GitHub repository settings

Values to apply by hand in the repository settings. Nothing here is applied automatically.

## Description (Settings → General → About)

```
Free, local ASO dashboard for iOS and Android apps, driven by Claude Code. Tracks App Store keyword rankings across countries, maps competitor keywords, audits metadata and localization, and verifies what went live. Python stdlib only, no API keys, your data stays on your machine.
```

(281 characters; the limit is 350.)

## Website

Until there is a dedicated page, leave the website field pointing at the demo instructions:

```
https://github.com/talhasoyludev/aso-marketinghub#try-the-demo-in-30-seconds
```

If you later publish the demo with GitHub Pages (the panel is a static page served from the repo root, so `https://talhasoyludev.github.io/aso-marketinghub/?demo=1` should work once Pages is enabled, provided the demo data is committed; test it first), use that URL instead. It lets people try the panel without cloning.

## Topics (12)

```
aso
app-store-optimization
app-store
google-play
keyword-tracking
mobile-marketing
localization
indie-dev
claude-code
claude-skills
agent-skills
python
```

## Social preview image

Settings → General → Social preview. This is what shows when the repo link is shared on X, LinkedIn, Slack and Discord.

- **Size:** 1280×640 PNG, under 1 MB. Keep important content inside the central 1200×600; some platforms crop the edges.
- **Left 45%:** the name "MarketingHub" in large type, and under it one line: "Free, local ASO for iOS and Android apps". Below that, smaller: "No API keys · Python stdlib · Claude Code skill".
- **Right 55%:** a cropped screenshot from the demo, ideally Competitor Radar with country rankings and deltas, or ASO Center with the publish verification panel. Slight shadow or device-free frame; no phone mockups.
- **Background:** the panel's own background colour, so the screenshot blends in.
- **Avoid:** small text (it is often shown at 400 px wide), emoji, stars or download counts, logos of Apple, Google or Anthropic.

## Pinned issue

Title: **Roadmap and feedback: what should MarketingHub measure next?**

Body idea:

> MarketingHub v0.2.0 is out. This issue is where the roadmap lives.
>
> **Shipping next:** [2-3 concrete items you actually plan].
> **Under consideration:** [items], vote with a reaction.
> **Not planned:** real search volume (no free source exists), Google Play rankings (no public API).
>
> Tell us: which platform you ship on, how many keywords and countries you track, and the one thing you still do by hand. Bugs go in separate issues, please.

Keep it updated after each release; an outdated roadmap is worse than none.

## Discussions

Enable Discussions (Settings → General → Features) with these categories:

| Category | Format | Purpose |
|---|---|---|
| Announcements | Announcement (maintainers only) | Releases and the weekly changelog post. |
| Q&A | Question / Answer | Setup and usage questions; mark the answer. |
| Ideas | Open discussion | Feature requests before they become issues. |
| Show and tell | Open discussion | People sharing their own setup or results. |
| ASO strategy | Open discussion | Keyword and localization questions not about the tool itself. |
| Translations | Open discussion | Coordinating new panel languages. |

Delete the default "General" and "Polls" categories if unused, so posts land somewhere specific.

## Release notes for v0.2.0

Tag: `v0.2.0` · Title: **v0.2.0: demo mode, English output, plugin install**

```markdown
MarketingHub is a free, local ASO dashboard for iOS and Android apps. A scanner measures your app and your competitors from the public stores, a panel turns that into decisions, and Claude Code writes the store copy following the skill shipped in this repo.

## New

- **Demo mode.** Try the panel with a fictional sample app, no config and no scan: `demo.bat` (Windows), `./demo.command` (macOS), or `python -m http.server 8137` and open http://localhost:8137/?demo=1.
- **Claude Code plugin install.** `/plugin marketplace add talhasoyludev/aso-marketinghub`, then `/plugin install marketinghub@marketinghub`. Or `npx skills add talhasoyludev/aso-marketinghub`.
- **English console output.** The scanner and setup scripts now print in English by default, and in Turkish when `config.json > lang` is `"tr"`. Rule-engine recommendations follow the same setting.

## Docs

- Rewritten README in English and Turkish: quick demo, 3-step setup, honest limits, FAQ.
- Added CONTRIBUTING.md and CHANGELOG.md.

## Upgrading

Pull the latest `main`. Your `workspace/` folder is untouched. If you want Turkish console output, set `"lang": "tr"` in `workspace/config.json`.

## Known limits

- Keyword volume and difficulty are estimates, not search volume.
- Rankings are App Store only; Google Play has no public ranking API.
- The iOS keyword field cannot be verified from outside the console.

Full list of changes: see [CHANGELOG.md](CHANGELOG.md).
```
