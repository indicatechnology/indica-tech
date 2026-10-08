#!/usr/bin/env python3
"""validate.py - the mechanical checks on index.html: well-formed HTML, no company names in visible text, every YAML parses,
word counts inside the prompt's limits, and (optional, --links) that every source URL answers 200."""
import html.parser, re, sys, glob, yaml, urllib.request
NAMES = ['OpenAI','Anthropic','GitHub','METR','Perplexity','Hugging Face','Z.ai','ZCode','GitGuardian','Cycode','Microsoft','Google',
         'Amazon','AWS','Meridian','AISI','Inspect','Medicare','Services Australia','GPT','Claude','Gemini','Fastly','PyPI','Firecracker',
         'Vercel','Salesforce','Zscaler','Alibaba','Tencent']
src = open('index.html', encoding='utf-8').read()
class P(html.parser.HTMLParser):
    def __init__(s): super().__init__(); s.stack=[]; s.errs=[]
    def handle_starttag(s,t,a):
        if t not in ('meta','link','input','br','img','hr'): s.stack.append(t)
    def handle_endtag(s,t):
        if not s.stack or s.stack[-1]!=t: s.errs.append((t,s.getpos()))
        else: s.stack.pop()
p=P(); p.feed(src); ok = not p.stack and not p.errs
print(("OK  " if ok else "FAIL") + " html well-formed", p.errs[:3])
text = re.sub(r'<(script|style).*?</\1>', '', src, flags=re.S); text = re.sub(r'href="[^"]*"', '', text); text = re.sub(r'<[^>]+>', ' ', text)
hits = {n: len(re.findall(r'\b'+re.escape(n)+r'\b', text)) for n in NAMES}; hits = {k:v for k,v in hits.items() if v}
print(("OK  " if not hits else "FAIL") + " no company names in visible text", hits)
urls = []
for f in sorted(glob.glob('specs/*.yaml')):
    s = yaml.safe_load(open(f, encoding='utf-8'))
    wi = len(s['intro'].split()); bad = []
    for c in s['checks']:
        w = len(c['why'].split())
        if not 20 <= w <= 120: bad.append((c['title'][:40], w))
        for x in c.get('sources') or []:
            if x['url'] not in urls: urls.append(x['url'])
    print(("OK  " if 45 <= wi <= 120 and not bad else "WARN") + f" {f}: intro {wi} words; why outside 20-120: {bad}")
if '--links' in sys.argv:
    for u in urls:
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=20); print("OK  ", r.status, u)
        except Exception as ex: print("FAIL", ex, u)
