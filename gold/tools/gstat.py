r"""Per-day statistics of local games from engine hooks: labour mix, losses, trades, farm state, DSM references.

.venv\Scripts\python.exe gold\tools\gstat.py A_MAIN B_MAIN SEED [--side 0|1] [--json OUT.json]
    one game, A in seat 0 and B in seat 1: per-day table of --side, totals of both sides
.venv\Scripts\python.exe gold\tools\gstat.py A_MAIN B_MAIN --seeds N --seed0 S [--both] [--workers W] [--json OUT.json]
    N seeds (each seed in both seats with --both) in a spawn pool; A is the candidate: per-day averages of A,
    per-game totals, final money of every game

Unit-turns: every existing unit (farmer + hands) every step. move = NORTH/SOUTH/EAST/WEST; effective = the tile,
the unit's inventory or the shed changed; pass = PASS, a malformed action, or a hand the agent sent no action for;
noop = a tile op that changed nothing (PLANT_NOSEED: PLANT the engine turned into PASS for lack of seeds).
Crop deaths = plants turned to weed at the daily refresh (missed watering); rot = yield units lost after the
lifespan (_decay_plants). Overflow = units destroyed because the shed was full (DROP and the end-of-day drop).
Cash at the end of day d is taken after its last step (day 29: after step 718, the last one fastarena runs, so it
equals the reward); the daily minimum is over the money before and after every step of the day.
DSM columns come from research/dsm_plan/out (92 games): cash is the median, hires / animals / crops are means.
"""
import argparse
import collections
import json
import math
import multiprocessing as mp
import os
import sys
import time
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import fastarena  # noqa: E402  (imports kaggle_environments with only the kaggriculture env)
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa: E402

C = collections.Counter
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["COW", "SHEEP", "GOOSE"]
ITEMS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
ABBR = {"WHEAT": "WHT", "CARROT": "CAR", "TOMATO": "TOM", "STRAWBERRY": "STR", "MELON": "MEL", "EGG": "EGG",
        "MILK": "MLK", "WOOL": "WOL", "FERTILIZER": "FER", "COW": "COW", "SHEEP": "SHP", "GOOSE": "GOS"}
OPS = ["WATER", "HARVEST", "PLANT", "FEED", "CARE", "COLLECT_FERTILIZER", "FERTILIZE", "PICKUP", "PLACE", "DROP",
       "DIG", "BUILD_COOP", "BUILD_PASTURE"]
TILE_OPS = set(OPS)
MOVES = set(K.FARMER_MOVES)

# ---- DSM references (research/dsm_plan/out) ----
# misc.md 8a "median money end of day"
DSM_CASH = {0: 6, 1: 3, 2: 9, 3: 18, 4: 433, 5: 836, 6: 34, 7: 75, 8: 2166, 9: 230, 10: 2082, 11: 5406, 12: 7788,
            13: 11479, 14: 20088, 15: 26613, 16: 36160, 17: 41466, 18: 49783, 19: 54914, 20: 61602, 21: 66216,
            22: 70924, 23: 74626, 24: 79833, 25: 84412, 26: 90540, 27: 96426, 28: 103487, 29: 110228}
# hires.md 5a "hires mean"
DSM_HIRES = {0: 4.0, 1: 4.7, 2: 6.3, 3: 6.0, 4: 5.4, 5: 6.0, 6: 8.0, 7: 8.8, 8: 9.0, 9: 10.1, 10: 12.1, 11: 11.3,
             12: 11.3, 13: 11.1, 14: 11.5, 15: 11.8, 16: 11.9, 17: 11.9, 18: 12.0, 19: 11.9, 20: 11.6, 21: 11.9,
             22: 11.8, 23: 11.7, 24: 11.6, 25: 11.7, 26: 11.5, 27: 11.2, 28: 10.9, 29: 10.0}
# alloc.md 3a mean tiles at the end of the day (no day 29): COW, SHEEP, GOOSE
DSM_ANIMALS = {0: (2.0, 3.0, 0.0), 1: (2.0, 3.0, 0.0), 2: (2.0, 3.0, 0.0), 3: (2.0, 3.0, 0.0), 4: (2.0, 3.0, 0.0),
               5: (2.0, 3.0, 0.0), 6: (6.3, 4.1, 1.6), 7: (7.0, 4.2, 1.9), 8: (7.5, 4.8, 1.9), 9: (9.2, 5.3, 4.4),
               10: (9.3, 5.8, 6.2), 11: (9.3, 5.8, 7.1), 12: (9.5, 6.5, 7.1), 13: (9.5, 6.5, 7.1),
               14: (9.5, 6.5, 7.1), 15: (9.4, 6.7, 7.1), 16: (9.4, 6.7, 7.1), 17: (9.3, 6.7, 7.1),
               18: (9.2, 6.6, 7.1), 19: (9.0, 6.5, 7.1), 20: (8.9, 6.5, 7.0), 21: (8.6, 6.2, 7.0),
               22: (8.5, 6.1, 6.9), 23: (8.2, 6.0, 6.8), 24: (8.1, 5.6, 6.8), 25: (7.6, 4.8, 6.7),
               26: (7.5, 4.6, 6.7), 27: (7.2, 4.0, 6.5), 28: (6.7, 0.8, 5.7)}
