r"""Route oracle: the champion forced onto each candidate route from day 6, against the unforced champion, on the same
worlds (both seats). Shows which animal portfolio wins in which world.
.venv\Scripts\python.exe gold\arena\route_oracle.py [--worlds 24] [--workers 6]"""
import copy
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "gold", "hybrid"))
sys.path.insert(0, os.path.join(ROOT, "gold", "arena"))
import layers  # noqa: E402
import search  # noqa: E402
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))
ROUTES = [0, 3, 12, 100, 101, 110, 111, 114, 115, 123]
SEED0 = 90000


def main():
    nw = int(sys.argv[sys.argv.index("--worlds") + 1]) if "--worlds" in sys.argv else 24
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
    champ = os.path.join(ROOT, "gold", "hybrid", "lm_fertlead.py")
    parent = search.parse_cfg(champ)
    for r in ROUTES:
        cfg = copy.deepcopy(parent)
        cfg["force_route"] = r
        path = os.path.join(ROOT, "gold", "hybrid", f"cx_route{r}.py")
        layers.write(path, f"route{r}", f"fertlead 强制走录像 {r}", cfg)
        js = os.path.join(ROOT, "gold", "arena", "games", f"oracle_route{r}.json")
        if not os.path.exists(js):
            subprocess.run([PY, os.path.join(ROOT, "gold", "tools", "gstat.py"), path, champ, "--seeds", str(nw),
                            "--seed0", str(SEED0), "--both", "--workers", str(workers), "--worlds", "--json", js],
                           cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        d = json.load(open(js))
        diffs = [g["rewards"][g["cand_side"]] - g["rewards"][1 - g["cand_side"]] for g in d["games"]]
        w = sum(1 for x in diffs if x > 0)
        print(f"route {r}: {w}-{sum(1 for x in diffs if x < 0)}-{sum(1 for x in diffs if x == 0)} mean {sum(diffs) / len(diffs):+.0f}",
              flush=True)


if __name__ == "__main__":
    main()
