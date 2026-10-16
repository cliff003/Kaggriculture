r"""Wrap an agent with a melon-race market layer.

    .venv\Scripts\python.exe gold\oracle\mk_melon.py BASE_MAIN_PY OUT_NAME [DAYS=10,11] [MIN_PRICE=0] [SHARE=1.0]

On the listed days, every step sells all melons that will be in the shed after this step's unit actions (shed plus
PLACE/DROP of melons by units standing on shed tiles) in slot 0, replacing the base agent's own melon order.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CODE = r'''
_BASE_PATH = %r
_DAYS = %r
_MIN_PRICE = %r
_SHARE = %r
_ACCESS = ((4, 4), (5, 4), (4, 5), (5, 5))


def _load_base():
    from kaggle_environments.agent import get_last_callable
    import contextlib, io, os
    raw = open(_BASE_PATH, encoding="utf-8").read()
    with contextlib.redirect_stdout(io.StringIO()):
        return get_last_callable(raw, path=os.path.abspath(_BASE_PATH))


_BASE = _load_base()


def _call_base(obs, cfg):
    co = getattr(_BASE, "__code__", None)
    if co is not None and co.co_argcount < 2:
        return _BASE(obs)
    return _BASE(obs, cfg)


def agent(observation, configuration=None):
    a = _call_base(observation, configuration)
    try:
        step = int(observation["step"])
        if step // 24 not in _DAYS or not isinstance(a, dict):
            return a
        me = int(observation["player"])
        farm = observation["farms"][me]
        pos = [tuple(farm["farmer"])] + [tuple(h) for h in (farm.get("hands") or [])]
        invs = observation["private"]["inventories"]
        units = [a.get("farmer")] + list(a.get("hands") or [])
        n = int(observation["private"]["shed"].get("MELON", 0) or 0)
        for i, act in enumerate(units):
            if i >= len(pos) or not act or pos[i] not in _ACCESS:
                continue
            inv = invs[i] if i < len(invs) else {}
            if act[0] == "DROP":
                n += int(inv.get("MELON", 0) or 0)
            elif act[0] == "PLACE" and len(act) >= 2 and act[1] == "MELON":
                n += min(int(inv.get("MELON", 0) or 0), int(act[2]) if len(act) >= 3 else 1)
        if n <= 0 or int(observation["market"]["prices"].get("MELON", 0)) < _MIN_PRICE:
            return a
        q = max(1, int(n * _SHARE))
        market = [o for o in (a.get("market") or []) if not (isinstance(o, list) and len(o) >= 2 and o[0] == "SELL" and o[1] == "MELON")]
        market.insert(0, ["SELL", "MELON", q])
        a = dict(a)
        a["market"] = market[:10]
    except Exception:
        pass
    return a
'''


def main():
    base, name = os.path.abspath(sys.argv[1]), sys.argv[2]
    kv = dict(x.split("=", 1) for x in sys.argv[3:])
    days = tuple(int(x) for x in kv.get("DAYS", "10,11").split(","))
    code = CODE % (base, days, int(kv.get("MIN_PRICE", "0")), float(kv.get("SHARE", "1.0")))
    out = os.path.join(ROOT, "gold", "builds", name)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(code)
    print(os.path.join(out, "main.py"))


if __name__ == "__main__":
    main()
