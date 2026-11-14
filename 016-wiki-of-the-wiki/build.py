#!/usr/bin/env python3
"""Build Field Notes on the LLM Wiki (Design Lab 16) from the April notes page.

Reads  lab-editorial-redesign/llm-wiki-of-the-wiki.html  (never writes to it),
splits it into pages, links the pages by rule, lints the result, and writes
index.html from template.html.

  python3 build.py SOURCE.html template.html index.html

The split (which block becomes which page, its short name, the words that
count as a mention of it) is done by hand in the tables below. Everything
after that is computed: links, backlinks, orphans, repeats, the lint list.
"""
import sys, re, json, html
from bs4 import BeautifulSoup, NavigableString

SRC, TPL, OUT = sys.argv[1:4]
soup = BeautifulSoup(open(SRC, encoding="utf-8").read(), "html.parser")

# ---------- text helpers ----------
DASH = [
    (r"maintains</em> — and let", "maintains</em>, and let"),
    (r"near zero — so", "near zero, so"),
    (r"you curate — the only", "you curate, the only"),
    (r"workflows — what makes", "workflows: what makes"),
    (r"cited — and good", "cited, and good"),
    (r"smarter retrieval — it was", "smarter retrieval. It was"),
    (r"ingested source — checked", "ingested source, checked"),
    (r"in weights — orthogonal", "in weights, orthogonal"),
    (r"human action — a button press — not", "human action (a button press), not"),
    (r"v0\.5\.0 — Tencent", "v0.5.0, Tencent"),
    (r"trajectories — including tool calls — for", "trajectories (including tool calls) for"),
    (r"encryption — the relay", "encryption: the relay"),
    (r"lifecycle — ingest", "lifecycle: ingest"),
    (r"API calls — the CLI", "API calls: the CLI"),
    (r"looks like — the bar", "looks like, the bar"),
    (r"podcast notes — filed", "podcast notes, filed"),
    (r"for everything — the model", "for everything: the model"),
    (r"dispute resolution — and an", "dispute resolution, and an"),
    (r"rebuilt — inverted", "rebuilt: inverted"),
    (r"the thinking — it's", "the thinking, it's"),
    (r"die in chat — that's", "die in chat. That's"),
    (r"collaboration — free", "collaboration, free"),
    (r"Channel → topic → fact tree", "Channel to topic to fact tree"),
    (r"Team Chat → Wiki", "Team Chat to Wiki"),
    (r"Web pages → markdown", "Web pages to markdown"),
    (r"Wiki content → presentation", "Wiki content to presentation"),
]

def clean(s):
    s = re.sub(r"\s+", " ", s).strip()
    for a, b in DASH:
        s = re.sub(a, b, s)
    assert "—" not in s and "→" not in s, s
    return s

def inner(el):
    """Inner HTML keeping only <code> and <em>."""
    out = []
    for c in el.children:
        if isinstance(c, NavigableString):
            out.append(html.escape(str(c), quote=False))
        elif c.name in ("code", "em"):
            out.append(f"<{c.name}>{inner(c)}</{c.name}>")
        elif c.name == "a" and "wikilink" in (c.get("class") or []):
            out.append(f'<a class="wl red" href="#{c.get_text()}">{html.escape(c.get_text())}</a>'
                       if c.get_text() == "sources/foo" else inner(c))
        elif c.name in ("strong", "b", "span"):
            if "dropcap" in (c.get("class") or []):
                out.append(inner(c))
            elif c.name == "span":
                out.append(inner(c))
            # <strong>/<b> lead-ins are taken as titles elsewhere
        else:
            out.append(inner(c))
    return "".join(out)

def txt(el):
    return clean(el.get_text(" "))

def plain(h):
    return html.unescape(re.sub(r"<[^>]+>", "", h))

P = []
def page(slug, label, kind, title, body="", al=(), cs=(), **kw):
    d = dict(id=slug, label=label, kind=kind, title=title, html=clean(body) if body else "",
             al=list(al), cs=list(cs))
    d.update(kw)
    P.append(d)
    return d

sel = soup.select

