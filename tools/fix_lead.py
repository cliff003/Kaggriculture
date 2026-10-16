r"""Fix the lead-sell layer of a v7b-line build to read the late route and optionally lead-sell bulk goods.

.venv\Scripts\python.exe tools\fix_lead.py IN_MAIN_PY OUT_DIR [--bulk CARROT,EGG,TOMATO] [--bulk-lead 2] [--last 716]

The wheat lead-sell layer (v7b) looks ahead in the route tape for the SELL orders of the next steps and for the
feed pickups it must keep. From step 648 the chassis plays route 2 (the shared endgame), but the lookahead kept
reading the day's native route, so in the last three days it anticipated sales that never come and missed the ones
that do. The fix reads route 2 for steps >= 648. --bulk adds a lead-sell of those goods (route 2 sells carrots,
eggs and tomatoes in the same steps for every family rival, so selling a step or two ahead takes the top of the
book), active up to step --last.
"""
import argparse
import os

OLD_PLANNED = '''    def planned(route, step, item, lead):
        tape = chassis.routes.get(route) or []
        q = 0
        for t in range(step + 1, min(len(tape), step + 1 + lead)):
            a = tape[t]
            if isinstance(a, dict):
                for o in a.get("market") or []:
                    if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                        q += int(o[2])
        return q'''
NEW_PLANNED = '''    def planned(route, step, item, lead):
        q = 0
        for t in range(step + 1, min(719, step + 1 + lead)):
            tape = chassis.routes.get(2 if t >= 648 else route) or []
            a = tape[t] if t < len(tape) else None
            if isinstance(a, dict):
                for o in a.get("market") or []:
                    if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                        q += int(o[2])
        return q'''
OLD_PICK = '''        tape = chassis.routes.get(route) or []
        q = 0
        for t in range(step + 1, min(len(tape), step + 1 + horizon)):
            a = tape[t]
            if isinstance(a, dict):
                for u in [a.get("farmer")] + list(a.get("hands") or []):'''
NEW_PICK = '''        q = 0
        for t in range(step + 1, min(719, step + 1 + horizon)):
            tape = chassis.routes.get(2 if t >= 648 else route) or []
            a = tape[t] if t < len(tape) else None
            if isinstance(a, dict):
                for u in [a.get("farmer")] + list(a.get("hands") or []):'''
OLD_WINDOW = "        if step < 240 or step > 700:\n            return action\n        st = chassis.players.get(player)"
OLD_CFG = "'layers': {'wheat_lead': {'lead': 2, 'hours': [], 'front': False, 'reserve_h': 4}}}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--bulk", default="")
    ap.add_argument("--bulk-lead", type=int, default=2)
    ap.add_argument("--last", type=int, default=700)
    a = ap.parse_args()
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    for old in (OLD_PLANNED, OLD_PICK, OLD_WINDOW, OLD_CFG):
        assert s.count(old) == 1, old[:60]
    s = s.replace(OLD_PLANNED, NEW_PLANNED).replace(OLD_PICK, NEW_PICK)
    s = s.replace(OLD_WINDOW, OLD_WINDOW.replace("step > 700", f"step > {a.last}"))
    if a.bulk:
        items = [x for x in a.bulk.split(",") if x]
        s = s.replace(OLD_CFG, OLD_CFG[:-2] + f", 'bulk_lead': {{'items': {items!r}, 'lead': {a.bulk_lead}, "
                                               f"'hours': [], 'front': False}}}}}}")
    compile(s, "main.py", "exec")
    if crlf:
        s = s.replace("\n", "\r\n")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "wb") as f:
        f.write(s.encode("utf-8"))
    print("wrote", os.path.join(a.out, "main.py"))


if __name__ == "__main__":
    main()
