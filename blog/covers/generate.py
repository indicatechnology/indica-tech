#!/usr/bin/env python3
"""Generate per-post social cover images and wire og:image / twitter:image.

Discovers blog posts (blog/*.html and blog/*/index.html), renders a 1200x630
PNG cover per post into blog/covers/<slug>.png using headless Chrome, and
inserts og:image + twitter:image metas into each post's <head>.

Design tokens mirror the site OG card (/og-image.png). Regenerate any time
with:  python3 blog/covers/generate.py
"""
import json
import re
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BLOG = REPO / "blog"
COVERS = BLOG / "covers"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE_URL = "https://indica-tech.com/blog/covers"
LISTING_SLUG = "field-notes-on-shipping-ai"

FONT_CSS = ("https://fonts.googleapis.com/css2?"
            "family=IBM+Plex+Mono:wght@400;500"
            "&family=IBM+Plex+Sans:wght@400;600&display=swap")

RENDER_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{font_css}" rel="stylesheet">
<style>html,body{{margin:0;padding:0;width:1200px;height:630px;overflow:hidden;background:#F7F4ED}}</style>
</head><body>
<svg width="1200" height="630" viewBox="0 0 1200 630" xmlns="http://www.w3.org/2000/svg">
<rect width="1200" height="630" fill="#F7F4ED"/>
<rect x="48" y="48" width="1104" height="534" fill="none" stroke="#0B0B0A" stroke-width="2"/>
<g transform="translate(96,118)"><circle cx="18" cy="14" r="10" fill="#00C46A"/><rect x="10" y="30" width="17" height="56" fill="#0B0B0A"/><path d="M48 86 L74 18 L66 18 L40 86 Z" fill="#0B0B0A"/></g>
<text x="200" y="178" font-family="'IBM Plex Mono', monospace" font-size="22" letter-spacing="3" fill="#6E6A62">INDICA TECH / BLOG</text>
<text id="main" font-family="'IBM Plex Sans', sans-serif" font-weight="600" font-size="54" letter-spacing="-2" fill="#0B0B0A"></text>
<text id="sub" font-family="'IBM Plex Sans', sans-serif" font-weight="400" font-size="32" fill="#4A4741"></text>
<line x1="96" y1="508" x2="1104" y2="508" stroke="#0B0B0A" stroke-width="1"/>
<text id="foot" x="96" y="554" font-family="'IBM Plex Mono', monospace" font-size="20" fill="#0B0B0A"></text>
<circle cx="1056" cy="544" r="12" fill="#00C46A"/>
</svg>
<script>
const DATA = {data};
const NS = "http://www.w3.org/2000/svg";
function wrap(text, weight, size, ls, maxW) {{
  const ctx = wrap.ctx || (wrap.ctx = document.createElement("canvas").getContext("2d"));
  ctx.font = weight + " " + size + 'px "IBM Plex Sans"';
  if ("letterSpacing" in ctx) ctx.letterSpacing = ls + "px";
  const lines = [];
  let cur = "";
  for (const w of text.split(/\\s+/)) {{
    const t = cur ? cur + " " + w : w;
    if (!cur || ctx.measureText(t).width <= maxW) cur = t;
    else {{ lines.push(cur); cur = w; }}
  }}
  if (cur) lines.push(cur);
  return lines;
}}
function fill(el, lines, x, y0, lh) {{
  el.textContent = "";
  lines.forEach((ln, i) => {{
    const t = document.createElementNS(NS, "tspan");
    t.setAttribute("x", x); t.setAttribute("y", y0 + i * lh); t.textContent = ln;
    el.appendChild(t);
  }});
}}
function layout() {{
  let size = 54, lines;
  for (const s of [54, 48, 42]) {{
    lines = wrap(DATA.main, "600", s, -2, 980);
    size = s;
    if (lines.length <= 2) break;
  }}
  const main = document.getElementById("main");
  main.setAttribute("font-size", size);
  fill(main, lines, 96, 290, 66);
  const sub = document.getElementById("sub");
  if (DATA.sub) {{
    const sl = wrap(DATA.sub, "400", 32, 0, 980).slice(0, 2);
    fill(sub, sl, 96, 290 + lines.length * 66 + 2, 40);
  }}
  document.getElementById("foot").textContent = DATA.foot;
}}
Promise.all([
  document.fonts.load('600 54px "IBM Plex Sans"'),
  document.fonts.load('400 32px "IBM Plex Sans"'),
  document.fonts.load('400 20px "IBM Plex Mono"'),
]).then(layout);
</script>
</body></html>
"""


def fail(msg):
    sys.exit(f"generate.py: ERROR: {msg}")


def slugify(text):
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if not slug:
        fail(f"empty slug from title {text!r}")
    return slug


def discover_posts():
    posts = [p for p in sorted(BLOG.glob("*.html")) if p.name != "index.html"]
    posts += sorted(p for p in BLOG.glob("*/index.html") if p.parent != COVERS)
    return posts


def extract(page):
    text = page.read_text(encoding="utf-8")
    og = re.search(r'<meta property="og:title" content="([^"]*)">', text)
    if not og:
        fail(f"{page.relative_to(REPO)}: no og:title meta")
    title = og.group(1)
    m = re.search(r'<meta property="article:published_time" content="([0-9]{4}-[0-9]{2}-[0-9]{2})">', text)
    if not m:
        m = re.search(r'"datePublished"\s*:\s*"([0-9]{4}-[0-9]{2}-[0-9]{2})"', text)
    if not m:
        fail(f"{page.relative_to(REPO)}: no article:published_time and no JSON-LD datePublished")
    return title, date.fromisoformat(m.group(1))


def listing_cover():
    text = (BLOG / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<meta name="description" content="([^"]*)">', text)
    desc = m.group(1) if m else ""
    subtitle = desc if len(desc) <= 90 else ""
    return "Field notes on shipping AI", subtitle, None


def render(slug, main, subtitle, published):
    if published:
        foot = f"{published.day:02d} {published.strftime('%B').upper()} {published.year} · indica-tech.com/blog"
    else:
        foot = "indica-tech.com/blog"
    data = json.dumps({"main": main, "sub": subtitle, "foot": foot})
    html_path = Path(f"/tmp/cover-render-{slug}.html")
    html_path.write_text(RENDER_HTML.format(font_css=FONT_CSS, data=data), encoding="utf-8")
    out = COVERS / f"{slug}.png"
    cmd = [
        CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--virtual-time-budget=20000",
        f"--screenshot={out}", "--window-size=1200,630", html_path.as_uri(),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    html_path.unlink()


def insert_metas(page, slug):
    text = page.read_text(encoding="utf-8")
    if 'property="og:image"' in text and 'name="twitter:image"' in text:
        return "skipped (already present)"
    m = re.search(r"^[ \t]*<meta name=\"twitter:card\" content=\"summary_large_image\">\n?", text, re.M)
    if not m:
        # some older posts have no twitter:card; anchor after the last og:* meta instead
        anchors = list(re.finditer(r"^[ \t]*<meta property=\"og:[^\"]+\" content=\"[^\"]*\">\n?", text, re.M))
        m = anchors[-1] if anchors else None
    if not m:
        fail(f"{page.relative_to(REPO)}: no twitter:card line and no og:* metas to anchor insertion")
    metas = (f'<meta property="og:image" content="{BASE_URL}/{slug}.png">\n'
             f'<meta name="twitter:image" content="{BASE_URL}/{slug}.png">\n')
    page.write_text(text[:m.end()] + metas + text[m.end():], encoding="utf-8")
    return "inserted"


def main():
    if not Path(CHROME).exists():
        fail(f"Chrome not found at {CHROME}")
    COVERS.mkdir(exist_ok=True)

    jobs = []  # (page or None for listing, slug, main, subtitle, published)
    for page in discover_posts():
        title, published = extract(page)
        main_title, sep, subtitle = title.partition(" — ")
        jobs.append((page, slugify(main_title), main_title, subtitle if sep else "", published))

    main_l, sub_l, pub_l = listing_cover()
    jobs.append((BLOG / "index.html", LISTING_SLUG, main_l, sub_l, pub_l))

    slugs = {}
    for page, slug, *_ in jobs:
        if slug in slugs:
            fail(f"slug collision {slug!r}: {slugs[slug]} and {page.relative_to(REPO)}")
        slugs[slug] = page.relative_to(REPO)

    generated, inserted, skipped = [], [], []
    for page, slug, main_t, subtitle, published in jobs:
        render(slug, main_t, subtitle, published)
        generated.append(f"{slug}.png")
        status = insert_metas(page, slug)
        (inserted if status == "inserted" else skipped).append(f"{page.relative_to(REPO)} ({status})")

    print(f"covers generated: {len(generated)} -> {COVERS.relative_to(REPO)}/")
    for name in generated:
        print(f"  {name}")
    print(f"metas inserted:   {len(inserted)}")
    for name in inserted:
        print(f"  {name}")
    print(f"skipped:          {len(skipped)}")
    for name in skipped:
        print(f"  {name}")


if __name__ == "__main__":
    main()
