"""Fast faithful game runner for Kaggriculture.

Replicates kaggle_environments' stepping semantics (initial reset via the real env,
per-step agent observation = own state + shared fields from player 0, structified copy)
but avoids the framework's heavy deepcopy/structify of the full history.

play((a_path, b_path, seed)) -> dict (same fields as arena.play)
"""
import importlib.abc
import json
import time
import io
import contextlib
import os
import sys


class _OnlyKaggriculture(importlib.abc.MetaPathFinder):
    """`import kaggle_environments` loads every bundled env (OpenSpiel, Lux, football, ...): ~150 MB and ~0.6 s
    per process. Only kaggriculture is played here, so the others fail fast and the package skips them."""

    def find_spec(self, name, path, target=None):
        p = name.split(".")
        if len(p) >= 3 and p[:2] == ["kaggle_environments", "envs"] and p[2] != "kaggriculture":
            raise ImportError(name)
        return None


if "kaggle_environments" not in sys.modules:
    _finder = _OnlyKaggriculture()
    sys.meta_path.insert(0, _finder)
    try:
        with contextlib.redirect_stdout(io.StringIO()):  # one "Loading environment X failed" line per skipped env
            import kaggle_environments
    finally:
        sys.meta_path.remove(_finder)

from kaggle_environments.utils import Struct

SHARED = ("farms", "market", "town", "day", "hour", "step")
_hook = lambda d: Struct(**d)


def _clone(o):
    return json.loads(json.dumps(o), object_hook=_hook)


def load_agent(path):
    if path in ("starter", "random", "pass"):
        from kaggle_environments.envs.kaggriculture import kaggriculture as K
        return K.agents[path]
    from kaggle_environments.agent import get_last_callable
    raw = open(path).read()
    with contextlib.redirect_stdout(io.StringIO()):
        fn = get_last_callable(raw, path=os.path.abspath(path))
    return fn


def _call(fn, obs, conf):
    co = getattr(fn, "__code__", None)
    if co is not None and co.co_argcount < 2:
        return fn(obs)
    return fn(obs, conf)


def run_game(fa, fb, seed, record=False, quiet=True, episode_steps=720, config_extra=None):
    from kaggle_environments import make
    from kaggle_environments.envs.kaggriculture import kaggriculture as K
    cfg = {"episodeSteps": episode_steps, "seed": seed}
    if config_extra:
        cfg.update(config_extra)
    env = make("kaggriculture", configuration=cfg, debug=False)
    env.reset(2)
    state = env.state
    conf = _clone(dict(env.configuration))
    fns = [fa, fb]
    times = [0.0, 0.0]
    maxt = [0.0, 0.0]
    errors = [0, 0]
    history = [] if record else None
    nsteps = 1  # len(env.steps) after reset
    sink = io.StringIO()
    while True:
        o0 = state[0].observation
        actions = []
        for i in range(2):
            if state[i].status != "ACTIVE":
                actions.append(None)
                continue
            obs = dict(state[i].observation)
            for k in SHARED:
                if k in o0:
                    obs[k] = o0[k]
            obs = _clone(obs)
            t = time.perf_counter()
            try:
                if quiet:
                    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                        a = _call(fns[i], obs, _clone(conf))
                else:
                    a = _call(fns[i], obs, _clone(conf))
            except Exception as e:  # agent crash -> ERROR status like kaggle
                a = e
                errors[i] += 1
            dt = time.perf_counter() - t
            times[i] += dt
            maxt[i] = max(maxt[i], dt)
            actions.append(a)
        # build action_state like env.step
        for i in range(2):
            a = actions[i]
            st = state[i]
            if isinstance(a, BaseException):
                st.status = "ERROR"
                st.action = None
            elif a is not None and not isinstance(a, dict):
                st.status = "INVALID"
                st.action = None
            else:
                st.action = _clone(a) if a is not None else None
        if record:
            history.append([
                {"action": state[i].action, "money": o0.farms[i]["money"]} for i in range(2)
            ])
        with contextlib.redirect_stdout(sink):
            K.interpreter(state, env)
        for st in state:
            if st.status in ("ERROR", "INVALID", "TIMEOUT"):
                st.reward = None
        state[0].observation.step = nsteps
        nsteps += 1
        if state[0].observation.step >= env.configuration.episodeSteps - 1:
            for st in state:
                if st.status in ("ACTIVE", "INACTIVE"):
                    st.status = "DONE"
        if all(st.status != "ACTIVE" for st in state):
            break
        sink.seek(0); sink.truncate(0)
    rewards = [st.reward for st in state]
    return {
        "rewards": rewards,
        "status": [st.status for st in state],
        "t_mean": [times[i] / max(1, nsteps - 1) for i in range(2)],
        "t_max": maxt,
        "errors": errors,
        "final_state": state,
        "history": history,
        "env": env,
    }


def play(args):
    a_path, b_path, seed = args[:3]
    t0 = time.time()
    fa = load_agent(a_path)
    fb = load_agent(b_path)
    r = run_game(fa, fb, seed)
    return {
        "a": a_path, "b": b_path, "seed": seed,
        "ra": r["rewards"][0], "rb": r["rewards"][1], "status": r["status"],
        "ta_mean": r["t_mean"][0], "ta_max": r["t_max"][0],
        "tb_mean": r["t_mean"][1], "tb_max": r["t_max"][1],
        "err_a": r["errors"][0], "err_b": r["errors"][1],
        "wall": time.time() - t0,
    }


if __name__ == "__main__":
    a, b, s = sys.argv[1], sys.argv[2], int(sys.argv[3])
    print(play((a, b, s)))
