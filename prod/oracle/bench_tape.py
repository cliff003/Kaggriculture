r"""Can our executor capture a top team's edge by following its own daily plan? (team 42 research, 9/29)

    .venv/bin/python prod/oracle/bench_tape.py CAND_MAIN.py --ref prod/oracle/ref_unreal.json \
        --tapes research/carrera/tapes/unreal_56618268.jsonl.gz [--opp tape|PATH] [--set JSON] [-j 9]

For every game of the plan file, the candidate sits in the recorded team's seat and follows that team's plan in that game
(oracle events + hires + land days, backlog 3 days); the opponent replays its recorded actions (--opp tape) or is a live
agent. Shops are forced to the game's. Reports our money / margin next to the recorded team's own.
"""
import argparse
import gzip
import json
import multiprocessing as mp
import os
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def job(args):
    cand, plan, acts_opp, opp, extra, acts_me, sell_tape = args
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import fastarena
    import forceshops
    from cfreplay import tape_agent
    forceshops.force(plan["shops"])
    fa = fastarena.load_agent(cand)
    ov = {"oracle": plan["events"], "oracle_hires": plan["hires"], "oracle_backlog": 3, "land_last": 29,
          "land_days": [plan["land"].get("NE", 99), plan["land"].get("SW", 99), plan["land"].get("SE", 99)]}
    ov.update(extra)
    if "STATE" in fa.__globals__:
        fa.__globals__["STATE"]["_override"] = ov
    fb = tape_agent(acts_opp) if opp == "tape" else fastarena.load_agent(os.path.join(ROOT, opp))
    seat = plan["seat"] if opp == "tape" else 0
    me = fa
    if sell_tape:
        # selling test: our orders minus our SELLs, with the recorded team's SELL orders of that step in front
        def me(obs, conf=None, _fa=fa):
            act = fastarena._call(_fa, obs, conf)
            t = int(obs["step"])
            rec = acts_me[t + 1] if t + 1 < len(acts_me) and isinstance(acts_me[t + 1], dict) else {}
            sells = [list(o) for o in (rec.get("market") or []) if o and o[0] == "SELL"]
            mine = [o for o in (act.get("market") or []) if o and o[0] != "SELL"]
            out = dict(act)
            out["market"] = (sells + mine)[:10]
            return out
    fns = [fb, fb]
    fns[seat] = me
    res = fastarena.run_game(fns[0], fns[1], plan["seed"])
    S = (fa.__globals__.get("STATE") or {}).get(seat) or {}
    return {"id": plan["id"], "money": res["rewards"][seat], "opp_money": res["rewards"][1 - seat],
            "ref": plan["final"], "ref_opp": plan["opp_final"], "errors": len(S.get("errors", [])), "tb": (S.get("tb") or "")[-300:]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("--ref", default="prod/oracle/ref_unreal.json")
    ap.add_argument("--tapes", default="research/carrera/tapes/unreal_56618268.jsonl.gz")
    ap.add_argument("--opp", default="tape")
    ap.add_argument("--set", default="{}")
    ap.add_argument("-j", type=int, default=9)
    ap.add_argument("--tag", default="")
    ap.add_argument("--sell-tape", action="store_true")
    a = ap.parse_args()
    plans = json.load(open(os.path.join(ROOT, a.ref)))
    recs = {}
    for line in gzip.open(os.path.join(ROOT, a.tapes), "rt", encoding="utf-8"):
        r = json.loads(line)
        if str(r["id"]) in plans:
            recs[str(r["id"])] = r
    extra = json.loads(a.set)
    cand = os.path.join(ROOT, a.cand) if not os.path.isabs(a.cand) else a.cand
    jobs = [(cand, p, recs[k]["acts"][1 - p["seat"]], a.opp, extra, recs[k]["acts"][p["seat"]], a.sell_tape)
            for k, p in plans.items() if k in recs]
    with mp.get_context("spawn").Pool(a.j) as pool:
        res = pool.map(job, jobs)
    mg = [r["money"] - r["opp_money"] for r in res]
    rmg = [r["ref"] - r["ref_opp"] for r in res]
    print(f"{a.tag or os.path.basename(os.path.dirname(cand))} vs {a.opp} {extra}{' +recorded SELLs' if a.sell_tape else ''}: games {len(res)}")
    print(f"  ours:      money {st.mean(r['money'] for r in res):8.0f}  margin {st.mean(mg):+8.0f}  wins {sum(x > 0 for x in mg)}  opp money {st.mean(r['opp_money'] for r in res):.0f}")
    print(f"  recorded:  money {st.mean(r['ref'] for r in res):8.0f}  margin {st.mean(rmg):+8.0f}  wins {sum(x > 0 for x in rmg)}  (the team's own live result)")
    print(f"  errors {sum(r['errors'] for r in res)}")
    bad = [r for r in res if r["errors"]]
    if bad:
        print("  first traceback:", bad[0]["tb"])


if __name__ == "__main__":
    main()
