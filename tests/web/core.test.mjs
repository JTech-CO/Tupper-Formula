import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {webcrypto, createHash} from 'node:crypto';
import * as c from '../../js/core.js';
if (!globalThis.crypto?.subtle) Object.defineProperty(globalThis,'crypto',{value:webcrypto});
const A=['010','101','111','101','101'];
const presets=JSON.parse(readFileSync(new URL('../../data/presets.json',import.meta.url),'utf8'));

test('known letter A has N=16015 and k=80075',()=>{
  assert.deepEqual(c.encode(A),{n:16015n,k:80075n,w:3,h:5});
  assert.deepEqual(c.decode(80075n,3,5),A);
});
test('all masks for 1x1, 2x2, 3x2, 2x3 and 3x3',()=>{
  let count=0;
  for(const [w,h] of [[1,1],[2,2],[3,2],[2,3],[3,3]]) for(let v=0;v<2**(w*h);v++){
    const rows=Array.from({length:h},(_,r)=>Array.from({length:w},(_,i)=>String((v>>(w*r+i))&1)).join(''));
    const {k}=c.encode(rows);assert.deepEqual(c.decode(k,w,h),rows);count++;
  }
  assert.equal(count,658);
});
test('presets match Python N, k, formula, digest and canonical masks',async()=>{
  for(const {manifest:m} of presets){
    const {n,k,w,h}=c.encode(m.rows);
    assert.equal(n.toString(),m.N);assert.equal(k.toString(),m.k);
    assert.deepEqual(c.decode(k,w,h),m.rows);
    assert.equal(c.formulaLatex(h,m.formula_variant),m.formula_latex);
    assert.equal(await c.digest(m.rows),m.bitmap_sha256);
    assert.deepEqual(await c.validateManifest(m),m.rows);
  }
});
test('historical orientation reverses both axes, not the stored mask',()=>{
  const rows=['10010','01000','00101'];
  assert.deepEqual(c.displayRows(rows,'historical'),['10100','00010','01001']);
  assert.deepEqual(c.displayRows(c.displayRows(rows,'historical'),'historical'),rows);
});
test('repeated occurrence has the same finite viewport',()=>{
  assert.equal(c.repeatedK(80075n,3,5),243915n);
  assert.deepEqual(c.decode(243915n,3,5),A);
});
test('dimensions, all-zero image and leading empty columns are explicit',()=>{
  const empty=['00000','00000'];assert.equal(c.encode(empty).k,0n);
  assert.deepEqual(c.decode(0n,5,2),empty);
  assert.throws(()=>c.checkDimensions(513,1));assert.throws(()=>c.checkDimensions(512,128));
  assert.throws(()=>c.checkDimensions(1.5,2));assert.throws(()=>c.checkDimensions(0,3));
});
test('reject invalid data, floats, oversized integers and unaligned k',()=>{
  for(const rows of [[],[''],['1','00'],['x'],[1],null])assert.throws(()=>c.encode(rows));
  for(const number of ['-1','1.5','1e6','１２','9'.repeat(5501),2])assert.throws(()=>c.parseDecimal(number));
  assert.throws(()=>c.decode(80076n,3,5));assert.throws(()=>c.decode(80075,3,5));
  assert.throws(()=>c.decode(-5n,3,5));assert.throws(()=>c.displayRows(A,'untrusted'));
});
test('row parser handles ./# and CRLF',()=>assert.deepEqual(c.parseRows('.#.\r\n#.#'),['010','101']));
test('SHA-256 payload has documented dimensions and terminal newline',async()=>{
  const text='tupper-bitmap-v1\n3 5\n010\n101\n111\n101\n101\n';
  assert.equal(c.canonicalText(A),text);
  assert.equal(await c.digest(A),createHash('sha256').update(text).digest('hex'));
});
test('web manifest round trip and all semantic tampering rejected',async()=>{
  const m=await c.manifest(A);assert.deepEqual(await c.validateManifest(m),A);
  for(const [key,value] of Object.entries({width:4,height:4,N:'16016',k:'80076',bitmap_sha256:'0'.repeat(64),canonical:false,encoding:'row-major',formula_variant:'bad',formula_latex:'evil',display_orientation:'bad',rows:['1']})){
    await assert.rejects(()=>c.validateManifest({...m,[key]:value}),undefined,key);
  }
  await assert.rejects(()=>c.validateManifest({...m,domain:{x:[0,3],y_relative_to_k:[0,5],endpoints:'closed'}}));
});
test('PBM and SVG exports contain exact discrete masks',()=>{
  assert.ok(c.pbm(A).startsWith('P1\n# canonical rows top-to-bottom; 1=ink\n3 5\n'));
  assert.equal((c.svg(A).match(/h1v1h-1z/g)||[]).length,10);
  assert.ok(c.svg(A).includes('viewBox="0 0 3 5"'));
});
test('large offset stays BigInt and is never coerced through Number',()=>{
  const historical=presets.find(p=>p.id==='historical').manifest;
  assert.equal(historical.k.length,543);
  assert.equal(c.parseDecimal(historical.k).toString(),historical.k);
});