# alloc.md 3a: WHEAT, CARROT, TOMATO, STRAWBERRY, MELON
DSM_CROPS = {0: (9.0, 0.0, 0.0, 0.0, 6.0), 1: (9.7, 0.0, 0.0, 0.0, 9.9), 2: (4.2, 0.0, 0.0, 3.8, 9.9),
             3: (0.1, 0.0, 0.0, 9.7, 9.9), 4: (0.0, 0.0, 0.0, 10.0, 9.9), 5: (0.0, 0.0, 0.0, 10.0, 9.9),
             6: (5.9, 0.1, 0.1, 17.0, 9.9), 7: (8.2, 0.1, 0.1, 17.6, 9.9), 8: (7.5, 0.3, 0.2, 17.7, 9.9),
             9: (18.8, 0.5, 4.1, 19.3, 9.9), 10: (27.9, 2.2, 5.7, 21.7, 3.9), 11: (31.9, 3.0, 8.2, 23.9, 0.0),
             12: (29.2, 3.4, 9.9, 27.7, 0.0), 13: (27.2, 3.7, 11.4, 28.9, 0.0), 14: (26.2, 3.9, 11.9, 28.9, 0.0),
             15: (23.2, 4.1, 13.1, 30.4, 0.0), 16: (21.9, 3.8, 14.4, 30.4, 0.0), 17: (20.7, 3.9, 15.8, 30.4, 0.0),
             18: (20.0, 3.9, 20.1, 26.5, 0.0), 19: (21.6, 4.7, 21.7, 21.8, 0.0), 20: (24.2, 6.7, 18.5, 20.0, 0.0),
             21: (25.2, 8.5, 16.5, 19.7, 0.0), 22: (29.1, 10.6, 14.2, 15.5, 0.0), 23: (30.9, 12.5, 12.6, 12.3, 0.0),
             24: (31.4, 15.1, 10.9, 11.6, 0.0), 25: (29.5, 18.2, 10.3, 10.3, 0.0), 26: (27.6, 22.9, 9.2, 8.6, 0.0),
             27: (25.2, 19.5, 8.3, 6.6, 0.0), 28: (13.3, 9.4, 7.4, 5.5, 0.0)}
# misc.md 8c sales per game: units, revenue
DSM_SALES = {"WHEAT": (538, 19341), "CARROT": (179, 7825), "TOMATO": (154, 10877), "STRAWBERRY": (216, 30889),
             "MELON": (60, 12467), "EGG": (211, 9898), "MILK": (202, 23794), "WOOL": (143, 21775),
             "FERTILIZER": (243, 12990)}
DSM_HIRE_TOTAL = (299, 6809)  # hires.md 5a season totals per game
# hires.md 5b, days 10-14 / 15-19 / 20-24 / 25-29: unit-turns per day, move %, pass %, no-effect %
DSM_MIX = [(285, 39.8, 0.1, 0.3), (293, 38.4, 0.1, 0.3), (290, 37.1, 0.1, 0.2), (273, 43.7, 0.7, 0.3)]

# ---- engine hooks ----
_ORIG = {}
_CUR = {"farms": None, "privates": None, "day": 0, "hour": 0, "raw": ([], []), "calls": [0, 0]}
_STATS = None  # (days of seat 0, days of seat 1) while a game runs


def _new_day(d):
    return {"day": d, "turns": 0, "move": 0, "effective": 0, "pass": 0, "noop": 0,
            "move_blocked": 0, "invalid": 0, "missing": 0, "eff_ops": C(), "noop_ops": C(),
            "plant_deaths": C(), "rot_units": C(), "rot_weeds": C(), "escapes": C(), "escape_units": C(),
            "overflow_drop": C(), "overflow_eod": C(), "sell_units": C(), "sell_rev": C(),
            "buy_units": C(), "buy_spend": C(), "hires": 0, "hire_cost": 0.0, "land": [],
            "min_money": None, "end": None}


def _D(p, day):
    days = _STATS[p]
    while len(days) <= day:
        days.append(_new_day(len(days)))
    return days[day]


def _pid(farm):
    return 0 if farm is _CUR["farms"][0] else 1


