"""Production agent P3 (team 42 research, 2026-09-26).

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


STATE = {}


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



# ============================================================================= crop / animal rules
WATER_AGES = {
    "WHEAT": {0, 2, 3},
    "CARROT": {0, 2},
    "TOMATO": {0, 2, 4, 6, 7, 8, 9, 10},
    "STRAWBERRY": {0, 2, 4, 6, 8, 9, 11, 13, 15},
    "MELON": {0, 2, 4, 6, 7, 8, 9, 10},
}
FERT_AGES = {"WHEAT": {2}, "CARROT": {2}, "TOMATO": {7, 10}, "STRAWBERRY": {9, 13}, "MELON": set()}
FINAL_AGE = {"TOMATO": 11, "STRAWBERRY": 16}
LAST_DAY = 29
SELLABLE = ("MELON", "MILK", "WOOL", "STRAWBERRY", "EGG", "TOMATO", "CARROT")
LOAD = {"WHEAT": 5, "CARROT": 3, "MELON": 6, "TOMATO": 4, "STRAWBERRY": 4}
ALOAD = {"COW": 3, "SHEEP": 4, "GOOSE": 2}


def wants_fert(crop, age, day, S, V):
    if age not in FERT_AGES[crop]:
        return False
    fp = V.prices.get("FERTILIZER", 100)
    if crop in ("TOMATO", "STRAWBERRY"):
        return fp <= S["cfg"]["fert_premium_max"]
    if crop == "WHEAT":
        return fp <= S["cfg"]["fert_wheat_max"] and day <= 26
    if crop == "CARROT":
        return fp <= S["cfg"]["fert_carrot_max"]
    return False


def plant_ops(tile, day, S, V, inv, planning=False):
    """(ops wanted now in order, urgency) urgency: 2 = dies tonight if not watered, 1 = harvest due, 0 = normal."""
    crop = tile["crop"]
    cd = CROPS[crop]
    age = day - tile["planted_day"]
    y = tile.get("yield_units", 0)
    w = tile.get("watered_today", False)
    fu = tile.get("fertilized_until_day", -1)
    cu = tile.get("consecutive_unwatered", 0)
    have_fert = planning or (inv is not None and inv.get("FERTILIZER", 0) > 0)
    die = 2 if (cu >= 1 and not w) else 0
    ops = []
    if day >= LAST_DAY and S["cfg"]["endgame"]:
        if age >= cd["first"] and y > 0:
            if not cd["ongoing"] and not w and age <= cd["maxday"] and crop != "MELON":
                ops.append("WATER")
            ops.append("HARVEST")
        return ops, (1 if ops else 0)
    if crop in ("WHEAT", "CARROT"):
        if age >= 2:
            fert_ok = age == 2 and fu < day and not w and have_fert and wants_fert(crop, age, day, S, V)
            if crop == "WHEAT" and age == 2 and (fert_ok or fu >= day):
                if fert_ok:
                    ops.append("FERTILIZE")
                if not w:
                    ops.append("WATER")
                return ops, max(die, 1)
            if crop == "CARROT" and age == 2 and S["cfg"]["carrot_age3"] and day < LAST_DAY - 1 and not fert_ok:
                # one more watered day in the yield window before the harvest
                if not w:
                    ops.append("WATER")
                return ops, max(die, 1)
            if crop == "WHEAT" and age == 3 and fu >= day and S["cfg"]["wheat_age4"] and day < LAST_DAY - 1:
                if not w:
                    ops.append("WATER")
                return ops, max(die, 1)
            if fert_ok:
                ops.append("FERTILIZE")
            if not w and age <= cd["maxday"]:
                ops.append("WATER")
            ops.append("HARVEST")
            return ops, max(die, 1)
        if not w and (age == 0 or cu >= 1 or S["cfg"]["water_all"]):
            ops.append("WATER")
        return ops, (2 if age == 0 and not w else die)
    if crop == "MELON":
        if age >= 10:
            if not w and age <= 12 and y < 6:
                ops.append("WATER")
            ops.append("HARVEST")
            return ops, max(die, 1)
        if not w and (age in WATER_AGES[crop] or cu >= 1 or S["cfg"]["water_all"]):
            ops.append("WATER")
        return ops, (2 if age == 0 and not w else die)
    final = FINAL_AGE[crop]
    if age >= final:
        if y > 0:
            ops.append("HARVEST")
        ops.append("DIG")
        return ops, 1
    if age in FERT_AGES[crop] and fu < day and have_fert and wants_fert(crop, age, day, S, V):
        ops.append("FERTILIZE")
    if y >= S["cfg"]["ongoing_harvest_min"] and age >= cd["first"]:
        ops.append("HARVEST")
    elif crop == "STRAWBERRY" and S["cfg"]["straw_next_day"] and y > 0 and age in (10, 12, 14):
        ops.append("HARVEST")
    if not w and (age in WATER_AGES[crop] or cu >= 1 or S["cfg"]["water_all"]):
        ops.append("WATER")
    return ops, (2 if age == 0 and not w else die)


def feed_worth(kind, tile, day, V, S):
    """DSM-style value feeding: always on production days; otherwise only if product/wheat price is high."""
    if not S["cfg"]["feed_skip"]:
        return True
    a = ANIMALS[kind]
    age = day - tile.get("placed_day", 0)
    nxt = day + 1
    dsf = nxt - tile.get("placed_day", 0) - a["first"]
    prod_day = dsf >= 0 and dsf % a["interval"] == 0
    if prod_day or tile.get("consecutive_unfed", 0) >= 1:
        return True
    ratio = V.prices.get(a["product"], 1) / max(1, V.prices.get("WHEAT", 25))
    return ratio >= S["cfg"]["feed_ratio"]


def last_feed_day(tile, S):
    kind = tile["animal"]
    if not S["cfg"]["stop_feed_auto"]:
        return S["cfg"]["stop_feed"].get(kind, 28)
    a = ANIMALS[kind]
    pl = tile.get("placed_day", 0)
    for D in range(28, -1, -1):
        dsf = D + 1 - pl - a["first"]
        if dsf >= 0 and dsf % a["interval"] == 0:
            return D
    return -1


def animal_ops(tile, day, S, V, inv, planning=False):
    ops = []
    kind = tile["animal"]
    if tile.get("yield_units", 0) > 0:
        ops.append("HARVEST")
    if day >= LAST_DAY and S["cfg"]["endgame"]:
        return ops, 0
    fed = tile.get("fed_today", False)
    stop = last_feed_day(tile, S)
    mand = tile.get("consecutive_unfed", 0) >= 1
    if not fed and (day <= stop or (mand and day <= stop + 1)) and (planning or inv.get("WHEAT", 0) > 0):
        if mand or feed_worth(kind, tile, day, V, S):
            ops.append("FEED")
    if not tile.get("cared_today", False) and (fed or "FEED" in ops) and day <= stop:
        ops.append("CARE")
    if tile.get("fertilizer_available", False) and V.prices.get("FERTILIZER", 0) >= S["cfg"]["collect_min_price"]:
        ops.append("COLLECT_FERTILIZER")
    return ops, (2 if mand and day <= stop else 0)


# ============================================================================= strategy
def shop_counts(shops, k=None):
    c = {}
    for s in (shops if k is None else shops[:k]):
        c[s] = c.get(s, 0) + 1
    return c


# ---- unreal mode (9/28): day-by-day targets read from unreal's 115 games (research/carrera/tapes/unreal_56618268)
UNREAL_CAR_CURVE = {11: 1.6, 12: 1.4, 13: 1.4, 14: 1.3, 15: 1.3, 16: 1.9, 17: 2.5, 18: 3.1, 19: 3.8, 20: 4.0, 21: 4.3,
                    22: 5.0, 23: 5.8, 24: 6.8, 25: 7.9, 26: 7.8, 27: 4.6}
UNREAL_CAR_TOTAL = [30, 60, 92, 129]


def _buyers(shops, item):
    return sum(1 for s in shops if item in SHOPS.get(s, []))


def targets_unreal(V, S):
    d, sh = V.day, V.shops
    milk6, egg6, straw6 = _buyers(sh[:2], "MILK"), _buyers(sh[:2], "EGG"), _buyers(sh[:2], "STRAWBERRY")
    yarn = sum(1 for s in sh[:4] if s == "YARN_STORE")
    straw12 = _buyers(sh[:4], "STRAWBERRY")
    cows = 2 if d < 2 else (min(5, d + 1) if d < 6 else min(11, 5 + 2 * milk6))
    sheep = 3 if d < 6 else min(15, 3 + 4 * yarn)
    geese = 0 if d < 6 else (min(12, 3 + int(round(1.5 * egg6))) if d < 8 else min(12, 8 + int(round(1.5 * egg6))))
    straw = 0 if d < 2 else 8
    if d >= 6:
        straw += [4, 12, 18][min(straw6, 2)]
    if d >= 12:
        straw += [5, 7, 10, 11, 11][min(straw12, 4)]
    tom = 9 if (d >= 15 and _buyers(sh[:5], "TOMATO") >= 3) else 0
    return {"SHEEP": sheep, "COW": cows, "GOOSE": geese, "STRAWBERRY": straw, "TOMATO": tom, "CARROT": 0}


def carrot_quota_unreal(V):
    if V.day not in UNREAL_CAR_CURVE:
        return 0
    total = UNREAL_CAR_TOTAL[min(3, _buyers(V.shops[:4], "CARROT"))]
    return int(round(UNREAL_CAR_CURVE[V.day] * total / 66.0))


def choose_crop_unreal(V, S, p, work, tg):
    day = V.day
    if day >= 28:
        return None
    if day <= 1:
        c = S["cfg"]["opening"].get(p)
        return c if c in CROPS else None
    if work.get("STRAWBERRY", 0) < tg["STRAWBERRY"] and day <= 15:
        return "STRAWBERRY"
    if day <= 5:
        return "WHEAT"
    if tg["TOMATO"] and 16 <= day <= 20 and work.get("TOMATO", 0) < tg["TOMATO"]:
        return "TOMATO"
    if day >= 11 and S.get("_car_today", 0) < carrot_quota_unreal(V):
        S["_car_today"] = S.get("_car_today", 0) + 1
        return "CARROT"
    if day <= 26:
        return "WHEAT"
    if day <= 27:
        return "CARROT"
    return None


def targets(V, S):
    cfg = S["cfg"]
    if cfg.get("target_mode") == "unreal":
        return targets_unreal(V, S)
    shops = V.shops
    et = cfg.get("early_targets")
    if et and V.day <= cfg["early_until"]:
        cur = None
        for d in sorted(et, key=int):
            if int(d) <= V.day:
                cur = et[d]
        c, sh, go, st = cur
        return {"SHEEP": sh, "COW": c, "GOOSE": go, "STRAWBERRY": st, "TOMATO": 0, "CARROT": 0}
    ft = cfg.get("fixed_targets")
    if ft and V.day >= 6:
        return dict(ft)
    if cfg.get("target_mode") == "decem" and V.day >= cfg["decem_from"]:
        # DECEM-style: every product scaled by the open shops' appetite (single-product shops count twice)
        d = {}
        for s_ in shops:
            items = SHOPS.get(s_, [])
            for it in items:
                d[it] = d.get(it, 0) + (2 if len(items) == 1 else 1)
        k = cfg["decem_k"]
        return {"SHEEP": min(k["sheep_max"], k["sheep0"] + k["sheep1"] * d.get("WOOL", 0)),
                "COW": min(k["cow_max"], k["cow0"] + k["cow1"] * d.get("MILK", 0)),
                "GOOSE": min(k["goose_max"], k["goose0"] + k["goose1"] * d.get("EGG", 0)),
                "STRAWBERRY": k["straw0"] + k["straw1"] * d.get("STRAWBERRY", 0),
                "TOMATO": (k["tom1"] * d.get("TOMATO", 0) if d.get("TOMATO", 0) >= k["tom_min"] else 0),
                "CARROT": k["car0"] + k["car1"] * d.get("CARROT", 0)}
    if V.day < 6:
        extra = cfg["early_cows"] if V.day >= cfg["early_cows_day"] else 0
        return {"SHEEP": cfg["sheep_d0"], "COW": cfg["cows_d0"] + extra, "GOOSE": cfg["geese_d0"],
                "STRAWBERRY": 0, "TOMATO": 0, "CARROT": 0}
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


def owned_animals(V):
    c = {}
    for k in ANIMALS:
        c[k] = V.shed.get(k, 0) + sum(inv.get(k, 0) for inv in V.invs)
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
    ops, _ = plant_ops(t, day, S, V, None, planning=True)
    return ("HARVEST" in ops and not CROPS[t["crop"]]["ongoing"]) or "DIG" in ops


LAST_PLANT = {"WHEAT": 26, "CARROT": 27, "TOMATO": 20, "STRAWBERRY": 17, "MELON": 1}


def choose_crop(V, S, p, work, tg):
    if S["cfg"].get("target_mode") == "unreal":
        return choose_crop_unreal(V, S, p, work, tg)
    day = V.day
    cfg = S["cfg"]
    if day >= 28:
        return None
    if day <= 1:
        c = cfg["opening"].get(p)
        return c if c in CROPS else None
    if cfg.get("early_targets") and day <= cfg["early_until"]:
        if day >= 2 and work.get("STRAWBERRY", 0) < tg["STRAWBERRY"]:
            return "STRAWBERRY"
        return "WHEAT"
    if day < 6:
        if 2 <= day <= 4 and work.get("STRAWBERRY", 0) < cfg["straw_early"]:
            return "STRAWBERRY"
        return "WHEAT"
    na = work.get("COW", 0) + work.get("SHEEP", 0) + work.get("GOOSE", 0) + S.get("pending_animals", 0)
    wheat_feed = int(math.ceil(na * cfg["wheat_per_animal"]))
    if day <= LAST_PLANT["WHEAT"] and work.get("WHEAT", 0) < wheat_feed:
        return "WHEAT"
    if day <= cfg["straw_last"] and work.get("STRAWBERRY", 0) < tg["STRAWBERRY"]:
        return "STRAWBERRY"
    if cfg["tom_first"] <= day <= cfg["tom_last"] and work.get("TOMATO", 0) < tg["TOMATO"]:
        return "TOMATO"
    if day >= cfg["car_first"] and work.get("CARROT", 0) < tg["CARROT"] * (cfg["car_early_frac"] if day < 19 else 1.0):
        return "CARROT"
    if day <= 26:
        return "WHEAT"
    if day <= 27:
        return "CARROT"
    return None


def _orc_done(t, use, d0):
    """True when the tile already carries the event's crop or animal, set on or after the event day."""
    if not isinstance(t, dict):
        return False
    if t.get("crop") == use:
        return int(t.get("planted_day", -9)) >= d0
    if t.get("animal") == use:
        return int(t.get("placed_day", -9)) >= d0
    return False


