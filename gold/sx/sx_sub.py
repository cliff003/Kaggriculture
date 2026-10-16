r"""SX: demand-driven SE expansion over a v7b-type agent (team 42, 2026-09-25).

In worlds whose unlocked shops demand a crop heavily (STRAWBERRY: BRUNCH/ICE_CREAM/SMOOTHIE/FARMERS_MARKET;
TOMATO: PIZZA/FARMERS_MARKET), buy the SE quadrant on day CFG["day"] after the tape's own hires, plant CFG["n"]
plants on the SE tiles nearest the shed, and run them with dedicated hands hired after the tape's hires each day they
have work (plant, survival watering, production-day fertilizer + water, harvests, delivery). Products reach the shed
by PLACE; strawberries are sold by the base's eager layer, tomatoes by this layer. cha22's own SE projects (V219
tomatoes, V233 sheep) are left alone: SX does not start when one of them is committed, and after SX owns SE they no
longer qualify (they need SE locked).

Variant files exec this file into a namespace, update CFG and end with their own top-level `def agent`.
"""
import copy

_BASE_PATH = r"/Users/cliff/Documents/coding/kaggriculture_handoff_20260927/project/submissions/v7b_own_cha22_eager_wheatlead/main.py"
_NS = {"__name__": "sx_base"}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
_BASE = _NS["agent"]
_BNS = _NS["_BASE_NS"]
_CH = _BNS["_IMPL"].chassis
_PROJECT = _NS["_project"]

CFG = {
    "crop": "STRAWBERRY",
    "min_shops": 3,           # demanding shops among the unlocked ones on the decision day
    "min_ratio": 0.0,         # and the crop's quote >= min_ratio x base
    "day": 11,                # decision day (first hour after the tape's last hire)
    "last_day": 12,           # last day the project may start
    "n": 10,                  # plants
    "reserve": 3000,          # cash kept after land + seeds + first hires
    "hire_last_hour": 10,     # no new worker after this hour
    "max_workers": 2,
    "ops_per_worker": 14,     # tile ops one hand is given per day
    "fert": True,
    "harvest_every": 2,       # harvest when yield >= this (or before an overflow / at the end)
    "sell_tomato_floor": 0.0,
}

SHED = ((4, 4), (5, 4), (4, 5), (5, 5))
DEMAND = {"STRAWBERRY": ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET"),
          "TOMATO": ("PIZZA_SHOP", "FARMERS_MARKET")}
BASE = {"STRAWBERRY": 120, "TOMATO": 60}
SEED = {"STRAWBERRY": 100, "TOMATO": 50}
# productions at the end of these ages; fertilize on the first age of each 3-day block
PROD = {"STRAWBERRY": (9, 11, 13, 15), "TOMATO": (7, 8, 9, 10)}
FERT_AGES = {"STRAWBERRY": (9, 13), "TOMATO": (7, 10)}
LAST_AGE = {"STRAWBERRY": 16, "TOMATO": 11}
_FIB = [1, 1]
while len(_FIB) < 40:
    _FIB.append(_FIB[-1] + _FIB[-2])
_ST = {}
_TEL = {}


def _g(o, k, d=None):
    try:
        v = o[k]
    except Exception:
        v = getattr(o, k, d)
    return d if v is None else v


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _near_shed(p):
    return min(SHED, key=lambda q: (_dist(p, q), SHED.index(q)))


def _walk(p, t):
    if p[0] != t[0]:
        return ["EAST" if t[0] > p[0] else "WEST"]
    return ["SOUTH" if t[1] > p[1] else "NORTH"]


SE_TILES = sorted([(x, y) for x in range(5, 10) for y in range(5, 10)],
                  key=lambda q: (_dist(q, _near_shed(q)), q[1], q[0]))


def _tape(route, t):
    tape = _CH.routes.get(route) or []
    if t >= 648:
        tape = _CH.routes.get(2) or tape
    if 0 <= t < len(tape) and isinstance(tape[t], dict):
        return tape[t]
    return None


