r"""Execution benchmark: our executor redoes DSM's work list of one day from DSM's start state.

    .venv\Scripts\python.exe gold\tools\execbench.py [--games 8] [--days 6,10,15,20,25] [--game ID] [-v]

Per (game, day): start from dsmday.make_farm_private (tiles, shed, seeds, units at step 24d), DSM's effective tile
ops of the day become jobs (one job per tile, DSM's op order; a PLANT may not start before the step its seed is in
stock, a PLACE not before its animal is in the shed). DSM's hires (same steps, spawn by the engine rule), purchases
and sales are replayed at DSM's steps; our executor may only take the shed wheat/fertilizer that DSM's own later
sales of the day do not need. Units act through the engine's _apply_unit_action; end of day runs the engine refresh.

Reported per day and in total: unit-turns, moves / effective / pass shares for us and DSM, ops left undone, and
end-of-day differences vs DSM (plants dead, animals escaped, yield in the ground, products harvested).
"""
import argparse
import collections
import copy
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "gold", "newagent"))
import dsmday as D  # noqa: E402
import executor as E  # noqa: E402

BIGCAP = 10 ** 6
TRACE = None
USE_FUTURE = True


def spawn_pos(positions):
    occ = {a: 0 for a in D.ACCESS}
    for p in positions:
        if tuple(p) in occ:
            occ[tuple(p)] += 1
    return list(sorted(occ.items(), key=lambda kv: (kv[1], D.ACCESS.index(kv[0])))[0][0])


def build_jobs(g, d):
    t0 = D.TPD * d
    acts = D.day_actions(g, d)
    mkt = D.day_market(g, d)
    st = D.day_state(g, d)
    seed_t = {c: [t0] * st["seeds"].get(c, 0) for c in D.CROPS}
    for c, e in mkt["seeds"].items():
        for (t, n) in e["steps"]:
            seed_t[c] += [t + 1] * n
    an_t = {a: [t0] * st["shed"].get(a, 0) for a in D.ANIMALS}
    for a, e in mkt["animals"].items():
        for (t, n) in e["steps"]:
            an_t[a] += [t + 2] * n
    # PLANT / PLACE ops in DSM time order get the k-th seed / animal
    plants = sorted((t, xy, i) for xy, ops in acts["tile_ops"].items() for i, (t, op, arg) in enumerate(ops)
                    if op == "PLANT")
    places = sorted((t, xy, i) for xy, ops in acts["tile_ops"].items() for i, (t, op, arg) in enumerate(ops)
                    if op == "PLACE")
    ear = {}
    used = collections.Counter()
    for (t, xy, i) in plants:
        c = acts["tile_ops"][xy][i][2]
        k = used[c]
        used[c] += 1
        ear[(xy, i)] = seed_t[c][k] if k < len(seed_t[c]) else t
    used = collections.Counter()
    for (t, xy, i) in places:
        a = acts["tile_ops"][xy][i][2]
        k = used[a]
        used[a] += 1
        ear[(xy, i)] = an_t[a][k] if k < len(an_t[a]) else t
    land_ready = {}
    for (t, q, cost, mb) in mkt["land"]:
        land_ready[q] = t + 1
    def quad(xy):
        return ("N" if xy[1] < 5 else "S") + ("W" if xy[0] < 5 else "E")
    for key in list(ear.keys()):
        pass
    jobs = []
    ANIM_OPS = {"FEED", "CARE", "COLLECT_FERTILIZER", "HARVEST"}
    for (xy, ops) in sorted(acts["tile_ops"].items()):
        oplist = [[op, arg] for (t, op, arg) in ops]
        oe = [max(ear.get((xy, i), t0), land_ready.get(quad(xy), t0)) for i in range(len(ops))]
        tile = st["tiles"][xy[1]][xy[0]]
        opn = [o[0] for o in oplist]
        isd = isinstance(tile, dict)
        if isd and "animal" in tile and all(o in ANIM_OPS for o in opn):
            crit = tile.get("consecutive_unfed", 0) >= 1
            if SPLIT_ANIMALS:
                for o, e in zip(oplist, oe):
                    pr = 0 if (crit and o[0] == "FEED") else 2
                    jobs.append(E.Job(len(jobs), xy, [o], earliest=t0, op_earliest=[e], prio=pr,
                                      value=10.0 if pr == 0 else 1.0))
                continue
            pr = 0 if (crit and "FEED" in opn) else 2
        elif isd and tile.get("kind") == "PLANT" and tile.get("consecutive_unwatered", 0) >= 1 and "WATER" in opn:
            pr = 0
        elif "PLANT" in opn:
            pr = 1
        else:
            pr = 2
        jobs.append(E.Job(len(jobs), xy, oplist, earliest=t0, op_earliest=oe, prio=pr,
                          value=10.0 if pr == 0 else (3.0 if pr == 1 else 1.0)))
    return jobs, acts, mkt, st


