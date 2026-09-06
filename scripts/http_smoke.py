"""Check real local HTTP delivery at / and at a repository subpath.

This uses Python's HTTP client, not a browser; ES module execution and browser
policy are covered only by the separate browser/Node test scopes.
"""
from __future__ import annotations
import argparse,functools,json,threading
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.request import urlopen
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def run()->dict:
    paths=[ROOT/'index.html',ROOT/'sitemap.xml',ROOT/'README.md',ROOT/'README-KR.md',ROOT/'LICENSE',ROOT/'references.bib',ROOT/'CITATION.cff']
    for name in ('css','js','data','assets','examples','schemas','docs'):
        paths.extend(p for p in (ROOT/name).rglob('*') if p.is_file())
    paths=sorted(set(paths));count=0
    for directory,subpath in ((ROOT,''),(ROOT.parent,ROOT.name+'/')):
        server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(directory)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            base=f'http://127.0.0.1:{server.server_port}/'
            for file in paths:
                with urlopen(base+quote(subpath+file.relative_to(ROOT).as_posix()),timeout=5) as response:
                    if response.status!=200 or response.read()!=file.read_bytes():raise AssertionError('HTTP content mismatch: '+file.name)
                count+=1
            with urlopen(base+quote(subpath),timeout=5) as response:
                if response.read()!=(ROOT/'index.html').read_bytes():raise AssertionError('index fallback mismatch')
            count+=1
        finally:server.shutdown();server.server_close()
    return {'suite':'static-http/v1','passed':True,'files_per_route':len(paths),
            'successful_requests':count,'routes':['/','/<repository>/'],
            'scope':'Python HTTP client: exact local response bytes and index resolution. Not browser module execution or live GitHub Pages.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'reports/http.json');a=p.parse_args()
    result=run();text=json.dumps(result,indent=2)+'\n';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text);print(text)
