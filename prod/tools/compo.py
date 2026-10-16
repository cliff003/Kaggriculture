r"""Farm composition and money by day in recorded games (both seats replayed from their own actions).

compo.py GAMES.jsonl.gz TEAM [--days 4,8,12,16,20,24,29] [--max N]
Per day, TEAM vs opponents: money, planted tiles by crop, animals by type, hands, gross sales so far.
"""
import argparse
import collections
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
import fastarena  # noqa: E402
from fidelity import tape_agent, load  # noqa: E402
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa: E402


def snap(farm):
    c = collections.Counter()
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    c["P_" + t["crop"]] += 1
                elif t.get("animal"):
                    c["A_" + t["animal"]] += 1
    c["hands"] = len(farm["hands"])
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("team")
    ap.add_argument("--days", default="4,8,12,16,20,24,29")
    ap.add_argument("--max", type=int, default=80)
    a = ap.parse_args()
    days = [int(x) for x in a.days.split(",")]
    recs = [r for r in load(a.games) if a.team in r["teams"]][:a.max]
    agg = {s: {d: collections.Counter() for d in days} for s in ("me", "opp")}
    money = {s: {d: 0.0 for d in days} for s in ("me", "opp")}
    orig = K.interpreter
    for r in recs:
        me = r["teams"].index(a.team)
        cur = {}

        def interp(state, env):
            out = orig(state, env)
            obs0 = state[0].observation
            if hasattr(obs0, "farms") and obs0.farms:
                st = obs0.get("step", 0)
                if st % 24 == 23 and st // 24 in days:
                    for seat, key in ((me, "me"), (1 - me, "opp")):
                        f = obs0.farms[seat]
                        cur[(key, st // 24)] = (snap(f), f.get("money", 0))
            return out

        K.interpreter = interp
        try:
            fastarena.run_game(tape_agent(r["acts"][0]), tape_agent(r["acts"][1]), r["seed"])
        finally:
            K.interpreter = orig
        for (key, d), (c, m) in cur.items():
            agg[key][d].update(c)
            money[key][d] += m
    n = len(recs)
    keys = sorted(set(k for s in agg.values() for c in s.values() for k in c))
    print(f"{a.team}: {n} games; per-game means (me / opp)")
    print("day  money" + "".join(f" {k[:12]:>13}" for k in keys))
    for d in days:
        row = f"{d:3d} {money['me'][d] / n:6.0f}/{money['opp'][d] / n:6.0f}"
        for k in keys:
            row += f" {agg['me'][d][k] / n:6.1f}/{agg['opp'][d][k] / n:5.1f}"
        print(row)


if __name__ == "__main__":
    main()
