r"""Per-product revenue and spend of both seats in live-game replays with CAND in our seat (rival tape kept).

    .venv\Scripts\python.exe gold\front\prodrep.py CAND.py ID [ID ...] [--workers 8] [--phases 0,10,20,26]

Prints per game: margin, then per item (rival minus us) sale revenue by day phase, units sold, and spend
differences (seeds, animals, hires, land, bought products).
"""
import argparse
import collections
import json
import multiprocessing as mp
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)


def play(job):
    cand, rec_path, phases = job
    import fastarena
    import forceshops
    from cfroute import tape_file
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    rec = json.load(open(rec_path, encoding="utf-8"))
    me = rec["teams"].index("42")
    REV = [collections.defaultdict(float), collections.defaultdict(float)]
    UNITS = [collections.Counter(), collections.Counter()]
    SPEND = [collections.defaultdict(float), collections.defaultdict(float)]
    CUR = {}
    orig_pm, orig_cu, orig_hire, orig_land = K._process_market, K._commit_unit, K._do_hire, K._do_buy_land

    def ph(step):
        d = step // 24
        k = 0
        for i, p in enumerate(phases):
            if d >= p:
                k = i
        return k

    def pm(state, env):
        CUR["step"] = state[0].observation.step
        CUR["farms"] = state[0].observation.farms
        return orig_pm(state, env)

    def seat(farm):
        for i, f in enumerate(CUR["farms"]):
            if f is farm:
                return i
        return -1

    def cu(op, item, price, farm, private, market, shed_capacity=100):
        ok = orig_cu(op, item, price, farm, private, market, shed_capacity)
        if ok:
            s = seat(farm)
            if op == "SELL":
                REV[s][(item, ph(CUR["step"]))] += price
                UNITS[s][item] += 1
            else:
                SPEND[s][op.replace("BUY_", "") + ":" + item] += price
        return ok

    def hire(farm, private, board_size, mult=1):
        before = farm["money"]
        orig_hire(farm, private, board_size, mult)
        SPEND[seat(farm)]["HIRE"] += before - farm["money"]

    def land(farm, board_size):
        before = farm["money"]
        orig_land(farm, board_size)
        SPEND[seat(farm)]["LAND"] += before - farm["money"]

    K._process_market, K._commit_unit, K._do_hire, K._do_buy_land = pm, cu, hire, land
    forceshops.force(rec["shops"])
    fns = [None, None]
    fns[me] = fastarena.load_agent(cand)
    fns[1 - me] = fastarena.load_agent(tape_file(rec, 1 - me))
    r = fastarena.run_game(fns[0], fns[1], rec["seed"])
    margin = (r["rewards"][me] or 0) - (r["rewards"][1 - me] or 0)
    op = 1 - me
    items = sorted({k[0] for k in list(REV[0]) + list(REV[1])})
    rev = {it: [round(REV[op][(it, p)] - REV[me][(it, p)]) for p in range(len(phases))] for it in items}
    units = {it: [UNITS[me][it], UNITS[op][it]] for it in items}
    sp = {k: round(SPEND[op].get(k, 0) - SPEND[me].get(k, 0)) for k in set(SPEND[0]) | set(SPEND[1])}
    return {"id": rec["id"], "opp": rec["teams"][op], "margin": margin, "rev": rev, "units": units, "spend": sp}


def main():
    from tgrun import find_recs
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--phases", default="0,10,20,26")
    ap.add_argument("--json")
    a = ap.parse_args()
    phases = [int(x) for x in a.phases.split(",")]
    recs = find_recs(a.ids)
    tmp = os.path.join(ROOT, "gold", "tmp", "tgrun")
    os.makedirs(tmp, exist_ok=True)
    jobs = []
    for rid, r in recs.items():
        p = os.path.join(tmp, f"{rid}.json")
        json.dump(r, open(p, "w", encoding="utf-8"))
        jobs.append((os.path.abspath(a.cand), p, phases))
    with mp.get_context("spawn").Pool(min(a.workers, len(jobs)), maxtasksperchild=1) as pool:
        out = list(pool.imap(play, jobs))
    tot = collections.defaultdict(float)
    for g in sorted(out, key=lambda g: g["margin"]):
        print(f"\n{g['id']} vs {g['opp']}: margin {g['margin']:+.0f}   (rival minus us, phases from day {phases})")
        for it, v in sorted(g["rev"].items(), key=lambda kv: -abs(sum(kv[1]))):
            if abs(sum(v)) >= 50:
                u = g["units"][it]
                print(f"   {it:11s} {' '.join(f'{x:+7d}' for x in v)}  total {sum(v):+7d}   units us {u[0]} rival {u[1]}")
                tot[it] += sum(v)
        big = {k: v for k, v in g["spend"].items() if abs(v) >= 100}
        print("   spend (rival minus us):", big)
    print("\nsum over games (rival minus us):", {k: round(v) for k, v in sorted(tot.items(), key=lambda kv: -abs(kv[1]))})
    if a.json:
        json.dump(out, open(a.json, "w", encoding="utf-8"))


if __name__ == "__main__":
    main()
