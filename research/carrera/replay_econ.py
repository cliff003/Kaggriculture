r"""Money breakdown of candidate replays: the candidate plays our seat against the live opponent's tape (shops forced,
as in ab_replay.py) while tools/econ.py's engine hooks log every sale, purchase, hire and lost unit of both sides.

.venv/bin/python research/carrera/replay_econ.py CAND.py IDS.json [--workers 8] [--out OUT.json]

Prints the mean net cash by item (opponent minus us) over the games, and the days where the margin moves most.
"""
import argparse
import collections
import json
import multiprocessing as mp
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)


def job(args):
    rec, path = args
    import econ          # patches the engine's commit / hire / land / drop functions to log
    import fastarena
    import forceshops
    from cfreplay import tape_agent
    forceshops.force(rec["shops"])
    me = rec["teams"].index("42")
    ours = fastarena.load_agent(path)
    fns = [tape_agent(a) for a in rec["acts"]]
    money = collections.defaultdict(dict)

    def spy(obs, conf=None):
        s = int(obs["step"])
        econ._CUR["step"] = s
        if s % 24 == 23:
            for i, f in enumerate(obs["farms"]):
                money[i][s // 24] = float(f["money"])
        return ours(obs, conf)

    def tape_spy(fn):
        def g(obs, conf=None):
            econ._CUR["step"] = int(obs["step"])
            return fn(obs, conf)
        return g
    fns[me] = spy
    fns[1 - me] = tape_spy(fns[1 - me])
    # econ's logger needs the live farm / private objects: wrap the engine's first step
    K = econ.K
    orig_interp = K.interpreter

    def interp(state, env):
        obs0 = state[0].observation
        if getattr(obs0, "farms", None) and econ._CUR.get("_env") is not env:
            econ._CUR.update(log=[], farms=obs0.farms, _env=env,
                             privates=[s.observation.private for s in state],
                             prices=obs0.market["prices"])
        return orig_interp(state, env)
    K.interpreter = interp
    econ._CUR.clear()
    try:
        res = fastarena.run_game(fns[0], fns[1], rec["seed"])
    finally:
        K.interpreter = orig_interp
    net = [collections.Counter(), collections.Counter()]
    for step, p, op, item, price in econ._CUR.get("log", []):
        if op == "SELL":
            net[p][item] += price
        elif op == "HIRE":
            net[p]["HIRE"] -= price
        elif op == "LAND":
            net[p]["LAND"] -= price
        elif op == "LOST":
            net[p]["LOST"] -= price
        else:
            key = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}.get(item, item)
            net[p][key] -= price
    late = [(step, p == me, item, price) for step, p, op, item, price in econ._CUR.get("log", []) if op == "SELL" and step >= 672]
    return {"id": rec["id"], "opp": rec["teams"][1 - me], "margin": res["rewards"][me] - res["rewards"][1 - me], "late": late,
            "us": dict(net[me]), "op": dict(net[1 - me]),
            "day_diff": {d: money[me].get(d, 0) - money[1 - me].get(d, 0) for d in money[me]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("ids")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out")
    a = ap.parse_args()
    os.environ["PYTHONHASHSEED"] = "0"
    from ab_replay import tapes
    recs = tapes()
    ids = [g for g in json.load(open(a.ids)) if g in recs]
    with mp.get_context("spawn").Pool(a.workers) as pool:
        res = pool.map(job, [(recs[g], os.path.abspath(a.cand)) for g in ids], chunksize=1)
    if a.out:
        json.dump(res, open(a.out, "w"))
    diff = collections.Counter()
    for r in res:
        for k in set(r["us"]) | set(r["op"]):
            diff[k] += (r["op"].get(k, 0) - r["us"].get(k, 0)) / len(res)
    print(f"{len(res)} games, mean margin {st.mean(r['margin'] for r in res):+.0f}; opponent minus us, net cash by item:")
    print("   " + "  ".join(f"{k} {v:+.0f}" for k, v in sorted(diff.items(), key=lambda kv: -abs(kv[1]))[:12]))
    swing = collections.Counter()
    for r in res:
        dd = {int(k): v for k, v in r["day_diff"].items()}
        for d in range(1, 30):
            if d in dd and d - 1 in dd:
                swing[d] += (dd[d] - dd[d - 1]) / len(res)
    print("   mean change of our lead by day (days 10-29): " + " ".join(f"d{d}:{swing[d]:+.0f}" for d in range(10, 30)))


if __name__ == "__main__":
    main()
