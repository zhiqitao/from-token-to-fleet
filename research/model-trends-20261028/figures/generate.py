#!/usr/bin/env python3
"""Original mechanism figures. Run from any directory; writes only beside this file."""
import datetime
import hashlib
import html
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from typing import Any

import fitz
from PIL import Image, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
W = 610
DPI = 400
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
C = dict(ink='#202020', compute='#3a6ea5', memory='#b02a22',
         control='#8a5700', pale_blue='#eef3f8', pale_red='#fbefee', pale_amber='#fff5df')
CAPTIONS = {
 'mt-1-history-state': 'History recurrence and attention history have different lifetimes. The recurrent layer group updates bounded state, while a separate full-attention layer group retains growing KV history. Three token positions are schematic. Qwen3.8-27B supplies the configuration-backed example, not a measured memory ratio.',
 'mt-2-depth-execution': 'Shared-depth execution reuses weights, not necessarily history state. Distinct iteration caches are shown for the separate-cache case. A true exit omits later work; selecting an earlier representation after all passes does not. The exit after pass 2 is illustrative, not an Ouro performance result.'
}
ALTS = {
 'mt-1-history-state': 'Three token-time columns show equal-sized recurrent-state boxes. Each state feeds the next recurrent update through a routed arrow. Below, a separate full-attention history grows from one to two to three KV cells. The recurrent and attention states belong to different layer groups.',
 'mt-2-depth-execution': 'One shared-weight rail supplies three core invocations. Each invocation has its own red history-cache slot. Below, an actual-stop lane executes passes 1 and 2 and leaves pass 3 unexecuted. A post-hoc lane executes all three passes before selecting the pass-2 representation.'
}

class SVG:
    def __init__(self, height):
        self.h = height
        self.parts = []
        self.labels = []
        self.text('') if False else None
    def rect(self, x, y, w, h, fill='white', stroke=None, dash=False):
        stroke = stroke or C['ink']
        extra = ' stroke-dasharray="5 4"' if dash else ''
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.3"{extra}/>')
    def text(self, x, y, text, size=14, bold=False, anchor='middle', color=None):
        color = color or C['ink']
        font = ImageFont.truetype(BOLD if bold else FONT, size * 10)
        bbox = font.getbbox(text)
        width = font.getlength(text) / 10
        left = x - width / 2 if anchor == 'middle' else x if anchor == 'start' else x - width
        # Pillow bbox is relative to the default ascender anchor, not baseline.
        baseline_box = font.getbbox(text, anchor='ls')
        bounds = [left, y + baseline_box[1] / 10, left + width, y + baseline_box[3] / 10]
        assert min(bounds[0], bounds[1]) >= 3, (text, bounds)
        assert bounds[2] <= W - 3 and bounds[3] <= self.h - 3, (text, bounds)
        assert size * 72 / 100 >= 9, (text, size)
        self.labels.append(dict(text=text, bounds=bounds, size_pt=size * .72))
        weight = 'bold' if bold else 'normal'
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{html.escape(text)}</text>')
    def arrow(self, points, color=None, dash=False, head=True):
        color = color or C['ink']
        end = ' marker-end="url(#arrow)"' if head else ''
        extra = ' stroke-dasharray="4 4"' if dash else ''
        coords = ' '.join(f'{x},{y}' for x, y in points)
        self.parts.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linejoin="round"{end}{extra}/>')
    def box(self, x, y, w, h, lines, fill, stroke, size=14):
        self.rect(x, y, w, h, fill, stroke)
        base = y + h / 2 - (len(lines) - 1) * 9 + 5
        for i, line in enumerate(lines):
            font = ImageFont.truetype(FONT, size * 10)
            assert font.getlength(line) / 10 < w - 12, (line, w)
            self.text(x + w / 2, base + i * 18, line, size=size)
    def write(self, name):
        desc = html.escape(ALTS[name])
        document = f'''<svg xmlns="http://www.w3.org/2000/svg" width="6.1in" height="{self.h/100}in" viewBox="0 0 610 {self.h}" role="img" aria-labelledby="title desc">
<title id="title">{name}</title><desc id="desc">{desc}</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker></defs>
<rect width="610" height="{self.h}" fill="white"/>
<g font-family="DejaVu Sans">{''.join(self.parts)}</g></svg>'''
        path = ROOT / f'{name}.svg'
        path.write_text(document)
        ET.parse(path)
        return self.labels


