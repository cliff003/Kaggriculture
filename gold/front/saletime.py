r"""Sale timing of both seats per product over a set of live-game replays (our seat = CAND): units and average
price by hour band, from day D0 on, plus the average price gap on the units both sold.
    .venv\Scripts\python.exe gold\front\saletime.py CAND.py ITEM[,ITEM] ID [ID ...] [--d0 10]"""
import sys, os, json, collections, argparse, multiprocessing as mp
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')
BANDS = [(0, 3), (4, 7), (8, 11), (12, 15), (16, 19), (20, 23)]
def play(job):
    cand, path, items, d0 = job
    import fastarena, forceshops
    from cfroute import tape_file
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    rec = json.load(open(path, encoding='utf-8')); me = rec['teams'].index('42')
    S = collections.defaultdict(lambda: [0, 0.0]); CUR = {}
    orig_pm, orig_cu = K._process_market, K._commit_unit
    def pm(state, env):
        CUR['s'] = state[0].observation.step; CUR['farms'] = state[0].observation.farms
        return orig_pm(state, env)
    def cu(op, item, price, farm, private, market, shed_capacity=100):
        ok = orig_cu(op, item, price, farm, private, market, shed_capacity)
        if ok and op == 'SELL' and item in items and CUR['s'] // 24 >= d0:
            seat = [i for i, f in enumerate(CUR['farms']) if f is farm][0]
            h = CUR['s'] % 24
            b = [i for i, (a, z) in enumerate(BANDS) if a <= h <= z][0]
            key = ('us' if seat == me else 'them', item, b)
            S[key][0] += 1; S[key][1] += price
        return ok
    K._process_market, K._commit_unit = pm, cu
    forceshops.force(rec['shops'])
    fns = [None, None]; fns[me] = fastarena.load_agent(cand); fns[1 - me] = fastarena.load_agent(tape_file(rec, 1 - me))
    fastarena.run_game(fns[0], fns[1], rec['seed'])
    return {repr(k): v for k, v in S.items()}
if __name__ == '__main__':
    from tgrun import find_recs
    ap = argparse.ArgumentParser(); ap.add_argument('cand'); ap.add_argument('items'); ap.add_argument('ids', nargs='+'); ap.add_argument('--d0', type=int, default=10)
    a = ap.parse_args(); items = a.items.split(',')
    recs = find_recs(a.ids); jobs = []
    for rid, r in recs.items():
        p = f'gold/tmp/tgrun/{rid}.json'; json.dump(r, open(p, 'w', encoding='utf-8')); jobs.append((os.path.abspath(a.cand), p, items, a.d0))
    with mp.get_context('spawn').Pool(min(12, len(jobs)), maxtasksperchild=1) as pool:
        outs = list(pool.imap(play, jobs))
    T = collections.defaultdict(lambda: [0, 0.0])
    for o in outs:
        for k, v in o.items():
            k = eval(k); T[k][0] += v[0]; T[k][1] += v[1]
    n = len(outs)
    for item in items:
        print(f"== {item} (per game, days {a.d0}+)")
        for side in ('us', 'them'):
            cells = []
            tu = tr = 0
            for b, (lo, hi) in enumerate(BANDS):
                u, rv = T[(side, item, b)]
                tu += u; tr += rv
                cells.append(f"h{lo:02d}-{hi:02d}: {u / n:5.1f} @ {rv / max(1, u):5.0f}")
            print(f"  {side:4s} total {tu / n:6.1f} units avg {tr / max(1, tu):5.0f} | " + ' | '.join(cells))
