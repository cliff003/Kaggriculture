r"""Write an SX variant: .venv\Scripts\python.exe gold\sx\mkvar.py NAME key=value ...  -> gold/builds/NAME/main.py"""
import ast, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
name = sys.argv[1]
upd = {}
for kv in sys.argv[2:]:
    k, v = kv.split("=", 1)
    try:
        upd[k] = ast.literal_eval(v)
    except Exception:
        upd[k] = v
src = open(os.path.join(ROOT, "gold", "sx", "sx_sub.py"), encoding="utf-8").read()
code = f'''_SX_PATH = r"{os.path.join(ROOT, 'gold', 'sx', 'sx_sub.py')}"
_SXNS = {{"__name__": "sx_layer"}}
exec(compile(open(_SX_PATH, encoding="utf-8").read(), _SX_PATH, "exec"), _SXNS)
_SXNS["CFG"].update({upd!r})


def agent(observation, configuration=None):
    return _SXNS["agent"](observation, configuration)
'''
out = os.path.join(ROOT, "gold", "builds", name)
os.makedirs(out, exist_ok=True)
open(os.path.join(out, "main.py"), "w", encoding="utf-8").write(code)
print(out, upd)
