r"""Item breakdown of a candidate against unreal's tapes (unreal_panel.py setup): our candidate in the seat of unreal's
live opponent, both sides' sales / purchases / hires / land / lost units logged by tools/econ.py hooks.

.venv/bin/python research/carrera/unreal_econ.py CAND.py [--workers 8] [--out OUT.json]

Scores only games where unreal keeps 90% of its live money (its tape does not react; see unreal_panel.py).
"""
import argparse
import collections
import json
import multiprocessing as mp
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))


def job(args):
    import replay_econ
    return replay_econ.job(args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out")
    a = ap.parse_args()
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(sys.executable, [sys.executable] + sys.argv)
    import unreal_panel
    recs = unreal_panel.load(os.path.join(HERE, "tapes", "unreal_*.jsonl.gz"))
    live_u = {g: r["rewards"][r["teams"].index("unreal")] for g, r in recs.items()}
    todo = []
    for g, r in recs.items():
        r = dict(r)
        r["teams"] = ["42" if t != "unreal" else t for t in r["teams"]]
        todo.append((r, os.path.abspath(a.cand)))
    with mp.get_context("spawn").Pool(a.workers) as pool:
        res = pool.map(job, todo, chunksize=1)
    if a.out:
        json.dump(res, open(a.out, "w"))
    # the panel cache of this candidate holds unreal's money in each game (same code, same PYTHONHASHSEED)
    cache = os.path.join(unreal_panel.RES, f"{unreal_panel.sha(a.cand)}.jsonl")
    if os.path.exists(cache):
        um = {d["id"]: d["unreal"] for d in map(json.loads, open(cache))}
        keep = [d for d in res if d["id"] in um and um[d["id"]] >= 0.9 * live_u[d["id"]]]
    else:
        print("no unreal_panel.py cache for this candidate: run it first to drop collapsed games; scoring all games")
        keep = res
    diff = collections.Counter()
    for r in keep:
        for k in set(r["us"]) | set(r["op"]):
            diff[k] += (r["op"].get(k, 0) - r["us"].get(k, 0)) / len(keep)
    print(f"{len(keep)} games, mean margin {st.mean(r['margin'] for r in keep):+.0f}; unreal minus us, net cash by item:")
    print("   " + "  ".join(f"{k} {v:+.0f}" for k, v in sorted(diff.items(), key=lambda kv: -abs(kv[1]))))


if __name__ == "__main__":
    main()
