r"""Lineage and market-habit table of the top-N teams from harvested records (gold/front/front_*.jsonl.gz).
    .venv\Scripts\python.exe gold\front\classify.py [--out gold/front/classify.json]

Lineage: the first 12 steps of unit-op names (farmer + hands) compared with cha22's opening (our seat in
data/games/live_v7b.jsonl.gz) and DSM's (gold/top30/top30.jsonl.gz); other openings are grouped by exact signature.
Market habits per team (all its harvested games): tick churn cycles (BUY_PRODUCT WHEAT >= 10 at s % 4 == 0 and
SELL WHEAT at s + 1) with the buy slot, share of steps whose first order is a SELL, placeholder orders ([] / NOOP /
qty 0) per game, fertilizer bought per game, hires per game, mean final money and margin.
"""
import argparse
import collections
import glob
import gzip
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def sig(acts, T=12):
    out = []
    for t in range(1, T + 1):
        a = (acts[t] if t < len(acts) else None) or {}
        u = [a.get("farmer")] + list(a.get("hands") or [])
        out.append("|".join(str(x[0] if isinstance(x, list) and x else x) for x in u))
    return " / ".join(out)


def load(pattern):
    out = []
    for p in sorted(glob.glob(pattern)):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            out += [json.loads(l) for l in f if l.strip()]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "classify.json"))
    args = ap.parse_args()
    pick = json.load(open(os.path.join(HERE, "pick_eps.json"), encoding="utf-8"))
    by_name = {r[1]: r for r in pick}
    cha = load(os.path.join(ROOT, "data", "games", "live_v7b.jsonl.gz"))[:5]
    cha_sig = collections.Counter(sig(r["acts"][r["teams"].index("42")]) for r in cha).most_common(1)[0][0]
    dsm = [r for r in load(os.path.join(ROOT, "gold", "top30", "top30.jsonl.gz")) if "DSM" in r["teams"]]
    dsm_sig = collections.Counter(sig(r["acts"][r["teams"].index("DSM")]) for r in dsm).most_common(1)[0][0]
    recs = load(os.path.join(HERE, "front_*.jsonl.gz"))
    seen = set()
    stats = collections.defaultdict(lambda: collections.Counter())
    sigs = collections.defaultdict(collections.Counter)
    for r in recs:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        for seat in range(2):
            name = r["teams"][seat]
            if name not in by_name:
                continue
            acts = r["acts"][seat]
            s = sig(acts)
            lab = "cha22" if s == cha_sig else ("DSM" if s == dsm_sig else "x" + hashlib.md5(s.encode()).hexdigest()[:6])
            sigs[name][lab] += 1
            st = stats[name]
            st["games"] += 1
            st["money"] += r["rewards"][seat] or 0
            st["margin"] += (r["rewards"][seat] or 0) - (r["rewards"][1 - seat] or 0)
            st["wins"] += (r["rewards"][seat] or 0) > (r["rewards"][1 - seat] or 0)
            for t in range(719):
                a = (acts[t + 1] if t + 1 < len(acts) else None) or {}
                m = a.get("market") or []
                if m and isinstance(m[0], list) and m[0] and m[0][0] == "SELL":
                    st["sell_first"] += 1
                if m:
                    st["steps_with_orders"] += 1
                for i, o in enumerate(m):
                    if not isinstance(o, list) or not o or o[0] in ("NOOP", "PASS"):
                        st["placeholder"] += 1
                        continue
                    if len(o) >= 3:
                        try:
                            q = int(o[2])
                        except Exception:
                            q = 0
                        if q <= 0:
                            st["placeholder"] += 1
                        if o[0] == "BUY_PRODUCT" and o[1] == "FERTILIZER":
                            st["fert_bought"] += q
                        if o[0] == "BUY_PRODUCT" and o[1] == "WHEAT" and q >= 10 and t % 4 == 0 and t >= 24:
                            nxt = (acts[t + 2] if t + 2 < len(acts) else None) or {}
                            if any(isinstance(x, list) and len(x) >= 3 and x[0] == "SELL" and x[1] == "WHEAT"
                                   for x in (nxt.get("market") or [])):
                                st["tick_cycles"] += 1
                                st["tick_units"] += q
                                st["tick_slot_sum"] += i
                    if o[0] == "HIRE":
                        st["hires"] += 1
    out = []
    for r in pick:
        name = r[1]
        st = stats.get(name)
        if not st:
            out.append({"rank": r[0], "name": name, "score": r[4], "games": 0})
            continue
        n = st["games"]
        lab = sigs[name].most_common(1)[0][0]
        out.append({"rank": r[0], "name": name, "score": r[4], "games": n, "lineage": lab,
                    "money": round(st["money"] / n), "margin": round(st["margin"] / n), "wins": st["wins"],
                    "tick_cycles": round(st["tick_cycles"] / n, 1), "tick_units": round(st["tick_units"] / n),
                    "tick_slot": round(st["tick_slot_sum"] / max(1, st["tick_cycles"]), 1),
                    "sell_first": round(st["sell_first"] / max(1, st["steps_with_orders"]), 2),
                    "placeholder": round(st["placeholder"] / n), "fert_bought": round(st["fert_bought"] / n),
                    "hires": round(st["hires"] / n)})
    json.dump(out, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    lin = collections.Counter(x.get("lineage") for x in out if x.get("games"))
    print("lineages:", lin.most_common())
    print(f"{'rk':>3} {'team':22s} {'score':>6} {'g':>2} {'lineage':8s} {'money':>7} {'margin':>7} {'tick c/u/slot':>15} "
          f"{'sell1st':>7} {'ph':>4} {'fertB':>5} {'hire':>4}")
    for x in out:
        if not x.get("games"):
            print(f"{x['rank']:3d} {x['name'][:22]:22s} {x['score']:6.0f}  no games")
            continue
        print(f"{x['rank']:3d} {x['name'][:22]:22s} {x['score']:6.0f} {x['games']:2d} {x['lineage']:8s} {x['money']:7d} "
              f"{x['margin']:+7d} {x['tick_cycles']:5.1f}/{x['tick_units']:5d}/{x['tick_slot']:3.1f} {x['sell_first']:7.2f} "
              f"{x['placeholder']:4d} {x['fert_bought']:5d} {x['hires']:4d}")


if __name__ == "__main__":
    main()
