r"""Section 4: seed/animal buying and planting schedule, crop lifetimes, replant transitions.
    .venv\Scripts\python.exe research\dsm_plan\schedule.py      -> out\schedule.md
"""
import collections
import os

import numpy as np

from common import HERE, kind, load_games, median, quadrant, quantiles, table

OUT = os.path.join(HERE, "out")
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]


def lifecycles(g):
    """Per planting: dict(crop, pos, t_plant, harvests=[(t, units)], end=(t, how))."""
    cur = {}
    out = []
    for (t, idx, a, pos, tb, ta, d) in g["units"]:
        if not a or tb == ta:
            continue
        op = a[0]
        if op == "PLANT" and ta and ta != "L" and ta[0] == "P":
            if pos in cur:
                cur[pos]["end"] = (t, "overwritten?")
                out.append(cur.pop(pos))
            cur[pos] = {"crop": ta[1], "pos": pos, "t": t, "day": ta[2], "harv": [], "fert": [], "end": None}
        elif op == "HARVEST" and tb and tb != "L" and tb[0] == "P" and pos in cur:
            units = d.get(tb[1], 0)
            cur[pos]["harv"].append((t, units))
            if ta is None:  # one-time crop removed
                cur[pos]["end"] = (t, "harvest")
                out.append(cur.pop(pos))
        elif op == "FERTILIZE" and tb and tb != "L" and tb[0] == "P" and pos in cur:
            cur[pos]["fert"].append(t)
        elif op == "DIG" and pos in cur:
            cur[pos]["end"] = (t, "dig-weed" if tb and tb != "L" and tb[0] == "W" else "dig-plant")
            out.append(cur.pop(pos))
    for p in cur.values():
        p["end"] = (719, "alive at end")
        out.append(p)
    return out


