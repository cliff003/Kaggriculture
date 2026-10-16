r"""Append the scheduled-fade layer to a self-contained v12 package and write a new package directory.

    .venv\Scripts\python.exe gold\front\pack_v12.py SRC_DIR OUT_DIR TAG [XMAX=80] [GATE=1] [SCHED=327,375,419,435,487]

The layer source is taken from gold/front/mk_sfade.py (CODE without its exec header), run in its own namespace bound
to the package's agent, its _project and its module globals (for the TICK layer's rival flow). LICENSE is copied,
NOTICE gets the change appended, submission.tar.gz is rebuilt (mode 644, mtime 0). Prints the sha256 values.
"""
import hashlib
import io
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    src_dir, out_dir, tag = sys.argv[1], sys.argv[2], sys.argv[3]
    kv = dict(x.split("=", 1) for x in sys.argv[4:])
    cfg = {"XMAX": int(kv.get("XMAX", 80)), "SCHED": [int(s) for s in kv.get("SCHED", "327,375,419,435,487").split(",")],
           "LEAD": 1, "RESERVE": 1500.0, "GATE": int(kv.get("GATE", 1))}
    import mk_sfade
    code = mk_sfade.CODE
    head, body = code.split('_PROJECT = _NS["_project"]\n', 1)
    imports = [l for l in head.splitlines() if l.startswith("import ")]
    layer = "\n".join(imports) + "\n" + body.replace("__CFG__", repr(cfg))
    assert "'''" not in layer
    main_src = open(os.path.join(src_dir, "main.py"), encoding="utf-8").read().rstrip("\n")
    for name in ("_PRE_SCH_AGENT", "_SCH_NS", "_SCH_SRC", "_SCH_AGENT"):
        assert name not in main_src, name
    tail = [
        "", "",
        "# " + "-" * 75,
        f"# Team 42 SCHEDULED FADE layer (outermost, {tag}): about 50 teams run a public layer that buys 63-89 wheat at the",
        "# fixed steps 327, 375, 419, 435, 487 (s % 4 == 3) and sells it the next step. One step earlier we buy up to 80",
        "# wheat in the last slot and sell it in the last slot of the scheduled step, after the rival's buy lifted the",
        "# price. The first scheduled step is played blind; later ones only after the rival was seen doing it.",
        "_SCH_SRC = r'''" + layer + "'''",
        "_PRE_SCH_AGENT = globals().pop(\"agent\")   # pop first: the loader takes the last callable in module order",
        "_SCH_NS = {\"__name__\": \"sched_fade_layer\", \"_BASE\": _PRE_SCH_AGENT, \"_PROJECT\": _project, \"_NS\": globals()}",
        "exec(compile(_SCH_SRC, \"sched_fade_layer\", \"exec\"), _SCH_NS)",
        "_SCH_AGENT = _SCH_NS[\"agent\"]",
        "", "",
        "def agent(observation, configuration=None):",
        "    return _SCH_AGENT(observation, configuration)",
        "",
    ]
    main = (main_src + "\n".join(tail)).encode("utf-8")
    assert b"C:\\Users" not in main and b"C:/Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(src_dir, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {tag} a scheduled-fade layer sells into a rival's fixed-step wheat buys (steps 327, 375, 419, 435, "
             f"487).").encode()
    notice = h + b"\n\n" + rest
    lic = open(os.path.join(src_dir, "LICENSE.txt"), "rb").read()
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
    print("main.py", hashlib.sha256(main).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
