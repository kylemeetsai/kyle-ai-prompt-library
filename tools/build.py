#!/usr/bin/env python3
"""Builds kylemeetsai.com from content/prompts/*.txt.

    python3 tools/build.py          # writes the site, then commit the generated files
    python3 tools/serve.py          # local preview at http://localhost:8768

Sources (edit these):
  content/prompts/<slug>.txt   one prompt per file (format: CLAUDE.md, "Adding a prompt")
  tools/templates/home.html    homepage body
  tools/templates/base.css     shared styles (prompt-page styles are appended from here)
Generated (never hand-edit): index.html, prompts/*.html, 404.html, data/prompts.json,
  assets/site.css, _redirects, _headers, sitemap.xml, robots.txt, favicon.ico
"""
import datetime, hashlib, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://kylemeetsai.com'
TIKTOK = 'https://www.tiktok.com/@kyle.meets.ai'
INSTAGRAM = 'https://www.instagram.com/kyle.meets.ai/'
EMAIL = 'kyle.meets.ai@gmail.com'
NEW_DAYS = 14

TOPICS = {'money': 'Money', 'agents': 'Agents', 'content': 'Content', 'career': 'Career',
          'design': 'Design', 'health': 'Health', 'skills': 'Skills'}
APPS = {'claude': 'Claude', 'chatgpt': 'ChatGPT', 'gemini': 'Gemini'}
FORMATS = {'prompt': 'Prompt', 'guide': 'Guide', 'link': 'Tool tips', 'skill': 'Skill'}
SECTIONS = ('description', 'steps', 'notes', 'prompt')
TOOLS = [  # "Tools I teach" strip. svg = inline file; color = keep original colours; label = name beside an icon
    {'svg': 'claude-logo.svg', 'h': 25, 'name': 'Claude'},
    {'file': 'chatgpt.svg', 'ar': 118 / 28, 'h': 25, 'name': 'ChatGPT'},
    {'file': 'muse.svg', 'ar': 1, 'h': 22, 'name': 'Meta Muse', 'label': 'Muse', 'color': True},
    {'file': 'higgsfield.svg', 'ar': 1, 'h': 20, 'name': 'Higgsfield', 'label': 'Higgsfield'},
    {'file': 'elevenlabs-wordmark.svg', 'ar': 694 / 90, 'h': 15, 'name': 'ElevenLabs'},
    {'file': 'world-labs-wordmark.svg', 'ar': 1029 / 225, 'h': 28, 'y': '-6px', 'name': 'World Labs'},
    {'file': 'notion-icon.svg', 'ar': 269 / 278, 'h': 22, 'name': 'Notion', 'label': 'Notion', 'color': True},
]
PARTNERS = [
    {'file': 'elevenlabs-wordmark.svg', 'ar': 694 / 90, 'h': 17, 'name': 'ElevenLabs'},
    {'file': 'typeless-wordmark.svg', 'ar': 369 / 81, 'h': 26, 'name': 'Typeless'},
    {'file': 'thetop.png', 'ar': 1000 / 194, 'h': 26, 'name': 'TheTop'},
]

e = lambda s: html.escape(s, quote=True)
today = datetime.date.today().isoformat()


def path(*p):
    return os.path.join(ROOT, *p)


def read(*p):
    with open(path(*p), encoding='utf-8') as f:
        return f.read()


ASSET_REF = re.compile(r'(/assets/[A-Za-z0-9_./-]+\.(?:mp4|webm|jpg|jpeg|png|svg|gif|webp|ico))(?![?\w])')


def version_assets(html_text):
    # Browsers keep /assets/ files for a week, so every image and video link carries its file's
    # hash: a changed file gets a new address and nobody sees a stale copy.
    def add(m):
        rel = m.group(1).lstrip('/')
        return m.group(1) + ('?v=' + version(rel) if os.path.exists(path(rel)) else '')
    return ASSET_REF.sub(add, html_text)


