r"""Revenue by product and period for both sides.  period.py CAND OPP SEEDS [k=v ...]"""
import sys, os, json, collections, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
_AG = {}
import os as _os
PER = [tuple(map(int, x.split("-"))) for x in _os.environ.get("PERIODS", "0-9,10-13,14-17,18-22,23-29").split(",")]
def play(args):
    a, b, seed, ov = args
    import acct, fastarena
    for p in (a, b):
        if p not in _AG:
            _AG[p] = fastarena.load_agent(p)
    if "STATE" in _AG[a].__globals__:
        _AG[a].__globals__["STATE"]["_override"] = ov
    acct._CUR["log"] = []; acct._CUR["snaps"] = []
    fastarena.run_game(_AG[a], _AG[b], seed)
    out = collections.defaultdict(float)
    for step, p, op, item, pr in acct._CUR["log"]:
        d = step // 24
        per = [k for k, (x, y) in enumerate(PER) if x <= d <= y][0]
        if op == "SELL":
            out[(p, item, per)] += pr
        elif op in ("BUY_PRODUCT",):
            out[(p, "buy:" + item, per)] -= pr
        elif op == "LOST":
            out[(p, "lost_units", per)] += pr
            continue
        else:
            out[(p, "cost", per)] -= pr
    return dict((f"{k[0]}|{k[1]}|{k[2]}", v) for k, v in out.items())
if __name__ == "__main__":
    a, b, seeds = sys.argv[1], sys.argv[2], sys.argv[3]
    ov = {}
    for kv in sys.argv[4:]:
        k, v = kv.split("=", 1)
        try: v = json.loads(v)
        except Exception: pass
        ov[k] = v
    x, y = seeds.split("-")
    jobs = [(a, b, s, ov) for s in range(int(x), int(y) + 1)]
    with mp.get_context("spawn").Pool(int(os.environ.get("POOL", "4"))) as pool:
        res = pool.map(play, jobs)
    n = len(res)
    tot = collections.defaultdict(float)
    for r in res:
        for k, v in r.items():
            tot[k] += v / n
    items = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER", "buy:WHEAT", "buy:FERTILIZER", "cost", "lost_units"]
    print("item          " + "  ".join(f"d{x}-{y:<2d} me/opp   " for x, y in PER))
    for it in items:
        cells = []
        for k in range(len(PER)):
            cells.append(f"{tot.get(f'0|{it}|{k}', 0):6.0f}/{tot.get(f'1|{it}|{k}', 0):<6.0f}")
        print(f"{it:13s} " + "  ".join(f"{c:15s}" for c in cells))
    for side in (0, 1):
        print(side, "net by period:", [round(sum(v for k, v in tot.items() if k.startswith(f"{side}|") and k.endswith(f"|{p}") and "lost_units" not in k)) for p in range(len(PER))])
