"""03 · THE WHEAT CYCLE: the town eats wheat after the market; four real rounds, unit by unit."""
from frame import X0, X1, card, div, esc, fam, fmt, section_bar, tok
import svg

NN = "03"
STEM = "wheat_cycle"
TITLE = "The wheat cycle"
SUBTITLE = "The town eats wheat after the market. Four rounds from real games show who earns from it, and how we defended it."
TAG = "MECHANISM"
HEIGHT = 1690
CAPTION = ("Fills logged by re-running recorded games in kaggle-environments 1.32.7: live game 113707384 (the re-run "
           "reproduces both players' final money exactly: us 104,872, the rival 121,615) and live game 113305232. "
           "Data: docs/figures/data/wheat_rounds.json.")
ALT = ("Four wheat rounds from real games: TICK alone +9 and sandwiched -117 (live), the trap guard's counter "
       "+241 and FADE +206 (on replay).")
ALLOW = [1, 32, "1.32", 113707384, 113305232, 104872, 121615, 47, 49]
NOTES_H = 216

UNIT = 2.4          # px per unit on the bars
COL_W, COL_GAP = 354, 24
COL_X = [X0 + i * (COL_W + COL_GAP) for i in range(4)]
SEC_B_Y = 470


def fills_of(rounds, key, step):
    return rounds[key]["steps"][str(step)]["fills"]


def label_for(f, base=False):
    who = "our base route" if base else ("us" if f["who"] == "us" else "rival")
    op = "BUY" if f["op"] == "BUY_PRODUCT" else "SELL"
    price = f"at {f['first']}" if f["first"] == f["last"] else f"{f['first']} to {f['last']}"
    total = "" if base else f" · {fmt(f['total'])}"
    return f"{who} {op} {f['units']} · {price}{total}"