def write(rel, text):
    if rel.endswith('.html'):
        text = version_assets(text)
    full = path(rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(text)


def version(rel):
    with open(path(rel), 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


# ---------------------------------------------------------------- content
def parse(file):
    slug = os.path.basename(file)[:-4]
    meta, sections, cur, buf = {}, {}, None, []
    for line in read('content', 'prompts', file).split('\n'):
        m = re.fullmatch(r'=== ([a-z]+) ===', line.strip())
        if m and m.group(1) in SECTIONS and cur != 'prompt':
            if cur:
                sections[cur] = '\n'.join(buf).strip('\n')
            cur, buf = m.group(1), []
        elif cur:
            buf.append(line)
        elif line.strip():
            k, sep, v = line.partition(':')
            if not sep:
                fail(slug, f'line "{line}" is not "key: value"')
            meta[k.strip()] = v.strip()
    if cur:
        sections[cur] = '\n'.join(buf).strip('\n')
    p = {'slug': slug, **meta,
         'apps': meta.get('apps', '').split(), 'tool': meta.get('tool', ''),
         'tiktok': meta.get('tiktok', ''), 'copy': meta.get('copy', 'Copy prompt'),
         'description': sections.get('description', '').strip(),
         'steps': [s for s in sections.get('steps', '').split('\n') if s.strip()],
         'notes': [s for s in sections.get('notes', '').split('\n') if s.strip()],
         'prompt': sections.get('prompt', '').rstrip()}
    for key in ('title', 'desc', 'topic', 'format', 'added'):
        if not p.get(key):
            fail(slug, f'missing "{key}:"')
    if p['topic'] not in TOPICS:
        fail(slug, f'topic must be one of {", ".join(TOPICS)}')
    if p['format'] not in FORMATS:
        fail(slug, f'format must be one of {", ".join(FORMATS)}')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', p['added']):
        fail(slug, 'added must look like 2026-12-01')
    bad = [a for a in p['apps'] if a not in APPS]
    if bad:
        fail(slug, f'unknown app {bad}; use {", ".join(APPS)} (or "tool:" for another tool)')
    if not p['prompt'] or not p['steps']:
        fail(slug, 'needs a "=== steps ===" and a "=== prompt ===" section')
    if p['tiktok'] and not p['tiktok'].isdigit():
        fail(slug, 'tiktok is the video number only')
    if re.search(r'[—]', p['title'] + p['desc'] + p['description'] + ''.join(p['steps'] + p['notes'])):
        print(f'  note: {slug} has an em dash in its page text')
    return p


def fail(slug, msg):
    sys.exit(f'content/prompts/{slug}.txt: {msg}')


# ---------------------------------------------------------------- pieces
def head(title, desc, url_path, extra='', noindex=False):
    css = '/assets/site.css?v=' + version('assets/site.css')
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{'<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{SITE}{url_path}">'}
<meta property="og:type" content="website">
<meta property="og:site_name" content="KyleMeetsAI">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{url_path}">
<meta name="theme-color" content="#ECEEF1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0F1114" media="(prefers-color-scheme: dark)">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/icon-48.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Geist:wght@400..700&family=Geist+Mono:wght@400..600&display=swap">
<link rel="stylesheet" href="{css}">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''


HEADER = '''<header class="site-header">
  <div class="wrap">
    <a class="wordmark" href="/" aria-label="KyleMeetsAI home"><img src="/assets/photo/kyle-tiktok-avatar.jpg" alt="" width="36" height="36"><span>KyleMeets<b>AI</b></span></a>
    <nav class="nav" aria-label="Main">
      <a class="hide-sm" href="/#prompts">Prompts</a>
      <a class="hide-sm" href="/#videos">Videos</a>
      <a class="hide-sm" href="/#about">About</a>
      <a class="nav-cta" href="/#work">Work with me</a>
    </nav>
  </div>
</header>
'''

FOOTER = f'''<footer class="site-footer">
  <div class="wrap">
    <a class="wordmark" href="/"><span>KyleMeets<b>AI</b></span></a>
    <nav aria-label="Footer">
      <a href="/#prompts">Prompts</a>
      <a href="/#videos">Videos</a>
      <a href="{TIKTOK}" target="_blank" rel="noopener">TikTok</a>
      <a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a>
      <a href="/#work">Work with me</a>
    </nav>
    <span class="fine">© {datetime.date.today().year} KyleMeetsAI</span>
  </div>
</footer>'''


def app_chips(p):
    names = [APPS[a] for a in p['apps']] or ([p['tool']] if p['tool'] else [])
    return ''.join(f'<span class="app">{e(n)}</span>' for n in names)


def card(p):
    return (f'<a class="p-card" href="/prompts/{p["slug"]}" data-drawer="{p["slug"]}" data-topic="{p["topic"]}" '
            f'data-apps="{" ".join(p["apps"])}" data-format="{p["format"]}" data-added="{p["added"]}"{" hidden" if p["added"] > today else ""}>'
            f'<span class="p-meta"><span class="p-topic">{TOPICS[p["topic"]]}</span><span class="new" hidden>New</span></span>'
            f'<h3>{e(p["title"])}</h3><p>{e(p["desc"])}</p>'
            f'<span class="p-foot"><span class="apps">{app_chips(p)}</span><span class="p-open">Open <span class="arrow" aria-hidden="true">→</span></span></span></a>')


def logos(items, copies):
    claude = read('tools', 'templates', 'claude-logo.svg').strip()

    def one(it, hidden):
        if 'svg' in it:
            mark = f'<span style="--h:{it["h"]}px">{claude}</span>'
        elif it.get('color'):
            mark = f'<img src="/assets/logos/{it["file"]}" alt="" style="height:{it["h"]}px;width:auto">'
        else:
            y = f';--y:{it["y"]}' if it.get('y') else ''
            mark = (f'<span class="logo" style="--src:url(&quot;/assets/logos/{it["file"]}&quot;);'
                    f'--ar:{it["ar"]:.4f};--h:{it["h"]}px{y}"></span>')
        label = f'<span class="brand-name">{e(it["label"])}</span>' if it.get('label') else ''
        a11y = 'aria-hidden="true"' if hidden else f'role="img" aria-label="{e(it["name"])}"'
        return f'<span class="brand" {a11y}>{mark}{label}</span>'
    out = []
    for half in range(2):  # the second half makes the loop seamless
        for c in range(copies):
            out += [one(it, half > 0 or c > 0) for it in items]
    return ''.join(out)


def related(p, prompts):
    others = [o for o in prompts if o['slug'] != p['slug']]
    groups = {}  # same topic first, then most apps in common; newest first inside each group
    for o in others:
        groups.setdefault((o['topic'] != p['topic'], -len(set(o['apps']) & set(p['apps']))), []).append(o)
    ordered = []
    for k in sorted(groups):
        ordered += sorted(groups[k], key=lambda o: o['added'], reverse=True)
    return ordered[:6]  # the page shows the first 3 whose videos are already out


# ---------------------------------------------------------------- pages
def prompt_page(p, prompts):
    slug, fmt = p['slug'], p['format']
    noun = p['copy'][5:] if p['copy'].startswith('Copy ') else 'prompt'
    names = [APPS[a] for a in p['apps']]
    works = (f'<div class="p-works"><span class="label">Works in</span><span class="apps">{app_chips(p)}</span></div>'
             if names or p['tool'] else '')
    actions = []
    copy_btn = lambda cls: f'<button class="btn {cls}" type="button" data-copy>{e(p["copy"])}</button>'
    if p.get('try'):
        url, label, sub = (p['try'].split('|') + ['', ''])[:3]
        actions.append(f'<a class="btn btn-primary" href="{e(url.strip())}" target="_blank" rel="noopener">{e(label.strip())} <span aria-hidden="true">↗</span></a>')
        actions.append(copy_btn('btn-ghost'))
        try_sub = f'<p class="p-fine">{e(sub.strip())}</p>' if sub.strip() else ''
    else:
        actions.append(copy_btn('btn-primary'))
        try_sub = ''
    if p.get('download'):
        actions.append(f'<a class="btn btn-ghost" href="/{e(p["download"])}" download>Download {e(p["download"])}</a>')
    if p['tiktok']:
        actions.append(f'<a class="btn btn-ghost" href="{TIKTOK}/video/{p["tiktok"]}" target="_blank" rel="noopener">Watch the video <span aria-hidden="true">↗</span></a>')
    source = ''
    if p.get('source'):
        by, url = (p['source'].split('|') + [''])[:2]
        source = (f'<p class="p-fine">{e(by.strip())} · <a href="{e(url.strip())}" target="_blank" rel="noopener">'
                  f'View source on GitHub <span aria-hidden="true">↗</span></a></p>')
    steps = ''.join(f'<li><span>{s}</span></li>' for s in p['steps'])
    notes = ''.join(f'<p>{n}</p>' for n in p['notes'])
    notes = f'<div class="p-notes">{notes}</div>' if notes else ''
    rel = ''.join(card(o) for o in related(p, prompts))
    lede = p['description'] or e(p['desc'])
    body = f'''{HEADER}
<main id="main" class="p-main">
  <div class="wrap">
    <div class="p-layout">
    <article class="p-article" data-added="{p['added']}">
      <a class="crumb" href="/#prompts"><span aria-hidden="true">←</span> All prompts</a>
      <header class="p-hero">
        <div class="p-eyebrow"><span class="label">{FORMATS[fmt] if TOPICS[p['topic']].rstrip('s') == FORMATS[fmt] else TOPICS[p['topic']] + ' · ' + FORMATS[fmt]}</span><span class="new" hidden>New</span></div>
        <h1>{e(p['title'])}</h1>
        <p class="p-lede">{lede}</p>
        {source}
        {works}
        <div class="p-actions">{''.join(actions)}</div>
        {try_sub}
      </header>

      <section class="p-section" aria-labelledby="how-h">
        <h2 class="p-h2" id="how-h">How to use it</h2>
        <ol class="p-steps">{steps}</ol>
        {notes}
      </section>

      <section class="p-section" aria-labelledby="box-h">
        <div class="p-box">
          <div class="p-box-bar"><h2 class="label" id="box-h">The {e(noun)}</h2><button class="copy-btn" type="button" data-copy>{e(p['copy'])}</button></div>
          <div class="p-box-text" id="prompt-text" tabindex="0">{e(p['prompt'])}</div>
        </div>
        <div class="p-after"><button class="btn btn-primary" type="button" data-copy>{e(p['copy'])}</button></div>
      </section>
    </article>

    <aside class="kyle-card" aria-label="About Kyle">
      <div class="kyle-card-tile"><img src="/assets/photo/kyle-square.jpg" alt="" width="600" height="600" loading="lazy"><span class="tile-name" aria-hidden="true"><span class="mic"><i></i><i></i><i></i><i></i></span>KyleMeetsAI</span></div>
      <div class="kyle-card-copy"><p class="kyle-card-title">Hi, I’m Kyle.</p><p>I post a new AI how-to every week, and its prompt waits for you here.</p></div>
      <div class="kyle-card-links"><a class="btn btn-ghost" href="{TIKTOK}" target="_blank" rel="noopener">TikTok <span aria-hidden="true">↗</span></a><a class="btn btn-ghost" href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram <span aria-hidden="true">↗</span></a></div>
    </aside>

    <section class="p-section p-related" aria-labelledby="rel-h">
      <div class="p-related-head"><h2 class="p-h2" id="rel-h">More like this</h2><a class="p-all" href="/#prompts">All prompts <span class="arrow" aria-hidden="true">→</span></a></div>
      <div class="p-grid" id="related">{rel}</div>
    </section>
    </div>
  </div>
</main>
{FOOTER}
<script src="/assets/prompt.js?v={version('assets/prompt.js')}" defer></script>
</body>
</html>
'''
    return head(f'{p["title"]} · KyleMeetsAI', p['desc'], f'/prompts/{slug}', noindex=p['added'] > today) + body


def home_page(prompts):
    live = [p for p in prompts if p['added'] <= today]
    chips = '<button class="chip" type="button" data-group="topic" data-value="all" aria-pressed="true">All</button>'
    chips += ''.join(f'<button class="chip" type="button" data-group="topic" data-value="{k}" aria-pressed="false">{v}</button>' for k, v in TOPICS.items())
    chips += '<span class="sep" aria-hidden="true"></span>'
    chips += ''.join(f'<button class="chip" type="button" data-group="app" data-value="{k}" aria-pressed="false">{v}</button>' for k, v in APPS.items())
    body = read('tools', 'templates', 'home.html')
    fills = {
        'TOOL_LOGOS': logos(TOOLS, 1), 'PARTNER_LOGOS': logos(PARTNERS, 2), 'CHIPS': chips,
        'COUNT': f'{len(live)} prompts and guides', 'CARDS': ''.join(card(p) for p in prompts),
        'FOOTER': FOOTER,
    }
    for k, v in fills.items():
        body = body.replace('{{%s}}' % k, v)
    left = re.findall(r'\{\{[A-Z_]+\}\}', body)
    if left:
        sys.exit(f'home.html: unfilled {left}')
    desc = 'Kyle teaches everyday people and businesses how to put AI to work, with a free library of the exact prompts from every video.'
    return (head('KyleMeetsAI · AI, made easy', desc, '/') + HEADER + body.replace('<main id="top">', '<main id="main">') +
            f'\n<script src="/assets/home.js?v={version("assets/home.js")}" defer></script>\n</body>\n</html>\n')


def not_found_page():
    body = f'''{HEADER}
<main id="main" class="p-main">
  <div class="wrap">
    <div class="nf">
      <span class="label">Page not found</span>
      <h1>That link moved.</h1>
      <p class="p-lede">Every prompt now lives in one library. Search it by what you want to get done.</p>
      <form class="nf-search" action="/" method="get" role="search">
        <label class="search"><span class="sr">Search prompts</span>
          <svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="9" cy="9" r="6" fill="none" stroke="currentColor" stroke-width="2"/><path d="m14 14 4 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          <input name="q" type="search" placeholder="Try “budget”, “resume” or “agent”" autocomplete="off">
        </label>
        <button class="btn btn-primary" type="submit">Search</button>
      </form>
      <a class="btn btn-ghost" href="/#prompts">See all prompts</a>
    </div>
  </div>
</main>
{FOOTER}
</body>
</html>
'''
    return head('Page not found · KyleMeetsAI', 'This page moved. Search the KyleMeetsAI prompt library.', '/404', noindex=True) + body


# ---------------------------------------------------------------- build
def main():
    files = sorted(f for f in os.listdir(path('content', 'prompts')) if f.endswith('.txt'))
    prompts = [parse(f) for f in files]
    prompts.sort(key=lambda p: (p['added'], p['title']), reverse=True)

    css = read('tools', 'templates', 'base.css') + '\n' + read('tools', 'templates', 'pages.css')
    write('assets/site.css', css)

    write('index.html', home_page(prompts))
    for p in prompts:
        write(f'prompts/{p["slug"]}.html', prompt_page(p, prompts))
    known = {f'{p["slug"]}.html' for p in prompts}
    for f in os.listdir(path('prompts')):
        if f.endswith('.html') and f not in known:
            os.remove(path('prompts', f))
            print('  removed prompts/' + f)
    write('404.html', not_found_page())

    data = [{k: p[k] for k in ('slug', 'title', 'desc', 'topic', 'apps', 'tool', 'format', 'added', 'tiktok', 'copy', 'prompt')}
            for p in prompts]
    write('data/prompts.json', json.dumps(data, ensure_ascii=False, separators=(',', ':')))

    # Old links (kyle-ai-prompt-library.pages.dev/<slug>, captions, DMs) keep working.
    lines = ['# Generated by tools/build.py. Old prompt links go to their new pages.',
             '/classes / 301', '/classes.html / 301', '/prompts / 301', '/prompts/ / 301',
             '/profile.jpg /assets/photo/kyle-tiktok-avatar.jpg 301',
             '# Working files stay in the repo but are not part of the site.',
             '/CLAUDE.md / 301', '/README.md / 301', '/tools/* / 301', '/content/* / 301']
    for p in prompts:
        lines += [f'/{p["slug"]} /prompts/{p["slug"]} 301', f'/{p["slug"]}.html /prompts/{p["slug"]} 301']
    write('_redirects', '\n'.join(lines) + '\n')

    urls = [f'{SITE}/'] + [f'{SITE}/prompts/{p["slug"]}' for p in prompts if p['added'] <= today]
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    write('_headers', '/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n'
          '/assets/*\n  Cache-Control: public, max-age=604800\n')

    live = sum(p['added'] <= today for p in prompts)
    print(f'built {len(prompts)} prompt pages ({live} live today, {len(prompts) - live} waiting for their video), homepage, 404, redirects')


if __name__ == '__main__':
    main()
