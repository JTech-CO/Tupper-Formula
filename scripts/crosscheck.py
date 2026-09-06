"""Generate JavaScript manifests, then verify them with Python exact arithmetic."""
from __future__ import annotations
import json,subprocess,sys,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from tupper_formula.manifest import verify_manifest

def run():
    program='''import {webcrypto} from 'node:crypto';
if(!globalThis.crypto?.subtle)Object.defineProperty(globalThis,'crypto',{value:webcrypto});
import {manifest} from './js/core.js';
const cases=[['010','101','111','101','101'],['10010','01000','00101'],['00000000','11100010','01010101']];
console.log(JSON.stringify(await Promise.all(cases.map((rows,i)=>manifest(rows,i===1?'historical':'cartesian',i===2?'bit':'tupper')))));
'''
    result=subprocess.run(['node','--input-type=module','-e',program],cwd=ROOT,text=True,capture_output=True,check=True)
    cases=json.loads(result.stdout);results=[verify_manifest(m,literal=True) for m in cases]
    return {'suite':'js-to-python/v1','cases':len(cases),'all_passed':all(r['passed'] for r in results),
            'results':results,'scope':'Native Node ES modules export the browser-format schema; Python recomputes it with literal rational checks. Not an OS file-dialog test.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'reports/cross-language.json');a=p.parse_args()
    report=run();text=json.dumps(report,indent=2)+'\n';a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text);print(text)
    raise SystemExit(0 if report['all_passed'] else 1)
