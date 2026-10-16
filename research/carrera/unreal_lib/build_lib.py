r"""Route library from harvested unreal games (feasibility test for a production-type route, not a submission).

.venv/bin/python research/carrera/unreal_lib/build_lib.py research/carrera/tapes/unreal_56618268.jsonl.gz

unreal's unit actions branch from day 0, but at the end of day 5 most of its games share one of two farm layouts. The
opening (steps 0-143) is the best game with the most common day-5 layout; from step 144 the route is chosen by the
first two shops, among games with that same layout (best final money per pair; a pair not covered falls back to the
best game with the same first shop, then to the opening game). Writes routes.json.gz next to this script.
"""
import collections
import gzip
import json
import multiprocessing as mp
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
SHOPS = ["BAKERY", "BRUNCH_SPOT", "FARMERS_MARKET", "ICE_CREAM_SHOP", "PET_CAFE", "PIZZA_SHOP", "SMOOTHIE_SHOP", "YARN_STORE"]


def layout(r):
    import econ
    K = econ.K
    env = econ.make("kaggriculture", configuration={"episodeSteps": 720, "seed": r["seed"]}, debug=False)
    env.reset(2)
    state = env.state
    econ._CUR.update(log=[], farms=state[0].observation.farms, privates=[s.observation.private for s in state],
                     prices=state[0].observation.market["prices"])
    i = r["teams"].index("unreal")
    n = len(r["acts"][0])
    for t in range(144):
        econ._CUR["step"] = t
        for k in range(2):
            a = r["acts"][k][t + 1] if t + 1 < n else None
            state[k].action = a if isinstance(a, dict) else None
        K.interpreter(state, env)
        state[0].observation.step = t + 1
    f = state[0].observation.farms[i]
    return r["id"], tuple((x, y, c.get("animal") or c.get("crop") or c.get("kind"))
                          for y, row in enumerate(f["tiles"]) for x, c in enumerate(row)
                          if isinstance(c, dict) and c.get("kind") != "WEED")


def tape(r):
    i = r["teams"].index("unreal")
    return [a if isinstance(a, dict) else {"farmer": ["PASS"], "hands": [], "market": []} for a in r["acts"][i][1:]]


def main():
    with gzip.open(sys.argv[1], "rt", encoding="utf-8") as f:
        recs = [json.loads(line) for line in f if line.strip()]
    with mp.Pool(8) as pool:
        lays = dict(pool.map(layout, recs))
    common = collections.Counter(lays.values()).most_common(1)[0][0]
    good = [r for r in recs if lays[r["id"]] == common]
    money = {r["id"]: r["rewards"][r["teams"].index("unreal")] for r in recs}
    best = lambda rs: max(rs, key=lambda r: money[r["id"]])
    opening = best(good)
    by_pair = collections.defaultdict(list)
    by_first = collections.defaultdict(list)
    for r in good:
        by_pair[tuple(r["shops"][:2])].append(r)
        by_first[r["shops"][0]].append(r)
    chosen, source = {}, collections.Counter()
    for a in SHOPS:
        for b in SHOPS:
            if (a, b) in by_pair:
                chosen[(a, b)] = best(by_pair[(a, b)]); source["pair"] += 1
            elif a in by_first:
                chosen[(a, b)] = best(by_first[a]); source["first shop"] += 1
            else:
                chosen[(a, b)] = opening; source["opening game"] += 1
    ids = sorted({r["id"] for r in chosen.values()} | {opening["id"]})
    tapes = {str(g): tape(next(r for r in recs if r["id"] == g)) for g in ids}
    out = {"opening": str(opening["id"]), "pairs": {f"{a}|{b}": str(r["id"]) for (a, b), r in chosen.items()}, "tapes": tapes}
    path = os.path.join(HERE, "routes.json.gz")
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"{len(good)}/{len(recs)} games share the common day-5 layout; opening game {opening['id']} "
          f"(money {money[opening['id']]:.0f}); 64 pairs from {dict(source)}; {len(tapes)} distinct tapes -> {path}")


if __name__ == "__main__":
    main()
