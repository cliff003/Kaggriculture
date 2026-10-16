
# ---------------------------------------------------------------------------
# V10_CarreraGT override (nohits): the TICK layer no longer pauses just because the rival churns wheat too. Its
# wheat-flow tracking keeps running (GUARD stays on), so the tick-trap guard still sees the flow it needs and still
# pauses TICK on a sandwich or prebuy trap.
_TICK_NS["CFG"]["HITS"] = 10 ** 9
