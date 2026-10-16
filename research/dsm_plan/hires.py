r"""Section 5: hires per day, at which hours, units acting, labour mix.
    .venv\Scripts\python.exe research\dsm_plan\hires.py      -> out\hires.md
"""
import collections
import os

import numpy as np

from common import HERE, load_games, median, table

OUT = os.path.join(HERE, "out")
MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}


def main():
    G = load_games()
    N = len(G)
    lines = [f"# Hires and labour ({N} games)\n"]
    hires = np.zeros((N, 30))
    cost = np.zeros((N, 30))
    hh = collections.defaultdict(collections.Counter)
    orders = np.zeros((N, 30))
    for gi, g in enumerate(G):
        for (t, p, c) in g["hire"]:
            if p == 0:
                hires[gi, t // 24] += 1
                cost[gi, t // 24] += c
                hh[t // 24][t % 24] += 1
        for t in range(719):
            orders[gi, t // 24] += sum(1 for o in (g["acts"][t + 1].get("market") or []) if o and o[0] == "HIRE")
    # units present per hour (after hires): steps[t]['nh']
    nh = np.zeros((N, 719))
    for gi, g in enumerate(G):
        nh[gi] = [s["nh"] for s in g["steps"]]
    rows = []
    for d in range(30):
        v = hires[:, d]
        hrs = hh[d]
        tot = sum(hrs.values())
        top = ", ".join(f"h{h}:{100 * n / tot:.0f}%" for h, n in sorted(hrs.items()) if n / tot >= 0.05)
        t0, t1 = d * 24, min(719, d * 24 + 24)
        hands_mid = nh[:, min(t0 + 12, 718)]
        rows.append([d, f"{v.mean():.1f}", f"{np.percentile(v, 10):.0f}-{np.percentile(v, 90):.0f}", f"{orders[:, d].mean():.1f}",
                     f"{cost[:, d].mean():.0f}", top, f"{hands_mid.mean():.1f}", f"{nh[:, t0 + 1:t1].max(1).mean():.1f}" if t1 > t0 + 1 else ""])
    lines.append("## 5a. Hires per day (executed), HIRE orders sent, cost, and hours\n")
    lines.append(table(["day", "hires mean", "p10-p90", "HIRE orders sent", "cost $", "hour of executed hires (share)",
                        "hands present at hour 12", "max hands that day"], rows))
    lines.append(f"\nSeason totals per game: hires {hires.sum(1).mean():.0f} (p10 {np.percentile(hires.sum(1), 10):.0f}, p90 {np.percentile(hires.sum(1), 90):.0f}), "
                 f"hire cost ${cost.sum(1).mean():.0f}.")
    # distribution of hires per day for days >= 10
    c = collections.Counter(int(x) for x in hires[:, 10:29].ravel())
    lines.append("Hires per day on days 10-28 (game-days): " + ", ".join(f"{k}: {v}" for k, v in sorted(c.items())))
    # relation to money at hour 0
    lines.append("\nHires executed at hour 0 vs money at the start of the day (days 1-9):\n")
    tab = collections.defaultdict(list)
    for gi, g in enumerate(G):
        for d in range(1, 10):
            m = g["steps"][d * 24]["money"]
            h0 = sum(1 for (t, p, cc) in g["hire"] if p == 0 and t == d * 24)
            tab[h0].append(m)
    rows = [[k, len(v), f"{median(v):.0f}", f"{min(v):.0f}-{max(v):.0f}"] for k, v in sorted(tab.items())]
    lines.append(table(["hires at hour 0", "game-days", "median money at hour 0", "range"], rows))

    # ---- labour mix ----------------------------------------------------------------------------------------------------------
    lines.append("\n## 5b. What the units do (all unit-turns of DSM, share %). `idle` = PASS or an action with no effect\n")
    mix = collections.defaultdict(collections.Counter)
    for g in G:
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            op = a[0] if a else "NONE"
            eff = tb != ta or bool(d)
            if op in MOVES:
                k = "move"
            elif op == "PASS":
                k = "pass"
            elif not eff and op not in ("DROP", "PICKUP", "PLACE"):
                k = "no-effect " + op
            else:
                k = op
            mix[t // 24 // 5][k] += 1
    keys = ["move", "pass", "WATER", "HARVEST", "PLANT", "FEED", "CARE", "COLLECT_FERTILIZER", "FERTILIZE", "PICKUP", "DROP", "PLACE", "DIG",
            "BUILD_PASTURE", "BUILD_COOP"]
    rows = []
    for b in range(6):
        c = mix[b]
        tot = sum(c.values())
        noeff = sum(v for k, v in c.items() if k.startswith("no-effect"))
        rows.append([f"{5 * b}-{5 * b + 4}", f"{tot / N / 5:.0f}"] + [f"{100 * c[k] / tot:.1f}" for k in keys] + [f"{100 * noeff / tot:.1f}"])
    lines.append(table(["days", "unit-turns/day"] + keys + ["no-effect"], rows))
    noe = collections.Counter()
    for b in range(6):
        for k, v in mix[b].items():
            if k.startswith("no-effect"):
                noe[k] += v
    lines.append("\nNo-effect actions by type (season total per game): " + ", ".join(f"{k[10:]} {v / N:.0f}" for k, v in noe.most_common(8)))

    # hour-of-day profile of the end of the day: moves at hours 22-23
    lines.append("\nShare of unit-turns that are moves, by hour of day (days 1-28):\n")
    byh = collections.defaultdict(collections.Counter)
    for g in G:
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if 24 <= t < 29 * 24:
                op = a[0] if a else "NONE"
                byh[t % 24]["move" if op in MOVES else "pass" if op == "PASS" else "work"] += 1
    rows = [[h] + [f"{100 * byh[h][k] / max(1, sum(byh[h].values())):.0f}" for k in ("move", "work", "pass")] + [f"{sum(byh[h].values()) / N / 28:.1f}"] for h in range(24)]
    lines.append(table(["hour", "move %", "work %", "pass %", "units acting"], rows))

    text = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, "hires.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
