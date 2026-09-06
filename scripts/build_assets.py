"""Generate an original 1200x630 social card from the exact historical bitmap.

No screenshot from a paper is copied and no font file is distributed. Pillow is
needed only to regenerate the PNG. The SVG stays vector and uses system fonts.
--font/--bold-font may select locally installed fonts; neither is copied.
"""
from __future__ import annotations
import argparse
import json
from html import escape
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def build(font: str | None = None, bold_font: str | None = None) -> None:
    from PIL import Image, ImageDraw, ImageFont
    m = json.loads((ROOT/'examples/historical/experiment.json').read_text())
    rows = [r[::-1] for r in reversed(m['rows'])]
    bg, ink, muted, line = '#fbfaf7', '#152c3b', '#596775', '#cad0d3'
    image = Image.new('RGB', (1200,630), bg)
    d = ImageDraw.Draw(image)
    normal_candidates = [font, '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
                         '/System/Library/Fonts/Supplemental/Georgia.ttf', 'C:/Windows/Fonts/georgia.ttf']
    bold_candidates = [bold_font, '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
                       '/System/Library/Fonts/Supplemental/Georgia Bold.ttf', 'C:/Windows/Fonts/georgiab.ttf']
    def f(size:int, bold:bool=False):
        for name in bold_candidates if bold else normal_candidates:
            if name and Path(name).is_file():return ImageFont.truetype(name,size)
        return ImageFont.load_default(size=size)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><title>Tupper-Formula — reproducible integer mathematics</title><rect width="1200" height="630" fill="{bg}"/>']
    def text(x,y,value,size=24,bold=False,fill=ink):
        d.text((x,y),value,font=f(size,bold),fill=fill,anchor='lt')
        svg.append(f'<text x="{x}" y="{y+size*.85}" font-family="Georgia,serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{fill}">{escape(value)}</text>')
    def rule(y):
        d.line((66,y,1134,y),fill=line,width=1)
        svg.append(f'<path d="M66 {y}H1134" stroke="{line}"/>')
    text(68,42,'RESEARCH NOTE   /   MATHEMATICS + CODE',19,False,muted)
    text(68,91,'Tupper-Formula',72,True)
    text(70,181,'A formula becomes its own image.',30)
    text(70,229,'Exact integers. Explicit coordinates. Reproducible experiments.',21,False,muted)
    rule(281)
    text(70,305,'106 × 17 BINARY CELLS',17,False,muted)
    # 10 px per cell; the mask itself, not a fonts-based approximation.
    for y,row in enumerate(rows):
        for x,bit in enumerate(row):
            if bit=='1':
                px,py=70+10*x,352+10*y
                d.rectangle((px,py,px+9,py+9),fill=ink)
                svg.append(f'<path d="M{px} {py}h10v10h-10z" fill="{ink}"/>')
    rule(551)
    text(70,578,'PYTHON  /  INTERACTIVE LAB  /  EN · 한국어'.replace('한국어','KO'),18,False,muted)
    text(945,578,'k = H × N',23,True)
    svg.append('</svg>')
    (ROOT/'assets/og-image.svg').write_text(''.join(svg)+'\n',encoding='utf-8')
    image.save(ROOT/'assets/og-image.png',optimize=True)
    print('Built assets/og-image.png (1200x630) and assets/og-image.svg')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font');parser.add_argument('--bold-font')
    a=parser.parse_args();build(a.font,a.bold_font)
