r"""Carrot-world swap layer (team 42 experiment, 2026-09-27; what LK30 and Gatswei do on the cha22 route).

    .venv\Scripts\python.exe gold\front\mk_csw.py OUT_NAME [FROM_DAY=15] [TO_DAY=24] [SCORE=4] [FRAC=0.5]
        [FEED_H=12] [SELL=1] [BASE=gold/front/var/v12_3_tom/main.py]

In worlds whose unlocked shops eat many carrots (pet cafe = 2 points, 12 a day; farmers market = 1 point, 6 a day;
the layer switches on once the score reaches SCORE), up to FRAC of the route's wheat plantings on days FROM_DAY..TO_DAY
become carrots. Carrots grow like the route's wheat (planted and watered on day 0, watered on day 2, watered and
harvested on day 3), so the route's own care fits and the tile is replanted on its normal cycle. Carrot seeds are
bought one step ahead for the route's next-step wheat plantings; the route's later wheat seed purchases are cut by
the swapped count; a swap is skipped while the shed's wheat does not cover the route's feed pickups of the next FEED_H
steps, and wheat sales are capped to keep that feed. SELL=1 sells carrots on arrival (slot 0) while the mode is on.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LAYER = r'''
CFG = __CFG__
TEL = {"worlds_on": 0, "swaps": 0, "seed_buys": 0, "seeds_saved": 0, "feed_skips": 0, "feed_cuts": 0, "carrot_sells": 0}
_ST = {}


def _get(o, k, d=None):
    try:
        return o[k]
    except Exception:
        return getattr(o, k, d)


def _score(shops):
    return sum(2 if s == "PET_CAFE" else 1 if s == "FARMERS_MARKET" else 0 for s in shops)


def _chassis():
    ns = _NS.get("_BASE_NS") or _NS
    return ns["_IMPL"].chassis


def _tape_step(seat, t):
    ch = _chassis()
    native = ch.players.get(seat)
    if not native or native.get("route") is None:
        return {}
    tape = ch.routes.get(2 if t >= 648 else native["route"]) or []
    return tape[t] if 0 <= t < len(tape) and isinstance(tape[t], dict) else {}


def _pickups(seat, step, item, horizon):
    total = 0
    for t in range(step + 1, min(719, step + 1 + horizon)):
        a = _tape_step(seat, t)
        for c in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or []):
            if c and c[0] == "PICKUP" and len(c) >= 2 and c[1] == item:
                total += max(0, int(c[2]) if len(c) >= 3 else 1)
    return total


def agent(observation, configuration=None):
    a = _BASE(observation, configuration)
    try:
        if not isinstance(a, dict):
            return a
        step = int(_get(observation, "step", 0))
        day = step // 24
        seat = int(_get(observation, "player", 0))
        st = _ST.get(seat)
        if st is None or step <= st["step"]:
            st = _ST[seat] = {"step": -1, "on": False, "swapped": 0, "wheat_surplus": 0, "planned": 0}
        st["step"] = step
        if day > CFG["TO_DAY"] + 1 or step >= 717:
            return a
        shops = list(_get(_get(observation, "town", {}) or {}, "unlocked_shops", []) or [])
        if not st["on"] and day <= CFG["TO_DAY"] and _score(shops) >= CFG["SCORE"]:
            st["on"] = True
            TEL["worlds_on"] += 1
        if not st["on"]:
            return a
        farm = _get(observation, "farms")[seat]
        priv = _get(observation, "private")
        tiles = _get(farm, "tiles")
        units = [list(a.get("farmer") or ["PASS"])] + [list(c) for c in (a.get("hands") or [])]
        positions = [tuple(_get(farm, "farmer"))] + [tuple(h) for h in (_get(farm, "hands", []) or [])]
        market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple)) and o]
        changed = False
        seeds = dict(_get(priv, "seeds", {}) or {})
        own_now = sum(1 for c in units[:len(positions)] if c[:2] == ["PLANT", "CARROT"])
        have = int(seeds.get("CARROT", 0)) - own_now   # the route's own carrot plantings keep their seeds
        # 1. this step's route wheat plantings -> carrots (within the fraction, while the feed is covered)
        if CFG["FROM_DAY"] <= day <= CFG["TO_DAY"]:
            wheat_now = [i for i, c in enumerate(units[:len(positions)]) if c[:2] == ["PLANT", "WHEAT"]]
            shed_w = int((_get(priv, "shed", {}) or {}).get("WHEAT", 0))
            carried_w = sum(int(inv.get("WHEAT", 0)) for inv in (_get(priv, "inventories", []) or []))
            feed = _pickups(seat, step, "WHEAT", CFG["FEED_H"])
            quota = int(round(len(wheat_now) * CFG["FRAC"] + 0.49)) if wheat_now else 0
            if quota and shed_w + carried_w < feed:
                TEL["feed_skips"] += 1
                quota = 0
            for i in wheat_now:
                if quota <= 0 or have <= 0:
                    break
                x, y = positions[i]
                if tiles[y][x] is None:
                    units[i] = ["PLANT", "CARROT"]
                    have -= 1
                    quota -= 1
                    st["swapped"] += 1
                    st["wheat_surplus"] += 1
                    TEL["swaps"] += 1
                    changed = True
        # 2. carrot seeds one step ahead for the route's next-step wheat plantings
        nxt = step + 1
        if CFG["FROM_DAY"] <= nxt // 24 <= CFG["TO_DAY"]:
            na = _tape_step(seat, nxt)
            n_next = sum(1 for c in [na.get("farmer") or ["PASS"]] + list(na.get("hands") or []) if c and c[:2] == ["PLANT", "WHEAT"])
            own_next = sum(1 for c in [na.get("farmer") or ["PASS"]] + list(na.get("hands") or []) if c and c[:2] == ["PLANT", "CARROT"])
            want = int(round(n_next * CFG["FRAC"] + 0.49)) - (max(0, have) - own_next)
            if want > 0 and float(_get(farm, "money", 0)) >= want * 20 + 1500 and len(market) < 10:
                market.append(["BUY_SEED", "CARROT", want])
                TEL["seed_buys"] += want
                changed = True
        # 3. the route's wheat seed purchases: skip the ones the swapped plantings no longer need
        for o in market:
            if o[0] == "BUY_SEED" and len(o) >= 3 and o[1] == "WHEAT" and st["wheat_surplus"] > 0:
                cut = min(int(o[2]), st["wheat_surplus"])
                if cut > 0:
                    o[2] = int(o[2]) - cut
                    st["wheat_surplus"] -= cut
                    TEL["seeds_saved"] += cut
                    changed = True
        market = [o for o in market if not (o[0] == "BUY_SEED" and len(o) >= 3 and int(o[2]) <= 0)]
        # 4. keep the route's feed: cap this step's wheat sales to what the next FEED_H steps do not pick up
        if st["swapped"] and any(o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT" for o in market):
            trial = dict(a)
            trial["farmer"], trial["hands"], trial["market"] = units[0], units[1:], market
            try:
                proj = _PROJECT(observation, trial)[0]
                short = _pickups(seat, step, "WHEAT", CFG["FEED_H"]) - int(proj.get("WHEAT", 0))
            except Exception:
                short = 0
            if short > 0:
                for o in market:
                    if short > 0 and o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT" and int(o[2]) > 0:
                        cut = min(int(o[2]), short)
                        o[2] = int(o[2]) - cut
                        short -= cut
                        TEL["feed_cuts"] += cut
                        changed = True
                market = [o for o in market if not (o[0] == "SELL" and len(o) >= 3 and int(o[2]) <= 0)]
        # 5. sell carrots on arrival while the mode is on
        if CFG["SELL"] and day <= CFG["TO_DAY"] + 1:
            trial = dict(a)
            trial["farmer"], trial["hands"], trial["market"] = units[0], units[1:], market
            try:
                spare = int(_PROJECT(observation, trial)[0].get("CARROT", 0))
            except Exception:
                spare = 0
            if spare > 0:
                for o in market:
                    if o[0] == "SELL" and len(o) >= 3 and o[1] == "CARROT":
                        o[2] = int(o[2]) + spare
                        break
                else:
                    if len(market) < 10:
                        market.insert(0, ["SELL", "CARROT", spare])
                TEL["carrot_sells"] += 1
                changed = True
        if changed:
            a = dict(a)
            a["farmer"], a["hands"], a["market"] = units[0], units[1:], market[:10]
    except Exception:
        pass
    return a
'''

CODE = r'''
_BASE_PATH = __BASE__
_NS = {"__name__": "csw_base"}
exec(compile(open(_BASE_PATH, encoding="utf-8").read(), _BASE_PATH, "exec"), _NS)
_BASE = _NS["agent"]
_PROJECT = _NS["_project"]
''' + LAYER


def cfg_from(kv):
    return {"FROM_DAY": int(kv.get("FROM_DAY", 15)), "TO_DAY": int(kv.get("TO_DAY", 24)), "SCORE": int(kv.get("SCORE", 4)),
            "FRAC": float(kv.get("FRAC", 0.5)), "FEED_H": int(kv.get("FEED_H", 12)), "SELL": int(kv.get("SELL", 1))}


def main():
    name = sys.argv[1]
    kv = dict(x.split("=", 1) for x in sys.argv[2:])
    cfg = cfg_from(kv)
    base = os.path.abspath(kv.get("BASE", os.path.join(ROOT, "gold", "front", "var", "v12_3_tom", "main.py")))
    out = os.path.join(ROOT, "gold", "front", "var", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(
        CODE.replace("__BASE__", repr(base)).replace("__CFG__", repr(cfg)))
    print(out, cfg)


if __name__ == "__main__":
    main()
