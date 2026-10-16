r"""Add the SANDWICH guard to the TICK layer of a v8-line build (v8, v9, v12): stop our wheat churn against a rival
that trades around it inside the same step.

.venv\Scripts\python.exe tools\add_sandguard.py IN_MAIN_PY OUT_DIR [--x 40] [--flow 10] [--hits 2] [--win 4]
                                                [--obo 0] [--obo-hits 3]

A sandwich rival (seen live on 09-26: Sho Saga, lumen) buys wheat in slot 0 of the step where we buy in slot 9 and
sells the same amount in slot 9, lockstep with our buy, then sells in slot 0/1 of the next step and buys back in
slot 9. Its net wheat flow per step is zero, so the churn guard (market identity) never sees it, while our churn
pays its spread every tick (-15k to -17k in those games).

The probe: on a TICK buy step whose other orders are only HIRE / BUY_SEED (known costs), record our money and the
exact cost the engine would charge without any other wheat trade before slot 9. One step later the money we really
spent shows the excess; a rival that bought ahead of us raises it. The step's rival wheat flow (from the churn
guard's market identity) tells a feed buyer (flow = -its buy) from a sandwich (flow ~ 0). A probe is a hit when the
excess is at least X coins and |flow| <= FLOW; HITS hits among the last WIN probes stop our churn for the game.

--obo TH also stops our churn against an off-by-one churner (Takahiro, 09-26): it buys at s % 4 == 3, one step before
our buy, and sells at s + 1 after the town ate, often in an earlier slot than our sale, so our churn buys dear and
sells cheap (-2.6k in that game). OBO_HITS such round trips of TH+ units in the churn guard's window stop our churn.
"""
import argparse
import os

OLD_CFG_END = "'HITS': 2"
OLD_SKIP = '''        if mem.get("rival"):
            TEL["rival_skips"] = TEL.get("rival_skips", 0) + 1
            return a'''
NEW_SKIP = '''        if mem.get("rival") or mem.get("sand") or mem.get("obo"):
            TEL["rival_skips"] = TEL.get("rival_skips", 0) + 1
            return a'''
OLD_BUY = '''        market.append(["BUY_PRODUCT", "WHEAT", n])
        mem["pend"] = {"n": n, "without": int(pshed.get("WHEAT", 0)), "step": step}'''
NEW_BUY = '''        fixed = _fixed_cost(market, int(_get(me_farm, "hires_today", 0) or 0))
        market.append(["BUY_PRODUCT", "WHEAT", n])
        mem["pend"] = {"n": n, "without": int(pshed.get("WHEAT", 0)), "step": step}
        mem["probe"] = ({"step": step, "money": money, "exp": cost + fixed}
                        if fixed is not None and money >= cost + fixed + 50 else None)'''
OLD_FLOW = '''    if prev is not None and prev["step"] == step - 1 and prev["step"] % 24 != 23:
        our_net = prev["w_units"] - w_now
        mem["flow"][prev["step"]] = (inv_w - prev["inv"]) - our_net + prev["cons"]'''
NEW_FLOW = OLD_FLOW + '''
    pr = mem.get("probe")
    if pr is not None and pr["step"] == step - 1:
        mem["probe"] = None
        try:
            me = int(_get(observation, "player", 0))
            money_now = float(_get(_get(observation, "farms")[me], "money", 0))
            excess = (pr["money"] - money_now) - pr["exp"]
            fl = mem["flow"].get(step - 1)
            hit = 1 if (excess >= CFG["SAND_X"] and fl is not None and abs(fl) <= CFG["SAND_FLOW"]) else 0
            hist = mem.setdefault("probes", [])
            hist.append(hit)
            TEL["probes"] = TEL.get("probes", 0) + 1
            TEL["probe_hits"] = TEL.get("probe_hits", 0) + hit
            if not mem.get("sand") and sum(hist[-CFG["SAND_WIN"]:]) >= CFG["SAND_HITS"]:
                mem["sand"] = True
                TEL["sand_step"] = step
        except Exception:
            pass
    if CFG.get("OBO_TH") and not mem.get("obo") and step % 4 == 2:
        fl = mem["flow"]
        hits = 0
        for s0 in range(step - 2, step - 2 - 4 * CFG["WIN"], -4):
            if fl.get(s0 - 1, 0) <= -CFG["OBO_TH"] and fl.get(s0 + 1, 0) >= CFG["OBO_TH"]:
                hits += 1
        if hits >= CFG["OBO_HITS"]:
            mem["obo"] = True
            TEL["obo_step"] = step'''
OLD_DECIDE = "def _decide(observation, configuration=None):"
NEW_DECIDE = '''def _fixed_cost(market, hires_today):
    """Cost of the turn's fixed-price orders, or None if the turn has any other order (the probe needs a clean turn)."""
    s = 0.0
    h = hires_today
    for o in market:
        if not o:
            continue
        if o[0] == "HIRE":
            s += _FIB[min(39, h)]
            h += 1
        elif o[0] == "BUY_SEED" and len(o) >= 3 and o[1] in _SEED:
            s += _SEED[o[1]] * int(o[2])
        else:
            return None
    return s


def _decide(observation, configuration=None):'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--x", type=float, default=40.0)
    ap.add_argument("--flow", type=int, default=10)
    ap.add_argument("--hits", type=int, default=2)
    ap.add_argument("--win", type=int, default=4)
    ap.add_argument("--obo", type=int, default=0)
    ap.add_argument("--obo-hits", type=int, default=3)
    a = ap.parse_args()
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    start = s.index("_TICK_SRC = r'''")
    end = s.index("'''", start + len("_TICK_SRC = r'''"))
    tick = s[start:end]
    cfg_line = next(l for l in tick.split("\n") if l.startswith("CFG = {"))
    assert cfg_line.count(OLD_CFG_END) == 1 and "SAND_X" not in cfg_line
    new_cfg = cfg_line.replace(OLD_CFG_END, OLD_CFG_END + f", 'SAND_X': {a.x}, 'SAND_FLOW': {a.flow}, "
                                                          f"'SAND_HITS': {a.hits}, 'SAND_WIN': {a.win}, "
                                                          f"'OBO_TH': {a.obo}, 'OBO_HITS': {a.obo_hits}")
    for old, new in ((cfg_line, new_cfg), (OLD_SKIP, NEW_SKIP), (OLD_BUY, NEW_BUY), (OLD_FLOW, NEW_FLOW),
                     (OLD_DECIDE, NEW_DECIDE)):
        assert tick.count(old) == 1, old[:70]
        tick = tick.replace(old, new)
    s = s[:start] + tick + s[end:]
    compile(s, "main.py", "exec")
    if crlf:
        s = s.replace("\n", "\r\n")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "wb") as f:
        f.write(s.encode("utf-8"))
    print("wrote", os.path.join(a.out, "main.py"))


if __name__ == "__main__":
    main()
