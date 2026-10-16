r"""Glut drip-sell layer (team 42 experiment, 2026-09-26; rule seen in Vadim Vasilenko's and DSM's games).

    .venv\Scripts\python.exe gold\front\mk_drip.py OUT_NAME [ITEMS=WOOL] [G=0.8] [FRAC=0.5] [FROM_DAY=10]
        [UNTIL=690] [SKIP_H=22,23] [BASE=submissions/v12_3_own_cha22_tick_fade_resume_late_sched_trap/main.py]

In a glutted market (quote below G x base) our SELL orders of the listed items are capped: at s % 4 == 1 (the first
step after a town meal) we sell up to ceil(FRAC x the item's consumption at that meal), at other steps nothing; the
rest waits in the shed. Wool above its reference inventory drops with the square of the excess, so lumps cost a lot
more than drips. Hours in SKIP_H are left alone (the day-end room guard sells there) and from step UNTIL on nothing
is capped (the base dumps its stock). A step whose projected shed would pass 100 - ROOM keeps enough sells to fit.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CODE = r'''
import math as _math
_BASE_PATH = __BASE__
_NS = {"__name__": "drip_base"}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
_BASE = _NS["agent"]
_PROJECT = _NS["_project"]
CFG = __CFG__
TEL = {"cuts": 0, "units_held": 0, "drip_sells": 0}
_BASEP = {"WOOL": 200, "MILK": 160, "STRAWBERRY": 120, "EGG": 50, "CARROT": 35, "TOMATO": 60}
_SHOPS = {
    "BAKERY": ["EGG", "WHEAT"], "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"], "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE": ["WOOL"], "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"], "PET_CAFE": ["CARROT"],
    "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"], "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}


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
    if step % 24 == 0:
        c += 1
    return c


def agent(observation, configuration=None):
    a = _BASE(observation, configuration)
    try:
        if not isinstance(a, dict):
            return a
        step = int(_get(observation, "step", 0))
        if step // 24 < CFG["FROM_DAY"] or step >= CFG["UNTIL"] or (step % 24) in CFG["SKIP_H"]:
            return a
        market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple))]
        mk = _get(observation, "market", {}) or {}
        prices = _get(mk, "prices", {}) or {}
        shops = list(_get(_get(observation, "town", {}) or {}, "unlocked_shops", []) or [])
        changed = False
        for item in CFG["ITEMS"]:
            q = int(_get(prices, item, 0) or 0)
            if q >= CFG["G"] * _BASEP[item]:
                continue
            idx = [i for i, o in enumerate(market) if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item]
            if not idx:
                continue
            want = sum(int(market[i][2]) for i in idx)
            allow = 0
            if step % 4 == 1:
                allow = int(_math.ceil(CFG["FRAC"] * _cons(shops, step - 1, item)))
            if allow >= want:
                continue
            # keep the shed from overflowing: projected shed with the capped sells must stay under 100 - ROOM
            trial = [list(o) for o in market]
            left = allow
            for i in idx:
                n = min(int(trial[i][2]), left)
                trial[i][2] = n
                left -= n
            pshed, pinvs = _PROJECT(observation, dict(a, market=[o for o in trial if o and not (o[0] == "SELL" and len(o) >= 3 and int(o[2]) <= 0)]))[:2]
            carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
            over = sum(int(v) for v in pshed.values()) + carried - (100 - CFG["ROOM"])
            if over > 0:
                allow = min(want, allow + over)
                left = allow
                trial = [list(o) for o in market]
                for i in idx:
                    n = min(int(trial[i][2]), left)
                    trial[i][2] = n
                    left -= n
            TEL["cuts"] += 1
            TEL["units_held"] += want - allow
            if allow > 0 and step % 4 == 1:
                TEL["drip_sells"] += 1
            market = trial
            changed = True
        if changed:
            a = dict(a)
            a["market"] = [o for o in market if not (o and o[0] == "SELL" and len(o) >= 3 and int(o[2]) <= 0)][:10]
    except Exception:
        pass
    return a
'''


def main():
    name = sys.argv[1]
    kv = dict(x.split("=", 1) for x in sys.argv[2:])
    cfg = {"ITEMS": kv.get("ITEMS", "WOOL").split(","), "G": float(kv.get("G", 0.8)), "FRAC": float(kv.get("FRAC", 0.5)),
           "FROM_DAY": int(kv.get("FROM_DAY", 10)), "UNTIL": int(kv.get("UNTIL", 690)),
           "SKIP_H": [int(h) for h in kv.get("SKIP_H", "22,23").split(",") if h], "ROOM": int(kv.get("ROOM", 8))}
    base = os.path.abspath(kv.get("BASE", os.path.join(ROOT, "submissions", "v12_3_own_cha22_tick_fade_resume_late_sched_trap",
                                                        "main.py")))
    out = os.path.join(ROOT, "gold", "front", "var", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(
        CODE.replace("__BASE__", repr(base)).replace("__CFG__", repr(cfg)))
    print(out, cfg)


if __name__ == "__main__":
    main()
