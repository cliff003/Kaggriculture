r"""Section 2: BUY_LAND timing, money before, what funds it.   .venv\Scripts\python.exe research\dsm_plan\land.py"""
import collections
import json
import os

from common import HERE, load_games, median, quantiles, table

OUT = os.path.join(HERE, "out")


def main():
    G = load_games()
    N = len(G)
    lines = [f"# Land purchases ({N} games)\n"]
    rows = []
    for q in ("NE", "SW", "SE"):
        ev = [(g, t, cost, mb) for g in G for (t, p, qq, cost, mb) in g["land"] if p == 0 and qq == q]
        dh = collections.Counter(f"{t // 24}:{t % 24:02d}" for (g, t, c, mb) in ev)
        mb = [x[3] for x in ev]
        q5 = quantiles(mb, (0, 0.1, 0.5, 0.9, 1))
        # money before the step's market (observation) and cash raised by sales executed earlier in the same step
        sold = collections.Counter()
        obs_m = []
        for (g, t, c, m) in ev:
            obs_m.append(g["steps"][t]["money"])
            for (tt, p, op, it, pr) in g["mkt"]:
                if tt == t and p == 0 and op == "SELL":
                    sold[it] += 1
        after = [x[3] - x[2] for x in ev]
        rows.append([q, f"{len(ev)}/{N}", ", ".join(f"{k} x{v}" for k, v in sorted(dh.items())),
                     f"{median(obs_m):.0f} ({min(obs_m):.0f}-{max(obs_m):.0f})",
                     "/".join(f"{x:.0f}" for x in q5),
                     f"{median(after):.0f}",
                     ", ".join(f"{k} {v / len(ev):.1f}" for k, v in sold.most_common())])
    lines.append(table(["quadrant", "games", "day:hour of BUY_LAND (games)", "money at start of step: median (min-max)",
                        "money right before BUY_LAND executes (min/p10/med/p90/max)", "median money right after",
                        "units sold earlier in the same step (per purchase)"], rows))

    # the order list that bought the land
    lines.append("\nOrder lists of the purchasing step (modal):\n")
    for q in ("NE", "SW", "SE"):
        c = collections.Counter()
        for g in G:
            for (t, p, qq, cost, mb) in g["land"]:
                if p == 0 and qq == q:
                    c[json.dumps(g["acts"][t + 1]["market"])] += 1
        lines.append(f"- {q}: " + " | ".join(f"`{k}` x{v}" for k, v in c.most_common(4)))

    # failed attempts
    fails = collections.Counter()
    for g in G:
        ok = {t for (t, p, q, c, m) in g["land"] if p == 0}
        for t in range(719):
            for o in (g["acts"][t + 1].get("market") or []):
                if o and o[0] == "BUY_LAND" and t not in ok:
                    fails[(t // 24, t % 24, json.dumps(g["acts"][t + 1]["market"]))] += 1
    lines.append("\nBUY_LAND orders that did not execute (day, hour, orders, games):\n")
    for (d, h, m), v in sorted(fails.items()):
        lines.append(f"- day {d} h{h}: `{m}` x{v}")

    # what was harvested just before: wool on day 6/9, melon on day 10
    lines.append("\nSales on the purchase day before the purchase step (units per game, median):\n")
    rows = []
    for q, d in (("NE", 6), ("SW", 9), ("SE", 10)):
        per = collections.defaultdict(list)
        for g in G:
            t0 = next(t for (t, p, qq, c, m) in g["land"] if p == 0 and qq == q)
            c = collections.Counter(it for (t, p, op, it, pr) in g["mkt"] if p == 0 and op == "SELL" and d * 24 <= t <= t0)
            for it in ("WOOL", "MELON", "MILK", "WHEAT", "FERTILIZER", "STRAWBERRY", "EGG"):
                per[it].append(c[it])
        rows.append([q] + [f"{median(per[it]):g}" for it in ("WOOL", "MELON", "MILK", "WHEAT", "FERTILIZER", "STRAWBERRY", "EGG")])
    lines.append(table(["quadrant", "WOOL", "MELON", "MILK", "WHEAT", "FERTILIZER", "STRAWBERRY", "EGG"], rows))
    text = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, "land.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
