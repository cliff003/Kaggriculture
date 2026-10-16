r"""Log every wheat unit trade (step, slot, player, op, price) in one local game; summarize the rival's wheat trades on
churn steps.  .venv\Scripts\python.exe gold\tick\wlog.py CAND OPP SEED"""
import sys, collections
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
import fastarena
from kaggle_environments.envs.kaggriculture import kaggriculture as K
LOG = []
CUR = {}
_orig_pm = K._process_market
_orig_cu = K._commit_unit
def pm(state, env):
    CUR['step'] = state[0].observation.step
    CUR['farms'] = state[0].observation.farms
    CUR['queues'] = [list((s.action or {}).get('market', []) or []) if isinstance(s.action, dict) else [] for s in state]
    return _orig_pm(state, env)
def cu(op, item, price, farm, private, market, shed_capacity=100):
    ok = _orig_cu(op, item, price, farm, private, market, shed_capacity)
    if ok and item == 'WHEAT':
        pid = [i for i, f in enumerate(CUR['farms']) if f is farm][0]
        LOG.append((CUR['step'], pid, op, price))
    return ok
K._process_market = pm
K._commit_unit = cu
if __name__ == '__main__':
    cand, opp, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    f = fastarena.load_agent(cand); g = fastarena.load_agent(opp)
    r = fastarena.run_game(f, g, seed)
    print('rewards', r['rewards'])
    churn = set()
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for st, pid, op, p in LOG:
        by[st][(pid, op)].append(p)
    for st in by:
        b = by[st].get((0, 'BUY_PRODUCT'), [])
        if st % 4 == 0 and len(b) >= 10:
            churn.add(st)
    agg = collections.Counter()
    for st in sorted(churn):
        for s2, tag in ((st, 'buy-step'), (st + 1, 'sell-step')):
            for (pid, op), ps in by[s2].items():
                if pid == 1:
                    agg[(tag, op, 'units')] += len(ps); agg[(tag, op, 'value')] += sum(ps)
    for k, v in sorted(agg.items()):
        print(k, v)
    # opponent wheat sells by hour overall
    hs = collections.Counter()
    for st, pid, op, p in LOG:
        if pid == 1:
            hs[(op, st % 4)] += 1
    print('rival wheat units by (op, step%4):', dict(hs))
