r"""Per-opponent summary of several rr.py --vs result files side by side.

.venv\Scripts\python.exe tools\evalsum.py results\eval_v5.jsonl results\eval_v4.jsonl ...

For each file the candidate is the agent that plays in every game. Cells are W/L/T and mean margin;
the last row is the overall score rate (win = 1, tie = 0.5).
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kg


def name(path):
    return os.path.basename(os.path.dirname(path.replace("\\", "/")))


def load(path):
    rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    count = collections.Counter(x for d in rows for x in (d["a"], d["b"]))
    cand = count.most_common(1)[0][0]
    per = collections.defaultdict(list)
    for d in rows:
        if d.get("status") != ["DONE", "DONE"] or d["ra"] is None or d["rb"] is None:
            per["坏局"].append(0)
            continue
        me, op = (d["ra"], d["rb"]) if d["a"] == cand else (d["rb"], d["ra"])
        per[name(d["b"] if d["a"] == cand else d["a"])].append(me - op)
    return name(cand), per


def main():
    data = [load(p) for p in sys.argv[1:]]
    opps = sorted({o for _, per in data for o in per})
    rows = []
    for o in opps:
        row = [o]
        for _, per in data:
            ms = per.get(o, [])
            row += [f"{sum(m > 0 for m in ms)}/{sum(m < 0 for m in ms)}/{sum(m == 0 for m in ms)}",
                    f"{sum(ms) / len(ms):+.0f}" if ms else ""]
        rows.append(row)
    total = ["得分率"]
    for _, per in data:
        ms = [m for o, v in per.items() if o != "坏局" for m in v]
        pts = sum(1.0 if m > 0 else 0.5 if m == 0 else 0.0 for m in ms)
        total += [f"{pts / len(ms):.1%} ({len(ms)} 局)", f"{sum(ms) / len(ms):+.0f}"]
    rows.append(total)
    headers = ["对手"]
    for cand, _ in data:
        headers += [cand + " 胜/负/平", "平均差距"]
    kg.table(headers, rows)


if __name__ == "__main__":
    main()
