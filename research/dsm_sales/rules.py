r"""Fit and score simple sell rules against DSM's per-turn sell quantities.

.venv\Scripts\python.exe research\dsm_sales\rules.py [PRODUCT ...]

Decision point = (game, step t, product) where DSM has stock S > 0 after its own unit drops of that step
(shed right before the market). Target q = units DSM actually sold at t (0 = hold).
Every rule maps the observation at t (plus DSM's own past sales) to a predicted q_hat <= S.
Parameters are fitted on the even-indexed games and scored on the odd-indexed games, then the other way
round; the tables report the pooled out-of-sample scores.

Metrics: exact = share of decision points with q_hat == q; sell/hold = share with (q_hat > 0) == (q > 0);
exact|sell = exact share among points where DSM sold; corr = Pearson(q_hat, q); vol = sum q_hat / sum q.
"""
import collections
import itertools
import sys

import numpy as np

from common import BASE, PI, PRODUCTS, SHOPS, load, per_step, price, town_demand

GAMES, ACTS = load()
PER = [per_step(g, ACTS[g["meta"]["id"]]) for g in GAMES]
INV_LO, INV_HI = 8000, 12500
PTAB = {x: np.array([price(x, i) for i in range(INV_LO, INV_HI)], np.int32) for x in PRODUCTS}


def shop_rate(shops, x):
    n = 0
    for s in shops:
        prods = SHOPS[s]
        if x in prods:
            n += 2 if len(prods) == 1 else 1
    return n


