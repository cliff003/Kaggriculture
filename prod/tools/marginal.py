r"""Marginal value of selling extra units of each item on each day against a fixed rival schedule.
marginal.py RAW.jsonl SIDE [K]"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mktsim

recs = mktsim.load(sys.argv[1])
side = int(sys.argv[2])
k = int(sys.argv[3]) if len(sys.argv) > 3 else 10
items = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
days = [2, 5, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
res = {it: {d: [0.0, 0.0] for d in days} for it in items}
for rec in recs:
    rival = mktsim.rival_flows(rec, side)
    o0, r0, *_ = mktsim.simulate(rec["shops"], rival, {})
    for it in items:
        for d in days:
            ours = {d * 24 + 12: {it: k}}
            o, r, *_ = mktsim.simulate(rec["shops"], rival, ours, items=[it])
            res[it][d][0] += (o[it]) / k
            res[it][d][1] += (r0[it] - r[it]) / k
n = len(recs)
print("item       " + " ".join(f"d{d:<9d}" for d in days))
for it in items:
    print(f"{it:10s} " + " ".join(f"{res[it][d][0]/n:4.0f}/{res[it][d][1]/n:<4.0f} " for d in days))
print("cell = our avg price per unit / rival revenue lost per unit")
