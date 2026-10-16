r"""Oracle value of extra goods: replay live games with CAND in our seat and drop N units of ITEM into our shed at
hour H of each day in [D0, D1] (engine-level hack, no labor or cost), so our own sell layers sell them. Prints the
margin with and without the gift; the difference is the gross value of the extra production against that rival
(our extra revenue plus the rival's revenue lost to lower prices).

    .venv\Scripts\python.exe gold\front\oracle_add.py CAND.py ITEM N D0 D1 ID [ID ...] [--hour 6] [--workers 8]
"""
import argparse
import json
import multiprocessing as mp
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)


def play(job):
    cand, rec_path, item, n, d0, d1, hour, sched = job[:8]
    costs = job[8] if len(job) > 8 else []
    import fastarena
    import forceshops
    from cfroute import tape_file
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    rec = json.load(open(rec_path, encoding="utf-8"))
    me = rec["teams"].index("42")
    res = []
    for gift in (0, n):
        orig = K._process_market

        def pm(state, env, _gift=gift):
            s = state[0].observation.step
            add = 0
            if _gift and sched:
                add = sum(q for (dd, hh, q) in sched if s == dd * 24 + hh)
            elif _gift and s % 24 == hour and d0 <= s // 24 <= d1:
                add = _gift
            if add:
                shed = state[me].observation.private["shed"]
                room = 100 - sum(shed.values())
                shed[item] = shed.get(item, 0) + max(0, min(add, room))
            if _gift:
                for (dd, hh, money, fert) in costs:
                    if s == dd * 24 + hh:
                        state[0].observation.farms[me]["money"] -= money
                        sh = state[me].observation.private["shed"]
                        sh["FERTILIZER"] = max(0, sh.get("FERTILIZER", 0) - fert)
            return orig(state, env)

        K._process_market = pm
        try:
            forceshops.force(rec["shops"])
            fns = [None, None]
            fns[me] = fastarena.load_agent(cand)
            fns[1 - me] = fastarena.load_agent(tape_file(rec, 1 - me))
            r = fastarena.run_game(fns[0], fns[1], rec["seed"])
        finally:
            K._process_market = orig
        res.append((r["rewards"][me] or 0) - (r["rewards"][1 - me] or 0))
    return rec["id"], rec["teams"][1 - me], rec["shops"], res


def main():
    from tgrun import find_recs
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("item")
    ap.add_argument("n", type=int)
    ap.add_argument("d0", type=int)
    ap.add_argument("d1", type=int)
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--hour", type=int, default=6)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--sched", default="", help="day:hour:qty,... overrides N D0 D1")
    ap.add_argument("--costs", default="", help="day:hour:money:fertilizer,... charged in the gift run")
    a = ap.parse_args()
    sched = [tuple(int(x) for x in part.split(":")) for part in a.sched.split(",") if part]
    costs = [tuple(int(x) for x in part.split(":")) for part in a.costs.split(",") if part]
    recs = find_recs(a.ids)
    tmp = os.path.join(ROOT, "gold", "tmp", "tgrun")
    os.makedirs(tmp, exist_ok=True)
    jobs = []
    for rid, r in recs.items():
        p = os.path.join(tmp, f"{rid}.json")
        json.dump(r, open(p, "w", encoding="utf-8"))
        jobs.append((os.path.abspath(a.cand), p, a.item, a.n, a.d0, a.d1, a.hour, sched, costs))
    with mp.get_context("spawn").Pool(min(a.workers, len(jobs)), maxtasksperchild=1) as pool:
        out = list(pool.imap(play, jobs))
    tot = 0
    flips = 0
    for rid, opp, shops, (m0, m1) in out:
        dem = sum(s in ("BRUNCH_SPOT", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP", "FARMERS_MARKET") for s in shops[:4])
        print(f"{rid} {opp[:20]:20s} straw-shops(first4) {dem}  margin {m0:+8.0f} -> {m1:+8.0f}  value {m1 - m0:+7.0f}")
        tot += m1 - m0
        flips += (m0 <= 0 < m1)
    print(f"mean value {tot / len(out):+.0f}  flips {flips}/{len(out)}")


if __name__ == "__main__":
    main()
