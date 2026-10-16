r"""Small CART trees (numpy only) for DSM's sell-vs-hold decision on premium goods: a ceiling for simple rules.

.venv\Scripts\python.exe research\dsm_sales\trees.py PRODUCT MODE MIN_STOCK DEPTH
MODE m1 = first turn after a tick (step % 4 == 1), h0 = hour 0. Accuracies printed are in-sample.
Features include DSM's own recent sales (own_sold24, since_own_sale), so the tree is descriptive, not causal.
"""
import sys

import numpy as np

from common import BASE, PI, load, per_step, town_demand

def gini(y):
    if len(y) == 0: return 0
    p = y.mean(); return 2 * p * (1 - p)

def best_split(X, y, names, min_leaf):
    best = None
    n = len(y)
    for k in range(X.shape[1]):
        x = X[:, k]; o = np.argsort(x, kind="stable"); xs = x[o]; ys = y[o]
        cs = np.cumsum(ys); tot = cs[-1]
        for i in range(min_leaf, n - min_leaf):
            if xs[i] == xs[i - 1]: continue
            nl = i; nr = n - i; pl = cs[i - 1] / nl; pr = (tot - cs[i - 1]) / nr
            g = (nl * 2 * pl * (1 - pl) + nr * 2 * pr * (1 - pr)) / n
            if best is None or g < best[0]:
                best = (g, k, (xs[i] + xs[i - 1]) / 2)
    return best

def grow(X, y, names, depth, min_leaf, pad=""):
    acc_leaf = max(y.mean(), 1 - y.mean())
    if depth == 0 or len(y) < 2 * min_leaf:
        print(f"{pad}leaf n={len(y)} P(sell)={y.mean():.2f}"); return
    b = best_split(X, y, names, min_leaf)
    if b is None or b[0] >= gini(y) - 1e-4:
        print(f"{pad}leaf n={len(y)} P(sell)={y.mean():.2f}"); return
    g, k, thr = b
    m = X[:, k] < thr
    print(f"{pad}{names[k]} < {thr:.2f}  (n={len(y)} P={y.mean():.2f})")
    grow(X[m], y[m], names, depth - 1, min_leaf, pad + "  |")
    print(f"{pad}{names[k]} >= {thr:.2f}")
    grow(X[~m], y[~m], names, depth - 1, min_leaf, pad + "  |")

def tree_acc(X, y, depth, min_leaf):
    # accuracy of the grown tree (in-sample)
    def rec(X, y, depth):
        if depth == 0 or len(y) < 2 * min_leaf:
            return max(y.sum(), len(y) - y.sum())
        b = best_split(X, y, None, min_leaf)
        if b is None or b[0] >= gini(y) - 1e-4:
            return max(y.sum(), len(y) - y.sum())
        g, k, thr = b; m = X[:, k] < thr
        return rec(X[m], y[m], depth - 1) + rec(X[~m], y[~m], depth - 1)
    return rec(X, y, depth) / len(y)

def build(item, mode, minav, games, acts):
    j = PI[item]
    animal = {"WOOL": "SHEEP", "MILK": "COW", "EGG": "GOOSE"}.get(item)
    rows = []; y = []; qv = []
    for g in games:
        me = g["meta"]["me"]; r = per_step(g, acts[g["meta"]["id"]])
        farmy = {}
        for d, tl in g["tiles"].items():
            farmy[d] = sum(t.get("yield_units", 0) for (x, yy, t) in tl if t.get("animal") == animal or t.get("crop") == item)
        last_sale = -99
        for t in range(24, 719):
            if r["sold"][t - 1, j] > 0: last_sale = t - 1
            if mode == "m1" and t % 4 != 1: continue
            if mode == "h0" and t % 24 != 0: continue
            S = g["shedpm"][me, t, j]
            if S < minav: continue
            p = g["mpx"][t, j]; inv = g["minv"][t, j]
            h = t % 24; d = t // 24
            f = [h, d, S, p / BASE[item], inv - 10000,
                 p - g["mpx"][t - 4, j], p - g["mpx"][t - 24, j], p - g["mpx"][t - h, j],
                 r["osold"][t - 4:t, j].sum(), r["sold"][t - 24:t, j].sum(), r["osold"][t - 24:t, j].sum(),
                 g["carried"][me, t, j], farmy.get(d, 0), town_demand(g["shops_by_day"][d], 4)[item],
                 t - last_sale, g["shed"][me, t].sum() + g["carried"][me, t].sum(), 719 - t,
                 (inv - g["minv"][t - 24, j])]
            rows.append(f); y.append(int(r["sold"][t, j] > 0)); qv.append(r["sold"][t, j])
    names = ["hour", "day", "S", "p/base", "inv-I0", "dp4", "dp24", "dp_since_h0", "opp_sold4", "own_sold24", "opp_sold24",
             "carried", "farm_yield_h0", "shop_demand", "since_own_sale", "shed+carried_total", "steps_left", "dinv24"]
    return np.array(rows, float), np.array(y), np.array(qv), names

if __name__ == "__main__":
    games, acts = load()
    item = sys.argv[1]; mode = sys.argv[2]; minav = int(sys.argv[3]); depth = int(sys.argv[4])
    X, y, q, names = build(item, mode, minav, games, acts)
    print(f"{item} {mode} S>={minav}: n={len(y)} P(sell)={y.mean():.3f}")
    grow(X, y, names, depth, 60)
    for d in (1, 2, 3, 4, 5):
        print("depth", d, "in-sample acc", round(tree_acc(X, y, d, 60), 3))
