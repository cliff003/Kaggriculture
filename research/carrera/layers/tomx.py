
# ---------------------------------------------------------------------------
# V10_CarreraGT layer (team 42, 2026-09-27): TOMX, eight more tomatoes next to cha22's V219 investment.
# V219 buys the south-east land on day 18 and grows ten tomatoes on its rows 5-6 for the day 26-29 harvests,
# with its own crew hired right after the route's hands. When V219 commits and the tomato quote is at least
# _CG_TX_MIN_QUOTE, TOMX buys _CG_TX_COUNT more seeds for the free cells of rows 7-8 and, on every day V219
# hires a crew, hires one more hand right behind V219's (same turn, so the new hand's index is known), that
# runs V219's own worker routine on TOMX's cells: plant on day 18, water, fertilize on days 24 and 27 (TOMX
# buys that fertilizer), harvest from day 26 and carry the tomatoes to the shed, where V219 sells them.
_CG_TX_COUNT = @COUNT@
_CG_TX_MIN_QUOTE = @QUOTE@
_CG_TX_CELLS = ((5, 7), (6, 7), (7, 7), (8, 7), (5, 8), (6, 8), (7, 8), (8, 8))[:_CG_TX_COUNT]
_CG_TX_STATE = {}
_CG_TX_REPORT = {"commits": 0, "hires": 0, "confirmed": 0, "misses": 0, "fert_buys": 0, "turns": 0, "errors": 0}


def _cg_tx(observation, action):
    try:
        step = int(_g(observation, "step", 0))
        seat = int(_g(observation, "player", 0))
        st = _CG_TX_STATE.get(seat)
        if st is None or step <= st["step"]:
            st = _CG_TX_STATE[seat] = {"step": -1, "active": None, "worker": None, "pending": None, "day": -1,
                                        "wstate": {"last_work": {}, "seen_plants": set(), "lost": set()}}
        st["step"] = step
        if not isinstance(action, dict) or step >= 719:
            return action
        day, hour = divmod(step, 24)
        if day < 18:
            return action
        ns = _BASE_NS
        v219 = (ns.get("_V219_STATES") or {}).get(seat) or {}
        farm = observation["farms"][seat]
        if st["day"] != day:
            st["day"], st["worker"] = day, None
            st["wstate"]["last_work"] = {}
        # confirm last turn's hire: the new hand must be exactly the index we reserved
        if st["pending"] is not None:
            want = st["pending"]
            st["pending"] = None
            if len(farm["hands"]) == want:
                st["worker"] = want
                _CG_TX_REPORT["confirmed"] += 1
            else:
                _CG_TX_REPORT["misses"] += 1
        out = action
        if st["active"] is None and day == 18 and v219.get("committed"):
            quote = int(observation["market"]["prices"].get("TOMATO", 0))
            st["active"] = quote >= _CG_TX_MIN_QUOTE
        if st["active"] and v219.get("requested_day") == day and v219.get("pending") and st["pending"] is None \
                and st["worker"] is None and v219["pending"].get("step") == step:
            pend = v219["pending"]
            market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
            extra = [["HIRE"]]
            if day == 18:
                extra.insert(0, ["BUY_SEED", "TOMATO", len(_CG_TX_CELLS)])
            if day in (24, 27):
                extra.insert(0, ["BUY_PRODUCT", "FERTILIZER", len(_CG_TX_CELLS)])
            prices = observation["market"]["prices"]
            cost = ns["_v219_fib"](int(farm.get("hires_today", 0)) + sum(1 for o in market if o[0] == "HIRE"))
            cost += 50 * len(_CG_TX_CELLS) * (day == 18) + (int(prices.get("FERTILIZER", 60)) + 5) * len(_CG_TX_CELLS) * (day in (24, 27))
            spend = 0
            for o in market:
                if o[0] == "BUY_PRODUCT" and len(o) >= 3:
                    spend += int(o[2]) * (int(prices.get(o[1], 50)) + 10)
                elif o[0] == "BUY_SEED" and len(o) >= 3:
                    spend += int(o[2]) * {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}.get(o[1], 100)
                elif o[0] == "BUY_ANIMAL" and len(o) >= 3:
                    spend += int(o[2]) * {"COW": 400, "SHEEP": 500, "GOOSE": 300}.get(o[1], 500)
                elif o[0] == "BUY_LAND":
                    spend += 4000
                elif o[0] == "HIRE":
                    spend += 250
            if len(market) + len(extra) <= 10 and float(farm["money"]) >= spend + cost + 3000:
                out = dict(action)
                out["market"] = market + extra
                st["pending"] = pend["first_actor"] + pend["count"]
                st["role"] = {"kind": "crop", "targets": list(_CG_TX_CELLS), "needs_fertilizer": day in (24, 27),
                              "fertilizer_quantity": len(_CG_TX_CELLS)}
                _CG_TX_REPORT["hires"] += 1
                _CG_TX_REPORT["fert_buys"] += int(day in (24, 27))
                if day == 18:
                    _CG_TX_REPORT["commits"] += 1
        if st["worker"] is not None and st["worker"] <= len(farm["hands"]):
            commands = [out.get("farmer") or ["PASS"]] + list(out.get("hands") or [])
            commands += [["PASS"] for _ in range(len(farm["hands"]) + 1 - len(commands))]
            commands[st["worker"]] = ns["_v219_worker"](observation, st["wstate"], st["worker"], st["role"])
            st["wstate"]["last_work"][st["worker"]] = {"step": step, "command": commands[st["worker"]],
                                                       "tomatoes": observation["private"]["inventories"][st["worker"]].get("TOMATO", 0)}
            out = dict(out)
            out["farmer"], out["hands"] = commands[0], commands[1:]
            _CG_TX_REPORT["turns"] += 1
        return out
    except Exception:
        _CG_TX_REPORT["errors"] += 1
        return action


_PRE_CG_TX_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    return _cg_tx(observation, _PRE_CG_TX_AGENT(observation, configuration))