SPLIT_ANIMALS = True


def run_day(g, d, ex_factory, verbose=False):
    K = D.engine()
    t0 = D.TPD * d
    t_end = t0 + D.TPD
    farm, private = D.make_farm_private(g, d)
    jobs, acts, mkt, st = build_jobs(g, d)
    n_ops = sum(len(J.ops) for J in jobs)
    ex = ex_factory()
    for J in jobs:
        ex.add_job(J)
    un = D.day_units(g, d)
    hires = collections.Counter()
    for (t, c) in un["hires"]:
        hires[t] += c
    # market events
    sales = collections.defaultdict(list)
    for item, e in mkt["sales"].items():
        for (t, n) in e["steps"]:
            sales[t].append((item, n))
    buys = collections.defaultdict(list)
    for grp in ("animals", "products"):
        for item, e in mkt[grp].items():
            for (t, n) in e["steps"]:
                buys[t].append((item, n))
    seedbuys = collections.defaultdict(list)
    for item, e in mkt["seeds"].items():
        for (t, n) in e["steps"]:
            seedbuys[t].append((item, n))
    land_t = collections.Counter(t for (t, q, cost, mb) in mkt["land"])
    # budget: we may take from the shed as much wheat / fertilizer as DSM's units took that day; DSM's sales of
    # these two are not replayed (its late sales are fed by the day's harvests and collections)
    budget = collections.Counter()
    for so in acts["shed_ops"]:
        if so["op"] == "PICKUP" and so["item"] in ("WHEAT", "FERTILIZER"):
            budget[so["item"]] += so["delta"].get(so["item"], 0)
    taken = collections.Counter()
    mix = collections.Counter()
    shed0 = dict(private["shed"])
    sold = collections.Counter()
    t_plan = 0.0
    for t in range(t0, t_end):
        units = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
        invs = [K._farmer_inventory(private, i) for i in range(len(units))]
        shed = private["shed"]
        avail_w = max(0, min(shed.get("WHEAT", 0), budget["WHEAT"] - taken["WHEAT"]))
        avail_f = max(0, min(shed.get("FERTILIZER", 0), budget["FERTILIZER"] - taken["FERTILIZER"]))
        an_av = {a: shed.get(a, 0) for a in D.ANIMALS if shed.get(a, 0) > 0}
        # hands hired later today (known to the agent since it orders them): spawn round-robin on access tiles
        future = []
        occ = collections.Counter(tuple(p) for p in units if tuple(p) in D.ACCESS_SET)
        for th in sorted(hires):
            if th >= t:
                for _ in range(hires[th]):
                    a_ = min(D.ACCESS, key=lambda q: (occ[q], D.ACCESS.index(q)))
                    occ[a_] += 1
                    future.append((th + 1, a_))
        c0 = time.perf_counter()
        actions = ex.act(t, t_end, d, units, invs, farm["tiles"], shed, private["seeds"], avail_w, avail_f, an_av,
                         future=future if USE_FUTURE else ())
        t_plan += time.perf_counter() - c0
        # atomic PLANT check
        dem = collections.Counter(a[1] for a in actions if a and a[0] == "PLANT")
        blocked = {c for c, n in dem.items() if n > private["seeds"].get(c, 0)}
        for i, a in enumerate(actions):
            if a and a[0] == "PLANT" and a[1] in blocked:
                a = ["PASS"]
                mix["blocked_plant"] += 1
            op = a[0]
            if op in D.MOVES:
                mix["move"] += 1
            elif op == "PASS":
                mix["pass"] += 1
            else:
                mix["op"] += 1
            if TRACE is not None:
                TRACE.setdefault(i, []).append((t, tuple(units[i]) if i < len(units) else None, a))
            if a and a[0] == "PICKUP" and a[1] in ("WHEAT", "FERTILIZER"):
                before = private["shed"].get(a[1], 0)
                K._apply_unit_action(farm, private, i, a, D.BOARD, d, D.TPD, BIGCAP)
                taken[a[1]] += before - private["shed"].get(a[1], 0)
                continue
            K._apply_unit_action(farm, private, i, a, D.BOARD, d, D.TPD, BIGCAP)
        # market of step t
        for item, n in sales.get(t, []):
            if item in ("WHEAT", "FERTILIZER"):
                continue
            take = min(n, private["shed"].get(item, 0))
            private["shed"][item] -= take
            sold[item] += take
        for item, n in buys.get(t, []):
            private["shed"][item] = private["shed"].get(item, 0) + n
        for item, n in seedbuys.get(t, []):
            private["seeds"][item] = private["seeds"].get(item, 0) + n
        for _ in range(land_t.get(t, 0)):
            farm["money"] = 10 ** 9
            K._do_buy_land(farm, D.BOARD)
        for _ in range(hires.get(t, 0)):
            pos = [farm["farmer"]] + farm["hands"]
            farm["hands"].append(spawn_pos(pos))
            private["inventories"].append({})
        K._decay_plants(farm, t)
    left = [(J.xy, J.ops) for J in ex.jobs.values() if J.ops]
    n_left = sum(len(o) for _, o in left)
    K._daily_refresh_plants(farm, d, D.TPD)
    K._daily_refresh_animals(farm, d)
    harvested = collections.Counter()
    for inv in private["inventories"]:
        for k, v in inv.items():
            harvested[k] += v
    for k, v in private["shed"].items():
        harvested[k] += v - shed0.get(k, 0)
    for k, v in sold.items():
        harvested[k] += v
    ours = summarize_tiles(farm["tiles"])
    dsm_end = summarize_tiles(D.end_state(g, d))
    ds = D.day_stats(g, d, acts, un)
    turns = mix["move"] + mix["pass"] + mix["op"]
    res = {"game": g["id"], "day": d, "turns": turns, "move": mix["move"], "pass": mix["pass"], "op": mix["op"],
           "ops_total": n_ops, "ops_left": n_left, "left": left,
           "dsm_turns": ds["unit_turns"], "dsm_move": ds["move"], "dsm_eff": ds["effective"],
           "dsm_pass": ds["pass"] + ds["idle"], "ours_end": ours, "dsm_end": dsm_end,
           "plan_s": t_plan, "stats": dict(ex.stats)}
    return res


