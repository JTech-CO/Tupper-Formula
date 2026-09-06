"""Build static English HTML from bilingual source data. No npm or network needed."""
import json
import re
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]

def build():
    content=json.loads((ROOT/'data/content.json').read_text(encoding='utf-8'))
    formulas=json.loads((ROOT/'data/formulas.json').read_text(encoding='utf-8'))
    refs=json.loads((ROOT/'data/references.json').read_text(encoding='utf-8'))
    site=json.loads((ROOT/'data/site.json').read_text(encoding='utf-8'))
    html=(ROOT/'scripts/templates/index.html').read_text(encoding='utf-8')
    html=html.replace('__BASE_URL__',escape(site['base_url'],quote=True)).replace('__REPO_URL__',escape(site['repo_url'],quote=True))
    def equation(match):
        name=match[1];f=formulas[name]
        tex=escape(f['latex']);attr=escape(f['latex'],quote=True)
        return f'''<div class="equation" data-equation="{name}"><div class="equation-header"><span class="equation-title">{escape(f['title']['en'])}</span><button type="button" data-copy-latex="{attr}">Copy LaTeX</button></div><div class="math-body"><math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics>{f['mathml']}<annotation encoding="application/x-tex">{tex}</annotation></semantics></math></div><details class="tex-source"><summary>LaTeX source</summary><pre><code>{tex}</code></pre></details></div>'''
    html=re.sub(r'__FORMULA_([a-z-]+)__',equation,html)
    html=re.sub(r'__CONTENT_([a-z-]+)__',lambda m:f'<div data-content="{m[1]}">{content["en"][m[1]]}</div>',html)
    # All reference URLs are curated data; attributes are still escaped.
    reference_html='\n'.join(f'<li id="ref-{r["id"]}"><span>{escape(r["authors"])} ({escape(r["year"])}).</span> <a href="{escape(r["url"],quote=True)}">{escape(r["title"])}.</a><span class="reference-meta">{escape(r["venue"])} · {escape(r["type"])}</span></li>' for r in refs)
    html=html.replace('__REFERENCES__',reference_html)
    if re.search(r'__[A-Z]+_',html):raise RuntimeError('Unresolved template placeholder')
    (ROOT/'index.html').write_text(html,encoding='utf-8')
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+escape(site['base_url'])+'</loc></url></urlset>\n',encoding='utf-8')
    print('Built index.html and sitemap.xml')

if __name__=='__main__':build()
