"""Production agent P1 (team 42 research, 2026-09-26).

Design: one visit per tile per day doing every needed action; units follow sweep-partitioned routes
around the central shed; allocation targets set from the town shops; sells on arrival.
"""
import math

# ----------------------------------------------------------------------------- game data
CROPS = {
    "WHEAT": {"seed": 10, "first": 2, "maxday": 4, "ongoing": False, "maxy": 6},
    "CARROT": {"seed": 20, "first": 2, "maxday": 3, "ongoing": False, "maxy": 4},
    "TOMATO": {"seed": 50, "first": 8, "maxday": 8, "ongoing": True, "maxy": 4, "interval": 1},
    "STRAWBERRY": {"seed": 100, "first": 10, "maxday": 10, "ongoing": True, "maxy": 4, "interval": 2},
    "MELON": {"seed": 80, "first": 10, "maxday": 12, "ongoing": False, "maxy": 6},
}
ANIMALS = {
    "GOOSE": {"cost": 300, "struct": "COOP", "first": 4, "interval": 1, "maxheld": 4, "product": "EGG"},
    "COW": {"cost": 400, "struct": "PASTURE", "first": 8, "interval": 2, "maxheld": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "struct": "PASTURE", "first": 6, "interval": 3, "maxheld": 6, "product": "WOOL"},
}
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
BASE = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250, "EGG": 50, "MILK": 160,
        "WOOL": 200, "FERTILIZER": 100}
MP = {
    "WHEAT": (25, 400, "sqrt", 0.80, "log", 0.20),
    "CARROT": (35, 450, "hinge", 1.00, "sqrt", 0.70),
    "TOMATO": (60, 200, "hinge", 0.40, "sqrt", 0.60),
    "STRAWBERRY": (120, 100, "sqrt", 0.70, "linear", 1.60),
    "MELON": (250, 300, "log", 0.20, "sq", 3.60),
    "EGG": (50, 332, "hinge", 0.40, "log", 0.20),
    "MILK": (160, 122, "sqrt", 0.60, "linear", 1.60),
    "WOOL": (200, 105, "log", 0.20, "sq", 3.20),
    "FERTILIZER": (100, 200, "linear", 0.40, "linear", 0.40),
}
SHOPS = {
    "BAKERY": ["EGG", "WHEAT"], "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"], "YARN_STORE": ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"], "PET_CAFE": ["CARROT"],
    "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"], "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}
SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]
LAND_ORDER = ["NE", "SW", "SE"]
LAND_PRICES = [1000, 2000, 4000]
MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
LAST_STEP = 718


def _shape(f, x, T):
    x = max(0.0, x)
    if f == "linear":
        return x
    if f == "sq":
        return x * x
    if f == "sqrt":
        return math.sqrt(x)
    if f == "log":
        return math.log(1.0 + x)
    if f == "hinge":
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def price(item, inv):
    base, T, bf, bt, af, at = MP[item]
    if inv < 10000:
        p = base + bt * base / _shape(bf, T, T) * _shape(bf, 10000 - inv, T)
    else:
        p = base - at * base / _shape(af, T, T) * _shape(af, inv - 10000, T)
    return max(1, int(round(p)))


def fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def quad(x, y):
    return ("N" if y < 5 else "S") + ("W" if x < 5 else "E")


def dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def shed_dist(p):
    return min(dist(p, s) for s in SHED_TILES)


def g(o, k, d=None):
    if isinstance(o, dict):
        return o.get(k, d)
    return getattr(o, k, d)


# ----------------------------------------------------------------------------- config
CFG = {
    "melons_d0": 12,
    "cows_d0": 2,
    "sheep_d0": 2,
    "hands_early": 4,
    "max_hands": 12,
    "land_days": (6, 9, 10),
    "animal_total": 23,
    "straw_last_plant": 13,
    "tomato_last_plant": 18,
}

# ----------------------------------------------------------------------------- state
STATE = {}


def new_state():
    return {"routes": {}, "plan_hour": -1, "day": -1, "alloc": {}, "want_hands": 0, "buy_animals": [],
            "pickups": {}, "log": [], "last_step": -1, "melon_race": False, "stats": {}}


