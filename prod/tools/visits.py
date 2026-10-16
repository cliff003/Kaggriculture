r"""Moves per tile visit, both sides.  visits.py A B SEED D0 D1 [k=v ...]"""
import sys, os, json, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
import fastarena
from kaggle_environments.envs.kaggriculture import kaggriculture as K
a, b, seed, d0, d1 = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
ov = {}
for kv in sys.argv[6:]:
    k, v = kv.split("=", 1)
    try: v = json.loads(v)
    except Exception: pass
    ov[k] = v
fa = fastarena.load_agent(a); fb = fastarena.load_agent(b)
if "STATE" in fa.__globals__:
    fa.__globals__["STATE"]["_override"] = ov
orig = K.interpreter
stats = collections.defaultdict(collections.Counter)
last = {}
def interp(state, env):
    o = state[0].observation
    if hasattr(o, "farms") and o.farms:
        st = o.get("step", 0); d = st // 24
        if d0 <= d <= d1:
            for side in (0, 1):
                f = o.farms[side]
                pos = [tuple(f["farmer"])] + [tuple(h) for h in f["hands"]]
                act = state[side].action or {}
                ua = [act.get("farmer")] + list(act.get("hands", []))
                for ui, (p, u) in enumerate(zip(pos, ua)):
                    if not u: continue
                    op = u[0]
                    if op in ("NORTH", "SOUTH", "EAST", "WEST"):
                        stats[side]["move"] += 1; last[(side, ui)] = None; continue
                    if op == "PASS":
                        stats[side]["pass"] += 1; continue
                    kind = "shed" if op in ("PICKUP", "DROP", "PLACE") and p in [(4,4),(5,4),(4,5),(5,5)] else "tile"
                    if last.get((side, ui)) != p:
                        stats[side]["v_" + kind] += 1
                    last[(side, ui)] = p
                    stats[side]["ops"] += 1
    return orig(state, env)
K.interpreter = interp
r = fastarena.run_game(fa, fb, seed)
print("rewards", r["rewards"])
for side in (0, 1):
    s = stats[side]
    print(side, dict(s), "moves/tilevisit %.2f" % (s["move"] / max(1, s["v_tile"])))
