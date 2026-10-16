r"""Executed fertilizer trades of both sides per step in live games (exact replay with an engine hook), to size a
fertilizer sandwich: per game, the rival's fertilizer units sold in steps where we also sell fertilizer, and the
slot of its first fertilizer sell.   .venv\Scripts\python.exe gold\front\fertfills.py [MAX]"""
import sys, gzip, json, glob, collections, multiprocessing as mp
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')

def run(rec):
    import fastarena, forceshops
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    forceshops.force(rec['shops'])
    LOG = collections.defaultdict(lambda: [0, 0, 0, 0])   # (step, pid) -> [sold units, sold value, bought units, bought value]
    CUR = {}
    orig_pm, orig_cu = K._process_market, K._commit_unit
    def pm(state, env):
        CUR['step'] = state[0].observation.step; CUR['farms'] = state[0].observation.farms
        return orig_pm(state, env)
    def cu(op, item, price, farm, private, market, shed_capacity=100):
        ok = orig_cu(op, item, price, farm, private, market, shed_capacity)
        if ok and item == 'FERTILIZER' and op in ('SELL', 'BUY_PRODUCT'):
            pid = [i for i, f in enumerate(CUR['farms']) if f is farm][0]
            e = LOG[(CUR['step'], pid)]
            if op == 'SELL': e[0] += 1; e[1] += price
            else: e[2] += 1; e[3] += price
        return ok
    K._process_market = pm; K._commit_unit = cu
    tapes = [[rec['acts'][s][t + 1] if t + 1 < len(rec['acts'][s]) else None for t in range(719)] for s in range(2)]
    PASS = {"farmer": ["PASS"], "hands": [], "market": []}
    def tape(seat):
        def f(obs, conf=None):
            a = tapes[seat][int(obs['step'])]
            return json.loads(json.dumps(a)) if isinstance(a, dict) else dict(PASS)
        return f
    fastarena.run_game(tape(0), tape(1), rec['seed'])
    K._process_market = orig_pm; K._commit_unit = orig_cu
    me = rec['teams'].index('42'); opp = 1 - me
    out = collections.Counter()
    for (t, pid), e in LOG.items():
        if pid == opp:
            out['opp_sold'] += e[0]; out['opp_bought'] += e[2]
            ours = LOG.get((t, me), [0, 0, 0, 0])
            m = (tapes[opp][t] or {}).get('market') or []
            first = next((i for i, o in enumerate(m) if isinstance(o, list) and len(o) >= 2 and o[0] == 'SELL' and o[1] == 'FERTILIZER'), None)
            if e[0]:
                out['opp_sell_steps'] += 1
                out['opp_sold_slot0' if first == 0 else 'opp_sold_later'] += e[0]
                if ours[0]:
                    out['opp_sold_when_we_sell'] += e[0]
        else:
            out['our_sold'] += e[0]
    return rec['id'], dict(out)

if __name__ == '__main__':
    from classify import sig
    mx = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    recs = {}
    for f in sorted(glob.glob('data/games/live_v7*.jsonl.gz')) + ['data/games/live_v8.jsonl.gz', 'gold/front/v8live.jsonl.gz']:
        for l in gzip.open(f, 'rt', encoding='utf-8'):
            if l.strip():
                r = json.loads(l)
                if '42' in r['teams'] and len(r.get('shops') or []) >= 8: recs[r['id']] = r
    ref = sig(next(iter(recs.values()))['acts'][next(iter(recs.values()))['teams'].index('42')])
    fam = [r for r in recs.values() if sig(r['acts'][1 - r['teams'].index('42')]) == ref][:mx]
    oth = [r for r in recs.values() if sig(r['acts'][1 - r['teams'].index('42')]) != ref][:mx // 2]
    with mp.get_context('spawn').Pool(12, maxtasksperchild=4) as pool:
        for name, sel in (('family', fam), ('other', oth)):
            res = list(pool.imap(run, sel))
            tot = collections.Counter()
            for _, o in res: tot.update(o)
            n = len(res)
            print(name, 'games', n, {k: round(v / n, 1) for k, v in sorted(tot.items())})
