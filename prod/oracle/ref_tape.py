r"""Extract a recorded team's daily plan from live tapes (team 42 research, 9/29): re-simulate each game from both
sides' recorded actions and read, for the chosen team, the tiles planted / animals placed each day, the land days,
hires per day and final money. Same plan schema as prod/oracle/ref.py, plus the seat and the opponent's name.

    .venv/bin/python prod/oracle/ref_tape.py TAPES.jsonl.gz --team unreal --out prod/oracle/ref_unreal.json
"""
import argparse
import gzip
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def extract(rec, team):
    import forceshops
    from kaggle_environments import make
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    seat = rec["teams"].index(team)
    forceshops.force(rec["shops"])
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": rec["seed"]}, debug=False)
    env.reset(2)
    st = env.state
    n = len(rec["acts"][0])
    out = {"seed": rec["seed"], "id": rec["id"], "seat": seat, "opp": rec["teams"][1 - seat], "shops": rec["shops"],
           "events": {}, "money": [], "hires": [], "land": {}}
    for t in range(719):
        o = st[0].observation
        day, hour = divmod(t, 24)
        farm = o.farms[seat]
        if hour == 0:
            out["money"].append(float(farm["money"]))
            if day > 0:
                ev = []
                for y, row in enumerate(farm["tiles"]):
                    for x, tl in enumerate(row):
                        if isinstance(tl, dict) and tl.get("crop") and int(tl.get("planted_day", -1)) == day - 1:
                            ev.append([x, y, tl["crop"]])
                        elif isinstance(tl, dict) and tl.get("animal") and int(tl.get("placed_day", -1)) == day - 1:
                            ev.append([x, y, tl["animal"]])
                out["events"][str(day - 1)] = ev
        for q in farm["unlocked_quadrants"]:
            out["land"].setdefault(q, day)
        if hour == 23:
            out["hires"].append(int(farm.get("hires_today", 0)))
        for i in range(2):
            a = rec["acts"][i][t + 1] if t + 1 < n else None
            st[i].action = a if isinstance(a, dict) else None
        K.interpreter(st, env)
        st[0].observation.step = t + 1
    out["final"] = float(st[0].observation.farms[seat]["money"])
    out["opp_final"] = float(st[0].observation.farms[1 - seat]["money"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tapes")
    ap.add_argument("--team", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = {}
    for line in gzip.open(a.tapes, "rt", encoding="utf-8"):
        rec = json.loads(line)
        if a.team not in rec["teams"] or len(rec["shops"]) != 8 or rec["teams"][0] == rec["teams"][1]:
            continue
        r = extract(rec, a.team)
        res[str(rec["id"])] = r
    json.dump(res, open(a.out, "w"))
    fin = [r["final"] for r in res.values()]
    mg = [r["final"] - r["opp_final"] for r in res.values()]
    print(f"wrote {a.out}: {len(res)} games, {a.team} mean money {sum(fin) / len(fin):.0f}, mean margin {sum(mg) / len(mg):+.0f}")


if __name__ == "__main__":
    main()
