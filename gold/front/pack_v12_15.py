r"""Build v12_15: v12_14 with the other session's x18g tomato patch applied to the embedded cha22 base.

    .venv/bin/python gold/front/pack_v12_15.py [OUT_DIR] [MIN_SHOPS=4]

x18g (research/carrera/patch_x18g.py, 9/28): when at least MIN_SHOPS pizza shops / farmers markets are open among the first
six shops on day 18 (V219's own decision day), V219 grows 18 tomatoes instead of 10 (rows 7-8, x 5-8 added), the crews
re-partition the cells, 18 seeds are bought and the crews carry the day's tomatoes to the shed before the day-end drop.
On the public line (v11 base) it changed 337 of 1142 replays (329 better, 8 worse, +67/game, no flips) and made +1391/game
on the tomato-rich panel. This script reuses the patch's own edit list and blob handling; only the header note differs
(the ace's header is not v10's). Everything else is byte-identical to v12_14.
"""
import base64
import hashlib
import io
import os
import sys
import tarfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "research", "carrera"))
import patch_x18g as X  # noqa: E402  (PATCHES, BLOB_RE)

SRC = os.path.join(ROOT, "submissions", "v12_14_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40")
TAG = "v12_15"


def patch_main(s, min_shops):
    m = X.BLOB_RE.search(s)
    assert m, "base blob not found"
    blob = "".join(line.strip()[1:-1] for line in m.group(1).splitlines() if line.strip())
    base = zlib.decompress(base64.b85decode(blob)).decode("utf-8")
    for old, new, count in X.PATCHES:
        n = base.count(old)
        assert n == count, f"patch expected {count}x, found {n}x: {old[:70]}"
        base = base.replace(old, new)
    anchor = "_V219_FERTILIZE = True"
    assert base.count(anchor) == 1
    base = base.replace(anchor, f"X18_MIN_SHOPS = {min_shops}  # team 42 x18g: 18 tomatoes when this many pizza/farmers-market shops are open on day 18\r\n" + anchor)
    compile(base, "base_agent.py", "exec")
    enc = base64.b85encode(zlib.compress(base.encode("utf-8"), 9)).decode("ascii")
    nl = "\r\n" if "\r\n" in s else "\n"
    lines = "".join(f"    '{enc[i:i + 120]}'{nl}" for i in range(0, len(enc), 120))
    s = s[:m.start()] + "_BASE_SRC = _zlib.decompress(_b64.b85decode(" + nl + lines + "))" + s[m.end():]
    key = "_BASE_SHA256 = "
    assert s.count(key) == 1
    note = ("# x18g (2026-09-28, research/carrera/patch_x18g.py): the embedded cha22 source also carries the 18-tomato V219 "
            f"extension, enabled only with {min_shops}+ pizza shops / farmers markets open on day 18.{nl}")
    s = s.replace(key, note + key, 1)
    return s, hashlib.sha256(base.encode("utf-8")).hexdigest()


def main():
    args = [x for x in sys.argv[1:] if "=" not in x]
    kv = dict(x.split("=", 1) for x in sys.argv[1:] if "=" in x)
    min_shops = int(kv.get("MIN_SHOPS", 4))
    out_dir = args[0] if args else os.path.join(
        ROOT, "submissions", "v12_15_own_cha22_tick_fade_resume_late_sched_trap_tomato_fguard_gfade_prebuy0_eod_x2n_wind_room_cap40_x18g")
    raw = open(os.path.join(SRC, "main.py"), "rb").read()
    s = raw.decode("utf-8")
    s, base_sha = patch_main(s, min_shops)
    compile(s.replace("\r\n", "\n"), "main.py", "exec")
    main = s.encode("utf-8")
    assert b"C:\\Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(SRC, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {TAG} the embedded base's tomato module (V219) grows 18 tomatoes instead of 10 when {min_shops} or more pizza shops or "
             f"farmers markets are open on day 18 (crews re-partitioned, 18 seeds, tomatoes carried to the shed before the day-end drop).").encode()
    notice = h + b"\n\n" + rest
    lic = open(os.path.join(SRC, "LICENSE.txt"), "rb").read()
    os.makedirs(out_dir, exist_ok=True)
    members = [("main.py", main), ("LICENSE.txt", lic), ("NOTICE.txt", notice)]
    for n, d in members:
        open(os.path.join(out_dir, n), "wb").write(d)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for n, d in members:
            info = tarfile.TarInfo(n)
            info.size = len(d)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(d))
    open(os.path.join(out_dir, "submission.tar.gz"), "wb").write(buf.getvalue())
    print("out", out_dir, "MIN_SHOPS", min_shops, "patched base sha", base_sha[:8])
    print("main.py", hashlib.sha256(main).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
