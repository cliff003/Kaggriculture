r"""Replay live games with a tick-trap guard build and print its measurements (team 42 experiment, 2026-09-26).

    .venv\Scripts\python.exe gold\front\tgrun.py CAND.py ID [ID ...] [--workers 8] [--json OUT.json]

Our seat (team 42) is replaced by CAND, the rival's recorded actions are kept. Prints the margin, when the guard
fired, and the tick cycles' devs (realized minus simulated cash, buy step + sell step).
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


def find_recs(ids):
    want = {int(i) for i in ids}
    out = {}
    pats = [os.path.join(ROOT, "data", "games", "live_*.jsonl.gz"), os.path.join(ROOT, "gold", "front", "front_*.jsonl.gz")]
    for p in pats:
        for f in sorted(glob.glob(p)):
            with gzip.open(f, "rt", encoding="utf-8") as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    if not any(str(i) in line[:40] for i in want):
                        continue
                    r = json.loads(line)
                    if r["id"] in want and r["id"] not in out and "42" in r["teams"]:
                        out[r["id"]] = r
    return out


def play(job):
    cand, rec_path, rid = job
    import forceshops
    import fastarena
    from cfroute import tape_file
    rec = json.load(open(rec_path, encoding="utf-8"))
    me = rec["teams"].index("42")
    tape = tape_file(rec, 1 - me)
    forceshops.force(rec["shops"])
    fns = [None, None]
    fns[me] = fastarena.load_agent(cand)
    fns[1 - me] = fastarena.load_agent(tape)
    r = fastarena.run_game(fns[0], fns[1], rec["seed"])
    tel = fns[me].__globals__.get("TEL", {})
    margin = (r["rewards"][me] or 0) - (r["rewards"][1 - me] or 0)
    return {"id": rid, "opp": rec["teams"][1 - me], "margin": margin, "live": rec["rewards"][me] - rec["rewards"][1 - me],
            "trap_step": tel.get("trap_step"), "prebuy_step": tel.get("prebuy_step"), "cycles": tel.get("cycles", []),
            "devs": tel.get("devs", []), "cf_log": tel.get("cf_log", []), "cf_cycles": tel.get("cf_cycles", [])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--json")
    a = ap.parse_args()
    recs = find_recs(a.ids)
    tmp = os.path.join(ROOT, "gold", "tmp", "tgrun")
    os.makedirs(tmp, exist_ok=True)
    jobs = []
    for rid, r in recs.items():
        p = os.path.join(tmp, f"{rid}.json")
        json.dump(r, open(p, "w", encoding="utf-8"))
        jobs.append((os.path.abspath(a.cand), p, rid))
    with mp.get_context("spawn").Pool(min(a.workers, len(jobs)), maxtasksperchild=1) as pool:
        out = list(pool.imap(play, jobs))
    for g in out:
        cyc = [c[1] for c in g["cycles"] if len(c) < 3 or c[2]]
        first = " ".join(f"{c[1]:+d}" + ("" if len(c) < 3 or c[2] else "x") for c in g["cycles"][:10])
        print(f"{g['id']} {g['opp'][:18]:18s} live {g['live']:+8.0f} replay {g['margin']:+8.0f} trap {g['trap_step']} "
              f"prebuy {g['prebuy_step']} cycles {len(cyc)} sum {sum(cyc):+.0f} "
              f"mean {st.mean(cyc) if cyc else 0:+.0f} | {first}")
    if a.json:
        json.dump(out, open(a.json, "w", encoding="utf-8"))


if __name__ == "__main__":
    main()
