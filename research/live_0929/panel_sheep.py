"""Paired reactive panel enriched for the early sheep-expansion opportunity."""
import hashlib
import argparse
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import statistics
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/port_0927'))
from panel import run, SHOPS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--target', choices=('sheep', 'tomato'), default='sheep')
    ap.add_argument('--candidate', type=Path, default=HERE / 'prototypes/sheep_cash/main.py')
    ap.add_argument('--worlds', type=int, default=24)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--out-dir', type=Path, default=HERE)
    ap.add_argument('--seed-start', type=int)
    a = ap.parse_args()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    os.environ['PYTHONHASHSEED'] = '0'
    seed_start = a.seed_start if a.seed_start is not None else (2026092903 if a.target == 'sheep' else 2026092911)
    rng = random.Random(seed_start)
    worlds = []
    # Distinct worlds, balanced seats. Choose every shop before playing.
    while len(worlds) < a.worlds:
        shops = [rng.choice(SHOPS) for _ in range(8)]
        eligible = (shops[:3].count('YARN_STORE') >= 2 if a.target == 'sheep' else
                    sum(s in ('PIZZA_SHOP', 'FARMERS_MARKET') for s in shops[:6]) >= 4)
        if not eligible:
            continue
        if any(w[1] == shops for w in worlds):
            continue
        worlds.append((seed_start + len(worlds), shops, len(worlds) % 2))
    names = ('cha22', 'emu_tick0', 'emu_eager_m', 'morewheat',
             'emu_antifade', 'emu_prebuy0', 'emu_tick3', 'emu_sw8')
    paths = [str(ROOT / 'submissions/V12_AventadorSVJ/main.py'),
             str(a.candidate.resolve())]
    jobs = [(name, str(ROOT / 'research/panel' / name / 'main.py'), p, seed, shops, seat)
            for seed, shops, seat in worlds for name in names for p in paths]
    meta = {'worlds': worlds, 'paths': {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},
            'opponents': {n: hashlib.sha256((ROOT / 'research/panel' / n / 'main.py').read_bytes()).hexdigest() for n in names}}
    (a.out_dir / f'{a.target}_panel_metadata.json').write_text(json.dumps(meta, indent=2))
    rows = []
    with mp.get_context('spawn').Pool(a.workers, maxtasksperchild=20) as pool, (a.out_dir / f'{a.target}_panel.jsonl').open('w') as f:
        for r in pool.imap_unordered(run, jobs, chunksize=1):
            f.write(json.dumps(r) + '\n'); f.flush(); rows.append(r)
            if len(rows) % 48 == 0:
                print(f'{len(rows)}/{len(jobs)}', flush=True)
    key = lambda r: (r['opponent'], r['seed'], r['seat'])
    base = {key(r): r for r in rows if r['path'] == paths[0]}
    for name in ('ALL',) + names:
        subset = [r for r in rows if r['path'] == paths[1] and (name == 'ALL' or r['opponent'] == name)]
        print(name, 'n', len(subset), 'base wins', sum(base[key(r)]['margin'] > 0 for r in subset),
              'new wins', sum(r['margin'] > 0 for r in subset),
              'up', sum(base[key(r)]['margin'] <= 0 < r['margin'] for r in subset),
              'down', sum(r['margin'] <= 0 < base[key(r)]['margin'] for r in subset),
              'delta', round(statistics.mean(r['margin'] - base[key(r)]['margin'] for r in subset), 2),
              'changed', sum(r['margin'] != base[key(r)]['margin'] for r in subset), flush=True)


if __name__ == '__main__':
    main()
