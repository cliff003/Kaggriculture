"""Test lower-cost tomato work schedules against the same V12 base."""
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


def once(s, old, new):
    assert s.count(old) == 1, (s.count(old), old[:100])
    return s.replace(old, new)


def build(name, crop_days, fert_workers):
    s = (ROOT / 'submissions/V12_AventadorSVJ/main.py').read_bytes().decode()
    match = BLOB_RE.search(s)
    blob = ''.join(line.strip()[1:-1] for line in match.group(1).splitlines() if line.strip())
    base = zlib.decompress(base64.b85decode(blob)).decode()
    base = once(base, '    labor=_r53_labor_assignment(obs,action,fertilizer)',
                '    if state.get(\'x18\') and day in ' + repr(tuple(crop_days)) +
                ':crop_workers=4\r\n    labor=_r53_labor_assignment(obs,action,fertilizer)')
    groups = '[[(5,5),(6,5),(7,5),(8,5),(9,5)],[(5,6),(6,6),(7,6),(8,6),(9,6)],[(5,7),(6,7),(7,7),(8,7)],[(5,8),(6,8),(7,8),(8,8)]][index]'
    base = once(base, "                elif pending['crop_workers']==2:targets=",
                "                elif pending['crop_workers']==4:targets=" + groups +
                "\r\n                elif pending['crop_workers']==2:targets=")
    old = 'fertilizer_quantity=_r70_parent_fert_qty(obs,action,planned,offset) if fertilizer else 0'
    base = once(base, old, old + "\r\n    if state.get('x18') and fertilizer:fertilizer_quantity+=8")
    old = "                if pending.get('labor') is not None:\r\n                    role=state['workers'][pending['first_actor']+index]"
    base = once(base, old, "                if state.get('x18'):\r\n"
                "                    role=state['workers'][pending['first_actor']+index]\r\n"
                "                    role['fertilizer_quantity']=len(role['targets'])\r\n" + old)
    if fert_workers == 2:
        old = "    count=crop_workers+int(fertilizer and day==27 and labor is None)"
        base = once(base, old, old + "\r\n    if state.get('x18') and fertilizer and day==27:count=crop_workers+2")
        base = once(base, "fertilizer_worker=index==pending['crop_workers']",
                    "fertilizer_worker=index>=pending['crop_workers']")
        base = once(base, "                if fertilizer_worker:targets=state['targets']",
                    "                if fertilizer_worker:targets=(state['targets'][(index-pending['crop_workers'])*9:(index-pending['crop_workers']+1)*9] if state.get('x18') else state['targets'])")
    compile(base, 'base_agent.py', 'exec')
    enc = base64.b85encode(zlib.compress(base.encode(), 9)).decode()
    lines = ''.join(f"    '{enc[i:i+120]}'\r\n" for i in range(0,len(enc),120))
    s = s[:match.start()] + '_BASE_SRC = _zlib.decompress(_b64.b85decode(\r\n' + lines + '))' + s[match.end():]
    s = re.sub(r'_BASE_SHA256 = "[0-9a-f]+"', '_BASE_SHA256 = "' + hashlib.sha256(base.encode()).hexdigest() + '"', s, count=1)
    compile(s, 'main.py', 'exec')
    out = HERE / 'prototypes' / name / 'main.py'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(s.encode())
    print(name, hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == '__main__':
    for name, days, fert in (
        ('crew4_fert1', range(24,30), 1),
        ('crew4_late', range(26,30), 2),
        ('crew4_last', range(27,30), 2),
        ('crew4_late_fert1', range(26,30), 1),
    ):
        build(name, days, fert)
