r"""Instrumented exact replay of the DSM games through the real kaggriculture engine.

    .venv\Scripts\python.exe research\dsm_plan\replay.py            build cache\<id>.pkl.gz for all games
    .venv\Scripts\python.exe research\dsm_plan\replay.py --check    also assert local money == server reward

Each record in data\games\dsm.jsonl.gz is stepped exactly like tools\econ.py does it
(make env with the record's seed, reset(2), state[i].action = acts[i][t+1], K.interpreter,
obs.step = t+1).  On top of that, every unit action of the DSM side is logged together with
the tile it stood on before/after the action, and every executed market unit, hire and land
purchase of both sides is logged.  Per-step observation summaries and end-of-day tile grids
are stored as well.  The cache is what all the analysis scripts in this folder read.

Cache format (one gzip pickle per game, see load_games()):
  id, seed, side, opp, teams, rewards, shops (final 8), acts (DSM, 720), oacts (opponent, 720)
  steps[t]   (t = 0..718, observation BEFORE the action of step t is applied):
             money (DSM), omoney (opponent), shed{}, seeds{}, prices{}, minv{}, nshops,
             nh (hands present), hires (hires_today), pos [farmer, hand1, ...]
  units      list of (t, idx, action, (x, y), tile_before, tile_after, inv_delta{})
             for every DSM unit that exists at step t (idx 0 = farmer, i = hand i)
  mkt        list of (t, pid, op, item, price) for every executed unit (both sides, pid 0/1)
  hire       list of (t, pid, cost)
  land       list of (t, pid, quadrant, cost, money_before)
  eod[d]     tiles after the end-of-day refresh of day d (= start of day d+1): [dsm_grid, opp_grid]
             grid[y][x] = tcode(tile)
  final      [dsm money, opponent money] after step 718
  final_stock  DSM shed + unit inventories after step 718 (unsold, worth $0)
tcode(tile): None | 'L' | ('W',) | ('S', 'COOP'|'PASTURE') (empty structure)
             | ('P', crop, planted_day, yield_units, fertilized_until_day, watered_today,
                     consecutive_unwatered, max_lifespan_step)
             | ('A', kind, animal, placed_day, yield_units, fed_today, cared_today,
                     fertilizer_available, pending_care_bonus, consecutive_unfed)
"""
import gzip
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(ROOT, "data", "games", "dsm.jsonl.gz")
CACHE = os.path.join(HERE, "cache")
TEAM = "DSM"


def _quiet_import():
    # kaggle_environments prints OpenSpiel game lists from C++ on import; silence fds 1 and 2
    sys.stdout.flush()
    sys.stderr.flush()
    saved = os.dup(1), os.dup(2)
    null = os.open(os.devnull, os.O_WRONLY)
    os.dup2(null, 1)
    os.dup2(null, 2)
    try:
        from kaggle_environments import make
        from kaggle_environments.envs.kaggriculture import kaggriculture
    finally:
        os.dup2(saved[0], 1)
        os.dup2(saved[1], 2)
        os.close(null)
    return make, kaggriculture


make, K = _quiet_import()

_ORIG = {"commit": K._commit_unit, "hire": K._do_hire, "land": K._do_buy_land, "unit": K._apply_unit_action}
CUR = {}


def tcode(t):
    if t is None:
        return None
    if t == "LOCKED":
        return "L"
    kind = t.get("kind")
    if kind == "WEED":
        return ("W",)
    if kind == "PLANT":
        return ("P", t["crop"], t["planted_day"], t["yield_units"], t["fertilized_until_day"],
                t["watered_today"], t["consecutive_unwatered"], t["max_lifespan_step"])
    if "animal" in t:
        return ("A", kind, t["animal"], t["placed_day"], t["yield_units"], t["fed_today"], t["cared_today"],
                t["fertilizer_available"], t.get("pending_care_bonus", 0), t["consecutive_unfed"])
    return ("S", kind)


def _pid(farm):
    return 0 if farm is CUR["farms"][0] else 1


def _commit(op, item, price, farm, private, market, shed_capacity=100):
    ok = _ORIG["commit"](op, item, price, farm, private, market, shed_capacity)
    if ok:
        CUR["mkt"].append((CUR["step"], _pid(farm), op, item, price))
    return ok


def _hire(farm, private, board_size, mult=1):
    before = farm["money"]
    _ORIG["hire"](farm, private, board_size, mult)
    if farm["money"] != before:
        CUR["hire"].append((CUR["step"], _pid(farm), before - farm["money"]))


def _land(farm, board_size):
    before = farm["money"]
    _ORIG["land"](farm, board_size)
    if farm["money"] != before:
        CUR["land"].append((CUR["step"], _pid(farm), farm["unlocked_quadrants"][-1], before - farm["money"], before))


