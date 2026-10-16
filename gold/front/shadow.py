r"""Shadow diff: replay a harvested live game exactly (both recorded tapes, record seed, forced shops) and, at every
step, feed the watched team's observation to a fresh copy of a reference agent (default: cha22 original). Records
where the team's recorded action differs from the reference's.

    .venv\Scripts\python.exe gold\front\shadow.py REC.jsonl.gz [...] --team NAME [--ref research/panel/cha22/main.py]
        [--max 4] [--out OUT.json]

Per game: unit-action agreement by day (share of units whose action equals the reference's), first step where
the unit actions diverge, and every market-list difference (step, reference list, team list).
"""
import argparse
import copy
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def norm_market(m):
    out = []
    for o in (m or []):
        if isinstance(o, (list, tuple)) and o:
            out.append(tuple(str(x) for x in o))
    return out


def units(a):
    a = a or {}
    return [tuple(a.get("farmer") or ["PASS"])] + [tuple(h) if isinstance(h, list) else ("?",) for h in (a.get("hands") or [])]


def run(rec, team, ref_path):
    import fastarena
    import forceshops
    forceshops.force(rec["shops"])
    me = rec["teams"].index(team)
    tapes = [[rec["acts"][s][t + 1] if t + 1 < len(rec["acts"][s]) else None for t in range(719)] for s in range(2)]
    ref = fastarena.load_agent(ref_path)
    log = {"unit_same": {}, "unit_n": {}, "first_unit_div": None, "market": []}
    PASS = {"farmer": ["PASS"], "hands": [], "market": []}

    def tape_agent(seat):
        def f(obs, conf=None):
            t = int(obs["step"])
            a = tapes[seat][t] if 0 <= t < 719 else None
            a = json.loads(json.dumps(a)) if isinstance(a, dict) else dict(PASS)
            if seat == me:
                try:
                    r = ref(copy.deepcopy(obs), conf)
                except Exception as e:
                    r = {"farmer": ["ERR"], "hands": [], "market": [["ERR", str(e)[:40]]]}
                d = t // 24
                ua, ur = units(a), units(r)
                same = sum(1 for x, y in zip(ua, ur) if x == y)
                log["unit_same"][d] = log["unit_same"].get(d, 0) + same
                log["unit_n"][d] = log["unit_n"].get(d, 0) + max(len(ua), len(ur))
                if log["first_unit_div"] is None and ua != ur:
                    log["first_unit_div"] = [t, [list(x) for x in ur], [list(x) for x in ua]]
                ma, mr = norm_market(a.get("market")), norm_market(r.get("market"))
                if ma != mr:
                    log["market"].append([t, [list(x) for x in mr], [list(x) for x in ma]])
            return a
        return f

    r = fastarena.run_game(tape_agent(0), tape_agent(1), rec["seed"])
    return {"id": rec["id"], "team": team, "opp": rec["teams"][1 - me], "seat": me, "server": rec["rewards"],
            "local": r["rewards"], "log": log}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recs", nargs="+")
    ap.add_argument("--team", required=True)
    ap.add_argument("--ref", default=os.path.join(ROOT, "research", "panel", "cha22", "main.py"))
    ap.add_argument("--max", type=int, default=4)
    ap.add_argument("--out")
    a = ap.parse_args()
    out = []
    for p in a.recs:
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                if a.team not in rec["teams"] or len(out) >= a.max:
                    continue
                g = run(rec, a.team, a.ref)
                lg = g["log"]
                days = sorted(lg["unit_n"], key=int)
                agree = " ".join(f"{d}:{lg['unit_same'][d] / max(1, lg['unit_n'][d]):.2f}" for d in days[::3])
                print(f"{g['id']} vs {g['opp'][:16]:16s} server {g['server']} local {g['local']} "
                      f"market diffs {len(lg['market'])} first unit div {lg['first_unit_div'][0] if lg['first_unit_div'] else None}",
                      flush=True)
                print("   unit agreement by day:", agree, flush=True)
                out.append(g)
    if a.out:
        json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    main()
