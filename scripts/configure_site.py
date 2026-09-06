"""Set publication metadata without contacting GitHub or deploying anything."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
from urllib.parse import urlsplit
from build_site import build
ROOT=Path(__file__).resolve().parents[1]

def configure(owner:str, repo:str, base_url:str|None=None)->None:
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}',owner):raise ValueError('invalid GitHub owner')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}',repo):raise ValueError('invalid repository name')
    base=base_url or f'https://{owner.lower()}.github.io/{repo}/'
    u=urlsplit(base)
    if u.scheme!='https' or not u.netloc or u.query or u.fragment or u.username or u.password:raise ValueError('base URL must be a public-style HTTPS URL without query, fragment or credentials')
    if any(c.isspace() or c in '<>\"\'' for c in base):raise ValueError('base URL contains unsafe characters')
    base=base.rstrip('/')+'/'
    site={'base_url':base,'repo_url':f'https://github.com/{owner}/{repo}',
          'note':'Configured publication target; existence and deployment are not asserted.'}
    (ROOT/'data/site.json').write_text(json.dumps(site,indent=2)+'\n')
    schema=json.loads((ROOT/'schemas/experiment.schema.json').read_text())
    schema['$id']=base+'schemas/experiment.schema.json'
    (ROOT/'schemas/experiment.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
    p=ROOT/'CITATION.cff'
    if p.exists():
        text=p.read_text();text=re.sub(r'^repository-code:.*$',f'repository-code: "{site["repo_url"]}"',text,flags=re.M)
        text=re.sub(r'^url:.*$',f'url: "{base}"',text,flags=re.M);p.write_text(text)
    build()
    print('Updated metadata only:',base)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owner',required=True);p.add_argument('--repo',default='Tupper-Formula');p.add_argument('--base-url')
    args=p.parse_args()
    try:configure(args.owner,args.repo,args.base_url)
    except (ValueError,OSError) as e:p.error(str(e))
