r"""Average money by day for both sides: curve.py CAND OPP SEEDS [--set k=v ...]"""
import sys, os, json, statistics, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
_AG = {}
def play(args):
    a, b, seed, ov = args
    import acct, fastarena
    for p in (a, b):
        if p not in _AG:
            _AG[p] = fastarena.load_agent(p)
    if "STATE" in _AG[a].__globals__:
        _AG[a].__globals__["STATE"]["_override"] = ov
    acct._CUR["log"] = []; acct._CUR["snaps"] = []
    r = fastarena.run_game(_AG[a], _AG[b], seed)
    return [[s[0]["money"], s[1]["money"], s[0]["tiles"], s[1]["tiles"]] for s in acct._CUR["snaps"]], r["rewards"]
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
    for d in range(30):
        m0 = statistics.mean(r[0][d][0] for r in res if d < len(r[0]))
        m1 = statistics.mean(r[0][d][1] for r in res if d < len(r[0]))
        def tc(i):
            c = {}
            for r in res:
                if d < len(r[0]):
                    for k, v in r[0][d][2 + i].items():
                        c[k] = c.get(k, 0) + v
            return " ".join(f"{k[:3]}{v / len(res):.0f}" for k, v in sorted(c.items()) if v / len(res) >= 0.5)
        print(f"d{d:2d} me {m0:8.0f}  opp {m1:8.0f}  diff {m0 - m1:+8.0f} | {tc(0)} || {tc(1)}")
