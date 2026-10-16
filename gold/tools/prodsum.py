r"""Per-product revenue and units (candidate A vs opponent B) averaged over the games of gstat --json files,
plus money by day checkpoints. .venv\Scripts\python.exe gold\tools\prodsum.py FILE.json [...]
"""
import collections
import json
import sys

PRODS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
DSM = {"WHEAT": 19341, "CARROT": 7825, "TOMATO": 10877, "STRAWBERRY": 30889, "MELON": 12467, "EGG": 9898,
       "MILK": 23794, "WOOL": 21775, "FERTILIZER": 12990}
for path in sys.argv[1:]:
    d = json.load(open(path, encoding="utf-8"))
    rev = [collections.Counter(), collections.Counter()]
    units = [collections.Counter(), collections.Counter()]
    money = [collections.defaultdict(float), collections.defaultdict(float)]
    n = len(d["games"])
    for g in d["games"]:
        a = g["cand_side"]
        for side, who in ((a, 0), (1 - a, 1)):
            for day in g["days"][side]:
                for k, v in day["sell_rev"].items():
                    rev[who][k] += v / n
                for k, v in day["sell_units"].items():
                    units[who][k] += v / n
                money[who][day["day"]] += day["end"]["money"] / n
    print(path)
    print(f"{'product':<11}{'A units':>9}{'A rev':>9}{'B units':>9}{'B rev':>9}{'DSM rev':>9}")
    for p in PRODS:
        print(f"{p:<11}{units[0][p]:>9.0f}{rev[0][p]:>9.0f}{units[1][p]:>9.0f}{rev[1][p]:>9.0f}{DSM[p]:>9}")
    print(f"{'total':<11}{'':>9}{sum(rev[0].values()):>9.0f}{'':>9}{sum(rev[1].values()):>9.0f}{sum(DSM.values()):>9}")
    print("money by day A: " + " ".join(f"d{k}:{money[0][k] / 1000:.1f}k" for k in (5, 8, 10, 12, 15, 20, 25, 29)))
    print("money by day B: " + " ".join(f"d{k}:{money[1][k] / 1000:.1f}k" for k in (5, 8, 10, 12, 15, 20, 25, 29)))
