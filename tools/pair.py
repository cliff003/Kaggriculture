r"""Paired comparison of rr.py result files that played the same opponents, seeds and seats.

.venv\Scripts\python.exe tools\pair.py CAND.jsonl BASE.jsonl

Each file holds one candidate (the rr.py --vs agent) against a panel. Games are matched on
(opponent, seed, seat). Per opponent it prints W/L/T and mean margin of both files, the mean paired
margin change with its standard error, and how many results flipped.
"""
import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg


def name(path):
    return os.path.basename(os.path.dirname(path.replace("\\", "/")))


def read(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def load(rows, other):
    # the candidate is the agent missing from the other file; with a larger panel it also plays every game
    agents = {d["a"] for d in rows} | {d["b"] for d in rows}
    own = agents - ({d["a"] for d in other} | {d["b"] for d in other})
    count = collections.Counter(x for d in rows for x in (d["a"], d["b"]) if x in (own or agents))
    cand = count.most_common(1)[0][0]
    out = {}
    for d in rows:
        seat = 0 if d["a"] == cand else 1
        opp = d["b"] if seat == 0 else d["a"]
        me, op = (d["ra"], d["rb"]) if seat == 0 else (d["rb"], d["ra"])
        if me is None or op is None or d.get("status") != ["DONE", "DONE"]:
            print(f"坏局 {d.get('status')} {d['a']} {d['b']} {d['seed']}", file=sys.stderr)
            continue
        out[(name(opp), d["seed"], seat)] = me - op
    return name(cand), out


def wlt(ms):
    return f"{sum(m > 0 for m in ms)}/{sum(m < 0 for m in ms)}/{sum(m == 0 for m in ms)}"


def main():
    ra, rb = read(sys.argv[1]), read(sys.argv[2])
    (na, a), (nb, b) = load(ra, rb), load(rb, ra)
    keys = sorted(set(a) & set(b))
    rows = []
    for opp in sorted({k[0] for k in keys}) + ["合计"]:
        ks = [k for k in keys if opp == "合计" or k[0] == opp]
        ma, mb = [a[k] for k in ks], [b[k] for k in ks]
        d = [x - y for x, y in zip(ma, mb)]
        n = len(d)
        mean = sum(d) / n
        # games sharing a seed are strongly correlated, so the error is computed over per-seed means
        by_seed = collections.defaultdict(list)
        for k, x in zip(ks, d):
            by_seed[k[1]].append(x)
        sm = [sum(v) / len(v) for v in by_seed.values()]
        s = len(sm)
        smean = sum(sm) / s
        se = math.sqrt(sum((x - smean) ** 2 for x in sm) / (s - 1) / s) if s > 1 else 0.0
        up = sum(1 for x, y in zip(ma, mb) if (x > 0) > (y > 0) or (x == 0 and y < 0))
        down = sum(1 for x, y in zip(ma, mb) if (x > 0) < (y > 0) or (x < 0 and y == 0))
        rows.append([opp, n, wlt(ma), f"{sum(ma) / n:.0f}", wlt(mb), f"{sum(mb) / n:.0f}", f"{mean:+.0f}", f"{se:.0f}", up, down])
    kg.table(["对手", "局数", na + " 胜/负/平", "差距", nb + " 胜/负/平", "差距", "配对变化", "标准误(按种子)", "变好", "变差"], rows)


if __name__ == "__main__":
    main()
