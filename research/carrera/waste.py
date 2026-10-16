r"""Route-level waste of both sides in harvested live games: crops lost to missed watering, yield rotting after
the lifespan, escaped animals, seeds bought but never planted, and spending in the last days.

.venv/bin/python research/carrera/waste.py TAPES.jsonl.gz [--workers 2]
"""
import collections, gzip, json, multiprocessing as mp, os, statistics as st, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))


def job(rec):
    import econ
    K = econ.K
    me = rec["teams"].index("42")
    stats = [collections.Counter(), collections.Counter()]
    inner_plants, inner_decay, inner_animals = K._daily_refresh_plants, K._decay_plants, K._daily_refresh_animals
    farms = {}

    def side(farm):
        return 0 if farm is farms["f"][0] else 1

    def plants(farm, day, tpd):
        before = [[dict(t) if isinstance(t, dict) else t for t in row] for row in farm["tiles"]]
        inner_plants(farm, day, tpd)
        p = side(farm)
        for y, row in enumerate(farm["tiles"]):
            for x, t in enumerate(row):
                b = before[y][x]
                if isinstance(b, dict) and b.get("kind") == "PLANT" and isinstance(t, dict) and t.get("kind") == "WEED":
                    stats[p]["crop_death"] += 1
                    stats[p]["crop_death_yield"] += b.get("yield_units", 0)
                    stats[p][f"death_day_{day}"] += 1

    def decay(farm, step):
        before = sum(t.get("yield_units", 0) for row in farm["tiles"] for t in row if isinstance(t, dict) and t.get("kind") == "PLANT")
        inner_decay(farm, step)
        after = sum(t.get("yield_units", 0) for row in farm["tiles"] for t in row if isinstance(t, dict) and t.get("kind") == "PLANT")
        if before > after:
            stats[side(farm)]["rot_units"] += before - after

    def animals(farm, day):
        before = sum(1 for row in farm["tiles"] for t in row if isinstance(t, dict) and "animal" in t)
        inner_animals(farm, day)
        after = sum(1 for row in farm["tiles"] for t in row if isinstance(t, dict) and "animal" in t)
        if before > after:
            stats[side(farm)]["escaped"] += before - after

    K._daily_refresh_plants, K._decay_plants, K._daily_refresh_animals = plants, decay, animals
    try:
        env = econ.make("kaggriculture", configuration={"episodeSteps": 720, "seed": rec["seed"]}, debug=False)
        env.reset(2)
        state = env.state
        farms["f"] = state[0].observation.farms
        econ._CUR.update(log=[], farms=state[0].observation.farms, privates=[s.observation.private for s in state],
                         prices=state[0].observation.market["prices"])
        n = len(rec["acts"][0])
        for t in range(719):
            econ._CUR["step"] = t
            for i in range(2):
                a = rec["acts"][i][t + 1] if t + 1 < n else None
                state[i].action = a if isinstance(a, dict) else None
            K.interpreter(state, env)
            state[0].observation.step = t + 1
        for i in range(2):
            seeds = state[i].observation.private.get("seeds", {})
            stats[i]["seeds_left"] = sum(v for v in seeds.values() if v > 0)
            stats[i]["seeds_left_cost"] = sum(v * {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}.get(k, 0)
                                              for k, v in seeds.items() if v > 0)
        for step, p, op, item, price in econ._CUR["log"]:
            if step >= 26 * 24 and op in ("HIRE", "BUY_SEED", "BUY_ANIMAL"):
                stats[p][f"late_{op}"] += price
    finally:
        K._daily_refresh_plants, K._decay_plants, K._daily_refresh_animals = inner_plants, inner_decay, inner_animals
    return rec["id"], dict(stats[me]), dict(stats[1 - me]), rec["rewards"][me] - rec["rewards"][1 - me]


if __name__ == "__main__":
    W = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 2
    recs = [json.loads(l) for l in gzip.open(sys.argv[1], "rt", encoding="utf-8") if l.strip()]
    with mp.get_context("spawn").Pool(W) as pool:
        res = pool.map(job, recs, chunksize=2)
    keys = ["crop_death", "crop_death_yield", "rot_units", "escaped", "seeds_left", "seeds_left_cost", "late_HIRE", "late_BUY_SEED", "late_BUY_ANIMAL"]
    print(f"games {len(res)}")
    print("| item | us: games with any | us: mean | opponent: mean |")
    print("|---|---|---|---|")
    for k in keys:
        u = [r[1].get(k, 0) for r in res]; o = [r[2].get(k, 0) for r in res]
        print(f"| {k} | {sum(x > 0 for x in u)} | {st.mean(u):.1f} | {st.mean(o):.1f} |")
    dd = collections.Counter()
    for r in res:
        for k, v in r[1].items():
            if k.startswith("death_day_"):
                dd[int(k[10:])] += v
    print("our crop deaths by day:", dict(sorted(dd.items())))
