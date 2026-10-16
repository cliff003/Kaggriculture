"""Build a g036-family agent whose petal router is replaced by the insertion planner of executor.py.

    .venv\\Scripts\\python.exe gold\\newagent\\mk_router.py BASE_MAIN_PY OUT_NAME [KEY=VALUE ...]

Only the assignment and ordering of tile jobs changes (plan_all's petal_plan call); stops, pickups, deliveries,
unloads, rebalancing and the market stay as in the base agent.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

GLUE = r'''

# ================================================================================================ insertion router
ROUTER = "ins"
ROUTE_TRIES = 2
ROUTE_LAT = 0.3
ROUTE_BAL = 0.5
_EXEC_SRC = None
_XNS = {}


def _xns():
    if not _XNS:
        exec(compile(_EXEC_SRC, "executor", "exec"), _XNS)
        _XNS["LAT_W"] = ROUTE_LAT
    return _XNS


def ins_plan(units, jobs, s):
    """units: dicts idx, pos, cap, inv (as petal_plan). Returns {idx: [tile xy, ...]}; jobs that do not fit stay
    unassigned (idle units pick them up)."""
    X = _xns()
    out = {u["idx"]: [] for u in units}
    if not jobs or not units:
        return out
    xj = {}
    for xy, j in jobs.items():
        ops = [[op, arg] for (op, arg, pr) in j.ops]
        xj[xy] = X["Job"](xy, xy, ops, earliest=0, prio=j.prio, value=1.0)
    n = len(s.units)
    spec = []
    for u in units:
        inv = u.get("inv") or {}
        an = {a: inv.get(a, 0) for a in ANIMALS if inv.get(a, 0) > 0}
        t_free = s.step if u["idx"] < n else s.step + 1
        spec.append((u["idx"], tuple(u["pos"]), t_free, inv.get("WHEAT", 0), inv.get("FERTILIZER", 0), an))
    t_end = min(s.day * TPD + TPD, LAST_STEP + 1)
    stock_w = s.shed.get("WHEAT", 0)
    stock_f = s.shed.get("FERTILIZER", 0)
    best = None
    rng = __import__("random").Random(s.step)
    for trial in range(max(1, ROUTE_TRIES)):
        P = X["Planner"](xj, spec, s.step, t_end, stock_w, stock_f, ROUTE_BAL)
        P.lat_w = ROUTE_LAT
        P.strip_fert = False
        P.jitter = 0.0 if trial == 0 else 1.0
        P.rng = rng
        routes, dropped = P.build(list(xj), [[] for _ in spec], [0] * len(spec))
        lost = sum(xj[j].dur for j in dropped)
        tot = sum(P.val(P.cost_of(k, routes[k])) for k in range(len(spec)))
        if best is None or (lost, tot) < best[0]:
            best = ((lost, tot), routes)
    routes = best[1]
    for k, u in enumerate(units):
        out[u["idx"]] = list(routes[k])
    return out
'''


def main():
    base, name = sys.argv[1], sys.argv[2]
    src = open(base, encoding="utf-8").read()
    ex = open(os.path.join(HERE, "executor.py"), encoding="utf-8").read()
    assert "'''" not in ex
    call = "    seqs = petal_plan(units, work)\n"
    assert src.count(call) == 1
    src = src.replace(call, "    seqs = ins_plan(units, work, s) if ROUTER == \"ins\" else petal_plan(units, work)\n")
    i = src.rindex("\ndef agent(obs, config=None):")
    glue = GLUE.replace("_EXEC_SRC = None", "_EXEC_SRC = r'''" + ex + "'''", 1)
    src = src[:i] + "\n" + glue + src[i:]
    for kv in sys.argv[3:]:
        k, v = kv.split("=", 1)
        src, c = re.subn(r"(?m)^" + re.escape(k) + r" = .*$", lambda m: k + " = " + v, src, count=1)
        assert c == 1, k
    out = os.path.join(ROOT, "gold", "builds", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(src)
    print(os.path.join(out, "main.py"))


if __name__ == "__main__":
    main()
