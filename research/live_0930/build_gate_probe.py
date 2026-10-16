"""Explore broader 18-tomato eligibility on the validated local candidate."""
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


def build(n):
    s = (HERE / 'prototypes/combined/main.py').read_bytes().decode()
    m = BLOB_RE.search(s)
    assert m
    blob = ''.join(line.strip()[1:-1] for line in m.group(1).splitlines() if line.strip())
    base = zlib.decompress(base64.b85decode(blob)).decode()
    old = 'X18_MIN_SHOPS = 4'
    assert base.count(old) == 1
    base = base.replace(old, f'X18_MIN_SHOPS = {n}')
    compile(base, 'base_agent.py', 'exec')
    enc = base64.b85encode(zlib.compress(base.encode(), 9)).decode()
    nl = '\r\n' if '\r\n' in s else '\n'
    lines = ''.join(f"    '{enc[i:i+120]}'{nl}" for i in range(0,len(enc),120))
    s = s[:m.start()] + '_BASE_SRC = _zlib.decompress(_b64.b85decode(' + nl + lines + '))' + s[m.end():]
    s = re.sub(r'_BASE_SHA256 = "[0-9a-f]+"',
               '_BASE_SHA256 = "' + hashlib.sha256(base.encode()).hexdigest() + '"', s, count=1)
    compile(s, 'main.py', 'exec')
    out = HERE / 'prototypes' / f'gate{n}' / 'main.py'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(s.encode())
    print(n, hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == '__main__':
    for n in (3, 2):
        build(n)
