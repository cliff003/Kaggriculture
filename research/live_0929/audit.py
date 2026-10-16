"""Current submissions: exact factual accounts and paired live-tape replays.

Opponent actions and all eight shops are fixed. Cross-version results are
counterfactual diagnostics, not a replacement for a reactive opponent panel.
"""
import argparse
import collections
import gzip
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / 'tools'), str(ROOT / 'research/carrera')]
VERSIONS = {'56633607': 'V10_CarreraGT', '56649860': 'V12_AventadorSVJ'}


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def prepare():
    from ab_replay import tapes
    recs = tapes()
    fresh = HERE / 'fresh.jsonl.gz'
    if fresh.exists():
        for line in gzip.open(fresh, 'rt'):
            rec = json.loads(line)
            recs[rec['id']] = rec
    snapshot = json.loads((HERE / 'episodes_snapshot.json').read_text())
    selection = {sid: [e['id'] for e in es[-40:]] for sid, es in snapshot.items()}
    ids = set(sum(selection.values(), []))
    missing = ids - recs.keys()
    if missing:
        raise RuntimeError(f'Missing episodes: {sorted(missing)}')
    with gzip.open(HERE / 'selected.jsonl.gz', 'wt') as f:
        for eid in sorted(ids):
            f.write(json.dumps(recs[eid], ensure_ascii=False) + '\n')
    write_json(HERE / 'selection.json', selection)
    print(f'Selected {len(ids)} episodes', flush=True)


def factual_job(rec):
    import econ
    import forceshops
    forceshops.force(rec['shops'])
    result = econ.resim(rec)
    net = [collections.Counter(), collections.Counter()]
    daily = [collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)]
    for step, p, op, item, value in econ._CUR['log']:
        if op == 'LOST':
            continue  # diagnostic valuation, not an actual cash expense
        if op in ('HIRE', 'LAND'):
            key, amount = op, -value
        else:
            key = {'COW': 'MILK', 'SHEEP': 'WOOL', 'GOOSE': 'EGG'}.get(item, item)
            amount = value if op == 'SELL' else -value
        net[p][key] += amount
        daily[p][step // 24][key] += amount
    return {'id': rec['id'], 'shops': rec['shops'], 'teams': rec['teams'],
            'server': rec['rewards'], 'result': result,
            'net': net, 'daily_net': daily,
            'max_reward_error': max(abs(x['money'] - x['server']) for x in result),
            'cash_error': [x['money'] - sum(net[p].values()) for p, x in enumerate(result)]}


def replay_job(arg):
    import cfreplay
    sid, rec = arg
    path = ROOT / 'submissions' / VERSIONS[sid] / 'main.py'
    eid, opp, live, margin, money, opp_money, status = cfreplay.job((rec, '42', str(path), True))
    return {'version': sid, 'id': eid, 'opp': opp, 'live': live,
            'margin': margin, 'money': money, 'opp_money': opp_money, 'status': status}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['prepare', 'factual', 'replay'])
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--source', type=Path, default=HERE / 'selected.jsonl.gz')
    ap.add_argument('--prefix', default='')
    a = ap.parse_args()
    os.environ['PYTHONHASHSEED'] = '0'
    if a.mode == 'prepare':
        return prepare()
    recs = [json.loads(line) for line in gzip.open(a.source, 'rt')]
    jobs = recs if a.mode == 'factual' else [(sid, rec) for sid in VERSIONS for rec in recs]
    fn = factual_job if a.mode == 'factual' else replay_job
    rows = []
    with mp.get_context('spawn').Pool(a.workers) as pool, (HERE / f'{a.prefix}{a.mode}.jsonl').open('w') as f:
        for r in pool.imap_unordered(fn, jobs, chunksize=1):
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
            f.flush()
            rows.append(r)
            if len(rows) % 20 == 0:
                print(f'{a.mode}: {len(rows)}/{len(jobs)}', flush=True)
    if a.mode == 'factual':
        print('maximum factual reward error:', max(r['max_reward_error'] for r in rows))
        print('initial cash / residual:', sorted(set(v for r in rows for v in r['cash_error'])))
    else:
        selection = json.loads((HERE / 'selection.json').read_text())
        lookup = {(r['version'], r['id']): r for r in rows}
        for sid, ids in selection.items():
            ids = [eid for eid in ids if (sid, eid) in lookup]
            same = sum(lookup[sid, eid]['margin'] == lookup[sid, eid]['live'] for eid in ids)
            print(sid, 'own live reproduction', same, '/', len(ids))
        print('bad status:', sum(r['status'] != ['DONE', 'DONE'] for r in rows))
    write_json(HERE / f'{a.prefix}{a.mode}_metadata.json', {
        'python_hash_seed': '0', 'episodes': len(recs),
        'source_sha256': hashlib.sha256(a.source.read_bytes()).hexdigest(),
        'versions': {sid: {'name': name, 'sha256': hashlib.sha256((ROOT / 'submissions' / name / 'main.py').read_bytes()).hexdigest()}
                     for sid, name in VERSIONS.items()}})


if __name__ == '__main__':
    main()
