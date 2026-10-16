r"""Job-rule benchmark: our maintenance jobs (gold\newagent\jobs.py) vs DSM's actual tile ops, same start state.

    .venv\Scripts\python.exe gold\tools\jobbench.py [--games 10] [--days 10-28] [-v]

For every tile that holds a crop or an animal at the start of the day, compare the op kinds we would do today
with the ones DSM did (PLANT / BUILD / PLACE are policy and not counted; ops on tiles that were empty at the
start are ignored). Output per op kind: both, ours only, DSM only; plus examples of disagreements with -v.
"""
import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "gold", "newagent"))
import dsmday as D  # noqa: E402
import jobs as J  # noqa: E402

SKIP = {"PLANT", "BUILD_COOP", "BUILD_PASTURE", "PLACE"}


def compare_day(g, d, ctx_extra=None):
    st = D.day_state(g, d)
    tiles = st["tiles"]
    ctx = {"price": dict(st["prices"])}
    if ctx_extra:
        ctx.update(ctx_extra)
    ours = collections.defaultdict(collections.Counter)
    kind = {}
    for (xy, ops, prio, val) in J.day_jobs(tiles, d, ctx):
        for op, arg in ops:
            ours[xy][op] += 1
    acts = D.day_actions(g, d)
    dsm = collections.defaultdict(collections.Counter)
    for xy, lst in acts["tile_ops"].items():
        t = tiles[xy[1]][xy[0]]
        if not isinstance(t, dict) or t.get("kind") not in ("PLANT",) and "animal" not in t:
            continue
        seen_plant = False
        for (tt, op, arg) in lst:
            if op in SKIP:
                seen_plant = True
                continue
            if seen_plant:
                continue          # ops on the new crop planted today
            dsm[xy][op] += 1
    res = collections.defaultdict(collections.Counter)
    ex = collections.defaultdict(list)
    for xy in set(ours) | set(dsm):
        t = tiles[xy[1]][xy[0]]
        if isinstance(t, dict) and t.get("kind") == "PLANT":
            tk = t["crop"] + f"@{d - t['planted_day']}"
            cat = t["crop"]
        elif isinstance(t, dict) and "animal" in t:
            tk = t["animal"] + f"@{d - t['placed_day']}"
            cat = t["animal"]
        else:
            continue
        for op in set(ours[xy]) | set(dsm[xy]):
            a, b = min(1, ours[xy][op]), min(1, dsm[xy][op])
            key = f"{cat}:{op}"
            if a and b:
                res[key]["both"] += 1
            elif a:
                res[key]["ours"] += 1
                ex[key + " ours-only"].append((d, xy, tk, dict(t) if False else None))
            else:
                res[key]["dsm"] += 1
                ex[key + " dsm-only"].append((d, xy, tk))
    return res, ex


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=10)
    ap.add_argument("--days", default="10-28")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    paths = D.list_games()
    k = max(1, min(a.games, len(paths)))
    paths = [paths[i * (len(paths) - 1) // max(1, k - 1)] for i in range(k)]
    if "-" in a.days:
        lo, hi = a.days.split("-")
        days = list(range(int(lo), int(hi) + 1))
    else:
        days = [int(x) for x in a.days.split(",")]
    tot = collections.defaultdict(collections.Counter)
    exs = collections.defaultdict(list)
    for p in paths:
        g = D.load_game(p)
        for d in days:
            r, ex = compare_day(g, d)
            for key, c in r.items():
                tot[key].update(c)
            for key, v in ex.items():
                exs[key].extend(v)
    print(f"{'crop/animal:op':28s} {'both':>6s} {'ours':>6s} {'dsm':>6s}  recall  precision")
    for key in sorted(tot):
        c = tot[key]
        rec = c["both"] / max(1, c["both"] + c["dsm"])
        pre = c["both"] / max(1, c["both"] + c["ours"])
        print(f"{key:28s} {c['both']:6d} {c['ours']:6d} {c['dsm']:6d}  {rec:6.2f}  {pre:6.2f}")
    if a.v:
        for key in sorted(exs):
            ages = collections.Counter(x[2] for x in exs[key])
            print(key, len(exs[key]), ages.most_common(8))


if __name__ == "__main__":
    main()
