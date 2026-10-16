r"""Shadow-diff every harvested game of the teams of one lineage against a reference agent, in parallel.
    .venv\Scripts\python.exe gold\front\shadow_batch.py --lineage cha22 [--ref research/panel/cha22/main.py]
        [--workers 12] [--out gold/front/shadow_cha22.json]
Team lineages come from gold/front/classify.json; records from gold/front/front_*.jsonl.gz."""
import argparse
import glob
import gzip
import json
import multiprocessing as mp
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def job(args):
    rec, team, ref = args
    import shadow
    try:
        return shadow.run(rec, team, ref)
    except Exception as e:
        return {"id": rec["id"], "team": team, "error": repr(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lineage", default="cha22")
    ap.add_argument("--ref", default=os.path.join(ROOT, "research", "panel", "cha22", "main.py"))
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out")
    a = ap.parse_args()
    cls = json.load(open(os.path.join(HERE, "classify.json"), encoding="utf-8"))
    teams = {x["name"]: x["rank"] for x in cls if x.get("lineage") == a.lineage}
    recs = {}
    for p in glob.glob(os.path.join(HERE, "front_*.jsonl.gz")):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    recs[r["id"]] = r
    jobs = []
    for r in recs.values():
        for t in r["teams"]:
            if t in teams:
                jobs.append((r, t, a.ref))
    print(f"{len(teams)} teams, {len(jobs)} team-games", flush=True)
    with mp.get_context("spawn").Pool(a.workers, maxtasksperchild=4) as pool:
        out = list(pool.imap_unordered(job, jobs))
    for g in out:
        g["rank"] = teams.get(g["team"])
    json.dump(out, open(a.out or os.path.join(HERE, f"shadow_{a.lineage}.json"), "w", encoding="utf-8"),
              ensure_ascii=False)
    for g in sorted(out, key=lambda g: (g["rank"] or 0, g["id"])):
        if "error" in g:
            print(g["rank"], g["team"], "ERROR", g["error"])
            continue
        lg = g["log"]
        n = sum(lg["unit_n"].values())
        s = sum(lg["unit_same"].values())
        print(f"#{g['rank']:3d} {g['team'][:18]:18s} {g['id']} server {g['server']} local {g['local']} "
              f"unit agree {s / max(1, n):.3f} first div {lg['first_unit_div'][0] if lg['first_unit_div'] else None} "
              f"market diffs {len(lg['market'])}", flush=True)


if __name__ == "__main__":
    main()
