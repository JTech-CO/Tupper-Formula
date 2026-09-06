"""Stage only public static content, without copying Python environments or Git files."""
from pathlib import Path
import argparse,shutil
ROOT=Path(__file__).resolve().parents[1]
ITEMS=['index.html','.nojekyll','sitemap.xml','css','js','data','assets','docs','examples',
       'reports','schemas','README.md','README-KR.md','LICENSE','CITATION.cff','references.bib']

def stage(destination:Path)->int:
    dest=destination.resolve()
    if dest==ROOT or ROOT.is_relative_to(dest):raise ValueError('destination must not replace the source or its ancestor')
    if any((ROOT/name).is_dir() and dest.is_relative_to(ROOT/name) for name in ITEMS):raise ValueError('destination must not be inside a copied source folder')
    if dest.exists():raise FileExistsError('staging destination already exists; remove it explicitly or use a new path')
    dest.mkdir(parents=True)
    for name in ITEMS:
        src=ROOT/name;target=dest/name
        if src.is_dir():shutil.copytree(src,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        else:shutil.copy2(src,target)
    return sum(p.is_file() for p in dest.rglob('*'))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'_site');a=p.parse_args()
    print('Staged',stage(a.output),'files')
