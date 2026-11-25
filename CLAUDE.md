# CLAUDE.md: working guide for this repo

This repo is **kylemeetsai.com**: Kyle's link-in-bio site and prompt library for a
non-technical TikTok and Instagram audience. It replaced the old prompt hub in Nov 2026. This
file is the process of record. Follow it.

## Rules that never bend

- **Kyle is only "Kyle" or "KyleMeetsAI".** Never his last name: not in page text, file names,
  image metadata, commit authors, or absolute file paths (his computer's username contains it,
  so never commit a path like `/Users/...`). No rates, no employer name, no LinkedIn link.
- **No em dashes** in anything Kyle or a visitor reads (page copy, descriptions, steps, notes).
  Prompt texts are AI input and may keep them.
- **Real viewer comments only** on the homepage. Never invent quotes.
- **Audience is non-technical.** Optimize for "tap, copy, paste." Never make them use GitHub, a
  terminal, or anything technical to get value.

## How the site works

- **Static files, built locally, no build on Cloudflare.** Merging into `main` publishes to
  Cloudflare Pages (project `kyle-ai-prompt-library`) within a minute or two.
- **You edit sources; `python3 tools/build.py` writes the site.** Commit both.
  - Sources: `content/prompts/<slug>.txt` (one file per prompt), `tools/templates/home.html`
    (homepage body), `tools/templates/base.css` + `pages.css` (styles), `assets/home.js`,
    `assets/prompt.js`, images and video in `assets/`.
  - Generated, never hand-edit: `index.html`, `prompts/<slug>.html`, `404.html`,
    `data/prompts.json`, `assets/site.css`, `_redirects`, `sitemap.xml`, `robots.txt`.
- **URLs:** homepage `/`, each prompt `/prompts/<slug>`. Old links (`/<slug>`, `/<slug>.html`,
  `/classes`) redirect through `_redirects`, so captions and DMs never break. `/?q=budget` opens
  the library already searched.
- **Homepage library:** every prompt is a card (newest first). Search (with a synonym list,
  `SYNONYMS` in `assets/home.js`), topic and app filters, 5 cards on phones and 9 on desktop
  until "Show all". Tapping a card opens a drawer with the full text and a copy button, and
  the address bar changes to the prompt's own page, so links and visitor stats work.
- **Dates:** `added` is the day the video posts. A prompt's card appears on the homepage on
  that day (until then its page works by direct link only, which suits scheduled posts). The
  "New" badge shows for 14 days. Both happen in the visitor's browser, so no rebuild is needed
  on the day.
- **Preview locally:** `python3 tools/serve.py` (port 8768) behaves like Cloudflare Pages:
  `/prompts/x` works, `_redirects` applies, unknown paths get the 404 page.

## Adding a prompt (or guide, link, skill)

1. Copy an existing file in `content/prompts/` to `content/prompts/<new-slug>.txt` (slug =
   lowercase words with hyphens) and edit it. Format:

   ```
   title: Claude Finds Refunds Companies Owe You
   desc: One or two sentences for the card and search results.
   headline: YOUR INBOX IS HIDING REFUNDS          (the video's on-screen hook; kept for reference)
   sub: One prompt · Claude finds money you're owed   (kept for reference)
   topic: money                (money, agents, content, career, design, health, skills)
   apps: claude chatgpt        (any of claude chatgpt gemini, in that order; see App tags)
   tool: Atlas                 (only when it runs in a non-chat tool instead of apps)
   format: prompt              (prompt, guide, link, skill)
   added: 2026-12-01           (the day its video posts)
   tiktok: 7711774082081017102 (video number; leave the line out until it posts)
   copy: Copy prompt           (button label: Copy prompt, Copy rules, Copy skill...)
   try: https://site.com | Try Atlas | small line under the button    (link format only)
   source: By Author · MIT license | https://github.com/...           (hosted skills only)
   download: humanizer.md      (a file at the repo root offered as a download)

   === description ===
   The longer description under the page title. Inline <strong> and <em> are fine.

   === steps ===
   One how-to step per line. Inline <strong> and <em> are fine.

   === notes ===
   Optional. One "Good to know" or "Using ChatGPT? ..." line per line.

   === prompt ===
   The exact text people copy. Everything after this line is copied as-is.
   ```
   (The notes in brackets above are explanations, not part of the file.)
2. Run `python3 tools/build.py`. It stops with a clear message if a field is missing or wrong,
   and notes any em dash in page copy.
3. Preview with `python3 tools/serve.py`, open `/prompts/<slug>` and the homepage, and check
   the card, the drawer and the copy button.
4. Commit the content file **and** the generated files together.

When the video posts, add its `tiktok:` line, rebuild and commit. That turns on "Watch the
video" on the page and in the drawer.

## Giveaway types

- **Prompt:** the copy box is the point (the AI does the work).
- **Guide:** the steps are the main content; the copy box holds an optional helper prompt.
- **Link:** the tool does the work. Add a `try:` line for a big "Try <tool>" button to the
  official site, plus tips in the copy box (see `atlas-photo-rules.txt`).
- **Skill:** host the skill file at the repo root verbatim (keep the original author's credit
  and license inside it), put its text in the prompt section, and add `source:` and
  `download:` lines (see `humanizer-skill.txt`). GitHub is the credit link, never the front
  door. Never strip authorship or imply Kyle wrote it.

## App tags

One tag per AI app the prompt honestly works in, in this order: Claude, ChatGPT, Gemini. Tag an
app ONLY after checking the prompt against that app's official docs (the Remotion project's
`docs/AI app capabilities (Nov 2026).md`). A tag that needs a small change gets that change (an
app-neutral wording edit plus a one-line "Using ChatGPT? ..." note). When unsure, leave the tag
off. Connectors (Gmail, Notion, Sheets) go in the text, not the tags. A page that sends people to
a non-chat tool uses `tool:` instead of `apps:`.

## Visitor stats

Cloudflare Web Analytics is on for this Pages project (privacy-friendly: no cookies, no banner).
Cloudflare injects its beacon on every deployment, so pages need no snippet. Drawer opens count
as visits to `/prompts/<slug>` because the address changes. Numbers: Cloudflare dashboard,
Workers & Pages, kyle-ai-prompt-library, Metrics, View Web Analytics.

## Git and PR workflow

- Prompt publishing happens on branch **`claude/prompt-library-organization-7pc5j0`**. One
  change = one PR into `main`. Don't stack.
- Since Nov 2026 Kyle has pre-approved publishing a video's prompt when the video is scheduled
  (Claude opens the PR and merges it). Anything else, Kyle reviews and merges.
- After a PR merges, restart the branch from main before the next change:
  `git fetch origin main && git checkout -B claude/prompt-library-organization-7pc5j0 origin/main`
  (a `git push --force-with-lease` is fine then).
- Commit messages: clear and descriptive, no model identifiers.

## Verify before shipping

- `python3 tools/build.py` runs clean.
- In the local preview, check the homepage at phone width (390px) and desktop, the new prompt
  page, search for a word from the new prompt, open its drawer and copy.
- `git diff --name-only` touches only what you intended: the content file plus regenerated
  output. A rebuild also refreshes `index.html`, `data/prompts.json` and other prompts'
  related lists; that's expected.
- After merging, confirm it's live: `curl -sL https://kylemeetsai.com/prompts/<slug>` and look
  for the title (an unknown path returns the 404 page).
