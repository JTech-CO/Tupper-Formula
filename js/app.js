import * as core from './core.js';
import {populateEquation,dynamicRecord} from './math.js';

const $=id=>document.getElementById(id);
let ui, content, equations, presets;
let lang='en';
let rows=['010','101','111','101','101'];
let orientation='cartesian', variant='tupper', selected={i:1,j:4};
let drawing=false, paintValue='1', lastPaint='', repeatValue='', lastStatus=null;
let geometry={cell:28,w:3,h:5,dpr:1};
const t=key=>ui?.[lang]?.[key] ?? key;
function status(key,kind='info') {
  lastStatus=key?{key,kind}:null;
  $('lab-status').textContent=key?t(key):'';
  $('lab-status').className=`lab-status ${kind}`;
}
function error(e) { status(e?.code || 'error-manifest','error'); }
function escapeHTML(s) { return s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

async function copy(text,button) {
  let success=false;
  try { if (navigator.clipboard?.writeText) {await navigator.clipboard.writeText(text);success=true;} } catch {}
  if (!success) {
    const ta=document.createElement('textarea');ta.value=text;ta.className='clipboard-helper';document.body.append(ta);
    ta.select();try {success=document.execCommand('copy');} catch {}ta.remove();
  }
  if (success) {
    $('announcer').textContent=t('copied');
    if (button) {const before=button.textContent;button.textContent=t('copied');setTimeout(()=>{if(button.isConnected) button.textContent=button.dataset.copyLatex!==undefined?t('copy-latex'):button.dataset.i18n?t(button.dataset.i18n):before;},1100);}
  } else {
    $('manual-copy-text').value=text;$('copy-dialog').showModal();$('manual-copy-text').select();
  }
}
function download(text,filename,mime) {
  const url=URL.createObjectURL(new Blob([text],{type:mime}));
  const a=document.createElement('a');a.href=url;a.download=filename;a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function setLanguage(next,updateURL=true) {
  lang=next==='ko'?'ko':'en';document.documentElement.lang=lang;
  document.querySelectorAll('[data-content]').forEach(el=>{el.innerHTML=content[lang][el.dataset.content];});
  document.querySelectorAll('[data-i18n]').forEach(el=>el.textContent=t(el.dataset.i18n));
  document.querySelectorAll('[data-i18n-aria]').forEach(el=>el.setAttribute('aria-label',t(el.dataset.i18nAria)));
  document.querySelectorAll('[data-lang]').forEach(el=>el.setAttribute('aria-pressed',String(el.dataset.lang===lang)));
  document.title=lang==='ko'?'Tupper-Formula | 자기 이미지를 그리는 공식':'Tupper-Formula | A formula becomes its own image';
  try {localStorage.setItem('tupper-language',lang);} catch {}
  if (updateURL) {try {const url=new URL(location.href);url.searchParams.set('lang',lang);history.replaceState(null,'',url);} catch {}}
  document.querySelectorAll('[data-readme-link]').forEach(el=>el.href=lang==='ko'?'./README-KR.md':'./README.md');
  $('bitmap-canvas').setAttribute('aria-label',t('editable-mask'));
  document.querySelector('.historical-figure img').alt=t('historical-alt');
  document.querySelectorAll('[data-equation]').forEach(el=>populateEquation(el,equations[el.dataset.equation],t));
  const chosen=$('preset').value;
  $('preset').replaceChildren(...presets.map(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=`${p.label[lang]} · ${p.manifest.width} × ${p.manifest.height}`;return o;}));
  if (presets.some(p=>p.id===chosen)) $('preset').value=chosen;
  if (lastStatus) status(lastStatus.key,lastStatus.kind);
  render();
  observeSections();
}
function render() {
  const {n,k,w,h}=core.encode(rows);
  selected.i=Math.min(w-1,Math.max(0,selected.i));selected.j=Math.min(h-1,Math.max(0,selected.j));
  $('grid-width').value=w;$('grid-height').value=h;
  $('orientation').value=orientation;
  $('cell-x').value=selected.i;$('cell-x').max=w-1;
  $('cell-j').value=selected.j;$('cell-j').max=h-1;
  $('rows-input').value=rows.join('\n');$('k-output').value=k.toString();
  $('capacity').textContent=`${w*h} ${t('bits-unit')}`;
  $('integer-bits').textContent=n===0n?'0':String(n.toString(2).length);
  $('k-digits').textContent=String(k.toString().length);
  const decoded=core.decode(k,w,h);
  const mismatch=rows.reduce((s,row,r)=>s+[...row].reduce((a,b,c)=>a+Number(b!==decoded[r][c]),0),0);
  $('mismatches').textContent=String(mismatch);
  $('match-badge').textContent=t(mismatch?'failed-match':'exact-match');
  $('decoded-preview').src=URL.createObjectURL(new Blob([core.svg(decoded,orientation)],{type:'image/svg+xml'}));
  const preview=$('decoded-preview');
  if(preview.dataset.lastUrl) URL.revokeObjectURL(preview.dataset.lastUrl);
  preview.dataset.lastUrl=preview.src;
  preview.alt=`${t('decoded-mask')}: ${w} × ${h}`;
  const index=h*selected.i+selected.j, bit=Number((n >> BigInt(index))&1n);
  $('cell-inspection').textContent=`(i, j) = (${selected.i}, ${selected.j}) · ${t('bit-index')}: ${index} · ${t('bit-value')}: ${bit}`;
  const cellTex=`b_{${selected.i},${selected.j}}=\\left\\lfloor\\frac{N}{2^{${index}}}\\right\\rfloor\\bmod 2=${bit}`;
  $('copy-cell').dataset.copyLatex=cellTex;$('copy-cell').textContent=t('copy-latex');
  populateEquation($('dynamic-equation'),dynamicRecord(equations,h,variant),t);
  drawCanvas();
  $('plot-axes').textContent=orientation==='cartesian'?`x: 0 → ${w}  ·  y: k+${h} ↓ k`:`x: ${w} → 0  ·  y: k ↓ k+${h}`;
  $('plot-dimensions').textContent=`${w} × ${h}`;
  if(repeatValue) {$('repeat-output').value='';repeatValue='';}
}
function drawCanvas() {
  const {w,h}=core.validateRows(rows);
  const available=Math.max(200,$('canvas-area').clientWidth-24);
  const cell=Math.min(30,Math.max(2,Math.floor(Math.min(available/w,300/h))));
  const dpr=Math.min(window.devicePixelRatio||1,2);
  const canvas=$('bitmap-canvas');canvas.width=Math.round(w*cell*dpr);canvas.height=Math.round(h*cell*dpr);
  canvas.style.width=`${w*cell}px`;canvas.style.height=`${h*cell}px`;
  const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);ctx.fillStyle='#ffffff';ctx.fillRect(0,0,w*cell,h*cell);
  core.displayRows(rows,orientation).forEach((row,r)=>[...row].forEach((bit,i)=>{
    if(bit==='1'){ctx.fillStyle='#20394b';ctx.fillRect(i*cell,r*cell,cell,cell);}
  }));
  if(cell>=8){ctx.beginPath();ctx.strokeStyle='#cbd4dc';ctx.lineWidth=.5;
    for(let i=0;i<=w;i++){ctx.moveTo(i*cell,0);ctx.lineTo(i*cell,h*cell);}for(let j=0;j<=h;j++){ctx.moveTo(0,j*cell);ctx.lineTo(w*cell,j*cell);}ctx.stroke();}
  const sx=orientation==='cartesian'?selected.i:w-1-selected.i;
  const sy=orientation==='cartesian'?h-1-selected.j:selected.j;
  ctx.strokeStyle='#a24d25';ctx.lineWidth=Math.min(2,cell/2);ctx.strokeRect(sx*cell+.6,sy*cell+.6,Math.max(.8,cell-1.2),Math.max(.8,cell-1.2));
  geometry={cell,w,h,dpr};
}
function fromPointer(event) {
  const rect=$('bitmap-canvas').getBoundingClientRect(),{w,h}=geometry;
  const i=Math.floor((event.clientX-rect.left)/rect.width*w),top=Math.floor((event.clientY-rect.top)/rect.height*h);
  if(i<0||i>=w||top<0||top>=h)return null;
  return orientation==='cartesian'?{i,j:h-1-top}:{i:w-1-i,j:top};
}
function paint(point,value) {
  if(!point)return;
  const {i,j}=point, top=rows.length-1-j;
  rows[top]=rows[top].slice(0,i)+value+rows[top].slice(i+1);
  selected={i,j};variant='tupper';status(null);render();
}
function pickPreset(id) {
  const p=presets.find(p=>p.id===id)??presets[0];
  rows=[...p.manifest.rows];orientation=p.manifest.display_orientation;variant=p.manifest.formula_variant;
  selected={i:0,j:0};status(null);render();
}
let navFrame = 0;
function observeSections() {
  const sections = [...document.querySelectorAll('main section[id]')];
  let active = sections[0];
  for (const section of sections) {
    if (section.getBoundingClientRect().top <= 145) active = section;
  }
  if (active) document.querySelectorAll('.contents a').forEach(a => {
    a.classList.toggle('active', a.hash === `#${active.id}`);
    if (a.hash === `#${active.id}`) a.setAttribute('aria-current', 'location');
    else a.removeAttribute('aria-current');
  });
}
window.addEventListener('scroll', () => {
  if (navFrame) return;
  navFrame = requestAnimationFrame(() => { observeSections(); navFrame = 0; });
}, {passive:true});
function installEvents() {
  document.addEventListener('click',async event=>{
    const latex=event.target.closest('[data-copy-latex]');if(latex){await copy(latex.dataset.copyLatex,latex);return;}
    const code=event.target.closest('[data-copy-code]');if(code){await copy($(code.dataset.copyCode).textContent,code);return;}
    const language=event.target.closest('[data-lang]');if(language)setLanguage(language.dataset.lang);
  });
  $('preset').addEventListener('change',e=>pickPreset(e.target.value));
  $('orientation').addEventListener('change',e=>{orientation=e.target.value;render();});
  $('new-grid').addEventListener('click',()=>{try {
    const w=Number($('grid-width').value),h=Number($('grid-height').value);core.checkDimensions(w,h);
    rows=Array(h).fill('0'.repeat(w));selected={i:0,j:0};variant='tupper';orientation='cartesian';status(null);render();
  }catch(e){error(e);}});
  $('apply-rows').addEventListener('click',()=>{try{rows=core.parseRows($('rows-input').value);variant='tupper';status(null);render();}catch(e){error(e);}});
  $('toggle-cell').addEventListener('click',()=>{try{
    const i=Number($('cell-x').value),j=Number($('cell-j').value),{w,h}=core.validateRows(rows);
    if(!Number.isInteger(i)||!Number.isInteger(j)||i<0||i>=w||j<0||j>=h)throw new core.InputError('error-size');
    paint({i,j},rows[h-1-j][i]==='1'?'0':'1');
  }catch(e){error(e);}});
  for (const id of ['cell-x','cell-j']) $(id).addEventListener('change',()=>{
    const i=Number($('cell-x').value),j=Number($('cell-j').value),{w,h}=core.validateRows(rows);
    if(Number.isInteger(i)&&Number.isInteger(j)&&i>=0&&i<w&&j>=0&&j<h){selected={i,j};render();}
  });
  const canvas=$('bitmap-canvas');
  canvas.addEventListener('pointerdown',e=>{
    if(e.button!==0)return;const point=fromPointer(e);if(!point)return;
    e.preventDefault();canvas.focus();canvas.setPointerCapture(e.pointerId);drawing=true;
    paintValue=rows[rows.length-1-point.j][point.i]==='1'?'0':'1';lastPaint=`${point.i},${point.j}`;paint(point,paintValue);
  });
  canvas.addEventListener('pointermove',e=>{if(!drawing)return;const point=fromPointer(e);if(point&&`${point.i},${point.j}`!==lastPaint){lastPaint=`${point.i},${point.j}`;paint(point,paintValue);}});
  for (const name of ['pointerup','pointercancel','lostpointercapture']) canvas.addEventListener(name,()=>{drawing=false;lastPaint='';});
  canvas.addEventListener('keydown',e=>{
    if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown',' ','Enter'].includes(e.key))return;
    e.preventDefault();const {w,h}=core.validateRows(rows);
    if(e.key===' '||e.key==='Enter'){paint(selected,rows[h-1-selected.j][selected.i]==='1'?'0':'1');return;}
    let dx=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0;
    let dy=e.key==='ArrowUp'?1:e.key==='ArrowDown'?-1:0;
    if(orientation==='historical'){dx=-dx;dy=-dy;}
    selected.i=Math.min(w-1,Math.max(0,selected.i+dx));selected.j=Math.min(h-1,Math.max(0,selected.j+dy));render();
    $('announcer').textContent=$('cell-inspection').textContent;
  });
  $('copy-k').addEventListener('click',()=>copy($('k-output').value,$('copy-k')));
  $('export-json').addEventListener('click',async()=>{try{
    const result=await core.manifest(rows,orientation,variant);download(JSON.stringify(result,null,2)+'\n','tupper-experiment.json','application/json');
  }catch(e){error(e);}});
  $('export-svg').addEventListener('click',()=>download(core.svg(rows,orientation),'tupper-plot.svg','image/svg+xml'));
  $('export-pbm').addEventListener('click',()=>download(core.pbm(rows),'tupper-mask.pbm','image/x-portable-bitmap'));
  $('import-json').addEventListener('change',async e=>{try{
    const file=e.target.files[0];if(!file)return;if(file.size>1000000)throw new core.InputError('error-file');
    let data;try{data=JSON.parse(await file.text());}catch{throw new core.InputError('error-file');}
    rows=await core.validateManifest(data);orientation=data.display_orientation;variant=data.formula_variant;
    selected={i:0,j:0};render();status('imported');
  }catch(err){error(err);}finally{e.target.value='';}});
  $('decode-k').addEventListener('click',()=>{try{
    const w=Number($('grid-width').value),h=Number($('grid-height').value);
    rows=core.decode(core.parseDecimal($('decode-input').value),w,h);variant='tupper';selected={i:0,j:0};render();status('normalized');
  }catch(e){error(e);}});
  $('next-k').addEventListener('click',()=>{const {k,w,h}=core.encode(rows);repeatValue=core.repeatedK(k,w,h).toString();$('repeat-output').value=repeatValue;});
  $('copy-next').addEventListener('click',()=>{if(repeatValue)copy(repeatValue,$('copy-next'));});
  $('close-copy').addEventListener('click',()=>$('copy-dialog').close());
  window.addEventListener('resize',drawCanvas);
}
async function start() {
  try {
    const urls=['ui','content','formulas','presets'];
    [ui,content,equations,presets]=await Promise.all(urls.map(async name=>{
      const response=await fetch(`./data/${name}.json`);if(!response.ok)throw new Error(name);return response.json();
    }));
    let saved='en';try{saved=localStorage.getItem('tupper-language')||'en';}catch{}
    const query=new URLSearchParams(location.search).get('lang');
    installEvents();setLanguage(query??saved,false);pickPreset('a');$('app-loading').hidden=true;
    $('laboratory').dataset.ready='true';
  } catch(e) {
    console.error('Local application initialization failed',e);
    $('app-loading').textContent='Could not initialize. Run: python -m http.server 8000, then open http://localhost:8000/ (not file://).';
    $('app-loading').classList.add('error');
  }
}
start();
