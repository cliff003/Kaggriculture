r"""Insert the SHEEPX layer (six more sheep next to cha22's V233 flock) just inside the TICK layer.

.venv\Scripts\python.exe tools\add_sheepx.py IN_MAIN_PY OUT_DIR [--count 6] [--min-yarn 2] [--last-commit-day 13]
                                             [--hire-hour 3] [--cash 2500]

cha22's V233 buys the SE quadrant and six sheep in yarn worlds (two or more yarn stores, wool quote >= 220) and
runs them with its own hires; switching V233 off costs ~10k a game in those worlds. SHEEPX adds COUNT more sheep on
free SE cells once V233 has committed: it buys them in one lot, and every day, after the route's and V233's hires,
hires one more hand and buys that day's feed. The hand runs V233's own worker routine (build pasture, place sheep,
fetch wheat, feed, care, harvest, deliver the wool and fertilizer before midnight) on SHEEPX's cells only.
"""
import argparse
import os

LAYER = r'''
# ---------------------------------------------------------------------------
# Team 42 SHEEPX layer: see tools/add_sheepx.py.
_SX_COUNT = @COUNT@
_SX_MIN_YARN = @MINYARN@
_SX_LAST_COMMIT_DAY = @LASTDAY@
_SX_HIRE_HOUR = @HIREHOUR@
_SX_CASH = @CASH@
_SX_TILES = ((5, 7), (6, 7), (7, 7), (8, 7), (8, 6), (8, 5), (9, 5), (9, 6), (9, 7))
_SX_STATE = {}
_SX_REPORT = {"commits": 0, "hires": 0, "hire_misses": 0, "feed_units": 0, "worker_turns": 0}


def _sx_ns():
    return globals().get("_BASE_NS") or globals()


def _sheepx(obs, action):
    step = int(obs["step"])
    day, hour = divmod(step, 24)
    seat = int(obs["player"])
    st = _SX_STATE.get(seat)
    if st is None or step <= st["step"]:
        st = _SX_STATE[seat] = {"step": -1, "committed": False, "bought": False, "day": -1, "worker": None,
                                "pending": None}
    st["step"] = step
    if not isinstance(action, dict) or day < 11 or step >= 718:
        return action
    ns = _sx_ns()
    farm = obs["farms"][seat]
    private = obs["private"]
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
    live = [o for o in market if o]
    changed = False
    if st["day"] != day:
        st["day"], st["worker"], st["pending"] = day, None, None
    # confirm yesterday's (or this morning's) hire: the new hand is the index we recorded
    if st["pending"] is not None:
        want = st["pending"]
        st["pending"] = None
        if len(farm["hands"]) == want:   # every hire of that turn went through, so the last hand is ours
            st["worker"] = want
        else:
            _SX_REPORT["hire_misses"] += 1
    v233 = (ns.get("_V233_STATES") or {}).get(seat) or {}
    tiles = list(_SX_TILES[:_SX_COUNT])
    if not st["committed"]:
        if not v233.get("committed") or day > _SX_LAST_COMMIT_DAY or "SE" not in farm["unlocked_quadrants"]:
            return action
        if list(obs["town"]["unlocked_shops"]).count("YARN_STORE") < _SX_MIN_YARN:
            return action
        if any(farm["tiles"][y][x] not in (None,) and not (isinstance(farm["tiles"][y][x], dict)
               and farm["tiles"][y][x].get("kind") == "WEED") for x, y in tiles):
            return action
        if float(farm.get("money", 0)) < 500 * _SX_COUNT + _SX_CASH or len(live) >= 10:
            return action
        market.append(["BUY_ANIMAL", "SHEEP", _SX_COUNT])
        st["committed"] = True
        _SX_REPORT["commits"] += 1
        changed = True
        live = [o for o in market if o]
    # one hand a day, after every hire the route and V233 plan for today
    if st["worker"] is None and st["pending"] is None and hour >= _SX_HIRE_HOUR and hour <= 12:
        planned = ns["_v219_native_day"](ns["_IMPL"].chassis.players[seat], day)
        later_native = any(o and o[0] == "HIRE" for a in planned[hour + 1:] for o in a.get("market", []))
        v233_done = v233.get("requested_day") == day or hour >= 7
        if not later_native and not v233.get("pending") and v233_done and len(live) + 2 <= 10:
            quote = int(obs["market"]["prices"].get("WHEAT", 40))
            if float(farm.get("money", 0)) > 1500 + _SX_COUNT * (quote + 10) + 400:
                hires_before = sum(1 for o in live if o[0] == "HIRE")
                market.append(["BUY_PRODUCT", "WHEAT", _SX_COUNT])
                market.append(["HIRE"])
                st["pending"] = len(farm["hands"]) + hires_before + 1
                _SX_REPORT["hires"] += 1
                _SX_REPORT["feed_units"] += _SX_COUNT
                changed = True
    commands = [list(action.get("farmer") or ["PASS"])] + [list(c) for c in (action.get("hands") or [])]
    if st["worker"] is not None and st["worker"] < len(commands) and st["worker"] <= len(farm["hands"]):
        commands[st["worker"]] = ns["_SL_WORKER"](obs, st["worker"], tiles)
        _SX_REPORT["worker_turns"] += 1
        changed = True
    if not changed:
        return action
    out = dict(action)
    out["farmer"], out["hands"], out["market"] = commands[0], commands[1:], market[:10]
    return out


_PRE_SX_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_SX_AGENT(observation, configuration)
    try:
        return _sheepx(observation, action)
    except Exception:
        return action

'''
MARK = "# ---------------------------------------------------------------------------\n# Team 42 TICK layer"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--count", type=int, default=6)
    ap.add_argument("--min-yarn", type=int, default=2)
    ap.add_argument("--last-commit-day", type=int, default=13)
    ap.add_argument("--hire-hour", type=int, default=3)
    ap.add_argument("--cash", type=int, default=2500)
    a = ap.parse_args()
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    src = raw.decode("utf-8").replace("\r\n", "\n")
    layer = (LAYER.replace("@COUNT@", str(a.count)).replace("@MINYARN@", str(a.min_yarn))
             .replace("@LASTDAY@", str(a.last_commit_day)).replace("@HIREHOUR@", str(a.hire_hour))
             .replace("@CASH@", str(a.cash)))
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
