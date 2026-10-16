r"""x18b: V219 grows 18 tomatoes instead of 10, fertilizer still bought and carried for ten (the extra cells are
watered and harvested, fertilized only when a worker has some left); three crews on days 18 and 24.

.venv/bin/python research/carrera/patch_x18.py IN_MAIN_PY OUT_MAIN_PY

Strong cha22 variants plant 18 tomatoes on day 18 with about the same daily hires as ours (live 9/27). The extra
eight cells are rows 7-8, x 5-8 of the south-east quadrant V219 already buys. V219's crews are re-partitioned to cover
all 18 cells (two crews of 9 on light days instead of one crew of 10, three crews of 6 on days 26-28), its day 26-28
labor planner (which only knows rows 5-6) is switched off in favour of the standard partition, and every place that
assumes ten cells (seeds, budget, fertilizer quantities, fertilizer worth) is scaled to 18. Each patch must match the
expected number of times. The base blob is re-encoded exactly like tools/patch_base.py does.
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
PATCHES = [
    ("extra += [['BUY_LAND'],['BUY_SEED','TOMATO',10]]", "extra += [['BUY_LAND'],['BUY_SEED','TOMATO',18]]", 1),
    ("'targets':[(x,y) for y in (5,6) for x in range(5,10)]}",
     "'targets':[(x,y) for y in (5,6) for x in range(5,10)]+[(x,y) for y in (7,8) for x in range(5,9)]}", 1),
    ("elif pending['crop_workers']==2:targets=state['targets'][index*5:index*5+5]",
     "elif pending['crop_workers']==2:targets=" + G2, 1),
    ("else:targets=[[(5,5),(6,5),(7,5)],[(8,5),(9,5),(9,6),(8,6)],[(5,6),(6,6),(7,6)]][index]", "else:targets=" + G3, 1),
    ("crop_workers=1 if day in (19,20,21,22,23,25) and offset<=2 else (3 if 26<=day<=28 else 2)",
     "crop_workers=2 if day in (19,20,21,22,23,25) and offset<=2 else (3 if 26<=day<=28 or day in (18,24) else 2)", 1),
    ("if day not in (26,27,28) or step%24>2:return None", "if True:return None", 1),
    ("farm=obs['farms'][obs['player']];day=int(obs['step'])//24;bonus=0\r\n    for y in (5,6):",
     "farm=obs['farms'][obs['player']];day=int(obs['step'])//24;bonus=0\r\n    for y in (5,6,7,8):", 1),
    ("if not state.get('committed'):budget+=4500", "if not state.get('committed'):budget+=4900", 1),
    # deliver the day's tomatoes before the day-end drop, not only on the last day: 18 cells keep the crews busy until
    # midnight and whatever they carry into the drop overflows the 100-unit shed (13k of tomatoes destroyed in a test)
    ("if step>=718-distance and inv.get('TOMATO',0):", "if (step>=718-distance or step%24>=22-distance) and inv.get('TOMATO',0):", 1),
]


def main():
    src_path, out_path = sys.argv[1], sys.argv[2]
    raw = open(src_path, "rb").read()
    s = raw.decode("utf-8")
    m = BLOB_RE.search(s)
    assert m, "base blob not found"
    blob = "".join(line.strip()[1:-1] for line in m.group(1).splitlines() if line.strip())
    base = zlib.decompress(base64.b85decode(blob)).decode("utf-8")
    for old, new, count in PATCHES:
        n = base.count(old)
        assert n == count, f"patch expected {count}x, found {n}x: {old[:70]}"
        base = base.replace(old, new)
    compile(base, "base_agent.py", "exec")
    enc = base64.b85encode(zlib.compress(base.encode("utf-8"), 9)).decode("ascii")
    nl = "\r\n" if "\r\n" in s else "\n"
    lines = "".join(f"    '{enc[i:i + 120]}'{nl}" for i in range(0, len(enc), 120))
    s = s[:m.start()] + "_BASE_SRC = _zlib.decompress(_b64.b85decode(" + nl + lines + "))" + s[m.end():]
    # the embedded base no longer matches the published sha: record it where the header states the base
    s = s.replace("# v10 (2026-09-26): the embedded cha22 source carries one change.",
                  "# v10 (2026-09-26) and x18b (2026-09-28): the embedded cha22 source carries changes (x18b: V219 grows 18 tomatoes, fertilizer for ten).", 1)
    compile(s, "main.py", "exec")
    open(out_path, "w", encoding="utf-8", newline="").write(s)
    print(out_path, len(s.encode("utf-8")), "bytes")


if __name__ == "__main__":
    main()
