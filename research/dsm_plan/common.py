"""Shared helpers for the DSM plan analysis scripts (read the cache built by replay.py)."""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from replay import load_games  # noqa: E402,F401

CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["COW", "SHEEP", "GOOSE"]
TYPES = ["COW", "SHEEP", "GOOSE", "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
SHOPS = ["BAKERY", "BRUNCH_SPOT", "FARMERS_MARKET", "ICE_CREAM_SHOP", "PET_CAFE", "PIZZA_SHOP", "SMOOTHIE_SHOP", "YARN_STORE"]
SHOP_AB = {"BAKERY": "BAK", "BRUNCH_SPOT": "BRU", "FARMERS_MARKET": "FM", "ICE_CREAM_SHOP": "ICE", "PET_CAFE": "PET",
           "PIZZA_SHOP": "PIZ", "SMOOTHIE_SHOP": "SMO", "YARN_STORE": "YARN"}
LABEL = {"WHEAT": "w", "CARROT": "c", "TOMATO": "t", "STRAWBERRY": "s", "MELON": "m", "COW": "C", "SHEEP": "S", "GOOSE": "G"}


def kind(t):
    """Tile type name: EMPTY, LOCKED, WEED, COOP/PASTURE (empty structure), COW/SHEEP/GOOSE, crop name."""
    if t is None:
        return "EMPTY"
    if t == "L":
        return "LOCKED"
    if t[0] == "W":
        return "WEED"
    if t[0] == "S":
        return t[1]
    if t[0] == "A":
        return t[2]
    return t[1]


def label(t):
    k = kind(t)
    return {"EMPTY": ".", "LOCKED": "#", "WEED": "x", "COOP": "o", "PASTURE": "p"}.get(k, LABEL.get(k, "?"))


def counts(grid):
    c = collections.Counter()
    for row in grid:
        for t in row:
            c[kind(t)] += 1
    return c


def shops_at_day(g, day):
    """Shops unlocked at the START of `day` (shop k unlocks at the end of day 3k+2)."""
    return g["shops"][:min(8, day // 3)]


def eod_grid(g, day):
    return g["eod"][day]["tiles"][0]


def quadrant(x, y):
    return ("N" if y < 5 else "S") + ("W" if x < 5 else "E")


def table(headers, rows):
    out = ["| " + " | ".join(str(h) for h in headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def mkt_of(g, side=0):
    return [m for m in g["mkt"] if m[1] == side]


def pct(a, b):
    return f"{100.0 * a / b:.0f}%" if b else "-"


def median(xs):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def quantiles(xs, qs=(0.1, 0.5, 0.9)):
    xs = sorted(xs)
    if not xs:
        return [float("nan")] * len(qs)
    return [xs[min(len(xs) - 1, int(q * (len(xs) - 1) + 0.5))] for q in qs]
