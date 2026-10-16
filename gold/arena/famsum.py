r"""Summarize gold/arena/games/fam_*.json (cha22-family panel) into a table: agent x opponent wins and mean margin."""
import collections
import glob
import json
import os

OPPS = ["cha22", "emu_eager", "emu_eager_m", "v4", "v6"]
rows = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "games", "fam_*.json")), key=os.path.getmtime):
    name = os.path.basename(f)[4:-5]
    opp = next(o for o in sorted(OPPS, key=len, reverse=True) if name.endswith("_" + o))
    agent = name[: -len(opp) - 1]
    d = json.load(open(f))
    w = l = t = 0
    ds = []
    for g in d["games"]:
        a, b = g["rewards"][g["cand_side"]], g["rewards"][1 - g["cand_side"]]
        ds.append(a - b)
        w, l, t = w + (a > b), l + (a < b), t + (a == b)
    rows.setdefault(agent, {})[opp] = (w, l, t, sum(ds) / len(ds))
print("| 版本 | " + " | ".join(OPPS) + " | 胜（不含对 v6） | 平均差 |")
print("|---|" + "---|" * len(OPPS) + "---|---|")
for agent, r in rows.items():
    cells = [f"{r[o][0]}-{r[o][1]}-{r[o][2]}（{r[o][3]:+.0f}）" if o in r else "" for o in OPPS]
    core = [o for o in OPPS if o != "v6" and o in r]
    wins = sum(r[o][0] + 0.5 * r[o][2] for o in core)
    mean = sum(r[o][3] for o in core) / max(1, len(core))
    print(f"| {agent} | " + " | ".join(cells) + f" | {wins:.0f}/{40 * len(core)} | {mean:+.0f} |")