def main():
    G = load_games()
    N = len(G)
    lines = [f"# Planting and buying schedule ({N} games)\n"]

    # ---- 4a. purchases per day ------------------------------------------------------------------------------------------
    keys = [("BUY_SEED", c) for c in CROPS] + [("BUY_ANIMAL", a) for a in ("COW", "SHEEP", "GOOSE")]
    per = collections.defaultdict(lambda: np.zeros((N, 30)))
    hrs = collections.defaultdict(list)
    for gi, g in enumerate(G):
        for (t, p, op, it, pr) in g["mkt"]:
            if p == 0 and (op, it) in keys:
                per[(op, it)][gi, t // 24] += 1
                hrs[(op, it, t // 24)].append(t % 24)
    rows = []
    for d in range(30):
        row = [d]
        for k in keys:
            v = per[k][:, d]
            if v.sum() == 0:
                row.append("")
                continue
            h = hrs[(k[0], k[1], d)]
            q = np.percentile(h, [25, 75])
            row.append(f"{v.mean():.1f} [{int((v > 0).sum())}] h{int(median(h))}")
        rows.append(row)
    lines.append("## 4a. Units bought per game per day: mean [games buying] h<median hour>\n")
    lines.append(table(["day"] + [f"{k[1].lower()} {'seed' if k[0] == 'BUY_SEED' else ''}" for k in keys], rows))

    # ---- 4b. effective plantings per day and where ------------------------------------------------------------------------
    pl = collections.defaultdict(lambda: np.zeros((N, 30)))
    plq = collections.defaultdict(collections.Counter)
    plh = collections.defaultdict(list)
    lcs = []
    for gi, g in enumerate(G):
        L = lifecycles(g)
        lcs.append(L)
        for p in L:
            d = p["t"] // 24
            pl[p["crop"]][gi, d] += 1
            plq[(p["crop"], d)][quadrant(*p["pos"])] += 1
            plh[(p["crop"], d)].append(p["t"] % 24)
    rows = []
    for d in range(30):
        row = [d]
        for c in CROPS:
            v = pl[c][:, d]
            if v.sum() == 0:
                row.append("")
                continue
            qc = plq[(c, d)]
            tot = sum(qc.values())
            qs = " ".join(f"{q}{round(100 * n / tot)}" for q, n in qc.most_common() if n / tot >= 0.1)
            row.append(f"{v.mean():.1f} h{int(median(plh[(c, d)]))} ({qs})")
        rows.append(row)
    lines.append("\n## 4b. Effective plantings per game per day: mean, h<median hour>, (quadrant shares %)\n")
    lines.append(table(["day"] + CROPS, rows))
    tot = {c: pl[c].sum(1) for c in CROPS}
    lines.append("\nPlantings per game over the season (p10 / median / p90): " + "; ".join(
        f"{c} {np.percentile(tot[c], 10):.0f}/{np.median(tot[c]):.0f}/{np.percentile(tot[c], 90):.0f}" for c in CROPS))
    last = {c: [max([p["t"] for p in L if p["crop"] == c], default=-1) for L in lcs] for c in CROPS}
    lines.append("\nLast planting (day:hour, p10 / median / p90 over games that plant the crop): " + "; ".join(
        f"{c} " + "/".join(f"{int(v) // 24}:{int(v) % 24:02d}" for v in np.percentile([x for x in last[c] if x >= 0], [10, 50, 90], method='nearest'))
        for c in CROPS if any(x >= 0 for x in last[c])))

    # ---- 4c. lifetimes / harvest age per crop ---------------------------------------------------------------------------
    lines.append("\n## 4c. Crop lifecycles (all plantings of all games)\n")
    rows = []
    for c in CROPS:
        ps = [p for L in lcs for p in L if p["crop"] == c]
        ends = collections.Counter(p["end"][1] for p in ps)
        if c in ("WHEAT", "CARROT", "MELON"):
            hv = [p for p in ps if p["end"][1] == "harvest"]
            ages = collections.Counter(p["end"][0] // 24 - p["day"] for p in hv)
            ys = collections.defaultdict(list)
            for p in hv:
                ys[p["end"][0] // 24 - p["day"]].append(p["harv"][-1][1])
            fert = collections.defaultdict(list)
            for p in hv:
                fert[p["end"][0] // 24 - p["day"]].append(1 if p["fert"] else 0)
            detail = "; ".join(f"age {a}: {n} ({100 * n / len(hv):.0f}%) yield {np.mean(ys[a]):.1f}, fert {100 * np.mean(fert[a]):.0f}%"
                               for a, n in sorted(ages.items()) if n / len(hv) >= 0.02)
        else:
            nh = collections.Counter(len(p["harv"]) for p in ps if p["end"][1] != "alive at end")
            endage = [p["end"][0] // 24 - p["day"] for p in ps if p["end"][1] != "alive at end"]
            units = [sum(u for (t, u) in p["harv"]) for p in ps if p["end"][1] != "alive at end"]
            hage = collections.Counter(t // 24 - p["day"] for p in ps for (t, u) in p["harv"])
            detail = (f"harvests per plant {dict(sorted(nh.items()))}; units per plant median {median(units):.0f} "
                      f"(mean {np.mean(units):.1f}); removed at age median {median(endage):.0f} (p10-p90 {np.percentile(endage, 10):.0f}-{np.percentile(endage, 90):.0f}); "
                      f"harvest ages {dict(sorted(hage.items()))}")
        rows.append([c, len(ps), ", ".join(f"{k} {v}" for k, v in ends.most_common()), detail])
    lines.append(table(["crop", "plantings", "how the tile was freed", "detail"], rows))

    # ---- 4d. what replaces what ----------------------------------------------------------------------------------------------
    lines.append("\n## 4d. Replanting: what goes on a tile after a crop leaves it, and how fast\n")
    trans = collections.defaultdict(collections.Counter)
    gaps = collections.defaultdict(list)
    for g in G:
        seq = collections.defaultdict(list)
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if not a or tb == ta:
                continue
            if a[0] == "PLANT":
                seq[pos].append((t, "plant", ta[1]))
            elif a[0] in ("BUILD_COOP", "BUILD_PASTURE"):
                seq[pos].append((t, "build", a[0][6:]))
            elif (a[0] == "HARVEST" and ta is None) or a[0] == "DIG":
                seq[pos].append((t, "free", kind(tb)))
        for pos, s in seq.items():
            for i, (t, ev, what) in enumerate(s):
                if ev != "free" or what in ("COOP", "PASTURE"):
                    continue
                nxt = next(((tt, e2, w2) for (tt, e2, w2) in s[i + 1:] if e2 in ("plant", "build")), None)
                key = (t // 24 // 3 * 3, what)
                if nxt is None:
                    trans[key]["(nothing)"] += 1
                else:
                    trans[key][nxt[2]] += 1
                    gaps[key].append(nxt[0] - t)
    rows = []
    for (d3, what), c in sorted(trans.items()):
        tot = sum(c.values())
        if tot < 10:
            continue
        rows.append([f"{d3}-{d3 + 2}", what, tot, ", ".join(f"{k} {100 * v / tot:.0f}%" for k, v in c.most_common(4)),
                     f"{median(gaps[(d3, what)]):.0f}" if gaps[(d3, what)] else ""])
    lines.append(table(["days freed", "crop that left (WEED = dug weed)", "events", "next use of the tile", "median hours until replant"], rows))

    # ---- 4e. strawberry cohorts ----------------------------------------------------------------------------------------------
    lines.append("\n## 4e. Strawberry and tomato cohorts: planting day -> tiles per game, and where\n")
    rows = []
    for c in ("STRAWBERRY", "TOMATO", "CARROT", "MELON"):
        cnt = collections.Counter()
        for L in lcs:
            for p in L:
                if p["crop"] == c:
                    cnt[p["day"]] += 1
        rows.append([c, " ".join(f"d{d}:{v / N:.1f}" for d, v in sorted(cnt.items()) if v / N >= 0.05)])
    lines.append(table(["crop", "plantings per game by planting day (>=0.05)"], rows))

    # ---- 4f. seed stock: bought just in time? ------------------------------------------------------------------------------
    lines.append("\n## 4f. Seed inventory at the start of each hour (mean over games and steps of the day) and buy->plant lag\n")
    rows = []
    for d in range(0, 30, 3):
        vals = {c: [] for c in CROPS}
        for g in G:
            for t in range(d * 24, min(719, (d + 3) * 24)):
                for c in CROPS:
                    vals[c].append(g["steps"][t]["seeds"].get(c, 0))
        rows.append([f"{d}-{d + 2}"] + [f"{np.mean(vals[c]):.2f} (max {max(vals[c])})" for c in CROPS])
    lines.append(table(["days"] + CROPS, rows))
    lag = collections.defaultdict(list)
    for g in G:
        buys = collections.defaultdict(list)
        for (t, p, op, it, pr) in g["mkt"]:
            if p == 0 and op == "BUY_SEED":
                buys[it].append(t)
        plants = collections.defaultdict(list)
        for (t, idx, a, pos, tb, ta, d) in g["units"]:
            if a and a[0] == "PLANT" and tb != ta:
                plants[a[1]].append(t)
        for c in CROPS:
            for tb_, tp in zip(sorted(buys[c]), sorted(plants[c])):
                lag[c].append(tp - tb_)
    lines.append("\nFIFO lag from seed purchase to planting (steps): " + "; ".join(
        f"{c} median {median(lag[c]):.0f}, p90 {np.percentile(lag[c], 90):.0f}" for c in CROPS if lag[c]))

    text = "\n".join(lines) + "\n"
    with open(os.path.join(OUT, "schedule.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    main()