# ---------- Start ----------
lede = sel(".lede-left p")
page("the-pitch", "The pitch", "Start", "The pitch",
     "<p>" + inner(lede[0]) + "</p><p>" + inner(lede[1]) + "</p>",
     see=["why-it-matters", "the-pattern", "step-1"])
why = sel(".lede-right p")[0]
why.find("b").extract()
page("why-it-matters", "Why it matters", "Start", "Why it matters",
     "<p>" + inner(why) + "</p>", al=["bookkeeping", "maintenance"])
page("the-pattern", "The pattern", "Start", "The pattern",
     "<p>" + inner(sel("p.lead")[0]) + "</p>",
     al=["three-layer", "three layers", "same architecture"],
     see=["raw-sources", "the-wiki", "the-schema", "ingest", "query", "lint"],
     count=12, chip="three-layer architecture")
cells = sel(".pattern-cell")
meta = [("raw-sources", "Raw sources", ["raw sources", "raw/", "raw collection", "raw"]),
        ("the-wiki", "The wiki", ["wiki/", "middle layer", "compounding artifact", "compounds", "compound", "compounding"]),
        ("the-schema", "The schema", ["schema", "CLAUDE.md", "AGENTS.md"])]
for c, (slug, label, al) in zip(cells, meta):
    page(slug, label, "Start", txt(c.h3), "<p>" + inner(c.p) + "</p>", al=al,
         credit=txt(c.select_one(".num")) + " · " + txt(c.select_one(".role")))
steps = sel(".loop-step")
meta = [("ingest", ["ingest", "ingested"], {}),
        ("query", ["query", "queries"], {}),
        ("lint", ["lint", "lints", "health check"], dict(count=4, chip="lint as first-class op"))]
for c, (slug, al, kw) in zip(steps, meta):
    page(slug, txt(c.select_one(".verb")), "Start", txt(c.select_one(".verb")),
         "<p>" + inner(c.p) + "</p>", al=al, credit=txt(c.h4), **kw)

# ---------- Ideas ----------
meta = [
 ("quality-gate", "Quality gate", ["quality gate", "filtering noise", "semantic filter", "in scope"], 6, "quality gate before storage"),
 ("citation-grounding", "Citation grounding", ["citation grounding", "citation rule", "citations", "citation", "cited", "cite", "provenance", "span anchors", "write-time"], 9, "citation & provenance"),
 ("weight-distillation", "Weight distillation", ["weight-level", "fine-tuned", "fine-tuning", "weights"], 2, "weight-level distillation"),
 ("conversation-as-unit", "Conversation as unit", ["conversation as", "conversation is primary", "conversations", "dialogue"], 3, "conversation-as-source"),
 ("background-daemon", "Background daemon", ["daemon", "daemons"], 4, "background daemon"),
 ("editorial-policy", "Editorial policy", ["editorial policy", "editorial YAML", "purpose.md", "editorial"], 2, "domain editorial policy"),
 ("recall-and-sleep", "Recall and sleep", ["sleep consolidation", "active recall"], 1, "sleep consolidation"),
 ("inverted-index", "Inverted index", ["inverted token index", "inverted indexes", "inverted index", "index.md"], None, None),
]
for c, (slug, label, al, n, chip) in zip(sel(".idea"), meta):
    pull = c.select_one(".pull")
    kw = dict(credit=txt(c.select_one(".idea-attr")))
    if pull: kw["pull"] = clean(inner(pull))
    if n: kw.update(count=n, chip=chip)
    page(slug, label, "Ideas", txt(c.select_one(".idea-title")), "<p>" + inner(c.p) + "</p>", al=al, **kw)

# ---------- Themes with no other page: a name and a count, nothing else ----------
chips = {}
for c in sel(".theme-chip"):
    n = int(c.select_one(".count").get_text().strip("×"))
    c.select_one(".count").extract()
    chips[txt(c)] = n
