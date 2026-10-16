r"""Build a hybrid agent: v8 (tape) until SWITCH_DAY, then p3 engine.  build.py OUT_DIR SWITCH_DAY [P3_PATH] [TAPE_AGENT_PATH]"""
import base64, os, sys, zlib
out, day = sys.argv[1], int(sys.argv[2])
p3 = sys.argv[3] if len(sys.argv) > 3 else "prod/agents/p3/main.py"
v8 = open(sys.argv[4] if len(sys.argv) > 4 else "submissions/v8_own_cha22_tick_guard10/main.py", encoding="utf-8").read()
pr = open(p3, encoding="utf-8").read()
enc = lambda s: base64.b85encode(zlib.compress(s.encode("utf-8"), 9)).decode("ascii")
src = f'''"""Hybrid: v8 tape until day {{SWITCH_DAY}}, then the p3 production engine (team 42 research)."""
import base64 as _b64, zlib as _zlib
SWITCH_DAY = {day}
_V8_SRC = "{enc(v8)}"
_P3_SRC = "{enc(pr)}"


def _load(src, name):
    ns = {{"__name__": name}}
    code = _zlib.decompress(_b64.b85decode(src)).decode("utf-8")
    exec(compile(code, name, "exec"), ns)
    fn = [v for v in ns.values() if callable(v) and getattr(v, "__module__", None) is None or callable(v)]
    return ns


_NS = {{}}
STATE = {{}}


def _ns(key, src):
    if key not in _NS:
        _NS[key] = _load(src, key)
    return _NS[key]


def agent(observation, configuration=None):
    step = observation.get("step", 0) if hasattr(observation, "get") else getattr(observation, "step", 0)
    day = step // 24
    v8 = _ns("v8", _V8_SRC)
    p3 = _ns("p3", _P3_SRC)
    ov = STATE.get("_override")
    if ov is not None:
        p3["STATE"]["_override"] = ov
    if day < SWITCH_DAY:
        return v8["agent"](observation, configuration)
    return p3["agent"](observation, configuration)
'''
os.makedirs(out, exist_ok=True)
open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(src)
print("wrote", out)
