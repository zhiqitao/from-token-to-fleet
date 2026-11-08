"""Public-source checkpoint retriever; writes only this task directory."""
import concurrent.futures
import datetime
import hashlib
import html.parser
import json
from pathlib import Path
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / 'citation-ledger.json'
SOURCES = Path('/home/ubuntu/.hermes/profiles/muta/skills/research/grounded-citations/scripts/sources.py')

class Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
        if tag in ('p', 'div', 'tr', 'h1', 'h2', 'h3', 'li', 'br'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def fetch(item):
    key, url = item
    result = {'key': key, 'url': url, 'retrieved_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    for fetch_url in (url, 'https://r.jina.ai/' + url):
        try:
            request = urllib.request.Request(fetch_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=45) as response:
                data = response.read(); result['resolved_url'] = response.url
                result['last_modified'] = response.headers.get('Last-Modified')
            if data.startswith(b'%PDF'):
                import pymupdf
                doc = pymupdf.open(stream=data, filetype='pdf')
                text = '\n'.join(page.get_text() for page in doc)
                (ROOT / 'sources' / (key + '.pdf')).write_bytes(data)
            else:
                text = data.decode('utf-8', 'replace')
                if '<html' in text[:2000].lower() or '<!doctype' in text[:2000].lower():
                    parser = Text(); parser.feed(text)
                    text = '\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())
            if len(text) < 150 or any(marker in text[:600].lower() for marker in ('access denied', 'just a moment', 'target url returned error', 'page not found')):
                raise ValueError('stub or access wall: ' + text[:100])
            target = ROOT / 'sources' / (key + '.txt'); target.write_text(text)
            result.update(status='FETCHED', path=str(target.relative_to(ROOT)), sha256=hashlib.sha256(data).hexdigest(), chars=len(text), fetch_url=fetch_url)
            return result
        except Exception as error:
            result.setdefault('errors', []).append(str(error))
    result['status'] = 'FAILED'
    return result

if __name__ == '__main__':
    (ROOT / 'sources').mkdir(exist_ok=True)
    batch = json.loads(sys.argv[1])
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(fetch, batch.items()))
    with (ROOT / 'retrievals.jsonl').open('a') as output:
        for result in results:
            if result['status'] == 'FETCHED':
                reg = subprocess.run([sys.executable, str(SOURCES), '--ledger', str(LEDGER), 'add', result['url'], '--title', result['key']], capture_output=True, text=True)
                result['citation_registration'] = reg.stdout.strip()
            output.write(json.dumps(result, ensure_ascii=False) + '\n')
            print(json.dumps(result, ensure_ascii=False))
            if result['status'] == 'FETCHED':
                text = (ROOT / result['path']).read_text()
                print(text[:int(sys.argv[2]) if len(sys.argv)>2 else 1200])