stubs = [
 ("mcp-server", "MCP server", "mcp server integration", ["MCP"]),
 ("knowledge-graph", "Knowledge graph", "knowledge graph layer", ["typed knowledge graph", "knowledge graphs", "knowledge graph", "typed graph", "graph"]),
 ("hybrid-search", "Hybrid search", "hybrid bm25 + vector", ["BM25", "hybrid", "vector"]),
 ("multi-agent", "Multi-agent consensus", "multi-agent consensus", ["multi-agent", "consensus voting", "Devil's Advocate"]),
 ("privacy", "Privacy and E2E", "privacy & e2e encryption", ["privacy", "E2E", "end-to-end encryption", "on-device"]),
]
for slug, label, chip, al in stubs:
    page(slug, label, "Themes", chip[0].upper() + chip[1:].replace("bm25", "BM25").replace("e2e", "E2E").replace("mcp", "MCP") if not chip.startswith("mcp") else "MCP server integration",
         "", al=al, count=chips[chip], chip=chip, stub=True)

# ---------- Projects ----------
names = [("beever-atlas", "Beever Atlas", ["Beever Atlas"]), ("weknora", "WeKnora", ["WeKnora"]),
         ("synthadoc", "Synthadoc", ["Synthadoc"]), ("theknowledge", "TheKnowledge", ["TheKnowledge"]),
         ("origin", "Origin", ["Origin"]), ("link", "Link", ["Link"]), ("opencrab", "OpenCrab", ["OpenCrab"]),
         ("dpc-messenger", "DPC Messenger", ["DPC Messenger", "DPC"]), ("omegawiki", "ΩmegaWiki", ["ΩmegaWiki"]),
         ("repositories-wiki", "Repositories Wiki", ["Repositories Wiki"]),
         ("llmwiki-cli", "llmwiki-cli", ["llmwiki-cli"]),
         ("obsidian-llm-wiki-local", "Obsidian LLM Wiki Local", ["Obsidian LLM Wiki Local"])]
for c, (slug, label, cs) in zip(sel(".impl"), names):
    page(slug, label, "Projects", clean(txt(c.h4)), "<p>" + inner(c.p) + "</p>", cs=cs,
         credit=txt(c.select_one(".impl-attr")),
         tags=[txt(t) for t in c.select(".tag")],
         url=c.select_one("a.impl-link")["href"], num=txt(c.select_one(".impl-num")))

# ---------- Tools ----------
meta = [("obsidian", "Obsidian", [], ["Obsidian"], dict(count=8, chip="obsidian as ide")),
        ("qmd", "qmd", [], ["qmd"], {}),
        ("web-clipper", "Web Clipper", ["Obsidian Web Clipper", "web clipper"], [], {}),
        ("marp", "Marp", [], ["Marp"], {}),
        ("dataview", "Dataview", ["dataview"], [], {}),
        ("tolkien-gateway", "Tolkien Gateway", ["Tolkien Gateway"], [], {}),
        ("text-is-the-new-binary", "Text is the new binary", [], [], {}),
        ("rag-wiki-or-gbrain", "RAG, wiki or GBrain", [], ["RAG"], {}),
        ("memex", "Memex", [], ["Memex", "Bush"], {})]
for c, (slug, label, al, cs, kw) in zip(sel("a.resource"), meta):
    page(slug, label, "Tools", txt(c.h5), "<p>" + inner(c.select_one(".resource-desc")) + "</p>",
         al=al, cs=cs, credit=txt(c.select_one(".resource-cat")), url=c["href"], **kw)

# ---------- Uses ----------
meta = [("personal", "Personal", []), ("research", "Research", ["research lifecycle", "research wiki"]),
        ("reading-a-book", "Reading a book", []), ("team-memory", "Team memory", ["Slack", "team chat", "team"]),
        ("codebase", "Codebase", ["source code", "code wiki", "your code"]),
        ("trips-courses-hobbies", "Trips, courses, hobbies", [])]
for c, (slug, label, al) in zip(sel(".use-case"), meta):
    page(slug, label, "Uses", txt(c.h4), "<p>" + inner(c.p) + "</p>", al=al,
         credit=txt(c.select_one(".domain")))

# ---------- Tensions ----------
meta = [("is-it-a-wiki", "Is it a wiki?", []),
        ("self-corruption", "Self-corruption", ["silent corruption", "corruption risk", "corruption", "hallucination", "confabulated"]),
        ("scale-wall", "Scale wall", ["scale wall", "breaks large"]),
        ("permissions", "Permissions", ["permissions", "access control", "NDA"])]
