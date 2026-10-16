r"""Per-planting / per-animal ledger for one side.  ledger.py A B SEED[,SEED...] [--side 0]

For every planting: crop, planted day, units harvested, end (harvest/dig/weed/alive).
Aggregates per crop: plantings, mean units, share dead. Animals: product units harvested per animal-day,
care rate, feed rate.
"""
import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
import fastarena  # noqa
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa


def run(a, b, seed, side):
    fa, fb = fastarena.load_agent(a), fastarena.load_agent(b)
    plants = {}     # pos -> record
    done = []
    animals = collections.defaultdict(lambda: {"days": 0, "fed": 0, "cared": 0, "units": 0, "coll": 0})
    orig = K.interpreter

    def interp(state, env):
        obs0 = state[0].observation
        if not (hasattr(obs0, "farms") and obs0.farms):
            return orig(state, env)
        step = obs0.get("step", 0)
        farm = obs0.farms[side]
        before = [[dict(t) if isinstance(t, dict) else t for t in row] for row in farm["tiles"]]
        invs_b = [dict(i) for i in state[side].observation.private["inventories"]]
        act = state[side].action or {}
        units = [act.get("farmer", ["PASS"])] + list(act.get("hands", []) or [])
        pos_b = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
        # animal day stats at end of day (before refresh)
        r = orig(state, env)
        after = farm["tiles"]
        for ui, a_ in enumerate(units):
            if not a_ or ui >= len(pos_b):
                continue
            x, y = pos_b[ui]
            tb = before[y][x]
            if a_[0] == "HARVEST" and isinstance(tb, dict):
                n = tb.get("yield_units", 0)
                if tb.get("kind") == "PLANT" and (x, y) in plants:
                    plants[(x, y)]["units"] += n
                    plants[(x, y)]["harv"] += 1
                elif tb.get("animal"):
                    animals[(x, y, tb["animal"], tb.get("placed_day"))]["units"] += n
            if a_[0] == "COLLECT_FERTILIZER" and isinstance(tb, dict) and tb.get("animal") and tb.get("fertilizer_available"):
                animals[(x, y, tb["animal"], tb.get("placed_day"))]["coll"] += 1
            if a_[0] == "FERTILIZE" and (x, y) in plants and invs_b[ui].get("FERTILIZER", 0) > 0:
                plants[(x, y)]["fert"] += 1
        if (step + 1) % 24 == 0:
            for yy in range(10):
                for xx in range(10):
                    tb = before[yy][xx]
                    if isinstance(tb, dict) and tb.get("animal"):
                        k = (xx, yy, tb["animal"], tb.get("placed_day"))
                        animals[k]["days"] += 1
                        animals[k]["fed"] += 1 if tb.get("fed_today") else 0
                        animals[k]["cared"] += 1 if tb.get("cared_today") else 0
        for yy in range(10):
            for xx in range(10):
                tb, ta = before[yy][xx], after[yy][xx]
                p = (xx, yy)
                was = isinstance(tb, dict) and tb.get("kind") == "PLANT"
                now = isinstance(ta, dict) and ta.get("kind") == "PLANT"
                if now and (not was or ta.get("planted_day") != tb.get("planted_day")):
                    if p in plants:
                        done.append(dict(plants[p], end="replaced"))
                    plants[p] = {"crop": ta["crop"], "day": ta["planted_day"], "units": 0, "harv": 0, "fert": 0}
                elif was and not now and p in plants:
                    end = "weed" if isinstance(ta, dict) and ta.get("kind") == "WEED" else ("dug" if ta is None and plants[p]["harv"] == 0 else "harvest")
                    if ta is None and plants[p]["harv"] > 0:
                        end = "harvest"
                    done.append(dict(plants[p], end=end, endday=(step) // 24))
                    del plants[p]
        return r

    K.interpreter = interp
    try:
        res = fastarena.run_game(fa, fb, seed)
    finally:
        K.interpreter = orig
    for p, rec in plants.items():
        done.append(dict(rec, end="alive"))
    return done, animals, res["rewards"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("seeds")
    ap.add_argument("--side", type=int, default=0)
    args = ap.parse_args()
    allp = []
    alla = collections.defaultdict(lambda: {"n": 0, "days": 0, "fed": 0, "cared": 0, "units": 0, "coll": 0})
    for s in [int(x) for x in args.seeds.split(",")]:
        done, animals, rew = run(args.a, args.b, s, args.side)
        print("seed", s, "rewards", rew)
        allp += done
        for k, v in animals.items():
            d = alla[k[2]]
            d["n"] += 1
            for f in ("days", "fed", "cared", "units", "coll"):
                d[f] += v[f]
    by = collections.defaultdict(list)
    for r in allp:
        by[r["crop"]].append(r)
    print("crop        plantings  mean_units  harvests  fert  end: harvest/weed/alive/dug")
    for c, rs in sorted(by.items()):
        ends = collections.Counter(r["end"] for r in rs)
        n = len(rs)
        print(f"{c:11s} {n:8d} {sum(r['units'] for r in rs) / n:10.2f} {sum(r['harv'] for r in rs) / n:8.2f} "
              f"{sum(r['fert'] for r in rs) / n:5.2f}   {ends['harvest']}/{ends['weed']}/{ends['alive']}/{ends['dug']}")
        # early/mid/late split of weed deaths
        wd = collections.Counter(r["day"] // 5 * 5 for r in rs if r["end"] == "weed")
        if wd:
            print("            weed deaths by planting day:", dict(sorted(wd.items())))
    print("animal  n  animal-days  fed%  cared%  units/day  coll/day")
    for k, d in alla.items():
        if d["days"]:
            print(f"{k:6s} {d['n']:3d} {d['days']:6d} {100 * d['fed'] / d['days']:6.0f} {100 * d['cared'] / d['days']:6.0f} "
                  f"{d['units'] / d['days']:8.2f} {d['coll'] / d['days']:8.2f}")


if __name__ == "__main__":
    main()
