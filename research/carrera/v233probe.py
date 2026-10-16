"""Replay live tapes with a candidate in our seat and report cha22's V233 / SHEEPX telemetry and wool sold."""
import gzip, json, sys, os
sys.path.insert(0, "tools")
import fastarena, forceshops
from cfreplay import tape_agent
path = sys.argv[1]
ids = set(int(x) for x in sys.argv[2:])
recs = {}
for p in ["research/carrera/tapes/live_pub.jsonl.gz"] + [os.path.join("data/games", f) for f in os.listdir("data/games") if f.startswith("live_")]:
    for line in gzip.open(p, "rt"):
        r = json.loads(line)
        if r["id"] in ids: recs.setdefault(r["id"], r)
for gid, r in recs.items():
    forceshops.force(r["shops"])
    me = r["teams"].index("42")
    ours = fastarena.load_agent(path)
    fns = [tape_agent(a) for a in r["acts"]]; fns[me] = ours
    res = fastarena.run_game(fns[0], fns[1], r["seed"])
    g = ours.__globals__
    ns = g.get("_BASE_NS") or {}
    rep = {k: v for k, v in (ns.get("_V233_REPORT") or {}).items() if v}
    ve = {k: v for k, v in (ns.get("_VE_REPORT") or {}).items() if v}
    sx = {k: v for k, v in (g.get("_SX_REPORT") or {}).items() if v}
    print(gid, r["teams"][1 - me][:14], "shops", ",".join(s[:4] for s in r["shops"][:6]), "margin", res["rewards"][me] - res["rewards"][1 - me])
    print("    V233", rep, "VE", ve, "SX", sx)
