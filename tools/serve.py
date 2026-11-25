#!/usr/bin/env python3
"""Local preview that behaves like Cloudflare Pages: /prompts/x serves prompts/x.html,
_redirects rules apply, and unknown paths get 404.html.   python3 tools/serve.py [port]"""
import http.server, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8768
REDIRECTS = {}
for line in open(os.path.join(ROOT, '_redirects')):
    parts = line.split()
    if len(parts) >= 2 and not line.startswith('#'):
        REDIRECTS[parts[0]] = (parts[1], int(parts[2]) if len(parts) > 2 else 302)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def send_head(self):
        path = self.path.split('?')[0].split('#')[0]
        rule = REDIRECTS.get(path) or next((v for k, v in REDIRECTS.items() if k.endswith('*') and path.startswith(k[:-1])), None)
        if rule:
            to, code = rule
            self.send_response(code); self.send_header('Location', to); self.end_headers(); return None
        local = os.path.join(ROOT, path.lstrip('/'))
        if path != '/' and not os.path.exists(local) and os.path.exists(local + '.html'):
            self.path = path + '.html'
        elif path != '/' and not os.path.exists(local):
            self.send_response(404)
            body = open(os.path.join(ROOT, '404.html'), 'rb').read()
            self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(body)))
            self.end_headers(); self.wfile.write(body); return None
        return super().send_head()

    def log_message(self, *a):
        pass


print(f'Preview: http://localhost:{PORT}')
http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
