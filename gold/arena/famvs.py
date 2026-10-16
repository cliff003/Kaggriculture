r"""cha22-family panel: each agent vs 5 reactive cha22-family opponents (cha22, emu_eager, emu_eager_m, v4, v6) on 40
random worlds (8 uniform shops each, fixed list gold/arena/famworlds.json), one game per world, seats alternating.
Wins are what the ranking counts; the live field near our rating is mostly this family.

.venv\Scripts\python.exe gold\arena\famvs.py NAME=PATH [NAME=PATH ...] [--workers 8]
Caches gold/arena/games/fam_<name>_<opp>.json and prints a table (wins per opponent, total wins/200, mean margin).
"""
import json
import os
import random
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))
WORLDS = os.path.join(ROOT, "gold", "arena", "famworlds.json")
SHOPS = sorted(["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE", "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP",
                "FARMERS_MARKET"])
OPPS = {
    "cha22": os.path.join(ROOT, "research", "panel", "cha22", "main.py"),
    "emu_eager": os.path.join(ROOT, "research", "panel", "emu_eager", "main.py"),
    "emu_eager_m": os.path.join(ROOT, "research", "panel", "emu_eager_m", "main.py"),
    "v4": os.path.join(ROOT, "submissions", "v4_own_cha22_slot", "main.py"),
    "v6": os.path.join(ROOT, "submissions", "v6_own_cha22_eager_g90", "main.py"),
}


PUBLIC = {k: os.path.join(ROOT, "data", "public", "agents", k, "main.py") for k in
          ("ahmed_v55", "ahmed_v53", "ahmed_v39", "ars_herdsafe_v3", "aurax7_router_v7", "nathan_pipe7", "prvsiyan_moon",
           "marketshock_wr1")}
PUBLIC["leo"] = os.path.join(ROOT, "gold", "public", "wrap_leo_song", "main.py")
if "--public" in sys.argv:
    OPPS = PUBLIC      # public agents from the Code page (other teams' market layers on the same route tapes)
if "--only" in sys.argv:
    _keep = sys.argv[sys.argv.index("--only") + 1].split(",")
    OPPS = {k: v for k, v in OPPS.items() if k in _keep}


def run(path, name, workers):
    if not os.path.exists(WORLDS):
        rng = random.Random(20260925)
        json.dump([[rng.choice(SHOPS) for _ in range(8)] for _ in range(40)], open(WORLDS, "w"))
    n = len(json.load(open(WORLDS)))
    row = {}
    for opp, op in OPPS.items():
        js = os.path.join(ROOT, "gold", "arena", "games", f"{'pub' if opp in PUBLIC and opp not in ('v4', 'v6') and '--public' in sys.argv else 'fam'}_{name}_{opp}.json")
        if not os.path.exists(js):
            nn = 20 if OPPS is PUBLIC else n
            subprocess.run([PY, os.path.join(ROOT, "gold", "tools", "gstat.py"), path, op, "--seeds", str(nn),
                            "--seed0", "64000", "--alt", "--workers", str(workers), "--worlds-file", WORLDS,
                            "--json", js], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
            w, l, t = w + (a > b), l + (a < b), t + (a == b)
        row[opp] = (w, l, t, sum(diffs) / len(diffs))
    return row


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--") and "=" in a]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    print("| agent | " + " | ".join(OPPS) + f" | wins | mean |")
    print("|---|" + "---|" * len(OPPS) + "---|---|")
    for a in args:
        if "=" not in a:
            continue
        name, path = a.split("=", 1)
        row = run(path, name, workers)
        tot = sum(v[0] + 0.5 * v[2] for v in row.values())
        mean = sum(v[3] for v in row.values()) / len(row)
        print(f"| {name} | " + " | ".join(f"{v[0]}-{v[1]}-{v[2]} ({v[3]:+.0f})" for v in row.values())
              + f" | {tot:.0f} | {mean:+.0f} |", flush=True)


if __name__ == "__main__":
    main()
