r"""Insert the STRAWSWAP layer into a team-42 agent, just inside the TICK layer when there is one (else outermost).

.venv\Scripts\python.exe tools\add_strawswap.py IN_MAIN_PY OUT_DIR [--k 10] [--from-day 11] [--to-day 13]
                                                [--min-shops 3] [--feed-h 12]

cha22's routes plant 33 strawberries in every world. Where at least MIN_SHOPS of the unlocked shops buy strawberries
(brunch spot, ice cream shop, smoothie shop, farmers market) the late strawberry book stays at 1.5-1.9x base in live
games, while wheat sells at ~1.6x of a 25 base. This layer turns up to K of the route's wheat plantings on days
FROM_DAY..TO_DAY into strawberries (seeds bought ahead in one lot). The route keeps visiting those tiles on its
wheat cycle: its waters keep the plant alive, its harvests collect the berries and its replants fail harmlessly on
the occupied tile, so the wheat and carrot seeds it keeps buying for them are not bought. While tiles are swapped,
wheat sales are capped so the shed keeps what the route's units pick up (feed) in the next FEED_H steps.
"""
import argparse
import os

LAYER = r'''
# ---------------------------------------------------------------------------
# Team 42 STRAWSWAP layer: see tools/add_strawswap.py.
_SS_K = @K@
_SS_FROM_DAY, _SS_TO_DAY = @FROM@, @TO@
_SS_MIN_SHOPS = @MINSHOPS@
_SS_FEED_H = @FEEDH@
_SS_CASH = 2500
_SS_SHOPS = ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET")
_SS_STATE = {}
_SS_REPORT = {"swaps": 0, "seed_lots": 0, "seeds_saved": 0, "feed_cuts": 0, "worlds_on": 0}


def _ss_ns():
    return globals().get("_BASE_NS") or globals()


def _ss_pickups(seat, step, item, horizon):
    chassis = _ss_ns()["_IMPL"].chassis
    native = chassis.players.get(seat)
    if not native or native.get("route") is None:
        return 0
    total = 0
    for t in range(step + 1, min(719, step + 1 + horizon)):
        tape = chassis.routes.get(2 if t >= 648 else native["route"]) or []
        a = tape[t] if t < len(tape) and isinstance(tape[t], dict) else {}
        for c in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or []):
            if c and c[0] == "PICKUP" and len(c) >= 2 and c[1] == item:
                total += max(0, int(c[2]) if len(c) >= 3 else 1)
    return total


def _strawswap(obs, action):
    step = int(obs["step"])
    day = step // 24
    seat = int(obs["player"])
    st = _SS_STATE.get(seat)
    if st is None or step <= st["step"]:
        st = _SS_STATE[seat] = {"step": -1, "on": False, "tiles": set(), "surplus": {"WHEAT": 0, "CARROT": 0}}
    st["step"] = step
    if not isinstance(action, dict) or day < _SS_FROM_DAY - 1 or step >= 717:
        return action
    farm = obs["farms"][seat]
    tiles = farm["tiles"]
    priv = obs["private"]
    changed = False
    units = [list(action.get("farmer") or ["PASS"])] + [list(c) for c in (action.get("hands") or [])]
    positions = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple)) and o]
    in_window = _SS_FROM_DAY <= day <= _SS_TO_DAY
    if not st["on"] and day <= _SS_TO_DAY:
        shops = list(obs["town"]["unlocked_shops"])
        if sum(1 for s in shops if s in _SS_SHOPS) >= _SS_MIN_SHOPS:
            st["on"] = True
            _SS_REPORT["worlds_on"] += 1
    if st["on"]:
        seeds = dict(priv.get("seeds") or {})
        have = int(seeds.get("STRAWBERRY", 0))
        left = _SS_K - len(st["tiles"])
        # 1. strawberry seeds one step ahead of the route's next wheat plantings (none of its own this late);
        #    seeds bought now are in stock for the plantings of the next step
        nxt = step + 1
        if _SS_FROM_DAY <= nxt // 24 <= _SS_TO_DAY and left - have > 0:
            chassis = _ss_ns()["_IMPL"].chassis
            native = chassis.players.get(seat)
            tape = chassis.routes.get(native["route"]) or [] if native and native.get("route") is not None else []
            a = tape[nxt] if nxt < len(tape) and isinstance(tape[nxt], dict) else {}
            n_next = sum(1 for c in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
                         if c and c[:2] == ["PLANT", "WHEAT"])
            need = min(n_next, left - have)
            if need > 0 and float(farm.get("money", 0)) >= need * 100 + _SS_CASH and len(market) < 10:
                market.append(["BUY_SEED", "STRAWBERRY", need])
                _SS_REPORT["seed_lots"] += 1
                changed = True
        # 2. the route's wheat plantings in the window become strawberries
        if in_window:
            for i, cmd in enumerate(units[:len(positions)]):
                if left <= 0 or have <= 0:
                    break
                if cmd[:2] == ["PLANT", "WHEAT"]:
                    x, y = positions[i]
                    if tiles[y][x] is None and (x, y) not in st["tiles"]:
                        units[i] = ["PLANT", "STRAWBERRY"]
                        st["tiles"].add((x, y))
                        st["surplus"]["WHEAT"] += 1
                        have -= 1
                        left -= 1
                        _SS_REPORT["swaps"] += 1
                        changed = True
        # 3. the route's later replants on swapped tiles fail on the occupied tile: do not buy their seeds
        for i, cmd in enumerate(units[:len(positions)]):
            if cmd and cmd[0] == "PLANT" and len(cmd) >= 2 and cmd[1] in st["surplus"] and positions[i] in st["tiles"]:
                t = tiles[positions[i][1]][positions[i][0]]
                if isinstance(t, dict) and t.get("crop") == "STRAWBERRY":
                    st["surplus"][cmd[1]] += 1
        for o in market:
            if o[0] == "BUY_SEED" and len(o) >= 3 and o[1] in st["surplus"] and st["surplus"][o[1]] > 0:
                cut = min(int(o[2]), st["surplus"][o[1]])
                if cut > 0:
                    o[2] = int(o[2]) - cut
                    st["surplus"][o[1]] -= cut
                    _SS_REPORT["seeds_saved"] += cut
                    changed = True
        market = [o for o in market if not (o[0] == "BUY_SEED" and len(o) >= 3 and int(o[2]) <= 0)]
        # 4. keep the feed the route picks up: cap this turn's wheat sales
        if st["tiles"] and any(o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT" for o in market):
            trial = dict(action)
            trial["farmer"], trial["hands"], trial["market"] = units[0], units[1:], market
            try:
                proj = _project(obs, trial)[0]
                short = _ss_pickups(seat, step, "WHEAT", _SS_FEED_H) - int(proj.get("WHEAT", 0))
            except Exception:
                short = 0
            if short > 0:
                for o in market:
                    if short > 0 and o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT" and int(o[2]) > 0:
                        cut = min(int(o[2]), short)
                        o[2] = int(o[2]) - cut
                        short -= cut
                        _SS_REPORT["feed_cuts"] += cut
                        changed = True
                market = [o for o in market if not (o[0] == "SELL" and len(o) >= 3 and int(o[2]) <= 0)]
    if not changed:
        return action
    out = dict(action)
    out["farmer"], out["hands"], out["market"] = units[0], units[1:], market[:10]
    return out


_PRE_SS_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_SS_AGENT(observation, configuration)
    try:
        return _strawswap(observation, action)
    except Exception:
        return action

'''
MARK = "# ---------------------------------------------------------------------------\n# Team 42 TICK layer"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--from-day", type=int, default=11)
    ap.add_argument("--to-day", type=int, default=13)
    ap.add_argument("--min-shops", type=int, default=3)
    ap.add_argument("--feed-h", type=int, default=12)
    a = ap.parse_args()
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    src = raw.decode("utf-8").replace("\r\n", "\n")
    layer = (LAYER.replace("@K@", str(a.k)).replace("@FROM@", str(a.from_day)).replace("@TO@", str(a.to_day))
             .replace("@MINSHOPS@", str(a.min_shops)).replace("@FEEDH@", str(a.feed_h)))
    if MARK in src:
        i = src.index(MARK)
        code = src[:i].rstrip("\n") + "\n\n" + layer.lstrip("\n") + "\n" + src[i:]
    else:
        code = src.rstrip("\n") + "\n" + layer
    compile(code, "main.py", "exec")
    if crlf:
        code = code.replace("\n", "\r\n")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "wb") as f:
        f.write(code.encode("utf-8"))
    print("wrote", os.path.join(a.out, "main.py"), "(inside TICK)" if MARK in src else "(outermost)")


if __name__ == "__main__":
    main()