def history():
    s = SVG(395)
    s.text(305, 25, 'Hybrid history: two state lifetimes', 17, True)
    s.text(305, 49, 'Schematic token snapshots; not a performance comparison', 13)
    for i, x in enumerate([130, 310, 490], 1):
        s.text(x, 81, f'token t{i}', 14, True)
        s.arrow([(x, 91), (x, 111)])
        s.box(x-70, 114, 140, 40, ['recurrent update'], C['pale_blue'], C['compute'], 13)
        s.arrow([(x, 155), (x, 180)])
        s.box(x-70, 184, 140, 44, [f'state after t{i}', 'fixed-size state'], C['pale_red'], C['memory'], 13)
        if i < 3:
            # State from the previous token enters the next update, not its output.
            s.arrow([(x+71, 206), (x+90, 206), (x+90, 134), (x+107, 134)])
        group_left = x - (i * 42 - 4) / 2
        for j in range(i):
            s.box(group_left+j*42, 285, 38, 34, [f'KV{j+1}'], C['pale_red'], C['memory'], 13)
        s.text(x, 342, f'{i} cached token' + ('s' if i > 1 else ''), 13)
    s.text(305, 248, 'Successive state snapshots, not jointly retained history', 13)
    s.text(305, 272, 'Full-attention layers: growing key/value (KV) history', 14, True)
    s.text(305, 365, 'Recurrent updates compute; state and KV boxes store', 13)
    s.text(305, 386, 'Arrows = token input / state flow; snapshots are schematic', 13)
    return s


def depth():
    s = SVG(454)
    s.text(305, 25, 'Shared weights do not remove executed work', 17, True)
    s.box(80, 48, 450, 30, ['one shared core weight set'], '#eef3f8', C['compute'], 14)
    for i, x in enumerate([130, 310, 490], 1):
        s.arrow([(x, 78), (x, 105)], dash=True)
        s.box(x-65, 109, 130, 36, [f'core pass {i}'], C['pale_blue'], C['compute'])
        if i < 3:
            s.arrow([(x+66, 127), (x+112, 127)])
        s.arrow([(x, 147), (x, 171)])
        s.box(x-65, 175, 130, 40, [f'iteration {i}', 'history cache'], C['pale_red'], C['memory'], 13)
    s.text(305, 240, 'Separate iteration caches shown; sharing is not automatic', 13)
    s.text(305, 270, 'Exit after pass 2: two different runtime paths', 14, True)
    # Deliberately separate decision paths: the rightmost node is omitted only above.
    s.text(16, 304, 'Actual stop', 13, True, 'start')
    s.text(16, 359, 'Post-hoc', 13, True, 'start')
    s.text(16, 377, 'selection', 13, True, 'start')
    for y in [287, 349]:
        for i, x in enumerate([160, 275, 390], 1):
            omitted = y == 287 and i == 3
            if omitted:
                s.rect(x, y, 80, 31, 'white', '#555555', True)
                s.text(x+40, y+21, f'pass {i}', 13, color='#555555')
            else:
                s.box(x, y, 80, 31, [f'pass {i}'], C['pale_blue'], C['compute'], 13)
        s.arrow([(241, y+15), (272, y+15)])
    s.arrow([(356, 364), (387, 364)])
    s.text(430, 338, 'not executed', 13)
    s.box(492, 287, 103, 31, ['exit'], C['pale_amber'], C['control'], 13)
    s.arrow([(355, 302), (374, 302), (374, 280), (543, 280), (543, 285)], C['control'])
    s.box(492, 349, 103, 42, ['select pass 2', 'after pass 3'], C['pale_amber'], C['control'], 13)
    s.arrow([(471, 364), (489, 364)], C['control'])
    s.text(305, 408, 'Dashed arrows = weight reuse; dashed box = not executed', 13)
    s.text(305, 427, 'Solid arrows = flow; labeled boxes mark exit / selection', 13)
    s.text(305, 446, 'Illustrative exit index; no latency or quality result', 13)
    return s


def proof(pdf, name, height):
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    left = 1.2 * 72
    width = 6.1 * 72
    page.insert_text((left, 57), 'RESEARCH PLACEMENT PROOF — NOT THE BOOK', fontname='helv', fontsize=10)
    page.insert_text((left, 83), 'US Letter; source artwork at 6.1-inch text width', fontname='helv', fontsize=10)
    source = fitz.open(pdf)
    rect = fitz.Rect(left, 110, left + width, 110 + height * .72)
    page.show_pdf_page(rect, source, 0)
    remaining = page.insert_textbox(fitz.Rect(left, rect.y1+12, left+width, rect.y1+90), CAPTIONS[name], fontname='helv', fontsize=10, lineheight=1.3)
    assert remaining >= 0, ('caption overflow', name, remaining)
    out = ROOT / f'{name}-letter-proof.pdf'
    doc.save(out)
    page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(ROOT / f'{name}-letter-proof.png')
    source.close()
    doc.close()


