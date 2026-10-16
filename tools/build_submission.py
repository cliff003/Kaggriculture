"""Build a self-contained submission: base agent source embedded + team-42 order-slot priority layer.

python build_submission.py BASE_MAIN_PY OUT_DIR [--start 288] [--license L] [--notice N] [--label TEXT]
"""
import argparse
import base64
import hashlib
import io
import os
import tarfile
import zlib

TEMPLATE = '''# Kaggriculture submission, team 42 (Kefei Yan, Frank Yang, yirenw11).
# Base agent: {label} (Apache-2.0, upstream notices retained inside the embedded source
# and in NOTICE.txt). Modification by team 42, {date}: order-slot priority layer.
# From step {start} on, each turn's market list is rewritten so that SELL orders are issued
# before placeholder slots and before fixed-price orders (HIRE, BUY_SEED, BUY_ANIMAL, BUY_LAND).
# BUY_PRODUCT orders keep their relative position. Quantities and the base policy are unchanged.
import base64 as _b64
import zlib as _zlib

_BASE_SHA256 = "{sha}"
_BASE_SRC = _zlib.decompress(_b64.b85decode(
{blob}
)).decode("utf-8")
_BASE_NS = {{}}
exec(compile(_BASE_SRC, "base_agent.py", "exec"), _BASE_NS)
_BASE_AGENT = [_v for _v in list(_BASE_NS.values()) if callable(_v)][-1]
_SLOT_START = {start}
_FIXED_PRICE = frozenset(("HIRE", "BUY_SEED", "BUY_ANIMAL", "BUY_LAND"))


def _slot_priority(observation, action):
    try:
        step = int(observation["step"])
    except Exception:
        step = int(getattr(observation, "step", 0) or 0)
    if step < _SLOT_START or not isinstance(action, dict):
        return action
    market = action.get("market") or []
    if not any(isinstance(o, list) and o and o[0] == "SELL" for o in market):
        return action
    head, tail = [], []
    for o in market:
        if not (isinstance(o, list) and o):
            continue
        (tail if o[0] in _FIXED_PRICE else head).append(o)
    out = dict(action)
    out["market"] = (head + tail)[:10]
    return out


def agent(observation, configuration=None):
    action = _BASE_AGENT(observation, configuration)
    try:
        action = _slot_priority(observation, action)
    except Exception:
        pass
    return action
'''


def build(base_path, out_dir, start=288, license_path=None, notice_path=None, label="base", date="2026-09-23"):
    src = open(base_path, "rb").read()
    sha = hashlib.sha256(src).hexdigest()
    enc = base64.b85encode(zlib.compress(src, 9)).decode("ascii")
    lines = [enc[i:i + 120] for i in range(0, len(enc), 120)]
    blob = "\n".join("    '" + ln + "'" for ln in lines)
    code = TEMPLATE.format(label=label, start=start, sha=sha, blob=blob, date=date)
    os.makedirs(out_dir, exist_ok=True)
    main_path = os.path.join(out_dir, "main.py")
    with open(main_path, "w") as f:
        f.write(code)
    compile(code, "main.py", "exec")
    members = [("main.py", code.encode("utf-8"))]
    if license_path and os.path.exists(license_path):
        members.append(("LICENSE.txt", open(license_path, "rb").read()))
    notice = b""
    if notice_path and os.path.exists(notice_path):
        notice = open(notice_path, "rb").read()
    notice = (b"Team 42 modification, " + date.encode() + b": order-slot priority layer appended around the base "
              b"agent (see main.py header). Base source embedded unchanged, SHA-256 " + sha.encode() +
              b".\n\n" + notice)
    members.append(("NOTICE.txt", notice))
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, data in members:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            tar.addfile(info, io.BytesIO(data))
    with open(os.path.join(out_dir, "submission.tar.gz"), "wb") as f:
        f.write(buf.getvalue())
    return main_path, sha


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("out")
    ap.add_argument("--start", type=int, default=288)
    ap.add_argument("--license", default=None)
    ap.add_argument("--notice", default=None)
    ap.add_argument("--label", default="base")
    ap.add_argument("--date", default="2026-09-23")
    a = ap.parse_args()
    p, sha = build(a.base, a.out, a.start, a.license, a.notice, a.label, a.date)
    print("wrote", p, "base sha", sha, "size", os.path.getsize(p))
