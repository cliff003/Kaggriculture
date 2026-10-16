r"""Categorize shadow-diff market differences per team (gold/front/shadow_<lineage>.json).
    .venv\Scripts\python.exe gold\front\diffcat.py [gold/front/shadow_cha22.json] [--team NAME --show 30]

Per team game: reorder-only steps; per item, units the team sold beyond the reference (extra) and short of it
(held), with the hour and step % 4 of the extra sells; wheat / fertilizer bought beyond the reference, split
into tick churn (buy at s % 4 == 0 and sell at s + 1) and the rest; hires, land, animals and seeds beyond or
short of the reference; placeholder orders.
"""
import argparse
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def agg(orders):
    c = collections.Counter()
    for o in orders:
        if not o:
            continue
        op = o[0]
        if op in ("SELL", "BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL") and len(o) >= 3:
            try:
                q = int(float(o[2]))
            except Exception:
                q = 0
            c[(op, o[1])] += q
        elif op in ("HIRE", "BUY_LAND"):
            c[(op, "")] += 1
        else:
            c[("OTHER", op)] += 1
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=os.path.join(HERE, "shadow_cha22.json"))
    ap.add_argument("--team")
    ap.add_argument("--show", type=int, default=0)
    a = ap.parse_args()
    games = [g for g in json.load(open(a.path, encoding="utf-8")) if "log" in g]
    by = collections.defaultdict(list)
    for g in games:
        by[(g["rank"], g["team"])].append(g)
    for (rank, team), gs in sorted(by.items()):
        if a.team and team != a.team:
            continue
        tot = collections.Counter()
        extra_h = collections.defaultdict(collections.Counter)
        n = len(gs)
        for g in gs:
            md = {t: (mr, ma) for t, mr, ma in g["log"]["market"]}
            buyw = {}
            for t, (mr, ma) in md.items():
                cr, ca = agg(mr), agg(ma)
                if cr == ca:
                    tot["reorder_steps"] += 1
                    continue
                for k in set(cr) | set(ca):
                    d = ca[k] - cr[k]
                    if d == 0:
                        continue
                    op, item = k
                    if op == "SELL":
                        if d > 0:
                            tot[f"sell+ {item}"] += d
                            extra_h[item][f"h{t % 24:02d}"] += d
                            extra_h[item][f"m4={t % 4}"] += d
                        else:
                            tot[f"sell- {item}"] += -d
                    elif op == "BUY_PRODUCT":
                        tot[f"buy{'+' if d > 0 else '-'} {item}"] += abs(d)
                        if item == "WHEAT" and d > 0:
                            buyw[t] = d
                    elif op in ("HIRE", "BUY_LAND"):
                        tot[f"{op}{'+' if d > 0 else '-'}"] += abs(d)
                    elif op in ("BUY_ANIMAL", "BUY_SEED"):
                        tot[f"{op}{'+' if d > 0 else '-'} {item}"] += abs(d)
                    else:
                        tot[f"other {item}"] += abs(d)
            for t, q in buyw.items():
                if t % 4 == 0 and t + 1 in md and agg(md[t + 1][1])[("SELL", "WHEAT")] - agg(md[t + 1][0])[("SELL", "WHEAT")] > 0:
                    tot["tick_cycles"] += 1
                    tot["tick_units"] += q
        us = [sum(g["log"]["unit_same"].values()) / max(1, sum(g["log"]["unit_n"].values())) for g in gs]
        fd = [g["log"]["first_unit_div"][0] if g["log"]["first_unit_div"] else None for g in gs]
        print(f"#{rank} {team}  games {n}  unit agree {', '.join(f'{u:.2f}' for u in us)}  first div {fd}")
        items = sorted((k for k in tot if k.startswith("sell")), key=lambda k: -tot[k])
        print("   sells: " + "; ".join(f"{k} {tot[k] / n:.0f}" for k in items))
        oth = sorted((k for k in tot if not k.startswith("sell")), key=lambda k: -tot[k])
        print("   other: " + "; ".join(f"{k} {tot[k] / n:.1f}" for k in oth))
        for item, h in sorted(extra_h.items(), key=lambda kv: -sum(v for k, v in kv[1].items() if k.startswith("h"))):
            hs = sorted(((k, v) for k, v in h.items() if k.startswith("h")), key=lambda kv: -kv[1])[:6]
            ms = sorted(((k, v) for k, v in h.items() if k.startswith("m4")))
            print(f"   extra {item}: top hours {hs}  by m4 {ms}")
        if a.show:
            g = gs[0]
            for t, mr, ma in g["log"]["market"][:a.show]:
                print(f"     s{t} d{t // 24}h{t % 24:02d} ref {mr}\n{'':20s}team {ma}")


if __name__ == "__main__":
    main()
