r"""Fertilizer sandwich layer (team 42 experiment, 2026-09-26).

    .venv\Scripts\python.exe gold\front\mk_fsand.py OUT_NAME [X=30] [PLACE=merge|front|front3] [FROM_DAY=6]
        [UNTIL=700] [RESERVE=1500] [BASE=submissions/v12_1_own_cha22_tick_fade_resume_late/main.py]

Fertilizer is priced linearly (0.2 per unit) and nothing but the players trades it, so in a step where the rival
sells fertilizer, fertilizer we sell ahead of it and buy back in the last slot earns 0.2 per unit per rival unit sold
in between, and the rival's units sell 0.2 per unit lower per unit we sold ahead: a round trip with no rival trade in
between nets exactly zero. Family rivals run our route tape, so they sell fertilizer in the steps where our base does.
In every step (FROM_DAY to UNTIL) where the base's final list sells fertilizer, s = min(X, shed fertilizer left after
the base's own orders and pickups) extra units are sold and X units are bought back in the last slot (padding with
empty orders), keeping a lot of about X in the shed. PLACE: merge = add s to the base's first fertilizer sell;
front = a separate sell in slot 0; front3 = slot 0 unless slot 0 already sells a premium good, else merge.
From UNTIL on nothing is bought back and the lot is sold with the base's fertilizer sells.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CODE = r'''
_BASE_PATH = __BASE__
_NS = {"__name__": "fsand_base"}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
_BASE = _NS["agent"]
_PROJECT = _NS["_project"]
CFG = __CFG__
TEL = {"sandwiches": 0, "extra_sold": 0, "bought_back": 0, "skipped_full": 0}
_PREMIUM = {"MILK", "WOOL", "STRAWBERRY", "MELON", "EGG", "TOMATO", "CARROT"}


def _get(o, k, d=None):
    try:
        return o[k]
    except Exception:
        return getattr(o, k, d)


def _pad_last(market, order):
    if len(market) >= 10:
        slot = next((i for i, o in enumerate(market) if not o), None)
        if slot is None:
            return False
        market.pop(slot)
    while len(market) < 9:
        market.append([])
    market.append(order)
    return True


def agent(observation, configuration=None):
    a = _BASE(observation, configuration)
    try:
        if not isinstance(a, dict):
            return a
        step = int(_get(observation, "step", 0))
        if step // 24 < CFG["FROM_DAY"] or step > 717:
            return a
        market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple))]
        live = [o for o in market if o]
        fidx = next((i for i, o in enumerate(market) if o and o[0] == "SELL" and len(o) >= 3 and o[1] == "FERTILIZER"), None)
        if fidx is None:
            return a
        pshed = _PROJECT(observation, dict(a, market=live))[0]
        spare = max(0, int(pshed.get("FERTILIZER", 0)))
        s = min(CFG["X"], spare)
        back = (CFG["X"] if not CFG.get("PURE") else s) if step < CFG["UNTIL"] else 0
        if s <= 0 and back <= 0:
            return a
        me = int(_get(observation, "player", 0))
        money = float(_get(_get(observation, "farms")[me], "money", 0))
        quote = int(_get(_get(_get(observation, "market", {}) or {}, "prices", {}) or {}, "FERTILIZER", 50))
        if back and money - CFG["RESERVE"] < back * (quote + 5):
            back = 0
        changed = False
        if s > 0:
            place = CFG["PLACE"]
            first = next((o for o in market if o), None)
            if place == "front3":
                place = "merge" if (first and first[0] == "SELL" and len(first) >= 2 and first[1] in _PREMIUM) else "front"
            if place == "front" and fidx != 0 and len(live) < 10:
                market.insert(0, ["SELL", "FERTILIZER", s])
            else:
                market[fidx][2] = int(market[fidx][2]) + s
            TEL["extra_sold"] += s
            changed = True
        if back > 0:
            if _pad_last(market, ["BUY_PRODUCT", "FERTILIZER", back]):
                TEL["bought_back"] += back
                changed = True
            else:
                TEL["skipped_full"] += 1
        if changed:
            TEL["sandwiches"] += 1
            a = dict(a)
            a["market"] = market[:10]
    except Exception:
        pass
    return a
'''


def main():
    name = sys.argv[1]
    kv = dict(x.split("=", 1) for x in sys.argv[2:])
    cfg = {"X": int(kv.get("X", 30)), "PLACE": kv.get("PLACE", "merge"), "FROM_DAY": int(kv.get("FROM_DAY", 6)),
           "UNTIL": int(kv.get("UNTIL", 700)), "RESERVE": float(kv.get("RESERVE", 1500)), "PURE": int(kv.get("PURE", 0))}
    base = os.path.abspath(kv.get("BASE", os.path.join(ROOT, "submissions", "v12_1_own_cha22_tick_fade_resume_late", "main.py")))
    out = os.path.join(ROOT, "gold", "front", "var", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(
        CODE.replace("__BASE__", repr(base)).replace("__CFG__", repr(cfg)))
    print(out, cfg)


if __name__ == "__main__":
    main()
