r"""Production profile of harvested games, by world type: what one team builds (land days, animals, crop tiles, hires)
and earns (net cash by item) when the town has many shops for a product.

.venv/bin/python research/carrera/prod_profile.py TAPES.jsonl.gz [TAPES ...] --team NAME [--workers 8] [--out OUT.json]

Each record is re-simulated exactly with tools/econ.py (both sides' recorded actions). World features count the shops
that buy each product among the shops open on day 18 and at the end (shops are drawn with replacement, at most 8).
Prints, per world bucket, the team's mean build and item cash next to its opponents', and the team's W/L there.
"""
import argparse
import collections
import gzip
import json
import multiprocessing as mp
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))

BUYERS = {"STRAWBERRY": ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET"),
          "TOMATO": ("PIZZA_SHOP", "FARMERS_MARKET"),
          "WOOL": ("YARN_STORE",),
          "CARROT": ("PET_CAFE", "FARMERS_MARKET"),
          "MILK": ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"),
          "EGG": ("BAKERY", "BRUNCH_SPOT")}
TILE_KEYS = ("COW", "SHEEP", "GOOSE", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT", "MELON")


def features(shops):
    return {p: sum(s in b for s in shops) for p, b in BUYERS.items()}


def job(rec):
    import econ
    shops18 = []
    inner = econ.K.interpreter

    def spy(state, env):
        out = inner(state, env)
        if int(state[0].observation.step) == 18 * 24 and not shops18:
            shops18.extend(state[0].observation.town["unlocked_shops"])
        return out
    econ.K.interpreter = spy
    try:
        r = econ.resim(rec)
    finally:
        econ.K.interpreter = inner
    sides = []
    for s in r:
        peak = {k: max(d["tiles"].get(k, 0) for d in s["days"]) for k in TILE_KEYS}
        net = collections.Counter()
        for item, (u, rev, _) in s["sales"].items():
            net[item] += rev
        for k, v in s["spend"].items():
            if ":" in k:
                kind, item = k.split(":", 1)
                net[item] -= v
        sides.append({"team": s["team"], "money": s["money"], "land": s["land"], "hires": s["hires"],
                      "hire_cost": s["spend"].get("HIRE", 0), "peak": peak, "net": dict(net),
                      "units": {i: v[0] for i, v in s["sales"].items()},
                      "lost": sum(s["lost"].values()),
                      "tiles_by_day": {d: dict(s["days"][d]["tiles"]) for d in (5, 8, 11, 14, 17, 20, 23, 26)}})
    return {"id": rec["id"], "teams": rec["teams"], "rewards": rec["rewards"], "shops_end": rec["shops"],
            "shops18": shops18, "f18": features(shops18), "fend": features(rec["shops"]), "sides": sides}


def mean(xs):
    return st.mean(xs) if xs else 0.0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("tapes", nargs="+")
    p.add_argument("--team", required=True)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--out")
    a = p.parse_args()
    recs = []
    for path in a.tapes:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            recs += [json.loads(line) for line in f if line.strip()]
    recs = [r for r in {r["id"]: r for r in recs}.values() if a.team in (r.get("teams") or [])]
    print(f"{len(recs)} games with {a.team}")
    with mp.Pool(a.workers) as pool:
        rows = pool.map(job, recs, chunksize=1)
    if a.out:
        json.dump(rows, open(a.out, "w"))
    report(rows, a.team)


def report(rows, team):
    def pick(r):
        i = r["teams"].index(team)
        return r["sides"][i], r["sides"][1 - i], r["rewards"][i] - r["rewards"][1 - i]
    buckets = [("all", lambda f: True),
               ("STRAW>=6", lambda f: f["STRAWBERRY"] >= 6), ("TOMATO==3", lambda f: f["TOMATO"] == 3),
               ("TOMATO>=4", lambda f: f["TOMATO"] >= 4), ("WOOL>=3", lambda f: f["WOOL"] >= 3),
               ("CARROT>=3", lambda f: f["CARROT"] >= 3), ("MILK>=4", lambda f: f["MILK"] >= 4),
               ("EGG>=3", lambda f: f["EGG"] >= 3)]
    for name, cond in buckets:
        sel = [r for r in rows if cond(r["fend"])]
        if not sel:
            continue
        t = [pick(r) for r in sel]
        w = sum(m > 0 for _, _, m in t)
        me = [x for x, _, _ in t]
        op = [y for _, y, _ in t]
        print(f"\n== {name}: {len(sel)} games, {team} {w}-{len(sel) - w}, mean margin {mean([m for _, _, m in t]):+.0f}")
        land = collections.Counter(tuple(x["land"]) for x in me).most_common(3)
        print(f"  land days (top): {land}")
        print(f"  {'':10s} {team[:10]:>10s} {'opp':>10s}")
        print(f"  {'money':10s} {mean([x['money'] for x in me]):10.0f} {mean([y['money'] for y in op]):10.0f}")
        print(f"  {'hires':10s} {mean([x['hires'] for x in me]):10.1f} {mean([y['hires'] for y in op]):10.1f}")
        print(f"  {'hire$':10s} {mean([x['hire_cost'] for x in me]):10.0f} {mean([y['hire_cost'] for y in op]):10.0f}")
        for k in TILE_KEYS:
            a_, b_ = mean([x["peak"][k] for x in me]), mean([y["peak"][k] for y in op])
            if a_ or b_:
                print(f"  {'peak ' + k[:5]:10s} {a_:10.1f} {b_:10.1f}")
        items = sorted({i for x in me + op for i in x["net"]})
        for i in items:
            a_, b_ = mean([x["net"].get(i, 0) for x in me]), mean([y["net"].get(i, 0) for y in op])
            if abs(a_) > 50 or abs(b_) > 50:
                print(f"  {'net ' + i[:6]:10s} {a_:10.0f} {b_:10.0f}")
        print(f"  {'lost':10s} {mean([x['lost'] for x in me]):10.0f} {mean([y['lost'] for y in op]):10.0f}")


if __name__ == "__main__":
    main()
