r"""Build variants of g036T and wrap them in the cha22-opening hybrid (switch at step 240).
    .venv\Scripts\python.exe gold\newagent\mkhyb.py NAME 'old=>new' ['old=>new' ...]"""
import os, sys, subprocess
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
name = sys.argv[1]
src = open(os.path.join(ROOT, "gold/builds/g036T/main.py"), encoding="utf-8").read()
for rep in sys.argv[2:]:
    a, b = rep.split("=>", 1)
    a = a.replace(chr(92) + "n", chr(10)); b = b.replace(chr(92) + "n", chr(10))
    assert a in src, a
    src = src.replace(a, b)
eng = os.path.join(ROOT, "gold/builds", "e_" + name)
os.makedirs(eng, exist_ok=True)
open(os.path.join(eng, "main.py"), "w", encoding="utf-8").write(src)
subprocess.check_call([sys.executable, os.path.join(ROOT, "engine/build_hybrid.py"), os.path.join(ROOT, "research/panel/cha22/main.py"),
                       os.path.join(ROOT, "gold/builds", name), "--switch", "240", "--engine", os.path.join(eng, "main.py")],
                      stdout=subprocess.DEVNULL)
print(name)