def _tape_hire_after(route, day, hour):
    for t in range(day * 24 + hour, day * 24 + 24):
        a = _tape(route, t)
        if a is not None and any(o and o[0] == "HIRE" for o in (a.get("market") or [])):
            return True
    return False


def _other_project(player, day):
    """(committed, active today): cha22's own SE projects."""
    committed = False
    late = False
    for key in ("_V219_STATES", "_V233_STATES"):
        pst = (_BNS.get(key) or {}).get(player) or {}
        if pst.get("committed"):
            committed = True
            if pst.get("requested_day") != day:
                late = True
    return committed, late


def _new():
    return {"last": -1, "committed": False, "decided": False, "p": None, "tiles": [], "hire": None,
            "workers": {}, "worker_day": -1, "tried": -1,
            "tel": {"gate": None, "gate_n": None, "gate_ratio": None, "commit": 0, "land_ok": 0, "planted": 0,
                    "died": 0, "hires": 0, "hire_cost": 0, "w_plant": 0, "w_water": 0, "w_fert": 0,
                    "w_harvest": 0, "w_place": 0, "fert_buy": 0, "tomato_sell": 0, "harvest_units": 0}}


def _is_ours(t, crop, p):
    return isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == crop and int(t.get("planted_day", -9)) == p


def _needs(t, crop, p, d):
    """Ops due today on our plant (P plant, F fertilize, W water, H harvest)."""
    out = set()
    if t is None or t == "LOCKED":
        if d == p:
            out.add("P")
        return out
    if not _is_ours(t, crop, p):
        return out
    a = d - p
    y = int(t.get("yield_units", 0) or 0)
    fu = t.get("fertilized_until_day")
    fu = -1 if fu is None else int(fu)
    prod_today = a in PROD[crop]
    if CFG.get("fert") and a in FERT_AGES[crop] and fu < d:
        out.add("F")
    gain = (2 if (fu >= d or "F" in out) else 1) if prod_today else 0
    if y > 0 and (y + gain > 4 or a >= LAST_AGE[crop] or y >= int(CFG["harvest_every"]) or d >= 29):
        out.add("H")
    if not t.get("watered_today") and a < LAST_AGE[crop] and d < 29:
        if prod_today or int(t.get("consecutive_unwatered", 0) or 0) >= 1:
            out.add("W")
    return out


