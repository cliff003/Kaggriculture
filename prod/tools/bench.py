r"""Benchmark candidate vs opponent on seeds (both seats), with optional CFG overrides.
bench.py CAND OPP --seeds 6000-6019 [--set key=val ...] [--tag name] [-j 14]
Prints win rate, mean money both sides, mean margin, and per-item sales for the candidate."""
import argparse, json, os, sys, time, statistics, collections, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))

_AG = {}


def _play(args):
    cand, opp, seed, swap, overrides = args
    import acct, fastarena
    if cand not in _AG:
        _AG[cand] = fastarena.load_agent(cand)
    if opp not in _AG:
        _AG[opp] = fastarena.load_agent(opp)
    fa = _AG[cand]
    g = fa.__globals__
    if "STATE" in g:
        g["STATE"]["_override"] = overrides
    fb = _AG[opp]
    acct._CUR["log"] = []
    acct._CUR["snaps"] = []
    acct._CUR["farms"] = None
    if swap:
        r = fastarena.run_game(fb, fa, seed)
        me = 1
    else:
        r = fastarena.run_game(fa, fb, seed)
        me = 0
    sides = [acct.summarize(acct._CUR["log"], 0), acct.summarize(acct._CUR["log"], 1)]
    errs = g.get("STATE", {}).get(me, {}).get("errors", []) if isinstance(g.get("STATE", {}).get(me), dict) else []
    return {"seed": seed, "me": me, "rewards": r["rewards"], "sides": sides, "errors": errs[:2]}


def parse_seeds(s):
    out = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("opp")
    ap.add_argument("--seeds", default="6000-6019")
    ap.add_argument("--set", nargs="*", default=[])
    ap.add_argument("--tag", default="")
    ap.add_argument("--one-seat", action="store_true")
    ap.add_argument("-j", type=int, default=14)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    ov = {}
    for kv in a.set:
        k, v = kv.split("=", 1)
        try:
            v = json.loads(v)
        except Exception:
            pass
        ov[k] = v
    jobs = []
    for s in parse_seeds(a.seeds):
        jobs.append((a.cand, a.opp, s, False, ov))
        if not a.one_seat:
            jobs.append((a.cand, a.opp, s, True, ov))
    t0 = time.time()
    with mp.get_context("spawn").Pool(min(a.j, len(jobs))) as pool:
        res = pool.map(_play, jobs)
    wins = sum(1 for r in res if r["rewards"][r["me"]] > r["rewards"][1 - r["me"]])
    ties = sum(1 for r in res if r["rewards"][r["me"]] == r["rewards"][1 - r["me"]])
    mine = [r["rewards"][r["me"]] for r in res]
    opp = [r["rewards"][1 - r["me"]] for r in res]
    marg = [m - o for m, o in zip(mine, opp)]
    se = statistics.pstdev(marg) / max(1, len(marg)) ** 0.5
    errs = [r["errors"] for r in res if r["errors"]]
    print(f"{a.tag or os.path.basename(os.path.dirname(a.cand))} {ov}: n={len(res)} W {wins} T {ties} "
          f"me {statistics.mean(mine):.0f} opp {statistics.mean(opp):.0f} margin {statistics.mean(marg):+.0f} (se {se:.0f}) "
          f"[{time.time() - t0:.0f}s] errs {len(errs)}")
    items = collections.defaultdict(lambda: [0, 0.0, 0, 0.0])
    spend = collections.Counter()
    for r in res:
        me = r["sides"][r["me"]]
        op = r["sides"][1 - r["me"]]
        for k, (u, v) in me["sales"].items():
            items[k][0] += u
            items[k][1] += v
        for k, (u, v) in op["sales"].items():
            items[k][2] += u
            items[k][3] += v
        for k, v in me["spend"].items():
            spend[k] += v
    n = len(res)
    print("   item        me_units  me_rev  | opp_units opp_rev")
    for k in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]:
        u, v, ou, ov_ = items[k]
        print(f"   {k:11s} {u / n:7.0f} {v / n:8.0f}  | {ou / n:7.0f} {ov_ / n:8.0f}")
    print("   spend: " + " ".join(f"{k}={v / n:.0f}" for k, v in sorted(spend.items(), key=lambda kv: -kv[1])))
    if errs:
        print("   errors:", errs[:2])
    if a.out:
        with open(a.out, "a", encoding="utf-8") as f:
            f.write(json.dumps({"tag": a.tag, "ov": ov, "res": res}) + "\n")


if __name__ == "__main__":
    main()
