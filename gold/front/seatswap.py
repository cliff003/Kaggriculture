r"""Seat swap: for every harvested game of the target teams, replay the game with CAND in the team's seat against the
opponent's recorded tape (same seed, forced shops) and compare CAND's margin with the team's live margin.

    .venv\Scripts\python.exe gold\front\seatswap.py CAND.py [--lineage cha22 | --teams A B ...] [--workers 12]
        [--out gold/front/seatswap_<lineage>.json]
"""
import argparse
import collections
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
TAPES = os.path.join(ROOT, "gold", "tmp", "tapes")
TAPE_SRC = '''import json
_T = json.load(open(r"{path}"))
_PASS = {{"farmer": ["PASS"], "hands": [], "market": []}}


def agent(observation, configuration=None):
    t = int(observation["step"])
    a = _T[t] if 0 <= t < len(_T) else None
    return json.loads(json.dumps(a)) if isinstance(a, dict) else dict(_PASS)
'''


def tape_file(rec, seat):
    os.makedirs(TAPES, exist_ok=True)
    js = os.path.join(TAPES, f"{rec['id']}_{seat}.json")
    py = os.path.join(TAPES, f"tape_{rec['id']}_{seat}.py")
    if not os.path.exists(py):
        json.dump(rec["acts"][seat][1:], open(js, "w"))
        open(py, "w", encoding="utf-8").write(TAPE_SRC.format(path=js))
    return py


def main():
    import gstat
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("--lineage")
    ap.add_argument("--teams", nargs="*")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out")
    a = ap.parse_args()
    cls = json.load(open(os.path.join(HERE, "classify.json"), encoding="utf-8"))
    rank = {x["name"]: x["rank"] for x in cls}
    if a.teams:
        teams = set(a.teams)
    else:
        teams = {x["name"] for x in cls if x.get("lineage") == a.lineage}
    recs = {}
    for p in glob.glob(os.path.join(HERE, "front_*.jsonl.gz")):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    recs[r["id"]] = r
    jobs, meta = [], []
    for r in recs.values():
        if len(r.get("shops") or []) < 8:
            continue
        for seat, t in enumerate(r["teams"]):
            if t in teams:
                tape = tape_file(r, 1 - seat)
                seats = (a.cand, tape) if seat == 0 else (tape, a.cand)
                jobs.append((seats[0], seats[1], r["seed"], seat, r["shops"]))
                meta.append((r, t, seat))
    print(f"{len(teams)} teams, {len(jobs)} replays", flush=True)
    with mp.get_context("spawn").Pool(a.workers, maxtasksperchild=1) as pool:
        out = list(pool.imap(gstat.play_one, jobs))
    per = collections.defaultdict(list)
    rows = []
    for (r, t, seat), g in zip(meta, out):
        live = (r["rewards"][seat] or 0) - (r["rewards"][1 - seat] or 0)
        cand = (g["rewards"][seat] or 0) - (g["rewards"][1 - seat] or 0)
        per[t].append((live, cand))
        rows.append({"id": r["id"], "team": t, "opp": r["teams"][1 - seat], "live": live, "cand": cand,
                     "team_money": r["rewards"][seat], "cand_money": g["rewards"][seat]})
    print(f"{'rank':>4} {'team':20s} {'n':>2} {'team W':>6} {'cand W':>6} {'team m':>8} {'cand m':>8} {'diff':>7}")
    allw = [0, 0, 0]
    for t, v in sorted(per.items(), key=lambda kv: rank.get(kv[0], 999)):
        wt = sum(x > 0 for x, _ in v)
        wc = sum(y > 0 for _, y in v)
        allw[0] += wt; allw[1] += wc; allw[2] += len(v)
        print(f"{rank.get(t, 0):4d} {t[:20]:20s} {len(v):2d} {wt:6d} {wc:6d} {st.mean(x for x, _ in v):+8.0f} "
              f"{st.mean(y for _, y in v):+8.0f} {st.mean(y - x for x, y in v):+7.0f}")
    print(f"total games {allw[2]}: team wins {allw[0]}, cand wins {allw[1]}")
    json.dump(rows, open(a.out or os.path.join(HERE, f"seatswap_{a.lineage or 'teams'}.json"), "w",
                         encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
