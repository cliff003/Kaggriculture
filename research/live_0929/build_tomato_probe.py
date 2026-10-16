"""Small, independent diagnostics of the existing 18-tomato execution plan."""
import base64
import hashlib
from pathlib import Path
import re
import sys
import zlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/carrera'))
from patch_x18g import BLOB_RE


def replace_once(s, old, new):
    assert s.count(old) == 1, (s.count(old), old[:100])
    return s.replace(old, new)


def build(mode):
    s = (ROOT / 'submissions/V12_AventadorSVJ/main.py').read_bytes().decode()
    match = BLOB_RE.search(s)
    blob = ''.join(line.strip()[1:-1] for line in match.group(1).splitlines() if line.strip())
    base = zlib.decompress(base64.b85decode(blob)).decode()
    if mode in ('water_deadline', 'water_fert'):
        old = "target,command=min(todo,key=lambda v:(abs(pos[0]-v[0][0])+abs(pos[1]-v[0][1]),targets.index(v[0])))"
        new = """target,command=min(todo,key=lambda v:(
            0 if state.get('x18') and v[1]==['WATER'] and int(view.tiles[v[0][1]][v[0][0]].get('consecutive_unwatered',0))>=1 else 1,
            abs(pos[0]-v[0][0])+abs(pos[1]-v[0][1]),targets.index(v[0])))""".replace('\n', '\r\n')
        base = replace_once(base, old, new)
    if mode in ('fert_quota', 'water_fert', 'crew4_full'):
        old = "fertilizer_quantity=_r70_parent_fert_qty(obs,action,planned,offset) if fertilizer else 0"
        base = replace_once(base, old, old + "\r\n    if state.get('x18') and fertilizer:fertilizer_quantity+=8")
        old = "                if pending.get('labor') is not None:\r\n                    role=state['workers'][pending['first_actor']+index]"
        new = """                if state.get('x18'):
                    role=state['workers'][pending['first_actor']+index]
                    role['fertilizer_quantity']=len(role['targets'])
                if pending.get('labor') is not None:
                    role=state['workers'][pending['first_actor']+index]""".replace('\n','\r\n')
        base = replace_once(base, old, new)
    if mode in ('crew4', 'crew4_full'):
        anchor = "    labor=_r53_labor_assignment(obs,action,fertilizer)"
        base = replace_once(base, anchor,
                            "    if state.get('x18') and day>=24:crop_workers=4\r\n" + anchor)
        anchor = "                elif pending['crop_workers']==2:targets="
        groups = "[[(5,5),(6,5),(7,5),(8,5),(9,5)],[(5,6),(6,6),(7,6),(8,6),(9,6)],[(5,7),(6,7),(7,7),(8,7)],[(5,8),(6,8),(7,8),(8,8)]][index]"
        base = replace_once(base, anchor,
                            "                elif pending['crop_workers']==4:targets=" + groups + "\r\n" + anchor)
    if mode == 'crew4_full':
        anchor = "    count=crop_workers+int(fertilizer and day==27 and labor is None)"
        base = replace_once(base, anchor, anchor + "\r\n    if state.get('x18') and fertilizer and day==27:count=crop_workers+2")
        base = replace_once(base, "fertilizer_worker=index==pending['crop_workers']", "fertilizer_worker=index>=pending['crop_workers']")
        base = replace_once(base, "                if fertilizer_worker:targets=state['targets']",
                            "                if fertilizer_worker:targets=(state['targets'][(index-pending['crop_workers'])*9:(index-pending['crop_workers']+1)*9] if state.get('x18') else state['targets'])")
    compile(base, 'base_agent.py', 'exec')
    enc = base64.b85encode(zlib.compress(base.encode(), 9)).decode()
    lines = ''.join(f"    '{enc[i:i+120]}'\r\n" for i in range(0,len(enc),120))
    s = s[:match.start()] + '_BASE_SRC = _zlib.decompress(_b64.b85decode(\r\n' + lines + '))' + s[match.end():]
    s = re.sub(r'_BASE_SHA256 = "[0-9a-f]+"', '_BASE_SHA256 = "' + hashlib.sha256(base.encode()).hexdigest() + '"', s, count=1)
    compile(s, 'main.py', 'exec')
    out = HERE / 'prototypes' / mode / 'main.py'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(s.encode())
    print(mode, hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == '__main__':
    for mode in sys.argv[1:] or ('water_deadline', 'fert_quota', 'water_fert'):
        build(mode)