for c, (slug, label, al) in zip(sel(".tension"), meta):
    ps = c.select("p")
    page(slug, label, "Tensions", txt(c.h4), "<p>" + inner(ps[0]) + "</p>", al=al,
         note=clean(inner(ps[1])), credit=txt(c.select_one(".tension-label")))

# ---------- Quotes ----------
qmeta = [("q-ide", "“Obsidian is the IDE”"), ("q-bookkeeping", "“The bookkeeping”"),
         ("q-noise", "“Noise at the door”"), ("q-conversation", "“Conversation is primary”"),
         ("q-silent-corruption", "“Silent corruption”"), ("q-memex", "“Bush's vision”"),
         ("q-contract", "“The contract”")]
for c, (slug, label) in zip(sel(".quote"), qmeta):
    page(slug, label, "Quotes", "", "<p>" + inner(c.select_one(".quote-text")) + "</p>",
         credit=txt(c.select_one(".quote-attr")), quote=True)
ps = soup.select_one(".pull-spread")
page("q-artifact", "“Compounding artifact”", "Quotes", "", "<p>" + inner(ps.select_one(".pull-text")) + "</p>",
     credit=txt(ps.select_one(".pull-attr")), quote=True)

# ---------- Playbook ----------
smeta = [("Pick a domain", []), ("Set up the folders", ["three directories"]), ("Write the schema first", []),
         ("Drop a source in", []), ("Watch links form", []), ("Add a quality gate", []),
         ("Add a citation rule", []), ("File answers back", ["filed back"]), ("Run the first lint", []),
         ("Make it a git repo", ["git backend", "version history", "versioning", "git repo"])]
for i, (li, (label, al)) in enumerate(zip(sel(".playbook li"), smeta), 1):
    t = txt(li.strong); li.strong.extract()
    page(f"step-{i}", f"{i} {label}", "Playbook", t, "<p>" + inner(li) + "</p>", al=al,
         credit=f"Step {i} of 10", see=[f"step-{i+1}"] if i < 10 else [], num=i)

ids = [p["id"] for p in P]
assert len(ids) == len(set(ids))
byid = {p["id"]: p for p in P}

# ---------- link by rule ----------
# A page links to another when its text holds one of the other's names.
# Longest name first, first mention only, never inside an existing link.
ALIAS = []
for p in P:
    for a in p["al"]: ALIAS.append((a, p["id"], False))
    for a in p["cs"]: ALIAS.append((a, p["id"], True))
ALIAS.sort(key=lambda x: -len(x[0]))

def link_html(src, h, done):
    for alias, tid, cs in ALIAS:
        if tid == src or tid in done: continue
        pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])", 0 if cs else re.I)
        toks = re.split(r"(<[^>]+>)", h)
        depth = 0
        for i, t in enumerate(toks):
            if t.startswith("<a"): depth += 1; continue
            if t.startswith("</a"): depth -= 1; continue
            if t.startswith("<") or depth: continue
            m = pat.search(html.unescape(t))
            if not m: continue
            m = pat.search(t)
            if not m: continue
            toks[i] = t[:m.start()] + f'<a class="wl" href="#{tid}">' + m.group(0) + "</a>" + t[m.end():]
            done.add(tid)
            break
        h = "".join(toks)
    return h

LINKS = set()
for p in P:
    done = set()
    for f in ("html", "pull", "note"):
        if p.get(f): p[f] = link_html(p["id"], p[f], done)
    if p.get("credit"):
        p["creditHtml"] = link_html(p["id"], html.escape(p["credit"], quote=False), done)
    for t in done: LINKS.add((p["id"], t))
    for t in p.get("see", []): LINKS.add((p["id"], t))

# same sentence on two pages: link the page to the quote
norm = lambda s: re.sub(r"[^a-z0-9 ]", "", plain(s).lower()).strip()
REPEATS = []
for q in P:
    if not q.get("quote"): continue
    qt = norm(q["html"])
    for p in P:
        if p is q: continue
        body = norm(p.get("html", "") + " " + p.get("pull", ""))
        if qt in body or any(len(s) > 40 and norm(s) in body for s in re.split(r"(?<=[.])\s", plain(q["html"]))):
            LINKS.add((p["id"], q["id"]))
            p.setdefault("see", []).append(q["id"])
            REPEATS.append((p["id"], q["id"]))

