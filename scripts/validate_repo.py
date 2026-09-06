"""Check publication artifacts, bilingual Markdown, links and semantic fixtures.

Uses the standard library; when jsonschema is installed, schema validation is
also run and reported. Does not claim to check external link availability.
"""
from __future__ import annotations
import argparse,json,re,sys,struct
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from tupper_formula.manifest import verify_manifest

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[];self.equations=0;self.copy_buttons=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if 'data-equation' in a:self.equations+=1
        if 'data-copy-latex' in a:self.copy_buttons+=1
        for name in ('src','href'):
            if a.get(name):self.links.append(a[name])

def validate()->dict:
    errors=[];checked=0
    def link(text,base):
        nonlocal checked
        u=urlsplit(text)
        if u.scheme or u.netloc or text.startswith('#'):return
        if not u.path:return
        target=(base/unquote(u.path)).resolve()
        if not target.is_relative_to(ROOT) or not target.exists():errors.append(f'Broken local link: {base.relative_to(ROOT)} -> {text}')
        checked+=1
    mds=sorted(p for p in ROOT.rglob('*.md') if not any(x in p.parts for x in ('_site','.venv','node_modules')))
    for p in mds:
        partner=p.with_name(p.stem[:-3]+'.md') if p.stem.endswith('-KR') else p.with_name(p.stem+'-KR.md')
        if not partner.exists():errors.append('Missing Markdown language pair: '+str(p.relative_to(ROOT)))
        for url in re.findall(r'\]\(([^\s)]+)',p.read_text(encoding='utf-8')):link(url,p.parent)
    parser=Links();html=(ROOT/'index.html').read_text();parser.feed(html)
    for url in parser.links:link(url,ROOT)
    for url in parser.links:
        if url.startswith('#') and url[1:] not in parser.ids:errors.append('Broken HTML anchor: '+url)
    if len(parser.ids)!=len(set(parser.ids)):errors.append('Duplicate HTML id')
    if re.search(r'__(?:BASE|REPO|CONTENT|FORMULA|REFERENCES)',html):errors.append('Unresolved HTML template marker')
    if parser.copy_buttons<parser.equations:errors.append('Equation missing copy control')
    for folder in ('css','js'):
        for p in (ROOT/folder).glob('*'):
            for url in re.findall(r'''(?:from\s+["']|url\(["']?)(\.[^"')\s]+)''',p.read_text()):link(url,p.parent)
    for p in ROOT.rglob('*'):
        if p.suffix.lower() in {'.ttf','.otf','.woff','.woff2','.ttc'} and not any(x in p.parts for x in ('.venv','node_modules')):errors.append('Font file must not be distributed: '+str(p))
    ui=json.loads((ROOT/'data/ui.json').read_text());content=json.loads((ROOT/'data/content.json').read_text())
    for obj in (ui,content):
        if set(obj['en'])!=set(obj['ko']):errors.append('Language key mismatch')
    for key in re.findall(r'data-i18n="([^"]+)"',html):
        if key not in ui['en']:errors.append('Missing UI key: '+key)
    for lang in ('en','ko'):
        for fragment in content[lang].values():
            pp=Links();pp.feed(fragment)
            for url in pp.links:link(url,ROOT)
    schema=json.loads((ROOT/'schemas/experiment.schema.json').read_text());schema_checked=False
    try:import jsonschema
    except ImportError:jsonschema=None
    manifests=list((ROOT/'examples').glob('*/experiment.json'))
    for p in manifests:
        data=json.loads(p.read_text());result=verify_manifest(data)
        if not result['passed']:errors.append('Invalid fixture: '+str(p))
        if jsonschema is not None:jsonschema.validate(data,schema);schema_checked=True
        if (p.parent/'target.pbm').read_bytes()!=(p.parent/'decoded.pbm').read_bytes():errors.append('PBM mismatch: '+str(p))
    for preset in json.loads((ROOT/'data/presets.json').read_text()):
        result=verify_manifest(preset['manifest'])
        if not result['passed']:errors.append('Invalid embedded preset')
    png=(ROOT/'assets/og-image.png').read_bytes()
    if png[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',png[16:24])!=(1200,630):errors.append('OG image must be PNG 1200x630')
    return {'suite':'repository-publication/v1','passed':not errors,'markdown_files':len(mds),
            'language_pairs':len(mds)//2,'local_links_checked':checked,'static_equations':parser.equations,
            'latex_copy_controls':parser.copy_buttons,'example_manifests':len(manifests),
            'jsonschema_checked':schema_checked,'font_files_distributed':0,'errors':errors,
            'scope':'Local files, bilingual keys, semantic fixtures and publication metadata; external URLs and deployed Pages not checked.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'reports/repository.json');a=p.parse_args()
    report=validate();text=json.dumps(report,indent=2)+'\n';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text);print(text)
    raise SystemExit(0 if report['passed'] else 1)
