r"""Summarize gstat --json files: candidate (A) mean money, opponent mean, W/L, per seat.
.venv\Scripts\python.exe gold\tools\jsum.py gold\tmp\g003_multi.json gold\tmp\g004_multi.json
"""
import json
import sys

for path in sys.argv[1:]:
    d = json.load(open(path, encoding="utf-8"))
    me, op, w, l = [], [], 0, 0
    for g in d["games"]:
        a_seat = g.get("cand_side", 0)
        r = g["rewards"]
        m, o = (r[0], r[1]) if a_seat == 0 else (r[1], r[0])
        me.append(m)
        op.append(o)
        w += m > o
        l += m < o
    n = len(me)
    print(f"{path}: n {n} A {sum(me) / n:,.0f} B {sum(op) / n:,.0f} diff {(sum(me) - sum(op)) / n:+,.0f} W/L {w}/{l}")