def body(theme, data):
    R = data["wheat_rounds"]
    ink, t2, muted = tok(theme, "ink"), tok(theme, "text2"), tok(theme, "muted")
    orange, orange_t = fam(theme, "wheat")
    violet, violet_t = fam(theme, "counter")
    grey = tok(theme, "muted")
    h, ov = [], []
    ov.append(f'<defs>{svg.hatch_def("hb", tok(theme, "hatch"), tok(theme, "card"))}</defs>')

    # ---------------- A: the cycle
    h.append(section_bar(180, "A", "The cycle", "TICK trades from day 10 (final agents: from day 13)", orange))
    phases = [("s % 4 = 0", 'market, then the town eats <span class="mono">c</span> wheat', True),
              ("s % 4 = 1", "the lot is sold back", False),
              ("s % 4 = 2", "quiet", False),
              ("s % 4 = 3", "pre-buyers trade here", False)]
    px, pw, pg, py, ph = X0, 178, 26, 248, 156
    for i, (k, txt, hot) in enumerate(phases):
        x = px + i * (pw + pg)
        inner = (div(14, 12, pw - 28, 30, f'<span class="mono s22 w7 t1">{esc(k)}</span>') +
                 div(14, 48, pw - 28, 84, f'<div class="s20 t2" style="line-height:1.25">{txt}</div>', fit=True))
        h.append(card(theme, x, py, pw, ph, "wheat" if hot else None, inner, style="" if hot else "border-width:1.5px"))
        if i < 3:
            ov.append(svg.arrow(x + pw + 2, py + ph / 2, x + pw + pg - 2, py + ph / 2, width=3, head=10))
    # return arrow under the boxes
    lx = px + 3 * (pw + pg) + pw / 2
    fx = px + pw / 2
    yb = py + ph
    ov.append(svg.path_arrow(f"M{lx:.1f} {yb + 2:.1f} V {yb + 26:.1f} H {fx:.1f} V {yb + 14:.1f}",
                             (fx, yb + 4), -90, width=3, head=10))
    h.append(div(px + 2 * (pw + pg) - 150, yb + 34, 300, 26, '<div class="s20 t2" style="text-align:center">every 4 steps, 6 times a day</div>'))
    # formula card
    fxc, fw = X0 + 4 * (pw + pg) + 20, X1 - (X0 + 4 * (pw + pg) + 20)
    inner = (div(24, 16, fw - 48, 34, '<span class="mono s24 w7 t1">gain ≈ c × (P(gap + N) - P(gap))</span>') +
             div(24, 60, fw - 48, 28, '<span class="s20 t2">gap = 10,000 - wheat stock; P(gap) = 25 + √gap, rounded</span>') +
             div(24, 92, fw - 48, 56, '<div class="s20 t2" style="line-height:1.3"><span class="mono">N</span> = our lot '
                                     '(up to 95); <span class="mono">c</span> = wheat the town eats (one per wheat shop, '
                                     'plus the town centre once a day)</div>', fit=True))
    h.append(card(theme, fxc, py, fw, 156, "wheat", inner))

    # ---------------- B: four rounds
    h.append(section_bar(SEC_B_Y, "B", "Four rounds from real games, unit by unit", "bar length = units filled", orange))
    rounds = [
        {"key": "tick_and_sandwich", "steps": (304, 305), "title": "TICK alone", "mode": "LIVE", "fam": "wheat",
         "src": "v8 · day 12, 16:00", "base": set(),
         "pnl": [("up", "us (TICK)", "+9")],
         "notes": ["3 eaten × (43 - 40) = 9",
                   "switching TICK off cost the final agent 616 a game on replay (1,504 games)"]},
        {"key": "tick_and_sandwich", "steps": (300, 301), "title": "Sandwiched", "mode": "LIVE", "fam": "wheat",
         "src": "v8 vs a sandwich trader · day 12, 12:00", "base": set(),
         "pnl": [("down", "us (TICK)", "-117"), ("up", "trader", "+127")],
         "notes": ["bought alone from the opening stock, our 95 would cost 3,900; we paid 3,990",
                   "that 90 is the trap guard's signal (limit 40)",
                   "v8 lost its games against two such traders by about 17k each"]},
        {"key": "trap_guard", "steps": (324, 325), "title": "Trap guard", "mode": "REPLAY", "fam": "wheat",
         "src": "v9 replayed in our seat, same game · day 13, 12:00", "base": set(),
         "pnl": [("up", "us (guard)", "+241"), ("down", "trader", "-207")],
         "notes": ["80 sold into the lift, 79 bought back after the drop",
                   "the whole game: -16,743 live, +13,919 on replay"]},
        {"key": "fade", "steps": (364, 365), "title": "FADE", "mode": "REPLAY", "fam": "counter",
         "src": "V12_AventadorSVJ vs a recorded arbitrageur · day 15, 04:00", "base": {(364, 0), (365, 0)},
         "pnl": [("up", "us (FADE)", "+206"), ("down", "arbitrageur", "-192")],
         "notes": ["estimate: our 90 × price slope 0.028 × (rival's 77 - 2 eaten) ≈ 190",
                   "the first FADE build: 41 → 47 wins of 49 replayed games vs arbitrageurs"]},
    ]
    top = SEC_B_Y + 60
    base_fill, base_stroke = tok(theme, "card"), t2
    cols = []
    for ci, r in enumerate(rounds):
        x = COL_X[ci]
        fcol, ftint = fam(theme, r["fam"])
        ours_col = violet if r["fam"] == "counter" else orange
        y = top
        # header
        pill = (f'<span class="chip" style="height:30px;font-size:18px;font-weight:700;letter-spacing:.08em;'
                f'border-color:{ink if r["mode"] == "REPLAY" else muted};color:{ink if r["mode"] == "REPLAY" else t2}">{r["mode"]}</span>')
        hdr = (div(18, 12, 230, 32, f'<span class="s24 w8 t1 caps" style="letter-spacing:.04em">{esc(r["title"])}</span>') +
               div(COL_W - 18 - 110, 12, 110, 32, f'<div style="text-align:right">{pill}</div>') +
               div(18, 50, COL_W - 36, 56, f'<div class="s20 t2" style="line-height:1.3">{esc(r["src"])}</div>', fit=True))
        hh = 112
        h.append(card(theme, x, y, COL_W, hh, None, hdr, fill=ftint, border=fcol, radius=14,
                      style="border-bottom-left-radius:0;border-bottom-right-radius:0"))
        y += hh
        body_top = y
        rows_svg = []

        def bar(bx, by, units, hgt, who, base):
            if base:
                return svg.rect(bx, by, units * UNIT, hgt, base_fill, rx=3, stroke=base_stroke, sw=1.5)
            return svg.rect(bx, by, units * UNIT, hgt, ours_col if who == "us" else grey, rx=3)

        for si, step in enumerate(r["steps"]):
            st = R[r["key"]]["steps"][str(step)]
            y += 16
            rows_svg.append(svg.text(x + 18, y + 18, f"step {step} (s % 4 = {step % 4}) · gap {st['gap_start']}",
                                     size=20, fill=t2, weight=600, nc=False))
            y += 34
            slots = {}
            for f in st["fills"]:
                slots.setdefault(f["slot"], []).append(f)
            for slot in sorted(slots):
                fl = slots[slot]
                rows_svg.append(svg.text(x + 18, y + 14, f"slot {slot}", size=20, fill=t2, mono=True, nc=False))
                bx = x + 112
                if len(fl) == 1:
                    f = fl[0]
                    base = (step, slot) in r["base"] and f["who"] == "us"
                    rows_svg.append(bar(bx, y, f["units"], 18, f["who"], base))
                    rows_svg.append(svg.text(x + 18, y + 44, label_for(f, base), size=20, fill=ink if f["who"] == "us" else t2, nc=False))
                    y += 62
                else:
                    for k, f in enumerate(fl):
                        base = (step, slot) in r["base"] and f["who"] == "us"
                        rows_svg.append(bar(bx, y + k * 14, f["units"], 12, f["who"], base))
                    rows_svg.append(f'<path d="M{bx - 4:.1f} {y:.1f} h-5 v26 h5" fill="none" stroke="{ink}" stroke-width="2.5"/>')
                    yy = y + 52
                    for f in fl:
                        base = (step, slot) in r["base"] and f["who"] == "us"
                        rows_svg.append(svg.text(x + 18, yy, label_for(f, base), size=20,
                                                 fill=ink if f["who"] == "us" else t2, nc=False))
                        yy += 26
                    y = yy - 4
            if si == 0:
                eaten = st["eaten"]
                ax = x + COL_W / 2
                rows_svg.append(svg.arrow(ax, y + 2, ax, y + 40, width=3, head=10))
                h.append(div(ax + 14, y + 6, 160, 30, f'<span class="chip" style="height:30px;border-color:{orange}">town eats {eaten}</span>'))
                y += 44
        cols.append({"x": x, "r": r, "rows": rows_svg, "end": y, "body_top": body_top})

    # footers start on one line across the columns
    foot = max(c["end"] for c in cols) + 14
    col_bottom = []
    for c in cols:
        x, r, rows_svg = c["x"], c["r"], c["rows"]
        y = foot
        rows_svg.append(svg.line(x + 18, y, x + COL_W - 18, y, stroke=tok(theme, "hairline"), width=1))
        y += 14
        for kind, name, val in r["pnl"]:
            upk = kind == "up"
            rows_svg.append(svg.tri(x + 26, y + 18, up=upk, size=14, fill=tok(theme, "up") if upk else tok(theme, "down")))
            rows_svg.append(f'<text x="{x + 44}" y="{y + 28}"><tspan font-size="22" font-weight="500" fill="{t2}">'
                            f'{esc(name)} </tspan><tspan font-size="30" font-weight="800" fill="{ink}">{esc(val)}</tspan></text>')
            y += 42
        y += 6
        notes = "".join(f'<div class="s20 t2" style="line-height:1.3;margin-bottom:8px">{esc(n)}</div>' for n in r["notes"])
        h.append(div(x + 18, y, COL_W - 36, NOTES_H - 8, notes, fit=True))
        col_bottom.append(y)
        h.append(f'<svg class="abs" style="left:0;top:0" width="1600" height="{HEIGHT}">{"".join(rows_svg)}</svg>')
    bottom = max(col_bottom) + NOTES_H
    for c in cols:
        fcol, _ = fam(theme, c["r"]["fam"])
        h.insert(0, card(theme, c["x"], c["body_top"] - 2, COL_W, bottom - c["body_top"] + 2, None, "",
                         border=fcol, style="border-top-left-radius:0;border-top-right-radius:0;border-top:0"))
    # how to read
    hy = bottom + 18
    sw = lambda c, extra="": f'<span style="display:inline-block;width:28px;height:16px;border-radius:3px;background:{c};{extra}vertical-align:-2px;margin-right:8px"></span>'  # noqa: E731
    zipper = (f'<svg width="40" height="26" style="vertical-align:-6px;margin-right:8px">'
              f'<path d="M6 1 h-5 v24 h5" fill="none" stroke="{ink}" stroke-width="2.5"/>'
              f'<rect x="10" y="1" width="28" height="10" rx="3" fill="{grey}"/>'
              f'<rect x="10" y="15" width="22" height="10" rx="3" fill="{orange}"/></svg>')
    items = [sw(orange) + "TICK and trap guard", sw(violet) + "FADE", sw(grey) + "rival",
             sw(base_fill, f"border:1.5px solid {base_stroke};box-sizing:border-box;") + "our base route",
             zipper + "two orders in one slot fill alternately, one unit each",
             "▲▼ cash from the fills shown, both steps",
             "LIVE: as played · REPLAY: our later code against the rival's recorded actions"]
    leg = "".join(f'<span class="s20 t2" style="margin-right:26px;white-space:nowrap">{i}</span>' for i in items)
    h.append(card(theme, X0, hy, X1 - X0, 116, None,
                  div(20, 12, 200, 26, '<span class="htr">How to read</span>') +
                  div(20, 44, X1 - X0 - 40, 64, f'<div style="display:flex;flex-wrap:wrap;row-gap:6px">{leg}</div>', fit=True),
                  style="border-width:1px", radius=10))
    assert hy + 116 <= HEIGHT - 84 - 8, hy + 116
    return "\n".join(h), "\n".join(ov)