def oracle_uses(V, S, orc):
    """Oracle test (9/28): today's plantings and placements come from a recorded plan (tile -> crop or animal);
    only tiles that are free (or freed today) are used, and seeds/animals not in stock are bought. With oracle_backlog
    > 0, events whose tile was not ready stay pending for that many days (unless a newer event takes the tile)."""
    tu = {}
    buys = {"animals": {}, "seeds": {}}
    seeds = dict(V.seeds)
    own = owned_animals(V)
    ev = [(V.day, x, y, u) for x, y, u in (orc.get(str(V.day)) or orc.get(V.day) or [])]
    back = S["cfg"].get("oracle_backlog", 0)
    if back:
        if S.get("orc_day") != V.day:
            today = {(int(x), int(y)) for _, x, y, _ in ev}
            keep = [e for e in S.get("orc_pending", [])
                    if V.day - e[0] <= back and (int(e[1]), int(e[2])) not in today
                    and not _orc_done(V.tile((int(e[1]), int(e[2]))), e[3], e[0])]
            S["orc_pending"] = keep + ev
            S["orc_day"] = V.day
        ev = list(S["orc_pending"])
    for d0, x, y, use in ev:
        p = (int(x), int(y))
        if not V.owned(p):
            continue
        t = V.tile(p)
        if _orc_done(t, use, d0):
            continue
        free = t is None or (isinstance(t, dict) and t.get("kind") == "WEED") or \
            (isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and not t.get("animal")) or \
            (isinstance(t, dict) and t.get("kind") == "PLANT" and freeing_today(t, V.day, S, V))
        if not free:
            continue
        tu[p] = use
        if use in ANIMALS:
            if own.get(use, 0) > 0:
                own[use] -= 1
            else:
                buys["animals"][use] = buys["animals"].get(use, 0) + 1
        elif seeds.get(use, 0) > 0:
            seeds[use] -= 1
        else:
            buys["seeds"][use] = buys["seeds"].get(use, 0) + 1
    S["tg"] = {}
    S["pending_animals"] = sum(1 for u in tu.values() if u in ANIMALS)
    return tu, buys


