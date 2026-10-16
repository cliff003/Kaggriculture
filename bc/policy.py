r"""Behaviour-cloned agent (research, 09-27): numpy forward pass of bc/train.py's Net + legality masks.

BC_WEIGHTS env var (or the default path) points at the exported .npz. Units: each step every unit (farmer + hands)
gets the most likely legal action; seeds are never over-committed (the engine drops all PLANTs of a crop when the
requests exceed the seeds). Market: expected counts from the market head, sells first, then buys and hires.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import encode as E  # noqa: E402

_W = None
_WPATH = os.environ.get("BC_WEIGHTS", os.path.join(HERE, "w_dsm.npz"))


def _load():
    global _W
    if _W is None:
        d = np.load(_WPATH)
        _W = {k.replace("__", "."): d[k].astype(np.float32) for k in d.files if k != "width"}
    return _W


def _conv(x, w, b):
    n, cin, h, wd = x.shape
    xp = np.pad(x, ((0, 0), (0, 0), (1, 1), (1, 1)))
    cols = np.empty((n, cin, 9, h, wd), np.float32)
    k = 0
    for dy in range(3):
        for dx in range(3):
            cols[:, :, k] = xp[:, :, dy:dy + h, dx:dx + wd]
            k += 1
    cols = cols.reshape(n, cin * 9, h * wd)
    out = np.einsum("oc,ncp->nop", w.reshape(w.shape[0], -1), cols, optimize=True) + b[None, :, None]
    return out.reshape(n, w.shape[0], h, wd)


def _relu(x):
    return np.maximum(x, 0)


def _trunk(W, board, planes):
    x = np.concatenate([np.repeat(board[None], len(planes), 0), planes], 1)
    x = _relu(_conv(x, W["c1.weight"], W["c1.bias"]))
    x = _relu(_conv(x, W["c2.weight"], W["c2.bias"])) + x
    x = _relu(_conv(x, W["c3.weight"], W["c3.bias"])) + x
    x = _relu(_conv(x, W["c4.weight"], W["c4.bias"])) + x
    return x


def _lin(W, name, x):
    return x @ W[name + ".weight"].T + W[name + ".bias"]


def _g(o, k, d=None):
    try:
        return o[k]
    except Exception:
        return getattr(o, k, d)


def _legal(tile, x, y, inv, shed, seeds, day):
    ok = np.zeros(len(E.ACTIONS), bool)
    ok[E.AIDX["NORTH"]] = y > 0
    ok[E.AIDX["SOUTH"]] = y < 9
    ok[E.AIDX["WEST"]] = x > 0
    ok[E.AIDX["EAST"]] = x < 9
    ok[E.AIDX["PASS"]] = True
    adj = E.shed_adjacent(x, y)
    is_dict = isinstance(tile, dict) or (tile is not None and tile != "LOCKED" and hasattr(tile, "keys"))
    kind = _g(tile, "kind") if is_dict else None
    animal = _g(tile, "animal") if is_dict else None
    if kind == "PLANT":
        ok[E.AIDX["WATER"]] = not _g(tile, "watered_today")
        crop = _g(tile, "crop")
        age = day - int(_g(tile, "planted_day", day) or day)
        ok[E.AIDX["HARVEST"]] = int(_g(tile, "yield_units", 0) or 0) > 0 and age >= E.FIRST_YIELD.get(crop, 99)
        ok[E.AIDX["FERTILIZE"]] = int(inv.get("FERTILIZER", 0) or 0) > 0 and int(_g(tile, "fertilized_until_day", -1) or -1) < day + 2
    if kind == "WEED":
        ok[E.AIDX["DIG"]] = True
    if animal:
        ok[E.AIDX["HARVEST"]] = int(_g(tile, "yield_units", 0) or 0) > 0
        ok[E.AIDX["FEED"]] = (not _g(tile, "fed_today")) and int(inv.get("WHEAT", 0) or 0) > 0
        ok[E.AIDX["CARE"]] = not _g(tile, "cared_today")
        ok[E.AIDX["COLLECT_FERTILIZER"]] = bool(_g(tile, "fertilizer_available"))
    if tile is None:
        ok[E.AIDX["BUILD_COOP"]] = True
        ok[E.AIDX["BUILD_PASTURE"]] = True
        for c in E.CROPS:
            ok[E.AIDX["PLANT_" + c]] = int(seeds.get(c, 0) or 0) > 0
    if adj:
        ok[E.AIDX["DROP"]] = any(int(v or 0) > 0 for v in inv.values())
        for i in E.ITEMS:
            ok[E.AIDX["PICKUP_" + i]] = int(shed.get(i, 0) or 0) > 0
            if i in E.PRODUCTS:
                ok[E.AIDX["PLACE_" + i]] = int(inv.get(i, 0) or 0) > 0
    for an, struct in (("GOOSE", "COOP"), ("COW", "PASTURE"), ("SHEEP", "PASTURE")):
        if kind == struct and not animal and int(inv.get(an, 0) or 0) > 0:
            ok[E.AIDX["PLACE_" + an]] = True
    return ok


_OPEN = None
_OPEN_PATH = os.environ.get("BC_OPENING", os.path.join(HERE, "opening.json"))
OPEN_STEPS = int(os.environ.get("BC_OPEN_STEPS", "11"))


def agent(observation, configuration=None):
    global _OPEN
    W = _load()
    me = int(_g(observation, "player", 0))
    step = int(_g(observation, "step", 0))
    if step < OPEN_STEPS:
        if _OPEN is None:
            _OPEN = json.load(open(_OPEN_PATH, encoding="utf-8")) if os.path.exists(_OPEN_PATH) else []
        if step < len(_OPEN) and isinstance(_OPEN[step], dict):
            a = _OPEN[step]
            nh = len(_g(_g(observation, "farms")[me], "hands") or [])
            hands = list(a.get("hands") or [])[:nh] + [["PASS"]] * max(0, nh - len(a.get("hands") or []))
            return {"farmer": a.get("farmer") or ["PASS"], "hands": hands, "market": list(a.get("market") or [])}
    day, hour = step // 24, step % 24
    farm = _g(observation, "farms")[me]
    priv = _g(observation, "private")
    board, pos = E.board(farm, day)
    board = np.clip(np.round(board * 4), 0, 255) / 4.0
    gv, shed = E.glob_vec(observation, me, day, hour)
    shed = {k: int(v or 0) for k, v in dict(shed).items()}
    seeds = {k: int(v or 0) for k, v in dict(_g(priv, "seeds", {}) or {}).items()}
    invs = list(_g(priv, "inventories", [{}]) or [{}])
    tiles = _g(farm, "tiles")
    n = len(pos)
    planes = np.zeros((n, 1, 10, 10), np.float32)
    for i, (x, y) in enumerate(pos):
        planes[i, 0, y, x] = 1.0
    feat = _trunk(W, board.astype(np.float32), planes)
    g = _relu(_lin(W, "g1", gv[None]))
    actions = []
    reserved = set()
    for i, (x, y) in enumerate(pos):
        inv = {k: int(v or 0) for k, v in dict(invs[i] if i < len(invs) else {}).items()}
        uv = E.unit_vec(inv, i, n)
        at = feat[i, :, y, x]
        pooled = feat[i].mean((1, 2))
        h = _relu(_lin(W, "u1", np.concatenate([at, pooled, g[0], uv])[None]))
        h = _relu(_lin(W, "u2", h))
        logits = _lin(W, "ua", h)[0]
        qty = _lin(W, "uq", h)[0]
        tile = tiles[y][x]
        ok = _legal(tile, x, y, inv, shed, seeds, day)
        if (x, y) in reserved:
            for k in ("WATER", "HARVEST", "FERTILIZE", "FEED", "CARE", "COLLECT_FERTILIZER", "DIG", "BUILD_COOP",
                      "BUILD_PASTURE") + tuple("PLANT_" + c for c in E.CROPS):
                ok[E.AIDX[k]] = False
        logits = np.where(ok, logits, -1e9)
        k = int(np.argmax(logits))
        name = E.ACTIONS[k]
        q = 1
        if name.startswith("PICKUP_"):
            item = name[7:]
            q = int(max(1, min(shed.get(item, 0), round(math.expm1(max(0.0, qty[k]))))))
            shed[item] = shed.get(item, 0) - q
        elif name.startswith("PLACE_"):
            item = name[6:]
            q = int(max(1, inv.get(item, 0))) if item in E.PRODUCTS else 1
        elif name.startswith("PLANT_"):
            seeds[name[6:]] = seeds.get(name[6:], 0) - 1
        if name not in E.MOVES and name not in ("PASS", "DROP") and not name.startswith("PICKUP_"):
            reserved.add((x, y))
        actions.append(E.action_from_class(k, q))
    # market
    pooled0 = feat[0].mean((1, 2)) if n else np.zeros(W["m1.weight"].shape[1] - 128, np.float32)
    hm = _relu(_lin(W, "m1", np.concatenate([pooled0, g[0]])[None]))
    mo = _lin(W, "m2", hm)[0]
    nm = len(E.MKT)
    cnt = {E.MKT[j]: (int(max(1, round(math.exp(min(6.0, float(mo[nm + j])))))) if mo[j] > 0 else 0) for j in range(nm)}
    orders = []
    for p in E.PRODUCTS:
        q = min(cnt["SELL_" + p], shed.get(p, 0))
        if q > 0:
            orders.append(["SELL", p, q])
    if cnt["BUY_WHEAT"] > 0:
        orders.append(["BUY_PRODUCT", "WHEAT", cnt["BUY_WHEAT"]])
    if cnt["BUY_FERT"] > 0:
        orders.append(["BUY_PRODUCT", "FERTILIZER", cnt["BUY_FERT"]])
    for c in E.CROPS:
        if cnt["SEED_" + c] > 0:
            orders.append(["BUY_SEED", c, cnt["SEED_" + c]])
    for an in E.ANIMALS:
        if cnt["ANIMAL_" + an] > 0:
            orders.append(["BUY_ANIMAL", an, cnt["ANIMAL_" + an]])
    if cnt["LAND"] > 0:
        orders.append(["BUY_LAND"])
    orders += [["HIRE"] for _ in range(min(12, cnt["HIRE"]))]
    return {"farmer": actions[0] if actions else ["PASS"], "hands": actions[1:], "market": orders[:10]}
