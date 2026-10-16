r"""Hill-climbing search over agent CFG overrides against an opponent.

search.py AGENT OPP --train 6000-6019 --valid 7000-7019 --iters 200 --out prod/results/search_X.jsonl
Each candidate = 2 seats x train seeds. Accept if mean margin improves by > accept_se * se.
"""
import argparse, json, os, random, sys, time, statistics, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
import bench

SPACE = {
    "melons_d0": [8, 10, 12, 14, 16],
    "opening_style": ["race", "dsm"],
    "cows_d0": [1, 2, 3], "sheep_d0": [1, 2, 3], "geese_d0": [0, 1, 2],
    "sheep_base": [1, 3, 5, 7], "cow_base": [3, 5, 7, 9], "animal_total": [14, 17, 20, 23, 26],
    "animal_order": [["SHEEP", "COW", "GOOSE"], ["COW", "SHEEP", "GOOSE"], ["COW", "GOOSE", "SHEEP"], ["GOOSE", "COW", "SHEEP"]],
    "straw_a": [5, 10, 13, 18, 25], "straw_b": [0, 4, 8.7, 12],
    "tom_a": [0, 5, 10, 14, 20], "tom_b": [0, 3, 7.2, 10],
    "car_a": [0, 5, 13, 20], "car_b": [0, 2, 4, 6], "car_early_frac": [0, 0.35, 0.7],
    "straw_early": [0, 5, 10, 14], "straw_last": [10, 12, 13, 15],
    "tom_first": [8, 9, 11], "tom_last": [14, 16, 18, 20], "car_first": [10, 14, 18],
    "animal_last_day": [9, 11, 12, 14], "animal_max_dist": [2, 3, 4],
    "max_hands": [10, 11, 12, 13], "max_hands_extra": [12, 13, 14, 15], "extra_hand_ratio": [1.0, 1.5, 2.5],
    "hands_min": [3, 4, 5, 6],
    "land_days": [[6, 9, 99], [5, 9, 99], [7, 10, 99], [6, 11, 99], [6, 9, 12], [6, 9, 10], [6, 99, 99]],
    "feed_skip": [True, False], "feed_ratio": [1.5, 2.5, 3.5],
    "fert_wheat_max": [0, 30, 45, 70, 999], "fert_carrot_max": [0, 30, 45, 999], "fert_premium_max": [60, 999],
    "wheat_per_animal": [0.3, 0.5, 0.65, 0.8, 1.0],
    "mid_drop_until": [0, 10], "drop_load": [8, 12, 20, 99],
    "reserve_frac": [0.5, 1.0, 1.5],
    "race_water_dist": [0, 2, 3], "race_hands": [10, 12, 14],
}


SOLO = False


def evaluate(pool, agent, opp, seeds, ov):
    jobs = []
    for s in seeds:
        jobs.append((agent, opp, s, False, ov))
        if not SOLO:
            jobs.append((agent, opp, s, True, ov))
    res = pool.map(bench._play, jobs)
    if SOLO:
        marg = [r["rewards"][r["me"]] for r in res]
    else:
        marg = [r["rewards"][r["me"]] - r["rewards"][1 - r["me"]] for r in res]
    wins = sum(1 for m in marg if m > 0)
    return statistics.mean(marg), statistics.pstdev(marg) / len(marg) ** 0.5, wins, statistics.mean(r["rewards"][r["me"]] for r in res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent")
    ap.add_argument("opp")
    ap.add_argument("--train", default="6000-6019")
    ap.add_argument("--valid", default="7000-7019")
    ap.add_argument("--iters", type=int, default=100)
    ap.add_argument("--start", default="{}")
    ap.add_argument("--accept-se", type=float, default=0.5)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("-j", type=int, default=14)
    ap.add_argument("--solo", action="store_true")
    a = ap.parse_args()
    global SOLO
    SOLO = a.solo
    rng = random.Random(a.seed)
    train = bench.parse_seeds(a.train)
    valid = bench.parse_seeds(a.valid)
    cur = json.loads(a.start)
    with mp.get_context("spawn").Pool(a.j) as pool:
        best, se, w, me = evaluate(pool, a.agent, a.opp, train, cur)
        print(f"start {best:+.0f} (se {se:.0f}) W{w} me {me:.0f} {cur}", flush=True)
        log = open(a.out, "a", encoding="utf-8")
        log.write(json.dumps({"it": 0, "ov": cur, "m": best, "se": se, "w": w, "acc": True}) + "\n")
        for it in range(1, a.iters + 1):
            cand = dict(cur)
            nmut = rng.choice([1, 1, 1, 2, 2, 3])
            keys = rng.sample(list(SPACE), nmut)
            for k in keys:
                opts = [v for v in SPACE[k] if cand.get(k) != v]
                cand[k] = rng.choice(opts)
            t0 = time.time()
            m, se2, w2, me2 = evaluate(pool, a.agent, a.opp, train, cand)
            acc = m > best + a.accept_se * se2
            print(f"it {it} {m:+.0f} (se {se2:.0f}) W{w2} me {me2:.0f} {'ACCEPT' if acc else ''} {dict((k, cand[k]) for k in keys)} [{time.time() - t0:.0f}s]", flush=True)
            log.write(json.dumps({"it": it, "ov": cand, "m": m, "se": se2, "w": w2, "acc": acc, "keys": keys}) + "\n")
            log.flush()
            if acc:
                cur, best = cand, m
                if it % 1 == 0:
                    vm, vse, vw, vme = evaluate(pool, a.agent, a.opp, valid, cur)
                    print(f"   valid {vm:+.0f} (se {vse:.0f}) W{vw} me {vme:.0f} :: {cur}", flush=True)
                    log.write(json.dumps({"it": it, "valid": vm, "vse": vse, "vw": vw, "ov": cur}) + "\n")
                    log.flush()
        print("FINAL", best, cur)


if __name__ == "__main__":
    main()
