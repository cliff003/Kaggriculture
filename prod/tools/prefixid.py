r"""Farmer/hands/market identity per day for game pairs sharing the first K unlocked shops (K=2..5).

prefixid.py GAMES.jsonl.gz TEAM [--days 3-24]
Shops unlock at the start of days 3,6,9,...; an agent that only depends on the shop prefix shows identity
1.0 until the day the (K+1)th shop unlocks.
"""
import collections
import gzip
import itertools
import json
import sys


def main():
    path, team = sys.argv[1], sys.argv[2]
    recs = [json.loads(l) for l in gzip.open(path, "rt", encoding="utf-8") if l.strip()]
    recs = [r for r in recs if team in r["teams"]]
    print(f"{team}: {len(recs)} games")
    for K in (1, 2, 3, 4, 5):
        by = collections.defaultdict(list)
        for r in recs:
            by[tuple(r["shops"][:K])].append((r, r["teams"].index(team)))
        rows = collections.defaultdict(list)
        n = 0
        for lst in by.values():
            for (a, ma), (b, mb) in itertools.combinations(lst, 2):
                n += 1
                A, B = a["acts"][ma], b["acts"][mb]
                for d in range(3, 25):
                    s = [t for t in range(d * 24 + 1, d * 24 + 25) if t < len(A) and t < len(B)]
                    if s:
                        rows[d].append(sum(json.dumps(A[t], sort_keys=True) == json.dumps(B[t], sort_keys=True) for t in s) / len(s))
        if n:
            print(f"K={K} ({n:3d} pairs) d3..24: " + " ".join(f"{sum(rows[d]) / len(rows[d]):.2f}" for d in range(3, 25)))


if __name__ == "__main__":
    main()
