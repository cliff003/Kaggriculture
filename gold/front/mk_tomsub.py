r"""Tomato substitution layer over v8 (team 42 experiment, 2026-09-26; idea from dodsters, LB #66).

    .venv\Scripts\python.exe gold\front\mk_tomsub.py OUT_NAME [K=13] [DAY=11] [XMAX=4] [YMIN=5] [SELL=1] [FLOOR=0.3]
        [MINSHOPS=0] [BASE=gold/front/pub/v8/main.py]

On day DAY the route tape plants strawberries on the south-west tiles it has just bought (x <= XMAX, y >= YMIN).
The first K of those plantings become tomatoes. The tape's own strawberry care (water on ages 0-7, fertilize and
water on age 9, harvest on age 10) grows and harvests about 4 tomatoes per tile without extra work; the tomato then
finishes and rots, and the tape's later strawberry actions on that tile are no-ops until it digs and replants.
Tomato seeds are bought at the first step of the day (K x 50); each converted planting leaves one strawberry seed
unused, so later BUY_SEED STRAWBERRY orders are cut by that surplus. Tomatoes in the shed are sold on arrival while
the quote is at least FLOOR x base. MINSHOPS: convert only when at least that many PIZZA_SHOP / FARMERS_MARKET are
unlocked on day DAY.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CODE = r'''
_BASE_PATH = __BASE__
_NS = {"__name__": "tomsub_base"}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
_BASE = _NS["agent"]
CFG = __CFG__
TEL = {"seed_buys": 0, "converted": 0, "seed_cut": 0, "tomato_sold_orders": 0, "skipped_no_seed": 0}
_MEM = {}


def _get(o, k, d=None):
    try:
        return o[k]
    except Exception:
        return getattr(o, k, d)


def _decide(observation, configuration=None):
    a = _BASE(observation, configuration)
    try:
        step = int(_get(observation, "step", 0))
        me = int(_get(observation, "player", 0))
    except Exception:
        return a
    mem = _MEM.setdefault(me, {"last": -1})
    if step <= mem["last"]:
        mem.clear()
        mem["last"] = -1
    mem["last"] = step
    mem.setdefault("conv", 0)
    mem.setdefault("surplus", 0)
    mem.setdefault("bought", False)
    mem.setdefault("active", None)
    if not isinstance(a, dict):
        return a
    try:
        day = step // 24
        priv = _get(observation, "private", {}) or {}
        seeds = dict(_get(priv, "seeds", {}) or {})
        shed = dict(_get(priv, "shed", {}) or {})
        market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple)) and o]
        changed = False
        if day == CFG["DAY"] and mem["active"] is None:
            town = _get(observation, "town", {}) or {}
            shops = list(_get(town, "unlocked_shops", []) or [])
            mem["active"] = sum(1 for s in shops if s in ("PIZZA_SHOP", "FARMERS_MARKET")) >= CFG["MINSHOPS"]
        if day == CFG["DAY"] and mem["active"]:
            if not mem["bought"] and len(market) < 10:
                market.append(["BUY_SEED", "TOMATO", CFG["K"]])
                mem["bought"] = True
                TEL["seed_buys"] += 1
                changed = True
            me_farm = _get(observation, "farms")[me]
            pos = [tuple(_get(me_farm, "farmer"))] + [tuple(h) for h in (_get(me_farm, "hands", []) or [])]
            units = [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
            tom_avail = int(seeds.get("TOMATO", 0))
            used = 0
            for i, u in enumerate(units):
                if mem["conv"] >= CFG["K"] or i >= len(pos):
                    break
                if isinstance(u, list) and len(u) >= 2 and u[0] == "PLANT" and u[1] == "STRAWBERRY":
                    x, y = pos[i]
                    if x <= CFG["XMAX"] and y >= CFG["YMIN"]:
                        if used < tom_avail:
                            units[i] = ["PLANT", "TOMATO"]
                            used += 1
                            mem["conv"] += 1
                            mem["surplus"] += 1
                            TEL["converted"] += 1
                            changed = True
                        else:
                            TEL["skipped_no_seed"] += 1
            if changed:
                a = dict(a)
                a["farmer"] = units[0]
                a["hands"] = units[1:]
        if mem["surplus"] > 0:
            for o in market:
                if o[0] == "BUY_SEED" and len(o) >= 3 and o[1] == "STRAWBERRY" and mem["surplus"] > 0:
                    cut = min(int(o[2]), mem["surplus"])
                    o[2] = int(o[2]) - cut
                    mem["surplus"] -= cut
                    TEL["seed_cut"] += cut
                    changed = True
            market = [o for o in market if not (o[0] == "BUY_SEED" and len(o) >= 3 and int(o[2]) <= 0)]
        if CFG["SELL"] and shed.get("TOMATO", 0) > 0 and step <= 717:
            prices = _get(_get(observation, "market", {}) or {}, "prices", {}) or {}
            if int(_get(prices, "TOMATO", 0)) >= CFG["FLOOR"] * 60:
                have = int(shed.get("TOMATO", 0))
                done = False
                for o in market:
                    if o[0] == "SELL" and len(o) >= 3 and o[1] == "TOMATO":
                        o[2] = max(int(o[2]), have)
                        done = True
                        break
                if not done and len(market) < 10:
                    i = 0
                    while i < len(market) and market[i][0] == "SELL":
                        i += 1
                    market.insert(i, ["SELL", "TOMATO", have])
                    done = True
                if done:
                    TEL["tomato_sold_orders"] += 1
                    changed = True
        if changed:
            a = dict(a)
            a["market"] = market[:10]
    except Exception:
        pass
    return a


def agent(observation, configuration=None):
    return _decide(observation, configuration)
'''


def main():
    name = sys.argv[1]
    kv = dict(x.split("=", 1) for x in sys.argv[2:])
    cfg = {"K": int(kv.get("K", 13)), "DAY": int(kv.get("DAY", 11)), "XMAX": int(kv.get("XMAX", 4)),
           "YMIN": int(kv.get("YMIN", 5)), "SELL": int(kv.get("SELL", 1)), "FLOOR": float(kv.get("FLOOR", 0.3)),
           "MINSHOPS": int(kv.get("MINSHOPS", 0))}
    base = os.path.abspath(kv.get("BASE", os.path.join(ROOT, "gold", "front", "pub", "v8", "main.py")))
    out = os.path.join(ROOT, "gold", "front", "var", name)
    os.makedirs(out, exist_ok=True)
    src = CODE.replace("__BASE__", repr(base)).replace("__CFG__", repr(cfg))
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(src)
    print(out, cfg)


if __name__ == "__main__":
    main()
