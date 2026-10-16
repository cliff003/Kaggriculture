r"""Section 3: tile allocation vs town shops, fitted rules, layout pattern.
    .venv\Scripts\python.exe research\dsm_plan\alloc.py
Writes out\alloc.md and out\alloc_per_game.csv (one row per game x checkpoint day).
"""
import collections
import csv
import os

import numpy as np

from common import HERE, SHOP_AB, SHOPS, counts, eod_grid, kind, load_games, quadrant, table

OUT = os.path.join(HERE, "out")
DAYS = (6, 9, 12, 15, 18, 21, 24, 27)
TYPES = ["COW", "SHEEP", "GOOSE", "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
# product demand per shop instance (single-product shops count double), see README
DEM = {"COW": {"PIZZA_SHOP": 1, "ICE_CREAM_SHOP": 1, "SMOOTHIE_SHOP": 1},
       "SHEEP": {"YARN_STORE": 2},
       "GOOSE": {"BAKERY": 1, "BRUNCH_SPOT": 1},
       "WHEAT": {"BAKERY": 1, "PIZZA_SHOP": 1, "BRUNCH_SPOT": 1, "ICE_CREAM_SHOP": 1, "FARMERS_MARKET": 1},
       "CARROT": {"PET_CAFE": 2, "FARMERS_MARKET": 1},
       "TOMATO": {"PIZZA_SHOP": 1, "FARMERS_MARKET": 1},
       "STRAWBERRY": {"BRUNCH_SPOT": 1, "ICE_CREAM_SHOP": 1, "SMOOTHIE_SHOP": 1, "FARMERS_MARKET": 1},
       "MELON": {}}
DEM_NAME = {"COW": "dairy = #PIZZA+#ICE+#SMOOTHIE", "SHEEP": "wool = 2*#YARN", "GOOSE": "egg = #BAKERY+#BRUNCH",
            "WHEAT": "wheat = #BAK+#PIZ+#BRU+#ICE+#FM", "CARROT": "carrot = 2*#PET+#FM", "TOMATO": "tomato = #PIZZA+#FM",
            "STRAWBERRY": "straw = #BRU+#ICE+#SMO+#FM", "MELON": "-"}


def dem(shops, typ):
    return sum(DEM[typ].get(s, 0) for s in shops)


def fit(X, y):
    X = np.column_stack([np.ones(len(y))] + list(X))
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    pred = X @ b
    ss = ((y - y.mean()) ** 2).sum()
    r2 = 1 - ((y - pred) ** 2).sum() / ss if ss > 0 else float("nan")
    return b, r2, float(np.sqrt(((y - pred) ** 2).mean())), pred


def main():
    G = load_games()
    N = len(G)
    lines = [f"# Tile allocation vs town shops ({N} games)\n"]

    # ---- per-game CSV -------------------------------------------------------------------------------------------------
    with open(os.path.join(OUT, "alloc_per_game.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["episode", "opponent", "day", "shops_known"] + TYPES + ["EMPTY_COOP", "EMPTY_PASTURE", "WEED", "EMPTY", "quadrants", "money_eod"])
        for g in G:
            for D in DAYS:
                c = counts(eod_grid(g, D))
                w.writerow([g["id"], g["opp"], D, "|".join(SHOP_AB[s] for s in g["shops"][:D // 3])] + [c[t] for t in TYPES]
                           + [c["COOP"], c["PASTURE"], c["WEED"], c["EMPTY"], len(g["eod"][D]["quads"]), round(g["eod"][D]["money"][0])])

    # ---- means --------------------------------------------------------------------------------------------------------
    rows = []
    for D in range(29):
        cs = [counts(eod_grid(g, D)) for g in G]
        rows.append([D] + [f"{np.mean([c[t] for c in cs]):.1f}" for t in TYPES + ["COOP", "PASTURE", "WEED", "EMPTY"]]
                    + [f"{np.mean([c['COW'] + c['SHEEP'] + c['GOOSE'] for c in cs]):.1f}"])
    lines.append("## 3a. Mean tile counts at the end of each day (all games)\n")
    lines.append(table(["day"] + TYPES + ["empty coop", "empty pasture", "weed", "empty", "animals"], rows))

    # ---- simple one-variable fits -------------------------------------------------------------------------------------
    lines.append("\n## 3b. One-variable fits `count(end of day D) = a + b*x`, x = demand of the product from the shops "
                 "unlocked by then (first D//3 shops). Cell: `a + b*x (R2)`\n")
    rows = []
    for t in TYPES[:-1]:
        row = [t, DEM_NAME[t]]
        for D in DAYS:
            y = np.array([counts(eod_grid(g, D))[t] for g in G], float)
            x = np.array([dem(g["shops"][:D // 3], t) for g in G], float)
            if x.std() == 0 or y.std() == 0:
                row.append(f"{y.mean():.1f}")
                continue
            b, r2, rmse, _ = fit([x], y)
            row.append(f"{b[0]:.1f}{b[1]:+.1f}x ({r2:.2f})")
        rows.append(row)
    lines.append(table(["type", "x"] + [f"day {D}" for D in DAYS], rows))

    # ---- animals: unlock-slot model ------------------------------------------------------------------------------------
    lines.append("\n## 3c. Animals: herd size vs WHEN the relevant shop unlocked\n")
    lines.append("Model: `max herd over days 6-15 = b0 + sum over relevant shops unlocked on day u (u=3,6,9,12,15) of inc(u)`. "
                 "Relevant: sheep YARN_STORE; cow PIZZA/ICE_CREAM/SMOOTHIE; goose BAKERY/BRUNCH.\n")
    REL = {"SHEEP": {"YARN_STORE"}, "COW": {"PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"}, "GOOSE": {"BAKERY", "BRUNCH_SPOT"}}
    herd = {}
    rows = []
    for t, rel in REL.items():
        y = np.array([max(counts(eod_grid(g, d))[t] for d in range(6, 16)) for g in G], float)
        herd[t] = y
        X = [np.array([1.0 if g["shops"][k] in rel else 0.0 for g in G]) for k in range(5)]
        b, r2, rmse, _ = fit(X, y)
        rows.append([t, f"{b[0]:.1f}"] + [f"{v:+.1f}" for v in b[1:]] + [f"{r2:.2f}", f"{rmse:.1f}"])
    lines.append(table(["animal", "b0 (no relevant shop)", "inc(u=3)", "inc(6)", "inc(9)", "inc(12)", "inc(15)", "R2", "RMSE"], rows))

    # sheep cross-tab by first yarn day
    lines.append("\nSheep peak (days 6-18) by the unlock day of the first and second YARN_STORE:\n")
    tab = collections.defaultdict(list)
    for g in G:
        ys = [3 * (i + 1) for i, s in enumerate(g["shops"]) if s == "YARN_STORE"]
        key = (ys[0] if ys else "-", ys[1] if len(ys) > 1 and ys[1] <= 18 else "-")
        tab[key].append(max(counts(eod_grid(g, d))["SHEEP"] for d in range(6, 19)))
    rows = [[k[0], k[1], len(v), f"{np.mean(v):.1f}", f"{min(v)}-{max(v)}"] for k, v in sorted(tab.items(), key=lambda kv: (str(kv[0][0]).zfill(3), str(kv[0][1]).zfill(3)))]
    lines.append(table(["1st yarn day", "2nd yarn day (<=18)", "games", "mean peak sheep", "range"], rows))

    # cows cross-tab by number of dairy shops known at day 6 and day 9
    lines.append("\nCow peak (days 6-15) by number of dairy shops (PIZZA/ICE/SMOOTHIE) among shops #1-#2 (known on day 6) and shop #3 (day 9):\n")
    tab = collections.defaultdict(list)
    for g in G:
        n6 = sum(1 for s in g["shops"][:2] if s in REL["COW"])
        n9 = 1 if g["shops"][2] in REL["COW"] else 0
        tab[(n6, n9)].append(herd["COW"][G.index(g)])
    rows = [[k[0], k[1], len(v), f"{np.mean(v):.1f}", f"{min(v):.0f}-{max(v):.0f}"] for k, v in sorted(tab.items())]
    lines.append(table(["dairy in shops 1-2", "dairy = shop 3", "games", "mean peak cows", "range"], rows))

    # total animals and geese as remainder
    lines.append("\nTotal animals (cow+sheep+goose) at the end of day D, and geese as the remainder:\n")
    rows = []
    for D in (9, 12, 15, 18, 21, 24, 27):
        tot = np.array([sum(counts(eod_grid(g, D))[t] for t in ("COW", "SHEEP", "GOOSE")) for g in G], float)
        q = np.percentile(tot, [10, 25, 50, 75, 90])
        rows.append([D, f"{tot.mean():.1f}", f"{tot.std():.1f}", "/".join(f"{v:.0f}" for v in q)])
    lines.append(table(["day", "mean", "sd", "p10/p25/p50/p75/p90"], rows))
    D = 12
    c12 = [counts(eod_grid(g, D)) for g in G]
    geese = np.array([c["GOOSE"] for c in c12], float)
    cs = np.array([c["COW"] + c["SHEEP"] for c in c12], float)
    egg = np.array([dem(g["shops"][:4], "GOOSE") for g in G], float)
    b, r2, rmse, _ = fit([cs, egg], geese)
    b1, r21, rmse1, _ = fit([egg], geese)
    lines.append(f"\nGeese at day 12: `{b[0]:.1f} {b[1]:+.2f}*(cows+sheep) {b[2]:+.1f}*#egg_shops` (R2 {r2:.2f}, RMSE {rmse:.1f}); "
                 f"egg shops alone: `{b1[0]:.1f} {b1[1]:+.1f}*#egg_shops` (R2 {r21:.2f}).")
    rows = []
    for e in sorted(set(egg.tolist())):
        m = egg == e
        tot = geese[m] + cs[m]
        rows.append([int(e), int(m.sum()), f"{tot.mean():.1f}", f"{geese[m].mean():.1f}", f"{geese[m].sum() / tot.sum():.2f}"])
    lines.append(table(["egg shops among first 4", "games", "animals day 12", "geese day 12", "goose share"], rows))

    # ---- crops: peak size vs demand ------------------------------------------------------------------------------------
    lines.append("\n## 3d. Crops: peak tile count vs product demand of the first K shops\n")
    rows = []
    for t in ("STRAWBERRY", "TOMATO", "CARROT", "WHEAT"):
        series = np.array([[counts(eod_grid(g, d))[t] for d in range(29)] for g in G], float)
        peak = series.max(1)
        pday = series.argmax(1)
        best = None
        for K in range(2, 9):
            x = np.array([dem(g["shops"][:K], t) for g in G], float)
            b, r2, rmse, _ = fit([x], peak)
            if best is None or r2 > best[0] + 0.02:
                best = (r2, K, b, rmse)
        r2, K, b, rmse = best
        rows.append([t, f"{peak.mean():.1f}", int(np.median(pday)), f"shops 1-{K}", f"{b[0]:.1f} {b[1]:+.1f}*x", f"{r2:.2f}", f"{rmse:.1f}"])
    lines.append(table(["crop", "mean peak tiles", "median peak day", "best K", "fit (x = demand from first K shops)", "R2", "RMSE"], rows))

    # full 8-shop regression for each type at selected days
    lines.append("\n## 3e. Multi-shop regression: count = b0 + sum_shop b_shop * (#instances of that shop known by then)\n")
    for D in (9, 12, 18, 24):
        rows = []
        for t in TYPES[:-1]:
            y = np.array([counts(eod_grid(g, D))[t] for g in G], float)
            X = [np.array([sum(1 for s in g["shops"][:D // 3] if s == S) for g in G], float) for S in SHOPS]
            b, r2, rmse, _ = fit(X, y)
            rows.append([t, f"{b[0]:.1f}"] + [f"{v:+.1f}" for v in b[1:]] + [f"{r2:.2f}"])
        lines.append(f"End of day {D} (first {D // 3} shops):\n")
        lines.append(table(["type", "b0"] + [SHOP_AB[s] for s in SHOPS] + ["R2"], rows))
        lines.append("")

    # ---- layout ---------------------------------------------------------------------------------------------------------
    lines.append("\n## 3f. Layout: where animals and crops go\n")
    rows = []
    for D in (9, 12, 18, 24, 27):
        per = collections.defaultdict(lambda: collections.Counter())
        for g in G:
            grid = eod_grid(g, D)
            for y in range(10):
                for x in range(10):
                    k = kind(grid[y][x])
                    per[quadrant(x, y)][k] += 1
        for q in ("NW", "NE", "SW", "SE"):
            c = per[q]
            rows.append([D, q] + [f"{c[t] / N:.1f}" for t in TYPES + ["WEED", "EMPTY"]])
    lines.append(table(["day", "quadrant"] + TYPES + ["weed", "empty"], rows))

    def cat(t):
        k = kind(t)
        if k in ("COW", "SHEEP", "GOOSE", "COOP", "PASTURE"):
            return "A"
        if k in TYPES:
            return {"WHEAT": "w", "CARROT": "c", "TOMATO": "t", "STRAWBERRY": "s", "MELON": "m"}[k]
        return {"EMPTY": ".", "WEED": "x", "LOCKED": "#"}[k]
    lines.append("\nShare of games in which the tile holds an animal (any kind), end of day 12 / 18 / 24 (%). The shed is between (4,4) and (5,5).\n")
    for D in (12, 18, 24):
        lines.append(f"Day {D}:\n```")
        for y in range(10):
            lines.append(" ".join(f"{round(100 * sum(1 for g in G if cat(eod_grid(g, D)[y][x]) == 'A') / N):3d}" for x in range(10)))
        lines.append("```")
    lines.append("\nModal content per tile (crop letter or A = animal) with share %, end of day 12 and 21:\n")
    for D in (12, 21):
        lines.append(f"Day {D}:\n```")
        for y in range(10):
            cells = []
            for x in range(10):
                c = collections.Counter(cat(eod_grid(g, D)[y][x]) for g in G)
                k, v = c.most_common(1)[0]
                cells.append(f"{k}{round(100 * v / N):3d}")
            lines.append(" ".join(cells))
        lines.append("```")
    # animal type by tile at day 15
    lines.append("\nWhich animal sits where (end of day 15): per tile, % of games with C(ow) / S(heep) / G(oose):\n```")
    for y in range(10):
        cells = []
        for x in range(10):
            c = collections.Counter(kind(eod_grid(g, 15)[y][x]) for g in G)
            s = "".join(f"{a[0]}{round(100 * c[a] / N)}" for a in ("COW", "SHEEP", "GOOSE") if c[a] >= 0.1 * N)
            cells.append(f"{s:>10}" if s else f"{'-':>10}")
        lines.append(" ".join(cells))
    lines.append("```")
    # distance to shed
    lines.append("\nManhattan distance from the nearest shed-access tile, end of day 15 (mean tiles per game):\n")
    acc = [(4, 4), (5, 4), (4, 5), (5, 5)]
    rows = []
    dist = collections.defaultdict(collections.Counter)
    for g in G:
        grid = eod_grid(g, 15)
        for y in range(10):
            for x in range(10):
                dd = min(abs(x - a) + abs(y - b) for a, b in acc)
                k = kind(grid[y][x])
                grp = "animal" if k in ("COW", "SHEEP", "GOOSE") else ("crop" if k in TYPES else k.lower())
                dist[dd][grp] += 1
    for dd in sorted(dist):
        c = dist[dd]
        tot = sum(c.values())
        rows.append([dd, f"{tot / N:.0f}", f"{c['animal'] / N:.1f}", f"{c['crop'] / N:.1f}", f"{(c['empty'] + c['weed']) / N:.1f}"])
    lines.append(table(["distance", "tiles", "animals", "crops", "empty+weed"], rows))

    text = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, "alloc.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
