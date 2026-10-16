r"""Pick one current submission per leaderboard team from gold/front/top_subs.json (newest with >= MIN episodes seen,
else the newest) and write gold/front/pick.json as [rank, name, sub, score, last].
    .venv\Scripts\python.exe gold\front\pick.py [--lo 1] [--hi 120] [--min 3]"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lo", type=int, default=1)
    ap.add_argument("--hi", type=int, default=120)
    ap.add_argument("--min", type=int, default=3)
    a = ap.parse_args()
    d = json.load(open(os.path.join(HERE, "top_subs.json"), encoding="utf-8"))
    out = []
    for tid, v in sorted(d.items(), key=lambda kv: kv[1]["rank"]):
        if not (a.lo <= v["rank"] <= a.hi) or not v["subs"]:
            continue
        subs = v["subs"]
        best = next((s for s in subs if s["n"] >= a.min), subs[0])
        out.append([v["rank"], v["name"], best["sub"], round(best["score"] or 0), best["last"][:16]])
    json.dump(out, open(os.path.join(HERE, "pick.json"), "w", encoding="utf-8"), ensure_ascii=False)
    for r in out:
        print(*r)


if __name__ == "__main__":
    main()
