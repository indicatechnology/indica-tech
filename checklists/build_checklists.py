#!/usr/bin/env python3
"""build_checklists.py - a hub page (index.html), one page per checklist (<slug>/index.html), one Markdown file per
checklist, and index.json, from specs/*.yaml.

    python3 build_checklists.py            # writes index.html, <slug>/index.html, md/<slug>.md and index.json next to this file

index.json is the machine-readable form of the same specs - every checklist, every check, every source - so anything that
reads the checklists programmatically never drifts from the page. It is a static file; GitHub Pages serves it as JSON.

The YAML keys are a superset of what automation/tools/lead_magnet.py reads (title, kicker, intro, checks[title, why, do, code],
footer), so the same spec also renders the one-page PDF. Body text names no company (NG's rule of 30 Sep 2026); the source
links carry the attribution. No JavaScript is required to read the page; the small script only remembers ticked boxes on the
reader's own device.
"""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SPECS = sorted((HERE / "specs").glob("*.yaml"))
OUT_HTML = HERE / "index.html"
OUT_MD = HERE / "md"
OUT_JSON = HERE / "index.json"
LEAD_MAGNETS = HERE / "lead-magnets"

SITE = "https://indica-tech.com"
MAIL = "hello@indica-tech.com"
CHANNEL = {
    "YouTube": "https://www.youtube.com/@demotoprod/shorts",
    "TikTok": "https://www.tiktok.com/@demotoprod",
    "Instagram": "https://instagram.com/demotoprod",
    "LinkedIn": "https://www.linkedin.com/company/indica-technology/",
}
ENGAGEMENTS = [
    ("Production Readiness Audit", f"{SITE}/services/audit.html"),
    ("Fractional AI Lead", f"{SITE}/services/fractional.html"),
    ("AI Build Sprint", f"{SITE}/services/build-sprint.html"),
    ("Governance and Compliance", f"{SITE}/services/governance.html"),
]
ABOUT = ("Written by Nitish Gautam, Indica Tech. Ten-plus years taking products from zero to one across seven sectors, "
         "including defence, fintech, medical and telecom, with AI shipped into regulated and air-gapped environments. "
         "The @demotoprod channel takes one production AI failure apart each day.")

e = html.escape


def load() -> list[dict]:
    specs = []
    for p in SPECS:
        s = yaml.safe_load(p.read_text(encoding="utf-8"))
        s["_file"] = p.name
        specs.append(s)
    return specs


def mailto(s: dict) -> str:
    subject = f"Send me the {s['title'].lower()} ({s['cta_word']})"
    return f"mailto:{MAIL}?subject={subject.replace(' ', '%20')}"


def why_label(s: dict) -> str:
    """The label before each check's reason. A spec may set why_label ("Why." or "What happened."); the id rule is the fallback."""
    if s.get("why_label"):
        return str(s["why_label"]).strip()
    return "Why." if s["id"].startswith("gates") or s["id"] == "kubernetes-probes" or s["id"] == "ai-failover" else "What happened."


