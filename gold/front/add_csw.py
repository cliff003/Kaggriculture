r"""Insert the CARROT-WORLD SWAP layer into a team-42 package just inside its TICK layer (so TICK, FADE, the
scheduled fade and the trap guard still place their orders around it, padding intact).

    .venv\Scripts\python.exe gold\front\add_csw.py IN_MAIN_PY OUT_DIR [--from-day 15] [--to-day 24] [--score 4]
        [--frac 0.5] [--feed-h 12] [--sell 1]

In worlds whose unlocked shops eat many carrots (pet cafe = 2 points, 12 a day; farmers market = 1 point, 6 a day;
on once the score reaches SCORE), up to FRAC of the route's wheat plantings on days FROM..TO become carrots. Carrots
grow like the route's wheat (planted and watered on day 0, watered on day 2, watered and harvested on day 3, as LK30
and Gatswei run them), so the route's own care fits and the tile is replanted on its normal cycle. Carrot seeds are
bought one step ahead for the route's next-step wheat plantings (the route's own carrot plantings keep their seeds:
the engine drops every planting of a crop when a turn asks for more than the seeds in stock); the route's later
wheat seed purchases are cut by the swapped count; a swap is skipped while the shed's wheat does not cover the route's
feed pickups of the next FEED_H steps, and the route's wheat sales are capped to keep that feed. SELL=1 sells the
shed's carrots every turn while the mode is on (existing carrot sell grows, else a new sell in the first free slot).
"""
import argparse
import os

