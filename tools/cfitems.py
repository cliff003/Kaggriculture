r"""Per-product effect of a candidate versus a baseline in counterfactual replays of live games.

.venv\Scripts\python.exe tools\cfitems.py GAMES.jsonl.gz TEAM BASE_MAIN_PY CAND_MAIN_PY [--workers 12] [--ids ...]

Both agents replay every game against the opponent's recorded actions (see cfreplay.py). For each
product it prints the mean change (candidate minus baseline) of our sales revenue and of the rival's,
so the relative effect of a market layer can be traced to the goods that carry it.
"""
import argparse
import collections
import gzip
import json
import multiprocessing as mp
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def job(args):
    import econ
    import fastarena
    from cfreplay import tape_agent
    rec, team, paths = args
    me = rec["teams"].index(team)
    out = []
    for path in paths:
        ours = fastarena.load_agent(path)
        theirs = tape_agent(rec["acts"][1 - me])
        agents = [ours, theirs] if me == 0 else [theirs, ours]
        econ._CUR.update(log=[], farms=[None, None], privates=[None, None], step=0, prices={})
        r = fastarena.run_game(agents[0], agents[1], rec["seed"], record=True)
        acts = [[None] + [h[i]["action"] for h in r["history"]] for i in range(2)]
        econ.resim(dict(rec, acts=acts))
        rev = collections.Counter()
        for s, p, op, it, pr in econ._CUR["log"]:
            if op == "SELL":
                rev[("us" if p == me else "them", it)] += pr
        out.append((r["rewards"][me] - r["rewards"][1 - me], dict(rev)))
    return rec["id"], out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("team")
    ap.add_argument("base")
    ap.add_argument("cand")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--ids", type=int, nargs="*")
    a = ap.parse_args()
    games = []
    for line in gzip.open(a.games, "rt", encoding="utf-8"):
        g = json.loads(line)
        if a.team in g["teams"] and (not a.ids or g["id"] in a.ids):
            games.append(g)
    paths = [os.path.abspath(a.base), os.path.abspath(a.cand)]
    with mp.get_context("spawn").Pool(a.workers) as pool:
        res = pool.map(job, [(g, a.team, paths) for g in games])
    n = len(res)
    dm = sum(o[1][0] - o[0][0] for _, o in res) / n
    items = sorted({k[1] for _, o in res for x in o for k in x[1]})
    print(f"games {n}  mean margin change {dm:+.0f}")
    print(f"{'item':10s} {'our rev change':>15s} {'rival rev change':>17s} {'relative':>9s}")
    for it in items:
        du = sum(o[1][1].get(("us", it), 0) - o[0][1].get(("us", it), 0) for _, o in res) / n
        dt = sum(o[1][1].get(("them", it), 0) - o[0][1].get(("them", it), 0) for _, o in res) / n
        print(f"{it:10s} {du:+15.0f} {dt:+17.0f} {du - dt:+9.0f}")


if __name__ == "__main__":
    main()
