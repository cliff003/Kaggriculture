
# ---------------------------------------------------------------------------
# V10_CarreraGT layer (team 42, 2026-09-27): day-11 strawberry-to-tomato swap.
# On day 11 the route buys and plants its last strawberry batch (13 seeds). When the shops open by then
# ask for tomatoes (pizza shop, farmers market), that batch is bought and planted as tomatoes instead: the
# route's own workers keep watering and harvesting the same cells. A tomato planted on day 11 grows one unit
# at every refresh from the end of day 18 (two when fertilized and watered), held up to four, against a
# strawberry every second refresh from day 20; tomato seed costs 50 instead of 100. Tomatoes in the shed are
# sold in lots of at most _CG_TS_LOT a turn. Seeing a tomato crop on day 18, cha22's V219 then skips its own
# ten-tomato investment and the south-east land.
_CG_TS_MIN_TOMATO_SHOPS = 1
_CG_TS_MAX_BERRY_SHOPS = 1
_CG_TS_LOT = 6
_CG_TS_RESCUE = 2
_CG_TS_KEEP_V219 = True
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
            farm = _g(observation, "farms")[seat]
            pos = [tuple(_g(farm, "farmer"))] + [tuple(h) for h in _g(farm, "hands", [])]
            for i, c in enumerate(units):
                if c[:2] == ["PLANT", "STRAWBERRY"]:
                    c[1] = "TOMATO"
                    changed = True
                    _CG_TS_REPORT["swapped_plants"] += 1
                    if i < len(pos):
                        st.setdefault("cells", set()).add(pos[i])
            market = []
            for o in action.get("market") or []:
                if isinstance(o, list) and len(o) >= 3 and o[:2] == ["BUY_SEED", "STRAWBERRY"]:
                    market.append(["BUY_SEED", "TOMATO", o[2]])
                    _CG_TS_REPORT["swapped_seeds"] += int(o[2])
                    changed = True
                else:
                    market.append(o)
            out["farmer"], out["hands"], out["market"] = units[0], units[1:], market
        if day >= 19 and st.get("cells") and step < 718:
            farm = _g(observation, "farms")[seat]
            pos = [tuple(_g(farm, "farmer"))] + [tuple(h) for h in _g(farm, "hands", [])]
            units = [list(out.get("farmer") or ["PASS"])] + [list(c) for c in (out.get("hands") or [])]
            hit = False
            for i, c in enumerate(units[:len(pos)]):
                if c != ["WATER"] or pos[i] not in st["cells"]:
                    continue
                x, y = pos[i]
                t = _g(farm, "tiles")[y][x]
                if (isinstance(t, dict) or hasattr(t, "keys")) and _g(t, "crop") == "TOMATO" \
                        and int(_g(t, "yield_units", 0)) >= _CG_TS_RESCUE and int(_g(t, "consecutive_unwatered", 1)) == 0:
                    units[i] = ["HARVEST"]
                    hit = True
                    _CG_TS_REPORT["rescues"] = _CG_TS_REPORT.get("rescues", 0) + 1
            if hit:
                out["farmer"], out["hands"] = units[0], units[1:]
                changed = True
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


_CG_TS_V219_QUALIFIES = _BASE_NS["_v219_qualifies"]


def _cg_ts_v219_qualifies(obs, native):
    st = _CG_TS_STATE.get(int(obs["player"])) or {}
    cells = st.get("cells") or set()
    if not cells:
        return _CG_TS_V219_QUALIFIES(obs, native)
    seat = int(obs["player"])
    farms = list(obs["farms"])
    farm = dict(farms[seat])
    tiles = [list(row) for row in farm["tiles"]]
    for x, y in cells:
        t = tiles[y][x]
        if isinstance(t, dict) and t.get("crop") == "TOMATO":
            tiles[y][x] = dict(t, crop="STRAWBERRY")
    farm["tiles"] = tiles
    farms[seat] = farm
    private = dict(obs["private"])
    private["seeds"] = dict(private["seeds"], TOMATO=0)
    private["shed"] = dict(private["shed"], TOMATO=0)
    view = dict(obs)
    view["farms"], view["private"] = farms, private
    return _CG_TS_V219_QUALIFIES(view, native)


if _CG_TS_KEEP_V219:
    _BASE_NS["_v219_qualifies"] = _cg_ts_v219_qualifies


_PRE_CG_TS_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    return _cg_tswap(observation, _PRE_CG_TS_AGENT(observation, configuration))
