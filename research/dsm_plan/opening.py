r"""Section 1: DSM opening (days 0-6).   .venv\Scripts\python.exe research\dsm_plan\opening.py

Writes out\opening.md (summary tables) and out\opening_steps.md (per-step modal market list for steps 0-150).
"""
import collections
import json
import os

from common import HERE, kind, label, load_games, median, quantiles, table

OUT = os.path.join(HERE, "out")


def fmt_orders(m):
    if not m:
        return "(none)"
    parts = []
    for o in m:
        if not o:
            parts.append("null")
        elif o[0] in ("HIRE", "BUY_LAND"):
            parts.append(o[0])
        else:
            parts.append(f"{o[0].replace('BUY_PRODUCT', 'BUY_PROD')} {o[1]} {o[2]}")
    # compress runs of HIRE
    out, i = [], 0
    while i < len(parts):
        j = i
        while j < len(parts) and parts[j] == parts[i]:
            j += 1
        out.append(parts[i] + (f" x{j - i}" if j - i > 1 else ""))
        i = j
    return ", ".join(out)


def fmt_unit(a):
    if not a:
        return "-"
    return " ".join(str(x) for x in a[:2]) if a[0] in ("PLANT", "PICKUP", "PLACE") else a[0]


def main():
    G = load_games()
    N = len(G)
    lines = [f"# Opening (days 0-6), {N} DSM games (submission 56518845)\n"]

    # ---------- 1a. day-0 tape -----------------------------------------------------------------------------------
    ev = collections.defaultdict(collections.Counter)
    for g in G:
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if t > 150:
                break
            if a and a[0] in ("PLANT", "BUILD_PASTURE", "BUILD_COOP", "PLACE", "DIG") and tb != ta:
                what = a[1] if a[0] in ("PLANT", "PLACE") else a[0].replace("BUILD_", "")
                ev[t][(what, pos)] += 1
    rows = []
    for t in range(24):
        c = collections.Counter(json.dumps(g["acts"][t + 1], sort_keys=True) for g in G)
        top, n = c.most_common(1)[0]
        a = json.loads(top)
        units = [fmt_unit(a.get("farmer"))] + [fmt_unit(h) for h in a.get("hands", [])]
        tiles = "; ".join(f"{w}@{p[0]},{p[1]}" + ("" if k == N else f" ({k})") for (w, p), k in sorted(ev[t].items()))
        rows.append([t, n, fmt_orders(a.get("market")), " / ".join(units), tiles])
    lines.append("## 1a. Day 0 tape (steps 0-23). `n` = games whose full action (farmer+hands+market) equals the modal one\n")
    lines.append(table(["step", "n", "market orders", "farmer / hand1..4", "tile changes (x,y) (n if <92)"], rows))
    var = []
    for t in range(24):
        c = collections.Counter(json.dumps(g["acts"][t + 1]["market"]) for g in G)
        if len(c) > 1:
            var.append(f"step {t}: " + "; ".join(f"{k} x{v}" for k, v in c.most_common()))
    lines.append("\nMarket variants on day 0: " + (" | ".join(var) if var else "none"))

    # ---------- 1b. per-step modal market list 0..150 (separate file) ------------------------------------------------
    srows = []
    for t in range(151):
        c = collections.Counter(json.dumps(g["acts"][t + 1].get("market") or []) for g in G)
        top, n = c.most_common(1)[0]
        second = c.most_common(2)[1] if len(c) > 1 else None
        ex = collections.Counter()
        for g in G:
            for (tt, p, op, it, pr) in g["mkt"]:
                if tt == t and p == 0 and op != "SELL":
                    ex[f"{op} {it}"] += 1
            for (tt, p, cost) in g["hire"]:
                if tt == t and p == 0:
                    ex["HIRE"] += 1
            for (tt, p, q, cost, mb) in g["land"]:
                if tt == t and p == 0:
                    ex["LAND " + q] += 1
        exs = ", ".join(f"{k} {v / N:.1f}" for k, v in sorted(ex.items()))
        tiles = "; ".join(f"{w}@{p[0]},{p[1]} ({k})" for (w, p), k in sorted(ev[t].items(), key=lambda kv: -kv[1])[:6])
        srows.append([t, f"{t // 24}:{t % 24:02d}", f"{n}/{N}", fmt_orders(json.loads(top)),
                      (fmt_orders(json.loads(second[0])) + f" ({second[1]})") if second else "", exs, tiles])
    with open(os.path.join(OUT, "opening_steps.md"), "w", encoding="utf-8") as f:
        f.write("# Per-step modal DSM market list, steps 0-150\n\n`n` = games with exactly the modal list. "
                "`executed/game` = mean executed buy units per game at that step (all games). "
                "`tile changes` = PLANT/BUILD/PLACE/DIG with effect, (games).\n\n")
        f.write(table(["step", "day:hr", "n", "modal market list", "2nd list (games)", "executed/game", "tile changes"], srows))
        f.write("\n")

    # ---------- 1c. per-day purchases, days 0-6 ------------------------------------------------------------------------
    keys = ["SEED WHEAT", "SEED MELON", "SEED STRAWBERRY", "SEED CARROT", "SEED TOMATO", "ANIMAL COW", "ANIMAL SHEEP",
            "ANIMAL GOOSE", "PRODUCT WHEAT", "HIRE", "SELL WHEAT", "SELL FERTILIZER", "SELL WOOL"]
    per = {k: collections.defaultdict(list) for k in keys}
    hours = {k: collections.defaultdict(list) for k in keys}
    for g in G:
        cnt = collections.Counter()
        hr = collections.defaultdict(list)
        for (t, p, op, it, pr) in g["mkt"]:
            if p or t >= 7 * 24:
                continue
            k = (op.replace("BUY_", "") + " " + it) if op != "SELL" else "SELL " + it
            cnt[(t // 24, k)] += 1
            hr[(t // 24, k)].append(t % 24)
        for (t, p, cost) in g["hire"]:
            if p == 0 and t < 7 * 24:
                cnt[(t // 24, "HIRE")] += 1
                hr[(t // 24, "HIRE")].append(t % 24)
        for d in range(7):
            for k in keys:
                per[k][d].append(cnt[(d, k)])
                hours[k][d] += hr[(d, k)]
    rows = []
    for d in range(7):
        row = [d]
        for k in keys:
            v = per[k][d]
            q = quantiles(v, (0.1, 0.5, 0.9))
            h = hours[k][d]
            cell = f"{median(v):g}" if q[0] == q[2] else f"{q[1]:g} ({q[0]:g}-{q[2]:g})"
            if h and median(v) > 0:
                cell += f" @h{int(median(h))}"
            row.append(cell if max(v) > 0 else "")
        rows.append(row)
    lines.append("\n## 1b. Executed purchases/sales per day, days 0-6 (median units per game (p10-p90), @h = median hour of the executed units)\n")
    lines.append(table(["day"] + [k.replace("SEED ", "seed ").replace("ANIMAL ", "").replace("PRODUCT WHEAT", "wheat(feed)") for k in keys], rows))

    # ---------- 1d. placements per tile, days 0-6 ---------------------------------------------------------------------
    pl = collections.defaultdict(list)
    for g in G:
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if t >= 7 * 24:
                break
            if a and a[0] in ("PLANT", "BUILD_PASTURE", "BUILD_COOP", "PLACE", "HARVEST", "DIG") and tb != ta:
                if a[0] == "HARVEST" and ta is not None:
                    continue  # only harvests that clear the tile
                what = {"PLANT": lambda: a[1], "PLACE": lambda: a[1], "HARVEST": lambda: "harvest " + kind(tb),
                        "DIG": lambda: "dig " + kind(tb)}.get(a[0], lambda: a[0].replace("BUILD_", ""))()
                pl[(t // 24, pos, what)].append(t % 24)
    rows = []
    for (d, pos, what), hs in sorted(pl.items(), key=lambda kv: (kv[0][0], min(kv[1]), kv[0][1])):
        if len(hs) < 5:
            continue
        rows.append([d, f"({pos[0]},{pos[1]})", what, f"{len(hs)}/{N}", median(hs), f"{min(hs)}-{max(hs)}"])
    lines.append("\n## 1c. Tile events days 0-6 (events seen in >=5 games; harvest = one-time crop removed)\n")
    lines.append(table(["day", "tile", "event", "games", "median hour", "hour range"], rows))

    # ---------- 1e. layouts ------------------------------------------------------------------------------------------
    lines.append("\n## 1d. Modal layout at the end of days 0, 1, 2, 3, 5, 6 (after the end-of-day refresh)\n")
    lines.append("Legend: w wheat, m melon, s strawberry, c carrot, t tomato, C cow, S sheep, G goose, o/p empty coop/pasture, "
                 "x weed, . empty, # locked. Number = % of games with that modal content.\n")
    for d in (0, 1, 2, 3, 5, 6):
        lines.append(f"End of day {d}:\n```")
        rows_ = []
        rng = range(5) if d < 6 else range(10)
        for y in rng:
            cells = []
            for x in range(10):
                c = collections.Counter(label(g["eod"][d]["tiles"][0][y][x]) for g in G)
                k, v = c.most_common(1)[0]
                cells.append(f"{k}{round(100 * v / N):3d}")
            rows_.append(" ".join(cells))
        lines.append("\n".join(rows_) + "\n```")

    # ---------- 1f. divergence -----------------------------------------------------------------------------------------
    lines.append("\n## 1e. What drives the divergence\n")
    # step-24 money -> hires
    tab = collections.defaultdict(list)
    grp = collections.defaultdict(list)
    for g in G:
        m24 = g["steps"][24]["money"]
        h = sum(1 for (t, p, c) in g["hire"] if p == 0 and t == 24)
        tab[h].append(m24)
        grp[h].append(g)
    rows = []
    for h, ms in sorted(tab.items()):
        gs = grp[h]
        agree = []
        for t in range(24, 48):
            c = collections.Counter(json.dumps(g["acts"][t + 1], sort_keys=True) for g in gs)
            agree.append(c.most_common(1)[0][1] / len(gs))
        d1 = collections.Counter(sum(1 for (t, p, c) in g["hire"] if p == 0 and t // 24 == 1) for g in gs)
        rows.append([h, len(ms), f"{min(ms):.0f}-{max(ms):.0f}", f"{100 * sum(agree) / len(agree):.0f}%",
                     ", ".join(f"{k}:{v}" for k, v in sorted(d1.items()))])
    allagree = []
    for t in range(24, 48):
        c = collections.Counter(json.dumps(g["acts"][t + 1], sort_keys=True) for g in G)
        allagree.append(c.most_common(1)[0][1] / N)
    lines.append("Step 24 (day 1 hour 0) always sends 8 HIRE orders; the number that executes is set by the $0-9 left "
                 "after the day-0 wheat-seed loop (hire costs 1,1,2,3). Games with the same number of step-24 hires "
                 "keep much more similar day-1 plans:\n")
    lines.append(table(["hires executed at step 24", "games", "money at step 24", "day-1 full-action agreement within group (steps 24-47)", "total day-1 hires: games"], rows))
    lines.append(f"\nAgreement over all {N} games on steps 24-47: {100 * sum(allagree) / len(allagree):.0f}%.\n")

    # money path: step-0 wheat price paid vs opponent's same-step wheat buys
    rows = []
    tab = collections.defaultdict(list)
    for g in G:
        dsm_cost0 = sum(pr for (t, p, op, it, pr) in g["mkt"] if t == 0 and p == 0 and op == "BUY_PRODUCT")
        opp_w0 = sum(1 for (t, p, op, it, pr) in g["mkt"] if t == 0 and p == 1 and op == "BUY_PRODUCT" and it == "WHEAT")
        opp_w06 = sum(1 for (t, p, op, it, pr) in g["mkt"] if t <= 6 and p == 1 and op == "BUY_PRODUCT" and it == "WHEAT") - \
            sum(1 for (t, p, op, it, pr) in g["mkt"] if t <= 6 and p == 1 and op == "SELL" and it == "WHEAT")
        net = sum((-pr if op.startswith("BUY") else pr) for (t, p, op, it, pr) in g["mkt"] if t <= 6 and p == 0 and it == "WHEAT")
        b = "0" if opp_w0 == 0 else "1-5" if opp_w0 <= 5 else "6-10" if opp_w0 <= 10 else ">10"
        tab[b].append((dsm_cost0, net, g["steps"][24]["money"], opp_w06))
    for b in ("0", "1-5", "6-10", ">10"):
        v = tab.get(b)
        if not v:
            continue
        rows.append([b, len(v), f"{median([x[0] for x in v]):.0f}", f"{median([x[1] for x in v]):.0f}",
                     f"{median([x[2] for x in v]):.0f}", ", ".join(f"{k}:{c}" for k, c in sorted(collections.Counter(int(x[2]) for x in v).items()))])
    lines.append("Money differences on day 0 come only from the wheat round trips of steps 0-6, whose prices move with "
                 "the opponent's wheat orders in the same steps (shared market, lockstep):\n")
    lines.append(table(["opponent wheat units bought at step 0", "games", "DSM paid for its 5 wheat at step 0",
                        "DSM net wheat cash steps 0-6", "median money step 24", "money at step 24: games"], rows))

    # step-13 variant
    v2 = [g for g in G if g["acts"][14]["market"][1][2] == 2]
    v5 = [g for g in G if g["acts"][14]["market"][1][2] == 5]
    ws = lambda gs: collections.Counter(sum(1 for (t, p, op, it, pr) in g["mkt"] if p == 0 and op == "BUY_SEED" and it == "WHEAT" and t < 24) for g in gs)
    lines.append(f"\nStep 13 variant: `SELL WHEAT 1, BUY_SEED WHEAT 2` in {len(v2)} games, `... BUY_SEED WHEAT 5` in {len(v5)}. "
                 f"Money at step 13: {min(g['steps'][13]['money'] for g in v2):.0f}-{max(g['steps'][13]['money'] for g in v2):.0f} vs "
                 f"{min(g['steps'][13]['money'] for g in v5):.0f}-{max(g['steps'][13]['money'] for g in v5):.0f} (overlapping); "
                 f"wheat seeds executed on day 0: {dict(sorted(ws(v2).items()))} vs {dict(sorted(ws(v5).items()))}. "
                 "Only the batching differs; the day-0 wheat total is the same (9-10, as many as cash allows).")

    # weeds in the opening
    wd = collections.Counter()
    digs = collections.Counter()
    for g in G:
        for d in range(6):
            wd[d] += sum(1 for row in g["eod"][d]["tiles"][0] for t in row if kind(t) == "WEED")
        for (t, idx, a, pos, tb, ta, dd) in g["units"]:
            if t >= 6 * 24:
                break
            if a and a[0] == "DIG" and tb != ta:
                digs[t // 24] += 1
    lines.append(f"\nWeeds on DSM's farm at the end of days 0-5 (sum over games): {dict(wd)}; effective DIGs days 0-5: {dict(digs)}. "
                 "Weeds are too rare to explain the day-1 divergence.")

    text = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, "opening.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