LINKS.add(("citation-grounding", "sources/foo"))
MISSING = dict(id="sources/foo", label="sources/foo", kind="Ideas", missing=True, title="sources/foo")

out = {i: sorted(t for s, t in LINKS if s == i) for i in ids}
inn = {i: sorted(s for s, t in LINKS if t == i) for i in ids}

# ---------- lint ----------
L = []
def finding(key, n, name, text, pages=(), ok=False):
    L.append(dict(key=key, n=n, name=name, text=text, pages=list(pages), ok=ok))

# contradiction: the same quoted line under two different credits
contra = []
for a, b in REPEATS:
    ca, cb = byid[a].get("credit", ""), byid[b].get("credit", "")
    if ca and cb and ca.split(" · ")[0].lstrip("@") != cb.split(" · ")[0].lstrip("@"):
        contra.append((a, b, ca, cb))
for a, b, ca, cb in contra:
    finding("contradiction", len(contra), "contradiction" if len(contra) == 1 else "contradictions",
            f"“{plain(byid[b]['html'])}” is credited to {ca.split(' · ')[0]} on one page and to {cb.split(' · ')[0]} on another.",
            [a, b])
finding("missing", 1, "link to a page that is not there",
        "One link points at sources/foo. No page has that name. It is the example in the paragraph about made-up citations.",
        ["citation-grounding"])
orph = [i for i in ids if not inn[i]]
finding("orphans", len(orph), "pages nothing links to", "No other page mentions these by name.", orph)
st = [p["id"] for p in P if p.get("stub")]
finding("stubs", len(st), "pages with no text", "A name and a count. Nothing explains them yet.", st)
qs = [p["id"] for p in P if p.get("quote")]
finding("uncited", len(qs), "quotes with no link to where they were said",
        "The idea asks for every claim to point at an exact spot in a source. These quotes carry a name and nothing else. I did not check them against the thread either.", qs)
stale_re = re.compile(r"v\d+\.\d+(\.\d+)?|\d+\+ ⭐|official MCP registry|Qwen3")
stale = [p["id"] for p in P if stale_re.search(plain(p.get("html", "")) + " " + p.get("title", "") + " " + p.get("credit", ""))]
finding("stale", len(stale), "pages with claims that go out of date",
        "Version numbers, star counts, model names and a registry listing, all as of April 2026. Not rechecked.", stale)
counted = [p["id"] for p in P if p.get("count")]
nchips = len(chips)
finding("counts", nchips + 2, "counts with no source",
        f"{nchips} theme counts (×12, ×9 and so on), “26+ threads mined” and “660+ comments”. Nothing says what was counted. The last two do not agree on the size of the thread.", counted)
big = [p["id"] for p in P if "biggest unlock" in plain(p.get("html", "")).lower()]
finding("repeats", len(big), "pages that call the quality gate the biggest unlock",
        f"The same point in the same words, on {len(big)} pages. {len(REPEATS)} quotes are also printed twice.", big + [b for a, b in REPEATS])
cands = ["NotebookLM", "Neo4j", "Weaviate", "Claude Code", "Cursor", "Codex", "Kiro", "FAISS", "GitHub Pages",
         "YAML", "Chrome extension", "frontmatter", "Karpathy", "markdown"]
nopage = []
for c in cands:
    hit = [p["id"] for p in P if re.search(r"(?<![A-Za-z])" + re.escape(c), plain(p.get("html", "") + " " + p.get("note", "") + " " + p.get("credit", "")))]
    if len(hit) >= 2: nopage.append((c, hit))
finding("nopage", len(nopage), "names used on two or more pages that have no page",
        ", ".join(f"{c} ({len(h)})" for c, h in nopage) + ". Checked against a list of " + str(len(cands)) + " names I picked.",
        sorted({i for c, h in nopage for i in h}, key=ids.index))
