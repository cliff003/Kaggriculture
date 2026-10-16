r"""Section 6: fertilizer - collection, use by crop and crop age, sales/purchases.
    .venv\Scripts\python.exe research\dsm_plan\fert.py      -> out\fert.md
"""
import collections
import os

import numpy as np

from common import HERE, load_games, median, table

OUT = os.path.join(HERE, "out")
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]


def main():
    G = load_games()
    N = len(G)
    lines = [f"# Fertilizer ({N} games)\n"]
    fz = collections.defaultdict(lambda: np.zeros((N, 30)))
    ages = collections.defaultdict(collections.Counter)
    ages_d = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    refert = collections.Counter()
    watered_before = collections.Counter()
    hours = collections.defaultdict(list)
    coll = np.zeros((N, 30))
    avail = np.zeros((N, 30))
    sold = np.zeros((N, 30))
    sold_rev = np.zeros((N, 30))
    bought = np.zeros((N, 30))
    for gi, g in enumerate(G):
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if not a:
                continue
            if a[0] == "FERTILIZE" and d.get("FERTILIZER", 0) < 0:
                crop, pday, fud, wat = tb[1], tb[2], tb[4], tb[5]
                day = t // 24
                age = day - pday
                fz[crop][gi, day] += 1
                ages[crop][age] += 1
                ages_d[crop][day // 5][age] += 1
                refert[(crop, fud >= day)] += 1
                watered_before[(crop, wat)] += 1
                hours[crop].append(t % 24)
            elif a[0] == "COLLECT_FERTILIZER" and d.get("FERTILIZER", 0) > 0:
                coll[gi, t // 24] += 1
        # animals alive at the start of each day (all have fertilizer_available after the refresh)
        for day in range(1, 30):
            grid = g["eod"][day - 1]["tiles"][0]
            avail[gi, day] = sum(1 for row in grid for x in row if x and x != "L" and x[0] == "A")
        for (t, p, op, it, pr) in g["mkt"]:
            if p == 0 and it == "FERTILIZER":
                if op == "SELL":
                    sold[gi, t // 24] += 1
                    sold_rev[gi, t // 24] += pr
                elif op == "BUY_PRODUCT":
                    bought[gi, t // 24] += 1
    rows = []
    for d in range(30):
        tot = sum(fz[c][:, d].mean() for c in CROPS)
        rows.append([d, f"{avail[:, d].mean():.1f}", f"{coll[:, d].mean():.1f}",
                     f"{100 * coll[:, d].sum() / max(1, avail[:, d].sum()):.0f}%" if d else "",
                     f"{tot:.1f}"] + [f"{fz[c][:, d].mean():.1f}" if fz[c][:, d].sum() else "" for c in CROPS[:4]]
                    + [f"{sold[:, d].mean():.1f}", f"{sold_rev[:, d].sum() / max(1, sold[:, d].sum()):.0f}" if sold[:, d].sum() else "",
                       f"{bought[:, d].mean():.1f}" if bought[:, d].sum() else ""])
    lines.append("## 6a. Per day (means per game): animals alive at day start, COLLECT_FERTILIZER, FERTILIZE by crop, fertilizer sold/bought\n")
    lines.append(table(["day", "animals", "collected", "collect rate", "FERTILIZE total", "on wheat", "on carrot", "on tomato", "on strawberry",
                        "sold", "avg sale price", "bought"], rows))
    tot_f = {c: fz[c].sum(1) for c in CROPS}
    alltot = sum(tot_f.values())
    lines.append(f"\nSeason per game: collected {coll.sum(1).mean():.0f}, FERTILIZE {alltot.mean():.0f} (" + ", ".join(
        f"{c.lower()} {tot_f[c].mean():.0f} = {100 * tot_f[c].sum() / alltot.sum():.0f}%" for c in CROPS if tot_f[c].sum()) +
                 f"), sold {sold.sum(1).mean():.0f} for ${sold_rev.sum(1).mean():.0f}, bought {bought.sum(1).mean():.1f}.")
    # shed stock check
    stock = [np.mean([g["steps"][t]["shed"].get("FERTILIZER", 0) for g in G]) for t in range(0, 719, 24)]
    lines.append("Fertilizer in the shed at hour 0 of each day (mean): " + " ".join(f"d{i}:{v:.0f}" for i, v in enumerate(stock)))

    lines.append("\n## 6b. Crop age (days since planting) when fertilized\n")
    rows = []
    for c in CROPS:
        tot = sum(ages[c].values())
        if not tot:
            continue
        rows.append([c, tot / N, ", ".join(f"age {a}: {100 * n / tot:.0f}%" for a, n in sorted(ages[c].items()) if n / tot >= 0.01),
                     f"{100 * refert[(c, True)] / tot:.0f}%", f"{100 * watered_before[(c, True)] / tot:.0f}%", f"{median(hours[c]):.0f}"])
    lines.append(table(["crop", "per game", "age distribution", "tile still fertilized (re-fertilize)", "already watered that day", "median hour"], rows))
    lines.append("\nAge distribution by 5-day block (share %):\n")
    rows = []
    for c in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"):
        for b in range(6):
            cnt = ages_d[c][b]
            tot = sum(cnt.values())
            if tot < 20:
                continue
            rows.append([c, f"{5 * b}-{5 * b + 4}", tot, ", ".join(f"{a}:{100 * n / tot:.0f}" for a, n in sorted(cnt.items()) if n / tot >= 0.03)])
    lines.append(table(["crop", "days", "events", "age:share%"], rows))

    # which plantings get fertilized at all
    lines.append("\n## 6c. Share of plantings that receive fertilizer, and how many times\n")
    per = collections.defaultdict(collections.Counter)
    for g in G:
        cur = {}
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if not a or tb == ta and not d:
                continue
            if a[0] == "PLANT" and ta and ta != "L" and ta[0] == "P":
                cur[pos] = [ta[1], t // 24, 0]
            elif a[0] == "FERTILIZE" and d.get("FERTILIZER", 0) < 0 and pos in cur:
                cur[pos][2] += 1
            elif ((a[0] == "HARVEST" and ta is None) or a[0] == "DIG") and pos in cur:
                c, pd, n = cur.pop(pos)
                per[(c, pd // 10)][n] += 1
    rows = []
    for (c, b), cnt in sorted(per.items()):
        tot = sum(cnt.values())
        if tot < 30:
            continue
        rows.append([c, f"planted days {10 * b}-{10 * b + 9}", tot, f"{100 * (tot - cnt[0]) / tot:.0f}%", ", ".join(f"{k}x:{100 * v / tot:.0f}%" for k, v in sorted(cnt.items()))])
    lines.append(table(["crop", "cohort", "finished plantings", "fertilized", "times fertilized"], rows))

    text = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, "fert.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