def _snapshot(farm, private):
    animals, crops, struct = C(), C(), C()
    weeds = empty = 0
    for row in farm["tiles"]:
        for t in row:
            if t is None:
                empty += 1
            elif isinstance(t, dict):
                if "animal" in t:
                    animals[t["animal"]] += 1
                elif t.get("kind") == "PLANT":
                    crops[t["crop"]] += 1
                elif t.get("kind") == "WEED":
                    weeds += 1
                else:
                    struct[t.get("kind")] += 1  # empty COOP / PASTURE
    shed = private["shed"]
    return {"money": farm["money"], "animals": dict(animals), "crops": dict(crops), "weeds": weeds, "empty": empty,
            "empty_struct": dict(struct), "shed": sum(shed.values()), "shed_items": {k: v for k, v in shed.items() if v},
            "seeds": {k: v for k, v in private["seeds"].items() if v}, "quads": list(farm["unlocked_quadrants"])}


def _interp(state, env):
    obs0 = state[0].observation
    farms = getattr(obs0, "farms", None)
    if _STATS is None or not farms or env.done:
        return _ORIG["interp"](state, env)
    cfg = env.configuration
    tpd = max(1, int(K.get(cfg, "turnsPerDay", 24)))
    step = K.get(obs0, "step", 0)
    day = step // tpd
    raw = []
    for s in state:  # unit actions as the engine reads them, to spot PLANTs it turns into PASS
        a = s.action if isinstance(s.action, dict) else {}
        hands = a.get("hands", [])
        raw.append([a.get("farmer", ["PASS"])] + (hands if isinstance(hands, list) else []))
    _CUR.update(farms=farms, privates=[s.observation.private for s in state], day=day, hour=step % tpd, raw=raw,
                calls=[0] * len(farms))
    units = [1 + len(f["hands"]) for f in farms]
    for i, f in enumerate(farms):  # the money the agent observed at this step
        d = _D(i, day)
        if d["min_money"] is None or f["money"] < d["min_money"]:
            d["min_money"] = f["money"]
    res = _ORIG["interp"](state, env)
    last = step >= int(K.get(cfg, "episodeSteps", 720)) - 2
    for i, f in enumerate(farms):
        d = _D(i, day)
        d["min_money"] = min(d["min_money"], f["money"])  # and after it, so the minimum never exceeds the day's end
        miss = units[i] - _CUR["calls"][i]
        if miss > 0:  # hands without an action stand still
            d["turns"] += miss
            d["pass"] += miss
            d["missing"] += miss
        if (step + 1) % tpd == 0 or last:
            d["end"] = _snapshot(f, state[i].observation.private)
    return res


def _unit(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=100):
    orig = _ORIG["unit"]
    pos = K._farmer_position(farm, idx) if _STATS is not None else None
    if pos is None:  # no game being measured, or an action for a hand that does not exist (ignored by the engine)
        return orig(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)
    p = _pid(farm)
    d = _D(p, day)
    _CUR["calls"][p] += 1
    d["turns"] += 1
    op = action[0] if isinstance(action, list) and action else None
    if not isinstance(op, str):
        op = None
    if op in MOVES:
        x, y = pos[0], pos[1]
        orig(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)
        d["move"] += 1
        q = K._farmer_position(farm, idx)
        if q[0] == x and q[1] == y:
            d["move_blocked"] += 1  # off the board
        return
    if op not in TILE_OPS:
        orig(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)
        r = _CUR["raw"][p][idx] if idx < len(_CUR["raw"][p]) else None
        if op == "PASS" and isinstance(r, list) and len(r) >= 2 and r[0] == "PLANT":
            d["noop"] += 1
            d["noop_ops"]["PLANT_NOSEED"] += 1
        else:
            d["pass"] += 1
            if op != "PASS":
                d["invalid"] += 1
        return
    x, y = pos[0], pos[1]
    tiles = farm["tiles"]
    t0 = tiles[y][x]
    if isinstance(t0, dict):
        t0 = dict(t0)  # tiles are flat dicts of scalars, so this copy is a deep copy
    invs = private["inventories"]
    inv0 = dict(invs[idx]) if idx < len(invs) else {}
    shed = private["shed"]
    shed0 = dict(shed)
    orig(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)
    invs = private["inventories"]
    inv1 = invs[idx] if idx < len(invs) else {}
    tile_changed = tiles[y][x] != t0
    if tile_changed or inv1 != inv0 or shed != shed0:
        d["effective"] += 1
        d["eff_ops"][op] += 1
        if op == "DROP" or (op == "PLACE" and not tile_changed):
            for item, n in inv0.items():  # left the inventory but never reached the shed
                lost = n - inv1.get(item, 0) - (shed.get(item, 0) - shed0.get(item, 0))
                if lost > 0:
                    d["overflow_drop"][item] += lost
    else:
        d["noop"] += 1
        d["noop_ops"][op] += 1