# ----------------------------------------------------------------------------------------------------------------------
# HTML
# ----------------------------------------------------------------------------------------------------------------------
CSS = """
/* The checklist-specific layer. The pages load the site's own stylesheets first —
   /styles.css, then /look.css (the current look, light or dark) — so nav, type,
   tokens and the theme switch all come from the site. What follows is only what
   the checklists add: the page head, list layout, cards, rail, pager and print.
   Everything reads the site's tokens, with fallbacks so the classic look
   (?look=classic disables look.css) still reads correctly. */

/* The reading column; the site gutter and section rhythm do the rest. */
.wrap{max-width:860px;margin:0 auto;padding:0 var(--gutter,28px)}
.listpage .wrap{max-width:1160px}
html{scroll-padding-top:96px}
body{overflow-wrap:break-word}
.skip{position:absolute;left:-999px;top:10px;z-index:60;background:var(--signal);color:var(--signal-ink);font-family:var(--mono);font-size:.8rem;font-weight:600;padding:10px 14px;border-radius:999px;text-decoration:none}
.skip:focus{left:12px}

/* The current page in the shared nav — the same entry every other page lights. */
.nav-links a[aria-current="page"]{color:var(--ink);border-bottom-color:var(--signal)}

/* Page head: a prose-style light header with a kicker, like the blog and services
   pages — the old dark band is gone. */
.top{padding:clamp(44px,7vw,84px) 0 clamp(30px,4vw,48px);border-bottom:1px solid var(--rule)}
.top .kicker{margin-bottom:22px}
.top h1{font-size:clamp(2.1rem,4.8vw,3.5rem);line-height:1.06;margin:0 0 18px;max-width:22ch}
.lede{color:var(--ink-mute);font-size:clamp(1.05rem,1.3vw,1.2rem);line-height:1.6;max-width:62ch}
.crumb{display:inline-block;font-family:var(--mono);font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint);text-decoration:none;margin-bottom:24px}
.crumb:hover,.crumb:focus-visible{color:var(--brass-ink,#0a6b3d)}
/* List pages: the list at reading width, and a rail that stays put with progress, the downloads, the checks as
   jump links and the next list. Below 900px the rail is a block above the list and the jump links are dropped. */
.listpage main.wrap{display:grid;grid-template-columns:minmax(0,1fr) 292px;gap:52px;align-items:start;padding-top:44px;padding-bottom:56px}
.col-main{grid-column:1;grid-row:1;min-width:0}
.rail{grid-column:2;grid-row:1;position:sticky;top:92px}
.rail-in{background:var(--surface,#FFFDF8);border:1px solid var(--card-border,var(--rule,#D0C9B9));border-radius:var(--radius,14px);box-shadow:var(--shadow,none);padding:20px 20px 18px}
.rail-k{font-family:var(--mono);font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);margin:0 0 8px}
.rail-c{display:flex;justify-content:space-between;align-items:baseline;gap:10px;font-weight:600;font-size:1.05rem;letter-spacing:-.01em;margin:0 0 8px;color:var(--ink)}
.rail-c button{font:inherit;font-family:var(--mono);font-size:.74rem;font-weight:400;color:var(--brass-ink,#0a6b3d);background:none;border:0;text-decoration:underline;cursor:pointer;padding:0}
.rail-c button:hover{text-decoration-color:var(--signal)}
.rail-bar{display:block;height:5px;background:var(--rule);border-radius:999px;overflow:hidden;margin:0 0 18px}
.rail-bar span{display:block;height:100%;width:0;background:var(--signal);transition:width .2s}
.rail-a{display:flex;flex-direction:column;gap:8px;margin:0 0 18px}
.act{display:inline-block;font-family:var(--mono);font-size:.78rem;font-weight:500;letter-spacing:.04em;line-height:1;text-align:center;color:var(--ink);background:transparent;border:1px solid var(--ink);border-radius:999px;padding:13px 15px;text-decoration:none;cursor:pointer;transition:background .15s,color .15s,border-color .15s}
.act:hover{background:var(--ink);color:var(--paper)}
.act:focus-visible{outline:2px solid var(--signal);outline-offset:2px}
.act-pdf{background:var(--signal);border-color:var(--signal);color:var(--signal-ink);font-weight:600}
.act-pdf:hover{background:var(--signal);border-color:var(--signal);color:var(--signal-ink);filter:brightness(1.06)}
.rail-toc{margin:0 0 18px;padding-left:1.2rem;font-size:.9rem;line-height:1.4}
.rail-toc li{margin:0 0 7px}
.rail-toc a{color:var(--ink-mute);text-decoration:none;border-bottom:1px solid transparent}
.rail-toc a:hover{color:var(--brass-ink,#0a6b3d);border-bottom-color:currentColor}
.rail-toc a.is-here{color:var(--brass-ink,#0a7a44);font-weight:600}
.rail-next{margin:0;font-weight:500;font-size:.95rem}
.rail-next a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--rule-2)}
.rail-next a:hover{color:var(--brass-ink,#0a6b3d);border-bottom-color:currentColor}
article.check{scroll-margin-top:104px}
@media (max-width:900px){.listpage main.wrap{display:block;padding-top:32px}.rail{position:static;margin:0 0 4px}.rail-in{padding:18px}.rail-toc,.rail-next,.rail-next-k,.rail nav{display:none}.rail-a{flex-direction:row;flex-wrap:wrap;margin-bottom:2px}.rail .act{flex:1 1 auto}}

/* Hub: one card per list, in the current look's card language (surface, hairline
   border, soft shadow). The title link is stretched over the whole card, so the
   card is the click target; the PDF link sits above it and stays its own target. */
.grid{list-style:none;margin:40px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.card{position:relative;display:flex;flex-direction:column;gap:10px;background:var(--surface,#FFFDF8);border:1px solid var(--card-border,var(--rule,#D0C9B9));border-radius:var(--radius,14px);box-shadow:var(--shadow,none);padding:22px 22px 20px;transition:border-color .2s,box-shadow .2s}
.card:hover{border-color:var(--rule-2);box-shadow:var(--shadow-md,none)}
.card .num{display:flex;justify-content:space-between;gap:10px;margin:0;padding-bottom:12px;border-bottom:1px dashed var(--rule-2);font-family:var(--mono);font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint)}
.card .num b{color:var(--brass-ink,#0a7a44);font-weight:600}
.card h2{font-size:1.28rem;line-height:1.25;letter-spacing:-.015em;margin:4px 0 0}
.card h2 a{color:var(--ink)}
.card h2 a::after{content:"";position:absolute;inset:0;border-radius:inherit;cursor:pointer}
.card h2 a:focus-visible{outline:2px solid var(--signal);outline-offset:3px}
.card .sub{margin:0;font-size:.95rem;color:var(--ink-mute);flex:1 1 auto}
.card .meta{display:flex;gap:16px;align-items:center;margin:6px 0 0;font-family:var(--mono);font-size:.74rem;letter-spacing:.04em;color:var(--ink-faint)}
.card .meta a{position:relative;z-index:1;color:var(--brass-ink,#0a6b3d);font-weight:600;text-decoration:none;border-bottom:1px solid transparent}
.card .meta a:hover{border-bottom-color:currentColor}
.card .meta a:focus-visible{outline:2px solid var(--signal);outline-offset:2px}

/* One list per page. */
.list{padding:0 0 8px}
.intro{margin:0 0 18px;max-width:56ch}
.checks-head{margin:0 0 12px}
.checks-head .note{font-size:.85rem;color:var(--ink-faint);margin:4px 0 0}
.cap{font-family:var(--mono);font-size:.74rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);margin:0}
.lead-code{margin:0 0 24px}
.lead-code .cap{margin:0 0 8px}
pre{font-family:var(--mono);font-size:.82rem;line-height:1.5;background:var(--deep,#16181C);color:var(--deep-mute,#E8E6E1);border-radius:var(--radius-sm,10px);padding:16px 18px;margin:10px 0 0;overflow-x:auto;white-space:pre}
article.check{background:var(--surface,#FFFDF8);border:1px solid var(--card-border,var(--rule,#D0C9B9));border-radius:var(--radius,14px);box-shadow:var(--shadow,none);padding:18px 20px;margin:0 0 12px;break-inside:avoid}
article.check.off{opacity:.55}
.check-head{display:flex;align-items:flex-start;gap:12px;cursor:pointer;margin:0}
.check-head input{appearance:none;-webkit-appearance:none;flex:0 0 26px;width:26px;height:26px;margin:2px 0 0;border:2px solid var(--ink);border-radius:8px;background:var(--surface,#fff);display:grid;place-items:center;cursor:pointer}
.check-head input:checked{background:var(--signal);border-color:var(--signal)}
.check-head input:checked::after{content:"";width:7px;height:13px;border:solid var(--signal-ink);border-width:0 3px 3px 0;transform:translateY(-2px) rotate(45deg)}
.check-head input:focus-visible{outline:2px solid var(--signal);outline-offset:2px}
.n{font-family:var(--mono);font-weight:600;color:var(--brass-ink,#0a7a44);font-size:.95rem;flex:0 0 auto;padding-top:5px}
.check-head h2{font-family:var(--display,var(--sans));font-size:1.08rem;line-height:1.3;margin:3px 0 0;font-weight:600;letter-spacing:-.01em}
.check-body{margin:10px 0 0 38px}
.check-body p{margin:0 0 8px}
.check-body p,.check-body ul,.notes{max-width:58ch}
.check-body b{font-weight:600;color:var(--ink)}
.check-body ul{margin:0 0 8px;padding-left:1.1rem}
.check-body li{margin:0 0 5px}
.src{font-size:.85rem;color:var(--ink-mute);margin:8px 0 0!important}
.src a{color:var(--brass-ink,#0a6b3d);text-decoration:underline;text-decoration-color:var(--rule-2);text-underline-offset:2px;word-break:break-word}
.src a:hover{text-decoration-color:currentColor}
.order{margin:24px 0 0}
.order h2{font-family:var(--mono);font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint);margin:0 0 10px;font-weight:600}
.order table{width:100%;border-collapse:collapse;font-size:.92rem;background:var(--surface,#FFFDF8);border:1px solid var(--card-border,var(--rule,#D0C9B9));border-radius:var(--radius-sm,10px);overflow:hidden}
.order th,.order td{text-align:left;padding:10px 14px;border-bottom:1px solid var(--rule);vertical-align:top}
.order th{font-family:var(--mono);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint);font-weight:600;background:var(--paper-2)}
.order tr:last-child td{border-bottom:0}
.order td.num{font-family:var(--mono);font-weight:600;color:var(--brass-ink,#0a7a44);width:2.2rem}
.notes{font-size:.86rem;color:var(--ink-mute);margin:14px 0 0}

/* The take-away block: a panel in the look's "deep" family — dark in both themes,
   with a solid signal button and a ghost, like the contact section's form. */
.get{margin:24px 0 0;background:var(--deep,#0B0B0A);color:var(--on-deep,#F7F4ED);border-radius:var(--radius,14px);box-shadow:var(--shadow-md,none);padding:22px 24px;display:flex;gap:18px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.get p{margin:0;font-weight:400;max-width:52ch;color:var(--on-deep)}
.get small{display:block;color:var(--deep-mute,#C9C6BF);font-weight:300;margin-top:6px;font-size:.88rem;line-height:1.5}
.get-btns{display:flex;gap:10px;flex-wrap:wrap}
.get .btn{border-radius:999px;font-size:.82rem;font-weight:600;background:var(--signal);border-color:var(--signal);color:var(--signal-ink)}
.get .btn:hover{filter:brightness(1.06)}
.get .btn-ghost{background:transparent;color:var(--on-deep);border-color:var(--deep-line,#3A3A36)}
.get .btn-ghost:hover{border-color:var(--signal);color:var(--signal);filter:none}
.ask{margin:16px 0 0;font-size:.95rem;color:var(--ink-mute);border-left:3px solid var(--signal);padding-left:12px}
.ask b{font-weight:600;color:var(--ink)}
.ask a{color:var(--brass-ink,#0a6b3d);text-decoration:underline;text-decoration-color:var(--rule-2);text-underline-offset:2px}
.ask a:hover{text-decoration-color:currentColor}

/* Previous and next list, so moving on never needs the hub. */
.pager{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:28px 0 0}
.pager a{display:flex;flex-direction:column;gap:4px;background:var(--surface,#FFFDF8);border:1px solid var(--card-border,var(--rule,#D0C9B9));border-radius:var(--radius,14px);box-shadow:var(--shadow,none);padding:16px 18px;color:var(--ink);transition:border-color .2s,box-shadow .2s}
.pager a:hover{border-color:var(--rule-2);box-shadow:var(--shadow-md,none)}
.pager a:focus-visible{outline:2px solid var(--signal);outline-offset:2px}
.pager .next{text-align:right;align-items:flex-end}
.pager small{font-family:var(--mono);font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint)}
.pager .t{font-weight:500;line-height:1.3}
.pager .all{grid-column:1/-1;justify-self:center;background:none;border:0;box-shadow:none;padding:12px;font-family:var(--mono);font-size:.8rem;color:var(--brass-ink,#0a6b3d)}
.pager .all:hover{border-color:transparent;box-shadow:none;text-decoration:underline}

/* Subscribe — an offer, never a gate. Nothing on this page is behind it. */
.sub-block{border-top:1px solid var(--rule);margin-top:52px;padding:48px 0 64px}
.sub-block h2{font-size:clamp(1.5rem,3.2vw,2.1rem);letter-spacing:-.02em;line-height:1.12;margin:.4rem 0 .6rem;max-width:24ch}
.sub-block>p{max-width:62ch;color:var(--ink-mute);margin:0 0 22px}
.sub-form{background:var(--paper-2);border:1px solid var(--rule);border-radius:var(--radius,14px);padding:22px;max-width:580px}
.sub-row{display:flex;gap:14px;flex-wrap:wrap}
.sub-row .f{display:flex;flex-direction:column;gap:6px;flex:1 1 200px}
.sub-form label{font-family:var(--mono);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-faint)}
.sub-form input[type=text],.sub-form input[type=email]{font:inherit;font-size:.95rem;padding:11px 13px;border:1px solid var(--rule);border-radius:var(--radius-sm,10px);background:var(--surface,#FFFDF8);color:var(--ink-2);width:100%}
.sub-form input[type=text]:focus,.sub-form input[type=email]:focus{outline:2px solid var(--signal);outline-offset:-1px;border-color:var(--signal)}
.sub-form .btn{border-radius:999px;font-weight:600;background:var(--signal);border-color:var(--signal);color:var(--signal-ink)}
.sub-form .btn:hover{filter:brightness(1.06)}
.sub-form .consent{display:flex;gap:10px;align-items:flex-start;margin:16px 0 18px;font-family:var(--sans);font-size:.88rem;letter-spacing:0;text-transform:none;color:var(--ink-mute);line-height:1.5}
.sub-form .consent input{flex:0 0 auto;width:18px;height:18px;margin-top:2px;accent-color:var(--signal)}
.sub-form .consent a{color:var(--brass-ink,#0a6b3d)}

/* Small print under the shared footer columns. */
.footer-note{max-width:72ch;font-size:.85rem;color:var(--ink-faint);margin:0 0 10px}
.footer-note a{color:var(--brass-ink,#0a6b3d);border-bottom:1px solid transparent}
.footer-note a:hover{border-bottom-color:currentColor}

/* Print: the page becomes the one-page PDF, and the contact block is the back page. */
.printonly{display:none}
@media (max-width:480px){.check-body{margin-left:0}.get{padding:18px}.pager{grid-template-columns:1fr}.pager .next{text-align:left;align-items:flex-start}.pager span:empty{display:none}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}.card,.pager a{transition:none}}
@media print{
.skip,.nav,.crumb,.rail,.checks-head .note,.get,.ask,.pager,.sub-block,.footer{display:none}
.listpage main.wrap{display:block;padding:0}
article.check.off{display:none}
.top{border-bottom:0;padding:0 0 12px}
body{background:#fff;font-size:10.5pt}
article.check{border-color:#bbb;box-shadow:none}
pre{white-space:pre-wrap;background:#f5f5f5;color:#111}
a{text-decoration:none;color:#000}
.src a::after{content:" (" attr(href) ")";font-size:.75rem;color:#555}
.printonly{display:block;break-before:page;border-top:2px solid #000;margin-top:14pt;padding-top:10pt}
.pc-name{font-family:var(--sans);font-weight:600;font-size:13pt;margin:0 0 2pt}
.pc-line{color:#444;margin:0 0 10pt;font-size:9.5pt}
.pc-links{list-style:none;margin:0;padding:0;columns:2;font-size:9.5pt}
.pc-links li{margin:0 0 4pt;break-inside:avoid}
.pc-links b{font-family:var(--mono);font-size:7.5pt;letter-spacing:.08em;text-transform:uppercase;color:#666;display:block}
.pc-foot{margin:10pt 0 0;font-size:8.5pt;color:#666;border-top:1px solid #ccc;padding-top:6pt}
}
"""

