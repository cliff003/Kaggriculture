r"""Crop deaths of side 0 with route status at h23 (hybrid or p3).  deaths.py AGENT SEED [k=v ...]"""
import sys, os, json, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
import fastarena
from kaggle_environments.envs.kaggriculture import kaggriculture as K
a, seed = sys.argv[1], int(sys.argv[2])
ov = {}
for kv in sys.argv[3:]:
    k, v = kv.split("=", 1)
    try: v = json.loads(v)
    except Exception: pass
    ov[k] = v
fa = fastarena.load_agent(a); fb = fastarena.load_agent("submissions/v8_own_cha22_tick_guard10/main.py")
fa.__globals__["STATE"]["_override"] = ov
def pstate():
    ns = fa.__globals__.get("_NS")
    if ns and "p3" in ns:
        return ns["p3"]["STATE"].get(0)
    return fa.__globals__["STATE"].get(0)
orig = K.interpreter
deaths = []
snap = {}
def interp(state, env):
    o = state[0].observation
    st = o.get("step", 0) if hasattr(o, "farms") and o.farms else None
    before = None
    if st is not None and (st + 1) % 24 == 0:
        before = [[dict(t) if isinstance(t, dict) else t for t in row] for row in o.farms[0]["tiles"]]
        S = pstate()
        if S:
            snap[st // 24] = {s2["pos"]: (i, s2["job"].get("value"), len(r), [x["pos"] for x in r[:2]]) for i, r in S["routes"].items() for s2 in r if s2["kind"] == "tile"}
            pos = [tuple(o.farms[0]["farmer"])] + [tuple(h) for h in o.farms[0]["hands"]]
            snap[(st // 24, "pos")] = pos
    r = orig(state, env)
    if before is not None:
        after = o.farms[0]["tiles"]
        for y in range(10):
            for x in range(10):
                tb, ta = before[y][x], after[y][x]
                if isinstance(tb, dict) and tb.get("kind") == "PLANT" and isinstance(ta, dict) and ta.get("kind") == "WEED":
                    d = st // 24
                    deaths.append((d, (x, y), tb["crop"], d - tb["planted_day"], tb["watered_today"], tb["yield_units"], snap.get(d, {}).get((x, y))))
                if isinstance(tb, dict) and tb.get("animal") and isinstance(ta, dict) and not ta.get("animal"):
                    deaths.append((st // 24, (x, y), "ESC:" + tb["animal"], None, None, None, snap.get(st // 24, {}).get((x, y))))
    return r
K.interpreter = interp
r = fastarena.run_game(fa, fb, seed)
K.interpreter = orig
print("rewards", r["rewards"])
for dd in deaths:
    print(dd)
