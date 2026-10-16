r"""Build the two wrappers of the opponent-foresight test.

    .venv\Scripts\python.exe gold\oracle\mk_oracle.py bus OPP_MAIN_PY OUT_NAME
    .venv\Scripts\python.exe gold\oracle\mk_oracle.py ours OUR_MAIN_PY OUT_NAME [MODE=reorder|extra|off] [ITEMS=...]

bus: runs the opponent unchanged and records each step's action in oracle_bus.OPP (it must sit in seat 0).
ours: runs our agent, then (seat 1) rewrites its market list with the opponent's same-step orders in view:
  - our SELL of an item the opponent also sells goes before its first sell of that item;
  - our SELL of an item the opponent buys goes after its last buy of that item (padding with [] slots);
  - our BUY_PRODUCT of an item the opponent sells goes after its last sell;
  - MODE=extra also adds a SELL of everything in our shed of an item the opponent sells now (ITEMS filter).
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TOOLS = os.path.join(ROOT, "gold", "tools")

HEAD = r'''
import copy as _copy
import sys as _sys
_TOOLS = %r
if _TOOLS not in _sys.path:
    _sys.path.insert(0, _TOOLS)
import oracle_bus as _BUS
_INNER_SRC_PATH = %r


def _load_inner():
    from kaggle_environments.agent import get_last_callable
    import contextlib, io, os
    raw = open(_INNER_SRC_PATH, encoding="utf-8").read()
    with contextlib.redirect_stdout(io.StringIO()):
        return get_last_callable(raw, path=os.path.abspath(_INNER_SRC_PATH))


_INNER = _load_inner()


def _call_inner(obs, cfg):
    co = getattr(_INNER, "__code__", None)
    if co is not None and co.co_argcount < 2:
        return _INNER(obs)
    return _INNER(obs, cfg)
'''

BUS = r'''

def agent(observation, configuration=None):
    a = _call_inner(observation, configuration)
    try:
        _BUS.OPP[int(observation["step"])] = _copy.deepcopy(a)
    except Exception:
        pass
    return a
'''

OURS = r'''
MODE = %r
ITEMS = %r
STATS = {"steps": 0, "reordered": 0, "extra": 0}


def _reorder(ours, theirs, shed):
    ts_sell_min, ts_sell_max, ts_buy_max = {}, {}, {}
    for i, o in enumerate(theirs or []):
        if not isinstance(o, list) or len(o) < 2:
            continue
        if o[0] == "SELL":
            ts_sell_min.setdefault(o[1], i)
            ts_sell_max[o[1]] = i
        elif o[0] == "BUY_PRODUCT":
            ts_buy_max[o[1]] = i
    early, mid_sell, mid_other, late = [], [], [], []
    selling = set()
    for o in ours or []:
        if not isinstance(o, list) or not o:
            continue
        op = o[0]
        it = o[1] if len(o) > 1 else None
        if op == "SELL":
            selling.add(it)
            if it in ts_buy_max:
                late.append((ts_buy_max[it] + 1, o))
            elif it in ts_sell_min:
                early.append((ts_sell_min[it], o))
            else:
                mid_sell.append(o)
        elif op == "BUY_PRODUCT" and it in ts_sell_max:
            late.append((ts_sell_max[it] + 1, o))
        else:
            mid_other.append(o)
    if MODE == "extra":
        for it, slot in ts_sell_min.items():
            if it in selling or it not in ITEMS or it in ts_buy_max:
                continue
            n = int(shed.get(it, 0) or 0)
            if n > 0:
                early.append((slot, ["SELL", it, n]))
                STATS["extra"] += 1
    early.sort(key=lambda x: x[0])
    out = [o for _, o in early] + mid_sell + mid_other
    for need, o in sorted(late, key=lambda x: x[0]):
        while len(out) < need and len(out) < 9:
            out.append([])
        out.append(o)
    return out[:10]


SAND_N = 60
SAND_M = 30
SAND_MIN_SLOT = 0


def _sandwich(obs, a, theirs):
    """Oracle sandwich: our round trip around the rival's same-step wheat/fertilizer orders, direction chosen so
    that its trade gets the worse price (rival buys: we buy first, sell back last; rival sells: we sell first,
    buy back last). Our own orders stay in between."""
    market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple)) and o]
    me = int(obs["player"])
    farm = obs["farms"][me]
    shed = dict(obs["private"]["shed"])
    prices = obs["market"]["prices"]
    room = 100 - sum(int(v) for v in shed.values())
    money = float(farm["money"])
    front, back = [], []
    for item, n_max in (("WHEAT", SAND_N), ("FERTILIZER", SAND_M)):
        buys = [k for k, o in enumerate(theirs or []) if isinstance(o, list) and len(o) >= 3 and o[0] == "BUY_PRODUCT" and o[1] == item]
        sells = [k for k, o in enumerate(theirs or []) if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and o[1] == item]
        if buys and not sells and min(buys) >= SAND_MIN_SLOT:
            px = int(prices.get(item, 40)) + 6
            n = min(n_max, room - 10, int((money - 3000) // max(1, px)))
            if n >= 5:
                front.append(["BUY_PRODUCT", item, n])
                back.append(["SELL", item, n])
                room -= n
                STATS["sand_buy"] = STATS.get("sand_buy", 0) + 1
        elif sells and not buys and min(sells) >= SAND_MIN_SLOT and item == "FERTILIZER":
            ours = sum(int(o[2]) for o in market if o[0] == "SELL" and len(o) >= 3 and o[1] == item)
            have = int(shed.get(item, 0)) - ours
            m = min(n_max, have)
            px = int(prices.get(item, 40)) + 6
            if m >= 5 and money - 3000 >= m * px:
                front.append(["SELL", item, m])
                back.append(["BUY_PRODUCT", item, m])
                STATS["sand_sell"] = STATS.get("sand_sell", 0) + 1
    if not front or len(market) + len(front) + len(back) > 10:
        return a
    new = front + market
    while len(new) + len(back) < 10:
        new.append([])
    new += back
    a = dict(a)
    a["market"] = new
    return a


def agent(observation, configuration=None):
    a = _call_inner(observation, configuration)
    if MODE == "off":
        return a
    if MODE == "sandwich":
        try:
            opp = _BUS.OPP.get(int(observation["step"]))
            if opp is not None and isinstance(a, dict) and int(observation["step"]) < 718:
                a = _sandwich(observation, a, opp.get("market", []) if isinstance(opp, dict) else [])
        except Exception:
            pass
        return a
    try:
        step = int(observation["step"])
        opp = _BUS.OPP.get(step)
        STATS["steps"] += 1
        if opp is not None and isinstance(a, dict):
            theirs = opp.get("market", []) if isinstance(opp, dict) else []
            shed = dict(observation["private"]["shed"])
            new = _reorder(a.get("market", []), theirs, shed)
            if new != a.get("market", []):
                STATS["reordered"] += 1
            a = dict(a)
            a["market"] = new
    except Exception:
        pass
    return a
'''


def main():
    kind, src, name = sys.argv[1], os.path.abspath(sys.argv[2]), sys.argv[3]
    kv = dict(x.split("=", 1) for x in sys.argv[4:])
    code = HEAD % (TOOLS, src)
    if kind == "bus":
        code += BUS
    else:
        items = tuple((kv.get("ITEMS") or "MILK,WOOL,STRAWBERRY,EGG,TOMATO,CARROT,MELON").split(","))
        code += OURS % (kv.get("MODE", "reorder"), items)
    out = os.path.join(ROOT, "gold", "builds", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(code)
    print(os.path.join(out, "main.py"))


if __name__ == "__main__":
    main()
