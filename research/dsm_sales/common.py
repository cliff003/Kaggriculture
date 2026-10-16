"""Shared loaders for the DSM sales study (reads the cache written by replay_dsm.py)."""
import collections
import gzip
import math
import os
import pickle

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache", "dsm_replay.pkl.gz")

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
PI = {x: i for i, x in enumerate(PRODUCTS)}
SHED_ITEMS = PRODUCTS + ["GOOSE", "COW", "SHEEP"]
BASE = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250, "EGG": 50, "MILK": 160,
        "WOOL": 200, "FERTILIZER": 100}
SHOPS = {
    "BAKERY": ["EGG", "WHEAT"], "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"], "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE": ["WOOL"], "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"], "PET_CAFE": ["CARROT"],
    "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"], "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}
MARKET_PARAMS = {
    "WHEAT": (25, 400, "sqrt", 0.80, "log", 0.20), "CARROT": (35, 450, "hinge", 1.00, "sqrt", 0.70),
    "TOMATO": (60, 200, "hinge", 0.40, "sqrt", 0.60), "STRAWBERRY": (120, 100, "sqrt", 0.70, "linear", 1.60),
    "MELON": (250, 300, "log", 0.20, "sq", 3.60), "EGG": (50, 332, "hinge", 0.40, "log", 0.20),
    "MILK": (160, 122, "sqrt", 0.60, "linear", 1.60), "WOOL": (200, 105, "log", 0.20, "sq", 3.20),
    "FERTILIZER": (100, 200, "linear", 0.40, "linear", 0.40),
}


def _shape(func, x, T):
    x = max(0.0, x)
    if func == "linear":
        return x
    if func == "sq":
        return x * x
    if func == "sqrt":
        return math.sqrt(x)
    if func == "log":
        return math.log(1.0 + x)
    if func == "hinge":
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def price(item, inv):
    """Engine price function (same as kaggriculture.market_price with default params)."""
    base, T, bf, bt, af, at = MARKET_PARAMS[item]
    if inv < 10000:
        p = base + bt * base / _shape(bf, T, T) * _shape(bf, 10000 - inv, T)
    else:
        p = base - at * base / _shape(af, T, T) * _shape(af, inv - 10000, T)
    return max(1, int(round(p)))


def load(path=CACHE):
    with gzip.open(path, "rb") as f:
        d = pickle.load(f)
    return d["games"], d["acts"]


def town_demand(shops, step):
    """Units of each product the town removes at the end of `step` (after the market)."""
    out = collections.Counter()
    if step % 4 == 0:
        for s in shops:
            prods = SHOPS[s]
            for x in prods:
                out[x] += 2 if len(prods) == 1 else 1
    if step % 24 == 0:
        for x in PRODUCTS[:-1]:
            out[x] += 1
    return out


def per_step(g, acts):
    """Per step t and product: DSM / opponent units sold and requested, prices and slots.

    Returns dict of arrays [720, 9]: sold, req, osold, oreq, bought, obought, first_px, last_px,
    first_slot (DSM slot of its first SELL of the item, -1 if none), oslot (opponent)."""
    me = g["meta"]["me"]
    op = 1 - me
    T = 720
    z = lambda: np.zeros((T, 9), np.int32)
    r = {k: z() for k in ("sold", "req", "osold", "oreq", "bought", "obought", "breq", "obreq")}
    r["first_px"] = np.full((T, 9), -1, np.int32)
    r["last_px"] = np.full((T, 9), -1, np.int32)
    r["slot"] = np.full((T, 9), -1, np.int32)
    r["oslot"] = np.full((T, 9), -1, np.int32)
    r["nsellorders"] = z()
    for (step, p, slot, o, item, px, invb) in g["log"]:
        if item not in PI:
            continue
        j = PI[item]
        if o == "SELL":
            if p == me:
                r["sold"][step, j] += 1
                if r["first_px"][step, j] < 0:
                    r["first_px"][step, j] = px
                r["last_px"][step, j] = px
            else:
                r["osold"][step, j] += 1
        elif o == "BUY_PRODUCT":
            if p == me:
                r["bought"][step, j] += 1
            else:
                r["obought"][step, j] += 1
    for t in range(T - 1):
        for side, key, bkey, skey in ((me, "req", "breq", "slot"), (op, "oreq", "obreq", "oslot")):
            a = acts[side][t + 1] if t + 1 < len(acts[side]) else None
            m = a.get("market") if isinstance(a, dict) else None
            if not isinstance(m, list):
                continue
            for s, o in enumerate(m[:10]):
                if not (isinstance(o, list) and len(o) >= 3 and o[1] in PI):
                    continue
                try:
                    q = int(o[2])
                except (TypeError, ValueError):
                    continue
                j = PI[o[1]]
                if o[0] == "SELL":
                    r[key][t, j] += q
                    if side == me:
                        r["nsellorders"][t, j] += 1
                    if r[skey][t, j] < 0:
                        r[skey][t, j] = s
                elif o[0] == "BUY_PRODUCT":
                    r[bkey][t, j] += q
    return r
