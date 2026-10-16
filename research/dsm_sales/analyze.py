r"""DSM selling / harvest study: descriptive tables (markdown) from the replay cache.

.venv\Scripts\python.exe research\dsm_sales\replay_dsm.py          (once: builds the cache)
.venv\Scripts\python.exe research\dsm_sales\analyze.py [when|premium|slots|stock|harvest|buy|all] > tables.md

Every number is computed from exact local re-simulation of the 92 DSM games in data\games\dsm.jsonl.gz
(all 92 reproduce the server rewards exactly). "DSM side" = teams.index("DSM").
Conventions: step t = observation step; the actions DSM returned at t run in the interpreter call for t:
unit actions first (so a DROP/PLACE of step t can be sold by the market of step t), then the market,
then town consumption (shops if t % 4 == 0, town centre if t % 24 == 0), then the day end if t % 24 == 23.
"Stock S" = DSM shed right before the market of step t (after its own unit drops of that step).
"""
import collections
import sys

import numpy as np

from common import BASE, PI, PRODUCTS, SHED_ITEMS, load, per_step, town_demand

GAMES, ACTS = load()
N = len(GAMES)
PER = [per_step(g, ACTS[g["meta"]["id"]]) for g in GAMES]
LINEAGE = {"DECEM", "Vadim Vasilenko", "Unknown Mother-Goose"}
SHORT = {"WHEAT": "WHT", "CARROT": "CAR", "TOMATO": "TOM", "STRAWBERRY": "STR", "MELON": "MEL", "EGG": "EGG",
         "MILK": "MLK", "WOOL": "WOL", "FERTILIZER": "FRT"}
ANIMAL_PRODUCT = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}


