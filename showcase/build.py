#!/usr/bin/env python3
"""HumanLup Design Lab showcase. python3 build.py
Writes index.html (images beside it in shots/, links to ../NNN-slug/index.html)
and project.html (small images inside the file, no links) from template.html.
Add a piece: put a 1440x900 screenshot in shots/NNN-slug.jpg and add a row to PIECES."""
import json, base64, io, os
from PIL import Image
PIECES = [  # folder, title, ground, ink, title color, caption
 ("002-terracotta","Terracotta","#efe6da","#1a1a1a","#b9531f","138 colors, fired as little test tiles."),
 ("003-tidal","Tidal","#ffffff","#111111","#0f5c55","A design language for buildings at the water's edge. The tide keeps moving."),
 ("004-terrain","Terrain","#f3efe6","#1b1d2a","#c2410c","The ground is made up. The sun is not. Drag it and the shadows move."),
 ("005-cinema","Cinema","#0b0b0e","#f4f4f2","#f08a4b","Short films cut from a few lines of text. Press play."),
 ("006-taste-report","Taste","#f4f4f1","#111111","#c4122f","An essay on taste with a slider under it. Drag left and it edits itself down."),
 ("007-ink-almanac","Prints","#F5F0E8","#1A1A1A","#b4541a","Every color gets a fingerprint. Type yours in."),
 ("008-reflecction","Reflecction","#0d1016","#e9edf2","#9ad1ff","A day of prompts on the left, what it says about me on the right."),
 ("009-layout-mode","Press L","#eeece7","#17181a","#2f6fe4","Press L and the page becomes the canvas."),
 ("010-glass","Glass","#101012","#f4f4f2","#e8c468","I wanted glass that acts like glass. Drag a piece over the type."),
 ("011-l-editorial","Rare Form","#f2efe9","#151515","#151515","One magazine issue, set four ways with nothing but type."),
 ("012-tool-library","Tool Library","#f3f0e8","#111111","#111111","A neighborhood tool library. The date is the biggest thing on the page."),
 ("013-swipe-file","Swipe File","#b4a54a","#0d0d0d","#0d0d0d","I counted every pixel on five sites I like."),
 ("014-only-copy","Only Copy","#efece4","#14110f","#cf3a12","Which repos exist only on this laptop? Red is the only copy."),
 ("015-layer-issue","No Script","#f1eee6","#15140f","#2a3fd6","An issue about CSS with no JavaScript on the page. Scroll and the headline turns into code."),
 ("016-wiki-of-the-wiki","Field Notes","#f1efea","#111111","#2238f5","My notes on the LLM wiki idea, as 71 pages on a ring."),
 ("017-set-board","Set Board","#efede8","#1a1a1a","#1a1a1a","A week of route setting for a climbing gym, on one board."),
 ("018-one-line-a-run","One Line","#ffffff","#111a2e","#1b2a6b","How I work, drawn one line each time a job runs."),
 ("019-seven-grays","Seven Grays","#050509","#F9FAFB","#FD7308","Seven grays, one black and a dither made with only CSS."),
 ("020-your-line-first","Your Line","#ffffff","#111111","#111111","Draw one line and the headline moves out of its way."),
 ("021-lets-talk","Let’s Talk","#111211","#f2f2ee","#86e39a","A contact page with no form. Change three sentences and it writes the email."),
 ("023-call-sheet","Call Sheet","#e5e1d8","#17181a","#17181a","A call sheet for a prompt. Fill five lines."),
 ("024-you-need-both","Grow","#ffffff","#151515","#2f6bff","Love how the flowers turned out. Thought it was a good idea for a creative studio."),
 ("025-eight-at-a-time","Eight","#f6f2ea","#1a1a1a","#2552d0","A style guide where every box sits on an 8 px line."),
 ("026-any-color","Any Color","#F8F8F8","#0A0A0A","#E04F26","Every dot is a different color at the same lightness. Type on it."),
 ("027-one-card","One Card","#f1efea","#151515","#b3541c","One social card that holds at any shape. Drag the corner."),
 ("028-take-the-l","Take the L","#e8e7e2","#0d0d0d","#c2185f","Two Ls make a W. Tap anywhere."),
 ("029-oclock","O’clock","#efeadd","#1b2fc4","#1b2fc4","A clock you count. Bumps are the hour, the dot is the minute."),
 ("030-nosy","Nosy","#edeae3","#191714","#c2410c","A page full of little guys that watch your cursor. Sit still and they drift off."),
 ("031-fold","Fold","#dfe3e0","#111512","#0d6e4b","A sheet of paper. Drag it and it folds, and it keeps the creases."),
]
def lum(h):
    h=h.lstrip('#'); r,g,b=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    f=lambda c: c/12.92 if c<=.03928 else ((c+.055)/1.055)**2.4
    return .2126*f(r)+.7152*f(g)+.0722*f(b)
def cr(a,b):
    x,y=sorted([lum(a),lum(b)],reverse=True); return (x+.05)/(y+.05)
def small(path,w,q):
    im=Image.open(path).convert('RGB'); im=im.resize((w,round(w*im.height/im.width)),Image.LANCZOS)
    b=io.BytesIO(); im.save(b,'WEBP',quality=q,method=6); return 'data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()
here=os.path.dirname(os.path.abspath(__file__)); tpl=open(os.path.join(here,'template.html'),encoding='utf-8').read()
dev,proj=[],[]
for slug,title,g,i,a,cap in PIECES:
    assert cr(g,i)>=7,(slug,'ink',cr(g,i)); assert cr(g,a)>=3,(slug,'title',round(cr(g,a),2))
    nn=slug[1:3]; shot=os.path.join(here,'shots',slug+'.jpg'); assert os.path.exists(shot),shot
    base=dict(nn=nn,title=title,g=g,i=i,a=a,cap=cap)
    dev.append(dict(base,img='shots/'+slug+'.jpg',href='../'+slug+'/index.html'))
    proj.append(dict(base,img=small(shot,720,58)))
def emit(name,data,links):
    out=tpl.replace('/*DATA*/',json.dumps(data,ensure_ascii=False,separators=(',',':'))).replace('/*LINKS*/','true' if links else 'false')
    open(os.path.join(here,name),'w',encoding='utf-8').write(out); print(name,len(out))
emit('index.html',dev,True); emit('project.html',proj,False)
