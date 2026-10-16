r"""Append the FERTMORE layer (more fertilizer spent on crops, fewer units sold cheaply) as the outermost layer.

.venv\Scripts\python.exe tools\add_fertmore.py IN_MAIN_PY OUT_DIR

cha22 sells most of the fertilizer its animals give (the late book falls to $10-20) and its own v9 FERT layer
only spends carried fertilizer on 1-day-old wheat and carrots from day 14. From step 288 to 690 this layer
turns a unit's turn into FERTILIZE when the unit carries fertilizer that its route does not use later today
and the expected extra crop is worth more than the fertilizer quote:
  * a PASS, or a WATER on a plant already watered today, on any fertilizer target;
  * the WATER on a 1-day-old wheat or carrot (watered on its planting day; the route waters it again in its
    yield window), as v9 FERT does, from day 12;
  * the WATER on a strawberry the day before a production, only when the route's own units water that tile
    tomorrow (simulated from the tape: spawn tiles, moves and hires), so the skipped water cannot kill it.
Expected gains: one-shot crops count the covered yield-window waters up to the room left under the maximum
yield (x0.75 for early harvests); strawberries and tomatoes count covered productions that get watered.
"""
import argparse
import os

LAYER = r'''

# ---------------------------------------------------------------------------
# Team 42 FERTMORE layer (outermost): see tools/add_fertmore.py.
_FM_FROM, _FM_TO = 288, 690
_FM_EXTRA = @EXTRA@   # extra units taken at the route's own fertilizer pickups
_FM_EXTRA_FROM = 20   # from this day (the fertilizer book is worth $10-20 by then)
# crop: (first_yield_day, max_yield_day, max_yield, ongoing, interval)
_FM_CROPS = {"WHEAT": (2, 4, 6, False, 0), "CARROT": (2, 3, 4, False, 0),
             "TOMATO": (8, 8, 4, True, 1), "STRAWBERRY": (10, 10, 4, True, 2)}
_FM_ACCESS = ((4, 4), (5, 4), (4, 5), (5, 5))
_FM_STEPS = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
_FM_CACHE = {}


def _fm_ns():
    return globals().get("_BASE_NS") or globals()


def _fm_spawn(positions):
    occ = {a: 0 for a in _FM_ACCESS}
    for p in positions:
        if tuple(p) in occ:
            occ[tuple(p)] += 1
    return min(_FM_ACCESS, key=lambda a: (occ[a], _FM_ACCESS.index(a)))


def _fm_tape_waters(seat, day):
    """Tiles the route's own units water on `day` (farmer from (4, 4), hands spawned by the tape's hires)."""
    key = (seat, day)
    if key in _FM_CACHE:
        return _FM_CACHE[key]
    chassis = _fm_ns()["_IMPL"].chassis
    native = chassis.players.get(seat)
    out = set()
    if native and native.get("route") is not None and day <= 29:
        pos = [(4, 4)]
        for t in range(day * 24, min(719, day * 24 + 24)):
            tape = chassis.routes.get(2 if t >= 648 else native["route"]) or []
            a = tape[t] if t < len(tape) and isinstance(tape[t], dict) else {}
            cmds = [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
            for i in range(len(pos)):
                c = cmds[i] if i < len(cmds) and cmds[i] else ["PASS"]
                if c[0] in _FM_STEPS:
                    dx, dy = _FM_STEPS[c[0]]
                    nx, ny = pos[i][0] + dx, pos[i][1] + dy
                    if 0 <= nx < 10 and 0 <= ny < 10:
                        pos[i] = (nx, ny)
                elif c[0] == "WATER":
                    out.add(pos[i])
            for o in a.get("market") or []:
                if o and o[0] == "HIRE":
                    pos.append(_fm_spawn(pos))
    if len(_FM_CACHE) > 16:
        _FM_CACHE.clear()
    _FM_CACHE[key] = out
    return out


def _fm_gain_units(t, day, replacing_water, tomorrow_watered):
    spec = _FM_CROPS.get(t.get("crop"))
    if not spec:
        return 0.0
    first, maxday, maxy, ongoing, interval = spec
    planted = int(t["planted_day"])
    fu = int(t.get("fertilized_until_day", -1))
    watered = bool(t.get("watered_today"))
    if not ongoing:
        ws = (maxday + 1) // 2
        covered = 0
        for d in (day, day + 1, day + 2):
            a = d - planted
            if a < ws or a > maxday or d <= fu:
                continue
            if d == day and (replacing_water or watered):
                continue
            covered += 1
        remaining = sum(1 for d in range(day, planted + maxday + 1)
                        if d - planted >= ws and not (d == day and watered))
        room = max(0, maxy - int(t.get("yield_units", 0)) - remaining)
        return 0.75 * min(covered, room)
    units = 0
    for e in (day, day + 1, day + 2):
        if e > 28 or e <= fu:
            continue
        dsf = e + 1 - planted - first
        if dsf < 0 or dsf % interval or dsf // interval + 1 > maxy:
            continue
        if e == day and not watered:
            continue
        if e == day + 1 and not tomorrow_watered:
            continue
        units += 1
    return 0.9 * units


def _fertmore(obs, action):
    step = int(obs["step"])
    day = step // 24
    if step < _FM_FROM or step > _FM_TO or not isinstance(action, dict):
        return action
    seat = int(obs["player"])
    chassis = _fm_ns()["_IMPL"].chassis
    native = chassis.players.get(seat)
    if not native or native.get("route") is None:
        return action
    farm = obs["farms"][seat]
    priv = obs["private"]
    tiles = farm["tiles"]
    positions = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
    invs = priv.get("inventories") or []
    units = [list(action.get("farmer") or ["PASS"])] + [list(c) for c in (action.get("hands") or [])]
    prices = obs["market"]["prices"]
    fquote = float(prices.get("FERTILIZER", 0))
    tape = chassis.routes.get(2 if step >= 648 else native["route"]) or []
    planned = {}
    for tt in range(step + 1, min(len(tape), day * 24 + 24)):
        a = tape[tt] if isinstance(tape[tt], dict) else {}
        for u, c in enumerate([a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])):
            if c and c[0] == "FERTILIZE":
                planned[u] = planned.get(u, 0) + 1
    tomorrow = None
    targeted = set()
    changed = False
    if _FM_EXTRA > 0 and day >= _FM_EXTRA_FROM:
        # the route's own fertilizer pickups take a few more units to spend along the way, but only out of
        # stock that no later pickup of the route needs today
        later = 0
        for tt in range(step + 1, min(len(tape), day * 24 + 24)):
            a = tape[tt] if isinstance(tape[tt], dict) else {}
            for c in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or []):
                if c and c[0] == "PICKUP" and len(c) >= 3 and c[1] == "FERTILIZER":
                    later += max(0, int(c[2]))
        shed_f = int((priv.get("shed") or {}).get("FERTILIZER", 0)) - later
        for u, cmd in enumerate(units[:len(positions)]):
            if cmd and cmd[0] == "PICKUP" and len(cmd) >= 2 and positions[u] in _FM_ACCESS:
                want = max(0, int(cmd[2]) if len(cmd) >= 3 else 1)
                if cmd[1] == "FERTILIZER":
                    extra = min(_FM_EXTRA, max(0, shed_f - want))
                    if extra > 0:
                        units[u] = ["PICKUP", "FERTILIZER", want + extra]
                        changed = True
                    shed_f -= min(shed_f, want + max(0, extra))
    for u, cmd in enumerate(units[:len(positions)]):
        inv = invs[u] if u < len(invs) else {}
        spare = int(inv.get("FERTILIZER", 0)) - planned.get(u, 0)
        if spare <= 0:
            continue
        pos = positions[u]
        t = tiles[pos[1]][pos[0]]
        if not (isinstance(t, dict) and t.get("kind") == "PLANT") or pos in targeted:
            continue
        crop = t.get("crop")
        if crop not in _FM_CROPS:
            continue
        op = cmd[0] if cmd else "PASS"
        replacing = False
        if op == "PASS" or (op == "WATER" and t.get("watered_today")):
            pass
        elif op == "WATER" and int(t.get("consecutive_unwatered", 1)) == 0:
            age = day - int(t["planted_day"])
            if crop in ("WHEAT", "CARROT") and age == 1:
                replacing = True
            elif crop == "STRAWBERRY":
                first, maxday, maxy, ongoing, interval = _FM_CROPS[crop]
                dsf = day + 1 - int(t["planted_day"]) - first
                if dsf >= 0 and dsf % interval == 0:
                    continue          # production tonight: keep today's water
                if tomorrow is None:
                    tomorrow = _fm_tape_waters(seat, day + 1)
                if pos not in tomorrow:
                    continue
                replacing = True
            else:
                continue
        else:
            continue
        tw = True
        if t.get("crop") in ("STRAWBERRY", "TOMATO"):
            if tomorrow is None:
                tomorrow = _fm_tape_waters(seat, day + 1)
            tw = pos in tomorrow
        value = _fm_gain_units(t, day, replacing, tw) * float(prices.get(crop, 0))
        if value <= fquote + 5:
            continue
        units[u] = ["FERTILIZE"]
        targeted.add(pos)
        changed = True
    if not changed:
        return action
    out = dict(action)
    out["farmer"], out["hands"] = units[0], units[1:]
    return out


_PRE_FM_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_FM_AGENT(observation, configuration)
    try:
        return _fertmore(observation, action)
    except Exception:
        return action
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--extra", type=int, default=4)
    a = ap.parse_args()
    code = (open(a.src, encoding="utf-8").read().replace("\r\n", "\n").rstrip("\n") + "\n"
            + LAYER.replace("@EXTRA@", str(a.extra)))
    compile(code, "main.py", "exec")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    print("wrote", os.path.join(a.out, "main.py"))


if __name__ == "__main__":
    main()
