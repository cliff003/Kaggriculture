r"""Compare per-tile operations of two agents playing seat 0 from the same state (hybrids sharing a tape prefix).

opcmp.py A B OPP SEEDS FROM_DAY TO_DAY
Plays A vs OPP and B vs OPP on each seed; for seat 0 tallies ops on each tile by (crop or animal, age) over
[FROM_DAY, TO_DAY] and prints where the counts differ most, plus product units harvested by kind.
"""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
import fastarena  # noqa: E402
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa: E402


def run(a, opp, seed, d0, d1):
    fa, fo = fastarena.load_agent(a), fastarena.load_agent(opp)
    tally = collections.Counter()
    units = collections.Counter()
    orig = K.interpreter

    def interp(state, env):
        obs0 = state[0].observation
        if hasattr(obs0, "farms") and obs0.farms:
            step = obs0.get("step", 0)
            day = step // 24
            if d0 <= day <= d1:
                farm = obs0.farms[0]
                act = state[0].action or {}
                acts = [act.get("farmer", ["PASS"])] + list(act.get("hands", []) or [])
                pos = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
                for a_, p in zip(acts, pos):
                    if not a_ or a_[0] in ("PASS", "NORTH", "SOUTH", "EAST", "WEST"):
                        tally[("move/pass", a_[0] if a_ else "PASS")] += 1
                        continue
                    t = farm["tiles"][p[1]][p[0]]
                    if isinstance(t, dict) and t.get("kind") == "PLANT":
                        k = (t["crop"], day - t["planted_day"], a_[0])
                        if a_[0] == "HARVEST":
                            units[t["crop"]] += t.get("yield_units", 0)
                    elif isinstance(t, dict) and t.get("animal"):
                        k = (t["animal"], "-", a_[0])
                        if a_[0] == "HARVEST":
                            units[t["animal"]] += t.get("yield_units", 0)
                    else:
                        k = ("other", "-", a_[0])
                    tally[k] += 1
        return orig(state, env)

    K.interpreter = interp
    try:
        r = fastarena.run_game(fa, fo, seed)
    finally:
        K.interpreter = orig
    return tally, units, r["rewards"]


def main():
    a, b, opp, seeds, d0, d1 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6])
    seeds = [int(s) for s in seeds.split(",")]
    TA, TB, UA, UB = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    for s in seeds:
        ta, ua, ra = run(a, opp, s, d0, d1)
        tb, ub, rb = run(b, opp, s, d0, d1)
        TA.update(ta); TB.update(tb); UA.update(ua); UB.update(ub)
        print("seed", s, "A", ra, "B", rb)
    n = len(seeds)
    print("harvested units per game  A / B:")
    for k in sorted(set(UA) | set(UB)):
        print(f"   {k:11s} {UA[k] / n:7.1f} {UB[k] / n:7.1f}")
    keys = sorted(set(TA) | set(TB), key=lambda k: -abs(TA[k] - TB[k]))
    print("ops per game (A / B), largest differences:")
    for k in keys[:40]:
        print(f"   {str(k):40s} {TA[k] / n:6.1f} {TB[k] / n:6.1f}")


if __name__ == "__main__":
    main()