def _unit(farm, private, idx, action, *args, **kw):
    if _pid(farm) != CUR["side"]:
        return _ORIG["unit"](farm, private, idx, action, *args, **kw)
    pos = K._farmer_position(farm, idx)
    if pos is None:
        return _ORIG["unit"](farm, private, idx, action, *args, **kw)
    x, y = pos[0], pos[1]
    tb = tcode(farm["tiles"][y][x])
    inv = private["inventories"][idx] if idx < len(private["inventories"]) else {}
    ib = dict(inv)
    _ORIG["unit"](farm, private, idx, action, *args, **kw)
    ta = tcode(farm["tiles"][y][x])
    ia = private["inventories"][idx] if idx < len(private["inventories"]) else {}
    delta = {k: ia.get(k, 0) - ib.get(k, 0) for k in set(ia) | set(ib) if ia.get(k, 0) != ib.get(k, 0)}
    CUR["units"].append((CUR["step"], idx, action if isinstance(action, list) else None, (x, y), tb, ta, delta))


K._commit_unit, K._do_hire, K._do_buy_land, K._apply_unit_action = _commit, _hire, _land, _unit


def load_records(path=DATA):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _nz(d):
    return {k: v for k, v in d.items() if v}


def replay(rec):
    side = rec["teams"].index(TEAM)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": rec["seed"]}, debug=False)
    env.reset(2)
    state = env.state
    obs = state[0].observation
    CUR.clear()
    CUR.update(side=side, farms=obs.farms, mkt=[], hire=[], land=[], units=[], step=0)
    steps, eod = [], []
    n = len(rec["acts"][0])
    for t in range(719):
        CUR["step"] = t
        me, op = obs.farms[side], obs.farms[1 - side]
        priv = state[side].observation.private
        steps.append({
            "money": me["money"], "omoney": op["money"], "shed": _nz(priv["shed"]), "seeds": _nz(priv["seeds"]),
            "prices": dict(obs.market["prices"]), "minv": dict(obs.market["inventory"]),
            "nshops": len(obs.town["unlocked_shops"]), "nh": len(me["hands"]), "hires": me["hires_today"],
            "pos": [tuple(me["farmer"])] + [tuple(h) for h in me["hands"]],
        })
        for i in range(2):
            a = rec["acts"][i][t + 1] if t + 1 < n else None
            state[i].action = a if isinstance(a, dict) else None
        K.interpreter(state, env)
        obs.step = t + 1
        if (t + 1) % 24 == 0:
            eod.append({"tiles": [[[tcode(x) for x in row] for row in obs.farms[s]["tiles"]] for s in (side, 1 - side)],
                        "shops": list(obs.town["unlocked_shops"]), "money": [obs.farms[side]["money"], obs.farms[1 - side]["money"]],
                        "quads": list(obs.farms[side]["unlocked_quadrants"]),
                        "shed": _nz(state[side].observation.private["shed"])})
    final = [obs.farms[side]["money"], obs.farms[1 - side]["money"]]
    fpriv = state[side].observation.private
    final_stock = _nz(fpriv["shed"])
    for inv in fpriv["inventories"]:
        for k, v in inv.items():
            final_stock[k] = final_stock.get(k, 0) + v
    mkt =[(t, 0 if p == side else 1, o, it, pr) for (t, p, o, it, pr) in CUR["mkt"]]
    hire = [(t, 0 if p == side else 1, c) for (t, p, c) in CUR["hire"]]
    land = [(t, 0 if p == side else 1, q, c, mb) for (t, p, q, c, mb) in CUR["land"]]
    return {"id": rec["id"], "seed": rec["seed"], "side": side, "opp": rec["teams"][1 - side], "teams": rec["teams"],
            "rewards": [rec["rewards"][side], rec["rewards"][1 - side]], "shops": rec["shops"],
            "acts": rec["acts"][side], "oacts": rec["acts"][1 - side], "steps": steps, "units": list(CUR["units"]),
            "mkt": mkt, "hire": hire, "land": land, "eod": eod, "final": final, "final_stock": final_stock}


def _work(rec):
    g = replay(rec)
    path = os.path.join(CACHE, f"{rec['id']}.pkl.gz")
    with gzip.open(path, "wb", compresslevel=5) as f:
        pickle.dump(g, f, protocol=pickle.HIGHEST_PROTOCOL)
    return rec["id"], g["final"], g["rewards"]


def load_games(limit=None):
    """Load cached games (build cache first with `python replay.py`)."""
    out = []
    for name in sorted(os.listdir(CACHE)):
        if name.endswith(".pkl.gz"):
            with gzip.open(os.path.join(CACHE, name), "rb") as f:
                out.append(pickle.load(f))
            if limit and len(out) >= limit:
                break
    return out


def main():
    import multiprocessing as mp
    import time
    recs = load_records()
    os.makedirs(CACHE, exist_ok=True)
    t0 = time.time()
    ctx = mp.get_context("spawn")
    bad = 0
    with ctx.Pool(min(12, os.cpu_count() or 4)) as pool:
        for gid, final, rewards in pool.imap_unordered(_work, recs):
            ok = abs(final[0] - rewards[0]) < 0.5 and abs(final[1] - rewards[1]) < 0.5
            bad += not ok
            if not ok:
                print(f"MISMATCH {gid} local {final} server {rewards}")
    print(f"{len(recs)} games cached in {time.time() - t0:.0f}s, mismatches {bad}")


if __name__ == "__main__":
    main()
