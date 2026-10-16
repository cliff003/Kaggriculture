r"""Same-step churn layer over v7b (team 42 experiment, 2026-09-25).

    .venv\Scripts\python.exe gold\churn\mk_churn.py OUT_NAME [WHEAT=all|mirror|off] [N=60] [FERT=off|mirror] [M=30]
                                                  [FROM_DAY=1] [RESERVE=800]

WHEAT: slot 0 BUY_PRODUCT WHEAT n + last slot SELL WHEAT n (a round trip nets zero unless the rival trades wheat in
between: its buys then cost more and our sell-back earns more). all = every step; mirror = only steps whose own
action already buys wheat (a mirror rival usually buys in the same step).
FERT: when our own action sells fertilizer, sell m more at slot 0 and buy m back at the last slot.
Sizes are capped by free shed room (projected after this step's unit actions) and by cash left for our own orders.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CODE = r'''
_BASE_PATH = r"/Users/cliff/Documents/coding/kaggriculture_handoff_20260927/project/submissions/v7b_own_cha22_eager_wheatlead/main.py"
_NS = {"__name__": "churn_base"}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
_BASE = _NS["agent"]
_PROJECT = _NS["_project"]
CFG = %r
TEL = {"wheat_churns": 0, "wheat_units": 0, "fert_churns": 0, "fert_units": 0}
_FIB = [1, 1]
while len(_FIB) < 40:
    _FIB.append(_FIB[-1] + _FIB[-2])
_PRICE = {"COW": 400, "SHEEP": 500, "GOOSE": 300}
_SEED = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}


def _spend(obs, market, hires_today):
    prices = obs["market"]["prices"]
    s = 0.0
    h = hires_today
    for o in market:
        if not o:
            continue
        if o[0] == "HIRE":
            s += _FIB[min(39, h)]
            h += 1
        elif o[0] == "BUY_LAND":
            s += 4000
        elif o[0] == "BUY_ANIMAL" and len(o) >= 3:
            s += _PRICE.get(o[1], 500) * int(o[2])
        elif o[0] == "BUY_SEED" and len(o) >= 3:
            s += _SEED.get(o[1], 100) * int(o[2])
        elif o[0] == "BUY_PRODUCT" and len(o) >= 3:
            s += (int(prices.get(o[1], 50)) + 6) * int(o[2])
    return s


def agent(observation, configuration=None):
    a = _BASE(observation, configuration)
    try:
        step = int(observation["step"])
        if step // 24 < CFG["FROM_DAY"] or step >= 718 or not isinstance(a, dict):
            return a
        me = int(observation["player"])
        farm = observation["farms"][me]
        market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple)) and o]
        pshed = _PROJECT(observation, dict(a, market=market))[0]
        room = 100 - sum(int(v) for v in pshed.values())
        money = float(farm["money"])
        spend = _spend(observation, market, int(farm.get("hires_today", 0) or 0))
        prices = observation["market"]["prices"]
        front, back = [], []
        mode = CFG["WHEAT"]
        buys_wheat = any(o[0] == "BUY_PRODUCT" and len(o) > 1 and o[1] == "WHEAT" for o in market)
        if mode != "off" and (mode == "all" or buys_wheat) and len(market) <= 8:
            px = int(prices.get("WHEAT", 40)) + 6
            n = min(int(CFG["N"]), room - 5, int((money - spend - CFG["RESERVE"]) // max(1, px)))
            if n >= 10:
                front.append(["BUY_PRODUCT", "WHEAT", n])
                back.append(["SELL", "WHEAT", n])
                TEL["wheat_churns"] += 1
                TEL["wheat_units"] += n
                room -= 0
        if CFG["FERT"] != "off" and len(market) + len(front) + len(back) <= 8:
            sells_f = [o for o in market if o[0] == "SELL" and len(o) >= 3 and o[1] == "FERTILIZER"]
            if sells_f:
                have = int(pshed.get("FERTILIZER", 0))
                m = min(int(CFG["M"]), have)
                fpx = int(prices.get("FERTILIZER", 50)) + 6
                if m >= 5 and money - spend - m * fpx >= CFG["RESERVE"]:
                    front.append(["SELL", "FERTILIZER", m])
                    back.insert(0, ["BUY_PRODUCT", "FERTILIZER", m])
                    TEL["fert_churns"] += 1
                    TEL["fert_units"] += m
        if not front:
            return a
        new = front + market
        while len(new) + len(back) < 10:
            new.append([])
        new += back
        a = dict(a)
        a["market"] = new[:10]
    except Exception:
        pass
    return a
'''


def main():
    name = sys.argv[1]
    kv = dict(x.split("=", 1) for x in sys.argv[2:])
    cfg = {"WHEAT": kv.get("WHEAT", "all"), "N": int(kv.get("N", 60)), "FERT": kv.get("FERT", "off"),
           "M": int(kv.get("M", 30)), "FROM_DAY": int(kv.get("FROM_DAY", 1)), "RESERVE": float(kv.get("RESERVE", 800))}
    out = os.path.join(ROOT, "gold", "builds", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(CODE % (cfg,))
    print(out, cfg)


if __name__ == "__main__":
    main()
