r"""Paired runs with our agent in seat 1 (so it can see the seat-0 opponent's same-step orders).

    .venv\Scripts\python.exe gold\oracle\run_oracle.py OPP_BUS VARIANT1 [VARIANT2 ...] [--worlds FILE] [--per 2] [--seed0 90000]

Every variant plays the same (world, seed) list. Prints wins / mean margin per variant and paired deltas vs the first.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def main():
    import gstat
    ap = argparse.ArgumentParser()
    ap.add_argument("opp")
    ap.add_argument("variants", nargs="+")
    ap.add_argument("--worlds", default=os.path.join(ROOT, "gold", "arena", "famworlds.json"))
    ap.add_argument("--per", type=int, default=2)
    ap.add_argument("--seed0", type=int, default=90000)
    ap.add_argument("--workers", type=int, default=14)
    ap.add_argument("--json")
    a = ap.parse_args()
    worlds = json.load(open(a.worlds))
    opp = os.path.join(ROOT, "gold", "builds", a.opp, "main.py")
    jobs, meta = [], []
    for v in a.variants:
        path = os.path.join(ROOT, "gold", "builds", v, "main.py")
        for w, shops in enumerate(worlds):
            for r in range(a.per):
                seed = a.seed0 + w * a.per + r
                jobs.append((opp, path, seed, 1, shops))
                meta.append((v, w, seed))
    with mp.get_context("spawn").Pool(a.workers, maxtasksperchild=4) as pool:
        out = list(pool.imap(gstat.play_one, jobs))
    res = {}
    for (v, w, seed), g in zip(meta, out):
        m, o = g["rewards"][1] or 0, g["rewards"][0] or 0
        res.setdefault(v, {})[(w, seed)] = (m - o, m, o, g.get("errors"))
    base = a.variants[0]
    for v in a.variants:
        r = res[v]
        wins = sum(1 for x in r.values() if x[0] > 0)
        mean = sum(x[0] for x in r.values()) / len(r)
        errs = sum(sum(x[3] or [0]) for x in r.values())
        line = f"{v:14s} wins {wins}/{len(r)} mean margin {mean:+.0f} ours {sum(x[1] for x in r.values())/len(r):.0f} opp {sum(x[2] for x in r.values())/len(r):.0f} errors {errs}"
        if v != base:
            d = [r[k][0] - res[base][k][0] for k in r]
            flips_up = sum(1 for k in r if r[k][0] > 0 >= res[base][k][0])
            flips_dn = sum(1 for k in r if r[k][0] <= 0 < res[base][k][0])
            import statistics
            se = statistics.pstdev(d) / max(1, len(d)) ** 0.5
            line += f" | paired {sum(d)/len(d):+.0f} (se {se:.0f}) flips +{flips_up} -{flips_dn}"
        print(line, flush=True)
    if a.json:
        json.dump({v: {f"{k[0]}_{k[1]}": x for k, x in r.items()} for v, r in res.items()}, open(a.json, "w"))


if __name__ == "__main__":
    main()
