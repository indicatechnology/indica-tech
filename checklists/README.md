# Checklists page for indica-tech.com

A hub page, `index.html`, and one page per checklist, `<slug>/index.html`, built from the YAML specs in `specs/`. No server code, no framework. The pages load the site's own
stylesheets (`/styles.css`, then `/look.css` + `/look.js`, root-absolute) like every other page, so they track the current look — theme switch included; a small inline `<style>`
in each page covers only the checklist-specific parts (list layout, cards, rail, pager, print), reading the site's design tokens. The only other network requests are Google Fonts
(they serve the classic look's IBM Plex; delete the three `<link>` lines in `build_checklists.py:render_head` and both looks fall back to system fonts). Ticked boxes are remembered
in the reader's own browser only.

## Deploy (static site, as the rest of indica-tech.com)

1. Copy `index.html` and every `<slug>/index.html` to the site under `/checklists/`, so the hub is
   `https://indica-tech.com/checklists/` and each list is `https://indica-tech.com/checklists/<slug>/` (the canonical
   tags assume those paths; change `SITE` in `build_checklists.py` if you choose another).
2. Add one link in the site nav or footer ("Checklists") and the same URL in every social bio.
3. Each list ends with a mailto button to `hello@indica-tech.com` carrying the series word in the subject; replying with
   the PDF is a manual step today. When an email service is wired in, replace the `.get` block in `build_checklists.py`
   with its form.

## Add or change a checklist

1. Write a new `specs/NN-slug.yaml` (use `CHECKLIST-PROMPT.md` to have an LLM draft it from your research notes), or edit
   an existing one.
2. `python3 build_checklists.py` → rewrites `index.html`, `<slug>/index.html`, `md/<slug>.md` and `index.json` (the
   Markdown is for the blog or LinkedIn). Add the new list's URL to `/sitemap.xml`.
3. The same YAML makes the PDF with the pipeline's tool (`~/Nitish/demotoprod/automation/tools/lead_magnet.py`):
   `automation/venv/bin/python3 automation/tools/lead_magnet.py <path to specs/NN-slug.yaml>` → `reference/lead-magnets/<pdf>`.
   The list is page one (a long list runs to two sheets) and the contact page is always last: name, the four
   engagements as the situations they fit, and every link, so the file says who to call wherever it ends up.
   Copy the PDF into `lead-magnets/` here; the file name is the spec's `pdf:` field.
4. Before publishing: open every source link, compare every number with the page it links to, search the text for
   company names, and view the page at phone width. (`validate.py` does the mechanical half.)

## Rules the content follows

- Every number, date and quote from a primary source; the source linked under the item.
- No company, vendor, product or model names in the text (NG's rule of 30 Sep 2026); standards and protocols may be named.
- Effort figures are labelled as planning estimates; lab numbers are labelled as what can happen, not what every model does.
