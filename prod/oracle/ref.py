r"""Record the cha22 tape's plan in solo games (cha22 in seat 0 vs the built-in "pass" agent), for the oracle
execution test (team 42 research, 9/28).

    .venv/bin/python prod/oracle/ref.py --seeds 9000-9019 --out prod/oracle/ref_9000.json [-j 9] [--agent PATH]

Per seed it stores: final money, money at the start of each day, the final shop list (to force the same world later),
the day each quadrant was bought, hires per day, and the plan as events: for every day d, the tiles that got a new
plant (crop, planted that day) or a new animal (placed that day), read from the next morning's observation.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_seeds(s):
    out = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def job(args):
    seed, agent_path = args
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import fastarena
    import forceshops
    forceshops.force(None)
    inner = fastarena.load_agent(agent_path)
    rec = {"seed": seed, "events": {}, "money": [], "hires": [], "land": {}, "shops": []}
    last = {"tiles": None}

    def spy(obs, conf=None):
        step = int(obs["step"])
        day, hour = divmod(step, 24)
        farm = obs["farms"][int(obs["player"])]
        if hour == 0:
            rec["money"].append(float(farm["money"]))
            if day > 0:
                ev = []
                for y, row in enumerate(farm["tiles"]):
                    for x, t in enumerate(row):
                        if not isinstance(t, dict):
                            continue
                        if t.get("kind") == "PLANT" or t.get("crop"):
                            if int(t.get("planted_day", -1)) == day - 1:
                                ev.append([x, y, t["crop"]])
                        elif t.get("animal") and int(t.get("placed_day", -1)) == day - 1:
                            ev.append([x, y, t["animal"]])
                rec["events"][str(day - 1)] = ev
        if hour == 23:
            rec["hires"].append(int(farm.get("hires_today", 0)))
        for q in farm["unlocked_quadrants"]:
            rec["land"].setdefault(q, day)
        rec["shops"] = list(obs["town"]["unlocked_shops"])
        return fastarena._call(inner, obs, conf)

    res = fastarena.run_game(spy, fastarena.load_agent("pass"), seed)
    rec["final"] = res["rewards"][0]
    rec["status"] = res["status"]
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="9000-9019")
    ap.add_argument("--out", required=True)
    ap.add_argument("--agent", default="research/panel/cha22/main.py")
    ap.add_argument("-j", type=int, default=9)
    a = ap.parse_args()
    seeds = parse_seeds(a.seeds)
    agent = os.path.join(ROOT, a.agent) if not os.path.isabs(a.agent) else a.agent
    with mp.get_context("spawn").Pool(min(a.j, len(seeds))) as pool:
        recs = pool.map(job, [(s, agent) for s in seeds])
    json.dump({str(r["seed"]): r for r in recs}, open(a.out, "w"))
    fin = [r["final"] for r in recs]
    print(f"wrote {a.out}: {len(recs)} seeds, mean final money {sum(fin) / len(fin):.0f}, "
          f"min {min(fin):.0f} max {max(fin):.0f}")


if __name__ == "__main__":
    main()
