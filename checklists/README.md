# Checklists page for indica-tech.com

One static page, `index.html`, built from the YAML specs in `specs/`. No server code, no framework, no external script;
the only network requests are Google Fonts (optional: delete the three `<link>` lines in `<head>` and the page falls back to
system fonts). Ticked boxes are remembered in the reader's own browser only.

## Deploy (static site, as the rest of indica-tech.com)

1. Copy `index.html` to the site as `/checklists/index.html` so the page is `https://indica-tech.com/checklists/`
   (the canonical tag in the file assumes that path; change it if you choose another).
2. Add one link in the site nav or footer ("Checklists") and the same URL in every social bio.
3. Each list ends with a mailto button to `hello@indica-tech.com` carrying the series word in the subject; replying with
   the PDF is a manual step today. When an email service is wired in, replace the `.get` block in `build_checklists.py`
   with its form.

## Add or change a checklist

1. Write a new `specs/NN-slug.yaml` (use `CHECKLIST-PROMPT.md` to have an LLM draft it from your research notes), or edit
   an existing one.
2. `python3 build_checklists.py` → rewrites `index.html` and `md/<slug>.md` (the Markdown is for the blog or LinkedIn).
3. The same YAML makes the one-page PDF with the pipeline's tool, from `automation/`:
   `py tools/lead_magnet.py ../website/checklists/specs/NN-slug.yaml` → `reference/lead-magnets/<pdf>`.
4. Before publishing: open every source link, compare every number with the page it links to, search the text for
   company names, and view the page at phone width. (`validate.py` does the mechanical half.)

## Rules the content follows

- Every number, date and quote from a primary source; the source linked under the item.
- No company, vendor, product or model names in the text (NG's rule of 30 Sep 2026); standards and protocols may be named.
- Effort figures are labelled as planning estimates; lab numbers are labelled as what can happen, not what every model does.
