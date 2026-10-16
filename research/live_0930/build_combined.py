"""Combine the independently tested cash reserve and late tomato schedule."""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

raw = (HERE / 'prototypes/crew4_last/main.py').read_text()
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
compile(raw, 'combined/main.py', 'exec')
out = HERE / 'prototypes/combined/main.py'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(raw)
print(out)
print(hashlib.sha256(out.read_bytes()).hexdigest())
