r"""Exact re-simulation of the DSM games with full per-step observations.

.venv\Scripts\python.exe research\dsm_sales\replay_dsm.py [--games N] [--procs P]

Writes research\dsm_sales\cache\dsm_replay.pkl.gz: one dict per game with
  meta     id, seed, teams, me (DSM side), shops, rewards, local money (checked against the server)
  shed     int16 [2, 720, 12]  shed contents seen at observation step t (before the action of step t)
  shedpm   int16 [2, 720, 12]  shed right before the market of step t (after that step's unit DROP/PLACE/PICKUP)
  shedam   int16 [2, 720, 12]  shed right after the market of step t
  carried  int16 [2, 720, 9]   goods carried in unit inventories at observation step t
  minv     int32 [720, 9]      market inventory seen at step t      mpx [720, 9] market prices seen at step t
  mpost    int32 [720, 9]      market inventory after the market of step t, before town consumption
  mtown    int32 [720, 9]      market inventory after town consumption of step t
  money    float [2, 720]      bank at observation step t
  nunits   int8  [2, 720]      farmer + hands at observation step t
  log      market commits (step, player, slot, op, item, price, inv_before)
  fail     failed commits (step, player, slot, op, item, price)
  units    DSM unit ops (step, idx, action, pos, tile_before, inv_before, inv_after, shed_total_before, shed_total_after)
  eod      end-of-day drops (step, player, carried, shed_before, shed_after)
  tiles    DSM tiles at every hour 0: {day: [(x, y, tile), ...]}
The approach is the one of tools\econ.py (recorded actions through the real interpreter with the
record's seed); this module does not import econ.py and does not touch tools\.
"""
import argparse
import collections
import copy
import gzip
import json
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(ROOT, "data", "games", "dsm.jsonl.gz")
CACHE = os.path.join(HERE, "cache", "dsm_replay.pkl.gz")


def _quiet_import():
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
PRODUCTS = list(K.PRODUCTS)
SHED_ITEMS = PRODUCTS + list(K.ANIMALS)
PI = {x: i for i, x in enumerate(PRODUCTS)}
LOG_OPS = {"HARVEST", "DROP", "PLACE", "PICKUP", "COLLECT_FERTILIZER", "FERTILIZE", "FEED", "PLANT", "DIG"}

_CUR = {}
_orig = {"commit": K._commit_unit, "hire": K._do_hire, "land": K._do_buy_land, "parse": K._parse_order,
         "unit": K._apply_unit_action, "eod": K._drop_inventories_to_shed, "town": K._town_consume,
         "market": K._process_market}


def _pid(farm):
    return 0 if farm is _CUR["farms"][0] else 1


def _parse(order):
    # the engine parses slot i of player 0, then slot i of player 1; find which by identity
    for p in (0, 1):
        for j, o in enumerate(_CUR["mk"][p]):
            if o is order:
                _CUR["slot"][p] = j
                break
    return _orig["parse"](order)


def _commit(op, item, price, farm, private, market, shed_capacity=100):
    p = _pid(farm)
    inv_before = market["inventory"].get(item) if item in market["inventory"] else None
    ok = _orig["commit"](op, item, price, farm, private, market, shed_capacity)
    rec = (_CUR["step"], p, _CUR["slot"][p], op, item, price, inv_before)
    (_CUR["log"] if ok else _CUR["fail"]).append(rec)
    return ok


def _hire(farm, private, board_size, mult=1):
    p = _pid(farm)
    before = farm["money"]
    _orig["hire"](farm, private, board_size, mult)
    if farm["money"] != before:
        _CUR["log"].append((_CUR["step"], p, _CUR["slot"][p], "HIRE", "", before - farm["money"], None))


def _land(farm, board_size):
    p = _pid(farm)
    before = farm["money"]
    _orig["land"](farm, board_size)
    if farm["money"] != before:
        _CUR["log"].append((_CUR["step"], p, _CUR["slot"][p], "LAND", farm["unlocked_quadrants"][-1],
                            before - farm["money"], None))


def _unit(farm, private, idx, action, *args, **kw):
    p = _pid(farm)
    op = action[0] if isinstance(action, list) and action else None
    if p != _CUR["me"] or op not in LOG_OPS:
        return _orig["unit"](farm, private, idx, action, *args, **kw)
    pos = K._farmer_position(farm, idx)
    tile = None
    if pos is not None:
        t = farm["tiles"][pos[1]][pos[0]]
        tile = copy.deepcopy(t) if isinstance(t, dict) else t
    invs = private["inventories"]
    inv_b = dict(invs[idx]) if idx < len(invs) else {}
    shed_b = sum(private["shed"].values())
    _orig["unit"](farm, private, idx, action, *args, **kw)
    invs = private["inventories"]
    inv_a = dict(invs[idx]) if idx < len(invs) else {}
    _CUR["units"].append((_CUR["step"], idx, list(action), tuple(pos) if pos is not None else None, tile,
                          inv_b, inv_a, shed_b, sum(private["shed"].values())))


def _eod(private, capacity):
    p = 0 if private is _CUR["privates"][0] else 1
    carried = collections.Counter()
    for inv in private["inventories"]:
        carried.update({k: v for k, v in inv.items() if v > 0})
    shed_before = dict(private["shed"])
    _orig["eod"](private, capacity)
    _CUR["eod"].append((_CUR["step"], p, dict(carried), shed_before, dict(private["shed"])))


