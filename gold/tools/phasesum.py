r"""Revenue per product by phase (days 0-9 / 10-19 / 20-29) for the candidate in gstat --json files, vs DSM.
.venv\Scripts\python.exe gold\tools\phasesum.py FILE.json
"""
import collections
import json
import sys

PRODS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
DSM = {"WHEAT": (570, 7407, 11365), "CARROT": (0, 1145, 6679), "TOMATO": (0, 1237, 9641),
       "STRAWBERRY": (0, 17085, 13804), "MELON": (0, 12467, 0), "EGG": (0, 4251, 5647),
       "MILK": (2237, 13122, 8435), "WOOL": (5519, 9085, 7171), "FERTILIZER": (5460, 6275, 1255)}
for path in sys.argv[1:]:
    d = json.load(open(path, encoding="utf-8"))
    n = len(d["games"])
    rev = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    for g in d["games"]:
        a = g["cand_side"]
        for day in g["days"][a]:
            ph = min(2, day["day"] // 10)
            for k, v in day["sell_rev"].items():
                rev[k][ph] += v / n
    print(path)
    print(f"{'product':<11}{'d0-9':>8}{'d10-19':>8}{'d20-29':>8}  | DSM {'d0-9':>7}{'d10-19':>8}{'d20-29':>8}")
    tot = [0, 0, 0]
    dt = [0, 0, 0]
    for p in PRODS:
        r = rev[p]
        print(f"{p:<11}{r[0]:>8.0f}{r[1]:>8.0f}{r[2]:>8.0f}  |     {DSM[p][0]:>7}{DSM[p][1]:>8}{DSM[p][2]:>8}")
        for i in range(3):
            tot[i] += r[i]
            dt[i] += DSM[p][i]
    print(f"{'total':<11}{tot[0]:>8.0f}{tot[1]:>8.0f}{tot[2]:>8.0f}  |     {dt[0]:>7}{dt[1]:>8}{dt[2]:>8}")
