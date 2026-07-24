# kyle.meets.ai — Prompt Pages

A lightweight, mobile-first prompt library for your TikTok bio link.

## What's in this folder

- `index.html` — the hub page (your main "link in bio" destination, lists all prompts)
- `resume-optimizer.html` — AI Resume Optimizer
- `budget-tracker.html` — AI Budget Tracker

## How to deploy it (free, ~5 minutes)

### Option 1 — Cloudflare Pages (recommended)

1. Go to https://pages.cloudflare.com and sign up (free)
2. Click **Create a project** → **Direct Upload**
3. Name it something like `kyle-prompts`
4. Drag this entire folder onto the upload area
5. Click **Deploy**
6. You'll get a URL like `kyle-prompts.pages.dev` — that's your link

### Option 2 — Netlify Drop (even simpler, no account needed to test)

1. Go to https://app.netlify.com/drop
2. Drag the folder onto the page
3. You get a live URL instantly
4. To make it permanent, sign up for a free Netlify account

Either way, your Beacons bio button will point to `yoururl.com/` (the hub) or individual prompt pages.

## How to add a new prompt later

1. Duplicate one of the existing prompt files (e.g. `resume-optimizer.html`) and rename it (e.g. `email-writer.html`)
2. Open the new file in any text editor (TextEdit on Mac works fine)
3. Update these three things:
   - The `<title>` tag at the top (browser tab name)
   - The `<div class="headline">` text (the big bold headline)
   - The prompt text inside `<div class="prompt-box" id="prompt-text">` (between the opening and closing tags)
   - The `<div class="description">` text
4. Open `index.html` and add a new `<a class="prompt-card">` block pointing to your new file. Copy an existing card and update its link, tool tag, title, and description. Each card needs two attributes so it sorts into the right filter:
   - `data-topic="..."` — which filter pill it appears under. One of: `skills`, `career`, `design`, `content`, `health`, `money`, `agents`
   - `data-tool="..."` — the colored tool tag on the card. One of: `claude`, `design` (Claude Design), `agent`, `connector`, `chatgpt`, `skill`
   - Add `data-new` (no value) to show a **NEW** badge; remove it later once the prompt isn't new anymore
   - Inside the card, the first row is `<div class="card-meta">` holding the `<span class="tool-tag tool-XXX">Label</span>` (and the NEW badge if used). Match the `tool-XXX` class to your `data-tool` value.

   Example:
   ```html
   <a href="email-writer.html" class="prompt-card" data-topic="content" data-tool="claude" data-new>
     <div class="card-meta"><span class="tool-tag tool-claude">Claude</span><span class="new-badge">New</span></div>
     <div class="prompt-title">AI Email Writer <span class="arrow">→</span></div>
     <div class="prompt-desc">Short description of what the prompt does.</div>
   </a>
   ```
   The pill counts update themselves automatically — no need to edit any numbers.
5. Re-upload the folder to Cloudflare/Netlify — it'll update the live site

## How to add a new Skill

Skills (like `humanizer-skill.html`) work the same way as prompts, with two extras:

1. Save the skill's markdown file into the folder (e.g. `humanizer.md`), keeping any
   original author credit / license notice inside it intact.
2. Duplicate `humanizer-skill.html`, rename it, and update the headline, description, the
   `How to use it` steps, the **Source** credit line (author + GitHub link), and the skill
   text inside `<div class="prompt-box">`. The `Download` button points at the `.md` file.
3. In `index.html`, add the card with `data-topic="skills"` and `data-tool="skill"` (rose
   `Skill` tag). That populates the **Skills** pill automatically.

Host the file yourself and always credit the original author with a link back to their
GitHub — don't send non-technical followers to GitHub to download.

## Branding

- Accent color: `#ff6b2c` (the orange bar from your TikTok intros)
- Background: `#fafaf7` (warm off-white)
- Typography: system fonts (San Francisco on iPhone, feels native)
- Styling matches your TikTok intro cards — bold black headline + orange accent bar

## Analytics

This setup doesn't include its own analytics. You'll see click counts in Beacons (how many people tapped "AI Resume Optimizer" from your bio page). To track copy actions specifically, you can add Cloudflare Web Analytics or Plausible later (both free tiers).

## Questions?

Ask Claude. Built by Kyle.
