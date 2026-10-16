r"""Does a route table win MORE GAMES against reactive cha22-family opponents? (The ranking counts wins only, and
against plain cha22 mirrors our market layers already win most games, so a higher mean margin is not enough.)

For every pair in the candidate's route table: fresh synthetic worlds (the pair + 6 uniform random shops, seeds not
used by routesearch.py), one game per world and opponent, seats alternating. BASE and CAND each play the same jobs.

.venv\Scripts\python.exe gold\arena\tablevs.py BASE.py CAND.py [--worlds 8] [--workers 8] [--out FILE.json]
"""
import argparse
import ast
import json
import multiprocessing as mp
import os
import random
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SHOPS = sorted(["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE", "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP",
                "FARMERS_MARKET"])
OPPS = {
    "cha22": os.path.join(ROOT, "research", "panel", "cha22", "main.py"),
    "emu_eager": os.path.join(ROOT, "research", "panel", "emu_eager", "main.py"),
    "emu_eager_m": os.path.join(ROOT, "research", "panel", "emu_eager_m", "main.py"),
    "v4": os.path.join(ROOT, "submissions", "v4_own_cha22_slot", "main.py"),
    "v6": os.path.join(ROOT, "submissions", "v6_own_cha22_eager_g90", "main.py"),
}


def route_table(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "_CFG":
            return ast.literal_eval(node.value).get("route_table") or {}
    return {}


def main():
    import gstat
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("cand")
    ap.add_argument("--worlds", type=int, default=8)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out")
    ap.add_argument("--pairs", help="comma-separated SHOP1|SHOP2 keys (default: every key of CAND's route table)")
    a = ap.parse_args()
    keys = a.pairs.split(",") if a.pairs else sorted(route_table(a.cand))
    jobs, meta = [], []
    for key in keys:
        p = key.split("|")
        rng = random.Random(90000 + SHOPS.index(p[0]) * 8 + SHOPS.index(p[1]))
        worlds = [p + [rng.choice(SHOPS) for _ in range(6)] for _ in range(a.worlds)]
        for wi, w in enumerate(worlds):
            seed = 900000 + 1000 * (SHOPS.index(p[0]) * 8 + SHOPS.index(p[1])) + wi
            for opp, op in OPPS.items():
                for tag, path in (("base", a.base), ("cand", a.cand)):
                    side = wi % 2
                    seats = (path, op) if side == 0 else (op, path)
                    jobs.append((seats[0], seats[1], seed, side, w))
                    meta.append((key, wi, opp, tag))
    print(f"{len(keys)} pairs, {len(jobs)} games", flush=True)
    with mp.get_context("spawn").Pool(max(1, min(a.workers, len(jobs))), maxtasksperchild=1) as pool:
        out = list(pool.imap(gstat.play_one, jobs))
    res = {}
    for (key, wi, opp, tag), g in zip(meta, out):
        c = g["cand_side"]
        ra, rb = g["rewards"][c], g["rewards"][1 - c]
        d = -99999.0 if (ra is None or rb is None or sum(g.get("errors") or [0])) else float(ra - rb)
        res.setdefault((key, opp), {}).setdefault(tag, []).append(d)
    rows = []
    tot = {"base": [0, 0], "cand": [0, 0]}
    print(f"{'pair':30} {'opp':12} {'base W':>7} {'cand W':>7} {'base mean':>10} {'cand mean':>10}")
    for (key, opp), v in sorted(res.items()):
        wb, wc = sum(x > 0 for x in v["base"]), sum(x > 0 for x in v["cand"])
        n = len(v["base"])
        tot["base"][0] += wb
        tot["cand"][0] += wc
        tot["base"][1] += n
        tot["cand"][1] += n
        mb, mc = sum(v["base"]) / n, sum(v["cand"]) / n
        rows.append({"pair": key, "opp": opp, "base": v["base"], "cand": v["cand"]})
        print(f"{key[:30]:30} {opp:12} {wb:>3}/{n:<3} {wc:>3}/{n:<3} {mb:+10.0f} {mc:+10.0f}")
    by_pair = {}
    for r in rows:
        bp = by_pair.setdefault(r["pair"], [0, 0, 0])
        bp[0] += sum(x > 0 for x in r["base"])
        bp[1] += sum(x > 0 for x in r["cand"])
        bp[2] += len(r["base"])
    print()
    for k, (wb, wc, n) in by_pair.items():
        print(f"{k:30} wins base {wb}/{n} cand {wc}/{n}  change {wc - wb:+d}")
    print(f"\nTOTAL wins base {tot['base'][0]}/{tot['base'][1]}  cand {tot['cand'][0]}/{tot['cand'][1]}")
    if a.out:
        json.dump(rows, open(a.out, "w"))


if __name__ == "__main__":
    main()
