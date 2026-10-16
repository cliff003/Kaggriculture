r"""Late-seller counter layer (team 42 experiment, 2026-09-27).

    .venv\Scripts\python.exe gold\front\mk_lsc.py OUT_NAME [ITEMS=MILK,STRAWBERRY,WOOL] [FROM_DAY=12] [LOOK=3]
        [MIN_UNITS=8] [LATE_H=16] [LATE_SHARE=0.6] [MORN_SHARE=0.25] [LEAD=1] [MIN_SELL_H=12] [ROOM=10] [UNTIL=700]
        [BASE=submissions/v12_3_own_cha22_tick_fade_resume_late_sched_trap/main.py] [LOG=0]

Many rivals (DSM-style rules, several cha22 variants) hold their milk, strawberries and wool in the late game and
sell them in the evening, when the town has eaten the morning glut; we sell on arrival in the morning and they get
20-60 more per unit. This layer infers the rival's sales of each item every step from the market identity
(inventory change = our units + rival units - town consumption, with the engine's exact consumption rules). When,
over the last LOOK days, the rival sold at least MIN_UNITS of an item with LATE_SHARE or more of them at hours >=
LATE_H and at most MORN_SHARE in hours 0-7, our sells of that item are held until LEAD hours before the rival's
earliest evening sale hour of those days (not before MIN_SELL_H), and then the whole shed stock is sold in slot 0.
Nothing is held when the projected shed would pass 100 - ROOM, at hours 22-23 (the day-end room guard), before
FROM_DAY or from step UNTIL on. Against morning sellers nothing changes.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LAYER = r'''
import math as _math
CFG = __CFG__
TEL = {"holds": 0, "held_units": 0, "late_sells": 0, "modes": {}}
_MEM = {}
_MP = {
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
_SHOPS = {
    "BAKERY": ["EGG", "WHEAT"], "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"], "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE": ["WOOL"], "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"], "PET_CAFE": ["CARROT"],
    "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"], "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}


def _shape(f, x, T):
    x = max(0.0, x)
    if f == "linear":
        return x
    if f == "sq":
        return x * x
    if f == "sqrt":
        return _math.sqrt(x)
    if f == "log":
        return _math.log(1.0 + x)
    if f == "hinge":
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def _price(item, inv):
    base, T, bf, bt, af, at = _MP[item]
    if inv < 10000:
        p = base + bt * base / _shape(bf, T, T) * _shape(bf, 10000 - inv, T)
    else:
        p = base - at * base / _shape(af, T, T) * _shape(af, inv - 10000, T)
    return max(1, int(round(p)))


def _get(o, k, d=None):
    try:
        return o[k]
    except Exception:
        return getattr(o, k, d)


def _cons(shops, step, item):
    c = 0
    if step % 4 == 0:
        for sh in shops:
            prods = _SHOPS.get(sh, [])
            if item in prods:
                c += 2 if len(prods) == 1 else 1
    if step % 24 == 0 and item != "FERTILIZER":
        c += 1
    return c


def _our_delta(observation, market, shed0):
    """Market inventory change our own orders make, per item (sells at $1 add no supply), orders alone."""
    inv = {k: int(v) for k, v in dict(_get(_get(observation, "market", {}) or {}, "inventory", {}) or {}).items()}
    inv0 = dict(inv)
    shed = {k: int(v) for k, v in dict(shed0).items()}
    for o in list(market)[:10]:
        if not isinstance(o, (list, tuple)) or len(o) < 3:
            continue
        try:
            q = int(o[2])
        except Exception:
            continue
        item = o[1]
        if o[0] == "SELL" and item in _MP:
            for _ in range(max(0, q)):
                if shed.get(item, 0) <= 0:
                    break
                p = _price(item, inv.get(item, 10000))
                shed[item] -= 1
                if p > 1:
                    inv[item] = inv.get(item, 10000) + 1
        elif o[0] == "BUY_PRODUCT" and item in ("WHEAT", "FERTILIZER"):
            for _ in range(max(0, q)):
                inv[item] = inv.get(item, 10000) - 1
    return {k: inv[k] - inv0.get(k, 10000) for k in inv}


def _mode(mem, item, step):
    """(late?, sell hour) from the rival's inferred sales of `item` over the last LOOK days."""
    day = step // 24
    sales = [(s, n) for (s, n) in mem["sales"].get(item, []) if s // 24 >= day - CFG["LOOK"]]
    tot = sum(n for s, n in sales)
    if tot < CFG["MIN_UNITS"]:
        return False, None
    late = sum(n for s, n in sales if s % 24 >= CFG["LATE_H"])
    morn = sum(n for s, n in sales if s % 24 <= 7)
    if late < CFG["LATE_SHARE"] * tot or morn > CFG["MORN_SHARE"] * tot:
        return False, None
    by_day = {}
    for s, n in sales:
        if s % 24 >= CFG["MIN_SELL_H"]:
            by_day.setdefault(s // 24, []).append(s % 24)
    if not by_day:
        return False, None
    first = min(min(h) for h in by_day.values())
    return True, max(CFG["MIN_SELL_H"], first - CFG["LEAD"])


def agent(observation, configuration=None):
    try:
        step = int(_get(observation, "step", 0))
        me = int(_get(observation, "player", 0))
    except Exception:
        return _BASE(observation, configuration)
    mem = _MEM.get(me)
    if mem is None or step <= mem["last"]:
        mem = _MEM[me] = {"last": -1, "prev": None, "sales": {}}
    mem["last"] = step
    try:
        prev = mem["prev"]
        mem["prev"] = None
        inv_now = dict(_get(_get(observation, "market", {}) or {}, "inventory", {}) or {})
        if prev is not None and prev["step"] == step - 1:
            for item in CFG["ITEMS"]:
                rf = (int(inv_now.get(item, 10000)) - prev["inv"].get(item, 10000) - prev["delta"].get(item, 0)
                      + _cons(prev["shops"], prev["step"], item))
                if rf > 0:
                    mem["sales"].setdefault(item, []).append((prev["step"], rf))
    except Exception:
        pass
    a = _BASE(observation, configuration)
    try:
        if isinstance(a, dict):
            market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple))]
            hour = step % 24
            changed = False
            if CFG["FROM_DAY"] * 24 <= step < CFG["UNTIL"] and hour not in (22, 23):
                live = [o for o in market if o]
                pshed, pinvs = _PROJECT(observation, dict(a, market=live))[:2]
                carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
                load = sum(int(v) for v in pshed.values()) + carried
                for item in CFG["ITEMS"]:
                    late, sell_h = _mode(mem, item, step)
                    if not late:
                        continue
                    TEL["modes"][item] = TEL["modes"].get(item, 0) + 1
                    idx = [i for i, o in enumerate(market) if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item]
                    if hour < sell_h:
                        held = sum(int(market[i][2]) for i in idx)
                        if held > 0 and load + held <= 100 - CFG["ROOM"]:
                            for i in idx:
                                market[i] = []
                            load += held
                            TEL["holds"] += 1
                            TEL["held_units"] += held
                            changed = True
                    else:
                        stock = int((_get(_get(observation, "private"), "shed", {}) or {}).get(item, 0))
                        selling = sum(int(market[i][2]) for i in idx)
                        if stock > selling:
                            if idx:
                                market[idx[0]][2] = int(market[idx[0]][2]) + stock - selling
                            elif len([o for o in market if o]) < 10:
                                market.insert(0, ["SELL", item, stock])
                            TEL["late_sells"] += 1
                            changed = True
            if changed:
                a = dict(a)
                a["market"] = market[:10]
            shed0 = _PROJECT(observation, dict(a, market=[]))[0]
            mem["prev"] = {"step": step, "inv": {k: int(v) for k, v in dict(_get(_get(observation, "market", {}) or {}, "inventory", {}) or {}).items()},
                           "delta": _our_delta(observation, a.get("market") or [], shed0),
                           "shops": list(_get(_get(observation, "town", {}) or {}, "unlocked_shops", []) or [])}
    except Exception:
        pass
    return a