LAYER = r'''
# ---------------------------------------------------------------------------
# Team 42 CARROT-WORLD SWAP layer: see gold/front/add_csw.py.
_CSW_CFG = @CFG@
_CSW_STATE = {}
_CSW_REPORT = {"worlds_on": 0, "swaps": 0, "seed_buys": 0, "seeds_saved": 0, "feed_skips": 0, "feed_cuts": 0,
               "carrot_sells": 0}


def _csw_ns():
    return globals().get("_BASE_NS") or globals()


def _csw_tape_step(seat, t):
    chassis = _csw_ns()["_IMPL"].chassis
    native = chassis.players.get(seat)
    if not native or native.get("route") is None:
        return {}
    tape = chassis.routes.get(2 if t >= 648 else native["route"]) or []
    return tape[t] if 0 <= t < len(tape) and isinstance(tape[t], dict) else {}


def _csw_pickups(seat, step, item, horizon):
    total = 0
    for t in range(step + 1, min(719, step + 1 + horizon)):
        a = _csw_tape_step(seat, t)
        for c in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or []):
            if c and c[0] == "PICKUP" and len(c) >= 2 and c[1] == item:
                total += max(0, int(c[2]) if len(c) >= 3 else 1)
    return total


def _csw_score(shops):
    return sum(2 if s == "PET_CAFE" else 1 if s == "FARMERS_MARKET" else 0 for s in shops)


def _csw(obs, action):
    cfg = _CSW_CFG
    step = int(obs["step"])
    day = step // 24
    seat = int(obs["player"])
    st = _CSW_STATE.get(seat)
    if st is None or step <= st["step"]:
        st = _CSW_STATE[seat] = {"step": -1, "on": False, "swapped": 0, "wheat_surplus": 0}
    st["step"] = step
    if not isinstance(action, dict) or day > cfg["to"] + 1 or step >= 717:
        return action
    if not st["on"] and day <= cfg["to"] and _csw_score(list(obs["town"]["unlocked_shops"])) >= cfg["score"]:
        st["on"] = True
        _CSW_REPORT["worlds_on"] += 1
    if not st["on"]:
        return action
    farm = obs["farms"][seat]
    priv = obs["private"]
    tiles = farm["tiles"]
    units = [list(action.get("farmer") or ["PASS"])] + [list(c) for c in (action.get("hands") or [])]
    positions = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
    changed = False
    own_now = sum(1 for c in units[:len(positions)] if c[:2] == ["PLANT", "CARROT"])
    have = int((priv.get("seeds") or {}).get("CARROT", 0)) - own_now
    if cfg["from"] <= day <= cfg["to"]:
        wheat_now = [i for i, c in enumerate(units[:len(positions)]) if c[:2] == ["PLANT", "WHEAT"]]
        if wheat_now and have > 0:
            shed_w = int((priv.get("shed") or {}).get("WHEAT", 0))
            carried_w = sum(int(inv.get("WHEAT", 0)) for inv in (priv.get("inventories") or []))
            quota = int(round(len(wheat_now) * cfg["frac"] + 0.49))
            if shed_w + carried_w < _csw_pickups(seat, step, "WHEAT", cfg["feed_h"]):
                _CSW_REPORT["feed_skips"] += 1
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
                    _CSW_REPORT["swaps"] += 1
                    changed = True
    live = [o for o in market if o]
    nxt = step + 1
    if cfg["from"] <= nxt // 24 <= cfg["to"]:
        na = _csw_tape_step(seat, nxt)
        cmds = [na.get("farmer") or ["PASS"]] + list(na.get("hands") or [])
        n_next = sum(1 for c in cmds if c and c[:2] == ["PLANT", "WHEAT"])
        own_next = sum(1 for c in cmds if c and c[:2] == ["PLANT", "CARROT"])
        want = int(round(n_next * cfg["frac"] + 0.49)) - (max(0, have) - own_next)
        if want > 0 and float(farm.get("money", 0)) >= want * 20 + 1500 and len(live) < 10:
            market.append(["BUY_SEED", "CARROT", want])
            live.append(market[-1])
            _CSW_REPORT["seed_buys"] += want
            changed = True
    for o in market:
        if o and o[0] == "BUY_SEED" and len(o) >= 3 and o[1] == "WHEAT" and st["wheat_surplus"] > 0:
            cut = min(int(o[2]), st["wheat_surplus"])
            if cut > 0:
                o[2] = int(o[2]) - cut
                st["wheat_surplus"] -= cut
                _CSW_REPORT["seeds_saved"] += cut
                changed = True
    market = [o for o in market if not (o and o[0] == "BUY_SEED" and len(o) >= 3 and int(o[2]) <= 0)]
    if st["swapped"] and any(o and o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT" for o in market):
        trial = dict(action)
        trial["farmer"], trial["hands"], trial["market"] = units[0], units[1:], [o for o in market if o]
        try:
            short = _csw_pickups(seat, step, "WHEAT", cfg["feed_h"]) - int(_project(obs, trial)[0].get("WHEAT", 0))
        except Exception:
            short = 0
        if short > 0:
            for o in market:
                if short > 0 and o and o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT" and int(o[2]) > 0:
                    cut = min(int(o[2]), short)
                    o[2] = int(o[2]) - cut
                    short -= cut
                    _CSW_REPORT["feed_cuts"] += cut
                    changed = True
            market = [o for o in market if not (o and o[0] == "SELL" and len(o) >= 3 and int(o[2]) <= 0)]
    if cfg["sell"]:
        trial = dict(action)
        trial["farmer"], trial["hands"], trial["market"] = units[0], units[1:], [o for o in market if o]
        try:
            spare = int(_project(obs, trial)[0].get("CARROT", 0))
        except Exception:
            spare = 0
        if spare > 0:
            for o in market:
                if o and o[0] == "SELL" and len(o) >= 3 and o[1] == "CARROT":
                    o[2] = int(o[2]) + spare
                    break
            else:
                slot = next((i for i, o in enumerate(market) if not o), None)
                if slot is not None:
                    market[slot] = ["SELL", "CARROT", spare]
                elif len(market) < 10:
                    market.append(["SELL", "CARROT", spare])
            _CSW_REPORT["carrot_sells"] += 1
            changed = True
    if not changed:
        return action
    out = dict(action)
    out["farmer"], out["hands"], out["market"] = units[0], units[1:], market[:10]
    return out


_PRE_CSW_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_CSW_AGENT(observation, configuration)
    try:
        return _csw(observation, action)
    except Exception:
        return action

'''
MARK = "# ---------------------------------------------------------------------------\n# Team 42 TICK layer"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--from-day", type=int, default=15)
    ap.add_argument("--to-day", type=int, default=24)
    ap.add_argument("--score", type=int, default=4)
    ap.add_argument("--frac", type=float, default=0.5)
    ap.add_argument("--feed-h", type=int, default=12)
    ap.add_argument("--sell", type=int, default=1)
    a = ap.parse_args()
    cfg = {"from": a.from_day, "to": a.to_day, "score": a.score, "frac": a.frac, "feed_h": a.feed_h, "sell": a.sell}
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    src = raw.decode("utf-8").replace("\r\n", "\n")
    layer = LAYER.replace("@CFG@", repr(cfg))
    assert MARK in src, "TICK layer marker not found"
    i = src.index(MARK)
    code = src[:i].rstrip("\n") + "\n\n" + layer.lstrip("\n") + "\n" + src[i:]
    compile(code, "main.py", "exec")
    if crlf:
        code = code.replace("\n", "\r\n")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "wb") as f:
        f.write(code.encode("utf-8"))
    print("wrote", os.path.join(a.out, "main.py"), cfg)


if __name__ == "__main__":
    main()
