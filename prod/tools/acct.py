r"""Accounting runner: play A vs B on seeds, log every market unit, hire, land purchase.

.venv\Scripts\python.exe prod\tools\acct.py A.py B.py --seeds 1000-1019 --out prod\results\x.jsonl [--swap] [-j 14]

Per game and side: final money, sales per item (units, revenue), spend per category,
tile counts at end of each day, shops.
"""
import argparse
import collections
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import fastarena  # noqa: E402
from kaggle_environments.envs.kaggriculture import kaggriculture as K  # noqa: E402

ITEMS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
_CUR = {"log": None, "farms": None, "step": 0}
_orig = {"commit": K._commit_unit, "hire": K._do_hire, "land": K._do_buy_land, "interp": K.interpreter}


def _pid(farm):
    fs = _CUR["farms"]
    return 0 if fs is not None and farm is fs[0] else 1


def _commit(op, item, price, farm, private, market, shed_capacity=100):
    ok = _orig["commit"](op, item, price, farm, private, market, shed_capacity)
    if ok and _CUR["log"] is not None:
        _CUR["log"].append((_CUR["step"], _pid(farm), op, item, price))
    return ok


def _hire(farm, private, board_size, mult=1):
    before = farm["money"]
    _orig["hire"](farm, private, board_size, mult)
    if farm["money"] != before and _CUR["log"] is not None:
        _CUR["log"].append((_CUR["step"], _pid(farm), "HIRE", "", before - farm["money"]))


def _land(farm, board_size):
    before = farm["money"]
    _orig["land"](farm, board_size)
    if farm["money"] != before and _CUR["log"] is not None:
        _CUR["log"].append((_CUR["step"], _pid(farm), "LAND", farm["unlocked_quadrants"][-1], before - farm["money"]))


def _interp(state, env):
    obs0 = state[0].observation
    if hasattr(obs0, "farms") and obs0.farms:
        _CUR["farms"] = obs0.farms
        _CUR["privates"] = [s.observation.private for s in state]
        _CUR["step"] = obs0.get("step", 0) if hasattr(obs0, "get") else getattr(obs0, "step", 0)
    r = _orig["interp"](state, env)
    step = _CUR["step"]
    if hasattr(obs0, "farms") and obs0.farms and (step + 1) % 24 == 0 and _CUR.get("snaps") is not None:
        snap = []
        for i in range(2):
            f = obs0.farms[i]
            c = collections.Counter()
            for row in f["tiles"]:
                for t in row:
                    if isinstance(t, dict):
                        c[t.get("animal") or t.get("crop") or t.get("kind")] += 1
            snap.append({"money": f["money"], "tiles": dict(c), "quads": len(f["unlocked_quadrants"]),
                         "shed": sum(state[i].observation.private["shed"].values())})
        _CUR["snaps"].append(snap)
    return r


_orig["drop"] = K._drop_inventories_to_shed


def _drop(private, capacity):
    carried = collections.Counter()
    for inv in private["inventories"]:
        for k, v in inv.items():
            if v > 0:
                carried[k] += v
    before = dict(private["shed"])
    _orig["drop"](private, capacity)
    if _CUR["log"] is not None and _CUR.get("privates") is not None:
        side = 0 if private is _CUR["privates"][0] else 1
        for k, n in carried.items():
            lost = n - (private["shed"].get(k, 0) - before.get(k, 0))
            if lost > 0:
                _CUR["log"].append((_CUR["step"], side, "LOST", k, lost))


K._commit_unit, K._do_hire, K._do_buy_land, K.interpreter = _commit, _hire, _land, _interp
K._drop_inventories_to_shed = _drop


def summarize(log, side):
    sales = collections.defaultdict(lambda: [0, 0.0])
    spend = collections.Counter()
    hires = 0
    land = []
    for step, p, op, item, price in log:
        if p != side:
            continue
        if op == "SELL":
            sales[item][0] += 1
            sales[item][1] += price
        elif op == "HIRE":
            spend["HIRE"] += price
            hires += 1
        elif op == "LAND":
            spend["LAND"] += price
            land.append(step // 24)
        elif op == "LOST":
            spend["LOST_UNITS:" + item] += price
        else:
            spend[op.replace("BUY_", "") + ":" + item] += price
    return {"sales": {k: v for k, v in sales.items()}, "spend": dict(spend), "hires": hires, "land": land}


_AG = {}


def play(args):
    a, b, seed = args
    if a not in _AG:
        _AG[a] = fastarena.load_agent(a)
    if b not in _AG:
        _AG[b] = fastarena.load_agent(b)
    _CUR["log"] = []
    _CUR["snaps"] = []
    _CUR["farms"] = None
    t0 = time.time()
    r = fastarena.run_game(_AG[a], _AG[b], seed)
    env = r["env"]
    shops = list(r["final_state"][0].observation.town["unlocked_shops"])
    out = {"a": a, "b": b, "seed": seed, "rewards": r["rewards"], "shops": shops,
           "sides": [summarize(_CUR["log"], 0), summarize(_CUR["log"], 1)],
           "snaps": _CUR["snaps"], "wall": time.time() - t0, "errors": r["errors"]}
    if os.environ.get("ACCT_RAW"):
        out["log"] = _CUR["log"]
    _CUR["log"] = None
    return out


def parse_seeds(s):
    out = []
    for part in s.split(","):
        if "-" in part:
            x, y = part.split("-")
            out.extend(range(int(x), int(y) + 1))
        else:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--seeds", default="1000-1009")
    ap.add_argument("--swap", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("-j", type=int, default=14)
    args = ap.parse_args()
    jobs = []
    for s in parse_seeds(args.seeds):
        jobs.append((args.a, args.b, s))
        if args.swap:
            jobs.append((args.b, args.a, s))
    ctx = mp.get_context("spawn")
    n = 0
    with ctx.Pool(min(args.j, len(jobs))) as pool, open(args.out, "a", encoding="utf-8") as f:
        for res in pool.imap_unordered(play, jobs):
            f.write(json.dumps(res) + "\n")
            f.flush()
            n += 1
            ra, rb = res["rewards"]
            print(f"{n}/{len(jobs)} seed {res['seed']} {os.path.basename(os.path.dirname(res['a']))}={ra:.0f} "
                  f"{os.path.basename(os.path.dirname(res['b']))}={rb:.0f} ({res['wall']:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
