r"""Route-table search against the cha22 default router (team 42, gold effort).

cha22's router picks the mid-game route tape (steps 144-647) from the first two shops only. Against an opponent that
uses the default table (the whole cha22 family, most of the field near our rating), another route can avoid selling
the same goods into the same market. For every ordered pair of first two shops this script plays candidate routes
(forced for steps 144-647, everything else identical) against the same agent on its default route, in synthetic
worlds: the pair followed by 6 uniform random shops (the engine draws shops uniformly with replacement).

Stages per pair (the result hardly depends on seat or seed, mostly on the later shops, so every game gets its own
world and seats alternate):
  S1  every candidate route on 12 worlds                              -> the best 2 with mean > +200
  S2  20 more worlds                                                  -> accepted when the best of the two has mean
      > +400 and >= 65% wins over its 32 worlds, and on the 20 fresh S2 worlds alone mean > +300 and >= 60% wins
      (v1 of this search used 2 worlds in S1 and was far too noisy).
Results: gold/arena/routesearch2.jsonl (every game batch) and gold/arena/route_table2.json (accepted entries).

.venv\Scripts\python.exe gold\arena\routesearch.py [--workers 8]
Stops between pairs when gold/arena/STOP_ROUTES exists; resumes (skips finished pairs) when restarted.
"""
import argparse
import itertools
import json
import multiprocessing as mp
import os
import random
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ARENA = os.path.join(ROOT, "gold", "arena")
sys.path.insert(0, os.path.join(ROOT, "gold", "hybrid"))
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, ARENA)

LOG = os.path.join(ARENA, "routesearch2.jsonl")
TABLE = os.path.join(ARENA, "route_table2.json")
BASE_FILE = os.path.join(ROOT, "gold", "hybrid", "cx_rs_base.py")
SHOPS = sorted(["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE", "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP",
                "FARMERS_MARKET"])
CANDS = [0, 9, 101, 105, 107, 110, 111, 115]   # 123 dropped at 03:30: its results equal 107 within 2 in every pair
SEED0 = 700000


def run_jobs(jobs, workers):
    import gstat
    with mp.get_context("spawn").Pool(max(1, min(workers, len(jobs))), maxtasksperchild=1) as pool:
        return list(pool.imap(gstat.play_one, jobs))


def diff_of(g):
    c = g["cand_side"]
    ra, rb = g["rewards"][c], g["rewards"][1 - c]
    if ra is None or rb is None or sum(g.get("errors") or [0]):
        return -99999.0
    return float(ra - rb)


def worlds_for(pair_idx, pair):
    rng = random.Random(1000 + pair_idx)
    return [list(pair) + [rng.choice(SHOPS) for _ in range(6)] for _ in range(32)]


def play(route_files, routes, worlds, seats, seed, workers):
    """Every route in `routes` on every world in `worlds`, candidate in each seat of `seats`. Returns {route: [diffs]}."""
    jobs, keys = [], []
    for r in routes:
        for wi, w in enumerate(worlds):
            for s in seats:
                a, b = (route_files[r], BASE_FILE) if s == 0 else (BASE_FILE, route_files[r])
                jobs.append((a, b, seed + wi, s, w))
                keys.append(r)
    out = {r: [] for r in routes}
    for k, g in zip(keys, run_jobs(jobs, workers)):
        out[k].append(diff_of(g))
    return out


def play_alt(route_files, routes, worlds, seed, workers):
    """Every route on every world, one game per world, candidate seat alternating with the world index."""
    jobs, keys = [], []
    for r in routes:
        for wi, w in enumerate(worlds):
            s = wi % 2
            a, b = (route_files[r], BASE_FILE) if s == 0 else (BASE_FILE, route_files[r])
            jobs.append((a, b, seed + wi, s, w))
            keys.append(r)
    out = {r: [] for r in routes}
    for k, g in zip(keys, run_jobs(jobs, workers)):
        out[k].append(diff_of(g))
    return out


def main():
    import layers
    import boldsearch
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    defaults = json.load(open(os.path.join(ROOT, "gold", "tmp", "default_routes.json")))
    if not os.path.exists(BASE_FILE):
        champ = json.load(open(os.path.join(ARENA, "champion.json"), encoding="utf-8"))
        cfg = boldsearch.parse_full(champ["path"])
        for k in ("route_table", "force_route", "late_route"):
            cfg.pop(k, None)
        layers.write(BASE_FILE, "rs_base", f"路线搜索的对手：{champ['name']} 去掉路线表（cha22 默认路线）", cfg)
    base_cfg = boldsearch.parse_full(BASE_FILE)
    route_files = {}
    for r in CANDS:
        path = os.path.join(ROOT, "gold", "hybrid", f"cx_rs_force{r}.py")
        if not os.path.exists(path):
            cfg = dict(base_cfg, force_route=r)
            layers.write(path, f"rs_force{r}", f"路线搜索：强制第 {r} 号路线（144 到 647 步）", cfg)
        route_files[r] = path
    done = set()
    if os.path.exists(LOG):
        for line in open(LOG, encoding="utf-8"):
            if line.strip():
                rec = json.loads(line)
                if rec.get("final"):
                    done.add(rec["pair"])
    table = json.load(open(TABLE)) if os.path.exists(TABLE) else {}
    pairs = list(itertools.product(SHOPS, SHOPS))
    # YARN pairs first (default route 9, the biggest gains in the oracle), then route-105 pairs, then the rest.
    pairs.sort(key=lambda p: (defaults["|".join(p)] != 9, defaults["|".join(p)] != 105, p))

    def log(rec):
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    for pi, pair in enumerate(pairs):
        key = "|".join(pair)
        if key in done:
            continue
        if os.path.exists(os.path.join(ARENA, "STOP_ROUTES")):
            break
        dflt = defaults[key]
        worlds = worlds_for(SHOPS.index(pair[0]) * 8 + SHOPS.index(pair[1]), pair)
        seed = SEED0 + 100 * (SHOPS.index(pair[0]) * 8 + SHOPS.index(pair[1]))
        cands = [r for r in CANDS if r != dflt]
        s1 = play_alt(route_files, cands, worlds[:12], seed, a.workers)
        log({"pair": key, "default": dflt, "stage": 1, "res": s1})
        mean = {r: sum(v) / len(v) for r, v in s1.items()}
        top = [r for r in sorted(mean, key=mean.get, reverse=True)[:2] if mean[r] > 200]
        best, verdict = None, "none"
        if top:
            s2 = play_alt(route_files, top, worlds[12:32], seed + 12, a.workers)
            log({"pair": key, "default": dflt, "stage": 2, "res": s2})
            allv = {r: s1[r] + s2[r] for r in top}
            r = max(allv, key=lambda x: sum(allv[x]) / len(allv[x]))
            v = allv[r]
            wins = sum(x > 0 for x in v) / len(v)
            fresh = s2[r]     # S2 worlds were not used to pick the route: require the gain there too
            fresh_ok = sum(fresh) / len(fresh) > 300 and sum(x > 0 for x in fresh) >= 0.6 * len(fresh)
            if sum(v) / len(v) > 400 and wins >= 0.65 and fresh_ok:
                best, verdict = r, "accepted"
                table[key] = r
                json.dump(table, open(TABLE, "w"), indent=1, sort_keys=True)
            else:
                verdict = f"rejected {r} mean {sum(v) / len(v):+.0f} wins {wins:.0%}"
        log({"pair": key, "default": dflt, "final": True, "best": best, "verdict": verdict})


if __name__ == "__main__":
    main()
