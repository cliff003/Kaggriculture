r"""Same-shop-pair action identity per day for one team's recorded games.

tapeid.py GAMES.jsonl.gz TEAM
For every two games of TEAM that share the first two shops, the share of steps in each day whose full
action (farmer, hands, market) is identical. High identity after the opening means tape-like play.
"""
import collections
import gzip
import itertools
import json
import sys


def load(path):
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for l in f:
            if l.strip():
                try:
                    out.append(json.loads(l))
                except Exception:
                    break
    return out


def main():
    path, team = sys.argv[1], sys.argv[2]
    recs = [r for r in load(path) if team in r["teams"]]
    by = collections.defaultdict(list)
    for r in recs:
        me = r["teams"].index(team)
        by[tuple(r["shops"][:2])].append((r, me))
    days = collections.defaultdict(list)
    cross = collections.defaultdict(list)
    npairs = 0
    for pair, lst in by.items():
        for (a, ma), (b, mb) in itertools.combinations(lst, 2):
            npairs += 1
            A, B = a["acts"][ma], b["acts"][mb]
            for d in range(30):
                s = [t for t in range(d * 24 + 1, d * 24 + 25) if t < len(A) and t < len(B)]
                if s:
                    days[d].append(sum(json.dumps(A[t], sort_keys=True) == json.dumps(B[t], sort_keys=True) for t in s) / len(s))
    allr = recs
    for (a, b) in itertools.islice(itertools.combinations(allr, 2), 400):
        ma, mb = a["teams"].index(team), b["teams"].index(team)
        if tuple(a["shops"][:2]) == tuple(b["shops"][:2]):
            continue
        A, B = a["acts"][ma], b["acts"][mb]
        for d in range(30):
            s = [t for t in range(d * 24 + 1, d * 24 + 25) if t < len(A) and t < len(B)]
            if s:
                cross[d].append(sum(json.dumps(A[t], sort_keys=True) == json.dumps(B[t], sort_keys=True) for t in s) / len(s))
    print(f"{team}: {len(recs)} games, {len(by)} pairs, {npairs} same-pair game pairs")
    print("day same-pair cross-pair")
    for d in range(30):
        sp = sum(days[d]) / len(days[d]) if days[d] else float('nan')
        cp = sum(cross[d]) / len(cross[d]) if cross[d] else float('nan')
        print(f"{d:3d} {sp:9.2f} {cp:9.2f}")


if __name__ == "__main__":
    main()
