r"""Per-day diagnostics for player 0 of A vs B.  diag.py A B SEED [--days 0-29] [--steps d:h-d:h]

Per day: money, units, action mix, escapes/weeds (from plants), tile counts, sales.
"""
import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
sys.path.insert(0, HERE)
import acct  # noqa: E402  (installs market hooks)
import fastarena  # noqa: E402
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa: E402


def tile_key(t):
    if t is None:
        return "."
    if t == "LOCKED":
        return "#"
    return t.get("animal") or t.get("crop") or t.get("kind")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("seed", type=int)
    ap.add_argument("--side", type=int, default=0)
    ap.add_argument("--trace", default="", help="d:h-d:h print unit actions")
    ap.add_argument("--set", nargs="*", default=[])
    args = ap.parse_args()
    fa = fastarena.load_agent(args.a)
    if args.set:
        import json as _json
        ov = {}
        for kv in args.set:
            k, v = kv.split("=", 1)
            try:
                v = _json.loads(v)
            except Exception:
                pass
            ov[k] = v
        fa.__globals__["STATE"]["_override"] = ov
    fb = fastarena.load_agent(args.b)
    side = args.side
    acct._CUR["log"] = []
    acct._CUR["snaps"] = []
    # wrap interpreter to capture per-step actions and tile deltas
    per_day = collections.defaultdict(lambda: {"ops": collections.Counter(), "units": 0, "noop": collections.Counter()})
    orig = K.interpreter
    tr0 = tr1 = None
    if args.trace:
        a, b = args.trace.split("-")
        tr0 = int(a.split(":")[0]) * 24 + int(a.split(":")[1])
        tr1 = int(b.split(":")[0]) * 24 + int(b.split(":")[1])
    prev = {}

    def interp(state, env):
        obs0 = state[0].observation
        if hasattr(obs0, "farms") and obs0.farms:
            step = obs0.get("step", 0)
            day = step // 24
            act = state[side].action or {}
            units = [act.get("farmer", ["PASS"])] + list(act.get("hands", []) or [])
            farm = obs0.farms[side]
            before = [[dict(t) if isinstance(t, dict) else t for t in row] for row in farm["tiles"]]
            pos_before = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
            invs_before = [dict(i) for i in state[side].observation.private["inventories"]]
            shed_before = dict(state[side].observation.private["shed"])
            r = orig(state, env)
            d = per_day[day]
            d["units"] = max(d["units"], len(pos_before))
            farm = obs0.farms[side]
            after = farm["tiles"]
            for yy in range(10):
                for xx in range(10):
                    tb_, ta_ = before[yy][xx], after[yy][xx]
                    if isinstance(tb_, dict) and tb_.get("kind") == "PLANT" and isinstance(ta_, dict) and ta_.get("kind") == "WEED":
                        why = "dry" if (step + 1) % 24 == 0 and tb_.get("consecutive_unwatered", 0) >= 1 and not tb_.get("watered_today") else "decay"
                        d["noop"]["D" + why[0] + ":" + tb_["crop"][:3]] += 1
                    if isinstance(tb_, dict) and tb_.get("animal") and isinstance(ta_, dict) and not ta_.get("animal") and ta_.get("kind") in ("COOP", "PASTURE"):
                        d["noop"]["ESC:" + tb_["animal"][:3]] += 1
            if (step + 1) % 24 == 0:
                carried = sum(sum(v for v in inv.values()) for inv in invs_before)
                d["eod_carried"] = carried
            for ui, a in enumerate(units):
                if not a:
                    continue
                op = a[0] if isinstance(a, list) else str(a)
                d["ops"][op] += 1
                if op in ("WATER", "HARVEST", "FEED", "CARE", "COLLECT_FERTILIZER", "FERTILIZE", "PLANT", "DIG",
                          "BUILD_COOP", "BUILD_PASTURE", "PLACE", "PICKUP", "DROP") and ui < len(pos_before):
                    x, y = pos_before[ui]
                    tb, ta = before[y][x], after[y][x] if (step + 1) % 24 else None
                    if (step + 1) % 24 and tb == ta and op not in ("PICKUP", "DROP", "PLACE"):
                        d["noop"][op] += 1
            if tr0 is not None and tr0 <= step <= tr1:
                print(f"step {step} d{day}h{step % 24} money {farm['money']:.0f} market {act.get('market')}", file=sys.stderr)
                for ui, a in enumerate(units):
                    p = pos_before[ui] if ui < len(pos_before) else None
                    t = before[p[1]][p[0]] if p else None
                    print(f"   u{ui} at {p} [{tile_key(t)}] -> {a}  inv {invs_before[ui] if ui < len(invs_before) else {}}", file=sys.stderr)
            return r
        return orig(state, env)

    K.interpreter = interp
    r = fastarena.run_game(fa, fb, args.seed)
    K.interpreter = orig
    snaps = acct._CUR["snaps"]
    log = acct._CUR["log"]
    print("rewards", r["rewards"])
    sales = collections.defaultdict(collections.Counter)
    spend = collections.defaultdict(collections.Counter)
    for step, p, op, item, pr in log:
        if p == side and op == "SELL":
            sales[step // 24][item] += pr
        elif p == side:
            key = {"BUY_SEED": "s", "BUY_ANIMAL": "a", "BUY_PRODUCT": "p", "HIRE": "h", "LAND": "L"}.get(op, op) + ":" + (item or "")[:3]
            spend[step // 24][key] += pr
    g = fa.__globals__
    for k, S in g.get("STATE", {}).items():
        if S.get("errors"):
            print("agent errors", S["errors"][:3])
            print(S.get("tb"))
    for day in range(30):
        d = per_day[day]
        s = snaps[day][side] if day < len(snaps) else {}
        ops = d["ops"]
        tot = sum(ops.values())
        mv = sum(ops[m] for m in ("NORTH", "SOUTH", "EAST", "WEST"))
        work = " ".join(f"{k[:4]}{v}" for k, v in sorted(ops.items()) if k not in ("NORTH", "SOUTH", "EAST", "WEST", "PASS"))
        noop = " ".join(f"{k[:4]}{v}" for k, v in d["noop"].items())
        tiles = " ".join(f"{k[:3]}{v}" for k, v in sorted(s.get("tiles", {}).items()))
        sl = " ".join(f"{k[:3]}{v:.0f}" for k, v in sorted(sales[day].items()))
        print(f"d{day:2d} ${s.get('money', 0):7.0f} u{d['units']:2d} turns {tot:3d} mv {mv:3d} pass {ops['PASS']:3d} | {work} | noop {noop}")
        sp = " ".join(f"{k}{v:.0f}" for k, v in sorted(spend[day].items()))
        print(f"      tiles {tiles} | shed {s.get('shed')} eodcarry {d.get('eod_carried')} | sold {sl}")
        print(f"      spend {sp}")


if __name__ == "__main__":
    main()
