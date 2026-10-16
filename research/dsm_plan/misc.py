r"""Section 8: other regularities - cash reserve, wheat balance, sales, order-slot padding, endgame.
    .venv\Scripts\python.exe research\dsm_plan\misc.py      -> out\misc.md
"""
import collections
import os

import numpy as np

from common import HERE, load_games, median, table

OUT = os.path.join(HERE, "out")
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
BASE = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250, "EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100}


def main():
    G = load_games()
    N = len(G)
    lines = [f"# Other regularities ({N} games)\n"]

    # ---- 8a. money ---------------------------------------------------------------------------------------------------------
    rows = []
    for d in range(30):
        mins, eods, low = [], [], []
        for g in G:
            ms = [g["steps"][t]["money"] for t in range(d * 24, min(719, d * 24 + 24))]
            mins.append(min(ms))
            low.append(np.mean([m < 100 for m in ms]))
            eods.append(g["eod"][d]["money"][0] if d < 29 else g["final"][0])
        omon = [g["eod"][d]["money"][1] if d < 29 else g["final"][1] for g in G]
        rows.append([d, f"{median(mins):.0f}", f"{np.percentile(mins, 90):.0f}", f"{100 * np.mean(low):.0f}%", f"{median(eods):.0f}", f"{median(omon):.0f}"])
    lines.append("## 8a. Cash: DSM spends down to ~$0 until day 10, then accumulates\n")
    lines.append(table(["day", "median of daily min money", "p90 of daily min", "share of steps with money < $100", "median money end of day", "opponent median end of day"], rows))

    # ---- 8b. wheat balance ---------------------------------------------------------------------------------------------------
    rows = []
    bal = collections.defaultdict(lambda: np.zeros((N, 30)))
    for gi, g in enumerate(G):
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if not a:
                continue
            if a[0] == "HARVEST" and d.get("WHEAT", 0) > 0:
                bal["harvested"][gi, t // 24] += d["WHEAT"]
            elif a[0] == "FEED" and d.get("WHEAT", 0) < 0:
                bal["fed"][gi, t // 24] += 1
        for (t, p, op, it, pr) in g["mkt"]:
            if p == 0 and it == "WHEAT":
                if op == "BUY_PRODUCT":
                    bal["bought"][gi, t // 24] += 1
                    bal["bought$"][gi, t // 24] += pr
                elif op == "SELL":
                    bal["sold"][gi, t // 24] += 1
                    bal["sold$"][gi, t // 24] += pr
                elif op == "BUY_SEED":
                    bal["seeds"][gi, t // 24] += 1
    for d in range(30):
        rows.append([d] + [f"{bal[k][:, d].mean():.1f}" for k in ("seeds", "harvested", "fed", "bought", "sold")]
                    + [f"{bal['bought$'][:, d].sum() / max(1, bal['bought'][:, d].sum()):.0f}" if bal["bought"][:, d].sum() else "",
                       f"{bal['sold$'][:, d].sum() / max(1, bal['sold'][:, d].sum()):.0f}" if bal["sold"][:, d].sum() else ""])
    lines.append("\n## 8b. Wheat balance per game per day (units)\n")
    lines.append(table(["day", "seeds bought", "harvested", "fed to animals", "bought (feed)", "sold", "avg buy price", "avg sell price"], rows))
    lines.append("\nSeason per game: " + ", ".join(f"{k} {bal[k].sum(1).mean():.0f}" for k in ("seeds", "harvested", "fed", "bought", "sold")))

    # ---- 8c. sales ------------------------------------------------------------------------------------------------------------
    rows = []
    sold = collections.defaultdict(lambda: np.zeros((N, 3)))
    rev = collections.defaultdict(lambda: np.zeros((N, 3)))
    lots = collections.defaultdict(list)
    turns = np.zeros(N)
    for gi, g in enumerate(G):
        per_turn = collections.defaultdict(collections.Counter)
        for (t, p, op, it, pr) in g["mkt"]:
            if p == 0 and op == "SELL":
                b = min(2, t // 240)
                sold[it][gi, b] += 1
                rev[it][gi, b] += pr
                per_turn[t][it] += 1
        turns[gi] = len(per_turn)
        for t, c in per_turn.items():
            for it, n in c.items():
                lots[it].append(n)
    for it in PRODUCTS:
        u = sold[it].sum(1)
        r = rev[it].sum(1)
        rows.append([it, f"{u.mean():.0f}", f"{r.mean():.0f}", f"{r.sum() / max(1, u.sum()) / BASE[it]:.2f}",
                     "/".join(f"{rev[it][:, b].mean():.0f}" for b in range(3)), f"{median(lots[it]):.0f}" if lots[it] else ""])
    tot = sum(rev[it].sum(1) for it in PRODUCTS)
    rows.append(["total", "", f"{tot.mean():.0f}", "", "", ""])
    lines.append("\n## 8c. Sales per game\n")
    lines.append(table(["product", "units", "revenue", "avg price / base", "revenue days 0-9 / 10-19 / 20-29", "median units per selling turn"], rows))
    lines.append(f"\nSelling turns per game: {turns.mean():.0f}. Final money: median {median([g['final'][0] for g in G]):.0f}, "
                 f"opponent median {median([g['final'][1] for g in G]):.0f}; DSM won {sum(g['final'][0] > g['final'][1] for g in G)}/{N}, "
                 f"median margin {median([g['final'][0] - g['final'][1] for g in G]):.0f}.")

    # ---- 8d. order-slot structure --------------------------------------------------------------------------------------------
    pad = collections.Counter()
    pos_buy = collections.Counter()
    sell_first = [0, 0]
    for g in G:
        for t in range(719):
            m = g["acts"][t + 1].get("market") or []
            if not m:
                continue
            npad = sum(1 for o in m if not o)
            pad[npad > 0] += 1
            for i, o in enumerate(m):
                if o and o[0] == "BUY_PRODUCT" and o[1] == "WHEAT":
                    pos_buy[(npad > 0, i)] += 1
            kinds = [o[0] for o in m if o]
            if "SELL" in kinds:
                sell_first[0] += 1
                if kinds[0] == "SELL":
                    sell_first[1] += 1
    lines.append("\n## 8d. Market list structure\n")
    lines.append(f"- Turns with a non-empty order list that contain empty placeholder orders `[]`: {pad[True]} of {pad[True] + pad[False]} "
                 f"({100 * pad[True] / (pad[True] + pad[False]):.0f}%).")
    tot_b = sum(pos_buy.values())
    lines.append(f"- Slot index of `BUY_PRODUCT WHEAT` (with padding / without): " + ", ".join(
        f"slot {i}{' (padded)' if p else ''}: {100 * v / tot_b:.0f}%" for (p, i), v in sorted(pos_buy.items(), key=lambda kv: -kv[1])[:8]))
    lines.append(f"- Turns with a SELL where the first non-empty order is a SELL: {100 * sell_first[1] / max(1, sell_first[0]):.1f}%.")
    lines.append(f"- Order counts: HIRE at most 8 at hour 0 (after up to 2 SELLs), the rest at hour 1-2.")

    # ---- 8e. endgame ------------------------------------------------------------------------------------------------------------
    lines.append("\n## 8e. Endgame\n")
    left = collections.Counter()
    for g in G:
        for k, v in g["final_stock"].items():
            if k in BASE:
                left[k] += v
    lines.append("Unsold stock (shed + unit inventories) after the last executed step (718), mean units per game: "
                 + ", ".join(f"{k} {v / N:.1f}" for k, v in left.most_common() if v)
                 + f" (value at base price ~${sum(v * BASE[k] for k, v in left.items()) / N:.0f}).")
    last_sell = collections.Counter()
    for g in G:
        ts = [t for (t, p, op, it, pr) in g["mkt"] if p == 0 and op == "SELL"]
        last_sell[max(ts)] += 1
    lines.append("Last SELL step: " + ", ".join(f"{k}: {v}" for k, v in sorted(last_sell.items())))
    last_buy = collections.defaultdict(list)
    for g in G:
        per = collections.defaultdict(int)
        for (t, p, op, it, pr) in g["mkt"]:
            if p == 0 and op.startswith("BUY"):
                per[op + " " + it] = max(per[op + " " + it], t)
        for k, v in per.items():
            last_buy[k].append(v)
    lines.append("Last purchase per game (median day:hour, games): " + "; ".join(
        f"{k} {int(median(v)) // 24}:{int(median(v)) % 24:02d} ({len(v)})" for k, v in sorted(last_buy.items())))
    # last day of each unit op type
    lastop = collections.defaultdict(list)
    for g in G:
        per = {}
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if a and (tb != ta or d) and a[0] in ("PLANT", "FEED", "CARE", "FERTILIZE", "WATER", "COLLECT_FERTILIZER"):
                per[a[0]] = t
        for k, v in per.items():
            lastop[k].append(v)
    lines.append("Last effective unit action per game (median day:hour): " + "; ".join(
        f"{k} {int(median(v)) // 24}:{int(median(v)) % 24:02d}" for k, v in sorted(lastop.items())))

    # ---- 8f. hour-of-day profile ----------------------------------------------------------------------------------------------
    from common import kind
    hrs = collections.defaultdict(list)
    for g in G:
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if not a or not (tb != ta or d) or t < 10 * 24 or t >= 28 * 24:
                continue
            op = a[0]
            if op in ("WATER", "HARVEST", "FERTILIZE", "PLANT", "FEED", "CARE", "COLLECT_FERTILIZER", "DIG", "PICKUP"):
                k = op + (" " + kind(tb) if op == "HARVEST" else " " + a[1] if op == "PICKUP" else "")
                hrs[k].append(t % 24)
    rows = []
    for k in sorted(hrs, key=lambda k: np.median(hrs[k])):
        v = hrs[k]
        if len(v) < 5 * N:
            continue
        q = np.percentile(v, [10, 50, 90])
        rows.append([k, f"{len(v) / N:.0f}", f"{q[0]:.0f}", f"{q[1]:.0f}", f"{q[2]:.0f}"])
    lines.append("\n## 8f. When in the day each effective unit action happens (days 10-27)\n")
    lines.append(table(["action", "per game", "hour p10", "median", "p90"], rows))

    text = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, "misc.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