def md(headers, rows):
    out = ["| " + " | ".join(str(h) for h in headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    print("\n".join(out))
    print()


def pct(a, b):
    return f"{100.0 * a / b:.0f}%" if b else "-"


def me_of(g):
    return g["meta"]["me"]


def opp_name(g):
    return g["meta"]["teams"][1 - g["meta"]["me"]]


def fresh_units(g, t, j):
    me = me_of(g)
    return max(0, int(g["shedpm"][me, t, j]) - int(g["shed"][me, t, j]))


# ----------------------------------------------------------------------------------------------
def sec_when():
    print("## 1. When DSM sells\n")
    rows = []
    hour_units = {x: np.zeros(24) for x in PRODUCTS}
    m4_units = {x: np.zeros(4) for x in PRODUCTS}
    m4_turns = {x: np.zeros(4) for x in PRODUCTS}
    for x in PRODUCTS:
        j = PI[x]
        lots, turns_per_day, h0u, fresh, tot = [], [], 0, 0, 0
        for g, r in zip(GAMES, PER):
            s = r["sold"][:, j]
            if s.sum() == 0:
                continue
            idx = np.nonzero(s)[0]
            for t in idx:
                q = int(s[t])
                lots.append(q)
                hour_units[x][t % 24] += q
                m4_units[x][t % 4] += q
                m4_turns[x][t % 4] += 1
                if t % 24 == 0:
                    h0u += q
                fresh += min(q, fresh_units(g, t, j))
                tot += q
            turns_per_day.extend(collections.Counter(int(t) // 24 for t in idx).values())
        L = np.array(lots)
        rows.append([x, f"{len(L) / N:.0f}", f"{L.sum() / N:.0f}", f"{np.median(L):.0f}", f"{L.mean():.1f}",
                     f"{np.percentile(L, 90):.0f}", int(L.max()), f"{np.mean(turns_per_day):.1f}", pct(h0u, tot),
                     pct(fresh, tot)])
    md(["product", "sale turns/game", "units/game", "lot median", "lot mean", "lot p90", "lot max",
        "sale turns per selling day", "units sold at hour 0", "units dropped by a unit in the same turn"], rows)
    exec_turns = [int(np.sum(r["sold"][:719].sum(axis=1) > 0)) for r in PER]
    print(f"Turns with at least one executed sale: {np.mean(exec_turns):.0f} per game (of 719 action steps).\n")

    print("Share of sold units by hour of day (hours with >=4% shown):\n")
    md(["product", "hour:share% of units"],
       [[x, " ".join(f"h{k}:{100 * v:.0f}" for k, v in enumerate(hour_units[x] / hour_units[x].sum()) if v >= 0.04)]
        for x in PRODUCTS])

    print("Share of sold units (and of sale turns) by step % 4. Town shops consume at the end of every step with "
          "step % 4 == 0 (after the market), so step % 4 == 1 is the first turn after a consumption tick:\n")
    rows = []
    for x in PRODUCTS:
        u = m4_units[x] / m4_units[x].sum()
        tt = m4_turns[x] / m4_turns[x].sum()
        rows.append([x] + [f"{100 * u[k]:.0f}% ({100 * tt[k]:.0f}%)" for k in range(4)])
    md(["product", "m4=0 (sells before the tick)", "m4=1 (first turn after tick)", "m4=2", "m4=3"], rows)

    print("P(DSM sells | stock S > 0) by hour of day:\n")
    rows = []
    for x in PRODUCTS:
        j = PI[x]
        num = np.zeros(24)
        den = np.zeros(24)
        for g, r in zip(GAMES, PER):
            av = g["shedpm"][me_of(g), :719, j] > 0
            sold = r["sold"][:719, j] > 0
            for h in range(24):
                num[h] += np.sum(sold[h::24] & av[h::24])
                den[h] += np.sum(av[h::24])
        rows.append([SHORT[x]] + [f"{num[h] / den[h]:.2f}" if den[h] else "-" for h in range(24)])
    md(["prod"] + [f"h{h}" for h in range(24)], rows)

    print("Sold units by sale component (a unit counts once, first matching column from the left):\n")
    rows = []
    for x in PRODUCTS:
        j = PI[x]
        c = collections.Counter()
        for g, r in zip(GAMES, PER):
            for t in np.nonzero(r["sold"][:, j])[0]:
                q = int(r["sold"][t, j])
                h = t % 24
                key = "h0" if h == 0 else "m1" if t % 4 == 1 else "fresh" if fresh_units(g, t, j) > 0 else \
                    "h22" if h in (22, 23) else "other"
                c[key] += q
        n = sum(c.values())
        rows.append([x] + [pct(c[k], n) for k in ("h0", "m1", "fresh", "h22", "other")])
    md(["product", "hour 0 (after day-end drop, before h0 tick)", "m4=1 (first turn after a tick)",
        "same-turn fresh drop, other hours", "hours 22-23", "other"], rows)

    print("Share of the stock present at hour 0 that is sold during that day (cumulative, days 8-28, "
          "days with >= 4 units at hour 0):\n")
    rows = []
    for x in PRODUCTS:
        j = PI[x]
        cum = np.zeros(24)
        n = 0
        for g, r in zip(GAMES, PER):
            me = me_of(g)
            for d in range(8, 29):
                s0 = g["shed"][me, d * 24, j]
                if s0 < 4:
                    continue
                cum += np.minimum(1.0, np.cumsum(r["sold"][d * 24:d * 24 + 24, j]) / s0)
                n += 1
        if n:
            c = cum / n
            rows.append([x, n] + [f"{c[h]:.2f}" for h in (1, 5, 9, 13, 17, 21, 23)])
    md(["product", "days", "by h1", "by h5", "by h9", "by h13", "by h17", "by h21", "by h23"], rows)

    print("Realised price: DSM vs the same-day mean quote (all units, 92 games):\n")
    rows = []
    for x in PRODUCTS:
        j = PI[x]
        a, b, o = [], [], []
        for g in GAMES:
            me = me_of(g)
            dm = [g["mpx"][d * 24:d * 24 + 24, j].mean() for d in range(30)]
            for (step, p, slot, op, it, px, _) in g["log"]:
                if op == "SELL" and it == x:
                    if p == me:
                        a.append(px / BASE[x])
                        b.append(px / max(1, dm[step // 24]))
                    else:
                        o.append(px / max(1, dm[step // 24]))
        rows.append([x, f"{np.mean(a):.2f}", f"{np.mean(b):.3f}", f"{np.mean(o):.3f}"])
    md(["product", "DSM price / base", "DSM price / same-day mean quote", "opponent price / same-day mean quote"], rows)

    print("Intraday quote profile, days 12-28 (quote at the start of the hour vs the day mean, %):\n")
    rows = []
    hs = (0, 1, 2, 5, 9, 13, 17, 20, 21, 22, 23)
    for x in PRODUCTS:
        j = PI[x]
        dev = np.zeros(24)
        n = 0
        for g in GAMES:
            for d in range(12, 29):
                p = g["mpx"][d * 24:d * 24 + 24, j].astype(float)
                if p.mean() >= 2:
                    dev += (p - p.mean()) / p.mean()
                    n += 1
        rows.append([x] + [f"{100 * dev[h] / n:+.1f}" for h in hs])
    md(["product"] + [f"h{h}" for h in hs], rows)


# ----------------------------------------------------------------------------------------------
def sec_premium():
    print("## 2. Premium goods: lot sizes and the hour-0 strawberry decision\n")
    for x, mode in (("STRAWBERRY", "m1"), ("STRAWBERRY", "h0"), ("MILK", "m1"), ("WOOL", "m1")):
        j = PI[x]
        tab = collections.Counter()
        for g, r in zip(GAMES, PER):
            me = me_of(g)
            for t in range(1, 719):
                if (mode == "m1" and (t % 4 != 1)) or (mode == "h0" and t % 24 != 0):
                    continue
                S = int(g["shedpm"][me, t, j])
                if S <= 0:
                    continue
                tab[(min(S, 16), min(int(r["sold"][t, j]), 13))] += 1
        qs = sorted({k[1] for k in tab})
        print(f"{x}, {'first turn after a tick (m4=1)' if mode == 'm1' else 'hour 0'}: rows = stock S (16 = 16+), "
              f"columns = units sold\n")
        md(["S \\ sold"] + qs, [[s] + [tab[(s, q)] for q in qs] for s in sorted({k[0] for k in tab})])

    print("Units sold at first-turn-after-tick steps (m4=1), by stock band (share of turns):\n")
    rows = []
    for x in ("STRAWBERRY", "MILK", "WOOL"):
        j = PI[x]
        for lo, hi in ((1, 3), (3, 8), (8, 999)):
            c = collections.Counter()
            for g, r in zip(GAMES, PER):
                me = me_of(g)
                for t in range(1, 719, 4):
                    if lo <= int(g["shedpm"][me, t, j]) < hi:
                        c[min(int(r["sold"][t, j]), 9)] += 1
            n = sum(c.values())
            rows.append([x, f"{lo}-{hi - 1}" if hi < 999 else f"{lo}+", n,
                         ", ".join(f"{k}:{v / n:.0%}" for k, v in sorted(c.items()) if v / n >= 0.02)])
    md(["product", "stock S", "turns", "units sold: share of turns (9 = 9+)"], rows)

    print("P(sell | S > 0) at first-turn-after-tick steps, by quote / base price:\n")
    rows = []
    bands = ("<0.2", "0.2-0.5", "0.5-1", "1-1.5", ">=1.5")
    for x in ("STRAWBERRY", "MILK", "WOOL"):
        j = PI[x]
        c = collections.Counter()
        for g, r in zip(GAMES, PER):
            me = me_of(g)
            for t in range(1, 719, 4):
                if g["shedpm"][me, t, j] <= 0:
                    continue
                pb = g["mpx"][t, j] / BASE[x]
                b = bands[0] if pb < 0.2 else bands[1] if pb < 0.5 else bands[2] if pb < 1 else bands[3] if pb < 1.5 else bands[4]
                c[(b, r["sold"][t, j] > 0)] += 1
        rows.append([x] + [f"{c[(b, True)] / (c[(b, True)] + c[(b, False)]):.2f} (n={c[(b, True)] + c[(b, False)]})"
                           if c[(b, True)] + c[(b, False)] else "-" for b in bands])
    md(["product"] + list(bands), rows)

    print("Turns where DSM's own units dropped fresh goods of the product into the shed in the same step:\n")
    rows = []
    for x in PRODUCTS:
        j = PI[x]
        c = collections.Counter()
        for g, r in zip(GAMES, PER):
            for t in range(719):
                fr = fresh_units(g, t, j)
                if fr <= 0:
                    continue
                key = "m4=1" if t % 4 == 1 else "other"
                q = int(r["sold"][t, j])
                c[(key, "n")] += 1
                if q > 0:
                    c[(key, "sold")] += 1
                    c[(key, "q==fresh")] += q == fr
        rows.append([x] + [f"{c[(k, 'n')]}: P(sell) {c[(k, 'sold')] / max(1, c[(k, 'n')]):.2f}, "
                           f"sold exactly the fresh amount {c[(k, 'q==fresh')]} of {c[(k, 'sold')]}" for k in ("m4=1", "other")])
    md(["product", "fresh-drop turns at m4=1", "fresh-drop turns at other steps"], rows)

    print("Premium sale turns by class (share of DSM's sale turns):\n")
    rows = []
    for x in ("STRAWBERRY", "MILK", "WOOL"):
        j = PI[x]
        c = collections.Counter()
        offh = collections.Counter()
        for g, r in zip(GAMES, PER):
            for t in np.nonzero(r["sold"][:719, j])[0]:
                if t % 24 == 0:
                    c["h0"] += 1
                elif t % 4 == 1:
                    c["m1"] += 1
                elif fresh_units(g, t, j) > 0:
                    c["fresh"] += 1
                else:
                    c["other"] += 1
                    offh[t % 24] += 1
        n = sum(c.values())
        rows.append([x, n, pct(c["h0"], n), pct(c["m1"], n), pct(c["fresh"], n), pct(c["other"], n),
                     ", ".join(f"h{h}" for h, _ in offh.most_common(4))])
    md(["product", "sale turns", "hour 0", "m4=1", "other step, fresh drop", "other step, no fresh drop",
        "main hours of the last class"], rows)

    print("Wool at m4=1 (S > 0): units sold vs wool consumed by the town at the tick just before "
          "(0 = no yarn store and not the h0 town-centre tick):\n")
    j = PI["WOOL"]
    c = collections.Counter()
    for g, r in zip(GAMES, PER):
        me = me_of(g)
        for t in range(1, 719, 4):
            if g["shedpm"][me, t, j] <= 0:
                continue
            cl = town_demand(g["shops_by_day"][(t - 1) // 24], t - 1)["WOOL"]
            c[(min(cl, 6), min(int(r["sold"][t, j]), 8))] += 1
    qs = sorted({k[1] for k in c})
    rows = []
    for cl in sorted({k[0] for k in c}):
        n = sum(c[(cl, q)] for q in qs)
        rows.append([cl, n, f"{1 - c[(cl, 0)] / n:.2f}"] + [f"{c[(cl, q)] / n:.0%}" for q in qs])
    md(["consumed at last tick", "turns", "P(sell)"] + [f"sold {q}" for q in qs], rows)

    print("P(DSM sells | S > 0) by hour, lineage opponents vs others (the within-day schedule is DSM's own):\n")
    rows = []
    hs = (0, 1, 5, 9, 13, 17, 21, 22)
    for x in ("STRAWBERRY", "MILK", "WOOL"):
        j = PI[x]
        for grp in ("lineage", "others"):
            num, den = np.zeros(24), np.zeros(24)
            for g, r in zip(GAMES, PER):
                if (opp_name(g) in LINEAGE) != (grp == "lineage"):
                    continue
                me = me_of(g)
                for t in range(24, 719):
                    if g["shedpm"][me, t, j] > 0:
                        den[t % 24] += 1
                        num[t % 24] += r["sold"][t, j] > 0
            rows.append([x, grp] + [f"{num[h] / den[h]:.2f}" if den[h] else "-" for h in hs])
    md(["product", "opponents"] + [f"h{h}" for h in hs], rows)

    print("Strawberry hour-0 lot sizes (S >= 6): count and median quote/base\n")
    j = PI["STRAWBERRY"]
    lots = collections.defaultdict(list)
    for g, r in zip(GAMES, PER):
        me = me_of(g)
        for d in range(1, 30):
            t = d * 24
            if g["shedpm"][me, t, j] >= 6 and r["req"][t, j] > 0:
                lots[int(r["req"][t, j])].append(g["mpx"][t, j] / BASE["STRAWBERRY"])
    md(["requested lot", "orders", "median quote/base"],
       [[k, len(v), f"{np.median(v):.2f}"] for k, v in sorted(lots.items())])
    both11 = collections.Counter()
    for g, r in zip(GAMES, PER):
        grp = "lineage" if opp_name(g) in LINEAGE else "others"
        for d in range(1, 30):
            t = d * 24
            if r["req"][t, j] == 11:
                both11[(grp, "dsm11")] += 1
                both11[(grp, "opp11")] += r["oreq"][t, j] == 11
    md(["opponents", "DSM SELL STRAWBERRY 11 at h0", "opponent also SELL STRAWBERRY 11 that step"],
       [[k, both11[(k, "dsm11")], both11[(k, "opp11")]] for k in ("lineage", "others")])

    print("Strawberry hour-0 sale vs market trend (S >= 9): dinv24 = market inventory now minus 24 steps ago\n")
    j = PI["STRAWBERRY"]
    c = collections.Counter()
    for g, r in zip(GAMES, PER):
        me = me_of(g)
        for d in range(1, 30):
            t = d * 24
            S = int(g["shedpm"][me, t, j])
            if S < 9:
                continue
            up = int(g["minv"][t, j]) - int(g["minv"][t - 24, j]) >= 9
            hi = g["mpx"][t, j] >= 0.7 * BASE["STRAWBERRY"]
            c[(up, hi, r["sold"][t, j] > 0)] += 1
    rows = []
    for up in (True, False):
        for hi in (True, False):
            n = c[(up, hi, True)] + c[(up, hi, False)]
            rows.append([f"dinv24 {'>=' if up else '<'} 9", f"price {'>=' if hi else '<'} 0.7 base", n,
                         f"{c[(up, hi, True)] / max(1, n):.2f}"])
    md(["trend", "price", "days", "P(sell at h0)"], rows)

    print("Lineage check: sell decisions at m4=1 when both sides hold stock\n")
    rows = []
    for x in ("STRAWBERRY", "MILK", "WOOL"):
        j = PI[x]
        for grp in ("DECEM/Vadim", "other"):
            both = d_only = o_only = neither = 0
            for g, r in zip(GAMES, PER):
                me = me_of(g)
                on = opp_name(g)
                if (on in ("DECEM", "Vadim Vasilenko")) != (grp == "DECEM/Vadim"):
                    continue
                for t in range(1, 719, 4):
                    if g["shedpm"][me, t, j] <= 0 or g["shedpm"][1 - me, t, j] <= 0:
                        continue
                    d_ = r["sold"][t, j] > 0
                    o_ = r["osold"][t, j] > 0
                    both += d_ and o_
                    d_only += d_ and not o_
                    o_only += o_ and not d_
                    neither += (not d_) and (not o_)
            n = both + d_only + o_only + neither
            rows.append([x, grp, n, f"{(both + d_only) / n:.2f}", f"{both / max(1, both + d_only):.2f}",
                         f"{o_only / max(1, o_only + neither):.2f}"])
    md(["product", "opponent", "turns", "P(DSM sells)", "P(opp sells | DSM sells)", "P(opp sells | DSM holds)"], rows)


# ----------------------------------------------------------------------------------------------
def sec_slots():
    print("## 3. Order-slot layout and the opponent\n")
    first_sell_slot = collections.Counter()
    before = collections.Counter()
    nsell_turns = 0
    contiguous = 0
    sells_per_turn = collections.Counter()
    bp_pos = collections.Counter()
    by_value = collections.Counter()
    phantom = collections.Counter()
    for g in GAMES:
        me = me_of(g)
        a = ACTS[g["meta"]["id"]][me]
        for t in range(719):
            m = a[t + 1].get("market") if isinstance(a[t + 1], dict) else None
            if not m:
                continue
            ops = [o[0] if isinstance(o, list) and o else "EMPTY" for o in m]
            for o in m:
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and o[1] in PI and \
                        g["shedpm"][me, t, PI[o[1]]] == 0:
                    phantom[o[1]] += 1
            if "SELL" not in ops:
                continue
            nsell_turns += 1
            fs = ops.index("SELL")
            first_sell_slot[min(fs, 3)] += 1
            for o in ops[:fs]:
                before[o] += 1
            sells = [o for o in m if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL"]
            sells_per_turn[min(len(sells), 4)] += 1
            last_sell = max(i for i, o in enumerate(ops) if o == "SELL")
            contiguous += all(o == "SELL" for o in ops[fs:last_sell + 1])
            for i, o in enumerate(ops):
                if o == "BUY_PRODUCT":
                    bp_pos["after last SELL" if i > last_sell else "before first SELL" if i < fs else "between"] += 1
            if len(sells) >= 2:
                vals = [int(o[2]) * g["mpx"][t, PI[o[1]]] for o in sells if o[1] in PI]
                by_value["descending qty x price" if vals == sorted(vals, reverse=True) else "other"] += 1
    print(f"Turns with at least one SELL order: {nsell_turns} ({nsell_turns / N:.0f}/game).\n")
    md(["slot of first SELL", "turns", "share"],
       [[("3+" if k == 3 else k), v, pct(v, nsell_turns)] for k, v in sorted(first_sell_slot.items())])
    md(["order placed before the first SELL", "count (all games)"], [[k, v] for k, v in before.most_common()])
    md(["SELL orders in a turn", "turns"], [[("4+" if k == 4 else k), v] for k, v in sorted(sells_per_turn.items())])
    print(f"SELL block contiguous (no other order between SELLs): {pct(contiguous, nsell_turns)} of SELL turns.\n")
    md(["order of SELLs when >= 2", "turns"], [[k, v] for k, v in by_value.most_common()])
    md(["BUY_PRODUCT position in turns that also SELL", "count"], [[k, v] for k, v in bp_pos.most_common()])
    last_bp = tot_bp = 0
    hires = collections.defaultdict(list)
    for g in GAMES:
        a = ACTS[g["meta"]["id"]][me_of(g)]
        for t in range(719):
            m = a[t + 1].get("market") if isinstance(a[t + 1], dict) else None
            m = [o for o in (m or []) if isinstance(o, list) and o]
            if t >= 240:
                hires[t % 24].append(sum(1 for o in m if o[0] == "HIRE"))
            idx = [i for i, o in enumerate(m) if o[0] == "BUY_PRODUCT"]
            if idx:
                tot_bp += 1
                last_bp += idx[-1] == len(m) - 1
    print(f"Turns with a BUY_PRODUCT order: {tot_bp}; the BUY_PRODUCT is the last non-empty order in {pct(last_bp, tot_bp)}.\n")
    print("Mean HIRE orders per turn from day 10 on: " + ", ".join(f"h{h}: {np.mean(v):.1f}" for h, v in sorted(hires.items())
                                                                  if np.mean(v) >= 0.05) + ".\n")
    md(["SELL orders issued with zero stock (fail harmlessly), per game"],
       [[", ".join(f"{k} {v / N:.1f}" for k, v in phantom.most_common())]])

    print("Contested sales (opponent sells the same product in the same turn) and reaction:\n")
    rows = []
    for grp in ("lineage (DECEM, Vadim, UMG)", "others"):
        for x in PRODUCTS:
            j = PI[x]
            ct = ut = 0
            cpx, upx = [], []
            oslot0 = 0
            react = collections.Counter()
            for g, r in zip(GAMES, PER):
                me = me_of(g)
                if (opp_name(g) in LINEAGE) != grp.startswith("lineage"):
                    continue
                unit_px = collections.defaultdict(list)
                for (step, p, slot, op, it, px, _) in g["log"]:
                    if p == me and op == "SELL" and it == x:
                        unit_px[step].append(px)
                for t in np.nonzero(r["sold"][:, j])[0]:
                    if r["osold"][t, j] > 0:
                        ct += 1
                        cpx += unit_px[t]
                        oslot0 += r["oslot"][t, j] == 0
                    else:
                        ut += 1
                        upx += unit_px[t]
                for t in range(5, 719, 4):
                    if g["shedpm"][me, t, j] > 0:
                        react[(r["osold"][t - 4:t, j].sum() > 0, r["sold"][t, j] > 0)] += 1
            if ct + ut == 0:
                continue
            pr = lambda o: react[(o, True)] / max(1, react[(o, True)] + react[(o, False)])
            rows.append([grp, x, pct(ct, ct + ut), f"{np.mean(cpx) / BASE[x]:.2f}" if cpx else "-",
                         f"{np.mean(upx) / BASE[x]:.2f}" if upx else "-", pct(oslot0, ct),
                         f"{pr(True):.2f} / {pr(False):.2f}"])
    md(["opponents", "product", "DSM sale turns contested", "DSM price/base contested", "alone",
        "opp SELL also in slot 0", "P(DSM sells at m4=1 | opp sold in previous 3 steps) yes / no"], rows)

    print("After DSM sold at a tick turn (m4=1): does it sell again at the next tick, contested vs alone?\n")
    rows = []
    for x in ("STRAWBERRY", "MILK", "WOOL"):
        j = PI[x]
        for grp in ("lineage", "others"):
            c = collections.Counter()
            for g, r in zip(GAMES, PER):
                me = me_of(g)
                if (opp_name(g) in LINEAGE) != (grp == "lineage"):
                    continue
                for t in range(1, 715, 4):
                    if r["sold"][t, j] > 0 and g["shedpm"][me, t + 4, j] > 0:
                        c[(r["osold"][t, j] > 0, r["sold"][t + 4, j] > 0)] += 1
            f = lambda k: c[(k, True)] / max(1, c[(k, True)] + c[(k, False)])
            rows.append([x, grp, f"{f(True):.2f} (n={c[(True, True)] + c[(True, False)]})",
                         f"{f(False):.2f} (n={c[(False, True)] + c[(False, False)]})"])
    md(["product", "opponents", "P(sell next tick) after contested sale", "after uncontested sale"], rows)


# ----------------------------------------------------------------------------------------------
def sec_stock():
    print("## 4. Stock levels, shed cap, endgame\n")
    S0 = np.zeros((30, 9))
    S23 = np.zeros((30, 9))
    maxfill, hit100, cap95 = [], 0, []
    lost = collections.Counter()
    for g in GAMES:
        me = me_of(g)
        sh = g["shed"][me]
        for d in range(30):
            S0[d] += sh[d * 24, :9]
            S23[d] += sh[min(719, d * 24 + 23), :9]
        tot = sh.sum(axis=1)
        maxfill.append(int(tot.max()))
        hit100 += tot.max() >= 100
        cap95.append(int((tot >= 95).sum()))
        for (step, p, carried, sb, sa) in g["eod"]:
            if p == me:
                for k, v in carried.items():
                    lost[k] += v - (sa.get(k, 0) - sb.get(k, 0))
    S0 /= N
    S23 /= N
    print(f"Max shed fill per game: median {np.median(maxfill):.0f}; {hit100} of {N} games reach 100 at some step; "
          f"steps with shed >= 95: {np.mean(cap95):.1f} per game.\n")
    md(["units lost at the day-end drop (shed full), per game"],
       [[", ".join(f"{k} {v / N:.1f}" for k, v in lost.most_common() if v)]])
    lost_mid = 0
    for g in GAMES:
        for (step, idx, action, pos, tile, inv_b, inv_a, sb, sa) in g["units"]:
            if action[0] == "DROP" and not inv_a and inv_b:
                lost_mid += sum(inv_b.values()) - (sa - sb)
    car = {h: np.mean([g["carried"][me_of(g), d * 24 + h].sum() for g in GAMES for d in range(12, 29)]) for h in (21, 22, 23)}
    shd = {h: np.mean([g["shed"][me_of(g), d * 24 + h].sum() for g in GAMES for d in range(12, 29)]) for h in (21, 22, 23)}
    print(f"Units lost by mid-day DROPs into a full shed: {lost_mid} in all {N} games. Days 12-28, mean shed / carried "
          f"items: h21 {shd[21]:.0f} / {car[21]:.0f}, h22 {shd[22]:.0f} / {car[22]:.0f}, h23 {shd[23]:.0f} / {car[23]:.0f}.\n")
    last = collections.defaultdict(list)
    for r in PER:
        for x in PRODUCTS:
            idx = np.nonzero(r["sold"][:, PI[x]])[0]
            if len(idx):
                last[x].append(int(idx[-1]))
    print("Last sale step per game (mean): " + ", ".join(f"{x} {np.mean(v):.0f}" for x, v in last.items()) + ".\n")
    rows = []
    for d in (5, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 28, 29):
        rows.append([d] + [f"{S0[d, k]:.1f}" for k in range(9)] + [f"{S0[d].sum():.0f}", f"{S23[d].sum():.0f}"])
    md(["day", *[SHORT[x] for x in PRODUCTS], "total at h0", "total at h23"], rows)

    print("Morning room-making: DSM units sold at hour 0 vs shed fill before the market (days 10-28):\n")
    rows = []
    for h in (0, 1, 2, 22):
        A = []
        for g, r in zip(GAMES, PER):
            me = me_of(g)
            for d in range(10, 29):
                t = d * 24 + h
                A.append((int(g["shedpm"][me, t].sum()), int(r["sold"][t].sum()), int(r["sold"][t, [0, 1, 2, 5]].sum())))
        A = np.array(A)
        for lo, hi in ((0, 60), (60, 80), (80, 90), (90, 95), (95, 101)):
            msk = (A[:, 0] >= lo) & (A[:, 0] < hi)
            if msk.sum() >= 20:
                rows.append([f"h{h}", f"{lo}-{hi - 1}", int(msk.sum()), f"{A[msk, 1].mean():.1f}", f"{A[msk, 2].mean():.1f}"])
    md(["hour", "shed fill", "days", "units sold (all)", "of which wheat/carrot/tomato/egg"], rows)

    print("Endgame: units sold per game by window (last market step is 718 = day 29 hour 22):\n")
    W = [("day 27", 648, 672), ("d28 h0-2", 672, 675), ("d28 h3-21", 675, 694), ("d28 h22-23", 694, 696),
         ("d29 h0-2", 696, 699), ("d29 h3-12", 699, 709), ("d29 h13-21", 709, 718), ("d29 h22 (step 718)", 718, 719)]
    rows = []
    for name, a, b in W:
        tot = sum(r["sold"][a:b].sum(axis=0) for r in PER) / N
        rows.append([name] + [f"{v:.1f}" for v in tot] + [f"{tot.sum():.0f}"])
    md(["window", *[SHORT[x] for x in PRODUCTS], "total"], rows)
    drops29 = np.zeros(24)
    for g in GAMES:
        for (step, idx, action, pos, tile, inv_b, inv_a, sb, sa) in g["units"]:
            if step >= 696 and action[0] in ("DROP", "PLACE") and sa > sb:
                drops29[step % 24] += sa - sb
    print("Day 29 mid-day drops into the shed (units/game by hour): "
          + " ".join(f"h{h}:{drops29[h] / N:.1f}" for h in range(23) if drops29[h] >= 0.5 * N / N) + "\n")
    val = []
    for g in GAMES:
        me = me_of(g)
        val.append(sum((g["shed"][me, 719, k] + g["carried"][me, 719, k]) * g["mpx"][719, k] for k in range(9)))
    print(f"Stranded at the end (shed + carried, valued at final quotes): mean ${np.mean(val):.0f}, "
          f"median ${np.median(val):.0f}, max ${max(val):.0f}.\n")


# ----------------------------------------------------------------------------------------------
def sec_harvest():
    print("## 5. Harvest timing and drops\n")
    rows = []
    for crop in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"):
        for lo, hi in ((0, 10), (10, 20), (20, 27), (27, 30)):
            c = collections.Counter()
            fert = 0
            for g in GAMES:
                for (step, idx, action, pos, tile, inv_b, inv_a, sb, sa) in g["units"]:
                    if action[0] != "HARVEST" or not isinstance(tile, dict) or tile.get("crop") != crop:
                        continue
                    y = tile.get("yield_units", 0)
                    d = step // 24
                    if y <= 0 or not lo <= d < hi:
                        continue
                    c[(d - tile["planted_day"], y)] += 1
                    fert += tile.get("fertilized_until_day", -1) >= 0
            n = sum(c.values())
            if n:
                rows.append([crop, f"d{lo}-{hi - 1}", f"{n / N:.1f}", pct(fert, n),
                             ", ".join(f"({a},{y}) {v / n:.0%}" for (a, y), v in c.most_common(4))])
    md(["crop", "days", "harvests/game", "fertilized", "top (age in days, yield) at harvest"], rows)

    rows = []
    for a, prod in ANIMAL_PRODUCT.items():
        gaps, ylds, hours = collections.Counter(), collections.Counter(), []
        for g in GAMES:
            last = {}
            for (step, idx, action, pos, tile, inv_b, inv_a, sb, sa) in g["units"]:
                if action[0] != "HARVEST" or not isinstance(tile, dict) or tile.get("animal") != a:
                    continue
                y = tile.get("yield_units", 0)
                if y <= 0:
                    continue
                key = (pos, tile["placed_day"])
                if key in last:
                    gaps[step // 24 - last[key]] += 1
                last[key] = step // 24
                ylds[y] += 1
                hours.append(step % 24)
        n = sum(ylds.values())
        ng = sum(gaps.values())
        rows.append([a, f"{n / N:.0f}", ", ".join(f"{k}:{v / n:.0%}" for k, v in sorted(ylds.items()) if v / n >= 0.02),
                     ", ".join(f"{k}d:{v / ng:.0%}" for k, v in sorted(gaps.items()) if v / ng >= 0.03),
                     f"{np.median(hours):.0f}"])
    md(["animal", "harvests/game", "yield at harvest", "days between harvests", "median hour"], rows)

    print("P(tile harvested that day | yield > 0 at hour 0), by the product's quote at hour 0 (days 10-28):\n")
    kinds = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL", "TOMATO": "TOMATO", "STRAWBERRY": "STRAWBERRY"}
    stat = collections.defaultdict(collections.Counter)
    for g in GAMES:
        harvested = collections.defaultdict(set)
        for (step, idx, action, pos, tile, inv_b, inv_a, sb, sa) in g["units"]:
            if action[0] == "HARVEST" and isinstance(tile, dict) and tile.get("yield_units", 0) > 0:
                harvested[step // 24].add(pos)
        for d in range(10, 29):
            for (x, y, tl) in g["tiles"][d]:
                k = tl.get("animal") or (tl.get("crop") if tl.get("kind") == "PLANT" else None)
                if k not in kinds or tl.get("yield_units", 0) <= 0:
                    continue
                pb = g["mpx"][d * 24, PI[kinds[k]]] / BASE[kinds[k]]
                b = "<0.3" if pb < 0.3 else "0.3-0.7" if pb < 0.7 else "0.7-1.1" if pb < 1.1 else ">=1.1"
                stat[k][(b, (x, y) in harvested[d])] += 1
    rows = []
    for k in kinds:
        cells = []
        for b in ("<0.3", "0.3-0.7", "0.7-1.1", ">=1.1"):
            n = stat[k][(b, True)] + stat[k][(b, False)]
            cells.append(f"{stat[k][(b, True)] / n:.2f} (n={n})" if n else "-")
        rows.append([k] + cells)
    md(["tile", "quote < 0.3 base", "0.3-0.7", "0.7-1.1", ">= 1.1"], rows)

    print("Same statistic split by game phase and by DSM's own shed stock of the product at hour 0 "
          "(checks that the price effect is not just a late-game effect):\n")
    rows = []
    for k in ("COW", "SHEEP", "STRAWBERRY"):
        for lo, hi in ((12, 20), (20, 29)):
            st = collections.Counter()
            for g in GAMES:
                me = me_of(g)
                harvested = collections.defaultdict(set)
                for (step, idx, action, pos, tile, inv_b, inv_a, sb, sa) in g["units"]:
                    if action[0] == "HARVEST" and isinstance(tile, dict) and tile.get("yield_units", 0) > 0:
                        harvested[step // 24].add(pos)
                for d in range(lo, hi):
                    for (x, y, tl) in g["tiles"][d]:
                        kk = tl.get("animal") or (tl.get("crop") if tl.get("kind") == "PLANT" else None)
                        if kk != k or tl.get("yield_units", 0) <= 0:
                            continue
                        prod = kinds[k]
                        pb = g["mpx"][d * 24, PI[prod]] / BASE[prod]
                        b = "<0.3" if pb < 0.3 else "0.3-0.7" if pb < 0.7 else ">=0.7"
                        s0 = g["shed"][me, d * 24, PI[prod]]
                        sb_ = "0" if s0 == 0 else "1-5" if s0 <= 5 else "6+"
                        st[(b, sb_, (x, y) in harvested[d])] += 1
            for b in ("<0.3", "0.3-0.7", ">=0.7"):
                cells = []
                for sb_ in ("0", "1-5", "6+"):
                    n = st[(b, sb_, True)] + st[(b, sb_, False)]
                    cells.append(f"{st[(b, sb_, True)] / n:.2f} (n={n})" if n >= 20 else "-")
                rows.append([k, f"d{lo}-{hi - 1}", b] + cells)
    md(["tile", "days", "quote/base", "own stock 0", "1-5", "6+"], rows)

    pl, hv, sold, tiles = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    for g, r in zip(GAMES, PER):
        n = 0
        for (step, idx, action, pos, tile, inv_b, inv_a, sb, sa) in g["units"]:
            if action[0] == "PLANT" and len(action) > 1 and action[1] == "MELON" and tile is None:
                pl[step // 24] += 1
                n += 1
            if action[0] == "HARVEST" and isinstance(tile, dict) and tile.get("crop") == "MELON":
                hv[step // 24] += 1
        tiles[n] += 1
        for t in np.nonzero(r["sold"][:, PI["MELON"]])[0]:
            sold[t // 24] += int(r["sold"][t, PI["MELON"]])
    print("Melon: tiles planted per game " + ", ".join(f"{k} tiles in {v} games" for k, v in sorted(tiles.items()))
          + "; planted on days " + ", ".join(f"d{k}:{v}" for k, v in sorted(pl.items()))
          + "; harvested on days " + ", ".join(f"d{k}:{v}" for k, v in sorted(hv.items()))
          + "; units sold on days " + ", ".join(f"d{k}:{v}" for k, v in sorted(sold.items())) + ".\n")

    harv, mid, eod, lostc =collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    hours = {x: collections.Counter() for x in PRODUCTS}
    ev = collections.Counter()
    for g in GAMES:
        me = me_of(g)
        for (step, idx, action, pos, tile, inv_b, inv_a, sb, sa) in g["units"]:
            if action[0] == "HARVEST" and isinstance(tile, dict) and tile.get("yield_units", 0) > 0:
                prod = tile.get("crop") if tile.get("kind") == "PLANT" else ANIMAL_PRODUCT.get(tile.get("animal"))
                harv[prod] += tile["yield_units"]
            elif action[0] in ("DROP", "PLACE") and sa > sb:
                ev[(action[0], step % 24)] += 1
                for k in inv_b:
                    v = inv_b.get(k, 0) - inv_a.get(k, 0)
                    if v > 0 and k in PI:
                        mid[k] += v
                        hours[k][step % 24] += v
        for (step, p, carried, sb, sa) in g["eod"]:
            if p == me:
                for k, v in carried.items():
                    got = sa.get(k, 0) - sb.get(k, 0)
                    eod[k] += got
                    lostc[k] += v - got
    rows = []
    for x in PRODUCTS:
        tot = mid[x] + eod[x]
        top = sorted(hours[x].items(), key=lambda kv: -kv[1])[:4]
        rows.append([x, f"{harv[x] / N:.0f}", f"{mid[x] / N:.0f}", f"{eod[x] / N:.0f}", pct(mid[x], tot),
                     " ".join(f"h{h}" for h, _ in sorted(top))])
    md(["product", "harvested/game", "dropped mid-day (DROP/PLACE)/game", "day-end drop/game", "mid-day share",
        "main mid-day drop hours"], rows)
    md(["mid-day shed deposits per game by hour", "DROP", "PLACE"],
       [[f"h{h}", f"{ev[('DROP', h)] / N:.1f}", f"{ev[('PLACE', h)] / N:.1f}"] for h in range(24)
        if ev[('DROP', h)] + ev[('PLACE', h)] >= 1 * N])

    pick = collections.defaultdict(collections.Counter)
    for g in GAMES:
        for (step, idx, action, pos, tile, inv_b, inv_a, sb, sa) in g["units"]:
            if action[0] == "PICKUP" and len(action) > 1:
                n = sum(inv_a.values()) - sum(inv_b.values())
                if n > 0:
                    pick[action[1]][step % 24] += n
    md(["item picked up from the shed", "units/game", "main hours (share)"],
       [[k, f"{sum(v.values()) / N:.1f}", ", ".join(f"h{h} {c / sum(v.values()):.0%}" for h, c in v.most_common(4))]
        for k, v in sorted(pick.items(), key=lambda kv: -sum(kv[1].values()))])
    cnt = collections.Counter()
    for g in GAMES:
        a = ACTS[g["meta"]["id"]][me_of(g)]
        for t in range(1, 720):
            act = a[t]
            if isinstance(act, dict):
                for u in [act.get("farmer")] + list(act.get("hands") or []):
                    if isinstance(u, list) and u:
                        cnt[u[0]] += 1
    print("DSM unit actions per game: " + ", ".join(f"{k} {v / N:.0f}" for k, v in cnt.most_common()) + ".\n")


# ----------------------------------------------------------------------------------------------
def sec_buy():
    print("## 6. BUY_PRODUCT\n")
    for x in ("WHEAT", "FERTILIZER"):
        j = PI[x]
        units, spend, prices = [], [], []
        byday = collections.Counter()
        byhour = collections.Counter()
        cell = collections.Counter()
        reqlots = collections.Counter()
        slotpos = collections.Counter()
        for g, r in zip(GAMES, PER):
            me = me_of(g)
            u = s = 0
            for (step, p, slot, op, it, px, _) in g["log"]:
                if p == me and op == "BUY_PRODUCT" and it == x:
                    u += 1
                    s += px
                    prices.append(px)
                    byday[step // 24] += 1
                    byhour[step % 24] += 1
                    cell[(step // 24, step % 24)] += 1
            units.append(u)
            spend.append(s)
            a = ACTS[g["meta"]["id"]][me]
            for t in range(719):
                if r["breq"][t, j] > 0:
                    reqlots[int(r["breq"][t, j])] += 1
                    for i, o in enumerate(a[t + 1]["market"]):
                        if isinstance(o, list) and o and o[0] == "BUY_PRODUCT" and o[1] == x:
                            slotpos[i] += 1
        U = np.array(units)
        print(f"**{x}**: bought in {int((U > 0).sum())}/{N} games; {U.mean():.1f} units/game (median "
              f"{np.median(U):.0f}, max {U.max()}); ${np.mean(spend):.0f}/game; mean unit price ${np.mean(prices):.1f} "
              f"(min {min(prices)}, max {max(prices)}).\n")
        md(["day", "units/game"], [[d, f"{v / N:.1f}"] for d, v in sorted(byday.items()) if v / N >= 0.5])
        md(["hour", "units/game"], [[h, f"{v / N:.1f}"] for h, v in sorted(byhour.items()) if v / N >= 0.5])
        md(["(day, hour)", "units/game"], [[k, f"{v / N:.1f}"] for k, v in cell.most_common(8)])
        md(["requested lot", "orders"], [[k, v] for k, v in sorted(reqlots.items()) if v >= 20])
        md(["slot of BUY_PRODUCT", "orders"], [[k, v] for k, v in sorted(slotpos.items())])
        rows = []
        for lo, hi in ((0, 3), (3, 10), (10, 13), (13, 29)):
            u, px, lots_, stock = 0, [], [], []
            for g, r in zip(GAMES, PER):
                me = me_of(g)
                for (step, p, slot, op, it, pr, _) in g["log"]:
                    if p == me and op == "BUY_PRODUCT" and it == x and lo <= step // 24 < hi:
                        u += 1
                        px.append(pr)
                for t in range(lo * 24, min(719, hi * 24)):
                    if r["breq"][t, j] > 0:
                        lots_.append(int(r["breq"][t, j]))
                        stock.append(int(g["shedpm"][me, t, j]))
            if lots_:
                rows.append([f"d{lo}-{hi - 1}", f"{u / N:.1f}", f"{np.mean(px):.1f}" if px else "-",
                             f"{np.median(lots_):.0f}", f"{np.median(stock):.0f}"])
        md(["days", "units/game", "mean price", "median requested lot", "median own stock before the buy"], rows)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in (("when", sec_when), ("premium", sec_premium), ("slots", sec_slots), ("stock", sec_stock),
                     ("harvest", sec_harvest), ("buy", sec_buy)):
        if which in (name, "all"):
            fn()