def _market(state, env):
    t = _CUR["step"]
    for p in range(2):
        _CUR["shedpm"][p, t] = [state[p].observation.private["shed"].get(x, 0) for x in SHED_ITEMS]
    _orig["market"](state, env)
    for p in range(2):
        _CUR["shedam"][p, t] = [state[p].observation.private["shed"].get(x, 0) for x in SHED_ITEMS]


def _town(env, state, step):
    m = state[0].observation.market
    _CUR["mpost"][step] = [m["inventory"][x] for x in PRODUCTS]
    _orig["town"](env, state, step)
    _CUR["mtown"][step] = [m["inventory"][x] for x in PRODUCTS]


K._commit_unit, K._do_hire, K._do_buy_land, K._parse_order = _commit, _hire, _land, _parse
K._apply_unit_action, K._drop_inventories_to_shed, K._town_consume = _unit, _eod, _town
K._process_market = _market


def load_records(path=DATA):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def replay(rec):
    me = rec["teams"].index("DSM")
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": rec["seed"]}, debug=False)
    env.reset(2)
    state = env.state
    obs0 = state[0].observation
    T = 720
    g = {
        "shed": np.zeros((2, T, len(SHED_ITEMS)), np.int16), "carried": np.zeros((2, T, 9), np.int16),
        "shedpm": np.zeros((2, T, len(SHED_ITEMS)), np.int16), "shedam": np.zeros((2, T, len(SHED_ITEMS)), np.int16),
        "minv": np.zeros((T, 9), np.int32), "mpx": np.zeros((T, 9), np.int32),
        "mpost": np.zeros((T, 9), np.int32), "mtown": np.zeros((T, 9), np.int32),
        "money": np.zeros((2, T)), "nunits": np.zeros((2, T), np.int8), "tiles": {}, "shops_by_day": {},
    }
    _CUR.clear()
    _CUR.update(log=[], fail=[], units=[], eod=[], me=me, farms=obs0.farms,
                privates=[s.observation.private for s in state], slot=[-1, -1], mk=[[], []],
                mpost=g["mpost"], mtown=g["mtown"], shedpm=g["shedpm"], shedam=g["shedam"], step=0)
    n = len(rec["acts"][0])
    for t in range(T):
        # observation at step t (what both agents saw when they chose acts[.][t+1])
        for p in range(2):
            priv = state[p].observation.private
            g["shed"][p, t] = [priv["shed"].get(x, 0) for x in SHED_ITEMS]
            c = collections.Counter()
            for inv in priv["inventories"]:
                c.update(inv)
            g["carried"][p, t] = [c.get(x, 0) for x in PRODUCTS]
            g["money"][p, t] = obs0.farms[p]["money"]
            g["nunits"][p, t] = 1 + len(obs0.farms[p]["hands"])
        g["minv"][t] = [obs0.market["inventory"][x] for x in PRODUCTS]
        g["mpx"][t] = [obs0.market["prices"][x] for x in PRODUCTS]
        if t % 24 == 0:
            d = t // 24
            g["shops_by_day"][d] = list(obs0.town["unlocked_shops"])
            tl = []
            for y, row in enumerate(obs0.farms[me]["tiles"]):
                for x, tile in enumerate(row):
                    if isinstance(tile, dict):
                        tl.append((x, y, copy.deepcopy(tile)))
            g["tiles"][d] = tl
        if t == T - 1:
            break
        _CUR["step"] = t
        _CUR["slot"] = [-1, -1]
        for i in range(2):
            a = rec["acts"][i][t + 1] if t + 1 < n else None
            state[i].action = a if isinstance(a, dict) else None
            m = a.get("market") if isinstance(a, dict) else None
            _CUR["mk"][i] = m if isinstance(m, list) else []
        K.interpreter(state, env)
        obs0.step = t + 1
    money = [obs0.farms[i]["money"] for i in range(2)]
    g["meta"] = {"id": rec["id"], "seed": rec["seed"], "teams": rec["teams"], "me": me, "shops": rec["shops"],
                 "rewards": rec["rewards"], "money": money,
                 "ok": all(abs(money[i] - rec["rewards"][i]) < 0.5 for i in range(2))}
    for k in ("log", "fail", "units", "eod"):
        g[k] = _CUR[k]
    return g


def _work(rec):
    return replay(rec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=0)
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--out", default=CACHE)
    a = ap.parse_args()
    recs = load_records()
    if a.games:
        recs = recs[:a.games]
    t0 = time.time()
    if a.procs > 1:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(a.procs) as pool:
            games = pool.map(_work, recs, chunksize=1)
    else:
        games = [replay(r) for r in recs]
    bad = [g["meta"]["id"] for g in games if not g["meta"]["ok"]]
    print(f"{len(games)} games in {time.time() - t0:.0f}s; money mismatches: {bad}")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with gzip.open(a.out, "wb") as f:
        pickle.dump({"games": games, "acts": {r["id"]: r["acts"] for r in recs}}, f, protocol=pickle.HIGHEST_PROTOCOL)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
