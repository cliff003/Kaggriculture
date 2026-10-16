r"""Upper bound of breaking same-step sell races: in a local game, for every step where both sides sell the same
premium good, compare our executed revenue with what we would get selling our units first (before the rival's).
    .venv\Scripts\python.exe gold\front\raceval.py AGENT OPP SEED[,SEED...]"""
import sys, collections
sys.path.insert(0, 'gold/tools'); sys.path.insert(0, 'tools')
import fastarena
from kaggle_environments.envs.kaggriculture import kaggriculture as K
PREM = ('MILK', 'STRAWBERRY', 'WOOL', 'EGG', 'TOMATO', 'CARROT', 'MELON')
if __name__ == '__main__':
    ag, opp, seeds = sys.argv[1], sys.argv[2], [int(s) for s in sys.argv[3].split(',')]
    tot = collections.Counter()
    for seed in seeds:
        LOG = collections.defaultdict(lambda: collections.defaultdict(list))
        INV = {}
        CUR = {}
        orig_pm, orig_cu = K._process_market, K._commit_unit
        def pm(state, env):
            CUR['step'] = state[0].observation.step; CUR['farms'] = state[0].observation.farms
            INV[CUR['step']] = dict(state[0].observation.market['inventory'])
            return orig_pm(state, env)
        def cu(op, item, price, farm, private, market, shed_capacity=100):
            ok = orig_cu(op, item, price, farm, private, market, shed_capacity)
            if ok and op == 'SELL' and item in PREM:
                pid = [i for i, f in enumerate(CUR['farms']) if f is farm][0]
                LOG[CUR['step']][(pid, item)].append(price)
            return ok
        K._process_market = pm; K._commit_unit = cu
        f = fastarena.load_agent(ag); g = fastarena.load_agent(opp)
        r = fastarena.run_game(f, g, seed)
        K._process_market = orig_pm; K._commit_unit = orig_cu
        gain = 0; races = 0; units = 0
        for t, d in LOG.items():
            for item in PREM:
                a, b = d.get((0, item), []), d.get((1, item), [])
                if a and b:
                    races += 1; units += len(a)
                    inv0 = INV[t][item]
                    # selling our len(a) units first from the same starting inventory (ignoring other orders in between)
                    first = sum(K.market_price(item, inv0 + k) for k in range(len(a)))
                    gain += first - sum(a)
        print(seed, 'rewards', r['rewards'], 'race steps', races, 'our units in races', units, 'first-mover gain', gain)
        tot['gain'] += gain; tot['races'] += races
    print('mean first-mover gain per game', round(tot['gain'] / len(seeds)), 'race steps', round(tot['races'] / len(seeds), 1))
