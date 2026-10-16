r"""Paired live-tape replay for V10_CarreraGT candidates (the opponent keeps its recorded actions, live shops forced).

.venv/bin/python research/carrera/ab_replay.py BASE.py CAND.py [CAND.py ...] [--workers 8] [--only-ids FILE.json]

Tapes: data/games/live_*.jsonl.gz plus research/carrera/tapes/*.jsonl.gz, deduplicated by episode id, games of
team 42 with all 8 shops recorded. Every agent's results are cached per code hash in research/carrera/results/
(one JSON line per game), so the base runs once and interrupted runs resume. PYTHONHASHSEED is fixed to 0 so a
rerun reproduces every game exactly. Prints, per candidate against the base: W/L/T, flips, mean change, and the
changed games.
"""
import argparse
import glob
import gzip
import hashlib
import json
import multiprocessing as mp
import os
import statistics as st
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
RES = os.path.join(HERE, "results")


def tapes():
    seen = {}
    files = sorted(glob.glob(os.path.join(ROOT, "data", "games", "live_*.jsonl.gz"))) + \
        sorted(glob.glob(os.path.join(HERE, "tapes", "*.jsonl.gz")))
    for p in files:
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                except Exception:
                    break
                if "42" in r["teams"] and len(r.get("shops") or []) == 8:
                    seen.setdefault(r["id"], r)
    return seen


def job(args):
    import cfreplay
    rec, path = args
    t = time.time()
    gid, opp, live, cf, m, o, status = cfreplay.job((rec, "42", path, True))
    return {"id": gid, "opp": opp, "live": live, "margin": cf, "money": m, "opp_money": o, "status": status,
            "wall": round(time.time() - t, 2)}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]


def run(path, recs, workers):
    os.makedirs(RES, exist_ok=True)
    out = os.path.join(RES, f"{sha(path)}.jsonl")
    done = {}
    if os.path.exists(out):
        for line in open(out):
            d = json.loads(line)
            done[d["id"]] = d
    todo = [r for gid, r in recs.items() if gid not in done]
    if todo:
        print(f"{os.path.relpath(path, ROOT)} [{sha(path)}]: {len(todo)} games to replay", flush=True)
        t0 = time.time()
        with mp.get_context("spawn").Pool(workers) as pool, open(out, "a") as f:
            for k, d in enumerate(pool.imap_unordered(job, [(r, os.path.abspath(path)) for r in todo], chunksize=2)):
                f.write(json.dumps(d) + "\n")
                f.flush()
                done[d["id"]] = d
                if (k + 1) % 100 == 0:
                    print(f"   {k + 1}/{len(todo)}  {time.time() - t0:.0f}s", flush=True)
    return {gid: done[gid] for gid in recs if gid in done}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("cands", nargs="+")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--only-ids")
    a = ap.parse_args()
    os.environ["PYTHONHASHSEED"] = "0"   # inherited by the spawned workers
    recs = tapes()
    if a.only_ids:
        keep = set(json.load(open(a.only_ids)))
        recs = {k: v for k, v in recs.items() if k in keep}
    print(f"games {len(recs)}")
    base = run(a.base, recs, a.workers)
    wl = lambda xs: f"{sum(x > 0 for x in xs)}/{sum(x < 0 for x in xs)}/{sum(x == 0 for x in xs)}"
    print(f"\nlive (as played):  W/L/T {wl([d['live'] for d in base.values()])}")
    print(f"base {os.path.relpath(a.base, ROOT)}: W/L/T {wl([d['margin'] for d in base.values()])}, "
          f"reproduces live in {sum(d['margin'] == d['live'] for d in base.values())} games")
    for c in a.cands:
        cand = run(c, recs, a.workers)
        ids = [g for g in base if g in cand]
        ch = [cand[g]["margin"] - base[g]["margin"] for g in ids]
        up = [g for g in ids if base[g]["margin"] <= 0 < cand[g]["margin"]]
        down = [g for g in ids if cand[g]["margin"] <= 0 < base[g]["margin"]]
        bad = [g for g in ids if cand[g]["status"] != ["DONE", "DONE"]]
        print(f"\ncand {os.path.relpath(c, ROOT)} [{sha(c)}]: W/L/T {wl([cand[g]['margin'] for g in ids])}, "
              f"flips up {len(up)} down {len(down)}, mean change {st.mean(ch):+.1f}, changed games {sum(x != 0 for x in ch)}, "
              f"better {sum(x > 0 for x in ch)} worse {sum(x < 0 for x in ch)}, not DONE {len(bad)}")
        for g in up + down:
            print(f"   {'UP  ' if g in up else 'DOWN'} {g} {base[g]['opp'][:20]:20s} {base[g]['margin']:+8.0f} -> {cand[g]['margin']:+8.0f}")
        worst = sorted(ids, key=lambda g: cand[g]["margin"] - base[g]["margin"])[:5]
        print("   largest drops:", [(g, round(cand[g]["margin"] - base[g]["margin"])) for g in worst if cand[g]["margin"] < base[g]["margin"]])


if __name__ == "__main__":
    main()