def plan_uses(V, S, budget, allow_buy=True):
    """Decide tile uses for today given a cash budget. Returns (tile_use, buys) where buys lists animals/seeds."""
    if S["cfg"].get("oracle") is not None:
        return oracle_uses(V, S, S["cfg"]["oracle"])
    tu = {}
    day = V.day
    cnt = count_uses(V)
    tg = targets(V, S)
    S["tg"] = tg
    own = owned_animals(V)
    buys = {"animals": {}, "seeds": {}}
    if S["cfg"]["opening_wheat_first"] and day <= 1 and allow_buy:
        # the opening's wheat tiles first: 10 a seed, harvested on day 2-3 for feed and cash
        free_w = V.seeds.get("WHEAT", 0)
        for p, u in sorted(S["cfg"]["opening"].items()):
            if u != "WHEAT" or V.tile(p) is not None:
                continue
            if free_w > 0:
                free_w -= 1
            elif budget >= CROPS["WHEAT"]["seed"]:
                budget -= CROPS["WHEAT"]["seed"]
                buys["seeds"]["WHEAT"] = buys["seeds"].get("WHEAT", 0) + 1
            else:
                break
            tu[p] = "WHEAT"
    want = []
    for k in S["cfg"]["animal_order"]:
        spare = own.get(k, 0)
        n = max(0, int(round(tg[k])) - cnt.get(k, 0) - spare) if (day <= S["cfg"]["animal_last_day"] and allow_buy) else 0
        want += [(k, True)] * spare + [(k, False)] * n
    slots = animal_slots(V)
    if S["cfg"]["opening_style"] == "race":
        marks = [p for p, u in S["cfg"]["opening"].items() if u == "ANIMAL"]
        slots = marks + [p for p in slots if p not in marks and S["cfg"]["opening"].get(p) != "MELON"]
    si = 0
    feedc = 2 * max(20, V.prices.get("WHEAT", 25) + 2)
    for k, owned in want:
        if not owned and budget < ANIMALS[k]["cost"] + feedc:
            continue
        placed = False
        while si < len(slots):
            p = slots[si]
            si += 1
            maxd = S["cfg"]["animal_max_dist"] if len(V.quads) > 1 else 8
            if shed_dist(p) > maxd and S["cfg"]["opening"].get(p) != "ANIMAL":
                continue
            t = V.tile(p)
            ok = t is None or (isinstance(t, dict) and t.get("kind") == "WEED") or \
                (isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and not t.get("animal"))
            if isinstance(t, dict) and t.get("kind") == "PLANT" and day >= S["cfg"]["free_slot_day"] and freeing_today(t, day, S, V):
                ok = True
            if ok:
                tu[p] = k
                placed = True
                break
        if placed and not owned:
            budget -= ANIMALS[k]["cost"] + feedc
            buys["animals"][k] = buys["animals"].get(k, 0) + 1
    # crops
    work = dict(cnt)
    S["pending_animals"] = sum(1 for u in tu.values() if u in ANIMALS)
    seeds = dict(V.seeds)
    cand = []
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
                cand.append(p)
    # nearer tiles first so the cheapest-to-reach land is used when cash is short
    cand.sort(key=lambda p: shed_dist(p))
    S["_car_today"] = sum(1 for row in V.tiles for t in row if isinstance(t, dict) and t.get("crop") == "CARROT"
                          and int(t.get("planted_day", -1)) == day)
    picks = []
    for p in cand:
        c = choose_crop(V, S, p, work, tg)
        if not c or day > LAST_PLANT[c]:
            continue
        if seeds.get(c, 0) > 0:
            seeds[c] -= 1
        else:
            cost = CROPS[c]["seed"]
            if not allow_buy or budget < cost:
                # fall back to wheat when a pricier crop is unaffordable
                if c != "WHEAT" and allow_buy and budget >= CROPS["WHEAT"]["seed"] and day <= LAST_PLANT["WHEAT"]:
                    c = "WHEAT"
                    cost = 10
                else:
                    continue
            budget -= cost
            buys["seeds"][c] = buys["seeds"].get(c, 0) + 1
        picks.append((p, c))
        work[c] = work.get(c, 0) + 1
    if S["cfg"].get("premium_near") and day >= 2 and len(picks) > 1:
        # p6: from day 2 the crop choice does not depend on the tile, so give the long-lived, must-water premium
        # crops the tiles nearest the shed; routes run near-to-far and lose their far tail when they overrun
        rank = {"STRAWBERRY": 0, "TOMATO": 1, "MELON": 2, "CARROT": 3, "WHEAT": 4}
        tiles_ = [p for p, _ in picks]
        crops_ = sorted((c for _, c in picks), key=lambda c: rank.get(c, 5))
        picks = list(zip(tiles_, crops_))
    for p, c in picks:
        tu[p] = c
    return tu, buys


# ============================================================================= jobs
CROP_UNITS = {"WHEAT": 5, "CARROT": 3, "MELON": 6, "TOMATO": 8, "STRAWBERRY": 8}


def job_value(j, V, S=None, t=None):
    """Approximate dollars lost if the visit is skipped today."""
    k = j["kind"]
    P = V.prices
    fp = P.get("FERTILIZER", 50)
    if k == "animal":
        if j.get("urg", 0) >= 2:
            return 3000
        a = ANIMALS[j["animal"]]
        pp = P.get(a["product"], 50)
        v = 0.0
        if "FEED" in j["ops"] or "CARE" in j["ops"]:
            v += pp
            if t is not None:
                dsf = V.day + 1 - t.get("placed_day", 0) - a["first"]
                if dsf >= 0 and dsf % a["interval"] == 0:
                    v += pp * t.get("pending_care_bonus", 0)
        if "COLLECT_FERTILIZER" in j["ops"]:
            v += fp
        if "HARVEST" in j["ops"] and t is not None:
            if V.day >= LAST_DAY:
                v += pp * t.get("yield_units", 0)
            elif t.get("yield_units", 0) >= a["maxheld"] - 1:
                v += pp
        return 100 + v
    if k == "place":
        return 900
    if k == "crop":
        c = j["crop"]
        pp = P.get(c, BASE[c])
        if j.get("urg", 0) >= 2:
            return 1200 + CROP_UNITS[c] * pp
        v = 60.0
        if "HARVEST" in j["ops"]:
            if c in ("TOMATO", "STRAWBERRY"):
                v += 3 * pp
            else:
                age = V.day - t["planted_day"] if t is not None else 0
                late = t is not None and age >= CROPS[c]["maxday"]
                v += (1.0 if late else 0.4) * CROP_UNITS[c] * pp
        if "FERTILIZE" in j["ops"]:
            v += 2 * pp - fp
        if "WATER" in j["ops"] and c in ("WHEAT", "CARROT", "MELON"):
            v += pp
        if "PLANT" in j["ops"]:
            v += 40
        return v
    if k == "plant":
        c = j.get("plant")
        return 40 + (30 if c in ("STRAWBERRY", "TOMATO") else 0)
    return 5


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
                ops, urg = plant_ops(t, day, S, V, None, planning=True)
                if ops:
                    j = {"pos": p, "ops": list(ops), "urg": urg, "kind": "crop", "crop": t["crop"]}
                    if ("HARVEST" in ops and not CROPS[t["crop"]]["ongoing"]) or "DIG" in ops:
                        if use in CROPS:
                            j["ops"] += ["PLANT", "WATER"]
                            j["plant"] = use
                        elif use in ANIMALS:
                            j["ops"] += ["BUILD", "PLACE"] + (["FEED", "CARE"] if S["cfg"]["place_feed"] else [])
                            j["place"] = use
            elif isinstance(t, dict) and t.get("animal"):
                ops, urg = animal_ops(t, day, S, V, None, planning=True)
                if ops:
                    j = {"pos": p, "ops": list(ops), "urg": urg, "kind": "animal", "animal": t["animal"]}
            else:
                weed = isinstance(t, dict) and t.get("kind") == "WEED"
                struct = isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE")
                if use is None:
                    if weed and day <= 26 and S["cfg"]["dig_weeds"]:
                        j = {"pos": p, "ops": ["DIG"], "urg": 0, "kind": "weed"}
                elif use in CROPS:
                    ops = (["DIG"] if weed or struct else []) + ["PLANT", "WATER"]
                    j = {"pos": p, "ops": ops, "urg": 0, "kind": "plant", "plant": use}
                elif use in ANIMALS:
                    ops = []
                    if weed or (struct and t.get("kind") != ANIMALS[use]["struct"]):
                        ops.append("DIG")
                    if not (struct and t.get("kind") == ANIMALS[use]["struct"]):
                        ops.append("BUILD")
                    ops.append("PLACE")
                    if S["cfg"]["place_feed"] and day < LAST_DAY:
                        ops += ["FEED", "CARE"]
                    j = {"pos": p, "ops": ops, "urg": 0, "kind": "place", "place": use}
            if j:
                j["value"] = job_value(j, V, S, t if isinstance(t, dict) else None)
                jobs.append(j)
    return jobs


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


# ============================================================================= routing
def mk_shed_stop(pos, drop=False, pickup=None):
    return {"pos": pos, "kind": "shed", "drop": drop, "pickup": dict(pickup or {}), "job": {"ops": [], "kind": "shed"}}


def nearest_shed(pos):
    return min(SHED_TILES, key=lambda s: (dist(pos, s), SHED_TILES.index(s)))


def nn_order(start, jobs, end=None):
    if not jobs:
        return []
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
    return path


