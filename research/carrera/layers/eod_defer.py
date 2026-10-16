
# ---------------------------------------------------------------------------
# V10_CarreraGT layer (team 42, 2026-09-27): end-of-day pickup deferral.
# At the last step of a day the engine drops every carried inventory into the shed and destroys whatever
# does not fit under the 100-unit cap. When this turn's actions would leave more than 100 units in the shed
# plus the units' hands (engine rules, _project above), this turn's HARVEST and COLLECT_FERTILIZER actions
# are turned into PASS, last unit first, until the projection fits. The produce stays on the tile or the
# animal and is picked up on a later day instead of being destroyed tonight. Nothing else changes.
def _cg_units(action):
    return [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])


def _cg_total(observation, action):
    shed, invs, _farm = _project(observation, action)
    return sum(v for v in shed.values() if v > 0) + sum(v for inv in invs for v in inv.values() if v > 0)


def _cg_eod_defer(observation, action):
    try:
        step = int(_g(observation, "step", 0))
        if step % 24 != 23 or step >= 718 or not isinstance(action, dict):
            return action
        if _cg_total(observation, action) <= _CAP:
            return action
        units = _cg_units(action)
        out = dict(action)
        for idx in range(len(units) - 1, -1, -1):
            act = units[idx]
            if not (isinstance(act, list) and act and act[0] in ("HARVEST", "COLLECT_FERTILIZER")):
                continue
            units[idx] = ["PASS"]
            out["farmer"], out["hands"] = units[0], units[1:]
            if _cg_total(observation, out) <= _CAP:
                break
        return out
    except Exception:
        return action


_PRE_CG_EOD_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    return _cg_eod_defer(observation, _PRE_CG_EOD_AGENT(observation, configuration))
