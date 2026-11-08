"""Task-local, offline integrity checks; not publication or accelerator certification."""
import ast
import hashlib
import json
from pathlib import Path
import re

import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text())


def main():
    required = ['research.md', 'claims.json', 'proposed-insertions.md',
                'independent_calculations.py', 'calculations.json', 'sources.md',
                'figure-plan.md', 'figures/manifest.json', 'figures/QA.md', 'STATUS.md']
    for name in required:
        assert (ROOT / name).is_file() and (ROOT / name).stat().st_size > 0, name
    claims = load('claims.json')
    sources = {s['source_id']: s for s in claims['sources']}
    ids = {c['claim_id'] for c in claims['claims']}
    assert len(ids) == len(claims['claims'])
    for sid, source in sources.items():
        raw = ROOT / 'evidence' / (sid + '.raw')
        assert hashlib.sha256(raw.read_bytes()).hexdigest() == source['sha256'], sid
        text = (ROOT / source['text_path']).read_text()
        for excerpt in source['excerpts']:
            assert excerpt['quote'] in text, (sid, excerpt['needle'])
        assert source['url'] and source['retrieved_at']
    prose = (ROOT / 'proposed-insertions.md').read_text()
    prose_anchors = set(re.findall(r'^#{1,6} (CCL-T\d+[a-z]?)\b', prose, re.M))
    for claim in claims['claims']:
        assert set(claim['sources']) <= sources.keys(), claim['claim_id']
        assert set(claim['candidate_anchors']) <= prose_anchors, claim['claim_id']
    for name in ['research.md', 'proposed-insertions.md']:
        text = (ROOT / name).read_text()
        refs = set(re.findall(r'\[([a-z][a-z0-9-]+)\]', text))
        assert refs <= sources.keys(), (name, refs - sources.keys())
        # Tables must not silently become literal pipes in pandoc.
        rows = text.splitlines()
        for index, row in enumerate(rows):
            if re.fullmatch(r'\|(?:\s*:?-+:?\s*\|)+', row.strip()):
                columns = row.count('|')
                assert index > 0 and rows[index - 1].count('|') == columns, name
                for following in rows[index + 1:]:
                    if not following.startswith('|'):
                        break
                    assert following.count('|') == columns, (name, following)
    figures = load('figures/manifest.json')
    figure_results = []
    for figure in figures['figures']:
        assert set(figure['related_prose_anchors']) <= prose_anchors
        assert set(figure['claim_ids']) <= ids
        assert set(figure['evidence_ids']) <= sources.keys()
        assert figure['id'].split('-')[0] + '-' + figure['id'].split('-')[1] in prose
        assert figure['caption'] and figure['alt_text'] and figures['reproduction_command']
        for key in ['svg', 'pdf', 'png', 'grayscale_png', 'actual_size_preview']:
            name = figure[key]
            path = (ROOT / name).resolve()
            assert ROOT in path.parents and path.is_file(), path
        assert not figure['geometry_failures']
        image = Image.open(ROOT / figure['png'])
        assert list(image.size) == figure['raster_pixels']
        assert abs(image.size[0] / 300 - figure['width_in']) < .005
        assert hashlib.sha256((ROOT / figure['png']).read_bytes()).hexdigest() == figure['png_sha256']
        assert Image.open(ROOT / figure['grayscale_png']).mode == 'L'
        pdf = pymupdf.open(ROOT / figure['pdf'])
        assert len(pdf) == 1 and abs(pdf[0].rect.width - 439.2) < .01
        spans = [s for b in pdf[0].get_text('dict')['blocks'] if 'lines' in b
                 for line in b['lines'] for s in line['spans']]
        minimum = min(s['size'] for s in spans)
        assert minimum >= 9.49
        figure_results.append({'id': figure['id'], 'pixels': list(image.size),
                               'width_pt': pdf[0].rect.width, 'minimum_pdf_font_pt': minimum})
    tree = ast.parse((ROOT / 'independent_calculations.py').read_text())
    test_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name.startswith('test_')]
    result = {
        'status': 'PASS — offline artifact integrity only',
        'claims': len(ids), 'cited_sources': len(sources),
        'recorded_failed_requests': len(claims['failed_requests']),
        'source_raw_sha256_and_exact_quotes': 'PASS',
        'prose_source_and_claim_anchor_links': 'PASS',
        'markdown_table_column_counts': 'PASS',
        'proposed_english_word_count': len(re.findall(r"\b[\w'-]+\b", prose)),
        'cpu_tests_available': test_names,
        'figures': figure_results,
        'publication_gate': 'PENDING parent integration and complete rendered-proof inspection',
        'measurements': 'No accelerator or network execution; analytical CPU checks only',
    }
    (ROOT / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
