
# ---------------------------------------------------------------------------
# v11 line layer (team 42, 2026-09-28): marginal-price cap on glut-prone sales.
# Milk, wool and strawberries fall steeply once the town market holds more than it eats (linear 1.6 / square 3.2 /
# linear 1.6 x base below the neutral stock), and the route sells whole harvest lots in one step, often in the same
# step as a mirror rival, so the last units of a lot go for a few coins. Each SELL of those goods is cut to the units
# whose quote (engine price function, our own units only) stays at or above _CG_MC_FLOOR x base price; the rest waits
# in the shed for a later step, where the unchanged sale layers offer it again. Only from step _CG_MC_START; from _CG_MC_END on, and at the
# last hour of a day (where the day-end room guard sells to avoid shed overflow), nothing is capped.
_CG_MC_FLOOR = 0.45
_CG_MC_END = 712
_CG_MC_START = 648
_CG_MC_ITEMS = ("MILK", "WOOL", "STRAWBERRY")
_CG_MC_REPORT = {"capped_orders": 0, "held_units": 0, "errors": 0}


def _cg_mcap(observation, action):
    try:
        step = int(_g(observation, "step", 0))
        if step < _CG_MC_START or step >= _CG_MC_END or step % 24 == 23 or not isinstance(action, dict):
            return action
        inv = dict(_g(_g(observation, "market"), "inventory", {}) or {})
        market = [list(o) if isinstance(o, list) else o for o in (action.get("market") or [])]
        used = {}
        changed = False
        for o in market:
            if not (isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and o[1] in _CG_MC_ITEMS):
                continue
            item, want = o[1], int(o[2])
            floor = _CG_MC_FLOOR * _MKT[item][0]
            start = int(inv.get(item, 10000)) + used.get(item, 0)
            n = 0
            while n < want and _mprice(item, start + n) >= floor:
                n += 1
            used[item] = used.get(item, 0) + n
            if n < want:
                _CG_MC_REPORT["capped_orders"] += 1
                _CG_MC_REPORT["held_units"] += want - n
                o[2] = n
                changed = True
        if not changed:
            return action
        out = dict(action)
        # a zeroed sell becomes an empty placeholder: later orders (the TICK buy in slot 9) keep their slots
        out["market"] = [[] if (isinstance(o, list) and len(o) >= 3 and o[0] == "SELL" and int(o[2]) <= 0) else o for o in market]
        return out
    except Exception:
        _CG_MC_REPORT["errors"] += 1
        return action


_PRE_CG_MC_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    return _cg_mcap(observation, _PRE_CG_MC_AGENT(observation, configuration))
