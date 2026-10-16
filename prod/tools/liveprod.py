r"""Per-product sales (units, revenue) of both sides in recorded live games, by opponent group.

liveprod.py GAMES.jsonl.gz TEAM [--min-opp-score 2700] [--max N]
Replays each recorded game (both sides from their actions) with the accounting hook and prints mean
units/revenue per product for TEAM and its opponents, split into opponents rated above/below the cut.
"""
import argparse
import collections
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
import acct  # noqa: E402
import fastarena  # noqa: E402
from fidelity import tape_agent  # noqa: E402

ITEMS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("team")
    ap.add_argument("--min-opp-score", type=float, default=2700)
    ap.add_argument("--max", type=int, default=1000)
    a = ap.parse_args()
    recs = [json.loads(l) for l in gzip.open(a.games, "rt", encoding="utf-8") if l.strip()]
    recs = [r for r in recs if a.team in r["teams"]][:a.max]
    agg = {}
    for r in recs:
        me = r["teams"].index(a.team)
        sc = (r.get("scores") or [0, 0])[1 - me] or 0
        grp = "strong" if sc >= a.min_opp_score else "other"
        acct._CUR["log"] = []
        acct._CUR["snaps"] = []
        acct._CUR["farms"] = None
        res = fastarena.run_game(tape_agent(r["acts"][0]), tape_agent(r["acts"][1]), r["seed"])
        for side, who in ((me, "us"), (1 - me, "opp")):
            s = acct.summarize(acct._CUR["log"], side)
            d = agg.setdefault((grp, who), {"n": 0, "money": 0.0, "units": collections.Counter(), "rev": collections.Counter(),
                                             "spend": collections.Counter()})
            d["n"] += 1
            d["money"] += res["rewards"][side]
            for k, (u, v) in s["sales"].items():
                d["units"][k] += u
                d["rev"][k] += v
            for k, v in s["spend"].items():
                d["spend"][k.split(":")[0] + (":" + k.split(":")[1] if k.startswith(("ANIMAL", "SEED")) else "")] += v
    for grp in ("strong", "other"):
        if (grp, "us") not in agg:
            continue
        u, o = agg[(grp, "us")], agg[(grp, "opp")]
        n = u["n"]
        print(f"== opponents {grp} (n={n})  money us {u['money'] / n:.0f} opp {o['money'] / n:.0f}")
        print("   item          us_units  us_rev |  opp_units  opp_rev")
        for k in ITEMS:
            print(f"   {k:12s} {u['units'][k] / n:8.0f} {u['rev'][k] / n:8.0f} | {o['units'][k] / n:8.0f} {o['rev'][k] / n:8.0f}")
        keys = sorted(set(u["spend"]) | set(o["spend"]), key=lambda k: -(u["spend"][k] + o["spend"][k]))
        print("   spend: " + "  ".join(f"{k} {u['spend'][k] / n:.0f}/{o['spend'][k] / n:.0f}" for k in keys[:14]))


if __name__ == "__main__":
    main()
