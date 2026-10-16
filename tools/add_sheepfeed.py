r"""Append the SHEEPFEED fix as the outermost layer of a team-42 agent (v6b, v7b and their descendants).

.venv\Scripts\python.exe tools\add_sheepfeed.py IN_MAIN_PY OUT_DIR

cha22's one-worker service for the six SE sheep (V233 + the single-lane worker) deadlocks when the shed runs
out of wheat: `hungry > carried` makes it issue PICKUP WHEAT 0 every turn for the rest of the day, so the six
sheep are neither fed nor cared for (a lost production bonus on their production day). Its wheat rescue does
not fire whenever any order of the turn mentions wheat, which the route tape (and v7b's wheat lead-sell)
often does. This layer runs after everything else:
  1. a V233 worker whose PICKUP of wheat cannot get any feeds the nearest hungry sheep with what it carries,
     otherwise cares for a fed sheep or harvests wool;
  2. while the committed sheep are short of feed (hungry - carried - shed wheat after this turn), SELL WHEAT
     orders of this turn are cut by the shortage and the rest is bought (until hour 20).
"""
import argparse
import os

LAYER = r'''

# ---------------------------------------------------------------------------
# Team 42 SHEEPFEED fix (outermost layer): see tools/add_sheepfeed.py.
_SF_MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}


def _sf_ns():
    return globals().get("_BASE_NS") or globals()


def _sf_walk(pos, target):
    x, y = pos
    tx, ty = target
    if x != tx:
        return ["EAST" if x < tx else "WEST"]
    if y != ty:
        return ["SOUTH" if y < ty else "NORTH"]
    return None


_SF_STUCK = {}


def _sheepfeed(obs, action):
    step = int(obs["step"])
    day, hour = divmod(step, 24)
    seat0 = int(obs["player"])
    rec = _SF_STUCK.get(seat0)
    if rec is None or step <= rec["step"]:
        rec = _SF_STUCK[seat0] = {"step": -1, "run": {}, "stall_day": {}}
    rec["step"] = step
    if day < 11 or step >= 717 or not isinstance(action, dict):
        return action
    seat = int(obs["player"])
    st = (_sf_ns().get("_V233_STATES") or {}).get(seat)
    if not st or not st.get("committed") or not st.get("workers"):
        return action
    farm = obs["farms"][seat]
    priv = obs["private"]
    tiles = farm["tiles"]
    hands = farm["hands"]
    units = [list(action.get("farmer") or ["PASS"])] + [list(c) for c in (action.get("hands") or [])]
    positions = [tuple(farm["farmer"])] + [tuple(h) for h in hands]
    access = {(4, 4), (5, 4), (4, 5), (5, 5)}
    invs = priv.get("inventories") or []
    shed_wheat = int((priv.get("shed") or {}).get("WHEAT", 0))
    sheep = {}
    for targets in st["workers"].values():
        for x, y in targets:
            t = tiles[y][x]
            if isinstance(t, dict) and t.get("animal") == "SHEEP":
                sheep[(x, y)] = t
    hungry = [xy for xy, t in sheep.items() if not t.get("fed_today")]
    changed = False
    stalled = False
    # wheat the earlier units pick up this turn, in engine order (farmer, then hands by index)
    left = shed_wheat
    for i, cmd in enumerate(units[:len(positions)]):
        pickup = bool(cmd) and cmd[0] == "PICKUP" and len(cmd) >= 2 and cmd[1] == "WHEAT" and positions[i] in access
        want = (int(cmd[2]) if len(cmd) >= 3 else 1) if pickup else 0
        if i in st["workers"]:
            if pickup:
                stuck_now = want <= 0 or left <= 0
                run = rec["run"].get(i, 0) + 1 if stuck_now else 0
                rec["run"][i] = run
                if stuck_now and run >= 2:   # a real deadlock: nothing to pick up on two turns in a row
                    rec["stall_day"][i] = day
            if rec["stall_day"].get(i) == day:
                # take the worker over for the day while it cannot get wheat from the shed
                stalled = True
                inv = invs[i] if i < len(invs) else {}
                pos = positions[i]
                new = None
                if int(inv.get("WHEAT", 0)) > 0 and hungry:
                    here = sheep.get(pos)
                    if not (cmd == ["FEED"] and here is not None and not here.get("fed_today")):
                        target = min(hungry, key=lambda xy: (abs(pos[0] - xy[0]) + abs(pos[1] - xy[1]), xy))
                        new = _sf_walk(pos, target) or ["FEED"]
                elif left <= 0 or not hungry:
                    todo = [xy for xy, t in sheep.items() if t.get("fed_today") and not t.get("cared_today")]
                    todo = todo or [xy for xy, t in sheep.items() if int(t.get("yield_units", 0)) > 0]
                    if todo:
                        target = min(todo, key=lambda xy: (abs(pos[0] - xy[0]) + abs(pos[1] - xy[1]), xy))
                        t = sheep[target]
                        new = _sf_walk(pos, target) or (["CARE"] if t.get("fed_today") and not t.get("cared_today")
                                                         else ["HARVEST"])
                if new:
                    units[i] = new
                    changed = True
                    continue
        if pickup:
            left -= min(max(0, want), left)
    carried = sum(int((invs[i] if i < len(invs) else {}).get("WHEAT", 0)) for i in st["workers"])
    short = len(hungry) - carried - left
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple)) and o]
    if stalled and short > 0 and hour <= 20:
        for o in market:
            if short > 0 and o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT" and int(o[2]) > 0:
                cut = min(int(o[2]), short)
                o[2] = int(o[2]) - cut
                short -= cut
                changed = True
        buying = sum(int(o[2]) for o in market if o[0] == "BUY_PRODUCT" and len(o) >= 3 and o[1] == "WHEAT")
        need = min(6, short - buying)
        quote = int((obs["market"]["prices"] or {}).get("WHEAT", 0))
        if need > 0 and 0 < quote and float(farm.get("money", 0)) > 1000 + need * (quote + 10):
            for o in market:
                if o[0] == "BUY_PRODUCT" and len(o) >= 3 and o[1] == "WHEAT":
                    o[2] = int(o[2]) + need
                    break
            else:
                if len(market) >= 10:
                    market = [o for o in market if not (o[0] == "SELL" and len(o) >= 3 and int(o[2]) <= 0)]
                if len(market) < 10:
                    market.insert(0, ["BUY_PRODUCT", "WHEAT", need])
            changed = True
    if not changed:
        return action
    out = dict(action)
    out["farmer"], out["hands"] = units[0], units[1:]
    out["market"] = market[:10]
    return out


_PRE_SF_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_SF_AGENT(observation, configuration)
    try:
        return _sheepfeed(observation, action)
    except Exception:
        return action
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    a = ap.parse_args()
    code = open(a.src, encoding="utf-8").read().replace("\r\n", "\n").rstrip("\n") + "\n" + LAYER
    compile(code, "main.py", "exec")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    print("wrote", os.path.join(a.out, "main.py"))


if __name__ == "__main__":
    main()
