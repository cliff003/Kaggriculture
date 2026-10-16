r"""Scheduled fade layer (team 42 experiment, 2026-09-26).

    .venv\Scripts\python.exe gold\front\mk_sfade.py OUT_NAME [XMAX=80] [SCHED=327,375,419,435,487] [LEAD=1]
        [RESERVE=1500] [BASE=submissions/v12_1_own_cha22_tick_fade_resume_late/main.py]

About 50 teams run a public layer that buys 63-89 wheat at the fixed steps 327, 375, 419, 435 and 487 (hour 15, 15,
11, 3, 7; s % 4 == 3) and sells it the next step. At step s - LEAD we buy up to XMAX wheat in the last slot; at step
s we sell that lot in the last slot, after the rival's buy has lifted the price. The rival pays the lift of our
early buy and we sell into its lift. Against a rival without the schedule the lot is bought and sold with no town
consumption in between, so it nets about zero. The lot is hidden from the base at step s (it sees its own wheat).
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CODE = r'''
import copy as _copy
_BASE_PATH = __BASE__
_NS = {"__name__": "sfade_base"}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
_BASE = _NS["agent"]
_PROJECT = _NS["_project"]
CFG = __CFG__
TEL = {"prebuys": 0, "prebought": 0, "sells": 0, "sold": 0}
_MEM = {}


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


def _armed(me, target):
    """GATE 0: always. GATE 1: the first scheduled step blind, later ones only after the rival was seen buying 20+
    at a scheduled step and selling 20+ the step after (inferred from the TICK layer's rival wheat flow)."""
    if not CFG["GATE"]:
        return True
    first = CFG["SCHED"][0]
    if target == first:
        return CFG["GATE"] == 1
    try:
        fl = (_NS["_TICK_NS"]["_MEM"].get(me) or {}).get("flow") or {}
    except Exception:
        return False
    for s0 in CFG["SCHED"]:
        if s0 >= target:
            break
        if fl.get(s0, 0) <= -20 and fl.get(s0 + 1, 0) >= 20:
            return True
    return False


def agent(observation, configuration=None):
    try:
        step = int(_get(observation, "step", 0))
        me = int(_get(observation, "player", 0))
    except Exception:
        return _BASE(observation, configuration)
    mem = _MEM.setdefault(me, {"last": -1, "lot": 0, "base_w": 0})
    if step <= mem["last"]:
        mem.update({"lot": 0, "base_w": 0})
    mem["last"] = step
    sched = CFG["SCHED"]
    obs_in = observation
    hide = 0
    if step in sched and mem["lot"] > 0:
        shed_w = int((_get(_get(observation, "private"), "shed", {}) or {}).get("WHEAT", 0))
        hide = max(0, min(mem["lot"], shed_w - mem["base_w"]))
        if hide > 0:
            try:
                obs_in = _copy.deepcopy(observation)
                pv = _get(obs_in, "private")
                sh = dict(_get(pv, "shed", {}) or {})
                sh["WHEAT"] = max(0, int(sh.get("WHEAT", 0)) - hide)
                pv["shed"] = sh
            except Exception:
                obs_in = observation
    a = _BASE(obs_in, configuration)
    try:
        if not isinstance(a, dict):
            return a
        market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple))]
        changed = False
        if step in sched:
            if hide > 0 and _pad_last(market, ["SELL", "WHEAT", hide]):
                TEL["sells"] += 1
                TEL["sold"] += hide
                changed = True
            mem["lot"] = 0
        elif (step + CFG["LEAD"]) in sched and _armed(me, step + CFG["LEAD"]):
            live = [o for o in market if o]
            pshed, pinvs = _PROJECT(observation, dict(a, market=live))[:2]
            carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
            room = 100 - sum(int(v) for v in pshed.values()) - carried - 3
            farm = _get(observation, "farms")[me]
            money = float(_get(farm, "money", 0))
            quote = int(_get(_get(_get(observation, "market", {}) or {}, "prices", {}) or {}, "WHEAT", 40))
            x = int(max(0, min(CFG["XMAX"], room, (money - CFG["RESERVE"]) // max(1, quote + 8))))
            if x >= 10 and _pad_last(market, ["BUY_PRODUCT", "WHEAT", x]):
                mem["lot"] = x
                mem["base_w"] = int(pshed.get("WHEAT", 0))
                TEL["prebuys"] += 1
                TEL["prebought"] += x
                changed = True
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
    cfg = {"XMAX": int(kv.get("XMAX", 80)), "SCHED": [int(s) for s in kv.get("SCHED", "327,375,419,435,487").split(",")],
           "LEAD": int(kv.get("LEAD", 1)), "RESERVE": float(kv.get("RESERVE", 1500)), "GATE": int(kv.get("GATE", 0))}
    base = os.path.abspath(kv.get("BASE", os.path.join(ROOT, "submissions", "v12_1_own_cha22_tick_fade_resume_late", "main.py")))
    out = os.path.join(ROOT, "gold", "front", "var", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(
        CODE.replace("__BASE__", repr(base)).replace("__CFG__", repr(cfg)))
    print(out, cfg)


if __name__ == "__main__":
    main()
