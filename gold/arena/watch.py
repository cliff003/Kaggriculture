r"""Event printer for the overnight runs (used by a Monitor): new panel verdicts, champion changes, route-table
entries, bold screens that pass, and any of the three background jobs dying. Polls every 20 s."""
import json
import os
import subprocess
import time

A = os.path.dirname(os.path.abspath(__file__))


def lines(p):
    try:
        return open(p, encoding="utf-8").read().splitlines()
    except OSError:
        return []


def alive():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | ForEach-Object { $_.CommandLine }"],
                         capture_output=True, text=True).stdout
    return {k: (k in out) for k in ("arena.py", "boldsearch.py", "routesearch.py")}


seen = {k: len(lines(os.path.join(A, k))) for k in ("gauntlet.jsonl", "gauntlet2.jsonl", "routesearch2.jsonl", "bold.jsonl")}
champ = open(os.path.join(A, "champion.json"), encoding="utf-8").read()
last_alive = alive()
tick = 0
while True:
    time.sleep(20)
    tick += 1
    g = lines(os.path.join(A, "gauntlet.jsonl"))
    for l in g[seen["gauntlet.jsonl"]:]:
        e = json.loads(l)
        print(f"PANEL {e['name']} wins {e['wins']:.0f}/192 mean {e['mean']:+.0f} passed={e.get('passed')}", flush=True)
    seen["gauntlet.jsonl"] = len(g)
    g2 = lines(os.path.join(A, "gauntlet2.jsonl"))
    for l in g2[seen["gauntlet2.jsonl"]:]:
        e = json.loads(l)
        tag = "champion" if e.get("champion") else f"dw {e.get('dw', 0):+.0f} dm {e.get('dm', 0):+.0f} title={e.get('passed')}"
        print(f"PANEL2 {e['name'][:60]} wins {e['wins']:.0f}/196 mean {e['mean']:+.0f} {tag}", flush=True)
    seen["gauntlet2.jsonl"] = len(g2)
    c = open(os.path.join(A, "champion.json"), encoding="utf-8").read()
    if c != champ:
        champ = c
        print(f"CHAMPION {json.loads(c)['name']}", flush=True)
    r = lines(os.path.join(A, "routesearch2.jsonl"))
    for l in r[seen["routesearch2.jsonl"]:]:
        e = json.loads(l)
        if e.get("final") and e.get("verdict") == "accepted":
            print(f"ROUTE {e['pair']} default {e['default']} -> {e['best']}", flush=True)
    seen["routesearch2.jsonl"] = len(r)
    b = lines(os.path.join(A, "bold.jsonl"))
    for l in b[seen["bold.jsonl"]:]:
        e = json.loads(l)
        if e.get("queued"):
            print(f"BOLD-PASS {e['name'][:70]} {e['w']}-{e['l']}-{e['t']}", flush=True)
    seen["bold.jsonl"] = len(b)
    if tick % 3 == 0:
        now = alive()
        for k, v in now.items():
            if last_alive.get(k) and not v:
                print(f"DIED {k}", flush=True)
        last_alive = now
