
# ---------------------------------------------------------------------------
# V10_CarreraGT layer (team 42, 2026-09-27): the TICK layer keeps arbitraging next to a plain wheat churner (a rival
# that buys at s % 4 == 0 and sells at s + 1 like we do), and pauses instead for a rival that trades against the round
# trip: it sells at least TH wheat in the step of our tick buy and buys at least TH back in the next step, twice within
# the WIN cycles. The flow tracking itself is unchanged, so the tick-trap guard keeps seeing the flow it needs.
_TICK_NS["CFG"]["HITS"] = 10 ** 9      # no pause for a plain churner
_CG_RG_TRACK = _TICK_NS["_track"]
_CG_RG_REPORT = {"reversal_stops": 0}


def _cg_rg_track(mem, observation, step, a):
    _CG_RG_TRACK(mem, observation, step, a)
    if mem.get("rival") or step % 4 != 2:
        return
    cfg = _TICK_NS["CFG"]
    fl = mem.get("flow") or {}
    hits = 0
    for s0 in range(step - 2, step - 2 - 4 * cfg["WIN"], -4):
        if fl.get(s0, 0) >= cfg["TH"] and fl.get(s0 + 1, 0) <= -cfg["TH"]:
            hits += 1
    if hits >= 2:
        mem["rival"] = True
        _CG_RG_REPORT["reversal_stops"] += 1


_TICK_NS["_track"] = _cg_rg_track


_PRE_CG_RG_AGENT = globals().pop("agent")   # the loader takes the last callable in module order: re-export agent last


def agent(observation, configuration=None):
    return _PRE_CG_RG_AGENT(observation, configuration)