JS = """
(function(){
  var key='indica-checklists-v1', state={};
  try{state=JSON.parse(localStorage.getItem(key)||'{}')||{}}catch(err){state={}}
  function save(){try{localStorage.setItem(key,JSON.stringify(state))}catch(err){}}
  function update(sec){
    var boxes=sec.querySelectorAll('input[type=checkbox]'),done=0;
    boxes.forEach(function(b){var a=b.closest('article');if(b.checked){done++;a.classList.remove('off')}else{a.classList.add('off')}});
    document.querySelectorAll('.count').forEach(function(p){p.textContent=done+' of '+boxes.length+' selected'});
    var bar=document.querySelector('.rail-bar span');if(bar){bar.style.width=(boxes.length?Math.round(done/boxes.length*100):0)+'%'}
  }
  document.querySelectorAll('.list').forEach(function(sec){
    sec.querySelectorAll('input[type=checkbox]').forEach(function(b){
      b.checked=(b.id in state)?!!state[b.id]:true;
      b.addEventListener('change',function(){state[b.id]=b.checked;save();update(sec)});
    });
    var r=document.querySelector('[data-reset]');
    if(r){r.addEventListener('click',function(){sec.querySelectorAll('input[type=checkbox]').forEach(function(b){b.checked=true;delete state[b.id]});save();update(sec)})}
    update(sec);
  });
})();
/* The jump link for the check currently in view is marked. */
(function(){
  var links=document.querySelectorAll('.rail-toc a');if(!links.length||!('IntersectionObserver' in window)){return}
  var map={};links.forEach(function(a){map[a.getAttribute('href').slice(1)]=a});
  links[0].classList.add('is-here');
  var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){links.forEach(function(a){a.classList.remove('is-here')});var a=map[en.target.id];if(a){a.classList.add('is-here')}}})},{rootMargin:'-15% 0px -70% 0px'});
  Object.keys(map).forEach(function(id){var el=document.getElementById(id);if(el){io.observe(el)}});
})();
/* Print: the browser's own print dialogue. The page holds one list, so the print
   stylesheet only drops the navigation and the calls to action and adds the contact
   page. No library, nothing generated server-side. */
document.querySelectorAll('[data-print]').forEach(function(b){
  b.addEventListener('click', function(){window.print()});
});
/* The mobile menu, the one thing the shared look.js leaves to the site's script.js. */
var nav=document.querySelector('.nav'),mb=document.querySelector('.menu-btn');
if(mb&&nav){mb.addEventListener('click',function(){nav.classList.toggle('open')})}
"""


