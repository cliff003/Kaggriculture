r"""Build the hybrid agent: an opening agent (embedded unchanged) plays steps < SWITCH, the team-42 engine
plays from SWITCH on (default 264 = day 11, hour 0: melons sold, yesterday's hands gone, goods in the shed).

.venv\Scripts\python.exe engine\build_hybrid.py OPENING_MAIN_PY OUT_DIR [--switch 264] [--engine engine\main.py]
"""
import argparse
import base64
import hashlib
import os
import zlib

TEMPLATE = '''# Kaggriculture submission, team 42 (Kefei Yan, Frank Yang, yirenw11).
# Steps < {switch}: embedded opening agent (sha256 {osha}), Apache-2.0 notices retained inside its source.
# Steps >= {switch}: team 42 adaptive engine (sha256 {esha}).
import base64 as _b64
import zlib as _zlib


def _load(blob, name):
    ns = {{"__name__": name}}
    src = _zlib.decompress(_b64.b85decode(blob)).decode("utf-8")
    exec(compile(src, name + ".py", "exec"), ns)
    return ns


_OPEN_NS = _load(
{oblob}, "opening_agent")
_OPENING = [_v for _v in list(_OPEN_NS.values()) if callable(_v)][-1]
_ENGINE_NS = _load(
{eblob}, "team42_engine")
_ENGINE = _ENGINE_NS["agent"]
_SWITCH = {switch}


def agent(observation, configuration=None):
    try:
        step = int(observation["step"])
    except Exception:
        step = int(getattr(observation, "step", 0) or 0)
    if step < _SWITCH:
        return _OPENING(observation, configuration)
    try:
        return _ENGINE(observation, configuration)
    except Exception:
        return {{"farmer": ["PASS"], "hands": [], "market": []}}
'''


def blob(src):
    enc = base64.b85encode(zlib.compress(src, 9)).decode("ascii")
    return "\n".join("    '" + enc[i:i + 120] + "'" for i in range(0, len(enc), 120))


def build(opening, out_dir, switch=264, engine="engine/main.py"):
    osrc, esrc = open(opening, "rb").read(), open(engine, "rb").read()
    code = TEMPLATE.format(switch=switch, osha=hashlib.sha256(osrc).hexdigest(), esha=hashlib.sha256(esrc).hexdigest(),
                           oblob=blob(osrc), eblob=blob(esrc))
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "main.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    compile(code, path, "exec")
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("opening")
    ap.add_argument("out")
    ap.add_argument("--switch", type=int, default=264)
    ap.add_argument("--engine", default="engine/main.py")
    a = ap.parse_args()
    p = build(a.opening, a.out, a.switch, a.engine)
    print("wrote", p, os.path.getsize(p))