def _plants(farm, day, tpd):
    tiles = farm["tiles"]
    before = [(x, y, t["crop"]) for y, row in enumerate(tiles) for x, t in enumerate(row)
              if isinstance(t, dict) and t.get("kind") == "PLANT"]
    res = _ORIG["plants"](farm, day, tpd)
    if _STATS is not None:
        d = _D(_pid(farm), day)
        for x, y, crop in before:
            t = tiles[y][x]
            if isinstance(t, dict) and t.get("kind") == "WEED":
                d["plant_deaths"][crop] += 1
    return res


def _animals(farm, day):
    tiles = farm["tiles"]
    before = [(x, y, t["animal"], t.get("yield_units", 0)) for y, row in enumerate(tiles) for x, t in enumerate(row)
              if isinstance(t, dict) and "animal" in t]
    res = _ORIG["animals"](farm, day)
    if _STATS is not None:
        d = _D(_pid(farm), day)
        for x, y, animal, held in before:
            t = tiles[y][x]
            if not (isinstance(t, dict) and "animal" in t):
                d["escapes"][animal] += 1
                d["escape_units"][animal] += held
    return res


def _decay(farm, step):
    tiles = farm["tiles"]
    due = []
    if _STATS is not None:  # plants past their lifespan lose one unit every other step, then turn to weed
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == "PLANT":
                    mls = t["max_lifespan_step"]
                    if 0 <= mls <= step and (step - mls) % 2 == 0:
                        due.append((x, y, t["crop"], t["yield_units"]))
    res = _ORIG["decay"](farm, step)
    if due:
        d = _D(_pid(farm), _CUR["day"])
        for x, y, crop, held in due:
            if held > 0:
                d["rot_units"][crop] += 1
            t = tiles[y][x]
            if isinstance(t, dict) and t.get("kind") == "WEED":
                d["rot_weeds"][crop] += 1
    return res


def _drop_eod(private, capacity):
    carried = C()
    for inv in private["inventories"]:
        for k, v in inv.items():
            if v > 0:
                carried[k] += v
    shed0 = dict(private["shed"])
    res = _ORIG["drop"](private, capacity)
    if carried and _STATS is not None:
        d = _D(0 if private is _CUR["privates"][0] else 1, _CUR["day"])
        shed = private["shed"]
        for item, n in carried.items():
            lost = n - (shed.get(item, 0) - shed0.get(item, 0))
            if lost > 0:
                d["overflow_eod"][item] += lost
    return res


def _commit(op, item, price, farm, private, market, shed_capacity=100):
    ok = _ORIG["commit"](op, item, price, farm, private, market, shed_capacity)
    if ok and _STATS is not None:
        d = _D(_pid(farm), _CUR["day"])
        if op == "SELL":
            d["sell_units"][item] += 1
            d["sell_rev"][item] += price
        else:
            key = op[4:] + ":" + item  # SEED:WHEAT, PRODUCT:WHEAT, PRODUCT:FERTILIZER, ANIMAL:COW
            d["buy_units"][key] += 1
            d["buy_spend"][key] += price
    return ok


def _hire(farm, *args, **kw):
    m0, n0 = farm["money"], len(farm["hands"])
    res = _ORIG["hire"](farm, *args, **kw)
    if _STATS is not None and len(farm["hands"]) > n0:
        d = _D(_pid(farm), _CUR["day"])
        d["hires"] += 1
        d["hire_cost"] += m0 - farm["money"]
    return res


def _land(farm, *args, **kw):
    m0, q0 = farm["money"], len(farm["unlocked_quadrants"])
    res = _ORIG["land"](farm, *args, **kw)
    if _STATS is not None and len(farm["unlocked_quadrants"]) > q0:
        _D(_pid(farm), _CUR["day"])["land"].append([_CUR["hour"], farm["unlocked_quadrants"][-1], m0 - farm["money"]])
    return res


def install_hooks():
    if _ORIG:
        return
    _ORIG.update(interp=K.interpreter, unit=K._apply_unit_action, plants=K._daily_refresh_plants,
                 animals=K._daily_refresh_animals, decay=K._decay_plants, drop=K._drop_inventories_to_shed,
                 commit=K._commit_unit, hire=K._do_hire, land=K._do_buy_land)
    K.interpreter, K._apply_unit_action = _interp, _unit
    K._daily_refresh_plants, K._daily_refresh_animals, K._decay_plants = _plants, _animals, _decay
    K._drop_inventories_to_shed, K._commit_unit, K._do_hire, K._do_buy_land = _drop_eod, _commit, _hire, _land


def _timed(fn, sink):
    def timed(obs, conf=None):
        t = time.perf_counter()
        try:
            return fastarena._call(fn, obs, conf)  # same obs/conf convention fastarena uses for fn itself
        finally:
            sink.append((time.perf_counter() - t) * 1000.0)
    return timed


def _q(xs, q):
    s = sorted(xs)
    return s[min(len(s) - 1, max(0, math.ceil(q * len(s)) - 1))] if s else 0.0


def _tsum(xs):
    return {"n": len(xs), "mean": sum(xs) / len(xs) if xs else 0.0, "p99": _q(xs, 0.99), "max": max(xs, default=0.0)}


