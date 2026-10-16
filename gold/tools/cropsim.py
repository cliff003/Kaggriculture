r"""Unit test of the gold agent's per-tile job rules against the real engine.

One unit stands on one tile and runs the first op of that tile's job every step (one op per step),
with unlimited wheat and fertilizer in hand. Engine functions do the rest: unit actions, decay every
step, plant and animal refresh at hour 23. Prints units harvested per cycle, ops used and deaths.

.venv\Scripts\python.exe gold\tools\cropsim.py [--days 30]
"""
import argparse
import collections
import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import fastarena  # noqa: E402,F401  (imports kaggle_environments quietly, kaggriculture only)
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa: E402


def load_agent_module(path=os.path.join(ROOT, "gold", "agent", "main.py")):
    spec = importlib.util.spec_from_file_location("gold_agent", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run(G, subject, days, fert_ok, xy=(1, 1), replant=True):
    farm = K._new_farm(10, 3000)
    private = K._new_private()
    farm["farmer"] = list(xy)
    tiles = farm["tiles"]
    if subject in G.ANIMALS:
        tiles[xy[1]][xy[0]] = K._new_animal(subject, 0)
    harvested = []          # (day, units)
    ops_used = collections.Counter()
    deaths = 0
    escapes = 0
    last_kind = None
    for t in range(days * 24):
        day, hour = t // 24, t % 24
        pol = G.Policy(day)
        pol.fert_ok = fert_ok
        pol.prices = dict(G.BASE)
        pol.targets = {xy: subject} if (replant or t == 0) else {}
        if subject in G.CROPS and day > G.plant_deadline(subject) and subject != "MELON":
            pol.targets = {}
        if subject == "MELON" and day > 0:
            pol.targets = {}
        private["seeds"][subject if subject in G.CROPS else "WHEAT"] = 5
        inv = private["inventories"][0]
        inv["WHEAT"] = 50
        inv["FERTILIZER"] = 50
        s = G.S()
        s.tiles = tiles
        s.day, s.hour, s.step = day, hour, t
        job = G.tile_job(s, xy, pol, hour, fert_in_hand=inv["FERTILIZER"])
        action = ["PASS"]
        if job is not None and job.ops:
            op, arg, _ = job.ops[0]
            action = [op] if arg is None else [op, arg]
            if op == "PLACE":
                inv[arg] = 1
            ops_used[op] += 1
        tile_before = tiles[xy[1]][xy[0]]
        before = dict(inv)
        K._apply_unit_action(farm, private, 0, action, 10, day, 24)
        if action[0] == "HARVEST":
            gained = sum(v - before.get(k, 0) for k, v in inv.items() if k not in ("WHEAT", "FERTILIZER"))
            gained += max(0, inv.get("WHEAT", 0) - before.get("WHEAT", 0))
            harvested.append((day, gained))
        K._decay_plants(farm, t)
        if hour == 23:
            kind_before = tiles[xy[1]][xy[0]]
            had_animal = isinstance(kind_before, dict) and kind_before.get("animal")
            was_plant = isinstance(kind_before, dict) and kind_before.get("kind") == "PLANT"
            K._daily_refresh_plants(farm, day, 24)
            K._daily_refresh_animals(farm, day)
            after = tiles[xy[1]][xy[0]]
            if was_plant and isinstance(after, dict) and after.get("kind") == "WEED":
                deaths += 1
            if had_animal and not (isinstance(after, dict) and after.get("animal")):
                escapes += 1
        del tile_before, last_kind
        last_kind = None
    return harvested, ops_used, deaths, escapes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    a = ap.parse_args()
    G = load_agent_module()
    rows = []
    for subject in ("WHEAT", "CARROT", "MELON", "TOMATO", "STRAWBERRY", "GOOSE", "COW", "SHEEP"):
        for fert in (False, True):
            if subject in G.ANIMALS and fert:
                continue
            h, ops, deaths, esc = run(G, subject, a.days, fert)
            total = sum(u for _, u in h)
            work = sum(ops.values())
            rows.append((subject, "fert" if fert else "-", total, len(h), work, deaths, esc,
                         " ".join(f"d{d}:{u}" for d, u in h[:12]),
                         " ".join(f"{k[:5]}{v}" for k, v in sorted(ops.items()))))
    for r in rows:
        print(f"{r[0]:<10} {r[1]:<4} units={r[2]:<4} harvests={r[3]:<3} ops={r[4]:<4} deaths={r[5]} escapes={r[6]}")
        print(f"    harvests: {r[7]}")
        print(f"    ops: {r[8]}")


if __name__ == "__main__":
    main()
