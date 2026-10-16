r"""Find current submission ids of the top-N leaderboard teams by crawling ListEpisodes from known top submissions.
    .venv\Scripts\python.exe gold\top30\crawl.py [--top 30] [--rounds 3]"""
import argparse, csv, glob, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import kg

_T30 = json.load(open(os.path.join(ROOT, "gold", "top30", "top_subs.json"), encoding="utf-8"))
SEEDS = [56573604, 56559314] + [v["subs"][0]["sub"] for v in _T30.values() if v.get("subs")]


def fetch(sid):
    path = os.path.join(kg.DATA, "episodes", f"{sid}.json")
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < 3 * 3600:
        return json.load(open(path, encoding="utf-8"))
    data = kg.web("POST", kg.LIST_EPISODES_URL, 6.0, json={"submissionId": sid}).json()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, "w", encoding="utf-8"))
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=120)
    ap.add_argument("--rounds", type=int, default=4)
    a = ap.parse_args()
    lb = sorted(glob.glob(os.path.join(HERE, "kaggriculture-publicleaderboard-*.csv")))[-1]
    rows = list(csv.DictReader(open(lb, encoding="utf-8-sig")))
    top = {int(r["TeamId"]): (int(r["Rank"]), r["TeamName"], float(r["Score"])) for r in rows[:a.top]}
    subs = {}          # teamId -> {subId: (last end time, n episodes seen, last score)}
    seen = set()
    frontier = list(SEEDS)
    for rnd in range(a.rounds):
        nxt = []
        for sid in frontier:
            if sid in seen:
                continue
            seen.add(sid)
            try:
                data = fetch(sid)
            except Exception as e:
                print("fail", sid, e)
                continue
            for e in data.get("episodes") or []:
                for g in e.get("agents") or []:
                    tid, s = g.get("teamId"), g.get("submissionId")
                    if tid in top and s:
                        rec = subs.setdefault(tid, {}).setdefault(s, ["", 0, None])
                        rec[0] = max(rec[0], e.get("endTime") or "")
                        rec[1] += 1
                        rec[2] = g.get("updatedScore") or g.get("initialScore")
                        if s not in seen:
                            nxt.append(s)
        found = len(subs)
        print(f"round {rnd}: queried {len(seen)} submissions, top teams found {found}/{len(top)}", flush=True)
        # only keep the newest submission per team for the next round
        frontier = []
        for tid, d in subs.items():
            best = max(d.items(), key=lambda kv: kv[1][0])[0]
            if best not in seen:
                frontier.append(best)
        if not frontier:
            break
    out = {}
    for tid, (rank, name, score) in sorted(top.items(), key=lambda kv: kv[1][0]):
        d = subs.get(tid, {})
        lst = sorted(d.items(), key=lambda kv: kv[1][0], reverse=True)
        out[str(tid)] = {"rank": rank, "name": name, "score": score,
                         "subs": [{"sub": s, "last": v[0], "n": v[1], "score": v[2]} for s, v in lst]}
        print(rank, name, score, [(s, v[0][:16], round(v[2] or 0)) for s, v in lst[:3]])
    json.dump(out, open(os.path.join(HERE, "top_subs.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