def load_worlds(path=None):
    """Shop sequences (8 shops each) of real games, used to force the town in local games."""
    import gzip
    path = path or os.path.join(ROOT, "data", "games", "dsm.jsonl.gz")
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                sh = json.loads(line).get("shops") or []
                if len(sh) == 8:
                    out.append(list(sh))
    return out


def play_one(job):
    """job = (seat-0 agent, seat-1 agent, seed, reported side[, forced shops]). Main process or spawn worker."""
    global _STATS
    seats, seed, side = list(job[:2]), job[2], job[3]
    shops = job[4] if len(job) > 4 else None
    import forceshops
    forceshops.force(shops)
    install_hooks()
    t0 = time.time()
    os.environ["GOLD_SEED"] = str(seed)       # read only by diagnostic agent builds
    fns = [fastarena.load_agent(p) for p in seats]
    times = ([], [])
    _STATS = ([], [])
    try:
        r = fastarena.run_game(_timed(fns[0], times[0]), _timed(fns[1], times[1]), seed)
    finally:
        days, _STATS = _STATS, None
    return {"seats": seats, "seed": seed, "cand_side": side, "shops": shops, "rewards": r["rewards"], "status": r["status"],
            "errors": r["errors"], "start_money": float(K.get(r["env"].configuration, "startingMoney", 3000)),
            "time_ms": [_tsum(t) for t in times],
            "step_ms": [[round(x, 3) for x in t] for t in times], "days": [list(x) for x in days],
            "wall": round(time.time() - t0, 1)}


# ---- output ----
def _width(s):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def _isnum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def table(headers, rows):
    rows = [["" if v is None else str(v) for v in r] for r in rows]
    ws = [max(map(_width, col)) for col in zip(headers, *rows)]
    right = [all(_isnum(c) for c in col if c) for col in zip(*rows)] if rows else [False] * len(headers)

    def line(cells):
        return "  ".join(" " * (w - _width(c)) + c if r else c + " " * (w - _width(c))
                         for c, w, r in zip(cells, ws, right)).rstrip()

    print(line(headers))
    print("  ".join("-" * w for w in ws))
    for r in rows:
        print(line(r))


def f0(v):
    return "" if v is None else f"{v:.0f}"


def f1(v):
    return "" if v is None else f"{v:.1f}"


