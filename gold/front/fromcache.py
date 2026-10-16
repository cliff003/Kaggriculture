r"""Pick each top-N team's newest submission and its latest episode ids from the cached ListEpisodes files
(data/episodes/*.json modified in the last HOURS hours), without new API calls.
    .venv\Scripts\python.exe gold\front\fromcache.py [--top 120] [--k 3] [--hours 6]
Writes gold/front/pick_eps.json: [[rank, name, team_id, sub, score, [episode ids newest first]], ...]"""
import argparse
import csv
import glob
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=120)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--hours", type=float, default=6)
    a = ap.parse_args()
    lb = sorted(glob.glob(os.path.join(HERE, "kaggriculture-publicleaderboard-*.csv")))[-1]
    rows = list(csv.DictReader(open(lb, encoding="utf-8-sig")))
    top = {int(r["TeamId"]): (int(r["Rank"]), r["TeamName"], float(r["Score"])) for r in rows[:a.top]}
    eps = {}      # episode id -> (endTime, [(teamId, subId, score)])
    now = time.time()
    for f in glob.glob(os.path.join(ROOT, "data", "episodes", "*.json")):
        if now - os.path.getmtime(f) > a.hours * 3600:
            continue
        try:
            data = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        for e in data.get("episodes") or []:
            if e.get("state") != "COMPLETED" or e.get("type") != "EPISODE_TYPE_PUBLIC":
                continue
            ag = [(g.get("teamId"), g.get("submissionId"), g.get("updatedScore") or g.get("initialScore"))
                  for g in (e.get("agents") or [])]
            eps[e["id"]] = (e.get("endTime") or "", ag)
    best = {}
    for eid, (end, ag) in eps.items():
        for tid, sid, sc in ag:
            if tid in top and sid:
                b = best.setdefault(tid, {})
                s = b.setdefault(sid, {"last": "", "eps": []})
                s["last"] = max(s["last"], end)
                s["eps"].append((end, eid))
                s["score"] = sc
    out = []
    for tid, (rank, name, score) in sorted(top.items(), key=lambda kv: kv[1][0]):
        b = best.get(tid)
        if not b:
            out.append([rank, name, tid, None, score, []])
            continue
        sid, s = max(b.items(), key=lambda kv: kv[1]["last"])
        ids = [eid for _, eid in sorted(s["eps"], reverse=True)][:a.k]
        out.append([rank, name, tid, sid, score, ids])
    json.dump(out, open(os.path.join(HERE, "pick_eps.json"), "w", encoding="utf-8"), ensure_ascii=False)
    miss = [r[1] for r in out if not r[5]]
    few = [r[1] for r in out if 0 < len(r[5]) < a.k]
    print(f"{len(out)} teams, {sum(len(r[5]) for r in out)} episodes; none: {len(miss)} {miss[:10]}; fewer than {a.k}: {len(few)}")


if __name__ == "__main__":
    main()
