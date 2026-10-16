r"""x18g: the embedded cha22 base's V219 tomato investment grows 18 tomatoes instead of 10, but only when at least
_X18_MIN_SHOPS pizza shops / farmers markets are open on day 18 (V219's own decision day, the first six shops).

.venv/bin/python research/carrera/patch_x18g.py IN_MAIN_PY OUT_MAIN_PY

Replays (531 tomato-shop worlds, v11 base): the ungated 18-cell version loses in worlds with 2-3 tomato shops among the
first six (-1128 / -505 a game) and wins with 4+ (+1176, +4335, +9882). With the flag off every patched line behaves
exactly like the original V219. With it on: rows 7-8 (x 5-8) of the south-east quadrant are added, crews re-partition
all 18 cells (two crews of 9 on light days, three of 6 on days 18, 24 and 26-28), the day 26-28 labor planner (rows 5-6
only) steps aside, 18 seeds and 400 more budget, fertilizer still for ten, and the crews carry the day's tomatoes to the
shed before the day-end drop (otherwise 18 cells keep them busy past midnight and the drop overflows the shed).
"""
import base64
import re
import sys
import zlib

BLOB_RE = re.compile(r"_BASE_SRC = _zlib\.decompress\(_b64\.b85decode\(\r?\n((?:    '[^'\r\n]*'\r?\n)+)\s*\)\)")
G2 = ("[[(5,5),(6,5),(7,5),(8,5),(9,5),(9,6),(8,6),(7,6),(6,6)],"
      "[(5,6),(5,7),(6,7),(7,7),(8,7),(8,8),(7,8),(6,8),(5,8)]][index]")
G3 = ("[[(5,5),(6,5),(7,5),(8,5),(9,5),(9,6)],[(8,6),(7,6),(6,6),(5,6),(5,7),(6,7)],"
      "[(7,7),(8,7),(8,8),(7,8),(6,8),(5,8)]][index]")
X = "state.get('x18')"
PATCHES = [
    # decide on day 18 with V219's own qualification and grow the target list
    ("    if step==432:state['eligible']=_v219_qualifies(observation,native)",
     "    if step==432:\r\n"
     "        state['eligible']=_v219_qualifies(observation,native)\r\n"
     "        state['x18']=bool(state['eligible'] and sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in observation['town']['unlocked_shops'])>=X18_MIN_SHOPS)\r\n"
     "        if state['x18']:state['targets']=[(x,y) for y in (5,6) for x in range(5,10)]+[(x,y) for y in (7,8) for x in range(5,9)]", 1),
    ("extra += [['BUY_LAND'],['BUY_SEED','TOMATO',10]]", "extra += [['BUY_LAND'],['BUY_SEED','TOMATO',18 if " + X + " else 10]]", 1),
    ("elif pending['crop_workers']==2:targets=state['targets'][index*5:index*5+5]",
     "elif pending['crop_workers']==2:targets=(" + G2 + ") if " + X + " else state['targets'][index*5:index*5+5]", 1),
    ("else:targets=[[(5,5),(6,5),(7,5)],[(8,5),(9,5),(9,6),(8,6)],[(5,6),(6,6),(7,6)]][index]",
     "else:targets=(" + G3 + ") if " + X + " else [[(5,5),(6,5),(7,5)],[(8,5),(9,5),(9,6),(8,6)],[(5,6),(6,6),(7,6)]][index]", 1),
    ("crop_workers=1 if day in (19,20,21,22,23,25) and offset<=2 else (3 if 26<=day<=28 else 2)",
     "crop_workers=(2 if " + X + " else 1) if day in (19,20,21,22,23,25) and offset<=2 else (3 if 26<=day<=28 or (" + X + " and day in (18,24)) else 2)", 1),
    ("    if day not in (26,27,28) or step%24>2:return None",
     "    if day not in (26,27,28) or step%24>2 or (_V219_STATES.get(obs['player']) or {}).get('x18'):return None", 1),
    ("farm=obs['farms'][obs['player']];day=int(obs['step'])//24;bonus=0\r\n    for y in (5,6):",
     "farm=obs['farms'][obs['player']];day=int(obs['step'])//24;bonus=0\r\n    for y in (5,6,7,8):", 1),
    ("if not state.get('committed'):budget+=4500", "if not state.get('committed'):budget+=4900 if " + X + " else 4500", 1),
    ("if step>=718-distance and inv.get('TOMATO',0):",
     "if (step>=718-distance or (" + X + " and step%24>=22-distance)) and inv.get('TOMATO',0):", 1),
]


def main():
    src_path, out_path = sys.argv[1], sys.argv[2]
    min_shops = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    s = open(src_path, "rb").read().decode("utf-8")
    m = BLOB_RE.search(s)
    assert m, "base blob not found"
    blob = "".join(line.strip()[1:-1] for line in m.group(1).splitlines() if line.strip())
    base = zlib.decompress(base64.b85decode(blob)).decode("utf-8")
    for old, new, count in PATCHES:
        n = base.count(old)
        assert n == count, f"patch expected {count}x, found {n}x: {old[:70]}"
        base = base.replace(old, new)
    # the flag's threshold lives next to V219's other constants
    anchor = "_V219_FERTILIZE = True"
    assert base.count(anchor) == 1
    base = base.replace(anchor, f"X18_MIN_SHOPS = {min_shops}  # team 42 x18g: 18 tomatoes when this many pizza/farmers-market shops are open on day 18\r\n" + anchor)
    compile(base, "base_agent.py", "exec")
    enc = base64.b85encode(zlib.compress(base.encode("utf-8"), 9)).decode("ascii")
    nl = "\r\n" if "\r\n" in s else "\n"
    lines = "".join(f"    '{enc[i:i + 120]}'{nl}" for i in range(0, len(enc), 120))
    s = s[:m.start()] + "_BASE_SRC = _zlib.decompress(_b64.b85decode(" + nl + lines + "))" + s[m.end():]
    old_hdr = "# v10 (2026-09-26): the embedded cha22 source carries one change."
    assert s.count(old_hdr) == 1
    s = s.replace(old_hdr, "# v10 (2026-09-26) and x18g (2026-09-28): the embedded cha22 source carries changes (x18g: with 4+ pizza/farmers-market shops open on day 18, V219 grows 18 tomatoes).")
    compile(s, "main.py", "exec")
    open(out_path, "w", encoding="utf-8", newline="").write(s)
    print(out_path, len(s.encode("utf-8")), "bytes")


if __name__ == "__main__":
    main()
