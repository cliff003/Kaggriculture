r"""Production composition of both seats in harvested games: plantings by crop and day band, animals bought by type
and day band, land purchase days, hires per day, and final money. Aggregates over games where team 42 lost to a
non-mirror opponent (or any filter) to show what winners build that we do not.

    .venv\Scripts\python.exe gold\front\compo.py FILE.jsonl.gz [FILE ...] [--team 42] [--min-id 0] [--lost-only]
        [--mirror-max 0.5]
"""
import argparse
import collections
import gzip
import json
import statistics as st

BANDS = [(0, 5), (6, 9), (10, 14), (15, 19), (20, 24), (25, 29)]


def band(d):
    for i, (a, b) in enumerate(BANDS):
        if a <= d <= b:
            return i
    return len(BANDS) - 1


def mscore(r, me, steps=96):
    a, b = r["acts"][me], r["acts"][1 - me]
    same = tot = 0
    for t in range(1, steps + 1):
        x = (a[t] if t < len(a) else None) or {}
        y = (b[t] if t < len(b) else None) or {}
        ux = [x.get("farmer")] + list(x.get("hands") or [])
        uy = [y.get("farmer")] + list(y.get("hands") or [])
        for i in range(max(len(ux), len(uy))):
            tot += 1
            same += i < len(ux) and i < len(uy) and ux[i] == uy[i]
    return same / max(1, tot)


def profile(acts):
    p = collections.Counter()
    hires = collections.Counter()
    land = []
    for t in range(1, len(acts)):
        s = t - 1
        d = s // 24
        a = acts[t] or {}
        for u in [a.get("farmer")] + list(a.get("hands") or []):
            if isinstance(u, list) and len(u) >= 2 and u[0] == "PLANT":
                p[("PLANT", u[1], band(d))] += 1
            elif isinstance(u, list) and u and u[0] in ("BUILD_COOP", "BUILD_PASTURE"):
                p[(u[0], "", band(d))] += 1
        for o in a.get("market") or []:
            if not o:
                continue
            if o[0] == "BUY_ANIMAL" and len(o) >= 3:
                p[("ANIMAL", o[1], band(d))] += int(o[2])
            elif o[0] == "HIRE":
                hires[d] += 1
            elif o[0] == "BUY_LAND":
                land.append(d)
    return p, hires, land


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--team", default="42")
    ap.add_argument("--min-id", type=int, default=0)
    ap.add_argument("--lost-only", action="store_true")
    ap.add_argument("--mirror-max", type=float, default=0.5)
    a = ap.parse_args()
    recs = {}
    for f in a.files:
        for l in gzip.open(f, "rt", encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                if a.team in r["teams"] and r["id"] >= a.min_id:
                    recs[r["id"]] = r
    us = collections.Counter()
    them = collections.Counter()
    hu = collections.Counter()
    ht = collections.Counter()
    lu = []
    lt = []
    n = 0
    margins = []
    for gid, r in sorted(recs.items()):
        me = r["teams"].index(a.team)
        margin = r["rewards"][me] - r["rewards"][1 - me]
        if a.lost_only and margin > 0:
            continue
        if mscore(r, me) > a.mirror_max:
            continue
        n += 1
        margins.append(margin)
        p, h, land = profile(r["acts"][me])
        q, g, land2 = profile(r["acts"][1 - me])
        us.update(p)
        them.update(q)
        hu.update(h)
        ht.update(g)
        lu += land
        lt += land2
    print(f"games {n}  mean margin {st.mean(margins) if margins else 0:+.0f}")
    keys = sorted(set(us) | set(them), key=lambda k: (k[0], k[1], k[2]))
    print(f"{'what':28s} " + " ".join(f"{'d%d-%d' % b:>11s}" for b in BANDS) + "   (us / them, per game)")
    rows = collections.defaultdict(dict)
    for k in keys:
        rows[(k[0], k[1])][k[2]] = (us[k] / n, them[k] / n)
    for (kind, item), v in sorted(rows.items()):
        cells = []
        for i in range(len(BANDS)):
            u, t = v.get(i, (0, 0))
            cells.append(f"{u:5.1f}/{t:<5.1f}")
        print(f"{kind + ' ' + item:28s} " + " ".join(cells))
    print("hires per day (us/them):", " ".join(f"d{d}:{hu[d] / n:.1f}/{ht[d] / n:.1f}" for d in range(0, 30, 2)))
    print("land buys per game us", round(len(lu) / n, 2), "days", collections.Counter(lu).most_common(6))
    print("land buys per game them", round(len(lt) / n, 2), "days", collections.Counter(lt).most_common(6))


if __name__ == "__main__":
    main()
