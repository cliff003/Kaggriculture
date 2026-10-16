r"""Quick debug game: our agent (exceptions raised, GOLD_DEBUG=1) against an opponent, one seed.

.venv\Scripts\python.exe gold\tools\quick.py [OURS] [OPP] [SEED] [--seat 0|1] [--days D]
Prints rewards, timing and a per-day line for our side (money, units, tiles, shed).
"""
import argparse
import collections
import os
import sys
import time

os.environ["GOLD_DEBUG"] = "1"
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import fastarena  # noqa: E402
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa: E402


def summarize(farm, priv):
    c = collections.Counter()
    for row in farm["tiles"]:
        for t in row:
            if t is None:
                c["."] += 1
            elif t == "LOCKED":
                continue
            elif t.get("kind") == "PLANT":
                c[t["crop"][:2].lower()] += 1
            elif t.get("animal"):
                c[t["animal"][:3]] += 1
            else:
                c["e" + t.get("kind", "?")[:2].lower()] += 1
    return " ".join(f"{k}{v}" for k, v in sorted(c.items())), sum(priv["shed"].values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ours", nargs="?", default="gold/agent/main.py")
    ap.add_argument("opp", nargs="?", default="research/panel/cha22/main.py")
    ap.add_argument("seed", nargs="?", type=int, default=50000)
    ap.add_argument("--seat", type=int, default=0)
    ap.add_argument("--routes", type=int, default=-1, help="print each unit's ops on this day")
    ap.add_argument("--world", type=int, default=-1, help="force the shops of real game K (gstat --worlds uses K = seed - seed0)")
    a = ap.parse_args()
    if a.world >= 0:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import gstat
        import forceshops
        forceshops.force(gstat.load_worlds()[a.world])
    fo, fp = fastarena.load_agent(a.ours), fastarena.load_agent(a.opp)
    fa, fb = (fo, fp) if a.seat == 0 else (fp, fo)
    me = a.seat
    days = []
    orig = K._end_of_day

    def eod(state, env, day):
        farm = state[0].observation.farms[me]
        priv = state[me].observation.private
        tiles, shed = summarize(farm, priv)
        days.append((day, farm["money"], state[0].observation.farms[1 - me]["money"], len(farm["hands"]),
                     "".join(q[0] + q[1].lower() for q in farm["unlocked_quadrants"]), tiles, shed))
        return orig(state, env, day)

    K._end_of_day = eod
    stats = collections.defaultdict(collections.Counter)
    routes_log = collections.defaultdict(list)
    orig_unit = K._apply_unit_action
    cur = {}

    def unit(farm, private, idx, action, *args, **kw):
        if farm is cur.get("farm"):
            d = cur["step"] // 24
            op = action[0] if isinstance(action, list) and action else "NONE"
            pos = K._farmer_position(farm, idx)
            before = None
            if pos is not None:
                t = farm["tiles"][pos[1]][pos[0]]
                before = repr(t)
            inv_b = dict(private["inventories"][idx]) if idx < len(private["inventories"]) else {}
            shed_b = dict(private["shed"])
            orig_unit(farm, private, idx, action, *args, **kw)
            after = repr(farm["tiles"][pos[1]][pos[0]]) if pos is not None else None
            inv_a = dict(private["inventories"][idx]) if idx < len(private["inventories"]) else {}
            if d == a.routes:
                eff = before != after or inv_b != inv_a or shed_b != private["shed"]
                routes_log[idx].append((cur["step"] % 24, tuple(pos) if pos else None, op, eff))
            if op in ("NORTH", "SOUTH", "EAST", "WEST"):
                stats[d]["move"] += 1
            elif op == "PASS":
                stats[d]["pass"] += 1
            elif before != after or inv_b != inv_a or shed_b != private["shed"]:
                stats[d]["eff"] += 1
                stats[d]["e_" + op] += 1
            else:
                stats[d]["noop"] += 1
                stats[d]["n_" + op] += 1
            return
        return orig_unit(farm, private, idx, action, *args, **kw)

    K._apply_unit_action = unit
    orig_plants, orig_animals = K._daily_refresh_plants, K._daily_refresh_animals

    LASTP = {"TOMATO": 10, "STRAWBERRY": 15}

    def plants(farm, day, tpd):
        if farm is cur.get("farm"):
            before = {}
            for y, row in enumerate(farm["tiles"]):
                for x, t in enumerate(row):
                    if isinstance(t, dict) and t.get("kind") == "PLANT":
                        before[(x, y)] = (t["crop"], day - t["planted_day"], t["watered_today"], t["consecutive_unwatered"], t["yield_units"])
            orig_plants(farm, day, tpd)
            for (x, y), (crop, age, w, cu, yl) in before.items():
                t = farm["tiles"][y][x]
                if isinstance(t, dict) and t.get("kind") == "WEED":
                    if crop in LASTP and age > LASTP[crop]:
                        stats[day]["fin"] += 1
                    else:
                        stats[day]["dead"] += 1
                        stats[day]["d_" + crop[:3] + str(age)] += 1
            return
        return orig_plants(farm, day, tpd)

    def animals(farm, day):
        if farm is cur.get("farm"):
            before = sum(1 for row in farm["tiles"] for t in row if isinstance(t, dict) and t.get("animal"))
            orig_animals(farm, day)
            after_a = sum(1 for row in farm["tiles"] for t in row if isinstance(t, dict) and t.get("animal"))
            stats[day]["esc"] += before - after_a
            return
        return orig_animals(farm, day)

    K._daily_refresh_plants, K._daily_refresh_animals = plants, animals
    orig_interp = K.interpreter

    def interp(state, env):
        cur["farm"] = state[0].observation.farms[me]
        cur["step"] = state[0].observation.step
        return orig_interp(state, env)

    K.interpreter = interp
    t0 = time.time()
    r = fastarena.run_game(fa, fb, a.seed, quiet=False)
    print("rewards", r["rewards"], "status", r["status"], "t_mean_ms", [round(x * 1000, 2) for x in r["t_mean"]],
          "t_max_ms", [round(x * 1000, 1) for x in r["t_max"]], "wall", round(time.time() - t0, 1))
    AB = {"WATER": "W", "HARVEST": "H", "PLANT": "P", "FERTILIZE": "F", "FEED": "f", "CARE": "c",
          "COLLECT_FERTILIZER": "k", "PICKUP": "U", "PLACE": "L", "DROP": "D", "DIG": "G", "PASS": ".",
          "BUILD_COOP": "B", "BUILD_PASTURE": "B"}
    for u in sorted(routes_log):
        seq, last, moves, ops, visits = [], None, 0, 0, 0
        for h, p, op, eff in routes_log[u]:
            if op in ("NORTH", "SOUTH", "EAST", "WEST"):
                moves += 1
                continue
            if p != last:
                seq.append(f"({p[0]},{p[1]})@{h}:")
                last = p
                visits += 1
            seq.append(AB.get(op, op[:2]) + ("" if eff else "!"))
            ops += 1
        print(f"u{u:2d} moves {moves:2d} ops {ops:2d} visits {visits:2d} | " + "".join(seq))
    for d in days:
        st = stats[d[0]]
        tot = st["move"] + st["pass"] + st["eff"] + st["noop"]
        print(f"d{d[0]:2d} ${d[1]:8.0f} opp ${d[2]:8.0f} hands {d[3]:2d} {d[4]:8s} shed {d[6]:3d} | {d[5]}")
        print(f"      turns {tot} move {st['move']} pass {st['pass']} eff {st['eff']} noop {st['noop']} dead {st['dead']} fin {st['fin']} esc {st['esc']} "
              + " ".join(f"{k[2:]}x{v}" for k, v in sorted(st.items()) if k.startswith("d_")) + " | "
              + " ".join(f"{k[2:6]}{v}" for k, v in sorted(st.items()) if k.startswith("e_"))
              + " || " + " ".join(f"{k}{v}" for k, v in sorted(st.items()) if k.startswith("n_")))


if __name__ == "__main__":
    main()
