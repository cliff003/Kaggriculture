r"""Marginal-floor sale cap over v9 (team 42 experiment, 2026-09-26; idea from Justin Yang, LB #119).

    .venv\Scripts\python.exe gold\front\mk_mfloor.py OUT_NAME [ITEMS=WOOL:0.3,MILK:0.3,STRAWBERRY:0.3] [FROM=288]
        [UNTIL=696] [SKIP_H=22,23] [BASE=gold/front/pub/v9/main.py]

The eager and route sells of premium goods dump the whole stock in one step once the quote clears the floor; with
wool's squared glut curve the last units of a 12-unit lot sell near zero. Here every SELL of a listed item is cut to
the units whose own quote (inventory before the order plus the units already sold ahead of it in this step's list)
stays at or above floor x base; the rest waits in the shed for the town to eat the glut. From UNTIL on nothing is cut
and all stock of the listed items is sold; hours in SKIP_H are left alone (the day-end room guard sells there).
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CODE = r'''
import math as _math
_BASE_PATH = __BASE__
_NS = {"__name__": "mfloor_base"}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
_BASE = _NS["agent"]
CFG = __CFG__
TEL = {"cuts": 0, "units_held": 0, "final_sells": 0}
_P = {
    "MILK": (160, 122, "sqrt", 0.60, "linear", 1.60),
    "WOOL": (200, 105, "log", 0.20, "sq", 3.20),
    "STRAWBERRY": (120, 100, "sqrt", 0.70, "linear", 1.60),
    "EGG": (50, 332, "hinge", 0.40, "log", 0.20),
    "CARROT": (35, 450, "hinge", 1.00, "sqrt", 0.70),
    "TOMATO": (60, 200, "hinge", 0.40, "sqrt", 0.60),
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
    base, T, bf, bt, af, at = _P[item]
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


def agent(observation, configuration=None):
    a = _BASE(observation, configuration)
    try:
        if not isinstance(a, dict):
            return a
        step = int(_get(observation, "step", 0))
        if step < CFG["FROM"] or (step % 24) in CFG["SKIP_H"]:
            return a
        market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple)) and o]
        inv = dict(_get(_get(observation, "market", {}) or {}, "inventory", {}) or {})
        shed = dict(_get(_get(observation, "private", {}) or {}, "shed", {}) or {})
        changed = False
        if step >= CFG["UNTIL"]:
            for item in CFG["ITEMS"]:
                have = int(shed.get(item, 0))
                if have <= 0:
                    continue
                sold = sum(int(o[2]) for o in market if o[0] == "SELL" and len(o) >= 3 and o[1] == item)
                if sold >= have:
                    continue
                for o in market:
                    if o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                        o[2] = have
                        break
                else:
                    if len(market) >= 10:
                        continue
                    market.insert(0, ["SELL", item, have])
                TEL["final_sells"] += 1
                changed = True
        else:
            ahead = {}
            for o in market:
                if o[0] != "SELL" or len(o) < 3 or o[1] not in CFG["ITEMS"]:
                    continue
                item = o[1]
                q = int(o[2])
                start = int(inv.get(item, 10000)) + ahead.get(item, 0)
                floor = CFG["ITEMS"][item] * _P[item][0]
                k = 0
                while k < q and _price(item, start + k) >= floor:
                    k += 1
                if k < q:
                    TEL["cuts"] += 1
                    TEL["units_held"] += q - k
                    o[2] = k
                    changed = True
                ahead[item] = ahead.get(item, 0) + k
            if changed:
                market = [o for o in market if not (o[0] == "SELL" and len(o) >= 3 and int(o[2]) <= 0)]
        if changed:
            a = dict(a)
            a["market"] = market[:10]
    except Exception:
        pass
    return a
'''


def main():
    name = sys.argv[1]
    kv = dict(x.split("=", 1) for x in sys.argv[2:])
    items = {}
    for part in kv.get("ITEMS", "WOOL:0.3,MILK:0.3,STRAWBERRY:0.3").split(","):
        k, v = part.split(":")
        items[k] = float(v)
    cfg = {"ITEMS": items, "FROM": int(kv.get("FROM", 288)), "UNTIL": int(kv.get("UNTIL", 696)),
           "SKIP_H": [int(h) for h in kv.get("SKIP_H", "22,23").split(",") if h]}
    base = os.path.abspath(kv.get("BASE", os.path.join(ROOT, "gold", "front", "pub", "v9", "main.py")))
    out = os.path.join(ROOT, "gold", "front", "var", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(
        CODE.replace("__BASE__", repr(base)).replace("__CFG__", repr(cfg)))
    print(out, cfg)


if __name__ == "__main__":
    main()
