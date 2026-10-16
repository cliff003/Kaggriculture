r"""Rebuild the replay cache and every table behind plan.md.

    .venv\Scripts\python.exe research\dsm_plan\run_all.py            (about 30 s)

Order: replay.py (exact engine replay of data\games\dsm.jsonl.gz into cache\), then the section scripts, each of
which writes out\<name>.md:
    opening.py   section 1 (+ out\opening_steps.md, per-step modal market list for steps 0-150)
    land.py      section 2
    alloc.py     section 3 (+ out\alloc_per_game.csv, counts per game at the end of days 6..27 with the shops)
    sequences.py section 3/4 (out\tile_sequences.md, modal use sequence of every tile)
    schedule.py  section 4
    hires.py     section 5
    fert.py      section 6
    animals.py   section 7
    misc.py      section 8
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

for name in ["replay", "opening", "land", "alloc", "sequences", "schedule", "hires", "fert", "animals", "misc"]:
    print(f"== {name}.py", flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, name + ".py")], cwd=HERE, stdout=subprocess.DEVNULL if name != "replay" else None)
    if r.returncode:
        sys.exit(f"{name}.py failed with exit code {r.returncode}")
print("done; tables in", os.path.join(HERE, "out"))
