r"""Section 7: animal care - FEED/CARE/COLLECT/HARVEST coverage per day, endgame release, harvest cadence and yields.
    .venv\Scripts\python.exe research\dsm_plan\animals.py      -> out\animals.md
"""
import collections
import os

import numpy as np

from common import HERE, load_games, median, table

OUT = os.path.join(HERE, "out")
AN = ["COW", "SHEEP", "GOOSE"]


def main():
    G = load_games()
    N = len(G)
    lines = [f"# Animal care ({N} games)\n"]
    cov = collections.defaultdict(lambda: collections.Counter())  # (animal, day) -> counter of fed/cared/coll/harv/alive
    harv = collections.defaultdict(list)   # animal -> list of (gap_days, units, day, age)
    first = collections.defaultdict(list)
    lastfeed = collections.defaultdict(list)
    escapes = collections.defaultdict(lambda: np.zeros(30))
    feed_hours = collections.defaultdict(list)
    care_before_feed = collections.Counter()
    bank_at_harvest = collections.defaultdict(list)
    for gi, g in enumerate(G):
        # per-day action sets per animal key (pos, placed_day)
        acts = collections.defaultdict(set)
        hlog = collections.defaultdict(list)
        order = {}
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if not a or not tb or tb == "L" or tb[0] != "A":
                continue
            key = (pos, tb[3], tb[2])
            day = t // 24
            op = a[0]
            eff = tb != ta or bool(d)
            if not eff:
                continue
            acts[(key, day)].add(op)
            if op == "FEED":
                feed_hours[tb[2]].append(t % 24)
                order.setdefault((key, day, "FEED"), t)
            if op == "CARE":
                order.setdefault((key, day, "CARE"), t)
            if op == "HARVEST":
                units = d.get({"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}[tb[2]], 0)
                hlog[key].append((t, units))
        # alive animals per day (start of day from eod[d-1]; placed during the day from units log)
        placed = collections.defaultdict(set)
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if a and a[0] == "PLACE" and ta and ta != "L" and ta[0] == "A" and tb != ta:
                placed[t // 24].add((pos, ta[3], ta[2]))
        prev = set()
        for day in range(29):
            start = set()
            if day > 0:
                grid = g["eod"][day - 1]["tiles"][0]
                for y in range(10):
                    for x in range(10):
                        c = grid[y][x]
                        if c and c != "L" and c[0] == "A":
                            start.add(((x, y), c[3], c[2]))
            alive = start | placed[day]
            end = set()
            grid = g["eod"][day]["tiles"][0]
            for y in range(10):
                for x in range(10):
                    c = grid[y][x]
                    if c and c != "L" and c[0] == "A":
                        end.add(((x, y), c[3], c[2]))
            for k in alive - end:
                escapes[k[2]][day] += 1
            for k in alive:
                an = k[2]
                s = acts.get((k, day), set())
                c = cov[(an, day)]
                c["alive"] += 1
                c["fed"] += "FEED" in s
                c["cared"] += "CARE" in s
                c["coll"] += "COLLECT_FERTILIZER" in s
                c["harv"] += "HARVEST" in s
                c["new"] += k in placed[day]
                if "FEED" in s and "CARE" in s:
                    care_before_feed[order[(k, day, "CARE")] < order[(k, day, "FEED")]] += 1
            prev = end
        # harvest cadence
        for key, hs in hlog.items():
            an = key[2]
            pday = key[1]
            last = None
            for (t, u) in hs:
                day = t // 24
                if last is None:
                    first[an].append((day - pday, u))
                else:
                    harv[an].append((day - last, u, day, day - pday))
                last = day
        # last feed per animal
        feeds = collections.defaultdict(int)
        for (k, day), s in acts.items():
            if "FEED" in s:
                feeds[k] = max(feeds[k], day)
        for k, dmax in feeds.items():
            lastfeed[k[2]].append(dmax)

    rows = []
    for day in range(29):
        row = [day]
        for an in AN:
            c = cov[(an, day)]
            if not c["alive"]:
                row += ["", "", "", "", ""]
                continue
            row += [f"{c['alive'] / N:.1f}", f"{100 * c['fed'] / c['alive']:.0f}", f"{100 * c['cared'] / c['alive']:.0f}",
                    f"{100 * c['coll'] / c['alive']:.0f}", f"{100 * c['harv'] / c['alive']:.0f}"]
        rows.append(row)
    hdr = ["day"]
    for an in AN:
        hdr += [f"{an.lower()} n", "fed%", "cared%", "fert%", "harv%"]
    lines.append("## 7a. Daily coverage: animals alive during the day (mean per game) and % that got FEED / CARE / COLLECT_FERTILIZER / HARVEST that day\n")
    lines.append(table(hdr, rows))
    lines.append(f"\nWhen an animal gets both, CARE comes before FEED in {100 * care_before_feed[True] / max(1, sum(care_before_feed.values())):.0f}% of animal-days. "
                 f"Median FEED hour: " + ", ".join(f"{an.lower()} {median(feed_hours[an]):.0f}" for an in AN))

    lines.append("\n## 7b. Escapes (animal disappears at the end of the day because it was unfed 2 days), per game per day\n")
    rows = []
    for day in range(18, 29):
        rows.append([day] + [f"{escapes[an][day] / N:.2f}" for an in AN])
    lines.append(table(["day", "cow", "sheep", "goose"], rows))
    lines.append("Total escapes per game before day 18: " + ", ".join(f"{an.lower()} {escapes[an][:18].sum() / N:.2f}" for an in AN)
                 + "; days 18-28: " + ", ".join(f"{an.lower()} {escapes[an][18:].sum() / N:.2f}" for an in AN))
    lines.append("\nLast FEED day per animal (share of animals):\n")
    rows = []
    for an in AN:
        c = collections.Counter(lastfeed[an])
        tot = sum(c.values())
        rows.append([an, tot / N] + [f"{100 * c[d] / tot:.0f}" for d in range(18, 30)])
    lines.append(table(["animal", "animals per game"] + [f"d{d}" for d in range(18, 30)], rows))

    lines.append("\n## 7c. Harvest cadence and yield per harvest\n")
    rows = []
    for an in AN:
        f = first[an]
        fa = collections.Counter(a for a, u in f)
        fu = [u for a, u in f]
        g_ = harv[an]
        gaps = collections.Counter(x[0] for x in g_)
        tot = sum(gaps.values())
        ubygap = collections.defaultdict(list)
        for gap, u, day, age in g_:
            ubygap[gap].append(u)
        rows.append([an, ", ".join(f"{a}:{n}" for a, n in sorted(fa.items()) if n / len(f) >= 0.03), f"{np.mean(fu):.1f}",
                     ", ".join(f"{k}d:{100 * v / tot:.0f}%" for k, v in sorted(gaps.items()) if v / tot >= 0.02),
                     ", ".join(f"{k}d:{np.mean(ubygap[k]):.1f}" for k in sorted(ubygap) if len(ubygap[k]) / tot >= 0.02)])
    lines.append(table(["animal", "age at first harvest (days since placed): count", "units at first harvest",
                        "days between harvests", "mean units by gap"], rows))
    # yield by phase
    rows = []
    for an in AN:
        for lo, hi in ((6, 12), (12, 18), (18, 24), (24, 30)):
            us = [u for gap, u, day, age in harv[an] if lo <= day < hi]
            if us:
                rows.append([an, f"{lo}-{hi - 1}", len(us) / N, f"{np.mean(us):.2f}"])
    lines.append("\nUnits per harvest by day block (repeat harvests):\n")
    lines.append(table(["animal", "days", "harvests per game", "mean units"], rows))

    # ---- 7d. value-based feed skipping ------------------------------------------------------------------------------------
    FI = {"COW": (8, 2), "SHEEP": (6, 3), "GOOSE": (4, 1)}
    PROD = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}
    res = collections.defaultdict(collections.Counter)
    for g in G:
        fed = set()
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if a and a[0] == "FEED" and tb != ta and tb and tb != "L" and tb[0] == "A":
                fed.add((pos, tb[3], t // 24))
        for day in range(10, 28):
            grid = g["eod"][day - 1]["tiles"][0]
            pr = g["steps"][day * 24 + 6]["prices"]
            for y in range(10):
                for x in range(10):
                    c = grid[y][x]
                    if not (c and c != "L" and c[0] == "A"):
                        continue
                    an, pday = c[2], c[3]
                    fy, iv = FI[an]
                    dsf = (day + 1) - pday - fy
                    prod = dsf >= 0 and dsf % iv == 0
                    ratio = pr[PROD[an]] / pr["WHEAT"]
                    b = "<1" if ratio < 1 else "1-1.5" if ratio < 1.5 else "1.5-2" if ratio < 2 else "2-3" if ratio < 3 else "3-4" if ratio < 4 else ">=4"
                    k = (an, prod, b)
                    res[k]["n"] += 1
                    res[k]["fed"] += ((x, y), pday, day) in fed
    bins = ["<1", "1-1.5", "1.5-2", "2-3", "3-4", ">=4"]
    rows = []
    for an in AN:
        for prod in (True, False):
            if an == "GOOSE" and not prod:
                continue
            cells = []
            for b in bins:
                v = res[(an, prod, b)]
                cells.append(f"{100 * v['fed'] / v['n']:.0f}% ({v['n']})" if v["n"] >= 30 else "")
            rows.append([an, "production day" if prod else "non-production day"] + cells)
    lines.append("\n## 7d. Feed skipping: % of animals fed on a day, days 10-27, by (product price / wheat price) at hour 6\n")
    lines.append("A production day is a day whose end-of-day refresh adds yield (cow every 2nd day from age 7, sheep every 3rd day from age 5, goose daily from age 3). "
                 "Cell: % fed (animal-days).\n")
    lines.append(table(["animal", "day type"] + [f"ratio {b}" for b in bins], rows))

    text = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, "animals.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
