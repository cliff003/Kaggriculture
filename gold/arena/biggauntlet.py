r"""Big gauntlet: each agent vs a fixed 6-opponent panel, 16 seeds x 2 seats per opponent (seeds 61000+, forced worlds).
.venv\Scripts\python.exe gold\arena\biggauntlet.py NAME=PATH [NAME=PATH ...] [--workers 10]
Writes gold/arena/games/bg_<name>_<opp>.json (skipped if present) and prints a table."""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))
OPPS = ["cha22", "emu_eager", "morewheat", "rescue", "v15stack", "herdsafe_race"]


def run(path, name, workers):
    row = {}
    for opp in OPPS:
        js = os.path.join(ROOT, "gold", "arena", "games", f"bg_{name}_{opp}.json")
        if not os.path.exists(js):
            subprocess.run([PY, os.path.join(ROOT, "gold", "tools", "gstat.py"), path, os.path.join(ROOT, "research", "panel", opp, "main.py"),
                            "--seeds", "16", "--seed0", "61000", "--both", "--workers", str(workers), "--worlds", "--json", js],
                           cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        d = json.load(open(js))
        w = l = t = 0
        diffs = []
        for g in d["games"]:
            a, b = g["rewards"][g["cand_side"]], g["rewards"][1 - g["cand_side"]]
            diffs.append((a or 0) - (b or 0))
            w += a > b
            l += a < b
            t += a == b
        row[opp] = (w, l, t, sum(diffs) / len(diffs))
    return row


OPPS2 = ["cha22", "emu_eager", "emu_eager_m", "morewheat", "rescue", "v15stack", "herdsafe_race"]
WORLDS2 = list(range(60, 88))      # 28 DSM worlds never used to pick route tables or knobs


def run2(path, name, workers):
    """Panel v2 (09-25 03:10 on): 7 opponents x 28 worlds (DSM 60-87), one game per world, seats alternating."""
    row = {}
    for opp in OPPS2:
        js = os.path.join(ROOT, "gold", "arena", "games", f"bg2_{name}_{opp}.json")
        if not os.path.exists(js):
            subprocess.run([PY, os.path.join(ROOT, "gold", "tools", "gstat.py"), path,
                            os.path.join(ROOT, "research", "panel", opp, "main.py"), "--seeds", str(len(WORLDS2)),
                            "--seed0", "62000", "--alt", "--workers", str(workers), "--worlds", "--world-list",
                            ",".join(map(str, WORLDS2)), "--json", js],
                           cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        d = json.load(open(js))
        w = l = t = 0
        diffs = []
        for g in d["games"]:
            a, b = g["rewards"][g["cand_side"]], g["rewards"][1 - g["cand_side"]]
            if a is None or b is None or sum(g.get("errors") or [0]):
                l += 1
                diffs.append(-99999.0)
                continue
            diffs.append(a - b)
            w += a > b
            l += a < b
            t += a == b
        row[opp] = (w, l, t, sum(diffs) / len(diffs))
    return row


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 10
    print("| agent | " + " | ".join(OPPS) + " | wins/192 |")
    for a in args:
        if "=" not in a:
            continue
        name, path = a.split("=", 1)
        row = run(path, name, workers)
        tot = sum(v[0] + 0.5 * v[2] for v in row.values())
        print(f"| {name} | " + " | ".join(f"{v[0]}-{v[1]}-{v[2]} ({v[3]:+.0f})" for v in row.values()) + f" | {tot:.0f} |", flush=True)


if __name__ == "__main__":
    main()
