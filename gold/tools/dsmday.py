r"""One DSM day from the exact-replay cache, in engine terms (library + CLI).

    .venv\Scripts\python.exe gold\tools\dsmday.py [--game ID] --day D [--tiles]
    .venv\Scripts\python.exe gold\tools\dsmday.py --validate [--games 3] [--days 10,15,20] [--game ID]
    .venv\Scripts\python.exe gold\tools\dsmday.py --validate --all      every cached game, days 0..28

Source: research\dsm_plan\cache\<episode_id>.pkl.gz, written by research\dsm_plan\replay.py (the cache format is
documented at the top of that file). Day d covers steps 24d..24d+23. steps[t] is the observation BEFORE step t, and
the unit actions of step t are the ones DSM submitted as acts[t+1]. The engine's last step is 718, so day 29 has
steps 696..718 only and no end-of-day record (eod covers days 0..28).

Library (g = load_game(...); grids are grid[y][x]; tiles are real engine objects unless called "codes"):
  list_games()                sorted cache paths
  load_game(path_or_id=None)  game dict (full path, file name or episode id; None = first cached game)
  untcode(c), tcode(tile)     cache code <-> engine tile; untcode_grid(grid)
  day_state(g, d)             start of day d: tiles, quads, money, shed, seeds, shops, prices, minv, pos
  make_farm_private(g, d)     (farm, private) at the start of day d, ready for K._apply_unit_action
  day_units(g, d)             units present at each step, hires of the day
  day_actions(g, d)           classified unit actions, per-tile effective tile ops, shed ops
  day_market(g, d)            DSM's executed market units of the day, grouped; land purchases
  day_stats(g, d)             unit-turn mix, effective ops per op, plantings, first release step per crop
  end_state(g, d)             tiles after the end-of-day refresh of day d (d <= 28)
  replay_day(g, d)            re-apply DSM's unit actions of day d with the engine's own functions
  validate_day(g, d)          replay_day vs end_state, plus every unit action vs its record
  engine()                    the engine module K (lazy import that loads only the kaggriculture env)
  check_engine()              constants and tile key sets vs the engine; [] when everything matches
  render_map(tiles), summary(g, d)
Do not import research\dsm_plan\replay.py in the same process: it monkeypatches the engine functions.
"""
import argparse
import bisect
import collections
import contextlib
import copy
import gzip
import importlib.abc
import io
import os
import pickle
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(ROOT, "research", "dsm_plan", "cache")

# Engine constants (default configuration). check_engine() verifies them against the installed engine.
BOARD = 10
TPD = 24                      # turns per day
SHED_CAP = 100
WEED_CHANCE = 0.005
LAST_DAY = 29
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["GOOSE", "COW", "SHEEP"]                          # engine dict order (shed key order)
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
ACCESS = [(4, 4), (5, 4), (4, 5), (5, 5)]                    # shed-access tiles, NWSE order
ACCESS_SET = set(ACCESS)
TILE_OPS = ["WATER", "HARVEST", "PLANT", "FERTILIZE", "FEED", "CARE", "COLLECT_FERTILIZER", "DIG",
            "BUILD_COOP", "BUILD_PASTURE", "PLACE"]            # PLACE = animal put on a structure
SHED_OPS = ["PICKUP", "PLACE_SHED", "DROP"]                   # PLACE_SHED = PLACE into the shed
LETTER = {"WHEAT": "w", "CARROT": "c", "TOMATO": "t", "STRAWBERRY": "s", "MELON": "m",
          "COW": "C", "SHEEP": "S", "GOOSE": "G"}


# ---------------------------------------------------------------------------------------------------- cache access
def list_games():
    """Sorted list of cache paths (by episode id)."""
    names = [n for n in os.listdir(CACHE) if n.endswith(".pkl.gz")]
    key = lambda n: (0, int(n[:-7])) if n[:-7].isdigit() else (1, n)
    return [os.path.join(CACHE, n) for n in sorted(names, key=key)]


def load_game(path_or_id=None):
    """Game dict from a full path, a cache file name or an episode id (int or str). None = first cached game."""
    if path_or_id is None:
        path = list_games()[0]
    else:
        s = str(path_or_id)
        if os.path.isfile(s):
            path = s
        else:
            base = os.path.basename(s)
            path = os.path.join(CACHE, base if base.endswith(".pkl.gz") else base + ".pkl.gz")
    with gzip.open(path, "rb") as f:
        return pickle.load(f)


