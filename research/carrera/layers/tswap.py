
# ---------------------------------------------------------------------------
# V10_CarreraGT layer (team 42, 2026-09-27): day-11 strawberry-to-tomato swap.
# On day 11 the route buys and plants its last strawberry batch (13 seeds). When the shops open by then
# ask for tomatoes (pizza shop, farmers market), that batch is bought and planted as tomatoes instead: the
# route's own workers keep watering and harvesting the same cells. A tomato planted on day 11 grows one unit
# at every refresh from the end of day 18 (two when fertilized and watered), held up to four, against a
# strawberry every second refresh from day 20; tomato seed costs 50 instead of 100. Tomatoes in the shed are
# sold in lots of at most _CG_TS_LOT a turn. Seeing a tomato crop on day 18, cha22's V219 then skips its own
# ten-tomato investment and the south-east land.
_CG_TS_MIN_TOMATO_SHOPS = @MINT@
_CG_TS_MAX_BERRY_SHOPS = @MAXB@
_CG_TS_LOT = @LOT@
_CG_TS_STATE = {}
_CG_TS_REPORT = {"swapped_seeds": 0, "swapped_plants": 0, "sold": 0, "errors": 0}


def _cg_ts_decide(observation):
    shops = list(_g(_g(observation, "town", {}), "unlocked_shops", []) or [])
    tomato = sum(s in ("PIZZA_SHOP", "FARMERS_MARKET") for s in shops)
    berry = sum(s in ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET") for s in shops)
    return tomato >= _CG_TS_MIN_TOMATO_SHOPS and berry <= _CG_TS_MAX_BERRY_SHOPS


def _cg_tswap(observation, action):
    try:
        step = int(_g(observation, "step", 0))
        seat = int(_g(observation, "player", 0))
        st = _CG_TS_STATE.get(seat)
        if st is None or step <= st["step"]:
            st = _CG_TS_STATE[seat] = {"step": -1, "swap": None}
        st["step"] = step
        if not isinstance(action, dict):
            return action
        day = step // 24
        if day == 11 and st["swap"] is None:
            st["swap"] = _cg_ts_decide(observation)
        if not st["swap"]:
            return action
        out = dict(action)
        changed = False
        if day == 11:
            units = [list(action.get("farmer") or ["PASS"])] + [list(c) for c in (action.get("hands") or [])]
            for c in units:
                if c[:2] == ["PLANT", "STRAWBERRY"]:
                    c[1] = "TOMATO"
                    changed = True
                    _CG_TS_REPORT["swapped_plants"] += 1
            market = []
            for o in action.get("market") or []:
                if isinstance(o, list) and len(o) >= 3 and o[:2] == ["BUY_SEED", "STRAWBERRY"]:
                    market.append(["BUY_SEED", "TOMATO", o[2]])
                    _CG_TS_REPORT["swapped_seeds"] += int(o[2])
                    changed = True
                else:
                    market.append(o)
            out["farmer"], out["hands"], out["market"] = units[0], units[1:], market
        if day >= 18 and step < 719:
            market = [list(o) for o in (out.get("market") or []) if isinstance(o, list) and o]
            if not any(o[:2] == ["SELL", "TOMATO"] for o in market) and len(market) < 10:
                shed, _invs, _farm = _project(observation, out)
                n = int(shed.get("TOMATO", 0)) if step >= 710 else min(int(shed.get("TOMATO", 0)), _CG_TS_LOT)
                price = int(_g(_g(_g(observation, "market"), "prices", {}), "TOMATO", 0))
                if n > 0 and price > 1:
                    market.insert(0, ["SELL", "TOMATO", n])
                    out["market"] = market
                    _CG_TS_REPORT["sold"] += n
                    changed = True
        return out if changed else action
    except Exception:
        _CG_TS_REPORT["errors"] += 1
        return action


_PRE_CG_TS_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    return _cg_tswap(observation, _PRE_CG_TS_AGENT(observation, configuration))
