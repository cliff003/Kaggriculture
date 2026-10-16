r"""Classify the opponents of harvested games by how long their unit actions mirror ours.

.venv\Scripts\python.exe tools\famcheck.py GAMES.jsonl.gz TEAM [--list]

cha22-family agents share one opening route, and our layers only touch market orders, so the step at
which the opponent's farmer/hand actions first differ from ours tells the family apart:
  clone    identical to the end (the same tape and layers as ours)
  family   identical through day 5 (step 144, the shared opening route), different later
  other    different before step 144
Prints W/L/T, mean margin and mean pre-game opponent rating per class.
"""
import argparse
import collections
import gzip
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg


def units(a):
    if not isinstance(a, dict):
        return None
    return json.dumps([a.get("farmer"), a.get("hands") or []], separators=(",", ":"))


def mirror_len(rec, side):
    mine, theirs = rec["acts"][side][1:], rec["acts"][1 - side][1:]
    for t in range(min(len(mine), len(theirs))):
        if units(mine[t]) != units(theirs[t]):
            return t
    return min(len(mine), len(theirs))


def klass(m):
    return "clone" if m >= 700 else ("family" if m >= 144 else "other")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games")
    ap.add_argument("team")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    games = [json.loads(l) for l in gzip.open(a.games, "rt", encoding="utf-8") if l.strip()]
    per = collections.defaultdict(list)
    for g in games:
        if a.team not in g["teams"]:
            continue
        side = g["teams"].index(a.team)
        m = mirror_len(g, side)
        margin = g["rewards"][side] - g["rewards"][1 - side]
        opp_score = (g.get("scores") or [None, None])[1 - side]
        per[klass(m)].append((margin, opp_score, m, g["teams"][1 - side], g["id"]))
        if a.list:
            print(f"{g['id']} {klass(m):6s} mirror {m:3d}  {margin:+8.0f}  opp {g['teams'][1 - side]}")
    rows = []
    n = sum(len(v) for v in per.values())
    for k in ("clone", "family", "other"):
        v = per.get(k, [])
        if not v:
            rows.append([k, 0, "", "", "", ""])
            continue
        w = sum(1 for x in v if x[0] > 0)
        l = sum(1 for x in v if x[0] < 0)
        t = len(v) - w - l
        sc = [x[1] for x in v if x[1] is not None]
        rows.append([k, f"{len(v)} ({len(v) / n:.0%})", f"{w}/{l}/{t}", f"{(w + 0.5 * t) / len(v):.0%}",
                     f"{statistics.mean(x[0] for x in v):+.0f}", f"{statistics.mean(sc):.0f}" if sc else ""])
    kg.table(["对手类别", "局数(占比)", "胜/负/平", "得分率", "平均差距", "对手赛前分均值"], rows)


if __name__ == "__main__":
    main()
