r"""Render the figures to docs/img/NN_stem_{light,dark}.png with headless Chrome.

python docs/figures/build.py                 all figures, both themes
python docs/figures/build.py --only 01 03    some figures
python docs/figures/build.py --theme light   one theme
python docs/figures/build.py --data          first rebuild docs/figures/data/ (needs the local replays, see data_build.py)

Each figure module (figNN_*.py) defines NN, STEM, TITLE, SUBTITLE, TAG, HEIGHT, CAPTION, ALT and
body(theme, data) -> (html, svg_overlay). Pass 1 dumps the DOM and checks height, fonts, overflow, out-of-bounds
elements and label collisions; pass 2 takes the screenshot at device scale 2 (3200 px wide).
"""
import argparse
import csv
import glob
import importlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import frame  # noqa: E402

BUILD = os.path.join(HERE, "build")
IMG = os.path.join(REPO, "docs", "img")
CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium",
]
DASHES = ("\u2013", "\u2014", "\u2212")


def chrome():
    for c in CHROME_CANDIDATES:
        if os.path.isabs(c) and os.path.exists(c):
            return c
    return CHROME_CANDIDATES[-2]


def load_data():
    d = {}
    for p in glob.glob(os.path.join(HERE, "data", "*")):
        name = os.path.basename(p)
        if name.endswith(".json"):
            d[name[:-5]] = json.load(open(p, encoding="utf-8"))
        elif name.endswith(".csv"):
            d[name[:-4]] = list(csv.DictReader(open(p, encoding="utf-8")))
    return d


def modules(only):
    mods = []
    for p in sorted(glob.glob(os.path.join(HERE, "fig[0-9][0-9]_*.py"))):
        m = importlib.import_module(os.path.basename(p)[:-3])
        if not only or m.NN in only:
            mods.append(m)
    return mods


def run_chrome(args, timeout=120):
    prof = os.path.join(BUILD, "chrome-profile")
    base = [chrome(), "--headless=new", "--disable-gpu", "--disable-lcd-text", "--hide-scrollbars", "--no-first-run",
            "--no-default-browser-check", f"--user-data-dir={prof}", "--virtual-time-budget=8000"]
    return subprocess.run(base + args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=timeout)


# ---------------------------------------------------------------- audits
NUM_RE = re.compile(r"(?<![\w.#])[-+]?\d[\d,]*(?:\.\d+)?(?:k|%)?(?![\w])")


def norm(tok):
    t = tok.lstrip("+-").replace(",", "")
    t = t.rstrip("%")
    if t.isdigit():
        t = str(int(t))
    return t


def allow_set(data, extra):
    allowed = set(str(i) for i in range(0, 32)) | {"2026", "100", "50"}
    blob = json.dumps(data, ensure_ascii=False)
    for t in NUM_RE.findall(blob):
        allowed.add(norm(t))
    for t in extra:
        allowed.add(norm(str(t)))
    # numbers shown with a k suffix may appear in data without it and vice versa
    more = set()
    for a in allowed:
        if a.endswith("k"):
            more.add(a[:-1])
        else:
            more.add(a + "k")
    return allowed | more


def number_audit(text, allowed):
    misses = []
    for t in NUM_RE.findall(text):
        n = norm(t)
        if n not in allowed:
            misses.append(t)
    return misses