def main():
    assert Path(FONT).is_file() and Path(BOLD).is_file()
    data: dict[str, Any] = dict(kind='DERIVED_NOT_MEASURED', full_attention_layers=16, kv_heads=4,
                head_dimension=256, kv_bytes_per_element=2, tokens=[131072,262144])
    per_token = 2 * data['full_attention_layers'] * data['kv_heads'] * data['head_dimension'] * data['kv_bytes_per_element']
    data['bytes_per_token'] = per_token
    data['full_attention_component_GiB'] = {str(n): per_token*n/2**30 for n in data['tokens']}
    example: dict[str, Any] = dict(label='ILLUSTRATIVE_NOT_MEASURED', baseline_core_passes=4, stopped_core_passes=3, fixed_work_C=1, core_work_F=2)
    example['baseline_work'] = example['fixed_work_C'] + example['baseline_core_passes'] * example['core_work_F']
    example['stopped_work'] = example['fixed_work_C'] + example['stopped_core_passes'] * example['core_work_F']
    example['core_only_reduction'] = 1 - example['stopped_core_passes'] / example['baseline_core_passes']
    example['total_work_reduction'] = 1 - example['stopped_work'] / example['baseline_work']
    data['adaptive_example'] = example
    assert per_token == 65536 and data['full_attention_component_GiB']['262144'] == 16
    (ROOT/'data.json').write_text(json.dumps(data, indent=2)+'\n')
    manifest = dict(schema_version=1, generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    scope='Original research candidates, not integrated manuscript figures', text_width_in=6.1,
                    layout_evidence=['render/latex/book.tex:7', 'render/latex/book.sty:61', 'design/book-architecture.md:222'],
                    reproduction_command='python3 research/model-trends-20261028/figures/generate.py',
                    dependencies=['Python 3', 'Pillow', 'PyMuPDF', 'Inkscape', 'DejaVu Sans'], figures=[])
    checks = []
    for name, obj, ids, anchor in [
        ('mt-1-history-state', history(), ['Q02','Q05'], 'B. Memory transfer box'),
        ('mt-2-depth-execution', depth(), ['R01','R02','R03','R04','R05'], 'A. A stopping rule is not yet a runtime saving')]:
        labels = obj.write(name)
        svg = ROOT/f'{name}.svg'
        png = ROOT/f'{name}.png'
        pdf = ROOT/f'{name}.pdf'
        subprocess.run(['inkscape',str(svg),'--export-type=png',f'--export-filename={png}',f'--export-dpi={DPI}'],check=True,capture_output=True)
        subprocess.run(['inkscape',str(svg),'--export-type=pdf',f'--export-filename={pdf}'],check=True,capture_output=True)
        im = Image.open(png)
        assert im.width == 2440 and abs(im.height-obj.h*4) <= 1, im.size
        im.save(png, dpi=(DPI,DPI))
        ImageOps.grayscale(im).save(ROOT/f'{name}-grayscale.png', dpi=(DPI,DPI))
        im.crop((120, 280, 2320, min(im.height,1030))).save(ROOT/f'{name}-detail-top.png')
        im.crop((30, 1010, 2410, im.height)).save(ROOT/f'{name}-detail-bottom.png')
        proof(pdf, name, obj.h)
        # Distinct text labels may not intersect, even if an SVG renderer accepts them.
        collisions=[]
        for a, first in enumerate(labels):
            x0,y0,x1,y1=first['bounds']
            for second in labels[a+1:]:
                u0,v0,u1,v1=second['bounds']
                if min(x1,u1)-max(x0,u0)>0.5 and min(y1,v1)-max(y0,v0)>0.5:
                    collisions.append([first['text'],second['text']])
        assert not collisions, collisions
        # All text is dark on white/pale fill: test the worst background, not the hue labels.
        checks.append(dict(id=name, png_pixels=list(im.size), effective_ppi=im.width/6.1,
                           width_in=6.1, height_in=obj.h/100, min_font_pt=min(x['size_pt'] for x in labels),
                           label_count=len(labels), label_bounds='PASS', text_collisions=collisions,
                           pdf_pages=len(fitz.open(pdf)), labels=labels))
        manifest['figures'].append(dict(id=name, source=f'figures/{name}.svg', generator='figures/generate.py',
            data='figures/data.json', png=f'figures/{name}.png', vector_pdf=f'figures/{name}.pdf',
            grayscale=f'figures/{name}-grayscale.png', placement_proof=f'figures/{name}-letter-proof.pdf',
            detail_crops=[f'figures/{name}-detail-top.png',f'figures/{name}-detail-bottom.png'],
            intended_width_in=6.1, intended_height_in=obj.h/100, effective_ppi=DPI,
            caption=CAPTIONS[name], alt_text=ALTS[name], related_prose_anchors=[anchor], evidence_claim_ids=ids,
            quantitative_scope='Mechanism schematic, not to scale; no benchmark curves',
            reproduction_command=manifest['reproduction_command']))
    (ROOT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    (ROOT/'geometry-checks.json').write_text(json.dumps(checks, indent=2)+'\n')
    print(json.dumps({x['id']:{k:v for k,v in x.items() if k!='labels'} for x in checks},indent=2))

if __name__ == '__main__':
    main()