def render_check(s: dict, k: int, c: dict) -> str:
    cid = f"{s['slug']}-{k}"
    dos = "".join(f"<li>{e(x)}</li>" for x in c.get("do", []))
    code = f"<pre>{e(c['code'].rstrip())}</pre>" if c.get("code") else ""
    srcs = c.get("sources") or []
    if srcs:
        links = "; ".join(f'<a href="{e(x["url"])}" rel="noopener">{e(x["label"])}</a>' for x in srcs)
        src = f'<p class="src">Source: {links}</p>'
    else:
        src = ""
    return f"""<article class="check" id="{cid}-card">
<label class="check-head" for="{cid}"><input type="checkbox" id="{cid}" checked><span class="n">{k}</span><h2>{e(c['title'])}</h2></label>
<div class="check-body">
<p><b>{why_label(s)}</b> {e(' '.join(c['why'].split()))}</p>
<p><b>The check.</b></p><ul>{dos}</ul>{code}{src}
</div>
</article>"""


def render_get(s: dict) -> str:
    """The take-away block and the ask after it. Nothing is gated: the list is readable on the page and as Markdown,
    the PDF is a plain download, and the print view is the same list with the contact block. The ask that follows is
    the one worth making — a live problem, not a file request."""
    pdf = s.get("pdf") if s.get("pdf") and (LEAD_MAGNETS / s["pdf"]).is_file() else None
    md = f'<a class="btn btn-ghost" href="{SITE}/checklists/md/{e(s["slug"])}.md">Markdown</a>'
    if pdf:
        btns = (f'<a class="btn" href="{SITE}/checklists/lead-magnets/{e(pdf)}" download>Download the PDF</a>{md}'
                f'<button class="btn btn-ghost" type="button" data-print>Print this list</button>')
        small = ("The PDF is the handout: this list on one or two pages. The Markdown is for your own "
                 "docs, your wiki, or an assistant you want to hand the list to. Print gives you this list only, without the navigation.")
    else:
        btns = f'<button class="btn" type="button" data-print>Print this list</button>{md}'
        small = ("Print gives you this list only, without the navigation. The Markdown is for your own docs, your wiki, "
                 "or an assistant you want to hand the list to.")
    return (f'<div class="get"><p>Take this list with you<small>{small}</small></p><div class="get-btns">{btns}</div></div>'
            f'<p class="ask"><b>Something in your production AI broke in a way that is not on this list?</b> '
            f'<a href="{SITE}/#contact">Tell me what broke</a>.</p>')


