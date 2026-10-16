r"""Ledger comparison in a hybrid game: side 0 = hybrid agent, side 1 = v8.  hybled.py HYB_MAIN SEEDS [k=v ...]"""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))
import ledger, fastarena
hyb = sys.argv[1]
seeds = [int(x) for x in sys.argv[2].split(",")]
ov = {}
for kv in sys.argv[3:]:
    k, v = kv.split("=", 1)
    try: v = json.loads(v)
    except Exception: pass
    ov[k] = v
fa = fastarena.load_agent(hyb)
fa.__globals__["STATE"]["_override"] = ov
orig = fastarena.load_agent
ledger.fastarena.load_agent = lambda p: fa if p == "A" else orig(p)
V8 = "submissions/v8_own_cha22_tick_guard10/main.py"
res = {0: [], 1: []}
anim = {0: collections.defaultdict(collections.Counter), 1: collections.defaultdict(collections.Counter)}
for s in seeds:
    for side in (0, 1):
        done, animals, rew = ledger.run("A", V8, s, side)
        res[side] += done
        for k, v in animals.items():
            a = anim[side][k[2]]
            a["n"] += 1
            for f in ("days", "fed", "cared", "units", "coll"):
                a[f] += v[f]
for side in (0, 1):
    print("== hybrid(p3)" if side == 0 else "== v8")
    by = collections.defaultdict(list)
    for r in res[side]:
        by[r["crop"]].append(r)
    for c, rs in sorted(by.items()):
        ends = collections.Counter(r["end"] for r in rs)
        n = len(rs)
        dead = collections.Counter(r["endday"] - r["day"] for r in rs if r["end"] == "weed")
        print(f"  {c:10s} n={n:4d} units/pl {sum(r['units'] for r in rs)/n:5.2f} harv {sum(r['harv'] for r in rs)/n:4.2f} fert {sum(r['fert'] for r in rs)/n:4.2f} ends {dict(ends)} weed-ages {dict(sorted(dead.items()))}")
    for k, d in anim[side].items():
        if d["days"]:
            print(f"  {k:6s} n={d['n']} days={d['days']} fed%={100*d['fed']/d['days']:.0f} cared%={100*d['cared']/d['days']:.0f} units/day={d['units']/d['days']:.2f} coll/day={d['coll']/d['days']:.2f}")
