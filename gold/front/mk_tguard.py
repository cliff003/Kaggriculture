r"""Tick-trap guard layer (team 42 experiment, 2026-09-26).

    .venv\Scripts\python.exe gold\front\mk_tguard.py OUT_NAME [ACT=1] [K=4] [NB=3] [BAD=40] [LOSS=0] [PREBUY=1] [TH=25] [HITS=2]
        [WIN=8] [BASE=submissions/v12_2_own_cha22_tick_fade_resume_late_sched/main.py]

Some rivals now trap the TICK layer's wheat round trip:
  sandwich: at s % 4 == 0 they buy 80-90 wheat in slot 0 (lifting the price) and sell the same amount in slot 9, where
            it fills in lockstep against our last-slot tick buy, so we pay the lifted price; their net wheat flow is 0,
            so the TICK guard (which reads the rival's net flow) never sees them (Sho Saga, lumen, emreaydin, URAD).
  prebuy:   they buy 35-60 wheat one step before our tick buy and sell it together with our tick sell (Takahiro
            Katsumata, Kaggriculture Agent).
Money moves only in the market, so this layer simulates the cash of our own final order list alone with the engine's
rules each step (exact unless the rival trades the same item that step) and reads the realized cash one step later.
dev = realized - simulated. A tick cycle's dev is the sum over its buy step and its sell step. A step is clean when
no other product we traded that step shows rival trading in the market identity (inventory change = our units -
town consumption, engine _town_consume); only clean cycles count. When NB of the last K
cycles have dev <= -BAD (or, with LOSS > 0, the last K lose more than LOSS in total), TICK is paused for the rest of
the game (the TICK layer's rival flag is held on). Normal games: 37 of 745 cycles <= -40, never 3 of 4 in a row.
PREBUY: also pause after HITS cycles in the last WIN where the rival's inferred net wheat flow was a buy of TH+ at
s0 - 1 and a sell of TH+ at s0 + 1. ACT=0 only measures (TEL).
CF=1 (sandwich fade, armed when the dev rule fires): at s % 4 == 0 sell up to CF_X wheat (keeping the route's next 2
steps of feed pickups) in slot CF_SLOT or later but before slot 9, i.e. after the rival's slot-0/1 lifting buy and ahead
of its slot-9 sell; at every s % 4 == 1 step top the counter's own lot up to CF_X in the last slot, within shed room
and cash. Against a prebuyer only the counter's own lot is sold (the base's wheat feeds its animals; selling it cost
1.8k in one replay); against a sandwich (CF_SPARE0=1) the base's spare wheat beyond the next CF_PICK steps of pickups
is sold too (the 80-unit lift pays for rebuying feed later). The lot is clipped to
the shed's wheat each step, restocking stops 12 steps before CF_UNTIL and what is left is sold after CF_UNTIL. CF_PREBUY=1: a rival
flagged by the prebuy rule gets the same counter with the sell at s % 4 == 3 (after its slot-0 buy there). A counter cycle's dev (both steps) is its
excess over trading alone (the rival's lift); when none of the last CF_K clean cycles reached CF_SPIKE the counter
stops for the game (intermittent trappers lift every second or third cycle by 100-360; without a lift a cycle's dev
is 0-25 and the cycle costs about 10: the lot is bought back after one town meal).
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LAYER = r'''
import math as _math
CFG = __CFG__
TEL = {"devs": [], "cycles": [], "trap_step": None, "prebuy_step": None}
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
_SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
_ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
_LAND = [1000, 2000, 4000]
_FIBS = [1, 1]
while len(_FIBS) < 60:
    _FIBS.append(_FIBS[-1] + _FIBS[-2])


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


def _cons(shops, step):
    """Town consumption of every product after the market of `step` (engine _town_consume)."""
    c = {}
    if step % 4 == 0:
        for sh in shops:
            prods = _SHOPS.get(sh, [])
            m = 2 if len(prods) == 1 else 1
            for it in prods:
                c[it] = c.get(it, 0) + m
    if step % 24 == 0:
        for it in _MP:
            if it != "FERTILIZER":
                c[it] = c.get(it, 0) + 1
    return c


def _sim(observation, market, shed0, me):
    """Cash change of our market list alone, engine rules (_process_market / _commit_unit); also our effect on the
    market inventory per item and the items we traded."""
    farm = _get(observation, "farms")[me]
    money = float(_get(farm, "money", 0))
    hires = int(_get(farm, "hires_today", 0) or 0)
    nland = len(list(_get(farm, "unlocked_quadrants", ["NW"]) or ["NW"])) - 1
    inv = {k: int(v) for k, v in dict(_get(_get(observation, "market", {}) or {}, "inventory", {}) or {}).items()}
    inv0 = dict(inv)
    shed = {k: int(v) for k, v in dict(shed0).items()}
    cash = 0.0
    traded = set()
    for o in list(market)[:10]:
        if not isinstance(o, (list, tuple)) or not o:
            continue
        op = o[0]
        if op == "HIRE":
            c = _FIBS[min(59, hires)]
            if money >= c:
                money -= c
                cash -= c
                hires += 1
            continue
        if op == "BUY_LAND":
            if nland < len(_LAND) and money >= _LAND[nland]:
                money -= _LAND[nland]
                cash -= _LAND[nland]
                nland += 1
            continue
        if len(o) < 3:
            continue
        try:
            q = int(o[2])
        except Exception:
            continue
        item = o[1]
        for _ in range(max(0, q)):
            if op == "SELL":
                if item not in _MP or shed.get(item, 0) <= 0:
                    break
                p = _price(item, inv.get(item, 10000))
                shed[item] -= 1
                money += p
                cash += p
                traded.add(item)
                if p > 1:
                    inv[item] = inv.get(item, 10000) + 1
            elif op == "BUY_PRODUCT":
                if item not in ("WHEAT", "FERTILIZER"):
                    break
                p = _price(item, inv.get(item, 10000) - 1)
                if money < p or sum(shed.values()) >= 100:
                    break
                money -= p
                cash -= p
                traded.add(item)
                shed[item] = shed.get(item, 0) + 1
                inv[item] = inv.get(item, 10000) - 1
            elif op == "BUY_SEED":
                p = _SEED_COST.get(item)
                if p is None or money < p:
                    break
                money -= p
                cash -= p
            elif op == "BUY_ANIMAL":
                p = _ANIMAL_COST.get(item)
                if p is None or money < p or sum(shed.values()) >= 100:
                    break
                money -= p
                cash -= p
                shed[item] = shed.get(item, 0) + 1
            else:
                break
    delta = {k: inv[k] - inv0.get(k, 10000) for k in inv if inv[k] != inv0.get(k, 10000)}
    return cash, delta, traded, inv0


_PB_SCHED = {327, 375, 419, 435, 487}


def _prebuy_hits(fl, step):
    """Rival buys TH+ one step before our tick buy (s0 - 1) and unwinds either with our tick sell (s0 + 1) or
    against our tick buy itself in a late slot (s0; the public fixed-step wheat buys at 327/375/419/435/487 are not
    counted, they unwind at s0 too but never trap)."""
    hits = 0
    for s0 in range(step - 2, step - 2 - 4 * CFG["WIN"], -4):
        if fl.get(s0 - 1, 0) <= -CFG["TH"] and (fl.get(s0 + 1, 0) >= CFG["TH"] or
                                                (fl.get(s0, 0) >= CFG["TH"] and (s0 - 1) not in _PB_SCHED)):
            hits += 1
    return hits


def _pickups(me, step, horizon):
    """Wheat the base route's units pick up from the shed in the next `horizon` steps (their feed)."""
    try:
        ns = _NS.get("_BASE_NS") or _NS
        chassis = ns["_IMPL"].chassis
        native = chassis.players.get(me)
        if not native or native.get("route") is None:
            return 0
        total = 0
        for t in range(step + 1, min(719, step + 1 + horizon)):
            tape = chassis.routes.get(2 if t >= 648 else native["route"]) or []
            a = tape[t] if t < len(tape) and isinstance(tape[t], dict) else {}
            for c in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or []):
                if c and c[0] == "PICKUP" and len(c) >= 2 and c[1] == "WHEAT":
                    total += max(0, int(c[2]) if len(c) >= 3 else 1)
        return total
    except Exception:
        return 30


