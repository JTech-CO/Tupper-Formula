/** Independent integer implementation. Canonical files store rows top-to-bottom. */
export const LIMITS = Object.freeze({ width: 512, height: 128, cells: 16384, digits: 5500 });
export class InputError extends Error {
  constructor(code) { super(code); this.code = code; }
}
export function checkDimensions(w, h) {
  if (!Number.isInteger(w) || !Number.isInteger(h) || w < 1 || h < 1 ||
      w > LIMITS.width || h > LIMITS.height || w*h > LIMITS.cells) throw new InputError('error-size');
}
export function validateRows(rows) {
  if (!Array.isArray(rows) || !rows.length || !rows.every(r => typeof r === 'string')) throw new InputError('error-rows');
  const h = rows.length, w = rows[0].length;
  checkDimensions(w, h);
  if (!rows.every(r => r.length === w && /^[01]+$/.test(r))) throw new InputError('error-rows');
  return { w, h };
}
export function parseRows(text) {
  if (typeof text !== 'string' || text.length > 100000) throw new InputError('error-rows');
  const rows = text.trim().split(/\r?\n/).map(r => r.trim().replaceAll('.', '0').replaceAll('#', '1'));
  validateRows(rows); return rows;
}
export function encode(rows) {
  const {w, h} = validateRows(rows);
  let n = 0n;
  for (let top = 0; top < h; top++) for (let i = 0; i < w; i++) {
    if (rows[top][i] === '1') n |= 1n << BigInt(h*i + h-1-top);
  }
  return { n, k: BigInt(h)*n, w, h };
}
export function parseDecimal(text) {
  if (typeof text !== 'string') throw new InputError('error-number');
  const value = text.trim();
  if (!/^[0-9]+$/.test(value) || value.length > LIMITS.digits) throw new InputError('error-number');
  return BigInt(value);
}
export function decode(k, w, h) {
  checkDimensions(w, h);
  if (typeof k !== 'bigint' || k < 0n || k.toString().length > LIMITS.digits) throw new InputError('error-number');
  if (k % BigInt(h) !== 0n) throw new InputError('error-alignment');
  const n = k / BigInt(h), rows = [];
  for (let j = h-1; j >= 0; j--) {
    let row = '';
    for (let i=0; i<w; i++) row += ((n >> BigInt(h*i+j)) & 1n).toString();
    rows.push(row);
  }
  return rows;
}
export function displayRows(rows, orientation = 'cartesian') {
  validateRows(rows);
  if (orientation === 'cartesian') return [...rows];
  if (orientation === 'historical') return [...rows].reverse().map(r => [...r].reverse().join(''));
  throw new InputError('error-manifest');
}
export function repeatedK(k, w, h) {
  decode(k,w,h);
  return k + BigInt(h)*(1n << BigInt(w*h));
}
export function canonicalText(rows) {
  const {w,h} = validateRows(rows);
  return `tupper-bitmap-v1\n${w} ${h}\n${rows.join('\n')}\n`;
}
export async function digest(rows) {
  if (!globalThis.crypto?.subtle) throw new InputError('error-crypto');
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalText(rows)));
  return Array.from(new Uint8Array(bytes), b => b.toString(16).padStart(2,'0')).join('');
}
export function formulaLatex(h, variant = 'tupper') {
  // h is already limited by the caller. Mirrors Python's generator, not eval().
  if (!Number.isInteger(h) || h < 1 || h > 4096) throw new InputError('error-size');
  const q = `\\left\\lfloor\\frac{y}{${h}}\\right\\rfloor`;
  const exponent = `${h}\\lfloor x\\rfloor+\\operatorname{mod}(\\lfloor y\\rfloor,${h})`;
  if (variant === 'tupper') return `\\frac{1}{2}<\\left\\lfloor\\operatorname{mod}\\left(${q}2^{-${h}\\lfloor x\\rfloor-\\operatorname{mod}(\\lfloor y\\rfloor,${h})},2\\right)\\right\\rfloor`;
  if (variant === 'bit') return `\\frac{1}{2}<\\operatorname{mod}\\left(\\left\\lfloor\\frac{${q}}{2^{${exponent}}}\\right\\rfloor,2\\right)`;
  throw new InputError('error-manifest');
}
export async function manifest(rows, orientation='cartesian', variant='tupper') {
  const {n,k,w,h} = encode(rows);
  displayRows(rows, orientation);
  return { schema:'tupper-experiment/v1', width:w, height:h, encoding:'column-major-bottom-up',
    rows:[...rows], N:n.toString(), k:k.toString(), canonical:true, display_orientation:orientation,
    formula_variant:variant, formula_latex:formulaLatex(h,variant),
    domain:{x:[0,w],y_relative_to_k:[0,h],endpoints:'left-closed-right-open'},
    bitmap_sha256:await digest(rows), source:{kind:'browser-bitmap',claim:'exact finite binary mask'},
    generator:{name:'tupper-formula-web',version:'1.0.0'} };
}
export async function validateManifest(data) {
  try {
    if (!data || data.schema !== 'tupper-experiment/v1' || data.encoding !== 'column-major-bottom-up' || data.canonical !== true) throw new Error();
    const {n,k,w,h} = encode(data.rows);
    if (data.width !== w || data.height !== h || parseDecimal(data.N)!==n || parseDecimal(data.k)!==k) throw new Error();
    if (data.formula_latex !== formulaLatex(h,data.formula_variant)) throw new Error();
    displayRows(data.rows,data.display_orientation);
    const d = data.domain;
    if (!d || d.endpoints !== 'left-closed-right-open' || JSON.stringify(d.x)!==JSON.stringify([0,w]) || JSON.stringify(d.y_relative_to_k)!==JSON.stringify([0,h])) throw new Error();
    if (data.bitmap_sha256 !== await digest(data.rows)) throw new Error();
    return [...data.rows];
  } catch (e) {
    if (e?.code === 'error-crypto') throw e;
    throw new InputError('error-manifest');
  }
}
export function svg(rows, orientation='cartesian') {
  const {w,h} = validateRows(rows);
  let path='';
  displayRows(rows,orientation).forEach((row,y)=>[...row].forEach((bit,x)=>{
    if (bit==='1') path+=`M${x},${y}h1v1h-1z`;
  }));
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w*8}" height="${h*8}" viewBox="0 0 ${w} ${h}" role="img"><title>Tupper-Formula bitmap</title><desc>${w} by ${h}; display ${orientation}; canonical data is separate.</desc><rect width="${w}" height="${h}" fill="white"/><path fill="#192d3f" shape-rendering="crispEdges" d="${path}"/></svg>`;
}
export function pbm(rows) {
  const {w,h}=validateRows(rows);
  return `P1\n# canonical rows top-to-bottom; 1=ink\n${w} ${h}\n${rows.map(r=>[...r].join(' ')).join('\n')}\n`;
}
