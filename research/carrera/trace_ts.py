"""Trace one live-tape replay with a candidate: tomato / strawberry tiles per day, seeds, money, layer telemetry."""
import gzip, json, os, sys, collections
sys.path.insert(0, "tools")
import fastarena, forceshops
from cfreplay import tape_agent
sys.path.insert(0, "research/carrera")
from ab_replay import tapes
path, gid = sys.argv[1], int(sys.argv[2])
rec = tapes()[gid]
forceshops.force(rec["shops"])
me = rec["teams"].index("42")
ours = fastarena.load_agent(path)
fns = [tape_agent(a) for a in rec["acts"]]
snaps = {}
def spy(obs, conf=None):
    a = ours(obs, conf)
    s = int(obs["step"])
    if s % 24 == 20 and 9 <= s // 24 <= 22:
        farm = obs["farms"][obs["player"]]
        c = collections.Counter()
        for row in farm["tiles"]:
            for t in row:
                if isinstance(t, dict): c[t.get("crop") or t.get("animal") or t.get("kind")] += 1
        snaps[s // 24] = (round(farm["money"]), dict(c), dict((k, v) for k, v in obs["private"]["seeds"].items() if v))
    return a
fns[me] = spy
res = fastarena.run_game(fns[0], fns[1], rec["seed"])
print("shops", rec["shops"][:6], "margin", res["rewards"][me] - res["rewards"][1 - me])
for d, (m, c, seeds) in sorted(snaps.items()):
    print(f"day {d}: money {m} tiles {c} seeds {seeds}")
g = ours.__globals__
print("TS", g.get("_CG_TS_REPORT"))
ns = g.get("_BASE_NS") or {}
for k in sorted(ns):
    if k.endswith("_REPORT") and isinstance(ns[k], dict):
        nz = {a: b for a, b in ns[k].items() if b}
        if nz and any(w in k for w in ("E343", "RECOV", "WEED", "V219", "LAG", "REPLAY", "DIVERG", "CHASSIS")):
            print(k, nz)