def _sx(obs, action):
    step = int(_g(obs, "step", 0))
    player = int(_g(obs, "player", 0))
    st = _ST.get(player)
    if st is None or step == 0 or step <= st["last"]:
        st = _ST[player] = _new()
        _TEL[player] = st["tel"]
    st["last"] = step
    tel = st["tel"]
    crop = CFG["crop"]
    day, hour = step // 24, step % 24
    farm = _g(obs, "farms")[player]
    tiles = _g(farm, "tiles")
    priv = _g(obs, "private", {}) or {}
    seeds = dict(_g(priv, "seeds", {}) or {})
    shed = dict(_g(priv, "shed", {}) or {})
    invs = list(_g(priv, "inventories", []) or [])
    money = float(_g(farm, "money", 0))
    quads = set(_g(farm, "unlocked_quadrants", []) or [])
    route = (_CH.players.get(player) or {}).get("route")
    prices = dict(_g(_g(obs, "market", {}), "prices", {}) or {})

    out = dict(action)
    market = [list(o) for o in (out.get("market") or []) if isinstance(o, (list, tuple)) and o]
    units = [out.get("farmer") or ["PASS"]] + list(out.get("hands") or [])
    pos = [tuple(_g(farm, "farmer"))] + [tuple(h) for h in (_g(farm, "hands", []) or [])]
    while len(units) < len(pos):
        units.append(["PASS"])
    changed = mchanged = False

    # 0. decision
    if not st["committed"] and not st["decided"] and CFG["day"] <= day <= CFG["last_day"] and route is not None:
        if hour >= 1 and not _tape_hire_after(route, day, hour) and hour <= 6:
            shops = list(_g(_g(obs, "town", {}), "unlocked_shops", []) or [])
            n = sum(1 for s in shops if s in DEMAND[crop])
            ratio = float(prices.get(crop, 0) or 0) / BASE[crop]
            other, _ = _other_project(player, day)
            land_order = any(o[0] == "BUY_LAND" for o in market)
            ok = (n >= int(CFG["min_shops"]) and ratio >= float(CFG["min_ratio"]) and not other
                  and quads == {"NW", "NE", "SW"} and not land_order)
            tel["gate_n"], tel["gate_ratio"] = n, round(ratio, 2)
            if ok:
                k = int(CFG["n"])
                cost = 4000 + k * SEED[crop]
                native = sum(1 for o in market if o[0] == "HIRE")
                if money >= cost + float(CFG["reserve"]) and len(market) + 2 <= 10:
                    market.append(["BUY_LAND"])
                    market.append(["BUY_SEED", crop, k])
                    mchanged = True
                    st["committed"] = True
                    st["p"] = day
                    st["tiles"] = SE_TILES[:k]
                    tel["commit"] += 1
                    tel["gate"] = True
            if not st["committed"] and day >= CFG["last_day"]:
                st["decided"] = True
                tel["gate"] = bool(tel["gate"])
    if not st["committed"]:
        if mchanged:
            out["market"] = market[:10]
        return out

    p = st["p"]
    if "SE" in quads and not tel["land_ok"]:
        tel["land_ok"] = 1

    # 1. workers: confirm last step's hire, hire when today's work needs it
    if st["hire"] is not None and step == st["hire"]["step"] + 1:
        h = st["hire"]
        if len(pos) - 1 >= h["expect_last"]:
            for i in range(h["count"]):
                st["workers"][h["expect_last"] - h["count"] + 1 + i] = True
            st["worker_day"] = day
            tel["hires"] += h["count"]
            tel["hire_cost"] += h["cost"]
        st["hire"] = None
    if st["worker_day"] != day:
        st["workers"] = {}
    se_ok = "SE" in quads or (st["p"] == day and any(o[0] == "BUY_LAND" for o in market))
    if (not st["workers"] and st["hire"] is None and st["tried"] != day and se_ok and route is not None
            and hour <= int(CFG["hire_last_hour"]) and day <= 29):
        needs = [_needs(tiles[y][x], crop, p, day) for (x, y) in st["tiles"]]
        n_ops = sum(len(s) + (1 if "P" in s else 0) for s in needs)
        n_tiles = sum(1 for s in needs if s)
        turns = n_ops + n_tiles + 3
        _, late = _other_project(player, day)
        min_hour = 7 if late else 1
        if n_ops > 0 and hour >= min_hour and not _tape_hire_after(route, day, hour + 1):
            avail = max(6, 22 - hour)
            count = max(1, min(int(CFG["max_workers"]), -(-turns // avail)))
            native = sum(1 for o in market if o[0] == "HIRE")
            base_n = int(_g(farm, "hires_today", 0) or 0) + native
            cost = sum(_FIB[min(len(_FIB) - 1, base_n + i)] for i in range(count))
            n_f = sum(1 for s in needs if "F" in s)
            have_f = int(shed.get("FERTILIZER", 0))
            buy_f = max(0, n_f - have_f)
            fpx = float(prices.get("FERTILIZER", 100) or 100)
            spend = cost + buy_f * (fpx + 3)
            room = 10 - len(market) - (1 if buy_f else 0)
            if room >= count and money - spend >= 500:
                if buy_f:
                    market.append(["BUY_PRODUCT", "FERTILIZER", buy_f])
                    tel["fert_buy"] += buy_f
                for _ in range(count):
                    market.append(["HIRE"])
                st["hire"] = {"step": step, "expect_last": len(pos) - 1 + native + count, "count": count, "cost": cost}
                st["tried"] = day
                mchanged = True

    # 2. drive the workers
    if st["workers"]:
        ws = sorted(w for w in st["workers"] if w < len(pos))
        # split today's tiles between workers by nearest-first order
        tasks = {xy: _needs(tiles[xy[1]][xy[0]], crop, p, day) for xy in st["tiles"]}
        claimed = st.setdefault("claimed", {})
        if claimed.get("day") != day:
            claimed.clear()
            claimed["day"] = day
        for w in ws:
            units[w] = _work(st, w, pos[w], dict(invs[w]) if w < len(invs) else {}, tiles, day, hour, shed, seeds,
                             tasks, claimed, tel, crop)
            changed = True

    # 3. sell tomatoes (strawberries go through the base's eager layer)
    if crop == "TOMATO" and day >= p + 7:
        tmp = dict(out)
        tmp["market"] = market
        pshed = _PROJECT(obs, tmp)[0]
        q = int(pshed.get("TOMATO", 0))
        quote = float(prices.get("TOMATO", 0) or 0)
        if q > 0 and quote >= max(2.0, float(CFG["sell_tomato_floor"]) * 60):
            for o in market:
                if o[0] == "SELL" and len(o) >= 3 and o[1] == "TOMATO":
                    o[2] = max(int(o[2]), q)
                    break
            else:
                if len(market) < 10:
                    market.append(["SELL", "TOMATO", q])
                    tel["tomato_sell"] += q
                    mchanged = True

    if changed:
        out["farmer"] = units[0]
        out["hands"] = units[1:len(pos)]
    if mchanged:
        out["market"] = market[:10]
    return out


def _work(st, w, pos, inv, tiles, day, hour, shed, seeds, tasks, claimed, tel, crop):
    carry = int(inv.get(crop, 0) or 0)
    fert = int(inv.get("FERTILIZER", 0) or 0)
    p = st["p"]
    # standing on one of our tiles: do its ops in order P, F, W, H
    s = tasks.get(pos)
    if s:
        if "P" in s and seeds.get(crop, 0) > 0:
            s.discard("P")
            tel["w_plant"] += 1
            tasks[pos] = {"W"}
            return ["PLANT", crop]
        if "F" in s and fert > 0:
            s.discard("F")
            tel["w_fert"] += 1
            return ["FERTILIZE"]
        if "W" in s:
            s.discard("W")
            tel["w_water"] += 1
            return ["WATER"]
        if "H" in s:
            s.discard("H")
            tel["w_harvest"] += 1
            return ["HARVEST"]
    need_f = sum(1 for xy, s2 in tasks.items() if "F" in s2 and claimed.get(xy, w) == w)
    if fert < need_f and shed.get("FERTILIZER", 0) > 0 and st.get("picked", {}).get(w) != day:
        if pos in SHED:
            st.setdefault("picked", {})[w] = day
            return ["PICKUP", "FERTILIZER", min(need_f - fert, int(shed.get("FERTILIZER", 0)))]
        return _walk(pos, _near_shed(pos))
    best = None
    for xy, s2 in tasks.items():
        if not s2 or claimed.get(xy, w) != w:
            continue
        if s2 == {"F"} and fert <= 0:
            continue
        if s2 == {"P"} and seeds.get(crop, 0) <= 0:
            continue
        d = _dist(pos, xy)
        if hour + d + len(s2) > 23:
            continue
        key = (d, xy)
        if best is None or key < best[0]:
            best = (key, xy)
    ds = _dist(pos, _near_shed(pos))
    if carry > 0 and (best is None or hour >= 22 - ds):
        if pos in SHED:
            tel["w_place"] += carry
            tel["harvest_units"] += carry
            return ["PLACE", crop, carry]
        return _walk(pos, _near_shed(pos))
    if best is not None:
        claimed[best[1]] = w
        return _walk(pos, best[1])
    if any(v > 0 for k, v in inv.items() if k != crop):
        if pos in SHED:
            return ["DROP"]
        return _walk(pos, _near_shed(pos))
    return ["PASS"]


def agent(observation, configuration=None):
    action = _BASE(observation, configuration)
    try:
        return _sx(observation, action)
    except Exception:
        return action
