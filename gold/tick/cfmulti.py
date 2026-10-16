r"""Live-tape replay of several candidates at once, reusing base margins from an earlier cfroute --json file.

    .venv\Scripts\python.exe gold\tick\cfmulti.py BASE_JSON CAND.py [CAND.py ...] [--workers 12] [--out OUT.json]

BASE_JSON: a cfroute.py --json output (its "base" margins are reused; every game in it is replayed for each CAND).
Prints wins, mean margin change vs base with its standard error, flips, per candidate.
"""
import argparse
import glob
import gzip
import json
import multiprocessing as mp
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def main():
    import gstat
    from cfroute import tape_file
    ap = argparse.ArgumentParser()
    ap.add_argument("base_json")
    ap.add_argument("cands", nargs="+")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out")
    a = ap.parse_args()
    base = json.load(open(a.base_json, encoding="utf-8"))
    recs = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "games", "live_*.jsonl.gz"))):
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                if str(r["id"]) in base and r["id"] not in recs:
                    r["_me"] = r["teams"].index("42")
                    recs[r["id"]] = r
    jobs, meta = [], []
    for rid, r in recs.items():
        me = r["_me"]
        tape = tape_file(r, 1 - me)
        for c in a.cands:
            seats = (c, tape) if me == 0 else (tape, c)
            jobs.append((seats[0], seats[1], r["seed"], me, r["shops"]))
            meta.append((rid, c))
    print(f"{len(recs)} games, {len(jobs)} replays", flush=True)
    with mp.get_context("spawn").Pool(a.workers, maxtasksperchild=1) as pool:
        out = list(pool.imap(gstat.play_one, jobs))
    res = {}
    for (rid, c), g in zip(meta, out):
        me = g["cand_side"]
        res.setdefault(c, {})[str(rid)] = (g["rewards"][me] or 0) - (g["rewards"][1 - me] or 0)
    wb = sum(1 for k in base if base[k]["base"] > 0)
    print(f"base wins {wb}/{len(base)}")
    for c in a.cands:
        d = [res[c][k] - base[k]["base"] for k in res[c]]
        w = sum(1 for k in res[c] if res[c][k] > 0)
        fw = sum(1 for k in res[c] if base[k]["base"] <= 0 < res[c][k])
        fl = sum(1 for k in res[c] if res[c][k] <= 0 < base[k]["base"])
        print(f"{c}: wins {w}/{len(d)}  mean {st.mean(d):+.0f} se {st.stdev(d) / len(d) ** 0.5:.0f} "
              f"median {st.median(d):+.0f}  flips +{fw} -{fl}", flush=True)
    if a.out:
        json.dump(res, open(a.out, "w"), ensure_ascii=False)


if __name__ == "__main__":
    main()