def _place_mid(market, order, lo):
    """Put order at an index in [lo, 8]: after the rival's slot-0/1 lift, before its slot-9 sell."""
    if len(market) <= 8:
        while len(market) < lo:
            market.append([])
        market.append(order)
        return True
    for i in range(lo, 9):
        if not market[i]:
            market[i] = order
            return True
    return False


def _place_last(market, order):
    if len(market) >= 10:
        slot = next((i for i, o in enumerate(market) if not o), None)
        if slot is None:
            return False
        market.pop(slot)
    while len(market) < 9:
        market.append([])
    market.append(order)
    return True


def _counter(observation, a, mem, step, me):
    """Sandwich fade: after the trap is confirmed, sell wheat in a middle slot at s % 4 == 0 (into the rival's slot-0
    lift, ahead of its slot-9 sell) and buy the lot back in the last slot of the next step."""
    market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple))]
    live = [o for o in market if o]
    changed = None
    owned = int(mem.get("cf_owned", 0))
    if step > CFG["CF_UNTIL"] or not mem["cf_on"]:
        if owned > 0 and step <= 717:
            shed_w = int(_PROJECT(observation, dict(a, market=live))[0].get("WHEAT", 0))
            y = int(min(owned, shed_w))
            if y > 0 and len(live) < 10:
                market = live + [["SELL", "WHEAT", y]]
                changed = ("sell", y)
    elif step % 4 == mem.get("cf_phase", 0):
        shed_w = int(_PROJECT(observation, dict(a, market=live))[0].get("WHEAT", 0))
        pick = _pickups(me, step, CFG["CF_PICK"])
        cap = owned if (mem.get("cf_phase", 0) != 0 or not CFG["CF_SPARE0"]) else CFG["CF_X"]
        y = int(min(CFG["CF_X"], cap, shed_w - pick))
        if CFG.get("LOG"):
            TEL.setdefault("cf_log", []).append(("S", step, shed_w, pick, y, len(live)))
        if y >= CFG["CF_MIN_N"] and _place_mid(market, ["SELL", "WHEAT", y], CFG["CF_SLOT"]):
            changed = ("sell", y)
    elif step % 4 == 1 and step <= CFG["CF_UNTIL"] - 12:
        pshed, pinvs = _PROJECT(observation, dict(a, market=live))[:2]
        shed_w = int(pshed.get("WHEAT", 0))
        want = CFG["CF_X"] - owned
        carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3
        farm = _get(observation, "farms")[me]
        quote = int(_get(_get(_get(observation, "market", {}) or {}, "prices", {}) or {}, "WHEAT", 40))
        cash = float(_get(farm, "money", 0)) - CFG["CF_RESERVE"]
        if CFG.get("LOG"):
            TEL.setdefault("cf_log", []).append(("B", step, shed_w, want, room, int(cash)))
        want = int(max(0, min(want, room, cash // max(1, quote + 6))))
        if want < 10:
            want = 0
        if want > 0 and _place_last(market, ["BUY_PRODUCT", "WHEAT", want]):
            changed = ("buy", want)
    if changed is None:
        return a, None
    a = dict(a)
    a["market"] = market[:10]
    return a, changed


def agent(observation, configuration=None):
    try:
        step = int(_get(observation, "step", 0))
        me = int(_get(observation, "player", 0))
    except Exception:
        return _BASE(observation, configuration)
    mem = _MEM.get(me)
    if mem is None or step <= mem["last"]:
        mem = _MEM[me] = {"last": -1, "prev": None, "cyc": None, "cycles": [], "trap": False, "prebuy": False,
                          "cf_on": False, "cf_off": False, "cf_cyc": None, "cf_cycles": [], "cf_sold_step": None}
    mem["last"] = step
    tick_mem = None
    try:
        tick_mem = _NS["_TICK_NS"]["_MEM"].get(me)
        money = float(_get(_get(observation, "farms")[me], "money", 0))
        prev = mem["prev"]
        mem["prev"] = None
        if prev is not None and prev["step"] == step - 1:
            dev = money - prev["money"] - prev["E"]
            inv_now = dict(_get(_get(observation, "market", {}) or {}, "inventory", {}) or {})
            cons = _cons(prev["shops"], prev["step"])
            clean = True
            for it in prev["traded"]:
                if it == "WHEAT":
                    continue
                rf = int(inv_now.get(it, 10000)) - prev["inv"].get(it, 10000) - prev["delta"].get(it, 0) + cons.get(it, 0)
                if rf != 0:
                    clean = False
                    break
            if CFG.get("LOG"):
                TEL["devs"].append((prev["step"], round(dev, 1), prev["tick"], prev["tsell"], prev.get("cf"), clean)
                                   + ((prev.get("mk"), prev.get("shed0")) if CFG.get("LOG", 0) >= 2 else ()))
            cf = prev.get("cf")
            if cf and cf[0] == "sell":
                mem["cf_cyc"] = {"s0": prev["step"], "dev": dev, "clean": clean}
                mem["cf_cyc_s0"] = prev["step"]
            elif cf and cf[0] == "buy" and mem["cf_cyc"] is not None and prev["step"] - mem["cf_cyc"]["s0"] <= 2:
                d = mem["cf_cyc"]["dev"] + dev
                ok = mem["cf_cyc"]["clean"] and clean
                mem["cf_cyc"] = None
                TEL.setdefault("cf_cycles", []).append((mem["cf_cyc_s0"], round(d), ok))
                if ok:
                    mem["cf_cycles"].append(d)
                last = mem["cf_cycles"][-CFG["CF_K"]:]
                if ok and len(last) >= CFG["CF_K"] and max(last) < CFG["CF_SPIKE"]:
                    mem["cf_on"] = False
                    mem["cf_off"] = True
                    TEL["cf_off_step"] = step
            if prev["tick"]:
                mem["cyc"] = {"s0": prev["step"], "dev": dev, "clean": clean}
            elif prev["tsell"] and mem["cyc"] is not None and mem["cyc"]["s0"] == prev["step"] - 1:
                d = mem["cyc"]["dev"] + dev
                ok = mem["cyc"]["clean"] and clean
                mem["cyc"] = None
                TEL["cycles"].append((prev["step"] - 1, round(d), ok))
                if ok:
                    mem["cycles"].append(d)
                last = mem["cycles"][-CFG["K"]:]
                bad = sum(1 for x in last if x <= -CFG["BAD"])
                if ok and not mem["trap"] and prev["step"] <= CFG["UNTIL"] and len(last) >= CFG["K"] and (
                        bad >= CFG["NB"] or (CFG["LOSS"] > 0 and sum(last) < -CFG["LOSS"])):
                    mem["trap"] = True
                    TEL["trap_step"] = step
                    if CFG["CF"] and not mem["cf_off"]:
                        mem["cf_on"] = True
                        mem["cf_phase"] = 0
        if CFG["PREBUY"] and not mem["prebuy"] and tick_mem is not None and step % 4 == 2:
            if _prebuy_hits(tick_mem.get("flow") or {}, step) >= CFG["HITS"]:
                mem["prebuy"] = True
                TEL["prebuy_step"] = step
                if CFG["CF"] and CFG["CF_PREBUY"] and not mem["cf_off"] and not mem["trap"]:
                    mem["cf_on"] = True
                    mem["cf_phase"] = 3
        if CFG["ACT"] and (mem["trap"] or mem["prebuy"]) and tick_mem is not None:
            tick_mem["rival"] = True
    except Exception:
        pass
    pend_before = (tick_mem or {}).get("pend") if tick_mem is not None else None
    a = _BASE(observation, configuration)
    cfd = None
    try:
        if mem.get("cf_owned", 0) > 0:
            shed_now = int((_get(_get(observation, "private"), "shed", {}) or {}).get("WHEAT", 0))
            mem["cf_owned"] = min(mem["cf_owned"], shed_now)
        if CFG["ACT"] and (mem["cf_on"] or mem.get("cf_owned", 0) > 0) and isinstance(a, dict):
            a, cfd = _counter(observation, a, mem, step, me)
            if cfd is not None:
                TEL["cf_" + cfd[0]] = TEL.get("cf_" + cfd[0], 0) + cfd[1]
                if cfd[0] == "sell":
                    mem["cf_sold_step"] = step
                    mem["cf_owned"] = max(0, mem.get("cf_owned", 0) - cfd[1])
                else:
                    mem["cf_owned"] = mem.get("cf_owned", 0) + cfd[1]
    except Exception:
        cfd = None
    try:
        if isinstance(a, dict):
            tick_mem = _NS["_TICK_NS"]["_MEM"].get(me) or {}
            pend = tick_mem.get("pend")
            tick = bool(pend and pend.get("step") == step)
            shed0 = _PROJECT(observation, dict(a, market=[]))[0]
            E, delta, traded, inv0 = _sim(observation, a.get("market") or [], shed0, me)
            shops = list(_get(_get(observation, "town", {}) or {}, "unlocked_shops", []) or [])
            mem["prev"] = {"step": step, "money": float(_get(_get(observation, "farms")[me], "money", 0)), "E": E,
                           "delta": delta, "traded": traded, "inv": inv0, "shops": shops,
                           "tick": tick and pend_before is None, "tsell": pend_before is not None, "cf": cfd}
            if CFG.get("LOG", 0) >= 2:
                mem["prev"]["mk"] = [list(o) for o in (a.get("market") or [])]
                mem["prev"]["shed0"] = dict(shed0)
    except Exception:
        pass
    return a
'''

CODE = r'''
_BASE_PATH = __BASE__
_NS = {"__name__": "tguard_base"}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
_BASE = _NS["agent"]
_PROJECT = _NS["_project"]
''' + LAYER


def cfg_from(kv):
    return {"ACT": int(kv.get("ACT", 1)), "K": int(kv.get("K", 4)), "NB": int(kv.get("NB", 3)),
            "BAD": float(kv.get("BAD", 40)), "LOSS": float(kv.get("LOSS", 0)), "UNTIL": int(kv.get("UNTIL", 700)),
            "PREBUY": int(kv.get("PREBUY", 1)), "TH": int(kv.get("TH", 25)), "HITS": int(kv.get("HITS", 2)),
            "WIN": int(kv.get("WIN", 8)), "LOG": int(kv.get("LOG", 0)),
            "CF": int(kv.get("CF", 0)), "CF_X": int(kv.get("CF_X", 80)), "CF_SLOT": int(kv.get("CF_SLOT", 2)),
            "CF_MIN_N": int(kv.get("CF_MIN_N", 15)), "CF_UNTIL": int(kv.get("CF_UNTIL", 688)),
            "CF_RESERVE": float(kv.get("CF_RESERVE", 1500)), "CF_K": int(kv.get("CF_K", 8)),
            "CF_SPIKE": float(kv.get("CF_SPIKE", 60)), "CF_SPARE0": int(kv.get("CF_SPARE0", 1)), "CF_PICK": int(kv.get("CF_PICK", 2)),
            "CF_STOCK": int(kv.get("CF_STOCK", 1)), "CF_PREBUY": int(kv.get("CF_PREBUY", 1))}


def main():
    name = sys.argv[1]
    kv = dict(x.split("=", 1) for x in sys.argv[2:])
    cfg = cfg_from(kv)
    base = os.path.abspath(kv.get("BASE", os.path.join(ROOT, "submissions", "v12_2_own_cha22_tick_fade_resume_late_sched",
                                                        "main.py")))
    out = os.path.join(ROOT, "gold", "front", "var", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(
        CODE.replace("__BASE__", repr(base)).replace("__CFG__", repr(cfg)))
    print(out, cfg)


if __name__ == "__main__":
    main()
