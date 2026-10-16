r"""Apply byte patches to the cha22 base source embedded in a team-42 build (research builds).

.venv\Scripts\python.exe tools\patch_base.py IN_MAIN_PY OUT_DIR --patch NAME [--patch NAME ...]

The base source is embedded as zlib + base85 in `_BASE_SRC`; this decodes it, applies the named patches
(tools/build_v7chain.py PATCHES plus the ones below) and writes the build with the re-encoded blob. A submission
built this way no longer embeds the base unchanged and must say so in its header and NOTICE.
"""
import argparse
import base64
import os
import re
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_v7chain import PATCHES as CHAIN_PATCHES  # noqa: E402

PATCHES = dict(CHAIN_PATCHES)
# V219 tomato investment (day 18, SE quadrant, 10 tomatoes) with 2 pizza/farmers-market shops instead of 3
PATCHES["v219n2"] = [(b"if sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in obs['town']['unlocked_shops']) < 3:",
                      b"if sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in obs['town']['unlocked_shops']) < 2:")]
# ... only when the two shops open early (both by day 9, one on day 3): their tomato demand by day 18 is at least 24
# shop-days, so the market is short when our tomatoes arrive on day 26 (09-26 live replays: +1777/game, 4 up 0 down
# in those 30 worlds, while later pairs lost 755-824/game)
PATCHES["v219n2e"] = [(b"if sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in obs['town']['unlocked_shops']) < 3:",
                       b"if sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in obs['town']['unlocked_shops']) < 3 and not ("
                       b"sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in obs['town']['unlocked_shops']) == 2 and "
                       b"sum(15-3*i for i,s in enumerate(obs['town']['unlocked_shops'][:6]) "
                       b"if s in ('PIZZA_SHOP','FARMERS_MARKET')) >= 24):")]
PATCHES["v219n1"] = [(b"if sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in obs['town']['unlocked_shops']) < 3:",
                      b"if sum(s in ('PIZZA_SHOP','FARMERS_MARKET') for s in obs['town']['unlocked_shops']) < 1:")]

BLOB_RE = re.compile(r"_BASE_SRC = _zlib\.decompress\(_b64\.b85decode\(\n((?:    '[^'\n]*'\n)+)\s*\)\)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--patch", action="append", required=True)
    a = ap.parse_args()
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    m = BLOB_RE.search(s)
    assert m, "embedded base blob not found"
    blob = "".join(line.strip()[1:-1] for line in m.group(1).splitlines())
    base = zlib.decompress(base64.b85decode(blob))
    for name in a.patch:
        for entry in PATCHES[name]:
            old, new = entry[:2]
            count = entry[2] if len(entry) > 2 else 1
            assert base.count(old) == count, (name, old[:60])
            base = base.replace(old, new)
    enc = base64.b85encode(zlib.compress(base, 9)).decode("ascii")
    lines = "".join(f"    '{enc[i:i + 120]}'\n" for i in range(0, len(enc), 120))
    s = s[:m.start()] + "_BASE_SRC = _zlib.decompress(_b64.b85decode(\n" + lines + "))" + s[m.end():]
    compile(s, "main.py", "exec")
    if crlf:
        s = s.replace("\n", "\r\n")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "main.py"), "wb") as f:
        f.write(s.encode("utf-8"))
    print("wrote", os.path.join(a.out, "main.py"), "patches", a.patch)


if __name__ == "__main__":
    main()
