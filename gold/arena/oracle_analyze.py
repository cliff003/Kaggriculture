r"""Per-world analysis of the route oracle: for every world, which forced route beats the champion's own choice
(mean over both seats), grouped by the first two shops (the only information the base's router has on day 6).
.venv\Scripts\python.exe gold\arena\oracle_analyze.py"""
import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
import gstat  # noqa: E402

W = gstat.load_worlds()
res = collections.defaultdict(dict)   # world -> route -> mean diff
for f in glob.glob(os.path.join(ROOT, "gold", "arena", "games", "oracle_route*.json")):
    r = int(re.search(r"oracle_route(\d+)", f).group(1))
    d = json.load(open(f))
    per = collections.defaultdict(list)
    for g in d["games"]:
        per[g["seed"]].append(g["rewards"][g["cand_side"]] - g["rewards"][1 - g["cand_side"]])
    for seed, v in per.items():
        res[seed - 90000][r] = sum(v) / len(v)
routes = sorted({r for v in res.values() for r in v})
print("world first2 | " + " ".join(f"{r:>6}" for r in routes) + " | best")
gain = 0.0
by_pair = collections.defaultdict(list)
for w in sorted(res):
    row = res[w]
    best = max(row, key=row.get)
    pair = "|".join(W[w % len(W)][:2])
    print(f"{w:5d} {pair[:34]:34s} | " + " ".join(f"{row.get(r, 0):+6.0f}" for r in routes) + f" | {best} {row[best]:+.0f}")
    gain += max(0.0, row[best])
    by_pair[pair].append((w, best, row[best]))
print(f"mean gain if the best route were always picked: {gain / max(1, len(res)):+.0f} per game")
