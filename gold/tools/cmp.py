r"""Paired comparison of two gstat --json runs on the same seeds/seats (ideally --worlds):
per-product revenue both sides and the paired diff with a per-seed standard error.
.venv\Scripts\python.exe gold\tools\cmp.py BASE.json NEW.json
"""
import collections
import json
import math
import sys

PRODS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    out = {}
    for g in d["games"]:
        a = g["cand_side"]
        rev = [collections.Counter(), collections.Counter()]
        for who, side in ((0, a), (1, 1 - a)):
            for day in g["days"][side]:
                rev[who].update(day["sell_rev"])
        r = g["rewards"]
        out[(g["seed"], a)] = (r[a], r[1 - a], rev)
    return out


A, B = load(sys.argv[1]), load(sys.argv[2])
keys = sorted(set(A) & set(B))
n = len(keys)
dd = [(B[k][0] - B[k][1]) - (A[k][0] - A[k][1]) for k in keys]
by_seed = collections.defaultdict(list)
for k, x in zip(keys, dd):
    by_seed[k[0]].append(x)
sm = [sum(v) / len(v) for v in by_seed.values()]
mean = sum(sm) / len(sm)
se = math.sqrt(sum((x - mean) ** 2 for x in sm) / (len(sm) - 1) / len(sm)) if len(sm) > 1 else 0
print(f"games {n}  diff change {mean:+,.0f} (se {se:,.0f})  ours {sum(B[k][0] - A[k][0] for k in keys) / n:+,.0f}  opp {sum(B[k][1] - A[k][1] for k in keys) / n:+,.0f}")
print(f"{'product':<11}{'ours base':>10}{'ours new':>10}{'opp base':>10}{'opp new':>10}")
for p in PRODS:
    ob = sum(A[k][2][0][p] for k in keys) / n
    on = sum(B[k][2][0][p] for k in keys) / n
    pb = sum(A[k][2][1][p] for k in keys) / n
    pn = sum(B[k][2][1][p] for k in keys) / n
    print(f"{p:<11}{ob:>10.0f}{on:>10.0f}{pb:>10.0f}{pn:>10.0f}")
