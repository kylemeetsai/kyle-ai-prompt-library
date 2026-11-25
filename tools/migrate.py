"""One-time move: old root prompt pages (<slug>.html) -> content/prompts/<slug>.txt.

Run again after rebasing if main gained a new old-style page; it only writes slugs that
don't have a content file yet (pass --force to redo all). Delete once the new site is live.
"""
import html, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'content', 'prompts')
SKIP = {'index.html', 'classes.html'}
force = '--force' in sys.argv

def text(s):
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

def inner(s, cls, tag='div'):
    m = re.search(r'<%s class="%s"[^>]*>([\s\S]*?)</%s>' % (tag, cls, tag), s)
    return m.group(1).strip() if m else ''

def plain_title(s):
    s = ''.join(ch for ch in s if unicodedata.category(ch) not in ('So', 'Sk', 'Mn', 'Cf'))
    return re.sub(r'\s+([:?!,.)])', r'\1', re.sub(r'\s+', ' ', s)).strip()

def tidy(s):
    return re.sub(r'\s+', ' ', s).strip()

# card data from the old hub
hub = open(os.path.join(ROOT, 'index.html')).read()
cards = {}
for m in re.finditer(r'<a href="([\w-]+)\.html" class="prompt-card"([^>]*)>([\s\S]*?)</a>', hub):
    slug, attrs, body = m.groups()
    a = dict(re.findall(r'data-([\w-]+)="([^"]*)"', attrs))
    t = re.search(r'<div class="prompt-title">([\s\S]*?)<span class="arrow"', body)
    d = re.search(r'<div class="prompt-desc">([\s\S]*?)</div>', body)
    cards[slug] = {'title': plain_title(text(t.group(1))) if t else '', 'desc': text(d.group(1)) if d else '',
                   'topic': a.get('topic', ''), 'apps': a.get('apps', a.get('tool', '')),
                   'format': a.get('format', 'prompt'), 'added': a.get('added', '')}

os.makedirs(OUT, exist_ok=True)
done = 0
for f in sorted(os.listdir(ROOT)):
    if not f.endswith('.html') or f in SKIP:
        continue
    slug = f[:-5]
    dest = os.path.join(OUT, slug + '.txt')
    if os.path.exists(dest) and not force:
        continue
    s = open(os.path.join(ROOT, f)).read()
    s = s[s.index('<body'):]
    c = cards.get(slug)
    if not c:
        print('!! no hub card for', slug); continue
    watch = re.search(r'href="https://www\.tiktok\.com/@kyle\.meets\.ai/video/(\d+)"', s)
    copy = re.search(r'id="copy-label">([^<]+)<', s)
    apps = ' '.join(a for a in c['apps'].split() if a in ('claude', 'chatgpt', 'gemini'))
    tool = 'Atlas' if slug == 'atlas-photo-rules' else ''
    meta = [('title', c['title']), ('desc', c['desc']),
            ('headline', text(inner(s, 'headline'))), ('sub', text(inner(s, 'subhead'))),
            ('topic', c['topic']), ('apps', apps), ('tool', tool), ('format', c['format']), ('added', c['added']),
            ('tiktok', watch.group(1) if watch else ''), ('copy', text(copy.group(1)) if copy else 'Copy prompt')]
    t = re.search(r'<a class="try-button" href="([^"]+)"[^>]*>([\s\S]*?)</a>', s)
    if t:
        label = text(t.group(2)).rstrip(' →').strip()
        meta.append(('try', '%s | %s | %s' % (t.group(1), label, text(inner(s, 'try-sub')))))
    src = inner(s, 'source-line')
    if src:
        by = text(re.sub(r'<span class="tool-tag">[\s\S]*?</span>', '', src.split('<a ')[0])).rstrip(' ·').strip()
        url = re.search(r'href="([^"]+)"', src)
        meta.append(('source', '%s | %s' % (by, url.group(1) if url else '')))
    dl = re.search(r'<a class="btn btn-download" href="([^"]+)"', s)
    if dl:
        meta.append(('download', dl.group(1)))
    steps_html = inner(s, 'how-to-steps')
    steps, notes = [], []
    for line in re.split(r'<br\s*/?>', steps_html):
        line = tidy(line)
        if not line:
            continue
        m = re.match(r'<strong>\d+\.</strong>\s*(.*)$', line)
        if m:
            steps.append(m.group(1))
        else:
            notes.append(re.sub(r'^<em>([\s\S]*)</em>$', r'\1', line))
    note = inner(s, 'how-to-note')
    if note:
        notes.append(tidy(note))
    prompt = html.unescape(re.search(r'<div class="prompt-box" id="prompt-text">([\s\S]*?)</div>', s).group(1))
    if '<' in re.sub(r'<(?=[^a-zA-Z/])', '', prompt) and re.search(r'</?(br|div|span|p)\b', prompt):
        print('!! tags inside prompt box:', slug)
    out = ['%s: %s' % kv for kv in meta if kv[1]]
    out += ['', '=== description ===', tidy(inner(s, 'description')), '', '=== steps ===', *steps]
    if notes:
        out += ['', '=== notes ===', *notes]
    out += ['', '=== prompt ===', prompt.strip('\n')]
    open(dest, 'w').write('\n'.join(out) + '\n')
    done += 1
print('wrote', done, 'content files to', os.path.relpath(OUT, ROOT))
