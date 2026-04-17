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
4. Open `index.html` and add a new `<a class="prompt-card">` block pointing to your new file
5. Re-upload the folder to Cloudflare/Netlify — it'll update the live site

## Branding

- Accent color: `#ff6b2c` (the orange bar from your TikTok intros)
- Background: `#fafaf7` (warm off-white)
- Typography: system fonts (San Francisco on iPhone, feels native)
- Styling matches your TikTok intro cards — bold black headline + orange accent bar

## Analytics

This setup doesn't include its own analytics. You'll see click counts in Beacons (how many people tapped "AI Resume Optimizer" from your bio page). To track copy actions specifically, you can add Cloudflare Web Analytics or Plausible later (both free tiers).

## Questions?

Ask Claude. Built by Kyle.
