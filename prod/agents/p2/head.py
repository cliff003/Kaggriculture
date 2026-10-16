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