# ---------------------------------------------------------------------------------------------------- tile codes
def tcode(t):
    """Engine tile -> cache code (identical to research\\dsm_plan\\replay.py tcode)."""
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


def untcode(c):
    """Cache code -> the exact engine tile object (same keys, key order and value types as _new_plant/_new_animal)."""
    if c is None:
        return None
    if c == "L":
        return "LOCKED"
    tag = c[0]
    if tag == "W":
        return {"kind": "WEED"}
    if tag == "S":
        return {"kind": c[1]}
    if tag == "P":
        _, crop, planted_day, yield_units, fert_until, watered, unwatered, max_life = c
        return {"kind": "PLANT", "crop": crop, "planted_day": planted_day, "watered_today": watered,
                "consecutive_unwatered": unwatered, "yield_units": yield_units, "max_lifespan_step": max_life,
                "fertilized_until_day": fert_until}
    if tag == "A":
        _, kind, animal, placed_day, yield_units, fed, cared, fert_avail, care_bonus, unfed = c
        return {"kind": kind, "animal": animal, "placed_day": placed_day, "yield_units": yield_units,
                "consecutive_unfed": unfed, "fed_today": fed, "cared_today": cared,
                "fertilizer_available": fert_avail, "pending_care_bonus": care_bonus}
    raise ValueError(f"unknown tile code {c!r}")


def untcode_grid(grid):
    return [[untcode(c) for c in row] for row in grid]