def build_route(V, S, start, jobs, mid_drop=False):
    phase_a = [j for j in jobs if j["kind"] in ("animal", "place")]
    phase_b = [j for j in jobs if j["kind"] not in ("animal", "place")]
    load = sum(job_load(j) for j in jobs)
    close = (load >= S["cfg"]["drop_load"] and S["cfg"]["drop_mode"] != "smart") or (V.day >= LAST_DAY and S["cfg"]["endgame"])
    pa = nn_order(start, phase_a)
    stops = [{"pos": j["pos"], "kind": "tile", "job": j} for j in pa]
    cur = pa[-1]["pos"] if pa else start
    if pa and phase_b and mid_drop:
        stops.append(mk_shed_stop(nearest_shed(cur), drop=True))
        cur = stops[-1]["pos"]
    elif pa and S["cfg"].get("place_mid") and any("HARVEST" in j["ops"] for j in pa) \
            and shed_dist(cur) <= S["cfg"].get("place_detour", 2):
        # p6 (9/28): animal products go to the shed right after the animal round, so they sell the same day
        st_ = mk_shed_stop(nearest_shed(cur))
        st_["place_only"] = True
        stops.append(st_)
        cur = st_["pos"]
    endp = None
    if phase_b:
        if close:
            cx = sum(j["pos"][0] for j in phase_b) / len(phase_b)
            cy = sum(j["pos"][1] for j in phase_b) / len(phase_b)
            endp = nearest_shed((int(round(cx)), int(round(cy))))
        pb = nn_order(cur, phase_b, end=endp)
        stops += [{"pos": j["pos"], "kind": "tile", "job": j} for j in pb]
    if stops and close:
        stops.append(mk_shed_stop(endp or nearest_shed(stops[-1]["pos"]), drop=True))
    elif stops and S["cfg"].get("place_end") and phase_b and \
            any("HARVEST" in j["ops"] and j.get("crop") in ("STRAWBERRY", "TOMATO", "MELON") for j in phase_b) and \
            shed_dist(stops[-1]["pos"]) <= S["cfg"].get("place_detour", 2):
        st_ = mk_shed_stop(nearest_shed(stops[-1]["pos"]))
        st_["place_only"] = True
        stops.append(st_)
    return stops


def stop_ops(st):
    return max(1, len(st["job"]["ops"])) if st["kind"] == "tile" else 1


def route_cost(start, stops):
    c = start
    t = 1.0 if stops else 0.0
    for st in stops:
        t += dist(c, st["pos"]) + stop_ops(st)
        c = st["pos"]
    return t


def route_plan(V, S, units, jobs, mid_drop=None):
    if not units:
        return {}
    if S["cfg"]["router"] == "split" and V.day >= S["cfg"]["split_from"]:
        return route_plan_split(V, S, units, jobs)
    if mid_drop is None:
        mid_drop = V.day < S["cfg"]["mid_drop_until"]
    endh = 22.5 if (V.day >= LAST_DAY and S["cfg"]["endgame"]) else 24
    caps = {i: max(0.5, (endh - h - 0.5) * S["cfg"]["cap_frac"]) for i, _, h in units}
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
    if S["cfg"]["route_ls"]:
        improve_routes(routes, starts, caps)
    fit_capacity(routes, starts, caps)
    if S["cfg"]["drop_mode"] == "smart" and V.day < LAST_DAY:
        smart_drops(V, S, routes, starts, caps)
    return routes


def two_opt_path(start, path, end=None, iters=40):
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
    n = len(path)
    while improved and it < iters:
        improved = False
        it += 1
        for a_ in range(n - 1):
            for b_ in range(a_ + 1, n):
                newp = path[:a_] + path[a_:b_ + 1][::-1] + path[b_ + 1:]
                L = plen(newp)
                if L < best:
                    path, best = newp, L
                    improved = True
        # or-opt: move single job elsewhere
        for a_ in range(n):
            j = path[a_]
            rest = path[:a_] + path[a_ + 1:]
            for b_ in range(len(rest) + 1):
                if b_ == a_:
                    continue
                newp = rest[:b_] + [j] + rest[b_:]
                L = plen(newp)
                if L < best:
                    path, best = newp, L
                    improved = True
                    break
    return path


