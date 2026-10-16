r"""Event printer for fieldsearch.py (used by a Monitor): children that pass the screen, promotions, process death."""
import json
import os
import subprocess
import time

A = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(A, "field.jsonl")


def lines():
    try:
        return open(LOG, encoding="utf-8").read().splitlines()
    except OSError:
        return []


seen = len(lines())
tick = 0
while True:
    time.sleep(20)
    tick += 1
    ls = lines()
    for l in ls[seen:]:
        r = json.loads(l)
        if "full_child" in r:
            fc, fp = r["full_child"], r["full_parent"]
            print(f"FULL {r['name'][:60]} total {fc['total']:.0f} vs parent {fp['total']:.0f} "
                  f"(fam {fc['fam']:.0f}/{fp['fam']:.0f}, p2 {fc['p2']:.0f}/{fp['p2']:.0f}) promoted={r.get('promoted', False)}",
                  flush=True)
    seen = len(ls)
    if tick % 6 == 0:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | ForEach-Object { $_.CommandLine }"],
                             capture_output=True, text=True).stdout
        if "fieldsearch.py" not in out:
            print("DIED fieldsearch.py", flush=True)
            break