# ---------------------------------------------------------------- render
def render(m, theme, data, strict=True):
    os.makedirs(BUILD, exist_ok=True)
    body, overlay = m.body(theme, data)
    doc = frame.page(theme, m.NN, m.TITLE, m.SUBTITLE, m.TAG, m.HEIGHT, body, m.CAPTION, overlay)
    for ch in DASHES:
        assert ch not in doc, f"{m.NN}: dash character U+{ord(ch):04X} in the figure"
    hp = os.path.join(BUILD, f"{m.NN}_{theme}.html")
    with open(hp, "w", encoding="utf-8") as f:
        f.write(doc)
    url = "file:///" + hp.replace("\\", "/")
    r = run_chrome([f"--window-size={frame.W},{m.HEIGHT}", "--dump-dom", url])
    mm = re.search(r"data-check=\"([^\"]*)\"", r.stdout)
    if not mm:
        raise SystemExit(f"{m.NN} {theme}: no data-check in DOM dump\n{r.stderr[-2000:]}")
    chk = json.loads(mm.group(1).replace("&quot;", '"'))
    det = re.search(r"data-detail=\"([^\"]*)\"", r.stdout)
    detail = json.loads(det.group(1).replace("&quot;", '"').replace("&amp;", "&")) if det else {}
    txt = re.search(r"data-text=\"([^\"]*)\"", r.stdout)
    text = txt.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">") if txt else ""
    problems = []
    if chk["h"] != m.HEIGHT:
        problems.append(f"height {chk['h']} != {m.HEIGHT}")
    if chk["fonts"] != 1:
        problems.append("fonts not loaded")
    if chk["overflow"]:
        problems.append(f"overflow {chk['overflow']}: {detail.get('overList')}")
    if chk["out"]:
        problems.append(f"out of bounds {chk['out']}: {detail.get('outList')}")
    if chk["collide"]:
        problems.append(f"collisions {chk['collide']}: {detail.get('colList')}")
    misses = number_audit(text, allow_set(data, getattr(m, "ALLOW", [])))
    if misses:
        problems.append(f"numbers not in data/facts: {sorted(set(misses))}")
    raw = os.path.join(BUILD, f"{m.NN}_{theme}_raw.png")
    r2 = run_chrome([f"--window-size={frame.W},{m.HEIGHT}", "--force-device-scale-factor=2",
                     "--default-background-color=00000000", f"--screenshot={raw}", url])
    from PIL import Image
    im = Image.open(raw)
    want = (frame.W * 2, m.HEIGHT * 2)
    if im.size != want:
        if im.size[0] == want[0] and im.size[1] > want[1]:
            tail = im.crop((0, want[1], want[0], im.size[1])).getextrema()
            assert len(tail) == 4 and tail[3][1] == 0, f"{m.NN}: cropped rows are not transparent"
            im = im.crop((0, 0) + want)
        else:
            problems.append(f"png size {im.size} != {want}")
    os.makedirs(IMG, exist_ok=True)
    out = os.path.join(IMG, f"{m.NN}_{m.STEM}_{theme}.png")
    im.save(out, optimize=True)
    size_kb = os.path.getsize(out) / 1024
    status = "OK" if not problems else "PROBLEMS"
    print(f"{m.NN} {theme:5s} {status}  {out}  {size_kb:.0f} KB")
    for p in problems:
        print("    -", p)
    if problems and strict:
        return False
    return True


def dash_audit():
    bad = []
    files = [os.path.join(REPO, "README.md"), os.path.join(REPO, "THIRD_PARTY_NOTICES.md"),
             os.path.join(REPO, "submissions", "README.md"), os.path.join(REPO, "results", "README.md")]
    files += glob.glob(os.path.join(REPO, "docs", "**", "*.md"), recursive=True)
    files += glob.glob(os.path.join(HERE, "*.py"))
    for f in files:
        if not os.path.exists(f):
            continue
        s = open(f, encoding="utf-8").read()
        for ch in DASHES:
            if ch in s:
                bad.append((os.path.relpath(f, REPO), f"U+{ord(ch):04X}", s.count(ch)))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--theme", choices=["light", "dark"])
    ap.add_argument("--data", action="store_true")
    ap.add_argument("--loose", action="store_true", help="write PNGs even if checks fail")
    a = ap.parse_args()
    if a.data:
        subprocess.run([sys.executable, os.path.join(HERE, "data_build.py")], check=True)
    data = load_data()
    ok = True
    for m in modules(a.only):
        for theme in ([a.theme] if a.theme else ["light", "dark"]):
            ok &= render(m, theme, data, strict=not a.loose)
    bad = dash_audit()
    if bad:
        print("dash audit:", bad)
        ok = False
    print("ALL OK" if ok else "SOME CHECKS FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