'''

CODE = r'''
_BASE_PATH = __BASE__
_NS = {"__name__": "lsc_base"}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
_BASE = _NS["agent"]
_PROJECT = _NS["_project"]
''' + LAYER


def cfg_from(kv):
    return {"ITEMS": kv.get("ITEMS", "MILK,STRAWBERRY,WOOL").split(","), "FROM_DAY": int(kv.get("FROM_DAY", 12)),
            "LOOK": int(kv.get("LOOK", 3)), "MIN_UNITS": int(kv.get("MIN_UNITS", 8)), "LATE_H": int(kv.get("LATE_H", 16)),
            "LATE_SHARE": float(kv.get("LATE_SHARE", 0.6)), "MORN_SHARE": float(kv.get("MORN_SHARE", 0.25)),
            "LEAD": int(kv.get("LEAD", 1)), "MIN_SELL_H": int(kv.get("MIN_SELL_H", 12)), "ROOM": int(kv.get("ROOM", 10)),
            "UNTIL": int(kv.get("UNTIL", 700)), "LOG": int(kv.get("LOG", 0))}


def main():
    name = sys.argv[1]
    kv = dict(x.split("=", 1) for x in sys.argv[2:])
    cfg = cfg_from(kv)
    base = os.path.abspath(kv.get("BASE", os.path.join(ROOT, "submissions", "v12_3_own_cha22_tick_fade_resume_late_sched_trap",
                                                        "main.py")))
    out = os.path.join(ROOT, "gold", "front", "var", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(
        CODE.replace("__BASE__", repr(base)).replace("__CFG__", repr(cfg)))
    print(out, cfg)


if __name__ == "__main__":
    main()