def _avg(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def name(path):
    p = path.replace("\\", "/").rstrip("/")
    parts = p.split("/")
    return parts[-2] if parts[-1] == "main.py" and len(parts) > 1 else os.path.splitext(parts[-1])[0]


def day_rows(games, multi):
    fs = f1 if multi else f0
    rows = []
    for d in range(max(len(g["days"][g["cand_side"]]) for g in games)):
        ds = [g["days"][g["cand_side"]][d] for g in games if d < len(g["days"][g["cand_side"]])]
        n = len(ds)
        ends = [x["end"] for x in ds if x["end"]]
        turns = sum(x["turns"] for x in ds)

        def pct(k):
            return 100.0 * sum(x[k] for x in ds) / turns if turns else None

        units, rev = C(), C()
        for x in ds:
            units.update(x["sell_units"])
            rev.update(x["sell_rev"])
        top = " ".join(f"{ABBR[k]} {units[k] / n:.0f}" for k, _ in rev.most_common(3))
        an = "/".join(f0(_avg([e["animals"].get(a, 0) for e in ends])) for a in ANIMALS) if ends else ""
        cr = "/".join(f0(_avg([e["crops"].get(c, 0) for e in ends])) for c in CROPS) if ends else ""
        da, dc = DSM_ANIMALS.get(d), DSM_CROPS.get(d)
        rows.append([
            d, f0(_avg([e["money"] for e in ends])), f0(_avg([x["min_money"] for x in ds])),
            fs(_avg([x["hires"] for x in ds])), f0(turns / n),
            f1(pct("move")), f1(pct("effective")), f1(pct("pass")), f1(pct("noop")),
            fs(_avg([sum(x["plant_deaths"].values()) for x in ds])), fs(_avg([sum(x["escapes"].values()) for x in ds])),
            fs(_avg([sum(x["overflow_drop"].values()) + sum(x["overflow_eod"].values()) for x in ds])),
            f0(_avg([sum(x["sell_rev"].values()) for x in ds])), top, an, cr,
            fs(_avg([e["weeds"] for e in ends])), fs(_avg([e["empty"] for e in ends])), f0(_avg([e["shed"] for e in ends])),
            "|", DSM_CASH.get(d, ""), f1(DSM_HIRES.get(d)),
            "/".join(f0(v) for v in da) if da else "-", "/".join(f0(v) for v in dc) if dc else "-"])
    return rows


SUMS = ("sell_units", "sell_rev", "buy_units", "buy_spend", "plant_deaths", "rot_units", "escapes", "escape_units",
        "overflow_drop", "overflow_eod", "eff_ops", "noop_ops")


def side_totals(games, side_of):
    """Season sums of one side over all games (divide by len(games) for per-game means)."""
    t = {k: C() for k in SUMS}
    t.update(hires=0, hire_cost=0.0, land=[], mix=C(), sub=C(), ms=[])
    for g in games:
        s = side_of(g)
        for d in g["days"][s]:
            for k in SUMS:
                t[k].update(d[k])
            t["hires"] += d["hires"]
            t["hire_cost"] += d["hire_cost"]
            t["land"] += [[d["day"]] + list(x) for x in d["land"]]
            for k in ("move_blocked", "invalid", "missing"):
                t["sub"][k] += d[k]
            if d["day"] >= 10:
                for k in ("turns", "move", "effective", "pass", "noop"):
                    t["mix"][k] += d[k]
                t["mix"]["days"] += 1
        t["ms"] += g["step_ms"][s]
    return t


def _by(counter, n):
    return " ".join(f"{ABBR.get(k, k)} {v / n:.{1 if n > 1 else 0}f}" for k, v in counter.most_common() if v)


def print_totals(games, labels):
    n = len(games)
    T = [side_totals(games, lambda g: g["cand_side"]), side_totals(games, lambda g: 1 - g["cand_side"])]
    per = "（每局平均）" if n > 1 else ""

    print(f"\n卖出{per}")
    rows = []
    for it in ITEMS:
        cells = [it]
        for t in T:
            u, r = t["sell_units"].get(it, 0), t["sell_rev"].get(it, 0)
            cells += [f0(u / n), f0(r / n), f0(r / u) if u else ""]
        cells += list(DSM_SALES[it])
        rows.append(cells)
    tot = [sum(t["sell_rev"].values()) / n for t in T]
    rows.append(["合计", "", f0(tot[0]), "", "", f0(tot[1]), "", "", sum(v[1] for v in DSM_SALES.values())])
    table(["产品", labels[0] + " 件", "收入", "均价", labels[1] + " 件", "收入", "均价", "DSM 件", "DSM 收入"], rows)

    print(f"\n支出{per}：件数 / 花费（细分为件数）")

    def buys(t, prefix):
        ks = [k for k in t["buy_units"] if k.startswith(prefix)]
        u, s = sum(t["buy_units"][k] for k in ks), sum(t["buy_spend"][k] for k in ks)
        detail = _by(C({k.split(":")[1]: t["buy_units"][k] for k in ks}), n)
        return u, s, detail

    rows = []
    rows.append(["雇工"] + [f"{t['hires'] / n:.0f} / {t['hire_cost'] / n:.0f}" for t in T]
                + [f"{DSM_HIRE_TOTAL[0]} / {DSM_HIRE_TOTAL[1]}"])
    land = []
    for t in T:
        c = f"{len(t['land']) / n:.{1 if n > 1 else 0}f} / {sum(x[3] for x in t['land']) / n:.0f}"
        if n == 1 and t["land"]:
            c += "（" + " ".join(f"{q}@{d}:{h:02d}" for d, h, q, _ in t["land"]) + "）"
        land.append(c)
    rows.append(["买地"] + land + [""])
    for label, prefix in (("牲口", "ANIMAL:"), ("种子", "SEED:"), ("小麦", "PRODUCT:WHEAT"), ("肥料", "PRODUCT:FERTILIZER")):
        cells = []
        for t in T:
            u, s, detail = buys(t, prefix)
            cells.append(f"{u / n:.0f} / {s / n:.0f}" + (f"（{detail}）" if detail and prefix.endswith(":") else ""))
        rows.append([label] + cells + [""])
    rows.append(["合计"] + [f"{(t['hire_cost'] + sum(x[3] for x in t['land']) + sum(t['buy_spend'].values())) / n:.0f}"
                          for t in T] + [""])
    table(["项目", labels[0], labels[1], "DSM"], rows)

    print(f"\n损耗{per}")
    rows = []
    for label, fn in (
            ("作物死（没浇水，棵）", lambda t: t["plant_deaths"]),
            ("烂在地里（过期掉的产量，件）", lambda t: t["rot_units"]),
            ("牲口跑（头）", lambda t: t["escapes"]),
            ("牲口跑时带走的产出（件）", lambda t: t["escape_units"]),
            ("爆仓丢：DROP（件）", lambda t: t["overflow_drop"]),
            ("爆仓丢：日末自动入仓（件）", lambda t: t["overflow_eod"])):
        rows.append([label] + [f"{sum(fn(t).values()) / n:.{1 if n > 1 else 0}f}"
                               + (f"（{_by(fn(t), n)}）" if sum(fn(t).values()) else "") for t in T])
    table(["项目", labels[0], labels[1]], rows)

    print("\n单位回合构成，第 10 到 29 天")
    w = sum(r[0] for r in DSM_MIX)
    dm = [sum(r[0] * r[i] for r in DSM_MIX) / w for i in (1, 2, 3)]
    dsm = {"turns": w / len(DSM_MIX), "move": dm[0], "pass": dm[1], "noop": dm[2], "effective": 100 - sum(dm)}
    rows = [["回合/天"] + [f0(t["mix"]["turns"] / t["mix"]["days"]) if t["mix"]["days"] else "" for t in T]
            + [f0(dsm["turns"])]]
    for label, k in (("走路%", "move"), ("有效%", "effective"), ("空闲%", "pass"), ("无效%", "noop")):
        rows.append([label] + [f1(100.0 * t["mix"][k] / t["mix"]["turns"]) if t["mix"]["turns"] else "" for t in T]
                    + [f1(dsm[k])])
    table(["", labels[0], labels[1], "DSM"], rows)

    print(f"\n动作次数{per}：有效 / 无效（没效果）")
    rows = []
    for op in OPS + ["PLANT_NOSEED"]:
        cells = [f"{t['eff_ops'].get(op, 0) / n:.0f} / {t['noop_ops'].get(op, 0) / n:.0f}" for t in T]
        if any(t["eff_ops"].get(op) or t["noop_ops"].get(op) for t in T):
            rows.append([op] + cells)
    for label, k in (("走路出界（算在走路里）", "move_blocked"), ("格式不对（算在空闲里）", "invalid"),
                     ("雇工没给动作（算在空闲里）", "missing")):
        rows.append([label] + [f"{t['sub'][k] / n:.0f}" for t in T])
    table(["动作", labels[0], labels[1]], rows)

    print("\n每步耗时（毫秒）：" + "；".join(
        f"{lab} 平均 {s['mean']:.1f}，p99 {s['p99']:.1f}，最大 {s['max']:.0f}"
        for lab, s in zip(labels, (_tsum(t["ms"]) for t in T))))


def check_money(g):
    """Final snapshot == reward, and start + sales - hires - land - purchases == reward (every money flow hooked)."""
    bad = []
    for s in (0, 1):
        days = g["days"][s]
        end = days[-1]["end"] if days else None
        r = g["rewards"][s]
        flow = g["start_money"] + sum(sum(d["sell_rev"].values()) - d["hire_cost"] - sum(x[2] for x in d["land"])
                                      - sum(d["buy_spend"].values()) for d in days)
        if end is None or r is None or abs(end["money"] - r) > 1e-6 or abs(flow - r) > 1e-6:
            bad.append(f"座位{s} 快照 {end and end['money']} 现金流 {flow} 奖励 {r}")
    return bad


def main():
    ap = argparse.ArgumentParser(description="kaggriculture 本地对局逐日统计（引擎钩子）")
    ap.add_argument("a", help="A 的 main.py（座位 0；多局模式下是候选）")
    ap.add_argument("b", help="B 的 main.py")
    ap.add_argument("seed", nargs="?", type=int, help="单局模式的种子")
    ap.add_argument("--side", type=int, choices=(0, 1), default=0, help="单局模式：逐日表显示哪一方")
    ap.add_argument("--seeds", type=int, help="多局模式：种子个数")
    ap.add_argument("--seed0", type=int, help="多局模式：第一个种子（默认用位置参数 SEED，否则 0）")
    ap.add_argument("--both", action="store_true", help="多局模式：每个种子双方各坐一次两个座位")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--json", help="把双方的逐日原始数据写到这个文件")
    ap.add_argument("--worlds", action="store_true", help="多局模式：用 DSM 92 局的真实商店顺序强制每局的商店（种子 i 用第 i 个）")
    ap.add_argument("--world0", type=int, default=0, help="多局模式：第一个种子用第几个世界（默认 0，之后依次加一）")
    ap.add_argument("--world-list", help="多局模式：逗号分隔的世界编号，种子依次循环使用（优先于 --world0）")
    ap.add_argument("--worlds-file", help="多局模式：JSON 文件，里面是若干个 8 家商店的列表，代替 DSM 的 92 个世界")
    ap.add_argument("--alt", action="store_true", help="多局模式：每个种子只打一局，A 的座位按种子交替（偶数座位 0，奇数座位 1）")
    a = ap.parse_args()
    worlds = (json.load(open(a.worlds_file)) if a.worlds_file else load_worlds()) if (a.worlds or a.worlds_file) else None
    na, nb = name(a.a), name(a.b)

    if a.seeds:
        seed0 = a.seed0 if a.seed0 is not None else (a.seed if a.seed is not None else 0)
        jobs = []
        for s in range(seed0, seed0 + a.seeds):
            if worlds and a.world_list:
                wl = [int(x) for x in a.world_list.split(",") if x.strip()]
                w = worlds[wl[(s - seed0) % len(wl)] % len(worlds)]
            else:
                w = worlds[(s - seed0 + a.world0) % len(worlds)] if worlds else None
            if a.alt and (s - seed0) % 2 == 1:
                jobs.append((a.b, a.a, s, 1, w))
                continue
            jobs.append((a.a, a.b, s, 0, w))
            if a.both:
                jobs.append((a.b, a.a, s, 1, w))
        workers = max(1, min(a.workers, len(jobs)))
        print(f"{len(jobs)} 局，{workers} 个进程", flush=True)
        games, t0 = [], time.time()
        with mp.get_context("spawn").Pool(workers, maxtasksperchild=1) as pool:
            for k, g in enumerate(pool.imap_unordered(play_one, jobs), 1):
                games.append(g)
                c = g["cand_side"]
                print(f"[{k}/{len(jobs)}] 种子 {g['seed']} A 在座位{c}：A {f0(g['rewards'][c])}，"
                      f"B {f0(g['rewards'][1 - c])}（{g['wall']:.0f} 秒）", flush=True)
        games.sort(key=lambda g: (g["seed"], g["cand_side"]))
        labels = (f"A {na}", f"B {nb}")
        seats = "，每个种子两个座位各一次" if a.both else "，A 在座位 0"
        print(f"\n候选 A={na} 对 B={nb}：种子 {seed0} 到 {seed0 + a.seeds - 1}{seats}，共 {len(games)} 局，"
              f"用时 {time.time() - t0:.0f} 秒。下表是 A 的逐日平均")
    else:
        if a.seed is None:
            ap.error("需要 SEED（单局）或 --seeds N（多局）")
        g = play_one((a.a, a.b, a.seed, a.side))
        games = [g]
        names = (na, nb)
        labels = (f"座位{a.side} {names[a.side]}", f"座位{1 - a.side} {names[1 - a.side]}")
        print(f"座位0 {na} 对 座位1 {nb}，种子 {a.seed}，状态 {'/'.join(g['status'])}，报错 {g['errors']}，"
              f"用时 {g['wall']:.0f} 秒。下表是 {labels[0]}")

    print("现金=日末；最低=当天每步前后的最低现金；回合=单位回合；走路/有效/空闲/无效见文件开头说明；"
          "爆仓丢=仓库满丢掉的件数；主要卖出=按收入前三（件数）；牲口C/S/G；作物w/c/t/s/m=小麦/胡萝卜/番茄/草莓/甜瓜；"
          "DSM 列：现金为中位数，其余为均值")
    table(["天", "现金", "最低", "雇工", "回合", "走路%", "有效%", "空闲%", "无效%", "作物死", "牲口跑", "爆仓丢",
           "卖出收入", "主要卖出", "牲口C/S/G", "作物w/c/t/s/m", "杂草", "空地", "仓库",
           "|", "DSM现金", "雇工", "牲口C/S/G", "作物w/c/t/s/m"], day_rows(games, len(games) > 1))

    print_totals(games, labels)

    bad = [f"种子 {g['seed']}：" + "，".join(b) for g in games for b in [check_money(g)] if b]
    if len(games) == 1:
        g = games[0]
        c = g["cand_side"]
        r = g["rewards"]
        diff = f"{r[c] - r[1 - c]:+.0f}" if None not in r else ""
        print(f"\n最终现金：{labels[0]} {f0(r[c])}，{labels[1]} {f0(r[1 - c])}，差 {diff}")
    else:
        print("\n每局最终现金")
        rows, res = [], C()
        for g in games:
            c = g["cand_side"]
            ra, rb = g["rewards"][c], g["rewards"][1 - c]
            if ra is None or rb is None:
                out, diff = "报错", ""
            else:
                out = "胜" if ra > rb else "负" if ra < rb else "平"
                diff = f"{ra - rb:+.0f}"
            res[out] += 1
            rows.append([g["seed"], c, f0(ra), f0(rb), diff, out, f0(g["wall"])])
        table(["种子", "A座位", "A现金", "B现金", "差", "结果", "秒"], rows)
        ok = [g for g in games if None not in g["rewards"]]
        if ok:
            ma = _avg([g["rewards"][g["cand_side"]] for g in ok])
            mb = _avg([g["rewards"][1 - g["cand_side"]] for g in ok])
            print(f"A 胜 {res['胜']} 负 {res['负']} 平 {res['平']}" + (f" 报错 {res['报错']}" if res["报错"] else "")
                  + f"；平均现金 A {ma:.0f}，B {mb:.0f}，差 {ma - mb:+.0f}")
    print("校验：最后快照现金、起始现金加收入减支出、run_game 奖励三者" + ("一致" if not bad else "不一致：" + "；".join(bad)))

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"a": a.a, "b": a.b, "games": games}, f, ensure_ascii=False)
        print(f"原始数据：{a.json}")


if __name__ == "__main__":
    main()
