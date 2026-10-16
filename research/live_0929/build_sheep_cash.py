"""Diagnostic prototype: keep one FADE refill from delaying day-11 sheep expansion.

This is an experiment, not a submission package. The existing live files are
read only. The eligibility window and price bounds come from the embedded
production module; no opponent identity or episode id is used.
"""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

raw = (ROOT / 'submissions/V12_AventadorSVJ/main.py').read_text()
anchor = '    elif step % 4 == 1 and step <= 713 and (_fd_rival_n(mem, step - 1) > 0 or (step - 1) in st["sold"]):'
assert raw.count(anchor) == 1
replacement = '''    elif (step % 4 == 1 and step <= 713
          and not (step == 11 * 24 + 1
                   and obs["town"]["unlocked_shops"].count("YARN_STORE") >= 2
                   and "SE" not in farm["unlocked_quadrants"]
                   and int(prices.get("WOOL", 0)) >= 220
                   and quote <= 45)
          and (_fd_rival_n(mem, step - 1) > 0 or (step - 1) in st["sold"])):'''
raw = raw.replace(anchor, replacement)
compile(raw, 'sheep_cash/main.py', 'exec')
out = HERE / 'prototypes/sheep_cash/main.py'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(raw)
print(out)
print(hashlib.sha256(out.read_bytes()).hexdigest())