def _initial_tiles():
    return [[None if (x < BOARD // 2 and y < BOARD // 2) else "LOCKED" for x in range(BOARD)] for y in range(BOARD)]


def _full_shed(sparse):
    shed = {item: 0 for item in PRODUCTS + ANIMALS}
    shed.update(sparse)
    return shed


def _full_seeds(sparse):
    seeds = {crop: 0 for crop in CROPS}
    seeds.update(sparse)
    return seeds


def _is_animal(c):
    return isinstance(c, tuple) and c[0] == "A"


def _span(g, d):
    """(t0, t1): the steps of day d that exist in the cache (day 29 stops at 718)."""
    if not 0 <= d <= LAST_DAY:
        raise ValueError(f"day {d} is outside 0..{LAST_DAY}")
    t0 = TPD * d
    return t0, min(t0 + TPD, len(g["steps"]))


def _units_of_day(g, d):
    t0 = TPD * d
    U = g["units"]
    return U[bisect.bisect_left(U, t0, key=lambda u: u[0]):bisect.bisect_left(U, t0 + TPD, key=lambda u: u[0])]


# ---------------------------------------------------------------------------------------------------- day views
def day_state(g, d):
    """Start of day d (d = 0 gives the initial farm).
    -> {day, t0, tiles (10x10 engine tiles, fresh objects), quads, shops, money, omoney, shed, seeds (full engine
        dicts incl. zeros), prices, minv, nshops, pos [farmer, hand1, ...], hires_today}"""
    t0, _ = _span(g, d)
    s = g["steps"][t0]
    if d == 0:
        tiles, quads, shops = _initial_tiles(), ["NW"], []
    else:
        e = g["eod"][d - 1]
        tiles, quads, shops = untcode_grid(e["tiles"][0]), list(e["quads"]), list(e["shops"])
    return {"day": d, "t0": t0, "tiles": tiles, "quads": quads, "shops": shops,
            "money": s["money"], "omoney": s["omoney"], "shed": _full_shed(s["shed"]), "seeds": _full_seeds(s["seeds"]),
            "prices": dict(s["prices"]), "minv": dict(s["minv"]), "nshops": s["nshops"],
            "pos": [tuple(p) for p in s["pos"]], "hires_today": s["hires"]}


def make_farm_private(g, d):
    """(farm, private) dicts at the start of day d in the engine's shapes:
    farm = {money, tiles, farmer, hands, unlocked_quadrants, hires_today}, private = {shed, seeds, inventories}."""
    st = day_state(g, d)
    farm = {"money": float(st["money"]), "tiles": st["tiles"], "farmer": list(st["pos"][0]),
            "hands": [list(p) for p in st["pos"][1:]], "unlocked_quadrants": st["quads"],
            "hires_today": st["hires_today"]}
    private = {"shed": st["shed"], "seeds": st["seeds"], "inventories": [{} for _ in st["pos"]]}
    return farm, private


def day_units(g, d):
    """-> {steps: [(t, n_units, [(x, y) farmer, hand1, ...]) for every step of the day],
           hires: [(t, count)] (pid 0; a unit hired at step t first acts at t+1), hire_cost, max_units}"""
    t0, t1 = _span(g, d)
    steps = [(t, g["steps"][t]["nh"] + 1, [tuple(p) for p in g["steps"][t]["pos"]]) for t in range(t0, t1)]
    cnt, cost = collections.Counter(), 0.0
    for (t, pid, c) in g["hire"]:
        if pid == 0 and t0 <= t < t0 + TPD:
            cnt[t] += 1
            cost += c
    return {"steps": steps, "hires": sorted(cnt.items()), "hire_cost": cost,
            "max_units": max(n for _, n, _ in steps)}


def day_actions(g, d):
    """DSM's unit actions of day d.
    -> {actions:  [{t, idx, op, arg, n, pos, cls, kind, tb, ta, delta}] in engine order (step, then farmer, hands);
                  cls: move (in-board move) | pass | effective (tile code changed or inventory delta non-empty) |
                  noop (anything else, including off-board moves); kind (effective only): the tile op name, or
                  PICKUP / PLACE_SHED / DROP; tb/ta are cache codes of the tile the unit stood on. Actions are the
                  ones the engine applied: a PLANT dropped by the atomic seed check would show as PASS (none of
                  the 92 games has one)
        tile_ops: {(x, y): [(t, op, arg_or_None)]} effective tile ops in order; arg = crop for PLANT, animal for
                  PLACE (PLACE here only when an animal was placed on a structure)
        shed_ops: [{t, idx, op, item, n, pos, delta, eff}] every PICKUP / DROP / PLACE-into-shed attempt on an
                  access tile; op PICKUP | PLACE | DROP, n = requested count (None for DROP), delta = unit
                  inventory change (the shed changes by -delta, except DROP overflow beyond the capacity)}"""
    actions, tile_ops, shed_ops = [], collections.defaultdict(list), []
    for (t, idx, a, pos, tb, ta, delta) in _units_of_day(g, d):
        op = a[0] if isinstance(a, list) and a else None
        arg = a[1] if op is not None and len(a) >= 2 else None
        n = a[2] if op is not None and len(a) >= 3 else None
        pos = tuple(pos)
        kind = None
        if op in MOVES:
            dx, dy = MOVES[op]
            cls = "move" if 0 <= pos[0] + dx < BOARD and 0 <= pos[1] + dy < BOARD else "noop"
        elif op == "PASS":
            cls = "pass"
        elif tb != ta or delta:
            cls = "effective"
            if op == "PLACE":
                kind = "PLACE" if (_is_animal(ta) and tb != ta) else "PLACE_SHED"
            else:
                kind = op
        else:
            cls = "noop"
        actions.append({"t": t, "idx": idx, "op": op, "arg": arg, "n": n, "pos": pos, "cls": cls, "kind": kind,
                        "tb": tb, "ta": ta, "delta": dict(delta)})
        if kind in TILE_OPS:
            tile_ops[pos].append((t, kind, arg if kind in ("PLANT", "PLACE") else None))
        if pos in ACCESS_SET and (op in ("PICKUP", "DROP") or (op == "PLACE" and kind != "PLACE")):
            shed_ops.append({"t": t, "idx": idx, "op": op, "item": None if op == "DROP" else arg,
                             "n": None if op == "DROP" else (int(n) if n is not None else 1),
                             "pos": pos, "delta": dict(delta), "eff": bool(delta)})
    return {"actions": actions, "tile_ops": dict(tile_ops), "shed_ops": shed_ops}


def day_market(g, d):
    """DSM's executed market units of day d (pid 0).
    -> {seeds, animals, products (BUY_PRODUCT: WHEAT/FERTILIZER), sales: {item: {n, money, steps [(t, n)],
        units [(t, price)]}}, land [(t, quadrant, cost, money_before)], hire_cost, spent (incl. land and hires),
        revenue}"""
    t0 = TPD * d
    groups = {"BUY_SEED": {}, "BUY_ANIMAL": {}, "BUY_PRODUCT": {}, "SELL": {}}
    for (t, pid, op, item, price) in g["mkt"]:
        if pid != 0 or not t0 <= t < t0 + TPD:
            continue
        e = groups[op].setdefault(item, {"n": 0, "money": 0.0, "steps": [], "units": []})
        e["n"] += 1
        e["money"] += price
        e["units"].append((t, price))
        if e["steps"] and e["steps"][-1][0] == t:
            e["steps"][-1] = (t, e["steps"][-1][1] + 1)
        else:
            e["steps"].append((t, 1))
    land = [(t, q, cost, mb) for (t, pid, q, cost, mb) in g["land"] if pid == 0 and t0 <= t < t0 + TPD]
    hire_cost = sum(c for (t, pid, c) in g["hire"] if pid == 0 and t0 <= t < t0 + TPD)
    spent = sum(e["money"] for op in ("BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT") for e in groups[op].values())
    spent += sum(x[2] for x in land) + hire_cost
    return {"seeds": groups["BUY_SEED"], "animals": groups["BUY_ANIMAL"], "products": groups["BUY_PRODUCT"],
            "sales": groups["SELL"], "land": land, "hire_cost": hire_cost, "spent": spent,
            "revenue": sum(e["money"] for e in groups["SELL"].values())}


def day_stats(g, d, actions=None, units=None):
    """-> {day, unit_turns (sum of units present), recorded, move, pass, effective, noop, idle (present units without
           a recorded action), eff_by_op {op: n} (tile ops + PICKUP/PLACE_SHED/DROP), noop_by_op {op: n},
           planted {crop: n}, release {crop: step}, hires, max_units}
    release: 24d if DSM held a seed of the crop at step 24d, else the step after its first BUY_SEED of the crop that
    day; crops without either are absent."""
    ac = actions or day_actions(g, d)
    un = units or day_units(g, d)
    t0 = TPD * d
    unit_turns = sum(n for _, n, _ in un["steps"])
    mix = collections.Counter(a["cls"] for a in ac["actions"])
    eff = collections.Counter(a["kind"] for a in ac["actions"] if a["cls"] == "effective")
    noop = collections.Counter(a["op"] for a in ac["actions"] if a["cls"] == "noop")
    planted = collections.Counter(a["arg"] for a in ac["actions"] if a["kind"] == "PLANT")
    stock = g["steps"][t0]["seeds"]
    first_buy = {}
    for (t, pid, op, item, price) in g["mkt"]:
        if pid == 0 and op == "BUY_SEED" and t0 <= t < t0 + TPD and item not in first_buy:
            first_buy[item] = t
    release = {}
    for crop in CROPS:
        if stock.get(crop, 0) > 0:
            release[crop] = t0
        elif crop in first_buy:
            release[crop] = first_buy[crop] + 1
    return {"day": d, "unit_turns": unit_turns, "recorded": len(ac["actions"]), "move": mix["move"],
            "pass": mix["pass"], "effective": mix["effective"], "noop": mix["noop"],
            "idle": unit_turns - len(ac["actions"]), "eff_by_op": dict(eff), "noop_by_op": dict(noop),
            "planted": dict(planted), "release": release, "hires": sum(c for _, c in un["hires"]),
            "max_units": un["max_units"]}


def end_state(g, d):
    """Engine tiles after the end-of-day refresh of day d (= start of day d+1), from eod[d]; d <= 28."""
    if not 0 <= d < len(g["eod"]):
        raise ValueError(f"no end-of-day record for day {d} (the cache has days 0..{len(g['eod']) - 1})")
    return untcode_grid(g["eod"][d]["tiles"][0])


# ---------------------------------------------------------------------------------------------------- engine replay
class _OnlyKaggriculture(importlib.abc.MetaPathFinder):
    """`import kaggle_environments` loads every bundled env; let only kaggriculture load (as tools\\fastarena.py)."""

    def find_spec(self, name, path, target=None):
        p = name.split(".")
        if len(p) >= 3 and p[:2] == ["kaggle_environments", "envs"] and p[2] != "kaggriculture":
            raise ImportError(name)
        return None


_K = []


def engine():
    """The kaggriculture engine module (imported on first use)."""
    if not _K:
        if "kaggle_environments" not in sys.modules:
            finder = _OnlyKaggriculture()
            sys.meta_path.insert(0, finder)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    import kaggle_environments  # noqa: F401
            finally:
                sys.meta_path.remove(finder)
        from kaggle_environments.envs.kaggriculture import kaggriculture as K
        _K.append(K)
    return _K[0]


def check_engine():
    """Compare this module's constants and tile conversion with the engine. Returns a list of problems ([] = OK)."""
    K = engine()
    bad = []
    spec = {k: v.get("default") for k, v in K.specification["configuration"].items() if isinstance(v, dict)}
    for name, mine, ref in (("CROPS", CROPS, list(K.CROPS)), ("ANIMALS", ANIMALS, list(K.ANIMALS)),
                            ("PRODUCTS", PRODUCTS, list(K.PRODUCTS)), ("MOVES", MOVES, dict(K.FARMER_MOVES)),
                            ("ACCESS", ACCESS, [tuple(p) for p in K._shed_access_tiles(BOARD)]),
                            ("BOARD", BOARD, spec.get("boardSize")), ("TPD", TPD, spec.get("turnsPerDay")),
                            ("SHED_CAP", SHED_CAP, spec.get("shedCapacity")),
                            ("WEED_CHANCE", WEED_CHANCE, spec.get("weedSpawnChance")),
                            ("initial tiles", _initial_tiles(), K._new_farm(BOARD, 3000)["tiles"]),
                            ("shed keys", list(_full_shed({})), list(K._new_private()["shed"])),
                            ("seed keys", list(_full_seeds({})), list(K._new_private()["seeds"]))):
        if mine != ref:
            bad.append(f"{name}: dsmday {mine!r} != engine {ref!r}")
    samples = [K._new_plant(c, 5, TPD) for c in K.CROPS] + [K._new_animal(a, 5) for a in K.ANIMALS]
    for a in K.ANIMALS:                        # after a production-day refresh (pending_care_bonus popped, re-added)
        farm = {"tiles": [[None] * BOARD for _ in range(BOARD)]}
        tile = K._new_animal(a, 0)
        tile.update(fed_today=True, cared_today=True, pending_care_bonus=1)
        farm["tiles"][0][0] = tile
        K._daily_refresh_animals(farm, K.ANIMALS[a]["first_yield_day"] - 1)
        samples.append(farm["tiles"][0][0])
    samples += [{"kind": "WEED"}, {"kind": "COOP"}, {"kind": "PASTURE"}, None, "LOCKED"]
    for ref in samples:
        back = untcode(tcode(ref))
        if repr(back) != repr(ref):            # same keys, key order, values and value types
            bad.append(f"tile round trip: {ref!r} -> {back!r}")
    return bad


def _inv_delta(before, after):
    return {k: after.get(k, 0) - before.get(k, 0) for k in set(before) | set(after) if after.get(k, 0) != before.get(k, 0)}


def replay_day(g, d, check=True):
    """Re-apply DSM's recorded unit actions of day d (0..28) with the engine's own functions, starting from
    day_state(g, d). Per step t: shed, seeds, money and unit positions are reset from steps[t] (the market is not
    simulated), the units act in engine order (K._apply_unit_action), land bought at t is unlocked (K._do_buy_land),
    then K._decay_plants(farm, t); after step 24d+23 K._daily_refresh_plants and K._daily_refresh_animals run. Weeds
    are not spawned. With check=True every action is compared with its record (position, tile code before and after,
    inventory delta) and unit positions after each step with steps[t+1].
    -> (farm, private, info {actions, action_mismatches [(t, idx, action, what)], move_mismatches [t], land})"""
    K = engine()
    if not 0 <= d < len(g["eod"]):
        raise ValueError(f"replay_day needs an end-of-day step: day {d} is outside 0..{len(g['eod']) - 1}")
    farm, private = make_farm_private(g, d)
    t0 = TPD * d
    by_t = collections.defaultdict(list)
    for u in _units_of_day(g, d):
        by_t[u[0]].append(u)
    land = collections.defaultdict(list)
    for (t, pid, q, cost, mb) in g["land"]:
        if pid == 0 and t0 <= t < t0 + TPD:
            land[t].append((q, cost, mb))
    info = {"actions": 0, "action_mismatches": [], "move_mismatches": [], "land": []}
    for t in range(t0, t0 + TPD):
        s = g["steps"][t]
        private["shed"] = _full_shed(s["shed"])
        private["seeds"] = _full_seeds(s["seeds"])
        farm["money"] = float(s["money"])
        farm["hires_today"] = s["hires"]
        farm["farmer"] = list(s["pos"][0])
        farm["hands"] = [list(p) for p in s["pos"][1:]]
        for (_, idx, a, pos, tb, ta, delta) in by_t.get(t, []):
            x, y = pos
            if check:
                where = tuple(K._farmer_position(farm, idx))
                before = tcode(farm["tiles"][y][x])
                inv0 = dict(K._farmer_inventory(private, idx))
            K._apply_unit_action(farm, private, idx, a, BOARD, d, TPD, SHED_CAP)
            if check:
                info["actions"] += 1
                what = []
                if where != tuple(pos):
                    what.append(f"pos {where} != {pos}")
                if repr(before) != repr(tb):
                    what.append(f"before {before} != {tb}")
                after = tcode(farm["tiles"][y][x])
                if repr(after) != repr(ta):
                    what.append(f"after {after} != {ta}")
                dl = _inv_delta(inv0, K._farmer_inventory(private, idx))
                if dl != delta:
                    what.append(f"delta {dl} != {delta}")
                if what:
                    info["action_mismatches"].append((t, idx, a, "; ".join(what)))
        for (q, cost, mb) in land.get(t, []):
            farm["money"] = mb
            K._do_buy_land(farm, BOARD)
            info["land"].append((t, q, farm["unlocked_quadrants"][-1] == q))
        if check and t + 1 < t0 + TPD:
            now = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
            if now != [tuple(p) for p in g["steps"][t + 1]["pos"][:len(now)]]:
                info["move_mismatches"].append(t)
        K._decay_plants(farm, t)
    K._daily_refresh_plants(farm, d, TPD)
    K._daily_refresh_animals(farm, d)
    return farm, private, info


def _weed_rng(g, d):
    """random.Random positioned at DSM's first weed draw at the end of day d, and whether that position is ambiguous.
    The engine uses Random((seed * 1_000_003) ^ day) and draws once per empty tile, player 0's farm first; when DSM is
    player 1 the opponent's pre-spawn empty-tile count is recovered from its post-spawn grid (ambiguous only if the
    next draw would also have spawned a weed)."""
    rng = random.Random((g["seed"] * 1_000_003) ^ d)
    if g["side"] == 0:
        return rng, False
    empty_after = sum(c is None for row in g["eod"][d]["tiles"][1] for c in row)
    n = hits = 0
    while n - hits < empty_after:
        n += 1
        hits += rng.random() < WEED_CHANCE
    state = rng.getstate()
    ambiguous = rng.random() < WEED_CHANCE
    rng.setstate(state)
    return rng, ambiguous


def validate_day(g, d):
    """replay_day(g, d) vs end_state(g, d). Tiles are compared strictly (repr: keys, key order, values, types).
    Tiles that are empty in the replay and WEED in the record (weeds spawned by the end-of-day RNG) are ignored.
    Also reports the result with the engine's weed RNG applied (K._spawn_weeds), which should match everything.
    -> {game, side, day, actions, action_mismatches, move_mismatches, land_mismatches, compared, equal, rng_weeds,
        tile_mismatches [(x, y, replay_code, record_code)], rng_equal (of 100), rng_ambiguous}"""
    K = engine()
    farm, private, info = replay_day(g, d)
    ref = end_state(g, d)
    equal = ignored = 0
    bad = []
    for y in range(BOARD):
        for x in range(BOARD):
            a, b = farm["tiles"][y][x], ref[y][x]
            if repr(a) == repr(b):
                equal += 1
            elif a is None and b == {"kind": "WEED"}:
                ignored += 1
            else:
                bad.append((x, y, tcode(a), tcode(b)))
    tiles = copy.deepcopy(farm["tiles"])
    rng, ambiguous = _weed_rng(g, d)
    K._spawn_weeds({"tiles": tiles}, BOARD, WEED_CHANCE, rng)
    rng_equal = sum(repr(tiles[y][x]) == repr(ref[y][x]) for y in range(BOARD) for x in range(BOARD))
    return {"game": g["id"], "side": g["side"], "day": d, "actions": info["actions"],
            "action_mismatches": info["action_mismatches"], "move_mismatches": info["move_mismatches"],
            "land_mismatches": [x for x in info["land"] if not x[2]],
            "compared": BOARD * BOARD - ignored, "equal": equal, "rng_weeds": ignored, "tile_mismatches": bad,
            "rng_equal": rng_equal, "rng_ambiguous": ambiguous}


# ---------------------------------------------------------------------------------------------------- text output
def letter(tile):
    """w wheat, c carrot, t tomato, s strawberry, m melon, C cow, S sheep, G goose, o empty coop, p empty pasture,
    x weed, . empty, # locked."""
    if tile is None:
        return "."
    if tile == "LOCKED":
        return "#"
    kind = tile.get("kind")
    if kind == "WEED":
        return "x"
    if kind == "PLANT":
        return LETTER[tile["crop"]]
    if "animal" in tile:
        return LETTER[tile["animal"]]
    return {"COOP": "o", "PASTURE": "p"}.get(kind, "?")


def render_map(tiles):
    """Rows of letters with x (column) and y (row) labels."""
    return ["   " + " ".join(str(x) for x in range(BOARD))] + \
           [f"{y:2d} " + " ".join(letter(t) for t in row) for y, row in enumerate(tiles)]


def _tile_counts(tiles):
    c = collections.Counter(letter(t) for row in tiles for t in row)
    return " ".join(f"{k}{c[k]}" for k in "wctsmCSGopx.#" if c[k])


def _kv(d, order=None):
    items = [(k, v) for k, v in d.items() if v]
    if order:
        rank = {k: i for i, k in enumerate(order)}
        items.sort(key=lambda kv: (rank.get(kv[0], len(rank)), str(kv[0])))
    else:
        items.sort(key=lambda kv: (-kv[1], str(kv[0])))
    return ", ".join(f"{k} {v}" for k, v in items) or "-"


def _tn(pairs):
    return " ".join(f"{t}:{n}" if n != 1 else f"{t}" for t, n in pairs) or "-"


def _runs(steps):
    out, start, prev, cur = [], None, None, None
    for t, n, _ in steps + [(None, None, None)]:
        if n != cur:
            if cur is not None:
                out.append(f"{start}-{prev}:{cur}" if prev != start else f"{start}:{cur}")
            start, cur = t, n
        prev = t
    return " ".join(out)


def _pct(a, b):
    return f"{100.0 * a / b:.0f}%" if b else "-"


def summary(g, d, show_tiles=False):
    st = day_state(g, d)
    un = day_units(g, d)
    ac = day_actions(g, d)
    mk = day_market(g, d)
    ss = day_stats(g, d, actions=ac, units=un)
    t0, t1 = _span(g, d)
    L = [f"game {g['id']}: DSM side {g['side']} vs {g['opp']}, final {g['final'][0]:.0f} : {g['final'][1]:.0f}",
         f"day {d} = steps {t0}..{t1 - 1} | money {st['money']:.0f} (opp {st['omoney']:.0f}) | quads "
         f"{' '.join(st['quads'])} | shops {' '.join(st['shops']) or '-'}",
         f"start shed : {_kv(st['shed'], PRODUCTS + ANIMALS)}",
         f"start seeds: {_kv(st['seeds'], CROPS)}",
         f"units      : {_runs(un['steps'])} (max {un['max_units']}) | hires {ss['hires']} at {_tn(un['hires'])}, "
         f"cost {un['hire_cost']:.0f}"]
    tot = ss["unit_turns"]
    L.append(f"unit-turns : {tot} = " + ", ".join(f"{k} {ss[k]} ({_pct(ss[k], tot)})"
                                                  for k in ("move", "pass", "effective", "noop"))
             + (f", idle {ss['idle']}" if ss["idle"] else ""))
    L.append(f"effective  : {_kv(ss['eff_by_op'], TILE_OPS + SHED_OPS)}")
    L.append(f"noops      : {_kv(ss['noop_by_op'])}")
    L.append(f"planted    : {_kv(ss['planted'], CROPS)} | release step: "
             + (" ".join(f"{c} {t}" for c, t in ss["release"].items()) or "-"))
    for label, key in (("seeds buy  ", "seeds"), ("animals buy", "animals"), ("product buy", "products"),
                       ("sold       ", "sales")):
        if mk[key]:
            L.append(f"{label}: " + "; ".join(f"{it} {e['n']} for {e['money']:.0f} [{_tn(e['steps'])}]"
                                              for it, e in mk[key].items()))
    if mk["land"]:
        L.append("land       : " + "; ".join(f"{q} at {t} for {c:.0f}" for (t, q, c, mb) in mk["land"]))
    L.append(f"money flow : spent {mk['spent']:.0f} (hires {mk['hire_cost']:.0f}), sales {mk['revenue']:.0f}")
    sums, nops = collections.defaultdict(collections.Counter), collections.Counter()
    for s in ac["shed_ops"]:
        if s["eff"]:
            name = "PLACE_SHED" if s["op"] == "PLACE" else s["op"]
            nops[name] += 1
            sums[name].update(s["delta"])
    L.append("shed ops   : " + ("; ".join(f"{op} x{nops[op]} (" + ", ".join(f"{k} {v:+d}" for k, v in
                                                                         sorted(sums[op].items())) + ")"
                                          for op in SHED_OPS if nops[op]) or "-")
             + f" | failed attempts {sum(1 for s in ac['shed_ops'] if not s['eff'])}")
    L.append(f"tile ops   : {sum(len(v) for v in ac['tile_ops'].values())} effective on {len(ac['tile_ops'])} tiles")
    start = render_map(st["tiles"])
    head = f"start of day {d}"
    if d < len(g["eod"]):
        end_tiles = end_state(g, d)
        end = render_map(end_tiles)
        L.append(f"   {head:<25}  end of day {d} (after refresh)")
        L += [f"   {a:<25}  {b}" for a, b in zip(start, end)]
        L.append(f"   start {_tile_counts(st['tiles'])} | end {_tile_counts(end_tiles)}")
    else:
        L.append(f"   {head} (no end-of-day record for day {d})")
        L += [f"   {a}" for a in start]
        L.append(f"   start {_tile_counts(st['tiles'])}")
    if show_tiles:
        L.append("effective tile ops per tile (step op [arg]):")
        for (x, y) in sorted(ac["tile_ops"], key=lambda p: (p[1], p[0])):
            L.append(f"  ({x},{y}) " + ", ".join(f"{t} {op.lower()}" + (f" {arg.lower()}" if arg else "")
                                                for t, op, arg in ac["tile_ops"][(x, y)]))
    return "\n".join(L)


def _validate_cli(paths, days):
    problems = check_engine()
    print("engine check: " + ("constants and tile key sets/order match the engine" if not problems else
                              "PROBLEMS\n  " + "\n  ".join(problems)))
    T = collections.Counter()
    for path in paths:
        g = load_game(path)
        for d in days:
            if d >= len(g["eod"]):
                continue
            r = validate_day(g, d)
            T["days"] += 1
            T["actions"] += r["actions"]
            T["action_bad"] += len(r["action_mismatches"])
            T["move_bad"] += len(r["move_mismatches"])
            T["compared"] += r["compared"]
            T["equal"] += r["equal"]
            T["weeds"] += r["rng_weeds"]
            T["rng_equal"] += r["rng_equal"]
            T["ambiguous"] += r["rng_ambiguous"]
            T["land_bad"] += len(r["land_mismatches"])
            ok = not (r["action_mismatches"] or r["move_mismatches"] or r["tile_mismatches"] or r["land_mismatches"])
            if len(paths) * len(days) <= 30 or not ok:
                print(f"game {r['game']} side {r['side']} day {d:2d}: unit actions {r['actions']} "
                      f"(mismatch {len(r['action_mismatches'])}), move steps mismatch {len(r['move_mismatches'])}, "
                      f"tiles {r['equal']}/{r['compared']} equal + {r['rng_weeds']} RNG weeds ignored; "
                      f"with weed RNG {r['rng_equal']}/100" + (" (ambiguous)" if r["rng_ambiguous"] else "")
                      + (f"; LAND MISMATCH {r['land_mismatches']}" if r["land_mismatches"] else ""))
            for m in r["action_mismatches"][:5]:
                print("   action", m)
            for m in r["tile_mismatches"][:5]:
                print("   tile", m)
    print(f"total: {T['days']} game-days, unit actions {T['actions'] - T['action_bad']}/{T['actions']} exact, "
          f"move mismatches {T['move_bad']}, land mismatches {T['land_bad']}, tiles {T['equal']}/{T['compared']} equal "
          f"({_pct(T['equal'], T['compared'])}) with {T['weeds']} RNG weeds ignored; "
          f"with the weed RNG {T['rng_equal']}/{100 * T['days']} ({_pct(T['rng_equal'], 100 * T['days'])})"
          + (f", {T['ambiguous']} ambiguous RNG days" if T["ambiguous"] else ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Summarise or validate one DSM day from research\\dsm_plan\\cache.")
    ap.add_argument("--game", help="episode id or cache path (default: first cached game)")
    ap.add_argument("--day", type=int, help="day 0..29")
    ap.add_argument("--tiles", action="store_true", help="also list the effective tile ops per tile")
    ap.add_argument("--validate", action="store_true", help="replay days with the engine and compare with eod")
    ap.add_argument("--games", type=int, default=3, help="--validate: number of games spread over the cache")
    ap.add_argument("--days", default="10,15,20", help="--validate: comma-separated days")
    ap.add_argument("--all", action="store_true", help="--validate: every cached game, days 0..28")
    args = ap.parse_args(argv)
    if args.validate:
        paths = list_games()
        if args.game:
            paths = [args.game]
        elif not args.all:
            k = max(1, min(args.games, len(paths)))
            paths = [paths[i * (len(paths) - 1) // (k - 1)] for i in range(k)] if k > 1 else paths[:1]
        days = list(range(LAST_DAY)) if args.all else [int(x) for x in args.days.split(",") if x.strip()]
        _validate_cli(paths, days)
        return
    if args.day is None:
        ap.error("--day is required (or use --validate)")
    print(summary(load_game(args.game), args.day, show_tiles=args.tiles))


if __name__ == "__main__":
    main()
