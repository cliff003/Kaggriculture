"""Observation / action encoding for behaviour cloning of a strong production team (research, team 42, 09-27).

Board: 10x10 grid, C channels. Global: vector G. Unit action: one class of ACTIONS (+ quantity for PICKUP/PLACE).
Market targets per step: hires, seed buys per crop, animal buys, land, wheat/fertilizer buys, sells per item.
Pure numpy so the same code runs inside a submitted agent.
"""
import math
import numpy as np

CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["GOOSE", "COW", "SHEEP"]
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
ITEMS = PRODUCTS + ANIMALS
SHOPS = ["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE", "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP",
         "FARMERS_MARKET"]
BASE = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250, "EGG": 50, "MILK": 160,
        "WOOL": 200, "FERTILIZER": 100}
FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}
SHED_TILES = {(4, 4), (5, 4), (4, 5), (5, 5)}
MOVES = ["NORTH", "SOUTH", "EAST", "WEST"]
SIMPLE = ["PASS", "WATER", "HARVEST", "FERTILIZE", "DIG", "BUILD_COOP", "BUILD_PASTURE", "FEED",
          "COLLECT_FERTILIZER", "CARE", "DROP"]
ACTIONS = MOVES + SIMPLE + ["PLANT_" + c for c in CROPS] + ["PICKUP_" + i for i in ITEMS] + ["PLACE_" + i for i in ITEMS]
AIDX = {a: i for i, a in enumerate(ACTIONS)}
C = 28
G = 10 + len(ITEMS) + len(CROPS) + 2 * len(PRODUCTS) + len(SHOPS)
U = len(ITEMS) + 4


def _g(o, k, d=None):
    try:
        return o[k]
    except Exception:
        return getattr(o, k, d)


def shed_adjacent(x, y):
    return (x, y) in SHED_TILES or any(abs(x - a) + abs(y - b) == 1 for a, b in SHED_TILES)


STATIC = np.zeros((10, 10), np.float32)
for _y in range(10):
    for _x in range(10):
        if (_x, _y) in SHED_TILES:
            STATIC[_y, _x] = 1.0


def board(farm, day):
    """C x 10 x 10 float32 board of one farm."""
    b = np.zeros((C, 10, 10), np.float32)
    tiles = _g(farm, "tiles")
    for y in range(10):
        row = tiles[y]
        for x in range(10):
            t = row[x]
            if t == "LOCKED":
                b[0, y, x] = 1
            elif t is None:
                b[1, y, x] = 1
            else:
                kind = _g(t, "kind")
                if kind == "WEED":
                    b[2, y, x] = 1
                elif kind == "PLANT":
                    b[3, y, x] = 1
                    crop = _g(t, "crop")
                    if crop in CROPS:
                        b[6 + CROPS.index(crop), y, x] = 1
                    b[11, y, x] = 1.0 if _g(t, "watered_today") else 0.0
                    b[12, y, x] = min(8, int(_g(t, "yield_units", 0) or 0)) / 4.0
                    age = day - int(_g(t, "planted_day", day) or day)
                    b[13, y, x] = age / 12.0
                    b[14, y, x] = 1.0 if int(_g(t, "fertilized_until_day", -1) or -1) >= day else 0.0
                    b[15, y, x] = min(3, int(_g(t, "consecutive_unwatered", 0) or 0)) / 3.0
                    b[16, y, x] = 1.0 if crop in FIRST_YIELD and age >= FIRST_YIELD[crop] else 0.0
                elif kind in ("COOP", "PASTURE"):
                    b[4 if kind == "COOP" else 5, y, x] = 1
                    an = _g(t, "animal")
                    if an in ANIMALS:
                        b[17 + ANIMALS.index(an), y, x] = 1
                        b[20, y, x] = 1.0 if _g(t, "fed_today") else 0.0
                        b[21, y, x] = 1.0 if _g(t, "cared_today") else 0.0
                        b[22, y, x] = 1.0 if _g(t, "fertilizer_available") else 0.0
                        b[23, y, x] = min(6, int(_g(t, "yield_units", 0) or 0)) / 3.0
    pos = [tuple(_g(farm, "farmer"))] + [tuple(h) for h in (_g(farm, "hands") or [])]
    for (x, y) in pos:
        if 0 <= x < 10 and 0 <= y < 10:
            b[24, y, x] += 1.0
    b[25] = STATIC
    return b, pos


