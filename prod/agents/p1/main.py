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


# ----------------------------------------------------------------------------- allocation
def shop_counts(shops, k=None):
    c = {}
    for s in (shops if k is None else shops[:k]):
        c[s] = c.get(s, 0) + 1
    return c


def targets(V, S):
    """Target counts of each tile use for the current day."""
    day = V.day
    shops = V.shops
    c4 = shop_counts(shops, 4)
    call = shop_counts(shops)
    straw_x = sum(c4.get(s, 0) for s in ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET"))
    tom_x = sum(c4.get(s, 0) for s in ("PIZZA_SHOP", "FARMERS_MARKET"))
    car_x = 2 * call.get("PET_CAFE", 0) + call.get("FARMERS_MARKET", 0)
    # animals by unlock day of relevant shop
    inc_sheep = {3: 8, 6: 7, 9: 7, 12: 4, 15: 2}
    inc_cow = {3: 4, 6: 4, 9: 2, 12: 1}
    inc_goose = {3: 4, 6: 3, 9: 2}
    sheep = 3
    cows = 5
    geese = 0
    for k, s in enumerate(shops):
        u = 3 * (k + 1)
        if s == "YARN_STORE":
            sheep += inc_sheep.get(u, 0)
        if s in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"):
            cows += inc_cow.get(u, 0)
        if s in ("BAKERY", "BRUNCH_SPOT"):
            geese += inc_goose.get(u, 0)
    total = S["cfg"]["animal_total"]
    geese = max(geese, total - sheep - cows)
    if day < 6:
        sheep, cows, geese = S["cfg"]["sheep_d0"], S["cfg"]["cows_d0"], 0
    straw = 13 + 8.7 * straw_x
    tom = 14 + 7.2 * tom_x
    car = 13 + 4 * car_x
    return {"SHEEP": sheep, "COW": cows, "GOOSE": geese, "STRAWBERRY": straw, "TOMATO": tom, "CARROT": car}


def animal_slots(V):
    """Owned tiles in order of preference for animals (closest to shed first)."""
    out = []
    for y in range(10):
        for x in range(10):
            if V.owned((x, y)):
                out.append((shed_dist((x, y)), abs(x - 4.5) + abs(y - 4.5), (x, y)))
    out.sort()
    return [p for _, _, p in out]


def count_uses(V):
    c = {}
    for y in range(10):
        for x in range(10):
            t = V.tiles[y][x]
            if isinstance(t, dict):
                k = t.get("animal") or t.get("crop") or t.get("kind")
                c[k] = c.get(k, 0) + 1
    return c


def choose_crop(V, S, p, cnt, tg):
    """Crop for a free tile at p today (or None to leave it)."""
    day = V.day
    if day >= 28:
        return None
    if day <= 1 and S["cfg"].get("opening_crop"):
        return S["cfg"]["opening_crop"].get(p, "WHEAT")
    if day < 6:
        return "STRAWBERRY" if 2 <= day <= 4 and cnt.get("STRAWBERRY", 0) < S["cfg"].get("straw_early", 10) else (
            "WHEAT" if day <= 25 else None)
    if day <= S["cfg"]["straw_last_plant"] and cnt.get("STRAWBERRY", 0) < tg["STRAWBERRY"]:
        return "STRAWBERRY"
    if 9 <= day <= S["cfg"]["tomato_last_plant"] and cnt.get("TOMATO", 0) < tg["TOMATO"]:
        return "TOMATO"
    if day >= 10 and day <= 27 and cnt.get("CARROT", 0) < tg["CARROT"] * (0.3 if day < 19 else 1.0):
        return "CARROT"
    if day <= 26:
        return "WHEAT"
    if day <= 27:
        return "CARROT"
    return None


# ----------------------------------------------------------------------------- planning (jobs)
def build_alloc(V, S):
    """Decide what goes on every free (or freeing-today) tile: crop name or ('A', kind)."""
    tg = targets(V, S)
    cnt = count_uses(V)
    alloc = {}
    # animals wanted beyond current
    have = {k: cnt.get(k, 0) for k in ANIMALS}
    pending = S.get("animal_queue", [])
    for k in pending:
        have[k] = have.get(k, 0) + 1
    want = []
    if V.day <= S["cfg"].get("animal_last_day", 12):
        for k in ("COW", "SHEEP", "GOOSE"):
            for _ in range(max(0, int(round(tg[k])) - have.get(k, 0))):
                want.append(k)
    S["tg"] = tg
    S["want_animals"] = want
    return alloc


def free_tiles_today(V, S):
    out = []
    for y in range(10):
        for x in range(10):
            p = (x, y)
            if not V.owned(p):
                continue
            t = V.tiles[y][x]
            if t is None or (isinstance(t, dict) and t.get("kind") == "WEED"):
                out.append(p)
    return out


def gen_jobs(V, S, planning=True):
    """List of stops needed today: dict(pos, ops(est), mandatory, kind)."""
    jobs = []
    day = V.day
    for y in range(10):
        for x in range(10):
            p = (x, y)
            t = V.tiles[y][x]
            if t == "LOCKED":
                continue
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                ops, mand = plant_ops(t, day, S, V, None, planning=True)
                if ops:
                    # replant after a final harvest / dig
                    if ("HARVEST" in ops and not CROPS[t["crop"]]["ongoing"]) or "DIG" in ops:
                        c = S["tile_use"].get(p)
                        if c and c in CROPS:
                            ops = ops + ["PLANT", "WATER"]
                    jobs.append({"pos": p, "ops": ops, "mand": mand, "kind": "crop", "crop": t["crop"]})
            elif isinstance(t, dict) and "animal" in t and t.get("animal"):
                ops, mand = animal_ops(t, day, S, V, None, planning=True)
                if ops:
                    jobs.append({"pos": p, "ops": ops, "mand": mand, "kind": "animal", "animal": t["animal"]})
            else:
                use = S["tile_use"].get(p)
                if use is None:
                    if isinstance(t, dict) and t.get("kind") == "WEED":
                        jobs.append({"pos": p, "ops": ["DIG"], "mand": False, "kind": "weed"})
                    continue
                ops = []
                if isinstance(t, dict) and t.get("kind") == "WEED":
                    ops.append("DIG")
                if use in CROPS:
                    ops += ["PLANT", "WATER"]
                    jobs.append({"pos": p, "ops": ops, "mand": False, "kind": "plant", "crop": use})
                elif use in ANIMALS:
                    st = ANIMALS[use]["struct"]
                    if not (isinstance(t, dict) and t.get("kind") == st):
                        ops.append("BUILD_" + st)
                    ops.append("PLACE")
                    jobs.append({"pos": p, "ops": ops, "mand": False, "kind": "place", "animal": use})
    return jobs


# ----------------------------------------------------------------------------- tile-use decisions
def decide_tile_use(V, S):
    """Assign uses to free tiles and tiles that free up today. Stored in S['tile_use'][pos]."""
    tu = S["tile_use"]
    day = V.day
    cnt = count_uses(V)
    tg = S["tg"]
    # clear uses for tiles now occupied by the planned thing
    for p in list(tu.keys()):
        t = V.tile(p)
        if isinstance(t, dict) and (t.get("kind") == "PLANT" or t.get("animal")):
            if tu[p] in ANIMALS and t.get("animal") == tu[p]:
                del tu[p]
            elif tu[p] in CROPS and t.get("kind") == "PLANT":
                # keep the replant choice only if the tile will be freed today; recomputed below
                del tu[p]
    # animals: queue of animals to place -> nearest free animal slots
    slots = [p for p in animal_slots(V) if V.owned(p)]
    want = list(S.get("want_animals", []))
    for p, u in tu.items():
        if u in want:
            want.remove(u)
    placed_targets = [p for p, u in tu.items() if u in ANIMALS]
    need = len(want)
    if need > 0:
        for p in slots:
            if need <= 0:
                break
            if p in tu and tu[p] in ANIMALS:
                continue
            t = V.tile(p)
            free = t is None or (isinstance(t, dict) and t.get("kind") in ("WEED", "COOP", "PASTURE") and not t.get("animal"))
            if not free:
                continue
            if shed_dist(p) > S["cfg"].get("animal_max_dist", 3):
                break
            k = want.pop(0)
            if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE"):
                # reuse matching structure if possible
                pass
            tu[p] = k
            need -= 1
    # crops on free tiles and tiles freeing today
    work = dict(cnt)
    for p, u in tu.items():
        if u in CROPS:
            work[u] = work.get(u, 0) + 1
    for y in range(10):
        for x in range(10):
            p = (x, y)
            if not V.owned(p) or p in tu:
                continue
            t = V.tiles[y][x]
            freeing = False
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                ops, _ = plant_ops(t, day, S, V, None, planning=True)
                if ("HARVEST" in ops and not CROPS[t["crop"]]["ongoing"]) or "DIG" in ops:
                    freeing = True
                    work[t["crop"]] = work.get(t["crop"], 0) - 1
            if t is None or (isinstance(t, dict) and t.get("kind") == "WEED") or freeing:
                c = choose_crop(V, S, p, work, tg)
                if c:
                    tu[p] = c
                    work[c] = work.get(c, 0) + 1


# ----------------------------------------------------------------------------- routing
def route_plan(V, S, units_avail, jobs):
    """units_avail: list of (idx, pos, start_hour). Returns {idx: [stop,...]}."""
    hours_left = {i: max(0, 24 - h) for i, _, h in units_avail}
    if not units_avail:
        return {}
    # sort jobs by angle around the shed
    cx, cy = 4.5, 4.5
    for j in jobs:
        x, y = j["pos"]
        j["ang"] = math.atan2(y - cy, x - cx)
        j["cost"] = len(j["ops"]) + 1.3
    jobs = sorted(jobs, key=lambda j: j["ang"])
    total = sum(j["cost"] for j in jobs)
    cap = sum(hours_left.values())
    # drop optional work when over capacity
    if total > cap * 0.92:
        opt = sorted([j for j in jobs if not j["mand"]], key=lambda j: j.get("value", 0))
        keep = set(id(j) for j in jobs)
        over = total - cap * 0.92
        for j in opt:
            if over <= 0:
                break
            keep.discard(id(j))
            over -= j["cost"]
        jobs = [j for j in jobs if id(j) in keep]
        total = sum(j["cost"] for j in jobs)
    n = len(units_avail)
    if not jobs:
        return {i: [] for i, _, _ in units_avail}
    # choose a rotation start: the largest angular gap
    best_start, best_gap = 0, -1
    for k in range(len(jobs)):
        a0 = jobs[k - 1]["ang"]
        a1 = jobs[k]["ang"]
        gap = (a1 - a0) % (2 * math.pi)
        if gap > best_gap:
            best_gap, best_start = gap, k
    jobs = jobs[best_start:] + jobs[:best_start]
    # split into n chunks proportional to unit capacity
    caps = [hours_left[i] for i, _, _ in units_avail]
    capsum = sum(caps) or 1
    chunks = []
    idx = 0
    acc = 0.0
    cur = []
    targ = [total * c / capsum for c in caps]
    k = 0
    for j in jobs:
        cur.append(j)
        acc += j["cost"]
        if k < n - 1 and acc >= targ[k] * 0.98:
            chunks.append(cur)
            cur = []
            acc = 0.0
            k += 1
    chunks.append(cur)
    while len(chunks) < n:
        chunks.append([])
    # assign chunks to units greedily by distance from unit start to chunk centroid
    cents = []
    for ch in chunks:
        if ch:
            cents.append((sum(j["pos"][0] for j in ch) / len(ch), sum(j["pos"][1] for j in ch) / len(ch)))
        else:
            cents.append((4.5, 4.5))
    order = sorted(range(n), key=lambda c: -sum(j["cost"] for j in chunks[c]))
    free_units = list(units_avail)
    assign = {}
    for c in order:
        best = None
        for u in free_units:
            d = abs(u[1][0] - cents[c][0]) + abs(u[1][1] - cents[c][1])
            # prefer units with more hours for bigger chunks
            sc = d - 0.2 * hours_left[u[0]]
            if best is None or sc < best[0]:
                best = (sc, u)
        free_units.remove(best[1])
        assign[best[1][0]] = (best[1], chunks[c])
    routes = {}
    for i, (u, ch) in assign.items():
        routes[i] = order_route(u[1], ch)
    return routes


def order_route(start, jobs):
    """Nearest neighbour then 2-opt on Manhattan distance."""
    if not jobs:
        return []
    rest = list(jobs)
    path = []
    cur = start
    while rest:
        j = min(rest, key=lambda j: (dist(cur, j["pos"]), -j.get("pri", 0)))
        rest.remove(j)
        path.append(j)
        cur = j["pos"]
    # 2-opt
    def plen(pth):
        c = start
        s = 0
        for j in pth:
            s += dist(c, j["pos"])
            c = j["pos"]
        return s
    improved = True
    it = 0
    while improved and it < 30:
        improved = False
        it += 1
        for a in range(len(path) - 1):
            for b in range(a + 1, len(path)):
                newp = path[:a] + path[a:b + 1][::-1] + path[b + 1:]
                if plen(newp) < plen(path):
                    path = newp
                    improved = True
    return [{"pos": j["pos"], "kind": j["kind"], "job": j} for j in path]


# ----------------------------------------------------------------------------- execution
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


def nearest_shed(pos):
    return min(SHED_TILES, key=lambda s: (dist(pos, s), SHED_TILES.index(s)))


def live_ops(V, S, pos, inv, seed_left, stop):
    """Ops to do right now at pos given live state. Returns list (first is executed)."""
    t = V.tile(pos)
    day = V.day
    kind = stop.get("kind")
    if kind == "shed":
        ops = []
        for item, n in stop.get("pickup", {}).items():
            have = inv.get(item, 0)
            need = n - have
            if need > 0 and V.shed.get(item, 0) > 0:
                ops.append(["PICKUP", item, int(min(need, V.shed.get(item, 0)))])
        if stop.get("drop") and any(v > 0 for k, v in inv.items() if k not in ("WHEAT", "FERTILIZER") or stop.get("drop_all")):
            ops.append(["DROP"])
        return ops
    if t == "LOCKED":
        return []
    if t is None:
        use = S["tile_use"].get(pos)
        if use in CROPS:
            if seed_left.get(use, 0) > 0:
                return [["PLANT", use]]
            return []
        if use in ANIMALS:
            st = ANIMALS[use]["struct"]
            return [["BUILD_" + st]]
        return []
    if t.get("kind") == "WEED":
        use = S["tile_use"].get(pos)
        if use is None and kind != "weed":
            return []
        return [["DIG"]]
    if t.get("kind") == "PLANT":
        ops, _ = plant_ops(t, day, S, V, inv, planning=False)
        out = []
        for op in ops:
            if op == "HARVEST":
                if day - t["planted_day"] < CROPS[t["crop"]]["first"] or t.get("yield_units", 0) <= 0:
                    continue
            if op == "DIG":
                # only dig after harvest is empty
                pass
            if op == "FERTILIZE" and inv.get("FERTILIZER", 0) <= 0:
                continue
            out.append([op])
        return out
    if t.get("kind") in ("COOP", "PASTURE"):
        if not t.get("animal"):
            use = S["tile_use"].get(pos)
            if use in ANIMALS and ANIMALS[use]["struct"] == t["kind"] and inv.get(use, 0) > 0:
                return [["PLACE", use]]
            if use in ANIMALS and ANIMALS[use]["struct"] != t["kind"]:
                return [["DIG"]]
            if use in CROPS:
                return [["DIG"]]
            return []
        ops, _ = animal_ops(t, day, S, V, inv, planning=False)
        return [[o] for o in ops]
    return []


def execute(V, S):
    """Produce unit actions for this step from routes."""
    n = len(V.units)
    acts = [["PASS"] for _ in range(n)]
    seed_left = dict(V.seeds)
    routes = S["routes"]
    for i in range(n):
        pos = V.units[i]
        inv = V.invs[i] if i < len(V.invs) else {}
        r = routes.get(i, [])
        guard = 0
        while r and guard < 50:
            guard += 1
            stop = r[0]
            target = stop["pos"]
            if pos != target:
                acts[i] = [step_toward(pos, target)]
                break
            ops = live_ops(V, S, pos, inv, seed_left, stop)
            if not ops:
                r.pop(0)
                continue
            op = ops[0]
            if op[0] == "PLANT":
                seed_left[op[1]] = seed_left.get(op[1], 0) - 1
            acts[i] = op
            break
        routes[i] = r
    return acts


# ----------------------------------------------------------------------------- supplies
def add_supplies(V, S, routes, units_avail):
    """Prepend a shed stop with pickups (wheat for FEED, fertilizer, animals to place) to each route."""
    start = {i: p for i, p, _ in units_avail}
    for i, r in routes.items():
        wheat = 0
        fert_bal = 0
        fert_min = 0
        animals = {}
        for st in r:
            j = st["job"]
            for op in j["ops"]:
                if op == "FEED":
                    wheat += 1
                elif op == "COLLECT_FERTILIZER":
                    fert_bal += 1
                elif op == "FERTILIZE":
                    fert_bal -= 1
                    fert_min = min(fert_min, fert_bal)
                elif op == "PLACE":
                    k = j.get("animal")
                    animals[k] = animals.get(k, 0) + 1
        pick = {}
        inv = V.invs[i] if i < len(V.invs) else {}
        if wheat > inv.get("WHEAT", 0):
            pick["WHEAT"] = wheat
        if -fert_min > inv.get("FERTILIZER", 0):
            pick["FERTILIZER"] = -fert_min
        for k, n in animals.items():
            if n > inv.get(k, 0):
                pick[k] = n
        if pick:
            p = start[i]
            sp = p if p in SHED_TILES else nearest_shed(p)
            r.insert(0, {"pos": sp, "kind": "shed", "pickup": pick, "job": {"ops": [], "kind": "shed"}})
    return routes


# ----------------------------------------------------------------------------- planning entry
def plan(V, S, units_avail, keep_current=True):
    build_alloc(V, S)
    decide_tile_use(V, S)
    jobs = gen_jobs(V, S)
    committed = {}
    if keep_current:
        for i, r in S["routes"].items():
            if r and i < len(V.units) and r[0]["kind"] != "shed" and V.units[i] != r[0]["pos"]:
                committed[i] = r[0]
    cpos = set(st["pos"] for st in committed.values())
    jobs = [j for j in jobs if j["pos"] not in cpos]
    for j in jobs:
        j["value"] = job_value(j, V)
    routes = route_plan(V, S, units_avail, jobs)
    for i, st in committed.items():
        if i in routes:
            routes[i].insert(0, st)
    add_supplies(V, S, routes, units_avail)
    for i, r in routes.items():
        if r:
            last = r[-1]["pos"]
            r.append({"pos": nearest_shed(last), "kind": "shed", "drop": True, "job": {"ops": [], "kind": "shed"}})
    S["routes"] = routes
    S["jobs_n"] = len(jobs)


def job_value(j, V):
    if j["mand"]:
        return 1000
    k = j["kind"]
    if k == "animal":
        return 500
    if k == "place":
        return 400
    if k == "crop":
        return 300 if "HARVEST" in j["ops"] else 200
    if k == "plant":
        return 150
    return 10


def workload(V, S):
    jobs = gen_jobs(V, S)
    return sum(len(j["ops"]) + 1.3 for j in jobs) + 6 * 1.0


# ----------------------------------------------------------------------------- market
def n_animals(V):
    return sum(1 for y in range(10) for x in range(10)
               if isinstance(V.tiles[y][x], dict) and V.tiles[y][x].get("animal"))


def reserve_wheat(V, S):
    if V.day >= 28:
        return 0
    n_anim = n_animals(V)
    fed = sum(1 for y in range(10) for x in range(10)
              if isinstance(V.tiles[y][x], dict) and V.tiles[y][x].get("animal") and V.tiles[y][x].get("fed_today"))
    carried = sum(inv.get("WHEAT", 0) for inv in V.invs)
    today_left = max(0, n_anim - fed - carried)
    pending = sum(1 for u in S["tile_use"].values() if u in ANIMALS)
    tomorrow = n_anim + pending
    return today_left + (tomorrow if V.hour >= 12 else 0) + 2


def reserve_fert(V, S):
    if V.day >= 28:
        return 0
    n = 0
    for y in range(10):
        for x in range(10):
            t = V.tiles[y][x]
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                age = V.day - t["planted_day"]
                for d in (0, 1):
                    if (age + d) in FERT_AGES[t["crop"]] and wants_fert(t["crop"], age + d, V.day + d, S, V):
                        n += 1
    carried = sum(inv.get("FERTILIZER", 0) for inv in V.invs)
    return max(0, n - carried)


SELL_PRI = {"MELON": 0, "MILK": 1, "WOOL": 2, "STRAWBERRY": 3, "FERTILIZER": 4, "TOMATO": 5, "EGG": 6, "CARROT": 7,
            "WHEAT": 8}


def market_orders(V, S, acts):
    orders = []
    cash = V.money
    last = V.step >= LAST_STEP - 1
    sells = []
    for item in PRODUCTS:
        have = V.shed.get(item, 0)
        if have <= 0:
            continue
        keep = 0
        if not last:
            if item == "WHEAT":
                keep = reserve_wheat(V, S)
            elif item == "FERTILIZER":
                keep = reserve_fert(V, S)
        n = have - keep
        if n > 0:
            sells.append([item, n])
    sells.sort(key=lambda s: SELL_PRI.get(s[0], 9))
    inv_sim = dict(V.minv)
    for item, n in sells:
        orders.append(["SELL", item, int(n)])
        for _ in range(int(n)):
            p = price(item, inv_sim.get(item, 10000))
            cash += p
            if p > 1:
                inv_sim[item] = inv_sim.get(item, 10000) + 1
    if last:
        return orders[:10]
    # --- hires
    if V.hour in (0, 1) and V.step < LAST_STEP - 2:
        want = S.get("want_hands", 0)
        have = len(V.units) - 1
        k = V.hires_today
        while have < want and len(orders) < 10:
            c = fib(k)
            if c > cash - 5:
                break
            orders.append(["HIRE"])
            cash -= c
            k += 1
            have += 1
    # --- land
    nq = len(V.quads)
    if nq < 4 and len(orders) < 10:
        cost = LAND_PRICES[nq - 1]
        dday = S["cfg"]["land_days"][nq - 1]
        if dday <= V.day <= 14 and cash >= cost + S["cfg"].get("land_reserve", 0):
            orders.append(["BUY_LAND"])
            cash -= cost
            S["replan"] = True
    # --- wheat for feed
    need_w = reserve_wheat(V, S) - V.shed.get("WHEAT", 0)
    if need_w > 0 and len(orders) < 10 and V.day < 28:
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
    # --- animals for assigned tiles
    if len(orders) < 10:
        need = {}
        for p, u in S["tile_use"].items():
            if u in ANIMALS:
                need[u] = need.get(u, 0) + 1
        for k in need:
            need[k] -= V.shed.get(k, 0) + sum(inv.get(k, 0) for inv in V.invs)
        for k in ("SHEEP", "COW", "GOOSE"):
            n = need.get(k, 0)
            while n > 0 and len(orders) < 10 and cash >= ANIMALS[k]["cost"] + S["cfg"].get("animal_reserve", 0) \
                    and V.shed_total() < 95:
                if orders and orders[-1][0] == "BUY_ANIMAL" and orders[-1][1] == k:
                    orders[-1][2] += 1
                else:
                    orders.append(["BUY_ANIMAL", k, 1])
                cash -= ANIMALS[k]["cost"]
                n -= 1
                S["replan"] = True
    # --- seeds for planned plantings
    if len(orders) < 10:
        need = {}
        for p, u in S["tile_use"].items():
            if u in CROPS:
                need[u] = need.get(u, 0) + 1
        for c in ("MELON", "STRAWBERRY", "TOMATO", "CARROT", "WHEAT"):
            n = need.get(c, 0) - V.seeds.get(c, 0)
            m = 0
            while n > 0 and cash >= CROPS[c]["seed"]:
                cash -= CROPS[c]["seed"]
                n -= 1
                m += 1
            if m and len(orders) < 10:
                orders.append(["BUY_SEED", c, m])
    return orders[:10]


# ----------------------------------------------------------------------------- main
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


def decide_hands(V, S):
    wl = workload(V, S)
    n = int(math.ceil(max(0.0, wl - 23) / 21.0))
    n = max(S["cfg"]["hands_early"] if V.day < 6 else 0, n)
    return min(S["cfg"]["max_hands"], n)


def opening_layout(cfg):
    """NW day-0/1 plan: tile -> crop; animals go to the first animal slots."""
    lay = {}
    nm = cfg["melons_d0"]
    mel_tiles = sorted([(x, y) for x in range(5) for y in range(5) if 3 <= (8 - x - y) <= 5],
                       key=lambda p: (8 - p[0] - p[1], -p[1]))
    for p in mel_tiles[:nm]:
        lay[p] = "MELON"
    for x in range(5):
        for y in range(5):
            if (x, y) not in lay and (8 - x - y) >= 3:
                lay[(x, y)] = "WHEAT"
    return lay


def _agent(V, S):
    day, hour = V.day, V.hour
    if S["day"] != day:
        S["day"] = day
        S["routes"] = {}
        S["replan"] = False
        S["tile_use"] = {p: u for p, u in S["tile_use"].items() if u in ANIMALS}
    units_avail = [(i, V.units[i], hour) for i in range(len(V.units))]
    if hour == 0:
        build_alloc(V, S)
        decide_tile_use(V, S)
        S["want_hands"] = decide_hands(V, S)
        exp = expected_spawns(V, max(0, S["want_hands"] - (len(V.units) - 1)), V.units[0])
        ua = units_avail + [(len(V.units) + k, p, 1) for k, p in enumerate(exp)]
        plan(V, S, ua, keep_current=False)
    elif S.get("replan"):
        plan(V, S, units_avail)
        S["replan"] = False
    elif hour < 22:
        idle = [u for u in units_avail if not S["routes"].get(u[0])]
        if idle and hour >= 2:
            plan_idle(V, S, idle)
    acts = execute(V, S)
    orders = market_orders(V, S, acts)
    return {"farmer": acts[0], "hands": acts[1:], "market": orders}


def plan_idle(V, S, idle):
    """Give idle units the jobs no other unit has in its route."""
    jobs = gen_jobs(V, S)
    taken = set()
    for i, r in S["routes"].items():
        for st in r:
            taken.add(st["pos"])
    jobs = [j for j in jobs if j["pos"] not in taken]
    if not jobs:
        # nothing left: park at shed drop if carrying goods
        for i, p, h in idle:
            inv = V.invs[i] if i < len(V.invs) else {}
            if any(v > 0 for k, v in inv.items() if k not in ("WHEAT", "FERTILIZER")) and V.hour < 23:
                S["routes"][i] = [{"pos": nearest_shed(p), "kind": "shed", "drop": True, "job": {"ops": [], "kind": "shed"}}]
        return
    for j in jobs:
        j["value"] = job_value(j, V)
    routes = route_plan(V, S, idle, jobs)
    add_supplies(V, S, routes, idle)
    for i, r in routes.items():
        if r:
            r.append({"pos": nearest_shed(r[-1]["pos"]), "kind": "shed", "drop": True, "job": {"ops": [], "kind": "shed"}})
        S["routes"][i] = r


def agent(obs, config=None):
    V = View(obs)
    key = V.me
    S = STATE.get(key)
    if S is None or V.step == 0 or V.step <= S["last_step"]:
        S = new_state()
        S["cfg"] = dict(CFG)
        S["tile_use"] = {}
        S["cfg"]["opening_crop"] = opening_layout(S["cfg"])
        STATE[key] = S
    S["last_step"] = V.step
    try:
        return _agent(V, S)
    except Exception as e:  # never crash
        S.setdefault("errors", []).append(repr(e))
        import traceback
        S["tb"] = traceback.format_exc()
        return {"farmer": ["PASS"], "hands": [["PASS"] for _ in V.units[1:]], "market": []}
