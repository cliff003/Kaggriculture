"""Local arena for Kaggriculture agents.

Usage:
  python arena.py A B --games 20 --workers 2 [--seed0 1000]
Each seed is played twice with seats swapped, so results are seat-balanced.
Agents are paths to main.py files (or builtin names: starter/random/pass).
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time
import io
import contextlib


def load_agent(path):
    if path in ("starter", "random", "pass"):
        return path
    from kaggle_environments.agent import get_last_callable
    raw = open(path).read()
    fn = get_last_callable(raw, path=os.path.abspath(path))
    return fn


class Timed:
    def __init__(self, fn):
        self.fn = fn
        self.total = 0.0
        self.maxt = 0.0
        self.n = 0
        self.errors = 0

    def __call__(self, obs, config):
        t = time.perf_counter()
        try:
            try:
                r = self.fn(obs, config)
            except TypeError:
                r = self.fn(obs)
        except Exception as e:  # count, return safe action
            self.errors += 1
            r = {"farmer": ["PASS"], "hands": [], "market": []}
        dt = time.perf_counter() - t
        self.total += dt
        self.n += 1
        if dt > self.maxt:
            self.maxt = dt
        return r


def play(args):
    a_path, b_path, seed = args
    from kaggle_environments import make
    t0 = time.time()
    fa = load_agent(a_path)
    fb = load_agent(b_path)
    ta = Timed(fa) if callable(fa) else fa
    tb = Timed(fb) if callable(fb) else fb
    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": seed}, debug=False)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        env.run([ta, tb])
    final = env.steps[-1]
    rewards = [s.reward for s in final]
    statuses = [s.status for s in final]
    info = {
        "a": a_path, "b": b_path, "seed": seed,
        "ra": rewards[0], "rb": rewards[1], "status": statuses,
        "ta_mean": (ta.total / ta.n) if isinstance(ta, Timed) and ta.n else None,
        "ta_max": ta.maxt if isinstance(ta, Timed) else None,
        "tb_mean": (tb.total / tb.n) if isinstance(tb, Timed) and tb.n else None,
        "tb_max": tb.maxt if isinstance(tb, Timed) else None,
        "err_a": ta.errors if isinstance(ta, Timed) else 0,
        "err_b": tb.errors if isinstance(tb, Timed) else 0,
        "wall": time.time() - t0,
    }
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--games", type=int, default=10, help="number of seeds (each played in both seats)")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--seed0", type=int, default=1000)
    ap.add_argument("--out", default=None)
    ap.add_argument("--one-seat", action="store_true")
    args = ap.parse_args()

    jobs = []
    for i in range(args.games):
        s = args.seed0 + i
        jobs.append((args.a, args.b, s))
        if not args.one_seat:
            jobs.append((args.b, args.a, s))
    res = []
    wins = losses = ties = 0
    margin = 0.0
    ctx = mp.get_context("fork")
    with ctx.Pool(args.workers, maxtasksperchild=1) as pool:
        for info in pool.imap_unordered(play, jobs):
            res.append(info)
            if info["a"] == args.a and info["b"] == args.b and not (args.a == args.b):
                my, op = info["ra"], info["rb"]
            elif args.a == args.b:
                my, op = info["ra"], info["rb"]
            else:
                my, op = info["rb"], info["ra"]
            my = my or 0
            op = op or 0
            if my > op:
                wins += 1
            elif my < op:
                losses += 1
            else:
                ties += 1
            margin += my - op
            n = wins + losses + ties
            print(f"[{n}/{len(jobs)}] seed={info['seed']} A_seat={'0' if info['a']==args.a else '1'} A={my:.0f} B={op:.0f} "
                  f"W/L/T={wins}/{losses}/{ties} tA={info['ta_mean'] if info['a']==args.a else info['tb_mean']} "
                  f"wall={info['wall']:.1f}s err={info['err_a']},{info['err_b']} status={info['status']}", flush=True)
    n = wins + losses + ties
    print(f"FINAL {args.a} vs {args.b}: W/L/T={wins}/{losses}/{ties} winrate={(wins + 0.5*ties)/max(1,n):.3f} mean_margin={margin/max(1,n):.0f}")
    if args.out:
        with open(args.out, "a") as f:
            for r in res:
                f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
