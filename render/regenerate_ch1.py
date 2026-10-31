#!/usr/bin/env python3
"""Rebuild canonical Fig1.1 with visible connectors and placed font floor.

Fig1.2 has its own source-specific regenerate_ch1_token_travel.py driver.
Neither script changes the shared Archify theme or crop implementation.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NAME = 'fig-1-1-kv-cache'
BODY_PT = 439.2


def main():
    os.chdir(ROOT)
    source = ROOT / 'render/archify' / (NAME + '.json')
    spec = json.loads(source.read_text())
    assert all(c.get('icon') == 'none' for c in spec['components'])
    assert next(c for c in spec['components'] if c['id'] == 'next')['pos'][1] == 398
    result = subprocess.run([
        'node', '/home/ubuntu/tools/archify/archify/bin/archify.mjs', 'deliver',
        'architecture', str(source), str(source.with_name(NAME + '-deliver.html')),
        '--quality', 'showcase', '--json',
    ], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    import gen_archify_min
    assert gen_archify_min.build(NAME)
    # The old 1.18 node masks hid arrowheads. Shorter canonical text permits
    # exact source boxes; INCLUDE_PATHS preserves the outside read-K path.
    os.environ.update(GBOX='1.0', INCLUDE_PATHS='1', FONTBOOST='1.45')
    import crop_archify_viewbox as crop
    html = source.with_name(NAME + '-min.html')
    crop.crop_viewbox(str(html))
    text = html.read_text()
    match = re.search(r'<svg\b.*?</svg>', text, re.S)
    assert match
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    svg = ET.fromstring(match.group())
    # Source-specific supported SVG transformation, persisted here. Do not
    # mutate shared CSS: darken only stored-state node text, including heads.
    for group in svg.iter():
        if group.get('data-node-id') in ('kstate', 'vstate'):
            for node in group.iter():
                if node.tag.rsplit('}', 1)[-1] == 'text':
                    node.set('style', 'fill:#1f2937!important')
    for node in svg.iter():
        if node.tag.rsplit('}', 1)[-1] == 'text':
            value = node.get('font-size', '')
            if re.fullmatch(r'[0-9.]+', value) and float(value) < 12:
                node.set('font-size', '12')
    edges = [n for n in svg.iter() if n.tag.rsplit('}', 1)[-1] == 'path' and n.get('data-edge-id')]
    assert len(edges) == 8 and all(n.get('marker-end') for n in edges)
    assert not any(n.get('data-icon') for n in svg.iter())
    html.write_text(text[:match.start()] + ET.tostring(svg, encoding='unicode') + text[match.end():])
    out = ROOT / 'design/manuscript/chapter-01/figures/fig-01-kv-cache'
    assert crop.render(str(html), str(out.with_suffix('.pdf')), str(out.with_suffix('.png')))
    assert out.with_suffix('.pdf').read_bytes().startswith(b'%PDF-')
    assert out.with_suffix('.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    import pymupdf
    doc = pymupdf.open(out.with_suffix('.pdf'))
    page = doc[0]
    spans = [s for b in page.get_text('dict')['blocks'] if b['type'] == 0 for l in b['lines'] for s in l['spans']]
    placed_min = min(s['size'] for s in spans) * BODY_PT / page.rect.width
    assert placed_min >= 8.0, placed_min
    assert all(label in page.get_text() for label in ('append K/V', 'store K', 'store V', 'read K', 'read V'))
    pix = page.get_pixmap()
    metrics = dict(figure='1.1', points=list(page.rect), min_placed_font_pt=placed_min,
                   svg_edge_count=len(edges), canonical_icons=0,
                   source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   text=page.get_text(), raster_sha256=hashlib.sha256(pix.samples).hexdigest(),
                   pdf_sha256=hashlib.sha256(out.with_suffix('.pdf').read_bytes()).hexdigest())
    print(json.dumps(metrics, ensure_ascii=False))


if __name__ == '__main__':
    main()
