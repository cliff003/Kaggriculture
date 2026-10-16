r"""Where does an oracle executor lose money against the tape (same plan, same land days, same hires)?
Revenue by item and period, spend, and units lost, summed over seeds (team 42 research, 9/28).

    .venv/bin/python prod/oracle/gap.py CAND_MAIN.py --ref prod/oracle/ref_9000.json --seeds 9000,9001,... [--set JSON]
"""
import argparse
import collections
import json
import multiprocessing as mp
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ITEMS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
PERIODS = [("d0-10", 0, 264), ("d11-20", 264, 504), ("d21-28", 504, 696), ("d29", 696, 720)]


def period(step):
    for name, a, b in PERIODS:
        if a <= step < b:
            return name
    return "d29"


def job(args):
    path, rec, ov = args
    sys.path.insert(0, os.path.join(ROOT, "prod", "tools"))
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import acct
    import fastarena
    import forceshops
    forceshops.force(rec["shops"])
    fa = fastarena.load_agent(path)
    if ov is not None and "STATE" in fa.__globals__:
        fa.__globals__["STATE"]["_override"] = ov
    acct._CUR["log"] = []
    acct._CUR["farms"] = None
    r = fastarena.run_game(fa, fastarena.load_agent("pass"), rec["seed"])
    out = collections.defaultdict(float)
    for step, pl, op, item, price in acct._CUR["log"]:
        if pl != 0:
            continue
        if op == "SELL":
            out[f"rev|{item}|{period(step)}"] += price
            out[f"units|{item}|{period(step)}"] += 1
        elif op == "LOST":
            out[f"lost|{item}"] += price
        else:
            out[f"spend|{op}{':' + item if op not in ('HIRE', 'LAND') else ''}"] += price
    out["money"] = r["rewards"][0]
    return dict(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("--ref", default="prod/oracle/ref_9000.json")
    ap.add_argument("--seeds", default="")
    ap.add_argument("--tape", default="research/panel/cha22/main.py")
    ap.add_argument("--set", default="{}")
    ap.add_argument("-j", type=int, default=9)
    a = ap.parse_args()
    refs = json.load(open(os.path.join(ROOT, a.ref)))
    seeds = [s for s in a.seeds.split(",") if s] or list(refs)
    extra = json.loads(a.set)
    jobs = []
    for s in seeds:
        rec = refs[s]
        ov = {"land_days": [rec["land"].get("NE", 99), rec["land"].get("SW", 99), rec["land"].get("SE", 99)], "land_last": 29,
              "oracle": rec["events"], "oracle_hires": rec["hires"]}
        ov.update(extra)
        jobs.append((os.path.join(ROOT, a.tape), rec, None))
        jobs.append((os.path.join(ROOT, a.cand), rec, ov))
    with mp.get_context("spawn").Pool(a.j) as pool:
        res = pool.map(job, jobs)
    tape = collections.defaultdict(float)
    cand = collections.defaultdict(float)
    for i, r in enumerate(res):
        tgt = tape if i % 2 == 0 else cand
        for k, v in r.items():
            tgt[k] += v / len(seeds)
    print(f"seeds {len(seeds)}: tape money {tape['money']:.0f}  cand money {cand['money']:.0f}  gap {cand['money'] - tape['money']:+.0f}")
    print("revenue per game (k), tape/cand and units, by period:")
    for it in ITEMS:
        cells = []
        gap = 0.0
        for p, _, _ in PERIODS:
            t, c = tape[f"rev|{it}|{p}"], cand[f"rev|{it}|{p}"]
            gap += c - t
            cells.append(f"{t / 1000:5.1f}/{c / 1000:5.1f} ({tape[f'units|{it}|{p}']:.0f}/{cand[f'units|{it}|{p}']:.0f})")
        print(f"  {it:10s} gap {gap / 1000:+6.1f}k | " + "  ".join(cells))
    keys = sorted({k for k in list(tape) + list(cand) if k.startswith(("spend|", "lost|"))})
    print("spend and lost per game, tape / cand:")
    for k in keys:
        print(f"  {k:28s} {tape[k]:8.0f} {cand[k]:8.0f}  diff {cand[k] - tape[k]:+8.0f}")


if __name__ == "__main__":
    main()
