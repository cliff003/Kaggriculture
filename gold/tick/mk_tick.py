r"""Tick-arbitrage layer over v7b (team 42 experiment, 2026-09-25; idea from Otter Vibe, LB #15).

    .venv\Scripts\python.exe gold\tick\mk_tick.py OUT_NAME [FROM_DAY=10] [NMAX=95] [RESERVE=1500] [MIN_GAIN=3]
                                                 [MARGIN=3] [BASE=path]

The town eats wheat right after the market at every step s with s % 4 == 0 (one unit per unlocked wheat shop, plus one
at s % 24 == 0). Buying N wheat in the last order slot of such a step and selling the same N at s + 1 earns roughly
c * (price(deficit + N) - price(deficit)): the c units the town eats come out of a market we have pushed up the curve.
N is capped by shed room that stays safe even if every unit drops its whole bag at s + 1, and by spare cash.
At s + 1 the base agent sees the shed without the churn wheat; the churn sell joins its wheat sell or goes right after
its leading sells, so its first-slot sells keep their positions.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_BASE = os.path.join(ROOT, "submissions", "v7b_own_cha22_eager_wheatlead", "main.py")

CODE = r'''
import copy as _copy
import math as _math
_BASE_PATH = __BASE__
_NS = {"__name__": "tick_base"}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
_BASE = _NS["agent"]
_PROJECT = _NS["_project"]
CFG = __CFG__
TEL = {"buys": 0, "units": 0, "sold": 0, "skips_full": 0, "carry": 0}
_WSHOPS = {"BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "ICE_CREAM_SHOP", "FARMERS_MARKET"}
_FIB = [1, 1]
while len(_FIB) < 40:
    _FIB.append(_FIB[-1] + _FIB[-2])
_PRICE = {"COW": 400, "SHEEP": 500, "GOOSE": 300}
_SEED = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
_AMP_B = 0.8 * 25 / _math.sqrt(400)
_AMP_A = 0.2 * 25 / _math.log(401)
_MEM = {}
_SHED = frozenset(((4, 4), (5, 4), (4, 5), (5, 5)))
_MOVES = {"MOVE_UP": (0, -1), "MOVE_DOWN": (0, 1), "MOVE_LEFT": (-1, 0), "MOVE_RIGHT": (1, 0),
          "UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0),
          "NORTH": (0, -1), "SOUTH": (0, 1), "WEST": (-1, 0), "EAST": (1, 0)}


def _wp(inv):
    if inv < 10000:
        p = 25 + _AMP_B * _math.sqrt(10000 - inv)
    else:
        p = 25 - _AMP_A * _math.log(1 + inv - 10000)
    return max(1, int(round(p)))


def _get(o, k, d=None):
    try:
        return o[k]
    except Exception:
        return getattr(o, k, d)


def _spend(prices, market, hires_today):
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
            s += (int(_get(prices, o[1], 50)) + 6) * int(o[2])
    return s


def _net_wheat(market):
    n = 0
    for o in market:
        if o and len(o) >= 3 and o[1] == "WHEAT":
            if o[0] == "SELL":
                n += int(o[2])
            elif o[0] == "BUY_PRODUCT":
                n -= int(o[2])
    return n


def _doctor(observation, hide):
    obs = _copy.deepcopy(observation)
    priv = _get(obs, "private")
    shed = dict(_get(priv, "shed", {}) or {})
    shed["WHEAT"] = max(0, int(shed.get("WHEAT", 0)) - hide)
    try:
        priv["shed"] = shed
    except Exception:
        setattr(priv, "shed", shed)
    return obs


def _cons(observation, step):
    if step % 4 != 0:
        return 0
    town = _get(observation, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    return sum(1 for s in shops if s in _WSHOPS) + (1 if step % 24 == 0 else 0)


def _track(mem, observation, step, a):
    """Infer the rival's net wheat flow of the previous step from the market identity
    dI = our net sold + rival net sold - town use; flag a rival that buys at s % 4 == 0 and sells at s + 1."""
    mk = _get(observation, "market", {}) or {}
    inv_w = int((_get(mk, "inventory", {}) or {}).get("WHEAT", 10000))
    w_now = int((_get(_get(observation, "private"), "shed", {}) or {}).get("WHEAT", 0))
    prev = mem.get("prev")
    if prev is not None and prev["step"] == step - 1 and prev["step"] % 24 != 23:
        our_net = prev["w_units"] - w_now
        mem["flow"][prev["step"]] = (inv_w - prev["inv"]) - our_net + prev["cons"]
    try:
        w_units = int(_PROJECT(observation, dict(a, market=[]))[0].get("WHEAT", 0))
    except Exception:
        w_units = w_now
    mem["prev"] = {"step": step, "inv": inv_w, "w_units": w_units, "cons": _cons(observation, step)}
    if not mem["rival"] and step % 4 == 2:
        fl = mem["flow"]
        hits = 0
        for s0 in range(step - 2, step - 2 - 4 * CFG["WIN"], -4):
            if fl.get(s0, 0) <= -CFG["TH"] and fl.get(s0 + 1, 0) >= CFG["TH"]:
                hits += 1
        if hits >= CFG["HITS"]:
            mem["rival"] = True
            TEL["rival_step"] = step


def _decide(observation, configuration=None):
    try:
        step = int(_get(observation, "step", 0))
        me = int(_get(observation, "player", 0))
    except Exception:
        return _BASE(observation, configuration)
    mem = _MEM.setdefault(me, {"pend": None, "last": -1})
    if step <= mem["last"]:
        mem.clear()
        mem.update({"pend": None, "last": -1})
    mem.setdefault("flow", {})
    mem.setdefault("rival", False)
    mem["last"] = step
    pend = mem["pend"]
    hide = 0
    if pend is not None:
        try:
            shed_w = int((_get(_get(observation, "private"), "shed", {}) or {}).get("WHEAT", 0))
            hide = max(0, min(pend["n"], shed_w - pend["without"]))
        except Exception:
            hide = 0
    obs_in = observation
    if hide > 0:
        try:
            obs_in = _doctor(observation, hide)
        except Exception:
            obs_in = observation
    a = _BASE(obs_in, configuration)
    try:
        if not isinstance(a, dict):
            return a
        market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple)) and o]
        if pend is not None:
            mem["pend"] = None
            if hide > 0:
                placed = False
                if CFG["SELLSLOT"] == "first" and len(market) < 10:
                    market.insert(0, ["SELL", "WHEAT", hide])
                    placed = True
                for o in ([] if placed else market):
                    if o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT":
                        o[2] = int(o[2]) + hide
                        placed = True
                        break
                if not placed and len(market) < 10:
                    i = 0
                    while i < len(market) and market[i][0] == "SELL":
                        i += 1
                    market.insert(i, ["SELL", "WHEAT", hide])
                    placed = True
                if placed:
                    TEL["sold"] += hide
                else:
                    TEL["carry"] += 1
                    mem["pend"] = {"n": hide, "without": pend["without"], "step": step}
            a = dict(a)
            a["market"] = market
            if mem["pend"] is not None:
                return a
        if step % 4 != 0 or step // 24 < CFG["FROM_DAY"] or step > 716:
            return a
        if mem.get("rival"):
            TEL["rival_skips"] = TEL.get("rival_skips", 0) + 1
            return a
        if len(market) >= 10:
            TEL["skips_full"] += 1
            return a
        town = _get(observation, "town", {}) or {}
        shops = list(_get(town, "unlocked_shops", []) or [])
        c = sum(1 for s in shops if s in _WSHOPS) + (1 if step % 24 == 0 else 0)
        if c <= 0:
            return a
        mk = _get(observation, "market", {}) or {}
        inv_w = int((_get(mk, "inventory", {}) or {}).get("WHEAT", 10000))
        prices = _get(mk, "prices", {}) or {}
        proj = _PROJECT(observation, dict(a, market=market))
        pshed, pinvs = proj[0], proj[1]
        carried = 0
        if CFG["NEAR"]:
            me_f = _get(observation, "farms")[me]
            pos = [tuple(_get(me_f, "farmer"))] + [tuple(h) for h in (_get(me_f, "hands", []) or [])]
            units = [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
            for idx, inv in enumerate(pinvs):
                if idx >= len(pos):
                    break
                x, y = pos[idx]
                act = units[idx] if idx < len(units) else ["PASS"]
                if isinstance(act, list) and act and act[0] in _MOVES:
                    dx, dy = _MOVES[act[0]]
                    x, y = x + dx, y + dy
                if (x, y) in _SHED:
                    carried += sum(int(v) for v in inv.values() if int(v) > 0)
        else:
            carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
        room = 100 - sum(int(v) for v in pshed.values()) - carried - CFG["MARGIN"]
        me_farm = _get(observation, "farms")[me]
        money = float(_get(me_farm, "money", 0))
        spend = _spend(prices, market, int(_get(me_farm, "hires_today", 0) or 0))
        cash = money - spend - CFG["RESERVE"]
        I = inv_w + _net_wheat(market)
        n = min(int(CFG["NMAX"]), room)
        TEL["lim_room"] = TEL.get("lim_room", 0) + (room < int(CFG["NMAX"]))
        cost = 0
        k = 0
        while k < n:
            p = _wp(I - k - 1)
            if cost + p > cash:
                break
            cost += p
            k += 1
        TEL["lim_cash"] = TEL.get("lim_cash", 0) + (k < n)
        n = k
        if n < 10:
            return a
        gain = sum(_wp(I - j) for j in range(n + 1, n + c + 1)) - sum(_wp(I - j) for j in range(1, c + 1))
        if gain < CFG["MIN_GAIN"]:
            return a
        if CFG["BUYSLOT"] == "pad":
            while len(market) < 9:
                market.append([])
        market.append(["BUY_PRODUCT", "WHEAT", n])
        mem["pend"] = {"n": n, "without": int(pshed.get("WHEAT", 0)), "step": step}
        TEL["buys"] += 1
        TEL["units"] += n
        a = dict(a)
        a["market"] = market
    except Exception:
        pass
    return a


def agent(observation, configuration=None):
    a = _decide(observation, configuration)
    try:
        if CFG["GUARD"] and isinstance(a, dict):
            step = int(_get(observation, "step", 0))
            me = int(_get(observation, "player", 0))
            _track(_MEM[me], observation, step, a)
    except Exception:
        pass
    return a
'''


def main():
    name = sys.argv[1]
    kv = dict(x.split("=", 1) for x in sys.argv[2:])
    cfg = {"FROM_DAY": int(kv.get("FROM_DAY", 10)), "NMAX": int(kv.get("NMAX", 95)),
           "RESERVE": float(kv.get("RESERVE", 1500)), "MIN_GAIN": float(kv.get("MIN_GAIN", 3)),
           "MARGIN": int(kv.get("MARGIN", 3)), "NEAR": int(kv.get("NEAR", 1)),
           "BUYSLOT": kv.get("BUYSLOT", "append"), "SELLSLOT": kv.get("SELLSLOT", "after"),
           "GUARD": int(kv.get("GUARD", 1)), "TH": int(kv.get("TH", 30)), "WIN": int(kv.get("WIN", 8)),
           "HITS": int(kv.get("HITS", 2))}
    base = kv.get("BASE", DEFAULT_BASE)
    out = os.path.join(ROOT, "gold", "builds", name)
    os.makedirs(out, exist_ok=True)
    src = CODE.replace("__BASE__", repr(base)).replace("__CFG__", repr(cfg))
    if kv.get("SELF", "0") == "1":
        # self-contained: base source verbatim, then the layer in its own namespace (its helper names would
        # otherwise shadow the base's module globals), bound to the base agent and its _project
        head = src.split("_NS = {", 1)[0]
        body = src.split('_PROJECT = _NS["_project"]', 1)[1]
        imports = [l for l in head.splitlines() if l.startswith("import ")]
        layer = chr(10).join(imports) + body
        assert "'''" not in layer
        note = ["", "", "# " + "-" * 75,
                "# Team 42 TICK layer (outermost), 2026-09-25: wheat tick arbitrage. The town eats wheat right after",
                "# the market of every step s with s % 4 == 0. At such steps (day 10 on) buy up to N wheat in the last",
                "# order slot, N capped by shed room that stays safe if every unit ending the step on a shed tile drops",
                "# its bag at s + 1, and by spare cash; sell the same wheat at s + 1 (joined to the base wheat sell or",
                "# right after the leading sells). The base policy sees the shed without that wheat. Stops for the rest",
                "# of the game once the rival is seen doing the same (its wheat flow is inferred from the market).",
                "_TICK_SRC = r'''" + layer + "'''",
                "_PRE_TICK_AGENT = globals().pop(\"agent\")   # pop first: the loader takes the last callable in module order",
                "_TICK_NS = {\"__name__\": \"tick_layer\", \"_BASE\": _PRE_TICK_AGENT, \"_PROJECT\": _project}",
                "exec(compile(_TICK_SRC, \"tick_layer\", \"exec\"), _TICK_NS)",
                "_TICK = _TICK_NS[\"agent\"]",
                "",
                "",
                "def agent(observation, configuration=None):",
                "    return _TICK(observation, configuration)",
                ""]
        src = open(base, encoding="utf-8").read().rstrip(chr(10)) + chr(10).join(note)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(src)
    print(out, cfg)


if __name__ == "__main__":
    main()
