"""Economic breakdown of one game using the fast runner + engine instrumentation.

python analyze2.py agents/A/main.py agents/B/main.py --seed 5
"""
import argparse, collections, json
import fastarena
from kaggle_environments.envs.kaggriculture import kaggriculture as K

LOG = []
_orig_commit = K._commit_unit
_orig_hire = K._do_hire
_orig_land = K._do_buy_land
CUR = {"step": 0, "farms": None}


def _commit(op, item, price, farm, private, market, shed_capacity=100):
    before = farm["money"]
    ok = _orig_commit(op, item, price, farm, private, market, shed_capacity)
    if ok:
        LOG.append(("M", CUR["step"], id(farm), op, item, price))
    return ok


def _hire(farm, private, board_size, mult=1):
    before = farm["money"]
    _orig_hire(farm, private, board_size, mult)
    if farm["money"] != before:
        LOG.append(("H", CUR["step"], id(farm), "HIRE", None, before - farm["money"]))


def _land(farm, board_size):
    before = farm["money"]
    _orig_land(farm, board_size)
    if farm["money"] != before:
        LOG.append(("L", CUR["step"], id(farm), "LAND", None, before - farm["money"]))


K._commit_unit = _commit
K._do_hire = _hire
K._do_buy_land = _land
_orig_interp = K.interpreter


def _interp(state, env):
    o0 = state[0].observation
    CUR["step"] = o0.get("step", 0) if hasattr(o0, "get") else 0
    if getattr(o0, "farms", None):
        CUR["farms"] = [id(f) for f in o0.farms]
    return _orig_interp(state, env)


K.interpreter = _interp


def analyze(a, b, seed, verbose=True):
    LOG.clear()
    fa, fb = fastarena.load_agent(a), fastarena.load_agent(b)
    r = fastarena.run_game(fa, fb, seed)
    # map farm ids -> player. farms objects persist in place through the game (interpreter mutates).
    st = r["final_state"]
    fid = [id(f) for f in st[0].observation.farms]
    out = {}
    shops = st[0].observation.town["unlocked_shops"]
    for p in (0, 1):
        rev = collections.defaultdict(lambda: [0, 0.0])
        cost = collections.defaultdict(lambda: [0, 0.0])
        hires_by_day = collections.Counter()
        land_days = []
        for kind, step, f, op, item, price in LOG:
            if f != fid[p]:
                continue
            if kind == "M":
                if op == "SELL":
                    rev[item][0] += 1; rev[item][1] += price
                else:
                    cost[(op, item)][0] += 1; cost[(op, item)][1] += price
            elif kind == "H":
                hires_by_day[step // 24] += 1
                cost[("HIRE", "")][0] += 1; cost[("HIRE", "")][1] += price
            elif kind == "L":
                land_days.append(step // 24)
                cost[("LAND", "")][0] += 1; cost[("LAND", "")][1] += price
        out[p] = dict(rev=dict(rev), cost=dict(cost), hires=dict(hires_by_day), land=land_days, reward=r["rewards"][p])
        if verbose:
            print(f"\n=== P{p} {[a, b][p]}  reward={r['rewards'][p]}")
            print("  land days:", land_days, " hires/day:", dict(sorted(hires_by_day.items())))
            tot = 0
            for item, (n, v) in sorted(rev.items(), key=lambda kv: -kv[1][1]):
                print(f"  SELL {item:11s} {n:5d} units  ${v:9.0f}  avg {v/max(1,n):6.1f}")
                tot += v
            print(f"  total revenue {tot:.0f}")
            ctot = 0
            for k, (n, v) in sorted(cost.items(), key=lambda kv: -kv[1][1]):
                print(f"  COST {k[0]:11s} {k[1]:10s} {n:5d}  ${v:9.0f}")
                ctot += v
            print(f"  total cost {ctot:.0f}   net {tot-ctot:.0f}")
    if verbose:
        print("shops:", shops)
        prices = st[0].observation.market["prices"]
        print("final prices:", dict(prices))
    return out, shops


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b")
    ap.add_argument("--seed", type=int, default=5)
    args = ap.parse_args()
    analyze(args.a, args.b, args.seed)