def render_list_body(s: dict) -> str:
    """One list: intro, lead code, the checks with their progress line, the order table, notes, and the take-away."""
    checks = "".join(render_check(s, k, c) for k, c in enumerate(s["checks"], 1))
    lead = ""
    if s.get("lead_code"):
        lead = (f'<div class="lead-code"><p class="cap">{e(s["lead_code"]["caption"])}</p>'
                f'<pre>{e(s["lead_code"]["code"].rstrip())}</pre></div>')
    order = ""
    if s.get("order"):
        rows = "".join(f'<tr><td class="num">{i}</td><td>{e(r[0])}</td><td>{e(r[1])}</td><td>{e(r[2])}</td></tr>'
                       for i, r in enumerate(s["order"], 1))
        order = (f'<div class="order"><h2>Work it in this order</h2><table><thead><tr><th>#</th><th>Control</th>'
                 f'<th>Effort</th><th>Impact</th></tr></thead><tbody>{rows}</tbody></table></div>')
    notes = f'<p class="notes">{e(" ".join(str(s["notes"]).split()))}</p>' if s.get("notes") else ""
    n = len(s["checks"])
    return f"""<article class="list" id="{e(s['slug'])}">
<p class="intro">{e(' '.join(s['intro'].split()))}</p>
{lead}
<div class="checks-head"><p class="cap">The checks</p><p class="note">Everything starts ticked. Untick what you will not do; the choice is saved on this device only, and Print keeps only what you kept.</p></div>
{checks}
{order}
{notes}
{render_get(s)}
</article>"""


# Page chrome shared by the hub and every list page.
BRAND_SVG = ('<svg class="brand-mark" viewBox="0 0 100 100" width="28" height="28" aria-label="Indica Tech">'
             '<circle cx="32" cy="26" r="7" fill="#00C46A"/>'
             '<rect x="25.5" y="40" width="13" height="42" fill="currentColor"/>'
             '<path d="M58 82 L78 18 L71 18 L51 82 Z" fill="currentColor"/></svg>')


def render_head(title: str, desc: str, url: str, og_type: str, first: str = "") -> str:
    """Everything inside <head>. The pages load the site's own stylesheets (styles.css, then
    look.css + look.js) with root-absolute paths, so the checklists track the current look —
    theme switch included — instead of carrying a frozen copy of it. `first` goes before the
    stylesheets, for a script that has to run before paint."""
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
{first}<link rel="stylesheet" href="/styles.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/look.css" id="look-css">
<script src="/look.js"></script>
<style>{CSS}</style>"""


def render_sitenav() -> str:
    """The shared nav markup every page carries, root-relative so it works from both the hub and
    the list pages; Checklists is the lit entry here."""
    return f"""<a class="skip" href="#main">Skip to content</a>