def summarize_tiles(tiles):
    s = collections.Counter()
    for row in tiles:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    s["plants"] += 1
                    s["yield"] += t.get("yield_units", 0)
                    s["fert"] += t.get("fertilized_until_day", -1) >= 0
                elif "animal" in t:
                    s["animals"] += 1
                    s["ayield"] += t.get("yield_units", 0)
                    s["care"] += t.get("pending_care_bonus", 0)
                elif t.get("kind") == "WEED":
                    s["weeds"] += 1
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=8)
    ap.add_argument("--days", default="6,10,15,20,25")
    ap.add_argument("--game")
    ap.add_argument("--replan", type=int, default=4)
    ap.add_argument("--balance", type=float, default=0.5)
    ap.add_argument("-v", action="store_true")
    ap.add_argument("--tries", type=int, default=6)
    ap.add_argument("--nosplit", action="store_true")
    ap.add_argument("--nofuture", action="store_true")
    ap.add_argument("--dispatch", action="store_true")
    ap.add_argument("--urgency", type=float, default=40.0)
    a = ap.parse_args()
    paths = D.list_games()
    if a.game:
        paths = [a.game]
    else:
        k = max(1, min(a.games, len(paths)))
        paths = [paths[i * (len(paths) - 1) // max(1, k - 1)] for i in range(k)]
    days = [int(x) for x in a.days.split(",")]
    global SPLIT_ANIMALS, USE_FUTURE
    SPLIT_ANIMALS = not a.nosplit
    USE_FUTURE = not a.nofuture
    fac = lambda: E.Executor(replan_every=a.replan, balance=a.balance, tries=a.tries)  # noqa: E731
    if a.dispatch:
        import dispatch as DP
        fac = lambda: DP.Dispatcher(urgency=a.urgency)  # noqa: E731
    tot = collections.Counter()
    print("game       day | turns us/dsm | move% us/dsm | op us/dsm | pass% us/dsm | left | end: plants yield animals"
          " ayield care weeds (us-dsm) | plan s")
    for p in paths:
        g = D.load_game(p)
        for d in days:
            r = run_day(g, d, fac, a.v)
            oe, de = r["ours_end"], r["dsm_end"]
            diff = {k: oe[k] - de[k] for k in ("plants", "yield", "animals", "ayield", "care", "weeds")}
            sk = {k[5:]: v for k, v in r["stats"].items() if k.startswith("skip_") or k.startswith("requeue")}
            print(f"{r['game']} {d:3d} | {r['turns']:4d}/{r['dsm_turns']:4d} | "
                  f"{100 * r['move'] / max(1, r['turns']):4.1f}/{100 * r['dsm_move'] / max(1, r['dsm_turns']):4.1f} | "
                  f"{r['op']:3d}/{r['dsm_eff']:3d} | {100 * r['pass'] / max(1, r['turns']):4.1f}/"
                  f"{100 * r['dsm_pass'] / max(1, r['dsm_turns']):4.1f} | {r['ops_left']:3d} | "
                  + " ".join(f"{diff[k]:+d}" for k in diff) + f" | {r['plan_s']:.2f} | skip {sk}")
            if a.v and r["left"]:
                print("   left:", r["left"][:12])
                print("   stats:", r["stats"])
            for k in ("turns", "move", "op", "pass", "ops_total", "ops_left", "dsm_turns", "dsm_move", "dsm_eff",
                      "dsm_pass"):
                tot[k] += r[k]
            for k, v in diff.items():
                tot["d_" + k] += v
            tot["plan_s"] += r["plan_s"]
            tot["n"] += 1
    n = tot["n"]
    print(f"\nTOTAL {n} days: move% us {100 * tot['move'] / tot['turns']:.1f} dsm {100 * tot['dsm_move'] / tot['dsm_turns']:.1f}"
          f" | ops done {tot['op']} of {tot['ops_total']} (left {tot['ops_left']}) dsm eff {tot['dsm_eff']}"
          f" | pass% us {100 * tot['pass'] / tot['turns']:.1f} dsm {100 * tot['dsm_pass'] / tot['dsm_turns']:.1f}"
          f" | end diffs per day: " + " ".join(f"{k[2:]} {tot[k] / n:+.2f}" for k in tot if k.startswith("d_"))
          + f" | plan {tot['plan_s'] / n:.2f}s/day")


if __name__ == "__main__":
    main()
