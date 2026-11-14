#!/usr/bin/env python3
"""Stamp every Design Lab page with Anthony Lupo / HumanLup meta.
Safe to run again: it replaces its own block (between the humanlup:meta marks) and touches nothing else.
  python3 _tools/meta.py                 # relative share images
  python3 _tools/meta.py https://lab.humanlup.com   # absolute share image + canonical URLs, once the pages have a home
Skips 022 (not public yet) and any *.v1.html."""
import re, sys, glob, os, html
BASE = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else ''
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'022-halfway'}
FALLBACK = {
 '001-wise-guys': 'Left Right Center for the Wise Guys. Three dollars a player, last one holding wins.',
 '002-terracotta': 'A color library shelved like glaze test tiles. 138 colors, sorted by pigment.',
 '003-tidal': 'A design language for buildings at the water’s edge, on a tide line that keeps moving.',
 '005-cinema': 'Short films drawn in the browser. Press play.',
}
A, Z = '<!-- humanlup:meta -->', '<!-- /humanlup:meta -->'
def block(folder, page, title, desc):
    nn = folder[:3]
    lab = 'HumanLup Design Lab' + ('' if folder == 'showcase' else ' ' + str(int(nn)).zfill(2))
    img = 'preview.jpg'
    url = ''
    if BASE:
        img = f'{BASE}/{folder}/preview.jpg'
        url = f'{BASE}/{folder}/' + ('' if page == 'index.html' else page)
    e = lambda s: html.escape(s, quote=True)
    L = [A,
     f'<!-- {lab} · Anthony Lupo · humanlup.com · X @humanlup · IG humanlup.ai · anthony@humanlup.com -->',
     '<meta name="author" content="Anthony Lupo">',
     '<meta name="creator" content="Anthony Lupo">',
     '<meta name="publisher" content="HumanLup">',
     '<meta name="copyright" content="© 2026 Anthony Lupo, HumanLup">',
     '<link rel="author" href="https://humanlup.com">',
     '<link rel="me" href="https://x.com/humanlup">',
     '<link rel="me" href="https://www.instagram.com/humanlup.ai">',
     '<meta property="og:type" content="website">',
     f'<meta property="og:site_name" content="{e(lab)}">',
     f'<meta property="og:title" content="{e(title)}">',
     f'<meta property="og:description" content="{e(desc)}">',
     f'<meta property="og:image" content="{e(img)}">',
     '<meta name="twitter:card" content="summary_large_image">',
     '<meta name="twitter:site" content="@humanlup">',
     '<meta name="twitter:creator" content="@humanlup">',
     f'<meta name="twitter:title" content="{e(title)}">',
     f'<meta name="twitter:description" content="{e(desc)}">',
     f'<meta name="twitter:image" content="{e(img)}">']
    if url: L += [f'<link rel="canonical" href="{e(url)}">', f'<meta property="og:url" content="{e(url)}">']
    L.append(Z)
    return '\n'.join(L)
n = 0
files = sorted(glob.glob(os.path.join(ROOT, '[0-9][0-9][0-9]-*', '*.html'))) + [os.path.join(ROOT, 'showcase', 'index.html'), os.path.join(ROOT, 'showcase', 'template.html')]
for f in files:
    folder, page = os.path.basename(os.path.dirname(f)), os.path.basename(f)
    if folder in SKIP or '.v1.' in page: continue
    s0 = open(f, encoding='utf-8').read()
    s = re.sub(r'\n?' + re.escape(A) + r'.*?' + re.escape(Z), '', s0, count=1, flags=re.S)  # work from the page without our block
    head_end = s.find('</head>')
    head = s[:head_end if head_end > 0 else 4000]
    mt = re.search(r'<title>(.*?)</title>', head, re.S)
    if not mt: print('no title, skipped', f); continue
    title = html.unescape(mt.group(1).strip())
    md = re.search(r'<meta name="description" content="(.*?)"\s*/?>', head, re.S)
    desc = html.unescape(md.group(1)) if md else FALLBACK.get(folder, 'A piece from the HumanLup Design Lab.')
    b = block(folder, page, title, desc)
    if not md: b = b.replace(A, A + '\n<meta name="description" content="' + html.escape(desc, quote=True) + '">', 1)
    i = mt.end()
    new = s[:i] + '\n' + b + s[i:]
    if new != s0:
        open(f, 'w', encoding='utf-8').write(new); n += 1
        print('stamped', folder + '/' + page)
print(n, 'files changed')
