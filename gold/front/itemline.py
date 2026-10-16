r"""Per-day sales of one item for both seats in a live-game replay (our seat = CAND, rival tape kept): units,
revenue, average price, the hours sold, plus the market quote at hour 0 of each day.
    .venv\Scripts\python.exe gold\front\itemline.py CAND.py GAME_ID ITEM"""
import sys, os, json, collections
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools'); sys.path.insert(0, 'gold/front')
if __name__ == '__main__':
    cand, gid, item = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    import fastarena, forceshops
    from cfroute import tape_file
    from tgrun import find_recs
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    rec = find_recs([gid])[gid]
    me = rec['teams'].index('42')
    D = collections.defaultdict(lambda: [collections.Counter(), collections.Counter(), collections.defaultdict(set)])
    Q = {}
    CUR = {}
    orig_pm, orig_cu = K._process_market, K._commit_unit
    def pm(state, env):
        CUR['step'] = state[0].observation.step; CUR['farms'] = state[0].observation.farms
        if CUR['step'] % 24 == 0:
            Q[CUR['step'] // 24] = (state[0].observation.market['prices'][item], state[0].observation.market['inventory'][item])
        return orig_pm(state, env)
    def cu(op, it, price, farm, private, market, shed_capacity=100):
        ok = orig_cu(op, it, price, farm, private, market, shed_capacity)
        if ok and op == 'SELL' and it == item:
            s = [i for i, f in enumerate(CUR['farms']) if f is farm][0]
            d = CUR['step'] // 24
            D[d][0][s] += 1; D[d][1][s] += price; D[d][2][s].add(CUR['step'] % 24)
        return ok
    K._process_market, K._commit_unit = pm, cu
    forceshops.force(rec['shops'])
    fns = [None, None]; fns[me] = fastarena.load_agent(cand); fns[1 - me] = fastarena.load_agent(tape_file(rec, 1 - me))
    r = fastarena.run_game(fns[0], fns[1], rec['seed'])
    op = 1 - me
    print('shops', rec['shops'])
    print(f"{'day':>3s} {'quote@h0':>8s} {'inv':>6s} | {'us n':>5s} {'avg':>5s} hours          | {'rival n':>7s} {'avg':>5s} hours")
    tu = tr = 0
    for d in range(30):
        u, rv, hs = D[d]
        q = Q.get(d, ('', ''))
        if u[me] or u[op]:
            print(f"{d:3d} {q[0]:>8} {q[1]:>6} | {u[me]:5d} {rv[me] / max(1, u[me]):5.0f} {sorted(hs[me])!s:14s} | {u[op]:7d} {rv[op] / max(1, u[op]):5.0f} {sorted(hs[op])}")
        tu += rv[me]; tr += rv[op]
    print('revenue us', round(tu), 'rival', round(tr))
