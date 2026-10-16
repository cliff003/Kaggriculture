r"""Scan live replays for BUY_PRODUCT orders (WHEAT, FERTILIZER): when each side buys, how much, at what slot, and the
market inventory/price at that moment. Front-running idea check.
.venv\Scripts\python.exe gold\tools\buyscan.py gold\replays\*.json"""
import collections
import glob
import json
import sys

files = [f for a in sys.argv[1:] for f in glob.glob(a)]
for f in files:
    d = json.load(open(f))
    steps = d["steps"]

    print(f"== {f}  teams {d.get('info', {}).get('TeamNames')}  rewards {d.get('rewards')}")
    tot = collections.defaultdict(lambda: collections.Counter())
    hours = collections.defaultdict(lambda: collections.Counter())
    for t, st in enumerate(steps):
        for p, a in enumerate(st):
            act = a.get("action") or {}
            m = act.get("market") if isinstance(act, dict) else None
            for slot, o in enumerate(m or []):
                if isinstance(o, list) and o and o[0] == "BUY_PRODUCT":
                    tot[p][o[1]] += int(o[2])
                    hours[p][(o[1], (t - 1) % 24)] += int(o[2])
    for p in (0, 1):
        print(f"  player {p} buys {dict(tot[p])}")
        print("    by hour", sorted(hours[p].items())[:30])
