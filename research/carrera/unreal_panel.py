r"""unreal panel: our candidate takes the seat of unreal's live opponent, unreal replays its recorded actions (same seed,
live shops forced). Answers "in the worlds unreal actually played, would this candidate beat unreal?".

.venv/bin/python research/carrera/unreal_panel.py CAND.py [CAND.py ...] [--workers 8] [--tapes GLOB]

Tapes default to research/carrera/tapes/unreal_*.jsonl.gz (tools/harvest.py --sub 56618268). unreal does not react
to our changes, like every paired replay, so the market side of the result is optimistic when we sell into the same
items. Results are cached per code hash in research/carrera/results_unreal/ (PYTHONHASHSEED 0). Prints each
candidate's W/L against unreal, overall and by world bucket (shop counts at the end), next to the live opponents.
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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
RES = os.path.join(HERE, "results_unreal")
TEAM = "unreal"


def load(pattern):
    recs = {}
    for p in sorted(glob.glob(pattern)):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    if TEAM in r["teams"] and len(r.get("shops") or []) == 8 and r["teams"][0] != r["teams"][1]:
                        recs.setdefault(r["id"], r)
    return recs


def job(args):
    import cfreplay
    rec, path = args
    seat = rec["teams"][1 - rec["teams"].index(TEAM)]
    gid, opp, live, cf, m, o, status = cfreplay.job((rec, seat, path, True))
    return {"id": gid, "live": live, "margin": cf, "money": m, "unreal": o, "status": status}


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
        print(f"{os.path.relpath(path, ROOT)} [{sha(path)}]: {len(todo)} games", flush=True)
        with mp.get_context("spawn").Pool(workers) as pool, open(out, "a") as f:
            for d in pool.imap_unordered(job, [(r, os.path.abspath(path)) for r in todo], chunksize=1):
                f.write(json.dumps(d) + "\n")
                f.flush()
                done[d["id"]] = d
    return {gid: done[gid] for gid in recs if gid in done}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cands", nargs="+")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--tapes", default=os.path.join(HERE, "tapes", "unreal_*.jsonl.gz"))
    a = ap.parse_args()
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(sys.executable, [sys.executable] + sys.argv)
    from prod_profile import features
    recs = load(a.tapes)
    feats = {gid: features(r["shops"]) for gid, r in recs.items()}
    buckets = [("all", lambda f: True), ("STRAW>=6", lambda f: f["STRAWBERRY"] >= 6),
               ("TOMATO==3", lambda f: f["TOMATO"] == 3), ("TOMATO>=4", lambda f: f["TOMATO"] >= 4),
               ("WOOL>=3", lambda f: f["WOOL"] >= 3), ("CARROT>=3", lambda f: f["CARROT"] >= 3),
               ("MILK>=4", lambda f: f["MILK"] >= 4), ("EGG>=3", lambda f: f["EGG"] >= 3)]
    res = {c: run(c, recs, a.workers) for c in a.cands}
    names = [os.path.basename(os.path.dirname(c)) or c for c in a.cands]
    # unreal's tape does not react: when our seat changes the market, its recorded feed buys or sales can fail and
    # its farm collapses. Only games where unreal keeps 90% of its live money (for every candidate) are scored.
    live_u = {g: r["rewards"][r["teams"].index(TEAM)] for g, r in recs.items()}
    intact = {g for g in recs if all(g in res[c] and res[c][g]["unreal"] >= 0.9 * live_u[g] for c in a.cands)}
    print(f"\n{len(recs)} unreal games, {len(intact)} with unreal's tape intact for every candidate "
          f"(collapsed per candidate: {[sum(res[c][g]['unreal'] < 0.7 * live_u[g] for g in res[c]) for c in a.cands]}).")
    print("W-L against unreal and mean margin (ours - unreal) on the intact games")
    print(f"{'bucket':10s} {'n':>4s} {'live opp':>16s} " + " ".join(f"{n[:16]:>18s}" for n in names))
    for bname, cond in buckets:
        ids = [g for g in recs if cond(feats[g]) and g in intact]
        if not ids:
            continue
        live = [res[a.cands[0]][g]["live"] for g in ids if g in res[a.cands[0]]]
        cells = [f"{sum(x > 0 for x in live)}-{sum(x <= 0 for x in live)} {st.mean(live):+6.0f}"]
        for c in a.cands:
            ms = [res[c][g]["margin"] for g in ids if g in res[c]]
            cells.append(f"{sum(x > 0 for x in ms)}-{sum(x <= 0 for x in ms)} {st.mean(ms):+7.0f}" if ms else "-")
        print(f"{bname:10s} {len(ids):4d} {cells[0]:>16s} " + " ".join(f"{x:>18s}" for x in cells[1:]))
    bad = [c for c in a.cands for d in res[c].values() if d["status"] != ["DONE", "DONE"]]
    if bad:
        print("non-DONE statuses:", len(bad))


if __name__ == "__main__":
    main()
