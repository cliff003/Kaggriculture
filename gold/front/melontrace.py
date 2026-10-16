r"""Trace melon logistics of seat 0 in a local game: per step on days 9-11, melon harvests, carried melons, deliveries
to the shed, melon sells, and the ripe melon tiles left.
    .venv\Scripts\python.exe gold\front\melontrace.py AGENT.py OPP.py SEED [--seat 0]"""
import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent")
    ap.add_argument("opp")
    ap.add_argument("seed", type=int)
    ap.add_argument("--seat", type=int, default=0)
    ap.add_argument("--from_step", type=int, default=216)
    ap.add_argument("--to_step", type=int, default=270)
    a = ap.parse_args()
    import fastarena
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    CNT = {"u": 0}
    LOG = collections.defaultdict(list)
    ST = {}
    orig_pm, orig_apply, orig_cu = K._process_market, K._apply_unit_action, K._commit_unit

    def pm(state, env):
        s = state[0].observation.step
        CNT["u"] = 0
        ST["step"] = s
        farm = state[0].observation.farms[a.seat]
        priv = state[a.seat].observation.private
        if a.from_step <= s <= a.to_step:
            ripe = 0
            planted = 0
            for row in farm["tiles"]:
                for t in row:
                    if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                        planted += 1
                        age = s // 24 - t["planted_day"]
                        if age >= 10 and t.get("yield_units", 0) > 0:
                            ripe += 1
            carried = sum(inv.get("MELON", 0) for inv in priv["inventories"])
            LOG[s].append(f"shed {priv['shed'].get('MELON', 0)} carried {carried} tiles {planted} ripe {ripe}")
        return orig_pm(state, env)

    def apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=100):
        if idx == 0:
            CNT["u"] += 1
        seat = CNT["u"] - 1
        s = ST.get("step", -1) + 1
        if seat == a.seat and a.from_step <= s <= a.to_step and isinstance(action, list) and action:
            pos = farm["farmer"] if idx == 0 else (farm["hands"][idx - 1] if idx - 1 < len(farm["hands"]) else None)
            inv = private["inventories"][idx] if idx < len(private["inventories"]) else {}
            tile = None
            if pos is not None:
                tile = farm["tiles"][pos[1]][pos[0]]
            op = action[0]
            mel = inv.get("MELON", 0)
            on_melon = isinstance(tile, dict) and tile.get("crop") == "MELON"
            if op in ("HARVEST", "DROP", "PLACE", "PICKUP") and (on_melon or mel or (len(action) > 1 and action[1] == "MELON")):
                LOG[s].append(f"u{idx}@{tuple(pos)} {action} carrying {mel}")
            elif on_melon:
                LOG[s].append(f"u{idx}@{tuple(pos)} {action} on melon")
        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    K._process_market, K._apply_unit_action = pm, apply
    f = fastarena.load_agent(a.agent)
    g = fastarena.load_agent(a.opp)
    fns = [f, g] if a.seat == 0 else [g, f]
    r = fastarena.run_game(fns[0], fns[1], a.seed)
    for s in sorted(LOG):
        print(f"s{s} d{s // 24}h{s % 24:02d}: " + " | ".join(LOG[s]))
    print("rewards", r["rewards"])


if __name__ == "__main__":
    main()
