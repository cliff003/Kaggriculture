r"""Build behaviour-cloning shards from recorded games of one team (research, 09-27).

.venv\Scripts\python.exe bc\extract.py TEAM OUT.npz GAMES.jsonl.gz [...] [--max N]

Each game is re-simulated with the local engine (it reproduces live games exactly); at every step the team's own
observation is encoded (bc/encode.py) together with each unit's recorded action and the step's market orders.
"""
import argparse
import glob
import gzip
import json
import multiprocessing as mp
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))


def job(args):
    rec, team = args
    import encode as E
    from kaggle_environments import make
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    me = rec["teams"].index(team)
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": rec["seed"]}, debug=False)
    env.reset(2)
    state = env.state
    n = len(rec["acts"][0])
    boards, globs, mkts = [], [], []
    u_step, u_vec, u_pos, u_act, u_qty = [], [], [], [], []
    for t in range(719):
        o0 = state[0].observation
        obs = {"farms": o0.farms, "private": state[me].observation.private, "market": o0.market,
               "town": o0.town, "step": t, "player": me}
        day, hour = t // 24, t % 24
        a = rec["acts"][me][t + 1] if t + 1 < n else None
        a = a if isinstance(a, dict) else {}
        farm = o0.farms[me]
        b, pos = E.board(farm, day)
        gv, shed = E.glob_vec(obs, me, day, hour)
        si = len(boards)
        boards.append(np.clip(np.round(b * 4), 0, 255).astype(np.uint8))
        globs.append(gv)
        mkts.append(E.market_targets(a.get("market")))
        invs = state[me].observation.private.get("inventories", [{}]) if hasattr(state[me].observation.private, "get") else [{}]
        units = [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
        for idx, (x, y) in enumerate(pos):
            act = units[idx] if idx < len(units) else ["PASS"]
            k, q = E.action_class(act)
            if k is None:
                continue
            inv_u = invs[idx] if idx < len(invs) else {}
            u_step.append(si)
            u_vec.append(E.unit_vec(inv_u, idx, len(pos)))
            u_pos.append((x, y))
            u_act.append(k)
            u_qty.append(q)
        for i in range(2):
            ai = rec["acts"][i][t + 1] if t + 1 < n else None
            state[i].action = ai if isinstance(ai, dict) else None
        K.interpreter(state, env)
        state[0].observation.step = t + 1
    final = [float(state[0].observation.farms[i]["money"]) for i in range(2)]
    ok = abs(final[me] - (rec["rewards"][me] or 0)) < 1.0
    return {"id": rec["id"], "ok": ok, "margin": final[me] - final[1 - me], "money": final[me],
            "boards": np.stack(boards), "globs": np.stack(globs), "mkts": np.stack(mkts),
            "u_step": np.asarray(u_step, np.int32), "u_vec": np.stack(u_vec), "u_pos": np.asarray(u_pos, np.int8),
            "u_act": np.asarray(u_act, np.int16), "u_qty": np.asarray(u_qty, np.int16)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("team")
    ap.add_argument("out")
    ap.add_argument("games", nargs="+")
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    recs, seen = [], set()
    for pat in a.games:
        for f in glob.glob(pat):
            for line in gzip.open(f, "rt", encoding="utf-8"):
                try:
                    g = json.loads(line)
                except Exception:
                    continue
                if a.team in g["teams"] and g["id"] not in seen and g.get("seed") is not None:
                    seen.add(g["id"])
                    recs.append(g)
    if a.max:
        recs = recs[:a.max]
    print(len(recs), "games of", a.team, flush=True)
    with mp.get_context("spawn").Pool(a.workers) as pool:
        res = pool.map(job, [(g, a.team) for g in recs], chunksize=1)
    bad = [r["id"] for r in res if not r["ok"]]
    res = [r for r in res if r["ok"]]
    print("reproduced", len(res), "games; mismatched", len(bad), bad[:5], flush=True)
    offs = np.cumsum([0] + [len(r["boards"]) for r in res])
    out = {"boards": np.concatenate([r["boards"] for r in res]), "globs": np.concatenate([r["globs"] for r in res]),
           "mkts": np.concatenate([r["mkts"] for r in res]),
           "u_step": np.concatenate([r["u_step"] + offs[i] for i, r in enumerate(res)]),
           "u_vec": np.concatenate([r["u_vec"] for r in res]), "u_pos": np.concatenate([r["u_pos"] for r in res]),
           "u_act": np.concatenate([r["u_act"] for r in res]), "u_qty": np.concatenate([r["u_qty"] for r in res]),
           "game": np.concatenate([np.full(len(r["boards"]), i, np.int32) for i, r in enumerate(res)]),
           "margin": np.asarray([r["margin"] for r in res], np.float32),
           "money": np.asarray([r["money"] for r in res], np.float32),
           "ids": np.asarray([r["id"] for r in res], np.int64)}
    np.savez_compressed(a.out, **out)
    print("wrote", a.out, "steps", len(out["boards"]), "unit samples", len(out["u_act"]),
          "mean money", float(out["money"].mean()), "mean margin", float(out["margin"].mean()))


if __name__ == "__main__":
    main()
