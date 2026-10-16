r"""Oracle execution test (team 42 research, 9/28): a candidate executes the tape's recorded plan (prod/oracle/ref.py)
solo vs "pass" in the same worlds (shops forced to the tape's), and its money is compared with the tape's own.

    .venv/bin/python prod/oracle/bench_oracle.py CAND_MAIN.py --ref prod/oracle/ref_9000.json [--own] [--set JSON] [-j 9]

--own runs the candidate's own plan instead (no oracle events; still the tape's land days unless --set overrides).
Prints per-seed money, the mean ratio to the tape, and execution telemetry (crop deaths, animal escapes, units carried
at night, stops left at 23:00 when the candidate exposes them with debug=True).
"""
import argparse
import json
import multiprocessing as mp
import os
import statistics as st
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def job(args):
    cand, rec, own, extra, hires, opp = args
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import fastarena
    import forceshops
    forceshops.force(rec["shops"])
    fa = fastarena.load_agent(cand)
    ov = {"land_days": [rec["land"].get("NE", 99), rec["land"].get("SW", 99), rec["land"].get("SE", 99)], "land_last": 29,
          "debug": True}
    if not own:
        ov["oracle"] = rec["events"]
        if hires:
            ov["oracle_hires"] = rec["hires"]
    ov.update(extra)
    g = fa.__globals__
    if "STATE" in g:
        g["STATE"]["_override"] = ov
    fb = fastarena.load_agent(opp if opp == "pass" else os.path.join(ROOT, opp))
    res = fastarena.run_game(fa, fb, rec["seed"])
    S = (g.get("STATE") or {}).get(0) or {}
    left = S.get("left") or []
    farm = res["final_state"][0].observation.farms[0]
    return {"seed": rec["seed"], "money": res["rewards"][0], "ref": rec["final"], "status": res["status"],
            "opp_money": res["rewards"][1],
            "errors": len(S.get("errors", [])), "tb": (S.get("tb") or "")[-400:],
            "left_urgent": sum(1 for d in left for it in d["items"] if it[2] == "crop" and it[4] >= 1200),
            "left_all": sum(d["n"] for d in left),
            "weeds_end": sum(1 for row in farm["tiles"] for t in row if isinstance(t, dict) and t.get("kind") == "WEED")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("--ref", default="prod/oracle/ref_9000.json")
    ap.add_argument("--own", action="store_true")
    ap.add_argument("--no-hires", action="store_true")
    ap.add_argument("--opp", default="pass")
    ap.add_argument("--set", default="{}")
    ap.add_argument("-j", type=int, default=9)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    refs = json.load(open(os.path.join(ROOT, a.ref) if not os.path.isabs(a.ref) else a.ref))
    cand = os.path.join(ROOT, a.cand) if not os.path.isabs(a.cand) else a.cand
    extra = json.loads(a.set)
    with mp.get_context("spawn").Pool(min(a.j, len(refs))) as pool:
        res = pool.map(job, [(cand, r, a.own, extra, not a.no_hires, a.opp) for r in refs.values()])
    res.sort(key=lambda r: r["seed"])
    for r in res:
        print(f"  {r['seed']} money {r['money']:9.0f} ref {r['ref']:9.0f} ratio {r['money'] / r['ref']:.3f}"
              f" left-urgent {r['left_urgent']:3d} left {r['left_all']:3d} weeds {r['weeds_end']:2d} errs {r['errors']}")
    m = st.mean(r["money"] for r in res)
    rf = st.mean(r["ref"] for r in res)
    print(f"{a.tag or os.path.basename(os.path.dirname(cand))} {'own' if a.own else 'oracle'}{'' if a.no_hires else '+hires'} {extra}: seeds {len(res)} "
          f"money {m:.0f} ref {rf:.0f} ratio {m / rf:.3f} left-urgent/game {st.mean(r['left_urgent'] for r in res):.1f} "
          f"errs {sum(r['errors'] for r in res)}")
    if a.opp != "pass":
        mg = [r["money"] - r["opp_money"] for r in res]
        print(f"   vs {a.opp}: margin {st.mean(mg):+.0f}  wins {sum(x > 0 for x in mg)}/{len(mg)}  opp money {st.mean(r['opp_money'] for r in res):.0f}")
    bad = [r for r in res if r["errors"]]
    if bad:
        print("first traceback:", bad[0]["tb"])


if __name__ == "__main__":
    main()
