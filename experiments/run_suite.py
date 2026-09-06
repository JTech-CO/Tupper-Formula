"""Deterministic arithmetic experiment; run from the repository root.

python experiments/run_suite.py --output reports/arithmetic.json
The checked-in report is a run artifact, not a portable timing benchmark.
"""
from __future__ import annotations
import argparse
import json
import random
import platform
import sys
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from tupper_formula import Bitmap,encode,decode,evaluate,evaluate_literal,repeat_k
from tupper_formula.radix import encode_array,decode_array


def run() -> dict:
    exhaustive=0; cells=0; points=0; mismatches=0
    for w,h in ((1,1),(2,2),(3,2),(2,3),(3,3)):
        for n in range(1 << (w*h)):
            bitmap=decode(n*h,w,h)
            mismatches += encode(bitmap)!=(n,n*h)
            exhaustive+=1;cells+=w*h
            for i in range(w):
                for j in range(h):
                    x=Fraction(2*i+1,2);y=Fraction(2*(h*n+j)+1,2)
                    mismatches += evaluate(x,y,h)!=evaluate_literal(x,y,h)
                    points+=1
    rng=random.Random(20260906)
    random_cases=300
    for _ in range(random_cases):
        w,h=rng.randint(1,32),rng.randint(1,24)
        b=Bitmap(tuple(''.join(str(rng.randrange(2)) for _ in range(w)) for _ in range(h)))
        _,k=encode(b)
        mismatches += decode(k,w,h)!=b
        mismatches += decode(repeat_k(k,w,h,rng.randrange(1,20)),w,h)!=b
        cells+=w*h
    radix_cases=0
    for base in (2,3,7,16):
        for shape in ((3,5),(2,3,4)):
            values=[rng.randrange(base) for _ in range(__import__('math').prod(shape))]
            mismatches += decode_array(encode_array(values,shape,base),shape,base)!=values
            radix_cases+=1
    return {'suite':'arithmetic-v1','seed':20260906,'python':platform.python_version(),
            'exhaustive_bitmaps':exhaustive,'random_bitmaps':random_cases,
            'binary_cells':cells,'literal_rational_midpoints':points,
            'radix_arrays':radix_cases,'mismatches':mismatches,'passed':mismatches==0,
            'scope':'Finite regression evidence. General correctness follows from the documented identity.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'reports/arithmetic.json');args=p.parse_args()
    report=run();text=json.dumps(report,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text,encoding='utf-8')
    print(text,end='');raise SystemExit(0 if report['passed'] else 1)
