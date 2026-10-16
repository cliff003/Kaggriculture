r"""Append the tick-trap guard layer (gold/front/mk_tguard.py LAYER) to a self-contained package.

    .venv\Scripts\python.exe gold\front\pack_tguard.py SRC_DIR OUT_DIR TAG [KEY=VALUE ...]

KEY=VALUE are the layer's CFG entries (see mk_tguard.cfg_from; defaults: ACT=1, CF=1 here). The layer runs in its own
namespace bound to the package's agent, its _project and its module globals (for the TICK layer's memory and the base
route chassis). LICENSE is copied, NOTICE gets the change appended, submission.tar.gz is rebuilt (mode 644, mtime 0).
Prints the sha256 values.
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
    kv = {"ACT": "1", "CF": "1"}
    kv.update(dict(x.split("=", 1) for x in sys.argv[4:]))
    import mk_tguard
    cfg = mk_tguard.cfg_from(kv)
    cfg["LOG"] = 0
    layer = mk_tguard.LAYER.replace("__CFG__", repr(cfg))
    assert "'''" not in layer
    main_src = open(os.path.join(src_dir, "main.py"), encoding="utf-8").read().rstrip("\n")
    for name in ("_PRE_TG_AGENT", "_TG_NS", "_TG_SRC", "_TG_AGENT"):
        assert name not in main_src, name
    assert "_TICK_NS" in main_src and "def _project" in main_src
    tail = [
        "", "",
        "# " + "-" * 75,
        f"# Team 42 TICK TRAP GUARD layer (outermost, {tag}). Some rivals trap the TICK layer's wheat round trip: at",
        "# s % 4 == 0 they buy 80-90 wheat in slot 0 and sell as much in slot 9, against our last-slot tick buy (net flow",
        "# zero, so the flow guard cannot see it), or they buy one step before our tick buy and sell with our tick sell.",
        "# Money moves only in the market, so each step the cash of our own final orders is simulated alone with the",
        "# engine's rules and compared with the realized cash one step later. Three of the last four tick cycles losing",
        "# 40+ (or the prebuy flow pattern twice) pause TICK for the game, and a counter sells a wheat lot into the",
        "# rival's lift (middle slot) and buys it back in the last slot after its sell, while that keeps paying.",
        "_TG_SRC = r'''" + layer + "'''",
        "_PRE_TG_AGENT = globals().pop(\"agent\")   # pop first: the loader takes the last callable in module order",
        "_TG_NS = {\"__name__\": \"tick_trap_guard\", \"_BASE\": _PRE_TG_AGENT, \"_PROJECT\": _project, \"_NS\": globals()}",
        "exec(compile(_TG_SRC, \"tick_trap_guard\", \"exec\"), _TG_NS)",
        "_TG_AGENT = _TG_NS[\"agent\"]",
        "", "",
        "def agent(observation, configuration=None):",
        "    return _TG_AGENT(observation, configuration)",
        "",
    ]
    main = (main_src + "\n".join(tail)).encode("utf-8")
    assert b"C:\\Users" not in main and b"C:/Users" not in main and b"/Users/cliff/" not in main
    notice = open(os.path.join(src_dir, "NOTICE.txt"), "rb").read()
    h, rest = notice.split(b"\n\n", 1)
    h = h + (f" In {tag} a tick-trap guard pauses the wheat tick arbitrage when the rival is seen trapping it (cash "
             f"check of our own orders, prebuy flow pattern) and sells into the trap's lift.").encode()
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
    print("cfg", cfg)
    print("main.py", hashlib.sha256(main).hexdigest())
    print("tar.gz", hashlib.sha256(buf.getvalue()).hexdigest())


if __name__ == "__main__":
    main()