# ----------------------------------------------------------------------------- view
class View:
    def __init__(self, obs):
        self.me = g(obs, "player", 0)
        self.step = g(obs, "step", 0) or 0
        self.day = g(obs, "day", self.step // 24)
        self.hour = g(obs, "hour", self.step % 24)
        farms = g(obs, "farms")
        self.farm = farms[self.me]
        self.opp = farms[1 - self.me]
        self.tiles = self.farm["tiles"] if isinstance(self.farm, dict) else g(self.farm, "tiles")
        self.money = float(g(self.farm, "money", 0))
        self.quads = list(g(self.farm, "unlocked_quadrants", ["NW"]))
        self.hires_today = int(g(self.farm, "hires_today", 0))
        self.units = [tuple(g(self.farm, "farmer"))] + [tuple(h) for h in (g(self.farm, "hands", []) or [])]
        priv = g(obs, "private", {})
        self.shed = dict(g(priv, "shed", {}) or {})
        self.seeds = dict(g(priv, "seeds", {}) or {})
        invs = list(g(priv, "inventories", [{}]) or [{}])
        self.invs = [dict(i or {}) for i in invs]
        while len(self.invs) < len(self.units):
            self.invs.append({})
        m = g(obs, "market", {})
        self.minv = dict(g(m, "inventory", {}) or {})
        self.prices = dict(g(m, "prices", {}) or {})
        self.shops = list(g(g(obs, "town", {}), "unlocked_shops", []) or [])

    def tile(self, p):
        return self.tiles[p[1]][p[0]]

    def owned(self, p):
        return self.tiles[p[1]][p[0]] != "LOCKED"

    def shed_total(self):
        return sum(v for v in self.shed.values())


# ----------------------------------------------------------------------------- crop logic
# ages at which we want to water / fertilize / harvest (planned visits)
WATER_AGES = {
    "WHEAT": {0, 2, 3},
    "CARROT": {0, 2},
    "TOMATO": {0, 2, 4, 6, 7, 8, 9, 10},
    "STRAWBERRY": {0, 2, 4, 6, 8, 9, 11, 13, 15},
    "MELON": {0, 2, 4, 6, 7, 8, 9, 10},
}
FERT_AGES = {"WHEAT": {2}, "CARROT": {2}, "TOMATO": {7, 10}, "STRAWBERRY": {9, 13}, "MELON": set()}


def crop_final_age(crop):
    return {"TOMATO": 11, "STRAWBERRY": 16}.get(crop)


def wants_fert(crop, age, day, S, V):
    """Is fertilizing this crop today worth it (vs selling the fertilizer)?"""
    if age not in FERT_AGES[crop]:
        return False
    fp = V.prices.get("FERTILIZER", 100)
    if crop in ("TOMATO", "STRAWBERRY"):
        return True
    if crop == "WHEAT":
        return fp <= S["cfg"].get("fert_wheat_max", 45) and day <= 26
    if crop == "CARROT":
        return fp <= S["cfg"].get("fert_carrot_max", 45)
    return False


def plant_ops(tile, day, S, V, inv, planning=False):
    """Ops wanted now on a plant tile (in order) and whether the visit is mandatory today.
    inv = unit inventory (None when planning: assume supplies are available)."""
    crop = tile["crop"]
    cd = CROPS[crop]
    p0 = tile["planted_day"]
    age = day - p0
    y = tile.get("yield_units", 0)
    w = tile.get("watered_today", False)
    fu = tile.get("fertilized_until_day", -1)
    cu = tile.get("consecutive_unwatered", 0)
    have_fert = planning or (inv is not None and inv.get("FERTILIZER", 0) > 0)
    ops = []
    if crop in ("WHEAT", "CARROT"):
        if age >= 2:
            fert_ok = (age == 2 and fu < day and not w and have_fert and wants_fert(crop, age, day, S, V))
            if crop == "WHEAT" and age == 2 and (fert_ok or fu >= day):
                if fert_ok:
                    ops.append("FERTILIZE")
                if not w:
                    ops.append("WATER")
                return ops, True
            if fert_ok:
                ops.append("FERTILIZE")
            if not w and age <= cd["maxday"]:
                ops.append("WATER")
            ops.append("HARVEST")
            return ops, True
        if not w and (age == 0 or cu >= 1):
            ops.append("WATER")
        return ops, (age == 0 or cu >= 1)
    if crop == "MELON":
        if age >= 10:
            if not w and age <= 12 and y < 6:
                ops.append("WATER")
            ops.append("HARVEST")
            return ops, True
        if not w and (age in WATER_AGES[crop] or cu >= 1):
            ops.append("WATER")
        return ops, (cu >= 1 or age == 0 or age >= 6)
    # ongoing crops
    final = crop_final_age(crop)
    if age >= final:
        if y > 0:
            ops.append("HARVEST")
        ops.append("DIG")
        return ops, True
    if age in FERT_AGES[crop] and fu < day and have_fert and wants_fert(crop, age, day, S, V):
        ops.append("FERTILIZE")
    if y >= 3 and age >= cd["first"]:
        ops.append("HARVEST")
    if not w and (age in WATER_AGES[crop] or cu >= 1):
        ops.append("WATER")
    return ops, (cu >= 1 or age == 0)


def animal_ops(tile, day, S, V, inv, planning=False):
    ops = []
    kind = tile["animal"]
    a = ANIMALS[kind]
    if tile.get("yield_units", 0) > 0:
        ops.append("HARVEST")
    fed = tile.get("fed_today", False)
    stop_feed = S["cfg"].get("stop_feed", {}).get(kind, 28)
    if not fed and day <= stop_feed and (planning or inv.get("WHEAT", 0) > 0):
        ops.append("FEED")
    if not tile.get("cared_today", False) and (fed or "FEED" in ops):
        ops.append("CARE")
    if tile.get("fertilizer_available", False):
        ops.append("COLLECT_FERTILIZER")
    return ops, tile.get("consecutive_unfed", 0) >= 1



# ============================================================================= allocation
def shop_counts(shops, k=None):
    c = {}
    for s in (shops if k is None else shops[:k]):
        c[s] = c.get(s, 0) + 1
    return c


def targets(V, S):
    """Target tile counts for animals and main crops (DSM-like fits)."""
    cfg = S["cfg"]
    shops = V.shops
    c4 = shop_counts(shops, 4)
    call = shop_counts(shops)
    straw_x = sum(c4.get(s, 0) for s in ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET"))
    tom_x = sum(c4.get(s, 0) for s in ("PIZZA_SHOP", "FARMERS_MARKET"))
    car_x = 2 * call.get("PET_CAFE", 0) + call.get("FARMERS_MARKET", 0)
    inc_sheep = {3: 8, 6: 7, 9: 7, 12: 4, 15: 2}
    inc_cow = {3: 4, 6: 4, 9: 2, 12: 1}
    inc_goose = {3: 4, 6: 3, 9: 2}
    sheep, cows, geese = cfg["sheep_base"], cfg["cow_base"], 0
    for k, s in enumerate(shops):
        u = 3 * (k + 1)
        if s == "YARN_STORE":
            sheep += inc_sheep.get(u, 0)
        if s in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"):
            cows += inc_cow.get(u, 0)
        if s in ("BAKERY", "BRUNCH_SPOT"):
            geese += inc_goose.get(u, 0)
    geese = max(geese, cfg["animal_total"] - sheep - cows)
    return {"SHEEP": sheep, "COW": cows, "GOOSE": geese,
            "STRAWBERRY": cfg["straw_a"] + cfg["straw_b"] * straw_x,
            "TOMATO": cfg["tom_a"] + cfg["tom_b"] * tom_x,
            "CARROT": cfg["car_a"] + cfg["car_b"] * car_x}


def count_uses(V):
    c = {}
    for y in range(10):
        for x in range(10):
            t = V.tiles[y][x]
            if isinstance(t, dict):
                k = t.get("animal") or t.get("crop") or t.get("kind")
                c[k] = c.get(k, 0) + 1
    return c


def animal_slots(V):
    out = []
    for y in range(10):
        for x in range(10):
            if V.owned((x, y)):
                out.append((shed_dist((x, y)), abs(x - 4.5) + abs(y - 4.5), (x, y)))
    out.sort()
    return [p for _, _, p in out]


def freeing_today(t, day, S, V):
    """True if the plant on tile t is harvested (one-time) or dug (ongoing final) today."""
    ops, _ = plant_ops(t, day, S, V, None, planning=True)
    return ("HARVEST" in ops and not CROPS[t["crop"]]["ongoing"]) or "DIG" in ops


def crop_ok_to_plant(crop, day):
    last = {"WHEAT": 26, "CARROT": 27, "TOMATO": 20, "STRAWBERRY": 17, "MELON": 1}
    return day <= last[crop]


def choose_crop(V, S, p, work, tg):
    day = V.day
    cfg = S["cfg"]
    if day >= 28:
        return None
    if day <= 1:
        return cfg["opening"].get(p)
    if day < 6:
        if 2 <= day <= 4 and work.get("STRAWBERRY", 0) < cfg["straw_early"]:
            return "STRAWBERRY"
        return "WHEAT"
    if day <= cfg["straw_last"] and work.get("STRAWBERRY", 0) < tg["STRAWBERRY"]:
        return "STRAWBERRY"
    if cfg["tom_first"] <= day <= cfg["tom_last"] and work.get("TOMATO", 0) < tg["TOMATO"]:
        return "TOMATO"
    if day >= cfg["car_first"] and work.get("CARROT", 0) < tg["CARROT"] * (0.35 if day < 19 else 1.0):
        return "CARROT"
    if day <= 26:
        return "WHEAT"
    if day <= 27:
        return "CARROT"
    return None


def decide_uses(V, S, animal_budget):
    """tile_use: pos -> crop or animal kind for free / freeing-today tiles."""
    tu = {}
    day = V.day
    cnt = count_uses(V)
    tg = targets(V, S) if day >= 6 else {"SHEEP": S["cfg"]["sheep_d0"], "COW": S["cfg"]["cows_d0"], "GOOSE": 0,
                                         "STRAWBERRY": 0, "TOMATO": 0, "CARROT": 0}
    S["tg"] = tg
    # animals
    carried = {}
    for inv in V.invs:
        for k in ANIMALS:
            carried[k] = carried.get(k, 0) + inv.get(k, 0)
    want = []
    if day <= S["cfg"]["animal_last_day"] or any(V.shed.get(k, 0) + carried.get(k, 0) for k in ANIMALS):
        for k in S["cfg"]["animal_order"]:
            have = cnt.get(k, 0)
            spare = V.shed.get(k, 0) + carried.get(k, 0)
            n = max(0, int(round(tg[k])) - have) if day <= S["cfg"]["animal_last_day"] else 0
            n = max(n, spare)
            for _ in range(n):
                want.append((k, spare > 0))
                spare -= 1
    budget = animal_budget
    slots = animal_slots(V)
    si = 0
    for k, owned in want:
        if not owned:
            if budget < ANIMALS[k]["cost"]:
                continue
        while si < len(slots):
            p = slots[si]
            si += 1
            if shed_dist(p) > S["cfg"]["animal_max_dist"]:
                si = len(slots)
                break
            t = V.tile(p)
            ok = t is None or (isinstance(t, dict) and t.get("kind") in ("WEED",)) or \
                (isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and not t.get("animal"))
            if isinstance(t, dict) and t.get("kind") == "PLANT" and day >= 6 and freeing_today(t, day, S, V):
                ok = True
            if ok:
                tu[p] = k
                if not owned:
                    budget -= ANIMALS[k]["cost"]
                break
    # crops
    work = dict(cnt)
    for y in range(10):
        for x in range(10):
            p = (x, y)
            if not V.owned(p) or p in tu:
                continue
            t = V.tiles[y][x]
            freeing = isinstance(t, dict) and t.get("kind") == "PLANT" and freeing_today(t, day, S, V)
            if freeing:
                work[t["crop"]] = work.get(t["crop"], 0) - 1
            if t is None or (isinstance(t, dict) and t.get("kind") == "WEED") or freeing or \
                    (isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and not t.get("animal")):
                c = choose_crop(V, S, p, work, tg)
                if c and crop_ok_to_plant(c, day):
                    tu[p] = c
                    work[c] = work.get(c, 0) + 1
    S["tile_use"] = tu


# ============================================================================= jobs
def gen_jobs(V, S):
    jobs = []
    day = V.day
    tu = S["tile_use"]
    for y in range(10):
        for x in range(10):
            p = (x, y)
            t = V.tiles[y][x]
            if t == "LOCKED":
                continue
            use = tu.get(p)
            j = None
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                ops, mand = plant_ops(t, day, S, V, None, planning=True)
                if ops:
                    j = {"pos": p, "ops": list(ops), "mand": mand, "kind": "crop", "crop": t["crop"]}
                    if ("HARVEST" in ops and not CROPS[t["crop"]]["ongoing"]) or "DIG" in ops:
                        if use in CROPS:
                            j["ops"] += ["PLANT", "WATER"]
                            j["plant"] = use
                        elif use in ANIMALS:
                            if "DIG" not in j["ops"] and CROPS[t["crop"]]["ongoing"]:
                                j["ops"].append("DIG")
                            j["ops"] += ["BUILD", "PLACE"]
                            j["place"] = use
            elif isinstance(t, dict) and t.get("animal"):
                ops, mand = animal_ops(t, day, S, V, None, planning=True)
                if ops:
                    j = {"pos": p, "ops": list(ops), "mand": mand, "kind": "animal", "animal": t["animal"]}
            else:
                weed = isinstance(t, dict) and t.get("kind") == "WEED"
                struct = isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE")
                if use is None:
                    if weed and day <= 27:
                        j = {"pos": p, "ops": ["DIG"], "mand": False, "kind": "weed"}
                elif use in CROPS:
                    ops = (["DIG"] if weed or struct else []) + ["PLANT", "WATER"]
                    j = {"pos": p, "ops": ops, "mand": False, "kind": "plant", "plant": use}
                elif use in ANIMALS:
                    ops = []
                    if weed:
                        ops.append("DIG")
                    if struct and t.get("kind") != ANIMALS[use]["struct"]:
                        ops.append("DIG")
                    if not (struct and t.get("kind") == ANIMALS[use]["struct"]):
                        ops.append("BUILD")
                    ops.append("PLACE")
                    j = {"pos": p, "ops": ops, "mand": False, "kind": "place", "place": use}
            if j:
                j["value"] = job_value(j)
                jobs.append(j)
    return jobs


def job_value(j):
    if j["mand"]:
        return 1000
    k = j["kind"]
    if k == "animal":
        return 600
    if k == "place":
        return 500
    if k == "crop":
        return 400 if "HARVEST" in j["ops"] else 300
    if k == "plant":
        return 200
    return 5


# ============================================================================= routing
def mk_shed_stop(pos, drop=False, pickup=None):
    return {"pos": pos, "kind": "shed", "drop": drop, "pickup": dict(pickup or {}), "job": {"ops": [], "kind": "shed"}}


def nearest_shed(pos):
    return min(SHED_TILES, key=lambda s: (dist(pos, s), SHED_TILES.index(s)))


def nn_order(start, jobs, end=None):
    """Nearest neighbour + 2-opt; if end is given the path cost includes returning to end."""
    if not jobs:
        return [], start
    rest = list(jobs)
    path = []
    cur = start
    while rest:
        j = min(rest, key=lambda j: (dist(cur, j["pos"]), -j["value"]))
        rest.remove(j)
        path.append(j)
        cur = j["pos"]

    def plen(pth):
        c = start
        s_ = 0
        for jj in pth:
            s_ += dist(c, jj["pos"])
            c = jj["pos"]
        if end is not None:
            s_ += dist(c, end)
        return s_
    best = plen(path)
    improved = True
    it = 0
    while improved and it < 25:
        improved = False
        it += 1
        for a_ in range(len(path) - 1):
            for b_ in range(a_ + 1, len(path)):
                newp = path[:a_] + path[a_:b_ + 1][::-1] + path[b_ + 1:]
                L = plen(newp)
                if L < best:
                    path, best = newp, L
                    improved = True
    return path, path[-1]["pos"]


LOAD = {"WHEAT": 5, "CARROT": 3, "MELON": 6, "TOMATO": 4, "STRAWBERRY": 4}
ALOAD = {"COW": 3, "SHEEP": 4, "GOOSE": 2}


def job_load(j):
    n = 0
    if "HARVEST" in j["ops"]:
        if j["kind"] == "crop":
            n += LOAD.get(j.get("crop"), 3)
        elif j["kind"] == "animal":
            n += ALOAD.get(j.get("animal"), 2)
    if "COLLECT_FERTILIZER" in j["ops"]:
        n += 1
    return n


def build_route(V, S, start, jobs, mid_drop=False):
    phase_a = [j for j in jobs if j["kind"] in ("animal", "place")]
    phase_b = [j for j in jobs if j["kind"] not in ("animal", "place")]
    load = sum(job_load(j) for j in jobs)
    close = S["cfg"]["final_drop"] and load >= S["cfg"]["drop_load"]
    pa, end_a = nn_order(start, phase_a)
    stops = [{"pos": j["pos"], "kind": "tile", "job": j} for j in pa]
    cur = end_a
    if pa and phase_b and mid_drop:
        stops.append(mk_shed_stop(nearest_shed(cur), drop=True))
        cur = stops[-1]["pos"]
    endp = None
    if close:
        endp = nearest_shed(cur) if not phase_b else None
    if phase_b:
        if close:
            # closed tour back to the shed tile nearest the centroid
            cx = sum(j["pos"][0] for j in phase_b) / len(phase_b)
            cy = sum(j["pos"][1] for j in phase_b) / len(phase_b)
            endp = nearest_shed((int(round(cx)), int(round(cy))))
        pb, _ = nn_order(cur, phase_b, end=endp)
        stops += [{"pos": j["pos"], "kind": "tile", "job": j} for j in pb]
    if stops and close:
        stops.append(mk_shed_stop(endp or nearest_shed(stops[-1]["pos"]), drop=True))
    return stops


def stop_ops(st):
    return max(1, len(st["job"]["ops"])) if st["kind"] == "tile" else 1


def route_cost(start, stops):
    c = start
    t = 1.0 if stops else 0.0  # pickup turn
    for st in stops:
        t += dist(c, st["pos"]) + stop_ops(st)
        c = st["pos"]
    return t


def route_plan(V, S, units, jobs, mid_drop=None):
    """units: list of (idx, pos, start_hour). Returns {idx: stops} fitting each unit's remaining turns."""
    if not units:
        return {}
    if mid_drop is None:
        mid_drop = V.day < S["cfg"]["mid_drop_until"]
    caps = {i: max(0.5, 24 - h - 0.5) for i, _, h in units}
    for j in jobs:
        x, y = j["pos"]
        j["ang"] = math.atan2(y - 4.5, x - 4.5)
        j["cost"] = len(j["ops"]) + 1.5
    if not jobs:
        return {i: [] for i, _, _ in units}
    jobs = sorted(jobs, key=lambda j: j["ang"])
    best_start, best_gap = 0, -1.0
    for k in range(len(jobs)):
        gap = (jobs[k]["ang"] - jobs[k - 1]["ang"]) % (2 * math.pi) if len(jobs) > 1 else 1.0
        if gap > best_gap:
            best_gap, best_start = gap, k
    jobs = jobs[best_start:] + jobs[:best_start]
    n = len(units)
    csum = sum(caps.values())
    jtot = sum(j["cost"] for j in jobs)
    ucaps = sorted(caps.values(), reverse=True)
    chunks, cur, acc, k = [], [], 0.0, 0
    for j in jobs:
        cur.append(j)
        acc += j["cost"]
        if k < n - 1 and acc >= jtot * ucaps[k] / csum:
            chunks.append(cur)
            cur, acc = [], 0.0
            k += 1
    chunks.append(cur)
    while len(chunks) < n:
        chunks.append([])
    order = sorted(range(len(chunks)), key=lambda c: -sum(j["cost"] for j in chunks[c]))
    free = list(units)
    routes = {}
    starts = {i: p for i, p, _ in units}
    for c in order:
        ch = chunks[c]
        if ch:
            cx = sum(j["pos"][0] for j in ch) / len(ch)
            cy = sum(j["pos"][1] for j in ch) / len(ch)
        else:
            cx, cy = 4.5, 4.5
        best = min(free, key=lambda u: (-round(caps[u[0]]), abs(u[1][0] - cx) + abs(u[1][1] - cy)))
        free.remove(best)
        routes[best[0]] = build_route(V, S, best[1], ch, mid_drop=mid_drop)
    fit_capacity(routes, starts, caps)
    return routes


def fit_capacity(routes, starts, caps):
    """Trim overloaded routes (lowest value first, never mandatory) and re-insert into routes with slack."""
    removed = []
    for i, r in routes.items():
        while route_cost(starts[i], r) > caps[i]:
            cand = [k for k, st in enumerate(r) if st["kind"] == "tile" and not st["job"]["mand"]]
            if not cand:
                break
            k = min(cand, key=lambda k: (r[k]["job"]["value"], -k))
            removed.append(r.pop(k))
    removed.sort(key=lambda st: -st["job"]["value"])
    for st in removed:
        best = None
        for i, r in routes.items():
            slack = caps[i] - route_cost(starts[i], r)
            if slack <= stop_ops(st):
                continue
            prev = starts[i]
            for k in range(len(r) + 1):
                nxt = r[k]["pos"] if k < len(r) else None
                add = dist(prev, st["pos"]) + stop_ops(st) + (dist(st["pos"], nxt) - dist(prev, nxt) if nxt else 0)
                if add <= slack and (best is None or add < best[0]):
                    best = (add, i, k)
                prev = r[k]["pos"] if k < len(r) else prev
        if best:
            routes[best[1]].insert(best[2], st)


def add_supplies(V, S, routes, starts):
    """Prepend pickups to the first shed contact; mid-route drop stops get re-pickups for phase B."""
    for i, r in routes.items():
        if not r:
            continue
        # walk the route tracking needs between shed contacts
        segs = []
        seg = {"WHEAT": 0, "FERT_need": 0, "FERT_bal": 0, "animals": {}}
        shed_idx = [-1]
        for k, st in enumerate(r):
            if st["kind"] == "shed":
                segs.append(seg)
                shed_idx.append(k)
                seg = {"WHEAT": 0, "FERT_need": 0, "FERT_bal": 0, "animals": {}}
                continue
            j = st["job"]
            for op in j["ops"]:
                if op == "FEED":
                    seg["WHEAT"] += 1
                elif op == "COLLECT_FERTILIZER":
                    seg["FERT_bal"] += 1
                elif op == "FERTILIZE":
                    seg["FERT_bal"] -= 1
                    seg["FERT_need"] = max(seg["FERT_need"], -seg["FERT_bal"])
                elif op == "PLACE":
                    a = j.get("place")
                    seg["animals"][a] = seg["animals"].get(a, 0) + 1
        segs.append(seg)
        # segment 0 = before first shed stop: pickups at a new first stop (unit start or nearest shed)
        inv = V.invs[i] if i < len(V.invs) else {}
        for si, sg in enumerate(segs):
            pick = {}
            if sg["WHEAT"] > 0:
                pick["WHEAT"] = sg["WHEAT"]
            if sg["FERT_need"] > 0:
                pick["FERTILIZER"] = sg["FERT_need"]
            for a, n in sg["animals"].items():
                pick[a] = n
            if not pick:
                continue
            if si == 0:
                if all(inv.get(k, 0) >= n for k, n in pick.items()):
                    continue
                p = starts.get(i, V.units[i] if i < len(V.units) else (4, 4))
                sp = p if p in SHED_TILES else nearest_shed(p)
                r.insert(0, mk_shed_stop(sp, pickup=pick))
                # shift indices of later shed stops
                shed_idx = [x + 1 if x >= 0 else x for x in shed_idx]
            else:
                k = shed_idx[si]
                if 0 <= k < len(r):
                    r[k]["pickup"] = pick
    return routes


# ============================================================================= execution
def step_toward(pos, target):
    x, y = pos
    tx, ty = target
    if x < tx:
        return "EAST"
    if x > tx:
        return "WEST"
    if y < ty:
        return "SOUTH"
    if y > ty:
        return "NORTH"
    return None


def live_ops(V, S, i, pos, inv, seed_left, stop, shed_now):
    if stop["kind"] == "shed":
        ops = []
        if stop.get("drop") and not stop.get("_dropped"):
            if any(v > 0 for k, v in inv.items()):
                ops.append(["DROP"])
            else:
                stop["_dropped"] = True
        for item, n in stop.get("pickup", {}).items():
            have = 0 if (stop.get("drop") and not stop.get("_dropped")) else inv.get(item, 0)
            need = n - have
            avail = shed_now.get(item, 0)
            if need > 0 and avail > 0:
                ops.append(["PICKUP", item, int(min(need, avail))])
        return ops
    t = V.tile(pos)
    day = V.day
    use = S["tile_use"].get(pos)
    job = stop["job"]
    if t == "LOCKED":
        return []
    if t is None:
        if use in CROPS:
            return [["PLANT", use]] if seed_left.get(use, 0) > 0 else []
        if use in ANIMALS:
            if inv.get(use, 0) > 0:
                return [["BUILD_" + ANIMALS[use]["struct"]]]
            return []
        return []
    kind = t.get("kind")
    if kind == "WEED":
        if use is not None or job.get("kind") == "weed":
            return [["DIG"]]
        return []
    if kind == "PLANT":
        ops, _ = plant_ops(t, day, S, V, inv, planning=False)
        out = []
        for op in ops:
            if op == "HARVEST" and (day - t["planted_day"] < CROPS[t["crop"]]["first"] or t.get("yield_units", 0) <= 0):
                continue
            if op == "DIG" and CROPS[t["crop"]]["ongoing"] and t.get("yield_units", 0) > 0:
                continue
            out.append([op])
        return out
    if kind in ("COOP", "PASTURE"):
        if not t.get("animal"):
            if use in ANIMALS:
                if ANIMALS[use]["struct"] == kind:
                    return [["PLACE", use]] if inv.get(use, 0) > 0 else []
                return [["DIG"]] if inv.get(use, 0) > 0 else []
            if use in CROPS:
                return [["DIG"]]
            return []
        ops, _ = animal_ops(t, day, S, V, inv, planning=False)
        return [[o] for o in ops]
    return []


def execute(V, S):
    n = len(V.units)
    acts = [["PASS"] for _ in range(n)]
    seed_left = dict(V.seeds)
    shed_now = dict(V.shed)
    routes = S["routes"]
    for i in range(n):
        pos = V.units[i]
        inv = V.invs[i] if i < len(V.invs) else {}
        r = routes.get(i, [])
        guard = 0
        while r and guard < 60:
            guard += 1
            stop = r[0]
            if pos != stop["pos"]:
                acts[i] = [step_toward(pos, stop["pos"])]
                break
            ops = live_ops(V, S, i, pos, inv, seed_left, stop, shed_now)
            if not ops:
                r.pop(0)
                continue
            op = ops[0]
            if op[0] == "PLANT":
                seed_left[op[1]] = seed_left.get(op[1], 0) - 1
            elif op[0] == "PICKUP":
                shed_now[op[1]] = shed_now.get(op[1], 0) - op[2]
            elif op[0] == "DROP":
                stop["_dropped"] = True
                for k, v in inv.items():
                    shed_now[k] = shed_now.get(k, 0) + v
            acts[i] = op
            break
        routes[i] = r
    S["shed_proj"] = shed_now
    return acts


# ============================================================================= planning glue
def expected_spawns(V, n_new, farmer_pos):
    occ = {s: 0 for s in SHED_TILES}
    for p in [farmer_pos] + list(V.units[1:]):
        if p in occ:
            occ[p] += 1
    out = []
    for _ in range(n_new):
        best = sorted(occ.items(), key=lambda kv: (kv[1], SHED_TILES.index(kv[0])))[0][0]
        out.append(best)
        occ[best] += 1
    return out


def day_plan(V, S):
    """Hour-0 plan: tile uses, hires, routes for farmer + expected hands."""
    cash = V.money
    sell_val = sum(V.shed.get(k, 0) * V.prices.get(k, 0) for k in PRODUCTS
                   if k not in ("WHEAT", "FERTILIZER")) + 0.6 * V.shed.get("FERTILIZER", 0) * V.prices.get("FERTILIZER", 0)
    budget = cash + 0.7 * sell_val - cash_reserve(V, S) - S["cfg"]["seed_budget"]
    if V.day < 6:
        budget = cash + 0.7 * sell_val
    decide_uses(V, S, max(0.0, budget))
    jobs = gen_jobs(V, S)
    wl = sum(len(j["ops"]) + 1.4 for j in jobs)
    nh = int(math.ceil(max(0.0, wl - 20) / 20.0))
    nh = max(nh, S["cfg"]["hands_min"] if V.day < 10 else 0)
    nh = min(nh, S["cfg"]["max_hands"])
    if V.day >= 29:
        nh = min(nh, 6)
    S["want_hands"] = nh
    race = S["cfg"]["melon_race"] and any(
        isinstance(V.tiles[y][x], dict) and V.tiles[y][x].get("crop") == "MELON" and
        V.day - V.tiles[y][x]["planted_day"] >= 10 for y in range(10) for x in range(10))
    if race:
        S["want_hands"] = max(S["want_hands"], S["cfg"]["race_hands"])
    exp = expected_spawns(V, max(0, S["want_hands"] - (len(V.units) - 1)), V.units[0])
    units = [(0, V.units[0], 0)] + [(k, V.units[k], 0) for k in range(1, len(V.units))] + \
        [(len(V.units) + k, p, 1) for k, p in enumerate(exp)]
    starts = {i: p for i, p, _ in units}
    if race:
        S["race_day"] = V.day
        routes = race_routes(V, S, units, jobs)
    else:
        routes = route_plan(V, S, units, jobs)
    add_supplies(V, S, routes, starts)
    S["routes"] = routes


def race_routes(V, S, units, jobs):
    mel = [j for j in jobs if j.get("crop") == "MELON" and "HARVEST" in j["ops"]]
    rest = [j for j in jobs if not (j.get("crop") == "MELON" and "HARVEST" in j["ops"])]
    mel.sort(key=lambda j: shed_dist(j["pos"]))
    free_at = {i: (h, p) for i, p, h in units}
    race = {i: [] for i, _, _ in units}
    for j in mel:
        best = None
        for i, (h, p) in free_at.items():
            t_done = h + dist(p, j["pos"]) + len(j["ops"]) + shed_dist(j["pos"]) + 1
            if best is None or t_done < best[0]:
                best = (t_done, i)
        t_done, i = best
        race[i].append({"pos": j["pos"], "kind": "tile", "job": j})
        sp = nearest_shed(j["pos"])
        race[i].append(mk_shed_stop(sp, drop=True))
        free_at[i] = (t_done, sp)
    units2 = [(i, free_at[i][1], free_at[i][0]) for i, _, _ in units]
    base = route_plan(V, S, units2, rest)
    out = {}
    for i, _, _ in units:
        out[i] = race[i] + base.get(i, [])
    return out


def replan_idle(V, S):
    idle = [(i, V.units[i], V.hour) for i in range(len(V.units)) if not S["routes"].get(i)]
    if not idle or V.hour >= 22:
        return
    jobs = gen_jobs(V, S)
    taken = set(st["pos"] for r in S["routes"].values() for st in r)
    jobs = [j for j in jobs if j["pos"] not in taken and j["value"] >= 200]
    if not jobs:
        for i, p, h in idle:
            inv = V.invs[i] if i < len(V.invs) else {}
            if any(v > 0 for k, v in inv.items()):
                S["routes"][i] = [mk_shed_stop(nearest_shed(p), drop=True)]
        return
    routes = route_plan(V, S, idle, jobs)
    add_supplies(V, S, routes, {i: p for i, p, _ in idle})
    for i, r in routes.items():
        S["routes"][i] = r


def replan_event(V, S):
    """Land bought / big change: recompute uses and re-route everyone (keep current stops)."""
    decide_uses(V, S, max(0.0, V.money - cash_reserve(V, S)))
    jobs = gen_jobs(V, S)
    keep = {}
    for i, r in S["routes"].items():
        if r and i < len(V.units) and r[0]["kind"] == "tile" and V.units[i] != r[0]["pos"]:
            keep[i] = r[0]
    kp = set(st["pos"] for st in keep.values())
    jobs = [j for j in jobs if j["pos"] not in kp]
    units = []
    for i in range(len(V.units)):
        if i in keep:
            st = keep[i]
            units.append((i, st["pos"], V.hour + dist(V.units[i], st["pos"]) + len(st["job"]["ops"])))
        else:
            units.append((i, V.units[i], V.hour))
    routes = route_plan(V, S, units, jobs)
    add_supplies(V, S, routes, {i: p for i, p, _ in units})
    for i in keep:
        routes.setdefault(i, []).insert(0, keep[i])
    S["routes"] = routes


# ============================================================================= market
def n_animals(V):
    return sum(1 for y in range(10) for x in range(10)
               if isinstance(V.tiles[y][x], dict) and V.tiles[y][x].get("animal"))


def cash_reserve(V, S):
    d = V.day
    if d >= 28:
        return 0
    if d < 6:
        return S["cfg"]["reserve_early"]
    if d < 10:
        return S["cfg"]["reserve_mid"]
    return S["cfg"]["reserve_late"]


def wheat_need(V, S):
    """Wheat to keep in the shed now. Carried wheat counts (it drops into the shed at night)."""
    if V.day >= 28:
        return 0
    na = n_animals(V)
    fed = sum(1 for y in range(10) for x in range(10)
              if isinstance(V.tiles[y][x], dict) and V.tiles[y][x].get("animal") and V.tiles[y][x].get("fed_today"))
    carried = sum(inv.get("WHEAT", 0) for inv in V.invs)
    pend = sum(1 for u in S["tile_use"].values() if u in ANIMALS)
    today = max(0, na - fed)
    tomorrow = (na + pend) if V.hour >= 14 else 0
    return max(0, today + tomorrow - carried) + (1 if V.hour < 20 else 0)


def fert_need(V, S):
    if V.day >= 28:
        return 0
    n = 0
    for y in range(10):
        for x in range(10):
            t = V.tiles[y][x]
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                age = V.day - t["planted_day"]
                for d in ((0, 1) if V.hour >= 12 else (0,)):
                    a = age + d
                    if a in FERT_AGES[t["crop"]] and wants_fert(t["crop"], a, V.day + d, S, V):
                        if d == 0 and t.get("fertilized_until_day", -1) >= V.day:
                            continue
                        n += 1
    carried = sum(inv.get("FERTILIZER", 0) for inv in V.invs)
    return max(0, n - carried)


SELL_PRI = {"MELON": 0, "MILK": 1, "WOOL": 2, "STRAWBERRY": 3, "FERTILIZER": 4, "TOMATO": 5, "EGG": 6,
            "CARROT": 7, "WHEAT": 8}


def route_etas(V, S, i):
    """[(stop, eta_arrival)] for unit i (hands not yet spawned start at hour 1)."""
    r = S["routes"].get(i, [])
    if i < len(V.units):
        pos, t = V.units[i], 0
    else:
        pos, t = None, 1
    out = []
    for st in r:
        if pos is None:
            pos = st["pos"]
        t += dist(pos, st["pos"])
        out.append((st, t))
        t += max(1, len(st["job"]["ops"])) if st["kind"] == "tile" else 1
        pos = st["pos"]
    return out


def market_orders(V, S, acts):
    orders = []
    cash = V.money
    last = V.step >= LAST_STEP - 1
    shed = dict(S.get("shed_proj", V.shed))
    R = cash_reserve(V, S)
    # ---- sells
    sells = []
    for item in PRODUCTS:
        have = shed.get(item, 0)
        if have <= 0:
            continue
        keep = 0
        if not last:
            if item == "WHEAT":
                keep = wheat_need(V, S)
            elif item == "FERTILIZER":
                keep = fert_need(V, S)
        n = have - keep
        if n > 0:
            sells.append([item, int(n)])
    # end-of-day shed room: carried goods drop into the shed after the hour-23 market
    if V.hour >= 22 and not last:
        carried = sum(sum(v for v in inv.values()) for inv in V.invs) + (2 * len(V.units) if V.hour == 22 else len(V.units))
        after = sum(v for k, v in shed.items()) - sum(n for _, n in sells)
        over = after + carried - S["cfg"]["shed_cap"]
        for item in ("WHEAT", "FERTILIZER"):
            if over <= 0:
                break
            kept = shed.get(item, 0) - sum(n for it, n in sells if it == item)
            extra = min(kept, over)
            if extra > 0:
                for sl in sells:
                    if sl[0] == item:
                        sl[1] += extra
                        break
                else:
                    sells.append([item, extra])
                over -= extra
    sells.sort(key=lambda s: SELL_PRI.get(s[0], 9))
    inv_sim = dict(V.minv)
    for item, n in sells:
        orders.append(["SELL", item, n])
        for _ in range(n):
            p = price(item, inv_sim.get(item, 10000))
            cash += p
            if p > 1:
                inv_sim[item] = inv_sim.get(item, 10000) + 1
    if last:
        return orders[:10]
    # ---- hires
    if V.hour <= 2 and V.step < LAST_STEP - 3:
        want = S.get("want_hands", 0)
        have = len(V.units) - 1
        k = V.hires_today
        limit = 8 if V.hour == 0 else 10
        while have < want and len(orders) < limit:
            c = fib(k)
            if c > cash:
                break
            orders.append(["HIRE"])
            cash -= c
            k += 1
            have += 1
    # ---- land
    nq = len(V.quads)
    if nq < 4 and len(orders) < 10:
        cost = LAND_PRICES[nq - 1]
        dday = S["cfg"]["land_days"][nq - 1]
        if dday <= V.day <= S["cfg"]["land_last"] and cash >= cost + S["cfg"]["land_reserve"]:
            orders.append(["BUY_LAND"])
            cash -= cost
            S["event"] = True
    # ---- wheat for feed
    need_w = wheat_need(V, S) - shed.get("WHEAT", 0)
    if need_w > 0 and len(orders) < 10:
        n = 0
        inv_w = V.minv.get("WHEAT", 10000)
        while n < need_w:
            p = price("WHEAT", inv_w - 1)
            if p > cash:
                break
            cash -= p
            inv_w -= 1
            n += 1
        if n:
            orders.append(["BUY_PRODUCT", "WHEAT", n])
    # ---- JIT animals & seeds from route ETAs
    need_a = {}
    need_s = {}
    horizon = 2
    for i, r in list(S["routes"].items()):
        for st, eta in route_etas(V, S, i):
            if eta > horizon + (1 if i >= len(V.units) else 0):
                break
            if st["kind"] == "shed":
                for k, nn in st.get("pickup", {}).items():
                    if k in ANIMALS:
                        need_a[k] = need_a.get(k, 0) + nn
            else:
                c = st["job"].get("plant")
                if c:
                    need_s[c] = need_s.get(c, 0) + 1
    # pickups executing this step already satisfy their stop
    for a in acts:
        if a and a[0] == "PICKUP" and a[1] in ANIMALS:
            need_a[a[1]] = need_a.get(a[1], 0) - a[2]
    for k in ("SHEEP", "COW", "GOOSE"):
        n = need_a.get(k, 0) - shed.get(k, 0)
        m = 0
        while n > 0 and cash - ANIMALS[k]["cost"] >= R and V.shed_total() + m < 98:
            cash -= ANIMALS[k]["cost"]
            n -= 1
            m += 1
        if m and len(orders) < 10:
            orders.append(["BUY_ANIMAL", k, m])
    for c in ("MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"):
        n = need_s.get(c, 0) - V.seeds.get(c, 0)
        m = 0
        while n > 0 and cash - CROPS[c]["seed"] >= (R if V.day >= 2 else 0):
            cash -= CROPS[c]["seed"]
            n -= 1
            m += 1
        if m and len(orders) < 10:
            orders.append(["BUY_SEED", c, m])
    return orders[:10]


# ============================================================================= entry
CFG = {
    "melons_d0": 12, "cows_d0": 2, "sheep_d0": 2,
    "sheep_base": 3, "cow_base": 5, "animal_total": 23,
    "straw_a": 13, "straw_b": 8.7, "tom_a": 14, "tom_b": 7.2, "car_a": 13, "car_b": 4,
    "straw_early": 10, "straw_last": 13, "tom_first": 9, "tom_last": 18, "car_first": 10,
    "animal_last_day": 12, "animal_max_dist": 3, "animal_order": ("SHEEP", "COW", "GOOSE"),
    "hands_min": 4, "max_hands": 12, "race_hands": 12, "melon_race": True,
    "land_days": (6, 9, 10), "land_last": 14, "land_reserve": 0,
    "reserve_early": 12, "reserve_mid": 60, "reserve_late": 150, "seed_budget": 300,
    "mid_drop_until": 10, "shed_cap": 100, "crop_inward": False, "final_drop": True, "drop_load": 12, "fert_wheat_max": 45, "fert_carrot_max": 45,
}


def opening_layout(cfg):
    lay = {}
    nm = cfg["melons_d0"]
    mel = sorted([(x, y) for x in range(5) for y in range(5) if 3 <= (8 - x - y) <= 5],
                 key=lambda p: (8 - p[0] - p[1], -p[1]))
    for p in mel[:nm]:
        lay[p] = "MELON"
    for x in range(5):
        for y in range(5):
            if (x, y) not in lay and (8 - x - y) >= 3:
                lay[(x, y)] = "WHEAT"
    return lay


def new_state():
    cfg = dict(CFG)
    cfg["opening"] = opening_layout(cfg)
    return {"cfg": cfg, "routes": {}, "tile_use": {}, "day": -1, "last_step": -1, "event": False}


def _agent(V, S):
    if S["day"] != V.day:
        S["day"] = V.day
        S["routes"] = {}
    if V.hour == 0:
        day_plan(V, S)
    elif S.get("event") and not (S.get("race_day") == V.day and V.hour < 9):
        S["event"] = False
        replan_event(V, S)
    else:
        # drop routes of hands that did not appear
        replan_idle(V, S)
    acts = execute(V, S)
    orders = market_orders(V, S, acts)
    return {"farmer": acts[0], "hands": acts[1:], "market": orders}


def agent(obs, config=None):
    V = View(obs)
    S = STATE.get(V.me)
    if S is None or V.step == 0 or V.step <= S["last_step"]:
        S = new_state()
        STATE[V.me] = S
    S["last_step"] = V.step
    try:
        return _agent(V, S)
    except Exception as e:
        import traceback
        S.setdefault("errors", []).append(repr(e))
        S["tb"] = traceback.format_exc()
        return {"farmer": ["PASS"], "hands": [["PASS"] for _ in V.units[1:]], "market": []}
