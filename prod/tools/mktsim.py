r"""Market-only simulator.

Given a recorded game (acct.py with ACCT_RAW=1) take one side's per-step market flows as the fixed
"rival" schedule, the world's shop unlock sequence as town demand, and evaluate an arbitrary
schedule of our sales (item -> list of (step, units)). Units are interleaved per the engine lockstep
(our unit, rival unit, ... in the same step; slot order ignored: we assume we go first within a step
when ours_first=True).

Returns our revenue and the rival's revenue per item.
"""
import json
import sys
import os
import collections

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
import fastarena  # noqa: E402,F401  (quiet kaggle_environments import)
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa: E402

ITEMS = K.PRODUCTS
SHOPS = K.SHOPS


def town_schedule(shops):
    """step -> {item: units consumed after the market phase of that step}"""
    cons = collections.defaultdict(collections.Counter)
    for step in range(720):
        day = step // 24
        active = [s for k, s in enumerate(shops) if day >= 3 * (k + 1)]
        if step % 4 == 0:
            for s in active:
                prods = SHOPS[s]
                mult = 2 if len(prods) == 1 else 1
                for it in prods:
                    cons[step][it] += mult
        if step % 24 == 0:
            for it in ITEMS:
                if it != "FERTILIZER":
                    cons[step][it] += 1
    return cons


def rival_flows(rec, side):
    """step -> item -> list of +1 (sell) / -1 (buy) units in commit order"""
    fl = collections.defaultdict(lambda: collections.defaultdict(list))
    for step, p, op, item, price in rec["log"]:
        if p != side:
            continue
        if op == "SELL":
            fl[step][item].append(1)
        elif op == "BUY_PRODUCT":
            fl[step][item].append(-1)
    return fl


def simulate(shops, rival, ours, ours_first=True, items=ITEMS):
    """ours: step -> item -> units to sell (all SELL).  Returns (our_rev, rival_rev, price_path) per item."""
    cons = town_schedule(shops)
    inv = {it: 10000 for it in ITEMS}
    our_rev = collections.Counter()
    riv_rev = collections.Counter()
    riv_units = collections.Counter()
    our_units = collections.Counter()
    path = collections.defaultdict(list)
    for step in range(720):
        for it in items:
            r = list(rival.get(step, {}).get(it, []))
            o = int(ours.get(step, {}).get(it, 0))
            ri = 0
            while ri < len(r) or o > 0:
                seq = []
                if ours_first:
                    if o > 0:
                        seq.append("o")
                    if ri < len(r):
                        seq.append("r")
                else:
                    if ri < len(r):
                        seq.append("r")
                    if o > 0:
                        seq.append("o")
                # lockstep: both quoted on same inventory
                quotes = {}
                for who in seq:
                    if who == "o":
                        quotes[who] = ("S", K.market_price(it, inv[it]))
                    else:
                        u = r[ri]
                        if u > 0:
                            quotes[who] = ("S", K.market_price(it, inv[it]))
                        else:
                            quotes[who] = ("B", K.market_price(it, inv[it] - 1))
                for who in seq:
                    kind, pr = quotes[who]
                    if kind == "S":
                        if pr > 1:
                            inv[it] += 1
                        if who == "o":
                            our_rev[it] += pr
                            our_units[it] += 1
                            o -= 1
                        else:
                            riv_rev[it] += pr
                            riv_units[it] += 1
                            ri += 1
                    else:
                        inv[it] -= 1
                        riv_rev[it] -= pr
                        ri += 1
        for it, n in cons.get(step, {}).items():
            inv[it] -= n
        if step % 24 == 12:
            for it in items:
                path[it].append(K.market_price(it, inv[it]))
    return our_rev, riv_rev, our_units, riv_units, path


def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


if __name__ == "__main__":
    recs = load(sys.argv[1])
    side = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    tot = collections.Counter()
    for rec in recs:
        rival = rival_flows(rec, side)
        o, r, ou, ru, path = simulate(rec["shops"], rival, {})
        tot.update(r)
    n = len(recs)
    for it in ITEMS:
        print(it, round(tot[it] / n))
    print("sum", round(sum(tot.values()) / n))