<nav class="nav" id="top"><div class="nav-inner">
<a href="/" class="brand">{BRAND_SVG}<span>Indica Tech <em>/ demo → prod</em></span></a>
<ul class="nav-links">
<li><a href="/#problem">The gap</a></li>
<li><a href="/#offers">Engagements</a></li>
<li><a href="/#proof">Proof</a></li>
<li><a href="/work/">Work</a></li>
<li><a href="/blog/">Blog</a></li>
<li><a href="/checklists/" aria-current="page">Checklists</a></li>
<li><a href="/#faq">FAQ</a></li>
</ul>
<a href="/#contact" class="nav-cta">Book a call <span class="arrow">→</span></a>
<button class="menu-btn" aria-label="Menu"><span></span><span></span><span></span></button>
</div></nav>"""


def render_subscribe() -> str:
    return f"""<section class="sub-block" id="more">
<h2>New checklists, as they are published</h2>
<p>One list at a time, each built the same way: a dated failure, the control that stops it, and the primary source so you can check it. Nothing else goes to this address, no digest and no newsletter.</p>
<form class="sub-form" action="https://formsubmit.co/{MAIL}" method="POST">
<input type="hidden" name="_subject" value="New checklist subscriber">
<input type="hidden" name="_captcha" value="true">
<input type="hidden" name="_template" value="table">
<input type="hidden" name="_next" value="{SITE}/thank-you.html">
<input type="text" name="_honey" tabindex="-1" autocomplete="off" style="display:none" aria-hidden="true">
<div class="sub-row">
<span class="f"><label for="sub-name">Name</label><input id="sub-name" name="name" type="text" autocomplete="name" required></span>
<span class="f"><label for="sub-email">Work email</label><input id="sub-email" name="email" type="email" autocomplete="email" required></span>
</div>
<label class="consent"><input id="sub-consent" name="consent" type="checkbox" value="I agree to receive new checklists by email" required>
<span>Email me new checklists as they are published. I can stop this any time by replying &ldquo;no&rdquo;. See the <a href="{SITE}/privacy.html">privacy policy</a>.</span></label>
<button class="btn" type="submit">Send me new checklists</button>
</form>
</section>"""


def render_print_contact() -> str:
    return f"""<aside class="printonly" aria-hidden="true">
<p class="pc-name">Nitish Gautam &mdash; Indica Technology Ltd</p>
<p class="pc-line">Founder-led AI engineering. Demo to production, in regulated industries, on fixed scope.</p>
<ul class="pc-links">
<li><b>Website</b> indica-tech.com</li>
<li><b>Book a call</b> indica-tech.com/#contact</li>
<li><b>Email</b> {MAIL}</li>
<li><b>YouTube</b> youtube.com/@demotoprod</li>
<li><b>LinkedIn</b> linkedin.com/company/indica-technology</li>
<li><b>Instagram / TikTok</b> @demotoprod</li>
</ul>
<p class="pc-foot">This list is free to share. The live version, with every source link, is at indica-tech.com/checklists/</p>
</aside>"""


def render_footer() -> str:
    """The shared footer skeleton every page carries, with the checklists' own small print kept
    as note lines; the nav column links mirror the rest of the site."""
    eng = "".join(f'<li><a href="{e(u)}">{e(t)}</a></li>' for t, u in ENGAGEMENTS)
    chan = "".join(f'<li><a href="{e(u)}" rel="noopener">{e(t)}</a></li>' for t, u in CHANNEL.items())
    return f"""<footer class="footer"><div class="container">
<div class="footer-grid">
<div class="footer-brand">
<a href="/" class="brand">{BRAND_SVG}<span>Indica Tech</span></a>
<p>{e(ABOUT)}</p>
</div>
<div class="footer-col">
<h4>Engagements</h4>
<ul>{eng}</ul>
</div>
<div class="footer-col">
<h4>Learn</h4>
<ul>
<li><a href="/blog/">Blog</a></li>
<li><a href="/checklists/">Checklists</a></li>
<li><a href="/work/">Work</a></li>
<li><a href="/about.html">About Nitish</a></li>
<li><a href="/#faq">FAQ</a></li>
</ul>
</div>
<div class="footer-col">
<h4>Elsewhere</h4>
<ul>{chan}</ul>
</div>
</div>
<p class="footer-note">The body text names no company; every incident is linked to its primary source so you can check the numbers before you take them to your team. Effort figures are planning estimates, not measurements.</p>
<p class="footer-note">Something broke in your production AI that is not on these lists? <a href="/#contact">Tell me about it</a>.</p>
<div class="footer-bottom">
<span>© {date.today().year} Indica Technology Ltd</span>
<span class="footer-legal">
<a href="/privacy.html">Privacy</a> ·
<a href="/terms.html">Terms</a> ·
<a href="/cookies.html">Cookies</a>
</span>
</div>
</div></footer>"""


def render_card(i: int, s: dict) -> str:
    pdf = s.get("pdf") if s.get("pdf") and (LEAD_MAGNETS / s["pdf"]).is_file() else None
    quick = f'<a href="{SITE}/checklists/lead-magnets/{e(pdf)}" download>PDF</a>' if pdf else ""
    return (f'<li class="card" id="{e(s["slug"])}">'
            f'<p class="num"><b>{i:02d}</b><span>{e(s["date"])}</span></p>'
            f'<h2><a href="{SITE}/checklists/{e(s["slug"])}/">{e(s["title"])}</a></h2>'
            f'<p class="sub">{e(s["subtitle"])}</p>'
            f'<p class="meta"><span>{len(s["checks"])} checks</span>{quick}</p></li>')


def render_hub(specs: list[dict]) -> str:
    """The hub: one card per list. Links shared before 19 Oct 2026 point at #slug anchors on this page, so a matching
    anchor is turned into that list's own address before paint; without JavaScript it still lands on the list's card."""
    cards = "\n".join(render_card(i, s) for i, s in enumerate(specs, 1))
    total = sum(len(s["checks"]) for s in specs)
    desc = ("Production AI checklists from Indica Tech: " + ", ".join(s["title"].lower() for s in specs) +
            ". Every item from a dated, sourced failure or a documented default, with the control that stops it.")
    slugs = json.dumps([s["slug"] for s in specs])
    redirect = (f'<script>(function(){{var s={slugs},h=location.hash.replace(/^#/,"");'
                f'if(s.indexOf(h)>-1){{location.replace("{SITE}/checklists/"+h+"/")}}}})();</script>\n')
    return f"""<!doctype html>
