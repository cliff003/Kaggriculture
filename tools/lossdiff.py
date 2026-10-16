r"""Where did a close game's margin come from: per-product revenue difference (opponent minus us) by phase.

.venv\Scripts\python.exe tools\lossdiff.py GAMES.jsonl.gz TEAM EPISODE_ID [EPISODE_ID ...]
Phases: days 0-9, 10-19, 20-25, 26-29. Also the spend difference and who sold first in the last days.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import econ
import kg

PHASES = ((0, 9), (10, 19), (20, 25), (26, 29))


def main():
    path, team = sys.argv[1], sys.argv[2]
    ids = [int(x) for x in sys.argv[3:]]
    games = {g["id"]: g for g in econ.load(path)}
    for gid in ids:
        g = games[gid]
        me = g["teams"].index(team)
        r = econ.resim(g)
        rev = collections.defaultdict(float)
        for step, p, op, item, price in econ._CUR["log"]:
            if op != "SELL":
                continue
            ph = next(i for i, (a, b) in enumerate(PHASES) if a <= step // 24 <= b)
            rev[(item, ph)] += price if p != me else -price
        spend = {k: r[1 - me]["spend"].get(k, 0) - r[me]["spend"].get(k, 0)
                 for k in set(r[0]["spend"]) | set(r[1]["spend"])}
        margin = r[1 - me]["money"] - r[me]["money"]
        print(f"episode {gid} vs {g['teams'][1 - me]}: opponent ahead by {margin:+.0f}")
        rows = []
        for item in econ.ITEMS:
            cells = [rev.get((item, ph), 0.0) for ph in range(len(PHASES))]
            if any(abs(c) >= 1 for c in cells):
                rows.append([item] + [f"{c:+.0f}" for c in cells] + [f"{sum(cells):+.0f}"])
        kg.table(["对方多卖(收入)", "0-9天", "10-19天", "20-25天", "26-29天", "合计"], rows)
        big = {k: v for k, v in spend.items() if abs(v) >= 1}
        if big:
            print("  对方多花:", {k: round(v) for k, v in sorted(big.items())})
        print()


if __name__ == "__main__":
    main()
