r"""Insert the CARROT swap layer into a team-42 v8 build, just inside the TICK layer.

.venv\Scripts\python.exe tools\add_carrot.py IN_MAIN_PY OUT_DIR [--ratio 1.8] [--first-day 10] [--last-day 23]
                                              [--reserve 40] [--boom 3.5] [--boom-reserve 10]

Adapted from the "v9 CARROT" layer of the public rescue-lineage agents (Apache-2.0; Dmitrii Gluzdov and co-authors,
as retained in data/public/agents/statma_ca25_0925). While the carrot quote is at least RATIO times the wheat quote
(pet cafes and farmers markets drain the carrot book) and the shed holds enough wheat for feed, the route's wheat
plantings on days FIRST..LAST become carrots (its wheat seed buys become carrot seed buys). The route waters and
harvests those tiles on its short wheat cycle; a carrot starts to decay at age 4, so the route's age-3 watering
visit harvests it instead. Swapped carrots are sold as they reach the shed (the route sells no carrots before its
own late carrot days). From BOOM times the wheat quote, the feed the swap no longer grows is bought.
"""
import argparse
import os

LAYER = r'''
# ---------------------------------------------------------------------------
# Team 42 CARROT layer: see tools/add_carrot.py (adapted from the public v9 CARROT layer, Apache-2.0).
_CR_RATIO = @RATIO@
_CR_FIRST_DAY, _CR_LAST_DAY = @FIRST@, @LAST@
_CR_RESERVE = @RESERVE@
_CR_BOOM, _CR_BOOM_RESERVE = @BOOM@, @BOOMRES@
_CR_STATE = {}
_CR_REPORT = {"swaps": 0, "seed_swaps": 0, "rescues": 0, "feed_buys": 0, "sells": 0}


def _carrot(obs, action):
    step = int(obs["step"])
    day = step // 24
    seat = int(obs["player"])
    st = _CR_STATE.get(seat)
    if st is None or step <= st["step"]:
        st = _CR_STATE[seat] = {"step": -1, "tiles": {}, "swapped": False}
    st["step"] = step
    if not isinstance(action, dict):
        return action
    prices = obs["market"]["prices"]
    private = obs["private"]
    farm = obs["farms"][seat]
    pos = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
    commands = [list(action.get("farmer") or ["PASS"])] + [list(c) for c in (action.get("hands") or [])]
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
    changed = False
    if st["tiles"]:
        # swapped carrots start to decay at age 4 while the wheat cycle may harvest then: harvest at age 3
        for i, c in enumerate(commands[:len(pos)]):
            if c != ["WATER"] or st["tiles"].get(pos[i]) != day - 3:
                continue
            t = farm["tiles"][pos[i][1]][pos[i][0]]
            if isinstance(t, dict) and t.get("crop") == "CARROT" and int(t.get("planted_day", -9)) == day - 3 \
                    and int(t.get("yield_units", 0)) > 0:
                commands[i] = ["HARVEST"]
                changed = True
                _CR_REPORT["rescues"] += 1
    wheat_held = int((private.get("shed") or {}).get("WHEAT", 0)) + sum(
        int(inv.get("WHEAT", 0)) for inv in (private.get("inventories") or []))
    ratio = int(prices.get("CARROT", 0)) / max(1, int(prices.get("WHEAT", 99)))
    boom = ratio >= _CR_BOOM
    reserve = _CR_BOOM_RESERVE if boom else _CR_RESERVE
    in_window = _CR_FIRST_DAY <= day <= _CR_LAST_DAY
    live = [o for o in market if o]
    if boom and in_window and wheat_held < _CR_RESERVE:
        topup = _CR_RESERVE - wheat_held
        budget = float(farm.get("money", 0)) - 1500
        qty = min(topup, int(budget // max(1, int(prices.get("WHEAT", 99)) + 5)))
        if qty > 0 and len(live) < 10 and not any(o[:2] == ["BUY_PRODUCT", "WHEAT"] for o in live):
            market.append(["BUY_PRODUCT", "WHEAT", qty])
            changed = True
            _CR_REPORT["feed_buys"] += qty
    if in_window and wheat_held >= reserve and ratio >= _CR_RATIO:
        seeds = int((private.get("seeds") or {}).get("CARROT", 0)) - sum(1 for c in commands if c[:2] == ["PLANT", "CARROT"])
        for i, c in enumerate(commands):
            if c[:2] == ["PLANT", "WHEAT"] and seeds > 0:
                c[1] = "CARROT"
                seeds -= 1
                changed = st["swapped"] = True
                _CR_REPORT["swaps"] += 1
                if i < len(pos):
                    st["tiles"][pos[i]] = day
        for o in market:
            if len(o) >= 3 and o[:2] == ["BUY_SEED", "WHEAT"]:
                o[1] = "CARROT"
                changed = st["swapped"] = True
                _CR_REPORT["seed_swaps"] += int(o[2])
    if st["swapped"] and day < 24:
        trial = dict(action)
        trial["farmer"], trial["hands"], trial["market"] = commands[0], commands[1:], [o for o in market if o]
        try:
            stock = int(_project(obs, trial)[0].get("CARROT", 0))
        except Exception:
            stock = 0
        selling = sum(int(o[2]) for o in market if len(o) >= 3 and o[:2] == ["SELL", "CARROT"])
        if stock > selling and len([o for o in market if o]) < 10 and int(prices.get("CARROT", 0)) >= 2:
            market.insert(0, ["SELL", "CARROT", stock - selling])
            changed = True
            _CR_REPORT["sells"] += 1
    if not changed:
        return action
    out = dict(action)
    out["farmer"], out["hands"], out["market"] = commands[0], commands[1:], market[:10]
    return out


_PRE_CR_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_CR_AGENT(observation, configuration)
    try:
        return _carrot(observation, action)
    except Exception:
        return action

'''
MARK = "# ---------------------------------------------------------------------------\n# Team 42 TICK layer"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--ratio", type=float, default=1.8)
    ap.add_argument("--first-day", type=int, default=10)
    ap.add_argument("--last-day", type=int, default=23)
    ap.add_argument("--reserve", type=int, default=40)
    ap.add_argument("--boom", type=float, default=3.5)
    ap.add_argument("--boom-reserve", type=int, default=10)
    a = ap.parse_args()
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    src = raw.decode("utf-8").replace("\r\n", "\n")
    layer = (LAYER.replace("@RATIO@", repr(a.ratio)).replace("@FIRST@", str(a.first_day))
             .replace("@LAST@", str(a.last_day)).replace("@RESERVE@", str(a.reserve))
             .replace("@BOOM@", repr(a.boom)).replace("@BOOMRES@", str(a.boom_reserve)))
    assert MARK in src
    i = src.index(MARK)
    code = src[:i].rstrip("\n") + "\n\n" + layer.lstrip("\n") + "\n" + src[i:]
    compile(code, "main.py", "exec")
    if crlf:
        code = code.replace("\n", "\r\n")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "wb") as f:
        f.write(code.encode("utf-8"))
    print("wrote", os.path.join(a.out, "main.py"))


if __name__ == "__main__":
    main()