<html lang="en">
<head>
{render_head("Production AI checklists · Indica Tech", desc, f"{SITE}/checklists/", "website", redirect)}
</head>
<body>
{render_sitenav()}
<header class="top"><div class="wrap">
<p class="kicker">Indica Tech · @demotoprod</p>
<h1>Production AI checklists</h1>
<p class="lede">{total} checks across {len(specs)} lists. Every item is a dated failure or a documented default, with the control that stops it and a link to the primary source. Each list is its own page with a PDF and a Markdown copy, and nothing is behind a form.</p>
</div></header>
<main class="wrap" id="main">
<ul class="grid">
{cards}
</ul>
{render_subscribe()}
</main>
{render_footer()}
</body>
</html>
"""


def render_pager(prev: dict | None, nxt: dict | None, count: int) -> str:
    """Previous and next list, so moving on never needs the hub. An empty span keeps "next" on the right."""
    def link(s: dict | None, rel: str, label: str) -> str:
        if not s:
            return "<span></span>"
        return (f'<a class="{rel}" rel="{rel}" href="{SITE}/checklists/{e(s["slug"])}/"><small>{label}</small>'
                f'<span class="t">{e(s["title"])}</span></a>')
    return (f'<nav class="pager" aria-label="More checklists">{link(prev, "prev", "Previous")}{link(nxt, "next", "Next")}'
            f'<a class="all" href="{SITE}/checklists/">All {count} checklists</a></nav>')


def render_rail(s: dict, nxt: dict | None, has_pdf: bool) -> str:
    """The sticky rail: progress, the three ways to take the list away, the checks as jump links, and the next list."""
    n = len(s["checks"])
    pdf = (f'<a class="act act-pdf" href="{SITE}/checklists/lead-magnets/{e(s["pdf"])}" download>Download the PDF</a>' if has_pdf else "")
    toc = "".join(f'<li><a href="#{e(s["slug"])}-{k}-card">{e(c["title"])}</a></li>' for k, c in enumerate(s["checks"], 1))
    nxt_html = (f'<a href="{SITE}/checklists/{e(nxt["slug"])}/">{e(nxt["title"])} &rarr;</a>' if nxt
                else f'<a href="{SITE}/checklists/">All checklists &rarr;</a>')
    return f"""<aside class="rail" aria-label="Progress, downloads and contents"><div class="rail-in">
<p class="rail-k">Your list</p>
<p class="rail-c"><span class="count">{n} of {n} selected</span><button type="button" data-reset>select all</button></p>
<p class="rail-bar"><span style="width:100%"></span></p>
<div class="rail-a">{pdf}<a class="act" href="{SITE}/checklists/md/{e(s["slug"])}.md">Markdown</a><button class="act" type="button" data-print>Print this list</button></div>
<nav aria-label="On this page"><p class="rail-k">On this page</p><ol class="rail-toc">{toc}</ol></nav>
<p class="rail-k rail-next-k">Next</p><p class="rail-next">{nxt_html}</p>
</div></aside>"""


def render_list_page(s: dict, idx: int, prev: dict | None, nxt: dict | None, count: int) -> str:
    """One list on its own page."""
    url = f"{SITE}/checklists/{s['slug']}/"
    has_pdf = bool(s.get("pdf")) and (LEAD_MAGNETS / s["pdf"]).is_file()
    desc = (f"{s['subtitle']}. {len(s['checks'])} checks, each from a dated failure or a documented default, with the "
            f"control that stops it and a link to the primary source. Free to read, with a Markdown copy"
            + (" and a PDF." if has_pdf else "."))
    return f"""<!doctype html>
