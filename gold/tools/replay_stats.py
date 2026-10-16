r"""Replay a live episode (kg.py replay JSON) through the local engine with gstat's hooks and compare both sides:
day-0 opening, money by day, sales by product and phase, melon sale hours.

.venv\Scripts\python.exe gold\tools\replay_stats.py gold\replays\EPISODE.json [--our-sub SUBID]
"""
import collections
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import fastarena  # noqa: E402
import gstat  # noqa: E402

PASS = {"farmer": ["PASS"], "hands": [], "market": []}


def tape_agent(tape):
    def agent(obs, conf=None):
        t = int(obs["step"])
        a = tape[t] if 0 <= t < len(tape) else None
        return copy.deepcopy(a) if isinstance(a, dict) else dict(PASS)
    return agent


def load(path):
    rep = json.load(open(path))
    steps = rep["steps"]
    tapes = [[steps[t + 1][i].get("action") for t in range(len(steps) - 1)] for i in range(2)]
    info = rep.get("info", {})
    seed = rep["configuration"].get("seed") or info.get("seed")
    shops = rep["steps"][-1][0]["observation"].get("town", {}).get("unlocked_shops")
    return rep, tapes, seed, info, shops


def main():
    path = sys.argv[1]
    rep, tapes, seed, info, shops = load(path)
    import forceshops
    forceshops.force(shops)
    names = info.get("TeamNames") or ["p0", "p1"]
    gstat.install_hooks()
    gstat._STATS = ([], [])
    melon = collections.defaultdict(lambda: [0, 0.0])
    K = gstat.K
    orig = K._commit_unit
    cur = gstat._CUR

    def commit(op, item, price, farm, private, market, shed_capacity=100):
        ok = orig(op, item, price, farm, private, market, shed_capacity)
        if ok and op == "SELL" and item == "MELON":
            pid = 0 if farm is cur["farms"][0] else 1
            melon[(pid, cur.get("step", 0))][0] += 1
            melon[(pid, cur.get("step", 0))][1] += price
        return ok
    K._commit_unit = commit
    oi = K.interpreter

    def interp(state, env):
        cur["step"] = state[0].observation.step
        return oi(state, env)
    K.interpreter = interp
    r = fastarena.run_game(tape_agent(tapes[0]), tape_agent(tapes[1]), seed)
    days = gstat._STATS
    print(f"episode {os.path.basename(path)} seed {seed} teams {names}")
    print(f"server rewards {rep.get('rewards')} local {r['rewards']}")
    for p in (0, 1):
        d0 = days[p][0]["end"]
        print(f"  p{p} {names[p]}: day0 end animals {d0['animals']} crops {d0['crops']} money {d0['money']}")
    print("money by day (p0 / p1):")
    print("   " + " ".join(f"d{d}:{days[0][d]['end']['money'] / 1000:.1f}/{days[1][d]['end']['money'] / 1000:.1f}"
                         for d in (5, 8, 10, 12, 15, 20, 25, 29) if d < len(days[0])))
    print("composition d12 / d20:")
    for p in (0, 1):
        for d in (12, 20):
            e = days[p][d]["end"]
            print(f"  p{p} d{d} animals {e['animals']} crops {e['crops']} empty {e['empty']} quads {len(e['quads'])}")
    print("revenue by product (d0-9 / d10-19 / d20-29), p0 vs p1:")
    items = sorted({k for p in (0, 1) for dd in days[p] for k in dd["sell_rev"]})
    for it in items:
        row = []
        for p in (0, 1):
            ph = [sum(dd["sell_rev"].get(it, 0) for dd in days[p] if lo <= dd["day"] <= hi) for lo, hi in ((0, 9), (10, 19), (20, 29))]
            un = sum(dd["sell_units"].get(it, 0) for dd in days[p])
            row.append(f"{ph[0]:6.0f} {ph[1]:6.0f} {ph[2]:6.0f} ({un:3d})")
        print(f"  {it:10s} p0 {row[0]} | p1 {row[1]}")
    for p in (0, 1):
        hires = sum(dd["hire_cost"] for dd in days[p])
        buys = collections.Counter()
        for dd in days[p]:
            for k, v in dd["buy_spend"].items():
                buys[k] += v
        print(f"  p{p} hires {hires:.0f} buys " + " ".join(f"{k}:{v:.0f}" for k, v in buys.most_common(8)))
    print("melon sales (day hour: units@avg):")
    for p in (0, 1):
        ks = sorted(k for k in melon if k[0] == p)
        print(f"  p{p} " + " ".join(f"d{k[1] // 24}h{k[1] % 24}:{melon[k][0]}@{melon[k][1] / melon[k][0]:.0f}" for k in ks))


if __name__ == "__main__":
    main()
