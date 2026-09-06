"""Browser UI smoke test with explicit http and in-memory modes.

Memory mode is a restricted-environment fallback, not a deployment test. The
clipboard and download receivers are test doubles in both modes; this checks
requested text/files without touching the OS clipboard or download folder.
"""
from __future__ import annotations
import argparse,base64,functools,hashlib,json,re,threading,sys
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from tupper_formula.manifest import verify_manifest

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

BRIDGES=r'''
window.__copied='';window.__downloads=[];
Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.__copied=text;}}});
const nativeURL=URL.createObjectURL.bind(URL);const blobs=new Map();
URL.createObjectURL=blob=>{const url=nativeURL(blob);blobs.set(url,blob);return url;};
const nativeClick=HTMLAnchorElement.prototype.click;
HTMLAnchorElement.prototype.click=function(){
  if(this.download&&blobs.has(this.href)){
    const name=this.download;blobs.get(this.href).text().then(text=>window.__downloads.push({name,text}));
  }else nativeClick.call(this);
};
'''

def memory_source():
    html=(ROOT/'index.html').read_text()
    html=re.sub(r'<link[^>]+>','',html)
    html=re.sub(r'<script[^>]+>.*?</script>','',html,flags=re.S)
    html=html.replace('</head>','<style>'+(ROOT/'css/style.css').read_text()+'</style></head>')
    html=html.replace('./assets/historical.svg','data:image/svg+xml;base64,'+base64.b64encode((ROOT/'assets/historical.svg').read_bytes()).decode())
    core=re.sub(r'^export ','',(ROOT/'js/core.js').read_text(),flags=re.M)
    math=re.sub(r'^export ','',(ROOT/'js/math.js').read_text(),flags=re.M)
    app=re.sub(r'^import .*;\n','',(ROOT/'js/app.js').read_text(),flags=re.M)
    fixtures={f'./data/{n}.json':json.loads((ROOT/f'data/{n}.json').read_text()) for n in ('ui','content','formulas','presets')}
    setup='const FIXTURES='+json.dumps(fixtures)+';'+r'''
window.fetch=async path=>new Response(JSON.stringify(FIXTURES[path]),{status:200});
history.replaceState=()=>{};
window.__shaBridge=false;
if(!globalThis.crypto?.subtle){
  Object.defineProperty(globalThis,'crypto',{value:{subtle:{digest:async(_algorithm,buffer)=>new Uint8Array(await window.__sha256([...new Uint8Array(buffer)])).buffer}}});
  window.__shaBridge=true;
}
'''
    exported='LIMITS,InputError,checkDimensions,validateRows,parseRows,encode,parseDecimal,decode,displayRows,repeatedK,canonicalText,digest,formulaLatex,manifest,validateManifest,svg,pbm'
    script=setup+BRIDGES+'\nconst core=(()=>{'+core+'\nreturn {'+exported+'};})();\n'+math+'\n'+app
    return html,script


