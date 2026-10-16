r"""Variants of the v8 TICK layer (edits inside its embedded source), optionally with the FADE layer on top.

.venv\Scripts\python.exe tools\build_v8x.py V8_MAIN_PY OUT_DIR [--from-day 10] [--resume 0] [--fadeguard]
                                             [--fade XMAX] [--th 10]

--resume K   (with --resume-max N: at most N times) the guard is no longer permanent: once no churn (or fade, with --fadeguard) of the rival has been seen
             for K ticks, the TICK layer trades again (a v8 rival that stopped for good leaves the churn to us)
--fadeguard  the guard also flags a rival that sells at s % 4 == 0 and buys back at s + 1 (it trades against us)
--from-day D first day of our own churn (a later start lets a churning rival show itself first)
--fade XMAX  add the FADE layer (tools/add_fade.py) with that lot size
"""
import argparse
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = (os.path.join(ROOT, ".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(ROOT, ".venv", "bin", "python"))

OLD_TRACK = '''    if not mem["rival"] and step % 4 == 2:
        fl = mem["flow"]
        hits = 0
        for s0 in range(step - 2, step - 2 - 4 * CFG["WIN"], -4):
            if fl.get(s0, 0) <= -CFG["TH"] and fl.get(s0 + 1, 0) >= CFG["TH"]:
                hits += 1
        if hits >= CFG["HITS"]:
            mem["rival"] = True
            TEL["rival_step"] = step'''
NEW_TRACK = '''    if step % 4 == 2:
        fl = mem["flow"]
        hits = 0
        last = None
        for s0 in range(step - 2, step - 2 - 4 * CFG["WIN"], -4):
            churn = fl.get(s0, 0) <= -CFG["TH"] and fl.get(s0 + 1, 0) >= CFG["TH"]
            fade = CFG.get("FADEGUARD") and fl.get(s0, 0) >= CFG["TH"] and fl.get(s0 + 1, 0) <= -CFG["TH"]
            if churn or fade:
                hits += 1
                if last is None:
                    last = s0
        if not mem["rival"]:
            if hits >= CFG["HITS"]:
                mem["rival"] = True
                TEL["rival_step"] = step
        elif CFG.get("RESUME") and (last is None or step - 2 - last >= 4 * CFG["RESUME"]) and \
                (not CFG.get("RESUME_MAX") or mem.get("resumed", 0) < CFG["RESUME_MAX"]):
            mem["rival"] = False
            mem["resumed"] = mem.get("resumed", 0) + 1
            TEL["resumes"] = TEL.get("resumes", 0) + 1'''
OLD_CFG = "'GUARD': 1, 'TH': 10, 'WIN': 8, 'HITS': 2}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--from-day", type=int, default=10)
    ap.add_argument("--resume", type=int, default=0)
    ap.add_argument("--fadeguard", action="store_true")
    ap.add_argument("--fade", type=int, default=0)
    ap.add_argument("--th", type=int, default=10)
    ap.add_argument("--resume-max", type=int, default=0, help="resume at most this many times (0 = no limit)")
    a = ap.parse_args()
    raw = open(a.src, "rb").read()
    crlf = b"\r\n" in raw
    s = raw.decode("utf-8").replace("\r\n", "\n")
    assert s.count(OLD_TRACK) == 1 and s.count(OLD_CFG) == 1 and s.count("'FROM_DAY': 10,") == 1
    s = s.replace(OLD_TRACK, NEW_TRACK)
    s = s.replace(OLD_CFG, f"'GUARD': 1, 'TH': {a.th}, 'WIN': 8, 'HITS': 2, 'RESUME': {a.resume}, "
                           f"'RESUME_MAX': {a.resume_max}, 'FADEGUARD': {int(a.fadeguard)}}}")
    s = s.replace("'FROM_DAY': 10,", f"'FROM_DAY': {a.from_day},")
    compile(s, "main.py", "exec")
    out_main = os.path.join(a.out, "main.py")
    os.makedirs(a.out, exist_ok=True)
    if a.fade:
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "main.py")
            open(p, "wb").write(s.encode("utf-8"))
            subprocess.run([PY, os.path.join(ROOT, "tools", "add_fade.py"), p, tmp + "_f", "--xmax", str(a.fade)],
                           check=True, capture_output=True)
            s = open(os.path.join(tmp + "_f", "main.py"), "rb").read().decode("utf-8").replace("\r\n", "\n")
    if crlf:
        s = s.replace("\n", "\r\n")
    with open(out_main, "wb") as f:
        f.write(s.encode("utf-8"))
    print("wrote", out_main)


if __name__ == "__main__":
    main()