<html lang="en">
<head>
{render_head(f"{s['title']} · Indica Tech", desc, url, "article")}
</head>
<body class="listpage">
{render_sitenav()}
<header class="top"><div class="wrap">
<a class="crumb" href="{SITE}/checklists/">&larr; All checklists</a>
<p class="kicker">Checklist {idx:02d} of {count} · {e(s['date'])}</p>
<h1>{e(s['title'])}</h1>
<p class="lede">{e(s['subtitle'])}</p>
</div></header>
<main class="wrap" id="main">
{render_rail(s, nxt, has_pdf)}
<div class="col-main">
{render_list_body(s)}
{render_pager(prev, nxt, count)}
{render_subscribe()}
</div>
</main>
{render_print_contact()}
{render_footer()}
<script>{JS}</script>
</body>
</html>
"""


# ----------------------------------------------------------------------------------------------------------------------
# Markdown
# ----------------------------------------------------------------------------------------------------------------------
def render_md(s: dict) -> str:
    out = [f"# {s['title']}", "", f"_{s['subtitle']}_  ", f"{s['kicker']} · {s['date']}", "", " ".join(s["intro"].split()), ""]
    if s.get("lead_code"):
        out += [f"**{s['lead_code']['caption']}**", "", "```", s["lead_code"]["code"].rstrip(), "```", ""]
    for k, c in enumerate(s["checks"], 1):
        out += [f"- [ ] **{k}. {c['title']}**", "", f"  **{why_label(s)}** {' '.join(c['why'].split())}", "", "  **The check.**"]
        out += [f"  - {x}" for x in c.get("do", [])]
        if c.get("code"):
            out += ["", "  ```", *("  " + ln for ln in c["code"].rstrip().splitlines()), "  ```"]
        for x in c.get("sources") or []:
            out += ["", f"  Source: [{x['label']}]({x['url']})"]
        out += [""]
    if s.get("order"):
        out += ["## Work it in this order", "", "| # | Control | Effort | Impact |", "|---|---|---|---|"]
        out += [f"| {i} | {r[0]} | {r[1]} | {r[2]} |" for i, r in enumerate(s["order"], 1)]
        out += [""]
    if s.get("notes"):
        out += [" ".join(str(s["notes"]).split()), ""]
    pdf_line = f" The PDF is at {SITE}/checklists/lead-magnets/{s['pdf']}." if s.get("pdf") and (LEAD_MAGNETS / s["pdf"]).is_file() else ""
    out += [f"The live version of this list, with every source link, is at {SITE}/checklists/{s['slug']}/.{pdf_line}",
            "", "---", "",
            "**Nitish Gautam — Indica Technology Ltd.** Founder-led AI engineering: demo to production, in regulated industries, on fixed scope.",
            "", f"Website {SITE} · Book a call {SITE}/#contact · {MAIL}",
            "", "YouTube youtube.com/@demotoprod · LinkedIn linkedin.com/company/indica-technology · Instagram and TikTok @demotoprod",
            "", f"_{s['footer']}_", ""]
    return "\n".join(out)


# ----------------------------------------------------------------------------------------------------------------------
# JSON
# ----------------------------------------------------------------------------------------------------------------------
def render_json(specs: list[dict]) -> str:
    """The whole set as one document. pdf_url is null until the PDF exists on disk, so the feed never promises a file
    that 404s; re-run the build after adding one and it fills in."""
    out = []
    for s in specs:
        pdf = s.get("pdf")
        has_pdf = bool(pdf) and (LEAD_MAGNETS / pdf).is_file()
        out.append({
            "id": s["id"],
            "slug": s["slug"],
            "title": s["title"],
            "subtitle": s.get("subtitle"),
            "date": s.get("date"),
            "cta_word": s.get("cta_word"),
            "url": f"{SITE}/checklists/{s['slug']}/",
            "markdown_url": f"{SITE}/checklists/md/{s['slug']}.md",
            "pdf_url": f"{SITE}/checklists/lead-magnets/{pdf}" if has_pdf else None,
            "intro": " ".join(s["intro"].split()),
            "check_count": len(s["checks"]),
            "checks": [{
                "n": k,
                "title": c["title"],
                "why": " ".join(c["why"].split()),
                "do": c.get("do", []),
                "code": (c.get("code") or "").rstrip() or None,
                "sources": [{"label": x["label"], "url": x["url"]} for x in (c.get("sources") or [])],
            } for k, c in enumerate(s["checks"], 1)],
            "order": [{"n": i, "control": r[0], "effort": r[1], "impact": r[2]}
                      for i, r in enumerate(s.get("order") or [], 1)],
        })
    doc = {
        "publisher": "Indica Technology Ltd",
        "site": SITE,
        "page": f"{SITE}/checklists/",
        "contact": MAIL,
        "licence": "Free to read, quote and share with attribution to indica-tech.com.",
        "note": ("Every figure comes from the linked primary source. Body text names no company; the source links carry "
                 "the attribution. Effort figures are planning estimates, not measurements."),
        "generated": date.today().isoformat(),
        "count": len(out),
        "check_count": sum(c["check_count"] for c in out),
        "checklists": out,
    }
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


RESERVED = {"md", "specs", "lead-magnets"}  # directories beside the list pages; a slug may not shadow one


def write_pages(specs: list[dict]) -> None:
    OUT_HTML.write_text(render_hub(specs), encoding="utf-8")
    for i, s in enumerate(specs):
        prev = specs[i - 1] if i else None
        nxt = specs[i + 1] if i + 1 < len(specs) else None
        page_dir = HERE / s["slug"]
        page_dir.mkdir(exist_ok=True)
        (page_dir / "index.html").write_text(render_list_page(s, i + 1, prev, nxt, len(specs)), encoding="utf-8")


def main() -> int:
    specs = load()
    clash = [s["slug"] for s in specs if s["slug"] in RESERVED]
    if clash:
        print(f"error: slug(s) {clash} would overwrite a directory next to the list pages")
        return 1
    write_pages(specs)
    OUT_MD.mkdir(exist_ok=True)
    for s in specs:
        (OUT_MD / f"{s['slug']}.md").write_text(render_md(s), encoding="utf-8")
    OUT_JSON.write_text(render_json(specs), encoding="utf-8")
    missing = [s["pdf"] for s in specs if s.get("pdf") and not (LEAD_MAGNETS / s["pdf"]).is_file()]
    print(f"wrote {OUT_HTML.name} ({OUT_HTML.stat().st_size:,} bytes), {len(specs)} list pages (<slug>/index.html), "
          f"{len(specs)} markdown files in md/, and {OUT_JSON.name} ({OUT_JSON.stat().st_size:,} bytes)")
    if missing:
        print(f"note: {len(missing)} PDF(s) named in specs but not in lead-magnets/ — pdf_url is null for these:")
        for m in missing:
            print(f"      {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