def run(mode:str,chromium:str|None=None,screenshots:Path|None=None)->dict:
    from playwright.sync_api import sync_playwright
    server=None;checks=[];errors=[];http_requests=[]
    if mode=='http':
        server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
    def check(name,condition=True):
        if not condition:raise AssertionError(name)
        checks.append(name)
    try:
      with sync_playwright() as playwright:
        options={'headless':True}
        if chromium:options['executable_path']=chromium
        browser=playwright.chromium.launch(**options)
        page=browser.new_page(viewport={'width':1440,'height':1060},device_scale_factor=1)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:http_requests.append({'url':r.url,'status':r.status}))
        if mode=='memory':
            page.expose_function('__sha256',lambda values:list(hashlib.sha256(bytes(values)).digest()))
            html,script=memory_source();page.set_content(html);page.add_script_tag(content=script)
        else:
            page.add_init_script(BRIDGES)
            page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='networkidle')
        page.wait_for_selector('#laboratory[data-ready="true"]')
        check('English initial language',page.locator('html').get_attribute('lang')=='en')
        check('known A offset',page.locator('#k-output').input_value()=='80075')
        check('rendered MathML',page.locator('math').count()>=14)
        if screenshots:
            screenshots.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(screenshots/'desktop-en.png'))
        count=page.locator('[data-copy-latex]').count()
        for i in range(count):
            button=page.locator('[data-copy-latex]').nth(i);expected=button.get_attribute('data-copy-latex')
            check(f'nonempty LaTeX control {i+1}',bool(expected))
            button.evaluate('(el)=>el.click()')
            page.wait_for_function('expected=>window.__copied===expected',arg=expected)
        check('every displayed equation copy handler',count>=15)
        page.locator('[data-lang="ko"]').click()
        check('Korean language toggle',page.locator('html').get_attribute('lang')=='ko')
        check('Korean lab label',page.locator('#new-grid').inner_text()=='빈 격자 만들기')
        if screenshots:
            page.evaluate('window.scrollTo({top:0,behavior:"instant"})');page.screenshot(path=str(screenshots/'desktop-ko.png'))
        presets=json.loads((ROOT/'data/presets.json').read_text())
        for p in presets:
            page.locator('#preset').select_option(p['id'])
            check('preset '+p['id'],page.locator('#k-output').input_value()==p['manifest']['k'])
            check('zero mismatches '+p['id'],page.locator('#mismatches').inner_text()=='0')
        page.locator('#preset').select_option('a')
        page.locator('#orientation').select_option('historical')
        check('orientation preserves canonical k',page.locator('#k-output').input_value()=='80075')
        page.locator('#orientation').select_option('cartesian')
        page.locator('#toggle-cell').click()
        check('numeric cell edit changes k',page.locator('#k-output').input_value()!='80075')
        page.locator('#preset').select_option('a')
        page.locator('#bitmap-canvas').focus();before=page.locator('#k-output').input_value()
        page.keyboard.press('Space')
        check('keyboard pixel edit',page.locator('#k-output').input_value()!=before)
        page.locator('#preset').select_option('a')
        page.locator('.data-tools > summary').click()
        page.locator('#rows-input').fill('10010\n01000\n00101');page.locator('#apply-rows').click()
        check('canonical row editor',page.locator('#grid-width').input_value()=='5' and page.locator('#grid-height').input_value()=='3')
        page.locator('#rows-input').fill('100\n01');page.locator('#apply-rows').click()
        check('invalid rows rejected','error' in page.locator('#lab-status').get_attribute('class'))
        page.locator('#preset').select_option('a')
        page.locator('#decode-input').fill('80076');page.locator('#decode-k').click()
        check('unaligned offset rejected','error' in page.locator('#lab-status').get_attribute('class'))
        page.locator('#decode-input').fill('243915');page.locator('#decode-k').click()
        check('repeated offset normalizes to visible mask',page.locator('#k-output').input_value()=='80075')
        page.locator('#next-k').click()
        check('next occurrence calculation',page.locator('#repeat-output').input_value()=='243915')
        fixture=presets[1]['manifest']
        page.locator('#import-json').set_input_files({'name':'fixture.json','mimeType':'application/json','buffer':json.dumps(fixture).encode()})
        page.wait_for_function('k=>document.getElementById("k-output").value===k',arg=fixture['k'])
        check('valid JSON import')
        bad={**fixture,'k':'1'}
        page.locator('#import-json').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':json.dumps(bad).encode()})
        page.wait_for_function('document.getElementById("lab-status").classList.contains("error")')
        check('tampered JSON rejected')
        page.locator('#export-json').click();page.locator('#export-svg').click();page.locator('#export-pbm').click()
        page.wait_for_function('window.__downloads.length===3')
        downloaded={d['name']:d['text'] for d in page.evaluate('window.__downloads')}
        exported=json.loads(downloaded['tupper-experiment.json'])
        check('browser export verified by Python',verify_manifest(exported,literal=True)['passed'])
        check('SVG export serialization',downloaded['tupper-plot.svg'].startswith('<svg'))
        check('PBM export serialization',downloaded['tupper-mask.pbm'].startswith('P1\n'))
        page.evaluate('navigator.clipboard.writeText=async()=>{throw Error("test denied")};document.execCommand=()=>false;')
        page.locator('#copy-k').click();page.wait_for_selector('#copy-dialog[open]')
        check('manual clipboard fallback',page.locator('#manual-copy-text').input_value()==page.locator('#k-output').input_value())
        page.locator('#close-copy').click()
        page.locator('[data-lang="en"]').click();page.locator('#preset').select_option('a')
        page.locator('#laboratory').scroll_into_view_if_needed();page.wait_for_timeout(100)
        check('sidebar tracks laboratory',page.locator('.contents a.active').get_attribute('href')=='#laboratory')
        if screenshots:page.screenshot(path=str(screenshots/'lab-en.png'))
        page.set_viewport_size({'width':390,'height':844})
        for lang in ('en','ko'):
            page.locator(f'[data-lang="{lang}"]').click()
            for section in ('overview','laboratory','beyond'):
                page.locator('#'+section).scroll_into_view_if_needed()
                check(f'no viewport overflow {lang}/{section}',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
            for preset_id in ('historical','formula'):
                page.locator('#preset').select_option(preset_id)
                page.locator('#laboratory').scroll_into_view_if_needed()
                check(f'large mask no viewport overflow {lang}/{preset_id}',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
                check(f'large mask left edge reachable {lang}/{preset_id}',page.evaluate('document.getElementById("bitmap-canvas").getBoundingClientRect().left>=document.getElementById("canvas-area").getBoundingClientRect().left'))
            page.locator('#preset').select_option('a')
            page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
            if screenshots:page.screenshot(path=str(screenshots/f'mobile-{lang}.png'))
        check('no uncaught page errors',not errors)
        sha_bridge=page.evaluate('Boolean(window.__shaBridge)')
        version=browser.version
        browser.close()
      return {'suite':'browser-ui/v1','passed':True,'mode':mode,'browser':'Chromium','browser_version':version,
              'checks':len(checks),'check_names':checks,'page_errors':errors,
              'static_formula_copy_controls':count,'viewports':[[1440,1060],[390,844]],
              'sha256_test_bridge_used':sha_bridge,
              'test_doubles':['clipboard receiver','download receiver']+(['local JSON fetch','URL history'] if mode=='memory' else []),
              'limits':['No actual OS clipboard or download-folder assertion','No deployed GitHub Pages or social-crawler test','No Firefox/WebKit test']+(['Browser navigation and native ES module graph not exercised; authored modules injected in memory'] if mode=='memory' else []),
              'http_response_count':len(http_requests)}
    finally:
        if server:server.shutdown();server.server_close()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['http','memory'],default='http');p.add_argument('--chromium')
    p.add_argument('--output',type=Path,default=ROOT/'reports/browser-local.json');p.add_argument('--screenshots',type=Path)
    a=p.parse_args()
    try:report=run(a.mode,a.chromium,a.screenshots)
    except Exception as exc:
        report={'suite':'browser-ui/v1','passed':False,'mode':a.mode,'error':str(exc)}
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
        raise
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