def route_plan_split(V, S, units, jobs):
    """Giant tour over all jobs from the shed, split into contiguous segments balanced by unit capacity."""
    if not units:
        return {}
    endh = 22.5 if (V.day >= LAST_DAY and S["cfg"]["endgame"]) else 24
    caps = {i: max(0.5, endh - h - 0.5) for i, _, h in units}
    starts = {i: p for i, p, _ in units}
    if not jobs:
        return {i: [] for i, _, _ in units}
    for j in jobs:
        j["cost"] = len(j["ops"]) + 1.5
    hub = (4, 4)
    tour = nn_order(hub, jobs, end=hub)
    tour = two_opt_path(hub, tour, end=hub)
    n = len(units)
    # try several rotations of the closed tour; split greedily by capacity (incl. access from the shed)
    order_units = sorted(units, key=lambda u: (u[2], SHED_TILES.index(u[1]) if u[1] in SHED_TILES else 9))
    best = None
    L = len(tour)
    rots = range(0, L, max(1, L // 12))
    for r0 in rots:
        tr = tour[r0:] + tour[:r0]
        segs = []
        k = 0
        cur = []
        acc = 0.0
        prev = None
        total_cap = sum(caps[u[0]] for u in order_units)
        tot_cost = sum(dist(tr[i - 1]["pos"], tr[i]["pos"]) + len(tr[i]["ops"]) for i in range(1, len(tr))) + 8.0 * n
        for j in tr:
            if k >= n:
                break
            u = order_units[k]
            add = (len(j["ops"]) + (dist(prev, j["pos"]) if prev is not None and cur else dist(u[1], j["pos"]) + 1))
            share = caps[u[0]] * min(1.0, tot_cost / max(1.0, total_cap)) * 1.02
            if cur and acc + add > share and k < n - 1:
                segs.append(cur)
                k += 1
                u = order_units[k]
                cur, acc, prev = [], 0.0, None
                add = len(j["ops"]) + dist(u[1], j["pos"]) + 1
            cur.append(j)
            acc += add
            prev = j["pos"]
        segs.append(cur)
        while len(segs) < n:
            segs.append([])
        cost = 0.0
        for u, sg in zip(order_units, segs):
            c = route_cost(u[1], [{"pos": jj["pos"], "kind": "tile", "job": jj} for jj in sg])
            cost += max(0.0, c - caps[u[0]]) * 20 + c
        if best is None or cost < best[0]:
            best = (cost, segs)
    routes = {}
    for u, sg in zip(order_units, best[1]):
        # orient the segment: start from the end closer to the unit's start
        if sg and dist(u[1], sg[-1]["pos"]) < dist(u[1], sg[0]["pos"]):
            sg = sg[::-1]
        stops = [{"pos": j["pos"], "kind": "tile", "job": j} for j in sg]
        load = sum(job_load(j) for j in sg)
        if stops and (load >= S["cfg"]["drop_load"] or (V.day >= LAST_DAY and S["cfg"]["endgame"])):
            stops.append(mk_shed_stop(nearest_shed(stops[-1]["pos"]), drop=True))
        routes[u[0]] = stops
    fit_capacity(routes, starts, caps)
    return routes


def rescue_reorder(V, S):
    """If a route cannot finish today, move its must-do stops (crops that die tonight, unfed animals) to the front."""
    left = 23 - V.hour
    for i in range(len(V.units)):
        r = S["routes"].get(i, [])
        if not r:
            continue
        pos = V.units[i]
        if route_cost(pos, r) <= left:
            continue
        urgent = [st for st in r if st["kind"] == "tile" and st["job"].get("value", 0) >= 1200]
        if not urgent:
            continue
        rest = [st for st in r if not (st["kind"] == "tile" and st["job"].get("value", 0) >= 1200)]
        # keep a leading shed pickup first
        head = []
        while rest and rest[0]["kind"] == "shed" and rest[0].get("pickup"):
            head.append(rest.pop(0))
        jobs_u = nn_order(pos, [st["job"] for st in urgent])
        ordered = [st for j in jobs_u for st in urgent if st["job"] is j]
        S["routes"][i] = head + ordered + rest


def _route_times(pos, r):
    """Completion time (turns from now) of each stop."""
    out = []
    t = 0
    for st in r:
        t += dist(pos, st["pos"]) + stop_ops(st)
        out.append(t)
        pos = st["pos"]
    return out


def rescue_targeted(V, S):
    """Move urgent stops that would finish after the day ends to a route position where they finish in time."""
    left = 24 - V.hour
    n = len(V.units)
    late = []
    for i in range(n):
        r = S["routes"].get(i, [])
        if not r:
            continue
        times = _route_times(V.units[i], r)
        for k in range(len(r) - 1, -1, -1):
            st = r[k]
            if st["kind"] == "tile" and st["job"].get("value", 0) >= 1200 and times[k] > left:
                late.append(r.pop(k))
    if not late:
        return
    late.sort(key=lambda st: -st["job"].get("value", 0))
    for st in late:
        best = None
        for j in range(n):
            r = S["routes"].setdefault(j, [])
            pos = V.units[j]
            times = _route_times(pos, r)
            prev = pos
            tprev = 0
            k_min = 1 if (r and r[0]["kind"] == "tile" and r[0]["pos"] == pos) else 0
            for k in range(len(r) + 1):
                if k < k_min:
                    tprev = times[0]
                    prev = r[0]["pos"]
                    continue
                arrive = tprev + dist(prev, st["pos"]) + stop_ops(st)
                if arrive <= left:
                    nxt = r[k]["pos"] if k < len(r) else None
                    add = dist(prev, st["pos"]) + stop_ops(st) + (dist(st["pos"], nxt) - dist(prev, nxt) if nxt else 0)
                    # penalty if this pushes other urgent stops late
                    pen = 0
                    for kk in range(k, len(r)):
                        if r[kk]["kind"] == "tile" and r[kk]["job"].get("value", 0) >= 1200 and times[kk] + add > left:
                            pen += 1000
                    sc = add + pen
                    if best is None or sc < best[0]:
                        best = (sc, j, k)
                if k < len(r):
                    tprev = times[k]
                    prev = r[k]["pos"]
        if best is None:
            j = min(range(n), key=lambda j: dist(V.units[j], st["pos"]))
            rj = S["routes"].setdefault(j, [])
            k0 = 1 if (rj and rj[0]["kind"] == "tile" and rj[0]["pos"] == V.units[j]) else 0
            rj.insert(k0, st)
        else:
            S["routes"][best[1]].insert(best[2], st)


def eod_drops(V, S):
    """Evening: if tonight's auto-drop would overflow the shed, send loaded units near the shed to drop now."""
    carried = [sum(inv.values()) if i < len(V.invs) else 0 for i, inv in enumerate(V.invs[:len(V.units)])]
    shed_keep = sum(V.shed.get(k, 0) for k in ("WHEAT", "FERTILIZER")) + sum(V.shed.get(k, 0) for k in ANIMALS)
    growth = 2 * len(V.units) * max(0, 23 - V.hour) // 6
    total = sum(carried) + shed_keep + growth
    room = S["cfg"]["shed_cap"] - S["cfg"]["drop_margin"]
    if total <= room:
        return
    cand = []
    for i in range(len(V.units)):
        r = S["routes"].get(i, [])
        if r and r[0]["kind"] == "shed" and r[0].get("drop"):
            total -= carried[i]
            continue
        d = shed_dist(V.units[i])
        if carried[i] <= 0 or d + 1 > 23 - V.hour:
            continue
        cand.append((d / carried[i], i, d))
    cand.sort()
    for _, i, d in cand:
        if total <= room:
            break
        r = S["routes"].setdefault(i, [])
        k0 = 1 if (r and r[0]["kind"] == "tile" and r[0]["pos"] == V.units[i]) else 0
        r.insert(k0, mk_shed_stop(nearest_shed(r[0]["pos"] if k0 else V.units[i]), drop=True))
        total -= carried[i]


def smart_drops(V, S, routes, starts, caps):
    """Add end-of-route shed drops only where needed so tonight's carried goods fit the shed."""
    feed_tom = feed_counts(V, S)[1]
    room = S["cfg"]["shed_cap"] - S["cfg"]["drop_margin"] - max(0, feed_tom - 5)
    cand = []
    total = 0
    for i, r in routes.items():
        load = sum(job_load(st["job"]) for st in r if st["kind"] == "tile")
        load += sum((V.invs[i] if i < len(V.invs) else {}).values()) if i < len(V.invs) else 0
        total += load
        if not r or r[-1]["kind"] == "shed":
            continue
        end = r[-1]["pos"]
        det = shed_dist(end) + 1
        slack = caps[i] - route_cost(starts[i], r)
        cand.append((det / max(1, load), det, load, i, slack))
    cand.sort()
    for _, det, load, i, slack in cand:
        if total <= room:
            break
        if load <= 0:
            continue
        r = routes[i]
        r.append(mk_shed_stop(nearest_shed(r[-1]["pos"]), drop=True))
        total -= load


def improve_routes(routes, starts, caps, passes=8, pen=50.0):
    """Multi-route local search: relocate stops between/within routes and 2-opt, minimizing walking
    plus a penalty for exceeding each unit's time cap. Only routes made of tile stops are touched."""
    ids = [i for i in routes if all(st["kind"] == "tile" for st in routes[i])]
    if len(ids) < 1:
        return
    R = {i: routes[i] for i in ids}

    def rcost(i):
        return route_cost(starts[i], R[i])

    cost = {i: rcost(i) for i in ids}

    def over(i, c):
        return max(0.0, c - caps[i])

    def pos_at(i, k):
        return starts[i] if k < 0 else R[i][k]["pos"]

    for _ in range(passes):
        improved = False
        for a in ids:
            k = 0
            while k < len(R[a]):
                st = R[a][k]
                pa = pos_at(a, k - 1)
                na = R[a][k + 1]["pos"] if k + 1 < len(R[a]) else None
                ops = stop_ops(st)
                rem = dist(pa, st["pos"]) + ops + ((dist(st["pos"], na) - dist(pa, na)) if na else 0)
                if len(R[a]) == 1:
                    rem += 1.0  # the pickup turn disappears with the route
                base_a = cost[a] - rem
                best = None
                for b in ids:
                    rb = R[b]
                    nb_ = len(rb)
                    for q in range(nb_ + 1):
                        if b == a and (q == k or q == k + 1):
                            continue
                        if b == a:
                            # positions refer to the list without st
                            lst = rb[:k] + rb[k + 1:]
                            qq = q if q < k else q - 1
                            prev = starts[b] if qq == 0 else lst[qq - 1]["pos"]
                            nxt = lst[qq]["pos"] if qq < len(lst) else None
                        else:
                            prev = starts[b] if q == 0 else rb[q - 1]["pos"]
                            nxt = rb[q]["pos"] if q < nb_ else None
                        add = dist(prev, st["pos"]) + ops + ((dist(st["pos"], nxt) - dist(prev, nxt)) if nxt else 0)
                        if b != a and nb_ == 0:
                            add += 1.0
                        if b == a:
                            new_a = base_a + add
                            delta = (new_a - cost[a]) + pen * (over(a, new_a) - over(a, cost[a]))
                        else:
                            new_b = cost[b] + add
                            delta = (base_a - cost[a]) + (new_b - cost[b]) + pen * (
                                over(a, base_a) - over(a, cost[a]) + over(b, new_b) - over(b, cost[b]))
                        if delta < -0.01 and (best is None or delta < best[0]):
                            best = (delta, b, q)
                if best:
                    _, b, q = best
                    R[a].pop(k)
                    if b == a:
                        qq = q if q < k else q - 1
                        R[a].insert(qq, st)
                    else:
                        R[b].insert(q, st)
                    cost[a] = rcost(a)
                    cost[b] = rcost(b)
                    improved = True
                    continue
                k += 1
        for i in ids:
            if len(R[i]) > 2:
                jobs = [st["job"] for st in R[i]]
                path = two_opt_path(starts[i], jobs, iters=10)
                m = {id(st["job"]): st for st in R[i]}
                R[i] = [m[id(j)] for j in path]
                cost[i] = rcost(i)
        if not improved:
            break
    for i in ids:
        routes[i] = R[i]


def fit_capacity(routes, starts, caps):
    removed = []
    for i, r in routes.items():
        while route_cost(starts[i], r) > caps[i]:
            cand = [k for k, st in enumerate(r) if st["kind"] == "tile" and st["job"]["value"] < 1200]
            if not cand:
                break
            k = min(cand, key=lambda k: (r[k]["job"]["value"] / (stop_ops(r[k]) + 1.5), -k))
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
                if k < len(r):
                    prev = r[k]["pos"]
        if best:
            routes[best[1]].insert(best[2], st)


def add_supplies(V, S, routes, starts):
    for i, r in routes.items():
        if not r:
            continue
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


def _live_ops_core(V, S, i, pos, inv, seed_left, stop, shed_now):
    if stop["kind"] == "shed" and stop.get("place_only"):
        room = S["cfg"]["shed_cap"] - sum(shed_now.values())
        for item in PREMIUM_PLACE:
            n = int(inv.get(item, 0))
            if n > 0 and room > 0:
                return [["PLACE", item, min(n, room)]]
        return []
    if stop["kind"] == "shed":
        ops = []
        if not stop.get("drop") and any(inv.get(k, 0) > 0 for k in SELLABLE):
            stop["drop"] = True
        if stop.get("drop") and not stop.get("_dropped"):
            if any(v > 0 for v in inv.values()):
                ops.append(["DROP"])
            else:
                stop["_dropped"] = True
        wait = False
        for item, n in stop.get("pickup", {}).items():
            have = 0 if (stop.get("drop") and not stop.get("_dropped")) else inv.get(item, 0)
            need = n - have
            avail = shed_now.get(item, 0)
            if need > 0 and avail > 0:
                ops.append(["PICKUP", item, int(min(need, avail))])
            elif need > 0 and item in ANIMALS and (S.get("buys") or {}).get("animals", {}).get(item, 0) > 0                     and not stop.get("_waited"):
                wait = True
        if not ops and wait:
            stop["_waited"] = True
            return [["PASS"]]
        return ops
    t = V.tile(pos)
    day = V.day
    use = S["tile_use"].get(pos)
    job = stop["job"]
    if t == "LOCKED":
        return []
    if job.get("race"):
        if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON":
            out = []
            if "WATER" in job["ops"] and not t.get("watered_today") and t.get("yield_units", 0) < 6:
                out.append(["WATER"])
            if t.get("yield_units", 0) > 0 and day - t["planted_day"] >= 10:
                out.append(["HARVEST"])
            return out
        return []
    if t is None:
        if use in CROPS:
            if V.hour >= 23:
                return []
            return [["PLANT", use]] if seed_left.get(use, 0) > 0 else []
        if use in ANIMALS and inv.get(use, 0) > 0:
            return [["BUILD_" + ANIMALS[use]["struct"]]]
        return []
    kind = t.get("kind")
    if kind == "WEED":
        if use is not None or job.get("kind") == "weed":
            if use in ANIMALS and inv.get(use, 0) <= 0:
                return []
            if use in CROPS and seed_left.get(use, 0) <= 0 and job.get("kind") != "weed":
                return []
            return [["DIG"]]
        return []
    if job.get("race"):
        if kind == "PLANT" and t.get("crop") == "MELON":
            out = []
            if "WATER" in job["ops"] and not t.get("watered_today") and t.get("yield_units", 0) < 6:
                out.append(["WATER"])
            if t.get("yield_units", 0) > 0 and day - t["planted_day"] >= 10:
                out.append(["HARVEST"])
            return out
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
            if use in CROPS and seed_left.get(use, 0) > 0:
                return [["DIG"]]
            return []
        ops, _ = animal_ops(t, day, S, V, inv, planning=False)
        return [[o] for o in ops]
    return []


PLACE_ITEMS = ("MILK", "WOOL", "STRAWBERRY", "MELON", "EGG", "TOMATO", "CARROT", "FERTILIZER")
PREMIUM_PLACE = ("MELON", "WOOL", "MILK", "STRAWBERRY", "TOMATO", "EGG", "CARROT")


def live_ops(V, S, i, pos, inv, seed_left, stop, shed_now):
    ops = _live_ops_core(V, S, i, pos, inv, seed_left, stop, shed_now)
    if ops or stop["kind"] != "tile" or pos not in SHED_TILES or not S["cfg"]["shed_place"]:
        return ops
    if stop.get("_placed", 0) >= 3 or sum(shed_now.values()) >= S["cfg"]["shed_cap"] - 5 or V.hour >= 23:
        return ops
    best = None
    for it in PLACE_ITEMS:
        n = inv.get(it, 0)
        if it == "FERTILIZER":
            n -= sum(1 for st in S["routes"].get(i, []) for op in st["job"].get("ops", []) if op == "FERTILIZE")
        if n <= 0:
            continue
        val = n * V.prices.get(it, 0)
        if val >= S["cfg"]["shed_place_min"] and (best is None or val > best[0]):
            best = (val, it, n)
    if best:
        stop["_placed"] = stop.get("_placed", 0) + 1
        return [["PLACE", best[1], int(best[2])]]
    return ops


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
                for k2, v in inv.items():
                    shed_now[k2] = shed_now.get(k2, 0) + v
            elif op[0] == "PLACE" and len(op) >= 3 and op[1] not in ANIMALS:
                shed_now[op[1]] = shed_now.get(op[1], 0) + int(op[2])
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


def n_animals(V):
    return sum(1 for y in range(10) for x in range(10)
               if isinstance(V.tiles[y][x], dict) and V.tiles[y][x].get("animal"))


def hires_cost(k0, n):
    return sum(fib(k0 + i) for i in range(n))


def sell_plan(V, S, shed, last=False):
    """[(item, n)] to sell now from the (projected) shed, keeping reserves."""
    out = []
    psh = S["cfg"].get("premium_sell_hours")
    for item in PRODUCTS:
        have = shed.get(item, 0)
        if have <= 0:
            continue
        if psh and item in ("MILK", "WOOL", "STRAWBERRY") and V.hour not in psh and not last and V.day >= 10                 and V.hour < 22:
            continue
        keep = 0
        if not last:
            if item == "WHEAT":
                keep = wheat_hold(V, S)
            elif item == "FERTILIZER":
                keep = fert_hold(V, S)
        n = have - keep
        if n > 0:
            out.append([item, int(n)])
    return out


def sale_value(V, sells):
    inv = dict(V.minv)
    tot = 0
    for item, n in sells:
        for _ in range(n):
            p = price(item, inv.get(item, 10000))
            tot += p
            if p > 1:
                inv[item] = inv.get(item, 10000) + 1
    return tot


def feed_counts(V, S):
    """(unfed animals still worth feeding today, animals worth feeding tomorrow)."""
    today = tom = 0
    for y in range(10):
        for x in range(10):
            t = V.tiles[y][x]
            if isinstance(t, dict) and t.get("animal"):
                lf = last_feed_day(t, S)
                if V.day <= lf and not t.get("fed_today"):
                    today += 1
                if V.day + 1 <= lf:
                    tom += 1
    pend = sum(1 for u in S["tile_use"].values() if u in ANIMALS) if V.day < 27 else 0
    return today + pend, tom + pend


def wheat_hold(V, S):
    today, tom = feed_counts(V, S)
    carried = sum(inv.get("WHEAT", 0) for inv in V.invs)
    return max(0, today + tom - carried)


def fert_hold(V, S):
    if V.day >= 28:
        return 0
    n = 0
    for y in range(10):
        for x in range(10):
            t = V.tiles[y][x]
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                age = V.day - t["planted_day"]
                for d in (0, 1):
                    a = age + d
                    if a in FERT_AGES[t["crop"]] and wants_fert(t["crop"], a, V.day + d, S, V):
                        if d == 0 and t.get("fertilized_until_day", -1) >= V.day:
                            continue
                        n += 1
    carried = sum(inv.get("FERTILIZER", 0) for inv in V.invs)
    return max(0, n - carried)


def reserve_next(V, S):
    """Cash to keep for tomorrow morning (hires + feed), minus a share of expected income."""
    if V.day >= 28:
        return 0
    nh = max(S["cfg"]["hands_min"], S.get("want_hands", 4))
    need = n_animals(V) + sum(1 for u in S.get("tile_use", {}).values() if u in ANIMALS)
    have = V.shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in V.invs)
    feed = max(0, need - have) * max(20, V.prices.get("WHEAT", 25) + 2)
    return S["cfg"]["reserve_frac"] * (hires_cost(0, nh) + feed)


def day_plan(V, S):
    cfg = S["cfg"]
    shed = dict(V.shed)
    sells = sell_plan(V, S, shed)
    cash = V.money + sale_value(V, sells)
    # hires estimated from yesterday's layout workload; refined below
    S["tile_use"] = {}
    jobs0 = gen_jobs(V, S)
    wl0 = sum(len(j["ops"]) + 1.5 for j in jobs0)
    na = n_animals(V)
    feed_need = max(0, na - V.shed.get("WHEAT", 0))
    feed_cost = feed_need * (V.prices.get("WHEAT", 25) + 2)
    budget = cash - feed_cost - reserve_next(V, S)
    # land on schedule
    S["buy_land"] = False
    nq = len(V.quads)
    if nq < 4:
        cost = LAND_PRICES[nq - 1]
        if cfg["land_days"][nq - 1] <= V.day <= cfg["land_last"] and budget - hires_cost(V.hires_today, 8) >= cost:
            S["buy_land"] = True
            budget -= cost
    est_hands = min(cfg["max_hands"], max(cfg["hands_min"] if V.day < 10 else 0, int(math.ceil((wl0 + 25 - 20) / 20.0))))
    budget -= hires_cost(V.hires_today, est_hands)
    if S["buy_land"]:
        # plan uses as if the new quadrant is ours: handled by an event replan after the purchase
        pass
    tu, buys = plan_uses(V, S, max(0.0, budget))
    S["tile_use"] = tu
    S["buys"] = buys
    jobs = gen_jobs(V, S)
    wl = sum(len(j["ops"]) + 1.5 for j in jobs)
    nh = int(math.ceil(max(0.0, wl - 20) / 20.0))
    nh = max(nh, cfg["hands_min"] if V.day < 10 else 0)
    hf = cfg.get("hands_floor")
    if hf and V.day < len(hf):
        nh = max(nh, int(hf[V.day]))
    nh = min(nh, cfg["max_hands"])
    if V.day >= cfg["late_from"]:
        nh = min(nh, cfg["late_max_hands"])
    race = cfg["melon_race"] and any(
        isinstance(V.tiles[y][x], dict) and V.tiles[y][x].get("crop") == "MELON" and
        V.day - V.tiles[y][x]["planted_day"] >= 10 for y in range(10) for x in range(10))
    if race:
        nh = max(nh, cfg["race_hands"])
        S["race_day"] = V.day
    oh = cfg.get("oracle_hires")
    if oh:
        # oracle test: the tape's own hire count for the day, so routing is compared at equal labour
        nh = int(oh[V.day]) if V.day < len(oh) else nh
    S["want_hands"] = nh
    while True:
        exp = expected_spawns(V, max(0, nh - (len(V.units) - 1)), V.units[0])
        units = [(k, V.units[k], 0) for k in range(len(V.units))] + [(len(V.units) + k, p, 1) for k, p in enumerate(exp)]
        starts = {i: p for i, p, _ in units}
        if race:
            routes = race_routes(V, S, units, jobs)
        else:
            routes = route_plan(V, S, units, jobs)
        if nh >= cfg["max_hands_extra"] or race or oh or (V.day >= cfg["late_from"] and nh >= cfg["late_max_hands"]):
            break
        inr = set(st["pos"] for r in routes.values() for st in r if st["kind"] == "tile")
        dval = sum(j["value"] for j in jobs if j["pos"] not in inr)
        if dval < cfg["extra_hand_ratio"] * fib(nh):
            break
        nh += 1
    S["want_hands"] = nh
    add_supplies(V, S, routes, starts)
    S["routes"] = routes
    if S["cfg"].get("debug"):
        inr = set(st["pos"] for r in routes.values() for st in r if st["kind"] == "tile")
        dropped = [j for j in jobs if j["pos"] not in inr]
        cap = sum(max(0.5, 24 - h - 0.5) for _, _, h in units)
        used = sum(route_cost(starts[i], r) for i, r in routes.items())
        S.setdefault("dbg", []).append({"day": V.day, "jobs": len(jobs), "wl": round(sum(len(j["ops"]) + 1.5 for j in jobs)),
                                        "cap": round(cap), "used": round(used), "hands": nh,
                                        "dropped": len(dropped), "dval": round(sum(j["value"] for j in dropped)),
                                        "dkinds": collections_count([(j["kind"], j.get("crop") or j.get("animal") or j.get("plant")) for j in dropped]),
                                        "dpos": [(j["pos"], j.get("crop"), round(j["value"])) for j in dropped],
                                        "jpos": [(j["pos"], j.get("crop"), tuple(j["ops"]), round(j["value"])) for j in jobs if j.get("crop") == "STRAWBERRY"]})


def collections_count(xs):
    c = {}
    for x in xs:
        c[str(x)] = c.get(str(x), 0) + 1
    return c


def race_routes(V, S, units, jobs):
    mel = [j for j in jobs if j.get("crop") == "MELON" and "HARVEST" in j["ops"]]
    rest = [j for j in jobs if not (j.get("crop") == "MELON" and "HARVEST" in j["ops"])]
    mel.sort(key=lambda j: shed_dist(j["pos"]))
    free_at = {i: (h, p) for i, p, h in units}
    race = {i: [] for i, _, _ in units}
    for j in mel:
        j = dict(j)
        j["ops"] = (["WATER", "HARVEST"] if shed_dist(j["pos"]) <= S["cfg"]["race_water_dist"] else ["HARVEST"])
        j["race"] = True
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
    return {i: race[i] + base.get(i, []) for i, _, _ in units}


def midday_buy(V, S):
    """Buy target animals with cash earned during the day; append pickup + placement to the least-loaded unit."""
    budget = V.money - reserve_next(V, S)
    if budget < 300:
        return
    tu_new, buys = plan_uses(V, S, budget)
    tu = S["tile_use"]
    added = []
    for p, u in tu_new.items():
        if u in ANIMALS and p not in tu:
            t = V.tile(p)
            if t is None or (isinstance(t, dict) and t.get("kind") in ("WEED", "COOP", "PASTURE") and not t.get("animal")):
                added.append((p, u))
    if not added:
        return
    n_units = len(V.units)
    for p, u in added:
        cost = ANIMALS[u]["cost"]
        if budget < cost + 60:
            break
        budget -= cost
        tu[p] = u
        S.setdefault("buys", {}).setdefault("animals", {})
        S["buys"]["animals"][u] = S["buys"]["animals"].get(u, 0) + 1
        # least loaded existing unit
        best = min(range(n_units), key=lambda i: route_cost(V.units[i], S["routes"].get(i, [])))
        r = S["routes"].setdefault(best, [])
        pos = V.units[best]
        sp = nearest_shed(pos)
        ops = []
        t = V.tile(p)
        if isinstance(t, dict) and t.get("kind") == "WEED":
            ops.append("DIG")
        if not (isinstance(t, dict) and t.get("kind") == ANIMALS[u]["struct"]):
            ops.append("BUILD")
        ops.append("PLACE")
        ops += ["FEED", "CARE"]
        job = {"pos": p, "ops": ops, "urg": 0, "kind": "place", "place": u, "value": 900}
        r.append(mk_shed_stop(sp, pickup={u: 1, "WHEAT": 1}))
        r.append({"pos": p, "kind": "tile", "job": job})


def steal_work(V, S, i):
    """Idle unit i takes tile stops that their owners will finish too late (or last), nearest-valuable first."""
    left = 24 - V.hour
    pos = V.units[i]
    inv = V.invs[i] if i < len(V.invs) else {}
    mine = []
    t_used = 0
    slack = S["cfg"]["steal_slack"]
    for _ in range(8):
        cand = []
        for j in range(len(V.units)):
            if j == i:
                continue
            r = S["routes"].get(j, [])
            if not r:
                continue
            times = _route_times(V.units[j], r)
            if not times or times[-1] <= left:
                continue
            for k, st in enumerate(r):
                if st["kind"] != "tile" or st.get("_stolen"):
                    continue
                if k == 0 and st["pos"] == V.units[j]:
                    continue
                if times[k] <= left - slack:
                    continue
                ops = st["job"].get("ops", [])
                if ("FEED" in ops and inv.get("WHEAT", 0) <= 0) or "PLACE" in ops:
                    continue
                d = dist(pos, st["pos"])
                if t_used + d + stop_ops(st) > left:
                    continue
                cand.append((st["job"].get("value", 0) / (d + stop_ops(st) + 1), j, k, st, d))
        if not cand:
            break
        cand.sort(key=lambda c: -c[0])
        _, j, k, st, d = cand[0]
        S["routes"][j].pop(k)
        st["_stolen"] = True
        mine.append(st)
        t_used += d + stop_ops(st)
        pos = st["pos"]
    if mine:
        S["routes"][i] = mine


def replan_idle(V, S):
    idle = [(i, V.units[i], V.hour) for i in range(len(V.units)) if not S["routes"].get(i)]
    if not idle or V.hour >= 22:
        return
    if S["cfg"]["steal"]:
        for i, p, h in idle:
            steal_work(V, S, i)
        idle = [(i, V.units[i], V.hour) for i in range(len(V.units)) if not S["routes"].get(i)]
        if not idle:
            return
    jobs = gen_jobs(V, S)
    taken = set(st["pos"] for i, r in S["routes"].items() if i < len(V.units) for st in r)
    jobs = [j for j in jobs if j["pos"] not in taken and j["value"] >= 30]
    if not jobs and S["cfg"]["idle_care"] and V.hour <= S["cfg"]["idle_care_until"]:
        # idle hands: feed and care the animals the day plan skipped (care bonus), only with spare time
        fs = S["cfg"]["feed_skip"]
        S["cfg"]["feed_skip"] = False
        try:
            jobs = [j for j in gen_jobs(V, S) if j["pos"] not in taken and j["kind"] == "animal" and "FEED" in j["ops"]]
        finally:
            S["cfg"]["feed_skip"] = fs
    if not jobs:
        for i, p, h in idle:
            inv = V.invs[i] if i < len(V.invs) else {}
            if sum(inv.values()) >= 4 and shed_dist(p) <= 23 - V.hour:
                S["routes"][i] = [mk_shed_stop(nearest_shed(p), drop=True)]
        return
    routes = route_plan(V, S, idle, jobs)
    add_supplies(V, S, routes, {i: p for i, p, _ in idle})
    for i, r in routes.items():
        S["routes"][i] = r


def replan_event(V, S, buy=True):
    """New land / big cash: re-plan uses with a fresh budget and re-route everyone (keep current stops)."""
    if buy:
        cash = V.money
        budget = cash - reserve_next(V, S)
        tu, buys = plan_uses(V, S, max(0.0, budget))
        S["tile_use"] = tu
        S["buys"] = buys
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
            units.append((i, st["pos"], V.hour + 1 + dist(V.units[i], st["pos"]) + len(st["job"]["ops"])))
        else:
            units.append((i, V.units[i], V.hour + 1))
    routes = route_plan(V, S, units, jobs)
    add_supplies(V, S, routes, {i: p for i, p, _ in units})
    for i in keep:
        routes.setdefault(i, []).insert(0, keep[i])
    S["routes"] = routes


# ============================================================================= market
SELL_PRI = {"MELON": 0, "MILK": 1, "WOOL": 2, "STRAWBERRY": 3, "FERTILIZER": 4, "TOMATO": 5, "EGG": 6,
            "CARROT": 7, "WHEAT": 8}


def market_orders(V, S, acts):
    cfg = S["cfg"]
    orders = []
    cash = V.money
    last = V.step >= LAST_STEP - 1
    shed = dict(S.get("shed_proj", V.shed))
    sells = sell_plan(V, S, shed, last=last)
    if V.hour >= 22 and not last:
        carried = sum(sum(inv.values()) for inv in V.invs) + (2 if V.hour == 22 else 1) * len(V.units)
        after = sum(shed.values()) - sum(n for _, n in sells)
        over = after + carried - cfg["shed_cap"]
        for item in ("FERTILIZER", "WHEAT"):
            if over <= 0:
                break
            kept = shed.get(item, 0) - sum(n for it, n in sells if it == item)
            if item == "WHEAT":
                kept = max(0, kept - max(0, feed_counts(V, S)[1] - sum(inv.get("WHEAT", 0) for inv in V.invs)))
            extra = min(kept, over)
            if extra > 0:
                for sl in sells:
                    if sl[0] == item:
                        sl[1] += extra
                        break
                else:
                    sells.append([item, extra])
                over -= extra
    sells.sort(key=lambda s_: SELL_PRI.get(s_[0], 9))
    # hour 0: the 10-order cap would push hires to hour 1 (hands then start at hour 2); sell after the hires
    defer = (cfg["hire_first"] and V.hour == 0 and not last and S.get("want_hands", 0) > len(V.units) - 1)
    if not defer:
        for item, n in sells:
            orders.append(["SELL", item, n])
        cash += sale_value(V, sells)
    if last:
        return orders[:10]
    # hires
    if V.hour <= 2 and V.step < LAST_STEP - 3:
        want = S.get("want_hands", 0)
        have = len(V.units) - 1
        k = V.hires_today
        limit = (cfg["hire_limit0"] if V.hour == 0 else 10)
        while have < want and len(orders) < limit:
            c = fib(k)
            if c > cash:
                break
            orders.append(["HIRE"])
            cash -= c
            k += 1
            have += 1
    # feed wheat: only today's shortfall (tomorrow's comes from tonight's drops or tomorrow morning)
    need_w = 0
    ftoday, ftom = feed_counts(V, S)
    carried_w = sum(inv.get("WHEAT", 0) for inv in V.invs)
    if V.hour < 20:
        need_w = max(0, ftoday - carried_w) - shed.get("WHEAT", 0)
    if 20 <= V.hour <= 21:
        need_w = max(0, ftom - shed.get("WHEAT", 0) - carried_w)
    if need_w > 0 and len(orders) < 10 and V.day <= 28:
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
    # planned buys at hour 0 (and after events)
    buys = S.get("buys") or {}
    if S.get("buy_land") and len(orders) < 10:
        nq = len(V.quads)
        if nq < 4 and cash >= LAND_PRICES[nq - 1]:
            orders.append(["BUY_LAND"])
            cash -= LAND_PRICES[nq - 1]
            S["event"] = True
        S["buy_land"] = False
    for k, n in list(buys.get("animals", {}).items()):
        m = 0
        while m < n and cash >= ANIMALS[k]["cost"] and V.shed_total() + m < 98 and len(orders) < 10:
            cash -= ANIMALS[k]["cost"]
            m += 1
        if m:
            orders.append(["BUY_ANIMAL", k, m])
            buys["animals"][k] -= m
    for c, n in list(buys.get("seeds", {}).items()):
        m = 0
        while m < n and cash >= CROPS[c]["seed"]:
            cash -= CROPS[c]["seed"]
            m += 1
        if m and len(orders) < 10:
            orders.append(["BUY_SEED", c, m])
            buys["seeds"][c] -= m
    # opportunistic: land when cash allows during the day
    nq = len(V.quads)
    if nq < 4 and 2 <= V.hour <= 20 and len(orders) < 10 and not S.get("event"):
        cost = LAND_PRICES[nq - 1]
        if cfg["land_days"][nq - 1] <= V.day <= cfg["land_last"] and cash - cost >= reserve_next(V, S):
            orders.append(["BUY_LAND"])
            cash -= cost
            S["event"] = True
    if defer:
        for item, n in sells:
            if len(orders) >= 10:
                break
            orders.append(["SELL", item, n])
    return orders[:10]


# ============================================================================= entry
CFG = {
    "melons_d0": 12, "cows_d0": 2, "sheep_d0": 2, "geese_d0": 0,
    "sheep_base": 3, "cow_base": 5, "animal_total": 23,
    "straw_a": 13, "straw_b": 8.7, "tom_a": 14, "tom_b": 7.2, "car_a": 13, "car_b": 4,
    "straw_early": 10, "straw_last": 13, "tom_first": 9, "tom_last": 18, "car_first": 10, "car_early_frac": 0.35,
    "animal_last_day": 12, "animal_max_dist": 3, "animal_order": ("SHEEP", "COW", "GOOSE"),
    "hands_min": 4, "max_hands": 12, "race_hands": 12, "melon_race": True,
    "land_days": (6, 9, 99), "land_last": 14,
    "reserve_frac": 1.0, "mid_drop_until": 10, "shed_cap": 100, "drop_load": 99,
    "fert_wheat_max": 80, "fert_carrot_max": 45, "fert_premium_max": 999, "collect_min_price": 0,
    "feed_skip": True, "feed_ratio": 2.5, "stop_feed": {"COW": 27, "SHEEP": 26, "GOOSE": 28},
    "dig_weeds": True, "route_ls": True, "steal": False, "steal_slack": 2, "shed_place": True, "shed_place_min": 400, "straw_next_day": True, "rescue2_hours": (12, 16, 19, 21), "water_all": False, "cap_frac": 1.0, "rescue_hours": (), "eod_drop": True, "drop_mode": "fixed", "drop_margin": 10, "router": "sweep", "split_from": 10, "wheat_age4": False, "stop_feed_auto": True, "endgame": True, "place_feed": False, "ongoing_harvest_min": 2, "wheat_per_animal": 0.8, "opening_style": "race", "race_water_dist": 2, "early_until": 10, "max_hands_extra": 14, "extra_hand_ratio": 1.5, "rebuy_hours": (), "midday_hours": (), "free_slot_day": 6, "rebuy_min": 300, "hire_first": True, "hire_limit0": 8, "global_replan_hours": (), "idle_care": False, "idle_care_until": 20, "carrot_age3": False, "late_from": 99, "late_max_hands": 12, "early_cows": 0, "early_cows_day": 2, "opening_wheat_first": False, "target_mode": "shops", "decem_from": 3,
    "decem_k": {"sheep0": 3, "sheep1": 4, "sheep_max": 20, "cow0": 5, "cow1": 2, "cow_max": 14, "goose0": 3, "goose1": 2,
                "goose_max": 8, "straw0": 14, "straw1": 4, "tom1": 2, "tom_min": 3, "car0": 4, "car1": 4},
}
# p6 (9/28): start from the Kaggle hill-climb best config (prod/kg search on p4s; fresh seeds 7000-7099: -9.1k vs v7c,
# 15/200 wins, tick-free on both sides).
CFG.update({"steal": True, "land_days": (6, 11, 99), "car_a": 6, "car_b": 2, "tom_a": 20, "fert_wheat_max": 60,
            "tom_last": 18, "early_cows": 1, "animal_total": 18, "car_first": 8, "max_hands": 11,
            "shed_place_min": 150, "feed_ratio": 2.0})


def opening_layout(cfg):
    """NW day-0 plan. style 'race': melons nearest the shed (sell first on day 10), animals on the next ring."""
    lay = {}
    nm = cfg["melons_d0"]
    nw = [(x, y) for x in range(5) for y in range(5)]
    if cfg["opening_style"] == "race":
        order = sorted(nw, key=lambda p: (8 - p[0] - p[1], abs(p[0] - p[1])))
        for p in order[:nm]:
            lay[p] = "MELON"
        na = cfg["cows_d0"] + cfg["sheep_d0"] + cfg["geese_d0"]
        rest = [p for p in order if p not in lay]
        for p in rest[:na]:
            lay[p] = "ANIMAL"
        for p in rest[na:]:
            lay[p] = "WHEAT"
        return lay
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
    cfg.update(STATE.get("_override", {}))
    cfg["opening"] = opening_layout(cfg)
    return {"cfg": cfg, "routes": {}, "tile_use": {}, "day": -1, "last_step": -1, "event": False, "buys": {}}


def _agent(V, S):
    if S["day"] != V.day:
        S["day"] = V.day
        S["routes"] = {}
    missing = [i for i, r in S["routes"].items() if i >= len(V.units) and r]
    if V.hour == 0:
        day_plan(V, S)
    elif V.hour in S["cfg"]["midday_hours"] and V.day <= S["cfg"]["animal_last_day"] and             not (S.get("race_day") == V.day and V.hour < 12):
        midday_buy(V, S)
        replan_idle(V, S)
    elif V.hour in S["cfg"]["rebuy_hours"] and V.day <= S["cfg"]["animal_last_day"] + 6 and             V.money - reserve_next(V, S) >= S["cfg"]["rebuy_min"] and not (S.get("race_day") == V.day and V.hour < 9):
        replan_event(V, S)
    elif S.get("event") and not (S.get("race_day") == V.day and (V.hour < 9 or any(inv.get("MELON", 0) > 0 for inv in V.invs))):
        S["event"] = False
        replan_event(V, S)
    elif V.hour in S["cfg"]["global_replan_hours"] and V.day < LAST_DAY and             not (S.get("race_day") == V.day and (V.hour < 9 or any(inv.get("MELON", 0) > 0 for inv in V.invs))):
        replan_event(V, S, buy=False)
    else:
        replan_idle(V, S)
    if V.hour in S["cfg"]["rescue_hours"]:
        rescue_reorder(V, S)
    if V.hour in S["cfg"]["rescue2_hours"]:
        rescue_targeted(V, S)
    if S["cfg"]["eod_drop"] and 18 <= V.hour <= 22 and V.day < LAST_DAY:
        eod_drops(V, S)
    acts = execute(V, S)
    orders = market_orders(V, S, acts)
    if S["cfg"].get("debug") and V.hour == 23:
        left = [(i, st["pos"], st["job"].get("kind"), st["job"].get("crop") or st["job"].get("animal") or st["job"].get("plant"),
                 round(st["job"].get("value", 0))) for i, r in S["routes"].items() for st in r if st["kind"] == "tile"]
        S.setdefault("left", []).append({"day": V.day, "n": len(left), "val": sum(x[4] for x in left), "items": left[:12],
                                          "units": len(V.units), "routes": sorted(S["routes"].keys()), "want": S.get("want_hands")})
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