def glob_vec(obs, me, day, hour):
    farm = _g(obs, "farms")[me]
    rival = _g(obs, "farms")[1 - me]
    priv = _g(obs, "private")
    shed = _g(priv, "shed", {}) or {}
    seeds = _g(priv, "seeds", {}) or {}
    mk = _g(obs, "market", {}) or {}
    prices = _g(mk, "prices", {}) or {}
    inv = _g(mk, "inventory", {}) or {}
    shops = list(_g(_g(obs, "town", {}) or {}, "unlocked_shops", []) or [])
    money = float(_g(farm, "money", 0))
    v = [day / 30.0, hour / 24.0, math.sin(2 * math.pi * hour / 24), math.cos(2 * math.pi * hour / 24),
         money / 50000.0, math.log1p(max(0.0, money)) / 12.0, float(_g(farm, "hires_today", 0) or 0) / 12.0,
         len(_g(farm, "hands") or []) / 12.0, float(_g(rival, "money", 0)) / 50000.0,
         len(_g(farm, "unlocked_quadrants") or []) / 4.0]
    v += [min(100, int(shed.get(i, 0) or 0)) / 50.0 for i in ITEMS]
    v += [min(60, int(seeds.get(c, 0) or 0)) / 20.0 for c in CROPS]
    v += [float(prices.get(p, BASE[p])) / BASE[p] for p in PRODUCTS]
    v += [(10000 - float(inv.get(p, 10000))) / 300.0 for p in PRODUCTS]
    v += [shops.count(s) / 2.0 for s in SHOPS]
    return np.asarray(v, np.float32), shed


def unit_vec(inv_u, idx, n_units):
    v = [min(50, int(inv_u.get(i, 0) or 0)) / 10.0 for i in ITEMS]
    v += [1.0 if idx == 0 else 0.0, idx / 12.0, n_units / 12.0, sum(int(x or 0) for x in inv_u.values()) / 20.0]
    return np.asarray(v, np.float32)


def action_class(a):
    """(class index, quantity) of one unit action, or (None, 0) if unknown."""
    if not isinstance(a, list) or not a:
        return AIDX["PASS"], 0
    op = a[0]
    if op in MOVES or op in SIMPLE:
        return AIDX[op], 0
    if op == "PLANT" and len(a) >= 2 and a[1] in CROPS:
        return AIDX["PLANT_" + a[1]], 0
    if op in ("PICKUP", "PLACE") and len(a) >= 2 and a[1] in ITEMS:
        q = int(a[2]) if len(a) >= 3 else 1
        return AIDX[op + "_" + a[1]], q
    return None, 0


def action_from_class(k, qty):
    name = ACTIONS[k]
    if name in MOVES or name in SIMPLE:
        return [name]
    if name.startswith("PLANT_"):
        return ["PLANT", name[6:]]
    op, item = name.split("_", 1)
    return [op, item, int(max(1, qty))]


# market targets: HIRE, BUY_SEED x5, BUY_ANIMAL x3, BUY_LAND, BUY_PRODUCT WHEAT, FERTILIZER, SELL x9
MKT = ["HIRE"] + ["SEED_" + c for c in CROPS] + ["ANIMAL_" + a for a in ANIMALS] + ["LAND", "BUY_WHEAT", "BUY_FERT"] + \
      ["SELL_" + p for p in PRODUCTS]


def market_targets(orders):
    t = np.zeros(len(MKT), np.float32)
    for o in orders or []:
        if not isinstance(o, list) or not o:
            continue
        op = o[0]
        q = int(o[2]) if len(o) >= 3 and str(o[2]).lstrip("-").isdigit() else 1
        if q <= 0 and op != "HIRE" and op != "BUY_LAND":
            continue
        if op == "HIRE":
            t[0] += 1
        elif op == "BUY_SEED" and len(o) >= 2 and o[1] in CROPS:
            t[1 + CROPS.index(o[1])] += q
        elif op == "BUY_ANIMAL" and len(o) >= 2 and o[1] in ANIMALS:
            t[6 + ANIMALS.index(o[1])] += q
        elif op == "BUY_LAND":
            t[9] += 1
        elif op == "BUY_PRODUCT" and len(o) >= 2 and o[1] == "WHEAT":
            t[10] += q
        elif op == "BUY_PRODUCT" and len(o) >= 2 and o[1] == "FERTILIZER":
            t[11] += q
        elif op == "SELL" and len(o) >= 2 and o[1] in PRODUCTS:
            t[12 + PRODUCTS.index(o[1])] += q
    return t
