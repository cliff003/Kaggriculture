r"""Summarize acct.py output.  acctsum.py FILE.jsonl [--side-name SUBSTR]

Prints per-agent mean final money, W/L, and per-item units/avg price/revenue, spend breakdown.
"""
import collections
import json
import os
import statistics
import sys

ITEMS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def name(p):
    return os.path.basename(os.path.dirname(p)) or p


def main():
    path = sys.argv[1]
    recs = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    per = collections.defaultdict(lambda: {"money": [], "margin": [], "w": 0, "l": 0, "t": 0,
                                           "sales": collections.defaultdict(lambda: [0, 0.0]),
                                           "spend": collections.Counter(), "hires": 0, "n": 0})
    for r in recs:
        names = [name(r["a"]), name(r["b"])]
        if names[0] == names[1]:
            names = [names[0] + "#0", names[1] + "#1"]
        for i in range(2):
            d = per[names[i]]
            d["n"] += 1
            m, o = r["rewards"][i], r["rewards"][1 - i]
            d["money"].append(m)
            d["margin"].append(m - o)
            d["w" if m > o else ("l" if m < o else "t")] += 1
            s = r["sides"][i]
            for k, (u, rev) in s["sales"].items():
                d["sales"][k][0] += u
                d["sales"][k][1] += rev
            for k, v in s["spend"].items():
                d["spend"][k] += v
            d["hires"] += s["hires"]
    for nm, d in per.items():
        n = d["n"]
        print(f"== {nm}: n={n} money {statistics.mean(d['money']):.0f} margin {statistics.mean(d['margin']):+.0f} "
              f"W/L/T {d['w']}/{d['l']}/{d['t']} hires/game {d['hires'] / n:.0f}")
        tot = 0
        for k in ITEMS:
            u, rev = d["sales"].get(k, [0, 0])
            if u:
                tot += rev
                print(f"   {k:11s} {u / n:7.1f} u  avg {rev / u:6.1f}  rev {rev / n:8.0f}")
        print(f"   {'SALES':11s} {tot / n:8.0f}")
        for k, v in sorted(d["spend"].items(), key=lambda kv: -kv[1]):
            print(f"   spend {k:18s} {v / n:8.0f}")


if __name__ == "__main__":
    main()
