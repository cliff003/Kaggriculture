r"""Run one game A vs B with a seed, print result + agent errors + day summary.  one.py A B SEED"""
import sys, os, collections, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
import fastarena
a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
fa = fastarena.load_agent(a)
fb = fastarena.load_agent(b)
r = fastarena.run_game(fa, fb, seed, quiet=True)
print("rewards", r["rewards"], "errors", r["errors"], "t_mean %.4f t_max %.3f" % (r["t_mean"][0], r["t_max"][0]))
g = fa.__globals__
for k, S in g.get("STATE", {}).items():
    print("player", k, "errors", S.get("errors", [])[:5])
    if S.get("tb"):
        print(S["tb"])
st = r["final_state"]
for i in range(2):
    f = st[0].observation.farms[i]
    print(i, f["money"], f["unlocked_quadrants"])
    for row in f["tiles"]:
        print("  " + " ".join((t if t is None or isinstance(t, str) else (t.get("animal") or t.get("crop") or t.get("kind")))[:2] if t else ".." for t in row))
