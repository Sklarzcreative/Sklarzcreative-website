#!/usr/bin/env python3
"""
audit.py — check every page against the rules this site actually depends on.

Python 3 standard library only. No install, no build step, consistent with the
rest of the repository.

    python3 tools/audit.py

What it checks
--------------
The six load-bearing rules in the root README are the ones that break something
visible. Two of them can be checked by reading the markup, and this does:

  rule 1  every page opens with a dark section (.hero / .page-hero), because the
          header is fixed and transparent at scroll-top and a light first
          section drops the nav below AA contrast
  rule 3  .page-hero never carries .is-dark, which would erase the gradient

Plus the things that rot quietly as pages are added: broken internal links,
missing alt text, absent or non-apex canonicals, missing titles and
descriptions, h1 count, the site-wide privacy link, and two-way sitemap
agreement (every listed URL exists, every page is listed).

Rules 4 and 5 — hidden animation start-states scoped to html.js, and
prefers-reduced-motion resolving reveals to their final state — cannot be
checked from markup. They need a browser. See tools/browser-audit.js.

What it deliberately ignores
----------------------------
Redirect stubs and templates are not content pages, and applying content rules
to them produces confident nonsense: a redirect stub does not want an h1 or a
meta description. Stubs are identified by behaviour — a meta-refresh or
location.replace together with robots noindex — not by file size, so a stub
that grows still gets recognised. /docs/ is treated as templates and notes.

The first run of this script reported twenty findings. Every one of them was on
a stub or a template, and every one was wrong. That is why the exclusion exists,
and why a finding should be read before it is fixed.
"""
import re, os, sys
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = '/home/user/Sklarzcreative-website'
SKIP_DIRS = {'.git', '_original-design', 'node_modules', 'editorial'}

pages = []
for dp, dns, fns in os.walk(ROOT):
    dns[:] = [d for d in dns if d not in SKIP_DIRS]
    for fn in fns:
        if fn.endswith('.html'):
            pages.append(os.path.join(dp, fn))
pages.sort()

def is_redirect_stub(h):
    """A deliberate noindex redirect: not a content page, so content rules do
    not apply to it. Judged by behaviour, not by size."""
    return ('http-equiv="refresh"' in h or 'location.replace' in h) and \
           re.search(r'<meta[^>]+name="robots"[^>]+noindex', h) is not None

def is_template(path):
    return '/docs/' in path.replace(os.sep, '/')

content_pages, stubs, templates = [], [], []
for p in pages:
    h = open(p, encoding='utf-8').read()
    if is_template(p):
        templates.append(p)
    elif is_redirect_stub(h):
        stubs.append(p)
    else:
        content_pages.append(p)

findings = []
def add(sev, page, msg):
    findings.append((sev, os.path.relpath(page, ROOT), msg))

def first_section_class(h):
    m = re.search(r'<main\b[^>]*>(.*?)</main>', h, re.S)
    scope = m.group(1) if m else h
    m2 = re.search(r'<section\b([^>]*)>', scope)
    return m2.group(1) if m2 else ''

for p in content_pages:
    h = open(p, encoding='utf-8').read()
    rel = os.path.relpath(p, ROOT)

    # --- repo rule 1: every page opens with a dark section
    fs = first_section_class(h)
    if not re.search(r'class="[^"]*\b(hero|page-hero)\b', fs):
        add('HIGH', p, f'first <section> is not .hero/.page-hero — nav contrast rule 1. got: {fs.strip()[:70]}')

    # --- repo rule 3: .page-hero must not carry .is-dark
    for m in re.finditer(r'<section\b[^>]*class="([^"]*)"', h):
        cls = m.group(1)
        if 'page-hero' in cls and 'is-dark' in cls:
            add('HIGH', p, 'rule 3: .page-hero carries .is-dark — erases the hero gradient')

    # --- lang
    if not re.search(r'<html[^>]*\blang=', h):
        add('MED', p, 'no lang attribute on <html>')

    # --- title / description / canonical / og
    if not re.search(r'<title>.*?</title>', h, re.S):
        add('HIGH', p, 'no <title>')
    if not re.search(r'<meta[^>]+name="description"', h):
        add('MED', p, 'no meta description')
    can = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', h)
    if not can:
        add('MED', p, 'no canonical link')
    elif not can.group(1).startswith('https://sklarzcreative.com'):
        add('HIGH', p, f'canonical is not the apex: {can.group(1)}')
    ogi = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', h)
    if not ogi:
        add('LOW', p, 'no og:image')

    # --- h1 count
    h1s = re.findall(r'<h1\b', h)
    if len(h1s) == 0:
        add('MED', p, 'no <h1>')
    elif len(h1s) > 1:
        add('LOW', p, f'{len(h1s)} <h1> elements')

    # --- images: alt present
    for m in re.finditer(r'<img\b([^>]*)>', h):
        attrs = m.group(1)
        if 'alt=' not in attrs:
            src = re.search(r'src="([^"]+)"', attrs)
            add('MED', p, f'img without alt: {src.group(1) if src else attrs[:50]}')

    # --- privacy footer link (claimed on every page)
    if '/privacy/' not in h:
        add('MED', p, 'no link to /privacy/ (footer privacy link claimed site-wide)')

    # --- internal links resolve
    for m in re.finditer(r'href="([^"#?][^"]*)"', h):
        href = m.group(1)
        if re.match(r'^(https?:|mailto:|tel:|//)', href):
            continue
        target = href.split('#')[0].split('?')[0]
        if not target:
            continue
        base = ROOT if target.startswith('/') else os.path.dirname(p)
        fp = os.path.normpath(os.path.join(base, target.lstrip('/')))
        ok = os.path.exists(fp) or os.path.exists(os.path.join(fp, 'index.html'))
        if not ok:
            add('HIGH', p, f'broken internal link: {href}')

# --- sitemap coverage
sm = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
urls = re.findall(r'<loc>([^<]+)</loc>', sm)
for u in urls:
    path = urlparse(u).path.lstrip('/')
    fp = os.path.join(ROOT, path)
    if not (os.path.exists(fp) or os.path.exists(os.path.join(fp, 'index.html'))):
        add('HIGH', os.path.join(ROOT, 'sitemap.xml'), f'sitemap lists a path that does not exist: {u}')

sitemap_paths = {urlparse(u).path.rstrip('/') or '/' for u in urls}
for p in content_pages:
    rel = os.path.relpath(p, ROOT)
    if rel in ('404.html',):
        continue
    web = '/' + rel.replace('index.html', '')
    web = web.rstrip('/') or '/'
    if web not in sitemap_paths:
        add('MED', p, f'page not in sitemap.xml (would be {web}/)')

sev_order = {'HIGH': 0, 'MED': 1, 'LOW': 2}
findings.sort(key=lambda f: (sev_order[f[0]], f[1]))
cur = None
for sev, page, msg in findings:
    if sev != cur:
        print(f'\n===== {sev} =====')
        cur = sev
    print(f'  {page}: {msg}')
print(f'\n{len(content_pages)} content pages audited '
      f'({len(stubs)} redirect stubs and {len(templates)} templates excluded), '
      f'{len(findings)} findings '
      f'({sum(1 for f in findings if f[0]=="HIGH")} high, '
      f'{sum(1 for f in findings if f[0]=="MED")} med, '
      f'{sum(1 for f in findings if f[0]=="LOW")} low)')
