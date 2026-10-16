r"""MIRROR mode for the TICK layer of a v8-line build: keep churning against a flagged tick churner, in slot 0.

.venv\Scripts\python.exe tools\add_mirror.py IN_MAIN_PY OUT_DIR

When the churn guard flags a rival that buys wheat at s % 4 == 0 and sells it at s + 1, v8 stops its own churn for
the game and the rival keeps the whole tick profit. With both sides trading the same slot the engine fills them
lockstep, unit by unit at the same quote, and to first order each side then earns what it would earn alone
(the price lift doubles, and so does the part of it the town's consumption pays). MIRROR puts our buy in slot 0 and
the sale at s + 1 in slot 0 instead of stopping. A build with the TICK TRAP GUARD layer also marks traps
("trapped"), and a trapped game stays stopped.
"""
import argparse
import os

OLD_SKIP = '''        if mem.get("rival"):
            TEL["rival_skips"] = TEL.get("rival_skips", 0) + 1
            return a'''
NEW_SKIP = '''        mirror = bool(mem.get("rival") and CFG.get("MIRROR") and not mem.get("trapped"))
        if mem.get("rival") and not mirror:
            TEL["rival_skips"] = TEL.get("rival_skips", 0) + 1
            return a'''
OLD_BUY = '''        if CFG["BUYSLOT"] == "pad":
            while len(market) < 9:
                market.append([])
        market.append(["BUY_PRODUCT", "WHEAT", n])
        mem["pend"] = {"n": n, "without": int(pshed.get("WHEAT", 0)), "step": step}'''
NEW_BUY = '''        if mirror:
            market.insert(0, ["BUY_PRODUCT", "WHEAT", n])
            TEL["mirror_buys"] = TEL.get("mirror_buys", 0) + 1
        else:
            if CFG["BUYSLOT"] == "pad":
                while len(market) < 9:
                    market.append([])
            market.append(["BUY_PRODUCT", "WHEAT", n])
        mem["pend"] = {"n": n, "without": int(pshed.get("WHEAT", 0)), "step": step, "mirror": mirror}'''
OLD_SELL = '''                if CFG["SELLSLOT"] == "first" and len(market) < 10:'''
NEW_SELL = '''                if (CFG["SELLSLOT"] == "first" or pend.get("mirror")) and len(market) < 10:'''
OLD_TG = '''        if CFG["ACT"] and (mem["trap"] or mem["prebuy"]) and tick_mem is not None:
            tick_mem["rival"] = True'''
NEW_TG = '''        if CFG["ACT"] and (mem["trap"] or mem["prebuy"]) and tick_mem is not None:
            tick_mem["rival"] = True
            tick_mem["trapped"] = True'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    a = ap.parse_args()
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    start = s.index("_TICK_SRC = r'''")
    end = s.index("'''", start + len("_TICK_SRC = r'''"))
    tick = s[start:end]
    cfg_line = next(l for l in tick.split("\n") if l.startswith("CFG = {"))
    assert "MIRROR" not in cfg_line
    tick = tick.replace(cfg_line, cfg_line[:-1] + ", 'MIRROR': 1}")
    for old, new in ((OLD_SKIP, NEW_SKIP), (OLD_BUY, NEW_BUY), (OLD_SELL, NEW_SELL)):
        assert tick.count(old) == 1, old[:60]
        tick = tick.replace(old, new)
    s = s[:start] + tick + s[end:]
    if "_TG_SRC = r'''" in s:
        assert s.count(OLD_TG) == 1
        s = s.replace(OLD_TG, NEW_TG)
    compile(s, "main.py", "exec")
    if crlf:
        s = s.replace("\n", "\r\n")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "wb") as f:
        f.write(s.encode("utf-8"))
    print("wrote", os.path.join(a.out, "main.py"))


if __name__ == "__main__":
    main()
