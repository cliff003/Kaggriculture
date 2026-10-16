r"""Goods our seat loses to a full shed (DROP overflow and end-of-day overflow) in live-game replays.

    .venv\Scripts\python.exe gold\front\droploss.py CAND.py ID [ID ...]

Our seat (team 42) is replaced by CAND, the rival's recorded actions are kept. Prints the margin and lost units by
item for both seats.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)


def main():
    import fastarena
    import forceshops
    from cfroute import tape_file
    from tgrun import find_recs
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    cand, ids = sys.argv[1], sys.argv[2:]
    recs = find_recs(ids)
    CNT = {"u": 0, "d": 0}
    LOST = collections.defaultdict(collections.Counter)
    orig_pm, orig_apply, orig_drop = K._process_market, K._apply_unit_action, K._drop_inventories_to_shed

    def pm(state, env):
        CNT["u"] = 0
        CNT["d"] = 0
        return orig_pm(state, env)

    def apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=100):
        if idx == 0:
            CNT["u"] += 1
        seat = CNT["u"] - 1
        if isinstance(action, list) and action and action[0] == "DROP":
            invs = private["inventories"]
            inv = dict(invs[idx]) if idx < len(invs) else {}
            before = sum(private["shed"].values())
            orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)
            gained = sum(private["shed"].values()) - before
            carried = sum(v for v in inv.values() if v > 0)
            if carried > gained and idx < len(invs) and not invs[idx]:
                left = carried - gained
                for item, n in sorted(inv.items(), key=lambda x: -x[1]):
                    if left <= 0:
                        break
                    k = min(n, left)
                    LOST[seat][item] += k
                    left -= k
            return None
        return orig_apply(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)

    def drop(private, capacity):
        CNT["d"] += 1
        seat = CNT["d"] - 1
        before = sum(private["shed"].values())
        carried = collections.Counter()
        for inv in private["inventories"]:
            for item, n in inv.items():
                if n > 0:
                    carried[item] += n
        orig_drop(private, capacity)
        gained = sum(private["shed"].values()) - before
        left = sum(carried.values()) - gained
        for item, n in carried.most_common():
            if left <= 0:
                break
            k = min(n, left)
            LOST[seat]["EOD:" + item] += k
            left -= k

    K._process_market, K._apply_unit_action, K._drop_inventories_to_shed = pm, apply, drop
    try:
        for rid, rec in recs.items():
            LOST.clear()
            me = rec["teams"].index("42")
            tape = tape_file(rec, 1 - me)
            forceshops.force(rec["shops"])
            fns = [None, None]
            fns[me] = fastarena.load_agent(cand)
            fns[1 - me] = fastarena.load_agent(tape)
            r = fastarena.run_game(fns[0], fns[1], rec["seed"])
            margin = (r["rewards"][me] or 0) - (r["rewards"][1 - me] or 0)
            print(f"{rid} {rec['teams'][1 - me][:18]:18s} margin {margin:+8.0f}  our lost {dict(LOST[me])}  "
                  f"rival lost {sum(LOST[1 - me].values())}", flush=True)
    finally:
        K._process_market, K._apply_unit_action, K._drop_inventories_to_shed = orig_pm, orig_apply, orig_drop


if __name__ == "__main__":
    main()
