"""Send the user's text-and-figures scope update to six exact live workers."""
import asyncio
import json
import os
from pathlib import Path
import sqlite3
import sys

os.environ['HERMES_HOME'] = '/home/ubuntu/.hermes/profiles/muta'
sys.path.insert(0, '/home/ubuntu/.hermes/hermes-agent')
from hermes_cli.gateway_client import connect_gateway

ROOT = Path(__file__).resolve().parent
DB = '/home/ubuntu/.hermes/profiles/muta/state.db'
TITLES = [
    'Research current model trends',
    'Research Intel GPU/XPU developments for book',
    'Research AWQ, GGUF, MXFP4, NVFP4 quantization',
    'Research diffusion fundamentals and language models',
    'Research Wan video generation serving implications',
    'Compare NCCL and oneCCL with MPI',
]

async def main():
    text = (ROOT / 'work/text_and_figures_addendum.md').read_text()
    conn = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    results = []
    async with connect_gateway() as gateway:
        for title in TITLES:
            row = conn.execute(
                "SELECT id FROM sessions WHERE title=? AND source='oneshot' ORDER BY started_at DESC LIMIT 1",
                (title,),
            ).fetchone()
            if row is None:
                raise RuntimeError(f'Missing exact worker: {title}')
            sid = row[0]
            before = await gateway.rpc('session.resume', session_id=sid)
            was_running = bool(before.get('running'))
            if was_running:
                ack = await gateway.rpc('session.steer', session_id=sid,
                                        execution_generation=before['execution_generation'], text=text)
            else:
                ack = await gateway.rpc('prompt.submit', session_id=sid, text=text,
                                        submission_id='text-and-figures-scope-v1',
                                        queued=True, finite=True, unattended=True)
            after = await gateway.rpc('session.resume', session_id=sid)
            events = await gateway.rpc('session.events.since', session_id=sid,
                                       last_sequence=before['last_sequence'])
            # Read back the exact target. Look in both its live snapshot and subsequent events.
            def contains_exact(value):
                if isinstance(value, str):
                    return text in value
                if isinstance(value, dict):
                    return any(contains_exact(v) for v in value.values())
                if isinstance(value, list):
                    return any(contains_exact(v) for v in value)
                return False
            snapshot_match = contains_exact(after)
            event_match = contains_exact(events)
            result = {
                'title': title, 'session_id': sid,
                'execution_generation': ack.get('execution_generation'),
                'status': ack.get('status'),
                'ack_text_matches': ack.get('text') == text,
                'readback_snapshot_match': snapshot_match,
                'readback_event_match': event_match,
                'running_after': after.get('running'),
            }
            results.append(result)
            (ROOT / 'work/text_and_figures_steering_receipts.json').write_text(
                json.dumps(results, ensure_ascii=False, indent=2) + '\n')
            print(json.dumps(result, ensure_ascii=False), flush=True)
    assert len(results) == 6
    assert all(r['status'] in {'queued', 'started', 'accepted'} for r in results)
    assert all(r['readback_snapshot_match'] or r['readback_event_match'] for r in results)

if __name__ == '__main__':
    asyncio.run(main())