def points(x):
    """Feature arrays for every decision point of product x."""
    j = PI[x]
    F = collections.defaultdict(list)
    for gi, (g, r) in enumerate(zip(GAMES, PER)):
        me = g["meta"]["me"]
        last_sale = -1
        run = 0
        for t in range(719):
            S = int(g["shedpm"][me, t, j])
            if S > 0:
                d, h = t // 24, t % 24
                shops = g["shops_by_day"][d]
                lt = t - 4 if t % 4 == 0 else t - t % 4   # last consumption tick strictly before this market
                F["g"].append(gi); F["t"].append(t); F["h"].append(h); F["m4"].append(t % 4); F["day"].append(d)
                F["S"].append(S); F["inv"].append(int(g["minv"][t, j])); F["p"].append(int(g["mpx"][t, j]))
                F["q"].append(int(r["sold"][t, j]))
                F["c_last"].append(town_demand(g["shops_by_day"][max(0, lt) // 24], lt)[x] if lt >= 0 else 0)
                F["rate"].append(shop_rate(shops, x))
                F["post_last"].append(int(g["mpost"][last_sale, j]) if last_sale >= 0 else -1)
                F["first_px_last"].append(int(r["first_px"][last_sale, j]) if last_sale >= 0 else -1)
                F["last_px_last"].append(int(r["last_px"][last_sale, j]) if last_sale >= 0 else -1)
                F["pmax24"].append(int(g["mpx"][max(0, t - 24):t + 1, j].max()))
                F["pmean24"].append(float(g["mpx"][max(0, t - 24):t + 1, j].mean()))
                F["since"].append(t - last_sale if last_sale >= 0 else 999)
                F["own24"].append(int(r["sold"][max(0, t - 24):t, j].sum()))
            if r["sold"][t, j] > 0:
                last_sale = t
    return {k: np.array(v) for k, v in F.items()}


def units_above(x, inv, S, thr):
    """Number of units (<= S) DSM could sell alone, from inventory inv, while the unit price stays >= thr."""
    out = np.zeros(len(inv), np.int32)
    tab = PTAB[x]
    for i in range(len(inv)):
        base = inv[i] - INV_LO
        k = 0
        s = S[i]
        th = thr[i]
        while k < s and tab[min(base + k, len(tab) - 1)] >= th:
            k += 1
        out[i] = k
    return out


def agg_corr(qh, q, key):
    ks, inv = np.unique(key, return_inverse=True)
    a = np.bincount(inv, weights=qh)
    b = np.bincount(inv, weights=q)
    return np.corrcoef(a, b)[0, 1] if a.std() > 0 and b.std() > 0 else float("nan")


def score(qh, q, P=None):
    qh = np.minimum(qh, 10 ** 6)
    exact = np.mean(qh == q)
    sh = np.mean((qh > 0) == (q > 0))
    m = q > 0
    ex_sell = np.mean(qh[m] == q[m]) if m.any() else float("nan")
    c = np.corrcoef(qh, q)[0, 1] if qh.std() > 0 and q.std() > 0 else float("nan")
    vol = qh.sum() / max(1, q.sum())
    cw = agg_corr(qh, q, P["g"] * 1000 + P["t"] // 4) if P is not None else float("nan")
    cd = agg_corr(qh, q, P["g"] * 1000 + P["t"] // 24) if P is not None else float("nan")
    return exact, sh, ex_sell, c, vol, cw, cd


# ---------------------------------------------------------------- rules (fit on a mask, predict on all)
def gate_hours(P, m, thr=0.5):
    hs = set()
    for h in range(24):
        k = m & (P["h"] == h)
        if k.sum() and np.mean(P["q"][k] > 0) >= thr:
            hs.add(h)
    return hs


def in_gate(P, hs):
    return np.isin(P["h"], sorted(hs)) if hs else np.zeros(len(P["h"]), bool)


def rule_all(P, x, m):
    return lambda P: P["S"].copy(), {}


def rule_hold(P, x, m):
    return lambda P: np.zeros_like(P["S"]), {}


def rule_gate_all(P, x, m):
    hs = gate_hours(P, m)
    return lambda P: np.where(in_gate(P, hs), P["S"], 0), {"gate": sorted(hs)}


def rule_gate_lot(P, x, m):
    hs = gate_hours(P, m)
    L = {}
    for h in hs:
        k = m & (P["h"] == h) & (P["q"] > 0)
        L[h] = int(np.median(P["q"][k])) if k.any() else 1
    def f(P):
        lot = np.array([L.get(h, 0) for h in P["h"]])
        return np.where(in_gate(P, hs), np.minimum(P["S"], lot), 0)
    return f, {"gate": sorted(hs), "lot": L}


def rule_gate_fixed(P, x, m):
    hs = gate_hours(P, m)
    best = None
    for L in range(1, 16):
        qh = np.where(in_gate(P, hs), np.minimum(P["S"], L), 0)
        e = np.mean(qh[m] == P["q"][m])
        if best is None or e > best[0]:
            best = (e, L)
    L = best[1]
    return lambda P: np.where(in_gate(P, hs), np.minimum(P["S"], L), 0), {"gate": sorted(hs), "L": L}


def rule_gate_frac(P, x, m):
    hs = gate_hours(P, m)
    best = None
    for f in np.arange(0.1, 1.01, 0.05):
        qh = np.where(in_gate(P, hs), np.ceil(f * P["S"]).astype(int), 0)
        e = np.mean(qh[m] == P["q"][m])
        if best is None or e > best[0]:
            best = (e, f)
    f = best[1]
    return lambda P: np.where(in_gate(P, hs), np.ceil(f * P["S"]).astype(int), 0), {"gate": sorted(hs), "f": round(f, 2)}


def rule_pace(P, x, m):
    """At gate hours sell ceil(S / (gate hours left today + k)), capped at Lmax."""
    hs = gate_hours(P, m)
    hsl = sorted(hs)
    rem = np.array([sum(1 for g in hsl if g >= h) for h in range(24)])
    best = None
    for k in range(0, 8):
        for Lmax in (1, 2, 3, 4, 6, 8, 11, 13, 100):
            qh = np.where(in_gate(P, hs), np.minimum(np.minimum(P["S"], Lmax),
                                                     np.ceil(P["S"] / np.maximum(1, rem[P["h"]] + k)).astype(int)), 0)
            e = np.mean(qh[m] == P["q"][m])
            if best is None or e > best[0]:
                best = (e, k, Lmax)
    _, k, Lmax = best
    def f(P):
        return np.where(in_gate(P, hs), np.minimum(np.minimum(P["S"], Lmax),
                                                   np.ceil(P["S"] / np.maximum(1, rem[P["h"]] + k)).astype(int)), 0)
    return f, {"gate": hsl, "k": k, "Lmax": Lmax}


def rule_demand_tick(P, x, m):
    """Sell what the town consumed at the last tick (only on the first turn after a tick, m4==1)."""
    def f(P):
        return np.where(P["m4"] == 1, np.minimum(P["S"], P["c_last"]), 0)
    return f, {}


def rule_demand_half(P, x, m):
    def f(P):
        return np.where(P["m4"] == 1, np.minimum(P["S"], np.ceil(P["c_last"] / 2).astype(int)), 0)
    return f, {}


def rule_restore(P, x, m):
    """Sell back to the market inventory left after DSM's previous sale (demand-preserving target)."""
    def f(P):
        tgt = np.where(P["post_last"] >= 0, P["post_last"] - P["inv"], P["S"])
        return np.clip(tgt, 0, P["S"])
    return f, {}


def rule_price_abs(P, x, m):
    best = None
    for a in np.arange(0.05, 2.01, 0.05):
        thr = np.full(len(P["S"]), int(round(a * BASE[x])))
        qh = units_above(x, P["inv"][m], P["S"][m], thr[m])
        e = np.mean(qh == P["q"][m])
        if best is None or e > best[0]:
            best = (e, a)
    a = best[1]
    return lambda P: units_above(x, P["inv"], P["S"], np.full(len(P["S"]), int(round(a * BASE[x])))), {"alpha": round(a, 2)}


def rule_price_abs_gate(P, x, m):
    hs = gate_hours(P, m, 0.3)
    g = in_gate(P, hs)
    best = None
    for a in np.arange(0.05, 2.01, 0.05):
        thr = np.full(len(P["S"]), int(round(a * BASE[x])))
        qh = np.where(g[m], units_above(x, P["inv"][m], P["S"][m], thr[m]), 0)
        e = np.mean(qh == P["q"][m])
        if best is None or e > best[0]:
            best = (e, a)
    a = best[1]
    def f(P):
        return np.where(in_gate(P, hs), units_above(x, P["inv"], P["S"], np.full(len(P["S"]), int(round(a * BASE[x])))), 0)
    return f, {"gate": sorted(hs), "alpha": round(a, 2)}


def rule_price_max24(P, x, m):
    """Sell while price >= (1 - d) * max observed price over the last 24 steps."""
    best = None
    for dlt in (0.0, 0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.2, 0.3):
        thr = np.ceil((1 - dlt) * P["pmax24"]).astype(int)
        qh = units_above(x, P["inv"][m], P["S"][m], thr[m])
        e = np.mean(qh == P["q"][m])
        if best is None or e > best[0]:
            best = (e, dlt)
    dlt = best[1]
    return lambda P: units_above(x, P["inv"], P["S"], np.ceil((1 - dlt) * P["pmax24"]).astype(int)), {"d": dlt}


def rule_price_last(P, x, m):
    """Sell while price >= DSM's last sale price (its last unit) minus D dollars."""
    best = None
    for D in (-4, -2, 0, 1, 2, 3, 5, 8, 12, 20):
        thr = np.where(P["last_px_last"] > 0, P["last_px_last"] - D, 0)
        qh = units_above(x, P["inv"][m], P["S"][m], thr[m])
        e = np.mean(qh == P["q"][m])
        if best is None or e > best[0]:
            best = (e, D)
    D = best[1]
    return lambda P: units_above(x, P["inv"], P["S"], np.where(P["last_px_last"] > 0, P["last_px_last"] - D, 0)), {"D": D}


def rule_impact_gate(P, x, m):
    """At gate hours sell while the unit price stays >= current price - D (price-impact cap)."""
    hs = gate_hours(P, m)
    g = in_gate(P, hs)
    best = None
    for D in (0, 1, 2, 3, 4, 5, 6, 8, 10, 15, 25):
        qh = np.where(g[m], units_above(x, P["inv"][m], P["S"][m], P["p"][m] - D), 0)
        e = np.mean(qh == P["q"][m])
        if best is None or e > best[0]:
            best = (e, D)
    D = best[1]
    return lambda P: np.where(in_gate(P, hs), units_above(x, P["inv"], P["S"], P["p"] - D), 0), {"gate": sorted(hs), "D": D}


RULES = [("hold (q=0)", rule_hold), ("sell all now", rule_all), ("hour gate, sell all", rule_gate_all),
         ("hour gate, fixed lot L", rule_gate_fixed), ("hour gate, median lot per hour", rule_gate_lot),
         ("hour gate, ceil(f*S)", rule_gate_frac), ("hour gate, pacing S/(slots left+k)", rule_pace),
         ("demand: last tick's consumption at m4=1", rule_demand_tick),
         ("demand/2 at m4=1", rule_demand_half), ("restore inventory after own last sale", rule_restore),
         ("price >= a*base (every turn)", rule_price_abs), ("hour gate + price >= a*base", rule_price_abs_gate),
         ("price >= (1-d)*max price 24 steps", rule_price_max24), ("price >= own last sale price - D", rule_price_last),
         ("hour gate + impact cap: price >= p0 - D", rule_impact_gate)]


def evaluate(x, rules=RULES):
    P = points(x)
    ng = P["g"]
    folds = [(ng % 2 == 0), (ng % 2 == 1)]
    res = []
    for name, rule in rules:
        qh = np.zeros_like(P["q"])
        params = []
        for tr, te in ((folds[0], folds[1]), (folds[1], folds[0])):
            f, prm = rule(P, x, tr)
            pred = f(P)
            qh[te] = np.minimum(pred[te], P["S"][te])
            params.append(prm)
        res.append((name, score(qh, P["q"], P), params))
    return P, res


def main():
    items = sys.argv[1:] or PRODUCTS
    for x in items:
        P, res = evaluate(x)
        print(f"\n### {x}: {len(P['q'])} decision points, DSM sold on {np.mean(P['q'] > 0):.1%} of them\n")
        print("| rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume | params (fold A / fold B) |")
        print("|---|---|---|---|---|---|---|---|---|")
        for name, (ex, sh, exs, c, vol, cw, cd), params in res:
            ps = " / ".join(", ".join(f"{k}={v}" for k, v in p.items() if k != "lot") for p in params)
            print(f"| {name} | {ex:.1%} | {sh:.1%} | {exs:.1%} | {c:.2f} | {cw:.2f} | {cd:.2f} | {vol:.2f} | {ps} |")


if __name__ == "__main__":
    main()
