"""Tomato-world panel: random shop lists forced to have >= 4 pizza shops / farmers markets among the first six."""
import json, multiprocessing as mp, os, random, statistics as st, sys, collections
ROOT = "/Users/cliff/Documents/coding/kaggriculture_handoff_20260927/project"
sys.path.insert(0, os.path.join(ROOT, "tools"))
SHOPS = ["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE", "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP", "FARMERS_MARKET"]

def run(job):
    import fastarena, forceshops
    rival, rpath, path, seed, shops, me = job
    forceshops.force(shops)
    fns = [fastarena.load_agent(path), fastarena.load_agent(rpath)]
    if me: fns.reverse()
    r = fastarena.run_game(*fns, seed)
    return {"rival": rival, "path": path, "seed": seed, "seat": me, "margin": r["rewards"][me] - r["rewards"][1 - me], "status": r["status"]}

if __name__ == "__main__":
    os.environ["PYTHONHASHSEED"] = "0"
    paths = [os.path.abspath(p) for p in sys.argv[1:]]
    rng = random.Random(20260928)
    worlds = []
    while len(worlds) < 16:
        sh = [rng.choice(SHOPS) for _ in range(8)]
        if sum(s in ("PIZZA_SHOP", "FARMERS_MARKET") for s in sh[:6]) >= 4:
            worlds.append((2026092900 + len(worlds), sh))
    rivals = {n: os.path.join(ROOT, "research/panel", n, "main.py") for n in ("cha22", "emu_eager", "morewheat", "emu_tick0", "rescue")}
    jobs = [(n, rp, p, s, sh, me) for s, sh in worlds for me in (0, 1) for n, rp in rivals.items() for p in paths]
    with mp.get_context("spawn").Pool(8) as pool:
        res = pool.map(run, jobs, chunksize=1)
    key = lambda r: (r["rival"], r["seed"], r["seat"])
    base = {key(r): r["margin"] for r in res if r["path"] == paths[0]}
    for p in paths:
        sub = [r for r in res if r["path"] == p]
        by = collections.defaultdict(list)
        for r in sub: by[r["rival"]].append(r)
        print(os.path.relpath(p, ROOT), f"games {len(sub)} wins {sum(r['margin'] > 0 for r in sub)} mean change {st.mean(r['margin'] - base[key(r)] for r in sub):+.0f}",
              f"flips up {sum(base[key(r)] <= 0 < r['margin'] for r in sub)} down {sum(r['margin'] <= 0 < base[key(r)] for r in sub)}",
              "| " + "  ".join(f"{n}: {sum(r['margin'] > 0 for r in rs)}/{len(rs)} {st.mean(r['margin'] - base[key(r)] for r in rs):+.0f}" for n, rs in sorted(by.items())))
