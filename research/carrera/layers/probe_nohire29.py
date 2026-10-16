
# ---------------------------------------------------------------------------
# V10_CarreraGT probe (research only): no HIRE orders on the last day (steps 696 and later).
def _cg_nohire29(observation, action):
    try:
        if int(_g(observation, "step", 0)) < 696 or not isinstance(action, dict):
            return action
        out = dict(action)
        out["market"] = [o for o in (action.get("market") or []) if not (isinstance(o, list) and o and o[0] == "HIRE")]
        return out
    except Exception:
        return action


_PRE_CG_NH_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    return _cg_nohire29(observation, _PRE_CG_NH_AGENT(observation, configuration))
