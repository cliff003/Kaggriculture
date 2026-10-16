"""02 · ORDER MATCHING: one engine step, why the order slot decides the price, and one real v8 turn."""
from frame import X0, X1, card, chip, div, esc, fam, fmt, section_bar, tok
from icons import icon
import svg

NN = "02"
STEM = "order_matching"
TITLE = "Order matching"
SUBTITLE = "Orders clear slot by slot and each unit sold lowers the price, so the earlier sell gets the better prices."
TAG = "MECHANISM"
HEIGHT = 1460
CAPTION = ("Engine: interpreter(), _process_market(), market_price() and _town_consume() in kaggle-environments "
           "1.32.7. Milk prices from market_price(). Turn: live game 113640990, step 492 (docs/solution.md).")
ALT = ("One engine step: units act, the market clears slot by slot, the town eats, the day ends. Selling 20 milk "
       "first earns 2,802 against 1,962 selling second; a real v8 turn shows its sells first and the TICK buy in "
       "slot 9.")
ALLOW = [1, 2, 3, 9, 10000, 288, 1.32, 36]

SEC_A, SEC_B, SEC_C = 180, 596, 1062


def body(theme, data):
    ink, t2, muted = tok(theme, "ink"), tok(theme, "text2"), tok(theme, "muted")
    blue_b, blue_t = fam(theme, "selling")
    org_b, org_t = fam(theme, "wheat")
    grey_b, grey_t = fam(theme, "base")
    up = tok(theme, "up")
    mr = data["milk_race"]
    turn = data["turn_example"]
    h, o = [], []

    # ================= A: one step of the engine
    h.append(section_bar(SEC_A, "A", "One step of the engine", "kaggle-environments 1.32.7 · interpreter()", blue_b))
    cy0, ch = 240, 276

    def head(num, ic, label, color):
        return (f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">'
                f'{icon(ic, color, 28)}<span class="htr t1">{num} · {label}</span></div>')

    cards = [
        (X0, 250, "base", "sprout", "1", "Units act",
         '<div class="s20 t2" style="line-height:1.35">The farmer and each hired helper take one action: move, '
         'plant, water, harvest, feed, pick up or drop goods.</div>'),
        (346, 540, "selling", "store", "2", "Market",
         '<div style="border:2px dashed {b};border-radius:10px;padding:8px 14px 10px">'
         '<div class="mono s20 t1" style="margin-bottom:6px">for slot = 0 … 9:</div>'
         '<div class="s20 t1" style="display:grid;grid-template-columns:22px 1fr;row-gap:4px;line-height:1.3">'
         '<span class="mono tm">1</span><span>HIRE and BUY_LAND execute (player 0, then 1)</span>'
         '<span class="mono tm">2</span><span>sells and buys: both players quote one unit from the same stock, '
         'both commit, repeat</span>'
         '<span class="mono tm">3</span><span>prices refresh</span></div></div>'
         '<div class="mono s20 t2" style="margin-top:8px">a buy is quoted at stock - 1</div>'),
        (926, 300, "wheat", "wheat", "3", "Town eats",
         '<div class="s20 t2" style="line-height:1.35">Every 4th step (s % 4 = 0) each shop eats 1 of each good it '
         'sells, 2 if it sells only one. Once a day the town centre eats 1 of each product.</div>'),
        (1266, X1 - 1266, "base", "moon", "4", "Day ends",
         '<div class="s20 t2" style="line-height:1.35">After hour 23, carried goods go into the warehouse; above 100 '
         'items they are destroyed. Helpers leave. A shop opens every 3 days.</div>'),
    ]
    for x, w, fm, ic, num, label, inner in cards:
        b, t = fam(theme, fm)
        h.append(card(theme, x, cy0, w, ch, fm,
                      f'<div class="fit" style="position:absolute;left:0;top:0;right:0;bottom:0;padding:16px 18px;'
                      f'overflow:hidden">{head(num, ic, label, b)}{inner.replace("{b}", b)}</div>'))
    for xa, xb in [(X0 + 250, 346), (346 + 540, 926), (926 + 300, 1266)]:
        o.append(svg.arrow(xa + 6, cy0 + ch / 2, xb - 6, cy0 + ch / 2, color=tok(theme, "arrow"), width=4, head=14))
    chips = ["price depends on market stock, neutral at 10,000",
             f"milk: {mr['milk_at_10000']} at 10,000, price 1 after {mr['price1_after']['MILK']} extra units",
             f"strawberries reach 1 after {mr['price1_after']['STRAWBERRY']}, wool after {mr['price1_after']['WOOL']}"]
    h.append(div(X0, cy0 + ch + 16, X1 - X0, 36, '<div style="display:flex;gap:12px">' +
                 "".join(chip(c) for c in chips) + "</div>", fit=True))

    # ================= B: why the slot matters
    h.append(section_bar(SEC_B, "B", "Why the slot matters · 20 milk each from stock 10,000",
                         "engine prices, illustrative", blue_b))
    first, pairs = mr["prices"]["first"], mr["prices"]["pairs"]
    TX0, CW_, CG, CH_ = 456, 16, 3, 28
    rows = [
        ("Rival sells first", "its sell in slot 0, ours in a later slot",
         ["r"] * 20 + ["u"] * 20, first,
         f"rival {fmt(mr['first'])} · us {fmt(mr['second'])}", None),
        ("Same slot", "both in slot 0: one unit each,|same price",
         ["r", "u"] * 20, [p for p in pairs for _ in (0, 1)],
         f"{fmt(mr['same_slot_each'])} each", mr["same_slot_each"] - mr["second"]),
        ("We sell first", "ours in slot 0, the rival's|behind its fixed-price orders",
         ["u"] * 20 + ["r"] * 20, first,
         f"us {fmt(mr['first'])} · rival {fmt(mr['second'])}", mr["first"] - mr["second"]),
    ]
    ry = SEC_B + 80
    o.append(svg.text(TX0, ry - 2, "each bar = 1 milk, height = its price, in fill order", size=20, fill=t2, nc=False))
    kx = TX0 + 40 * (CW_ + CG) - CG
    for lab, c in (("rival", grey_b), ("us", blue_b)):
        w_ = 12 * len(lab) + 4
        kx -= w_
        o.append(svg.text(kx, ry - 2, lab, size=20, fill=t2, nc=False))
        kx -= 24
        o.append(svg.rect(kx, ry - 18, 16, 16, c, rx=3))
        kx -= 18
    for title, sub, who, prices, total, delta in rows:
        h.append(div(X0, ry + 4, 380, 88, f'<div class="s22 w7 t1">{esc(title)}</div>'
                                          f'<div class="s20 t2" style="line-height:1.3">{esc(sub).replace("|", "<br>")}</div>', fit=True))
        for i, (wv, p) in enumerate(zip(who, prices)):
            x = TX0 + i * (CW_ + CG)
            hh = max(4, round(CH_ * 1.6 * p / 160))
            o.append(svg.rect(x, ry + 10 + CH_ * 1.6 - hh, CW_, hh, blue_b if wv == "u" else grey_b, rx=3))
        # one price range per run, centred under it
        runs = [(0, 19), (20, 39)] if who[0] == who[1] else [(0, 39)]
        for a, b in runs:
            xa = TX0 + a * (CW_ + CG)
            xb = TX0 + b * (CW_ + CG) + CW_
            lab = f"{prices[a]} \u2192 {prices[b]}" if len(runs) == 2 else f"pairs {prices[a]} \u2192 {prices[b]}"
            o.append(svg.text((xa + xb) / 2, ry + 76, lab, size=20, fill=t2, anchor="middle", mono=True, nc=False))
        inner = f'<div class="mono s20 t1">{total}</div>'
        if delta:
            inner += (f'<div style="margin-top:6px">{chip(f"<span style=\'color:{up}\'>▲</span>&nbsp;+{delta} vs selling second")}'
                      f'</div>')
        h.append(div(1240, ry + 8, X1 - 1240, 84, inner, fit=True))
        ry += 104
    h.append(div(X0, ry + 4, X1 - X0, 56, '<span class="s20 t2">Measured: order-slot alone won 97 W / 3 L (+36 per '
                                          'game) against the unmodified cha22 (local), and a live rating of 2454 against '
                                          '2342 six hours after a simultaneous upload.</span>', fit=True))

    # ================= C: one real turn
    h.append(section_bar(SEC_C, "C", f"One real turn · <span class='nocaps'>v8</span> · live game, day {turn['day']}, "
                                     f"{turn['hour']}:00", "blue: selling layers · orange: TICK · plain: base route",
                         org_b, raw=True))
    FW, EW, GAP = 262, 58, 8
    sx = X0
    cells = []
    for i, od in enumerate(turn["orders"]):
        w = FW if od else EW
        cells.append((sx, w, od))
        sx += w + GAP
    assert sx - GAP <= X1, sx
    sy = SEC_C + 92
    for i, (x, w, od) in enumerate(cells):
        o.append(svg.text(x + (6 if od else w / 2), sy - 12, f"slot {i}" if od else str(i), size=20, fill=t2,
                          anchor="start" if od else "middle", mono=True, nc=False))
        if not od:
            h.append(div(x, sy, w, 72, '<span class="mono s20 tm">[ ]</span>',
                         style=f"border:2px dashed {tok(theme, 'frame')};border-radius:10px;display:flex;"
                               "align-items:center;justify-content:center"))
            continue
        op, item, n = od
        barc = {"SELL": blue_b, "BUY_SEED": tok(theme, "card"), "BUY_PRODUCT": org_b}[op]
        border = f"2px solid {org_b}" if op == "BUY_PRODUCT" else f"1.5px solid {tok(theme, 'frame')}"
        h.append(div(x, sy, w, 72, f'<div class="mono s20 w7 t1">{op}</div><div class="mono s20 t2">{item} {n}</div>',
                     style=f"border:{border};border-radius:10px;background:{tok(theme, 'card')};"
                           f"box-shadow:inset 6px 0 0 {barc};padding:8px 0 0 20px", fit=True))
    # brackets and notes
    by = sy + 84

    def bracket(i0, i1, html, wmin=None):
        xa = cells[i0][0]
        xb = cells[i1][0] + cells[i1][1]
        o.append(svg.bracket_below(xa + 2, xb - 2, by, depth=10, color=t2))
        h.append(div(xa, by + 18, xb - xa, 56, f'<div class="s20 t2" style="line-height:1.3">{html}</div>', fit=True))

    bracket(0, 1, '<b class="t1">Sells first,</b> so they fill before the rival\'s later orders')
    bracket(2, 2, '<b class="t1">Base route\'s seed buy,</b> moved behind the sells')
    bracket(3, 8, '<b class="t1">Empty orders</b> pad the list, so the TICK buy follows the rival\'s slots 0 to 8')
    bracket(9, 9, '<b class="t1">TICK buys</b> on a step the town eats wheat')
    ny = by + 92
    nxt = turn["next"]
    nchips = []
    for i, (op, item, n) in enumerate(nxt):
        barc = org_b if item == "WHEAT" else blue_b
        nchips.append(chip(f'<span class="tm">slot {i}</span>&nbsp;&nbsp;{op} {item} {n}', mono=True, bar_color=barc))
    h.append(div(X0, ny, X1 - X0, 36, '<div style="display:flex;gap:12px;align-items:center">'
                 '<span class="s20 w7 t1" style="margin-right:4px">Next step:</span>' + "".join(nchips) +
                 '<span class="s20 t2" style="margin-left:6px">the TICK lot is sold back</span></div>', fit=True))
    assert ny + 36 <= HEIGHT - 84 - 10, ny + 36
    return "\n".join(h), "\n".join(o)
