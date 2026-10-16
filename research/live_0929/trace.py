"""Trace production divergence without changing either submitted agent."""
import collections
import gzip
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import fastarena
import forceshops
from cfreplay import tape_agent


def run(rec, name, path=None):
    forceshops.force(rec['shops'])
    me = rec['teams'].index('42')
    fn = fastarena.load_agent(str(path or ROOT / 'submissions' / name / 'main.py'))
    rows = []
    def spy(obs, conf):
        act = fn(obs, conf)
        s = int(obs['step'])
        row = {'step': s, 'action': act, 'cash': obs['farms'][me]['money'],
               'shed': obs['private']['shed']}
        if s % 24 in (0, 23):
            farm = obs['farms'][me]
            row['tiles'] = [dict(t, x=x, y=y) for y, ts in enumerate(farm['tiles'])
                            for x, t in enumerate(ts) if isinstance(t, dict)]
        rows.append(row)
        return act
    fns = [tape_agent(a) for a in rec['acts']]
    fns[me] = spy
    result = fastarena.run_game(*fns, rec['seed'])
    g = fn.__globals__
    reports = {k: v for k, v in (g.get('_BASE_NS') or g).items() if k.endswith('_REPORT') and isinstance(v, dict)}
    reports.update({k: v for k, v in g.items() if k.endswith('_REPORT') and isinstance(v, dict)})
    for k in ('_TICK_NS', '_TG_NS', '_SCH_NS'):
        reports[k] = (g.get(k) or {}).get('TEL')
    return {'version': name, 'id': rec['id'], 'rewards': result['rewards'],
            'errors': result['errors'], 'reports': reports, 'steps': rows}


if __name__ == '__main__':
    eid = int(sys.argv[1])
    rec = next(r for r in map(json.loads, gzip.open(HERE / 'selected.jsonl.gz', 'rt')) if r['id'] == eid)
    for name in ('V10_CarreraGT', 'V12_AventadorSVJ'):
        result = run(rec, name)
        with gzip.open(HERE / f'trace_{eid}_{name}.json.gz', 'wt') as f:
            json.dump(result, f)
        print(name, result['rewards'], result['errors'], flush=True)
