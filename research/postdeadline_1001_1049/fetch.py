"""Fetch all twenty formal matches since the preceding live-status check."""
import gzip
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import harvest
import kg

IDS = [116275122, 116220727, 116159587, 116237200,
       116262342, 116259129, 116189312, 116164792,
       116258579, 116279074]

def main():
    metas = {m['id']: m for sid in (56649860, 56713491) for m in harvest.episode_meta(sid)}
    out = HERE / 'newgames.jsonl.gz'
    if not out.exists():
        with gzip.open(out, 'wt') as f:
            for rec in harvest.load(HERE / 'diagnosis10.jsonl.gz'):
                f.write(json.dumps(rec, ensure_ascii=False, separators=(',', ':'))+'\n')
    have = {r['id'] for r in harvest.load(out)}
    api = kg.api()
    ids = sorted(eid for eid,m in metas.items() if m['end'] >= '2026-10-01T04:38:45')
    for eid in ids:
        if eid in have:
            continue
        rec = harvest.record(eid, metas[eid], api)
        with gzip.open(out, 'at') as f:
            f.write(json.dumps(rec, ensure_ascii=False, separators=(',', ':'))+'\n')
        print(eid, rec['teams'], rec['rewards'], flush=True)
        time.sleep(1.5)

if __name__ == '__main__':
    main()
