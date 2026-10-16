r"""Per-day diagnostics of one local game: money, deaths (weeds from missed watering, escaped animals),
idle and moving unit-turns, hires, shed fill.

.venv\Scripts\python.exe tools\diag.py A_MAIN_PY B_MAIN_PY SEED [--side 0]
"""
import argparse
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fastarena
from kaggle_environments.envs.kaggriculture import kaggriculture as K

import kg

DEATHS = collections.Counter()
_orig_plants, _orig_animals = K._daily_refresh_plants, K._daily_refresh_animals
_CUR = {}


def _pid(farm):
    return 0 if farm is _CUR["farms"][0] else 1


def _plants(farm, day, tpd):
    before = {(x, y) for y, row in enumerate(farm["tiles"]) for x, t in enumerate(row)
              if isinstance(t, dict) and t.get("kind") == "PLANT"}
    _orig_plants(farm, day, tpd)
    for x, y in before:
        t = farm["tiles"][y][x]
        if isinstance(t, dict) and t.get("kind") == "WEED":
            DEATHS[(_pid(farm), day, "plant")] += 1


def _animals(farm, day):
    before = {(x, y) for y, row in enumerate(farm["tiles"]) for x, t in enumerate(row)
              if isinstance(t, dict) and t.get("animal")}
    _orig_animals(farm, day)
    for x, y in before:
        t = farm["tiles"][y][x]
        if not (isinstance(t, dict) and t.get("animal")):
            DEATHS[(_pid(farm), day, "animal")] += 1


K._daily_refresh_plants, K._daily_refresh_animals = _plants, _animals

_orig_interp = K.interpreter


def _interp(state, env):
    _CUR["farms"] = state[0].observation.farms
    return _orig_interp(state, env)


K.interpreter = _interp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("seed", type=int)
    ap.add_argument("--side", type=int, default=0)
    a = ap.parse_args()
    fa, fb = fastarena.load_agent(a.a), fastarena.load_agent(a.b)
    r = fastarena.run_game(fa, fb, a.seed, record=True)
    h = r["history"]
    p = a.side
    print("rewards", r["rewards"], "status", r["status"], "t_mean", [round(x, 4) for x in r["t_mean"]],
          "t_max", [round(x, 3) for x in r["t_max"]])
    rows = []
    for d in range(30):
        acts = [h[t][p]["action"] or {} for t in range(d * 24, min(len(h), d * 24 + 24))]
        units = [[a_.get("farmer") or ["PASS"]] + list(a_.get("hands") or []) for a_ in acts]
        turns = sum(len(u) for u in units)
        idle = sum(1 for u in units for x in u if not x or x[0] == "PASS")
        move = sum(1 for u in units for x in u if x and x[0] in ("NORTH", "SOUTH", "EAST", "WEST"))
        hires = sum(1 for a_ in acts for o in (a_.get("market") or []) if o and o[0] == "HIRE")
        money = h[min(len(h) - 1, d * 24 + 23)][p]["money"]
        rows.append([d, f"{money:.0f}", hires, turns, idle, move, DEATHS[(p, d, "plant")], DEATHS[(p, d, "animal")]])
    kg.table(["天", "钱(当天末)", "雇工", "单位回合", "空闲", "移动", "作物死", "牲口跑"], rows)


if __name__ == "__main__":
    main()
