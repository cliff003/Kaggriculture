r"""Composite per-product sell rules assembled from the components found in analyze.py / rules.py.

.venv\Scripts\python.exe research\dsm_sales\composite.py

The few parameters (hours, lot sizes, thresholds) were chosen by looking at all 92 games, so the scores are
in-sample; the cross-validated scores of the single-component rule families are in rules.py.
Scored on the same decision points as rules.py (DSM holds S > 0 after its own unit drops of the step).
"""
import numpy as np

from common import BASE, PI, PRODUCTS, SHOPS
from rules import GAMES, PER, points, score


def extra_features(P, x):
    """Adds fresh (units dropped by DSM's own units this step), n_animals, dinv24 and c_last."""
    j = PI[x]
    fresh = np.zeros(len(P["q"]), np.int32)
    nan = np.zeros(len(P["q"]), np.int32)
    dinv24 = np.zeros(len(P["q"]), np.int32)
    for i, (gi, t) in enumerate(zip(P["g"], P["t"])):
        g = GAMES[gi]
        me = g["meta"]["me"]
        fresh[i] = max(0, int(g["shedpm"][me, t, j]) - int(g["shed"][me, t, j]))
        nan[i] = sum(1 for (_, _, tl) in g["tiles"][t // 24] if tl.get("animal"))
        dinv24[i] = int(g["minv"][t, j]) - int(g["minv"][max(0, t - 24), j])
    P["fresh"], P["nan"], P["dinv24"] = fresh, nan, dinv24
    return P


def comp_melon(P):
    return P["S"].copy()


def comp_gate22(P):
    return np.where(np.isin(P["h"], [22, 23]) | (P["t"] == 718), P["S"], 0)


def comp_wheat(P):
    q = np.where(np.isin(P["h"], [22, 23]) | (P["t"] == 718), P["S"], 0)
    morning = np.isin(P["h"], [0, 1, 2])
    reserve = np.where(P["h"] == 0, P["nan"], np.where(P["h"] == 1, (P["nan"] * 2) // 3, P["nan"] // 3))
    return np.where(morning, np.maximum(0, P["S"] - reserve), q)


def comp_fert(P):
    return np.where(np.isin(P["h"], [0, 2, 3, 7, 22, 23]) & (P["p"] >= 0.4 * BASE["FERTILIZER"]), P["S"], 0)


def comp_strawberry(P):
    x = "STRAWBERRY"
    h, S = P["h"], P["S"]
    q = np.zeros_like(S)
    # hour 0: dump a lot when the market has been flooding (inventory up >= 9 in 24 steps) and price >= 0.7 base
    h0 = (h == 0) & (P["dinv24"] >= 9) & (P["p"] >= 0.7 * BASE[x]) & (S >= 9)
    lot0 = np.where(P["p"] >= 1.3 * BASE[x], 11, 6)
    q = np.where(h0, np.minimum(S, lot0), q)
    # first turn after each tick from hour 5 on: lots of 2
    tick = (P["m4"] == 1) & (h >= 5)
    q = np.where(tick, np.minimum(S, 2), q)
    # a unit dropped fresh berries at another hour: sell them, at most 6
    other = (P["m4"] != 1) & (h != 0) & (P["fresh"] > 0)
    q = np.where(other, np.minimum(P["fresh"], 6), q)
    return q


def comp_milk(P):
    x = "MILK"
    h, S = P["h"], P["S"]
    q = np.zeros_like(S)
    tick = (P["m4"] == 1) & np.isin(h, [9, 13, 17, 21]) & (P["p"] >= 0.24 * BASE[x])
    q = np.where(tick, np.minimum(S, 2), q)
    q = np.where((P["fresh"] > 0) & (P["p"] >= 0.24 * BASE[x]), np.maximum(q, P["fresh"]), q)
    return np.minimum(q, S)


def comp_wool(P):
    h, S = P["h"], P["S"]
    q = np.where(P["m4"] == 1, np.minimum(S, np.ceil(P["c_last"] / 2).astype(int)), 0)
    q = np.where(P["fresh"] > 0, np.maximum(q, P["fresh"]), q)
    return np.minimum(q, S)


COMPOSITE = {
    "WHEAT": ("hour 22-23: sell all; hours 0/1/2: sell stock above a feed reserve of n_animals, 2/3 n, 1/3 n", comp_wheat),
    "CARROT": ("hour 22-23: sell all, else hold", comp_gate22),
    "TOMATO": ("hour 22-23: sell all, else hold", comp_gate22),
    "STRAWBERRY": ("h0: min(S, 11 if p>=1.3 base else 6) when market inventory rose >=9 in 24 steps, p>=0.7 base, S>=9; "
                   "m4==1 from h5: min(S,2); fresh drop at other hours: min(fresh,6)", comp_strawberry),
    "MELON": ("sell everything as soon as it is in the shed", comp_melon),
    "EGG": ("hour 22-23: sell all, else hold", comp_gate22),
    "MILK": ("m4==1 at h9/13/17/21: min(S,2); a fresh drop is sold in full; nothing below 0.24 base", comp_milk),
    "WOOL": ("m4==1: min(S, ceil(last tick consumption / 2)); a fresh drop is sold in full", comp_wool),
    "FERTILIZER": ("hours 0,2,3,7,22,23: sell all while price >= 0.4 base", comp_fert),
}


def with_morning_room(f):
    """Variant: also sell everything at hour 0 when the shed (before the market) holds >= 90 items."""
    def g(P):
        return np.where((P["h"] == 0) & (P["shed_total"] >= 90), P["S"], f(P))
    return g


def main():
    print("| product | composite rule | exact | sell/hold | exact on sell turns | corr turn | corr 4-step window | corr day | volume |")
    print("|---|---|---|---|---|---|---|---|---|")
    for x in PRODUCTS:
        P = extra_features(points(x), x)
        P["shed_total"] = np.array([int(GAMES[g]["shedpm"][GAMES[g]["meta"]["me"], t].sum()) for g, t in zip(P["g"], P["t"])])
        variants = [COMPOSITE[x]]
        if x in ("CARROT", "TOMATO", "EGG"):
            variants.append((COMPOSITE[x][0] + " + hour 0: sell all when the shed holds >= 90 items",
                             with_morning_room(COMPOSITE[x][1])))
        for desc, f in variants:
            qh = np.minimum(f(P), P["S"])
            ex, sh, exs, c, vol, cw, cd = score(qh, P["q"], P)
            print(f"| {x} | {desc} | {ex:.1%} | {sh:.1%} | {exs:.1%} | {c:.2f} | {cw:.2f} | {cd:.2f} | {vol:.2f} |")
    print()
    print("Stability check: the same composite rules scored separately on even- and odd-indexed games\n")
    print("| product | exact even / odd | sell/hold even / odd | corr turn even / odd | corr day even / odd |")
    print("|---|---|---|---|---|")
    for x in PRODUCTS:
        P = extra_features(points(x), x)
        qh = np.minimum(COMPOSITE[x][1](P), P["S"])
        out = []
        for par in (0, 1):
            m = P["g"] % 2 == par
            out.append(score(qh[m], P["q"][m], {k: v[m] for k, v in P.items()}))
        print(f"| {x} | {out[0][0]:.1%} / {out[1][0]:.1%} | {out[0][1]:.1%} / {out[1][1]:.1%} | "
              f"{out[0][3]:.2f} / {out[1][3]:.2f} | {out[0][6]:.2f} / {out[1][6]:.2f} |")


if __name__ == "__main__":
    main()
