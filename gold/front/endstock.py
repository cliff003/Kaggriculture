r"""Goods left unsold at the end of live-game replays (our seat replaced by CAND, rival tape kept).
    .venv\Scripts\python.exe gold\front\endstock.py CAND.py FILE.jsonl.gz [--n 20]"""
import sys, os, json, gzip, argparse, collections
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cand'); ap.add_argument('file'); ap.add_argument('--n', type=int, default=20)
    a = ap.parse_args()
    import fastarena, forceshops
    from cfroute import tape_file
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    recs = [json.loads(l) for l in gzip.open(a.file, 'rt', encoding='utf-8') if l.strip()][:a.n]
    CAP = {}
    orig = K._town_consume
    def pm(env, state, step):
        if step >= 717:
            CAP[step] = [(dict(x.observation.private['shed']), [dict(i) for i in x.observation.private['inventories']]) for x in state]
            CAP['prices'] = dict(state[0].observation.market['prices'])
        return orig(env, state, step)
    K._town_consume = pm
    tot = collections.Counter(); totv = collections.Counter()
    for r in recs:
        if '42' not in r['teams']:
            continue
        me = r['teams'].index('42')
        forceshops.force(r['shops'])
        fns = [None, None]
        fns[me] = fastarena.load_agent(a.cand); fns[1 - me] = fastarena.load_agent(tape_file(r, 1 - me))
        CAP.clear()
        res = fastarena.run_game(fns[0], fns[1], r['seed'])
        last = max(k for k in CAP if isinstance(k, int))
        shed, invs = CAP[last][me]
        left = collections.Counter({k: v for k, v in shed.items() if v > 0})
        for i in invs:
            for k, v in i.items():
                if v > 0: left[k] += v
        pr = CAP['prices']
        val = sum(v * pr.get(k, 0) for k, v in left.items())
        oshed, oinvs = CAP[last][1 - me]
        oleft = sum(v for v in oshed.values() if v > 0)
        print(r['id'], r['teams'][1 - me][:16], 'step', last, 'our left', dict(left), 'value', round(val), '| rival shed units', oleft, flush=True)
        for k, v in left.items():
            tot[k] += v; totv[k] += v * pr.get(k, 0)
    print('mean per game:', {k: round(v / len(recs), 1) for k, v in tot.items()}, 'value', round(sum(totv.values()) / len(recs)))
