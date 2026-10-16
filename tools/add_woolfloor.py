r"""Insert the WOOLFLOOR layer into a team-42 build, just inside the TICK layer (else outermost).

.venv\Scripts\python.exe tools\add_woolfloor.py IN_MAIN_PY OUT_DIR [--floor 0.4] [--min-yarn 2] [--last-step 690]

Where at least MIN_YARN yarn stores are unlocked the town eats wool fast (a single-product shop takes two units
every four steps), so a lot the route dumps at once crashes the square-shaped glut curve but the quote comes back
within a day (live yarn worlds: sold at ~$18, back to ~$52 a day later). This layer caps every turn's wool sales at
the units whose marginal quote stays at or above FLOOR x base (wool price function of the engine, current market
inventory); what is held back stays in the shed and the eager layer sells it once the quote is back. From
LAST_STEP on nothing is capped (the stock must go before the end).
"""
import argparse
import os

LAYER = r'''
# ---------------------------------------------------------------------------
# Team 42 WOOLFLOOR layer: see tools/add_woolfloor.py.
import math as _wf_math
_WF_FLOOR = @FLOOR@
_WF_MIN_YARN = @MINYARN@
_WF_LAST = @LAST@
_WF_REPORT = {"capped_turns": 0, "held_units": 0}


def _wf_price(inv):
    base, i0, t = 200.0, 10000, 105.0
    if inv < i0:
        amp = 0.20 * base / _wf_math.log(1 + t)
        p = base + amp * _wf_math.log(1 + (i0 - inv))
    else:
        amp = 3.20 * base / (t * t)
        p = base - amp * (inv - i0) ** 2
    return max(1, int(round(p)))


def _woolfloor(obs, action):
    step = int(obs["step"])
    if not isinstance(action, dict) or step >= _WF_LAST:
        return action
    if list(obs["town"]["unlocked_shops"]).count("YARN_STORE") < _WF_MIN_YARN:
        return action
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
    total = sum(int(o[2]) for o in market if o and len(o) >= 3 and o[:2] == ["SELL", "WOOL"])
    if total <= 0:
        return action
    inv = int((obs["market"].get("inventory") or {}).get("WOOL", 10000))
    floor = _WF_FLOOR * 200
    allowed = 0
    while allowed < total and _wf_price(inv + allowed) >= floor:
        allowed += 1
    if allowed >= total:
        return action
    cut = total - allowed
    _WF_REPORT["capped_turns"] += 1
    _WF_REPORT["held_units"] += cut
    for o in reversed(market):
        if cut > 0 and o and len(o) >= 3 and o[:2] == ["SELL", "WOOL"]:
            take = min(int(o[2]), cut)
            o[2] = int(o[2]) - take
            cut -= take
    market = [o for o in market if not (o and len(o) >= 3 and o[:2] == ["SELL", "WOOL"] and int(o[2]) <= 0)]
    out = dict(action)
    out["market"] = market
    return out


_PRE_WF_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_WF_AGENT(observation, configuration)
    try:
        return _woolfloor(observation, action)
    except Exception:
        return action

'''
MARK = "# ---------------------------------------------------------------------------\n# Team 42 TICK layer"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--floor", type=float, default=0.4)
    ap.add_argument("--min-yarn", type=int, default=2)
    ap.add_argument("--last-step", type=int, default=690)
    a = ap.parse_args()
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    src = raw.decode("utf-8").replace("\r\n", "\n")
    layer = (LAYER.replace("@FLOOR@", repr(a.floor)).replace("@MINYARN@", str(a.min_yarn))
             .replace("@LAST@", str(a.last_step)))
    if MARK in src:
        i = src.index(MARK)
        code = src[:i].rstrip("\n") + "\n\n" + layer.lstrip("\n") + "\n" + src[i:]
    else:
        code = src.rstrip("\n") + "\n" + layer
    compile(code, "main.py", "exec")
    if crlf:
        code = code.replace("\n", "\r\n")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "wb") as f:
        f.write(code.encode("utf-8"))
    print("wrote", os.path.join(a.out, "main.py"))


if __name__ == "__main__":
    main()