merged = [p["id"] for p in P if p.get("chip") and not p.get("stub")]
finding("merged", len(merged), "themes that were another page under a second name",
        "Folded into the page they describe.", merged)
nproj = sum(1 for p in P if p["kind"] == "Projects")
passes = []
if nproj == 12 and "12" in txt(soup.select_one(".masthead-meta")): passes.append("12 projects listed, and the header says 12")
if len(sel(".playbook li")) == 10: passes.append("10 steps, and the heading says ten")
if all(p.get("url") for p in P if p["kind"] == "Projects"): passes.append("every project has a repo link")
finding("passes", len(passes), "checks passed", ". ".join(s[0].upper() + s[1:] for s in passes) + ".", ok=True)

# ---------- about (not on the ring, not counted) ----------
col = sel(".colophon-left p")
a1 = re.sub(r"\s+", " ", inner(col[0])).replace("to the point — the patterns", "to the point: the patterns")
a2 = re.sub(r"\s+", " ", inner(col[1])).replace("source of truth — this is just", "source of truth. This is just")
ABOUT = dict(id="about", label="About", kind="About", title="About these notes", off=True,
             credit="Notes from April 2026",
             html="<p>" + a1.strip() + "</p><p>" + a2.strip() + "</p><p>I split the notes into " + str(len(P)) +
                  " pages by hand and wrote down the words that count as a mention of each. The links, the backlinks and the lint list are worked out from that. Nothing was checked against the thread.</p>",
             url="https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f", text="")
assert "—" not in ABOUT["html"]

# ---------- emit ----------
KINDS = ["Start", "Ideas", "Themes", "Projects", "Tools", "Uses", "Tensions", "Quotes", "Playbook"]
for p in P:
    p.pop("al"); p.pop("cs")
    p["text"] = norm(" ".join([p["title"], p["label"], p.get("credit", ""), p.get("html", ""), p.get("pull", ""),
                               p.get("note", ""), " ".join(p.get("tags", []))]))
pages = []
for k in KINDS:
    for p in P:
        if p["kind"] == k: pages.append(p)
        if k == "Ideas" and p["id"] == "inverted-index": pages.append(MISSING)
data = dict(kinds=KINDS, about=ABOUT, pages=pages, links=sorted(LINKS), lint=L,
            src=dict(links=len(sel("a.wikilink")), ext=len(sel('a[href^="http"]'))))

def static(p):
    if p.get("missing"): return ""
    h = f'<article id="{p["id"]}"><h3>{html.escape(p["title"] or p["label"])}</h3>'
    if p.get("credit"): h += f'<p><small>{html.escape(p["credit"])}</small></p>'
    h += p.get("html") or "<p>No text.</p>"
    if p.get("pull"): h += f'<blockquote>{p["pull"]}</blockquote>'
    if p.get("note"): h += f'<p>{p["note"]}</p>'
    if p.get("url"): h += f'<p><a href="{p["url"]}">{p["url"]}</a></p>'
    if inn[p["id"]]:
        h += "<p>Linked from: " + ", ".join(f'<a href="#{i}">{html.escape(byid[i]["label"])}</a>' for i in inn[p["id"]]) + "</p>"
    return h + "</article>"

t = open(TPL, encoding="utf-8").read()
t = t.replace("/*DATA*/", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
t = t.replace("<!--STATIC-->", "\n".join(static(p) for p in pages))
t = t.replace("{{NPAGES}}", str(len(P))).replace("{{NLINKS}}", str(len(LINKS)))
open(OUT, "w", encoding="utf-8").write(t)

print(len(P), "pages", len(LINKS), "links")
print("orphans", orph)
for f in L: print(f["n"], f["name"], "|", f["text"][:150], "|", len(f["pages"]))
deg = sorted(((len(inn[i]), i) for i in ids), reverse=True)[:12]
print(deg)
print("max out", sorted(((len(out[i]), i) for i in ids), reverse=True)[:6])
print("longest", sorted(((len(plain(p.get('html','')+p.get('pull','')+p.get('note',''))), p['id']) for p in P), reverse=True)[:5])
if "-v" in sys.argv:
    for s, tt in sorted(LINKS): print(s, "->", tt)
