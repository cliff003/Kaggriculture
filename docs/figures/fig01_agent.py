"""01 · THE AGENT: the public replay base and our wrappers, inner to outer, each with its evidence."""
from frame import X0, X1, card, chip, div, esc, fam, tok
from icons import icon
import svg

NN = "01"
STEM = "agent"
TITLE = "The agent"
SUBTITLE = "A public agent that follows recorded routes runs the farm. Seven groups of our wrappers edit its action every step."
TAG = "MECHANISM"
HEIGHT = 1380
CAPTION = ("Wrapper order as in submissions/V12_AventadorSVJ/main.py; v12_19 adds two source patches and a sheep "
           "cash reserve inside FADE. Chips: the versions that added each piece. On replay: our live games re-run "
           "with the rival's recorded moves. Evidence: docs/solution.md.")
ALT = ("Team 42's agent: the public cha22 route-replay agent (41 recorded routes, public reactive layers, our gated source "
       "patches) wrapped, inner to outer, by our selling layers, base fixes, TICK, FADE, the trap guard, GFADE and "
       "harvest deferral, each with its evidence.")
ALLOW = [1600, 288, 2000]

WRAPPERS = [
    ("selling", "list", "Sell first", "v4 to v7b",
     "Sells move ahead of hires and seed buys; milk, strawberries and wool sell on arrival",
     "97 W / 3 L", "order-slot alone vs the unmodified cha22, local"),
    ("fixes", "wrench", "Base fixes", "v7c",
     "Unstick the six-sheep worker; spend carried fertilizer where it beats its price",
     "844 → 873", "local wins of 980"),
    ("wheat", "wheat", "TICK + peer guard", "v8, v12_1",
     "When the town eats wheat, buy up to 95 in the last slot and sell next step",
     "497 → 538", "v7b → v8: wins of 576 live games, on replay"),
    ("counter", "repeat", "FADE + scheduled fade", "v12, v12_2",
     "Sell after another arbitrageur's buy lifts the price; buy back after its sell",
     "+2.0k → +21.5k", "per game vs an emulated arbitrageur, local"),
    ("wheat", "shield", "Trap guard", "v9, v12_3",
     "Check our cash against our own orders; on a mismatch, stop TICK and trade back",
     "-16,743 → +13,919", "one of two sandwich-trap games, on replay"),
    ("counter", "repeat", "GFADE", "v12_6",
     "Also fade arbitrageurs that trade one to three steps off the town's meal",
     "+1,940", "per game on 9 such games, on replay"),
    ("fixes", "moon", "Harvest deferral", "v11, v12_8",
     "If the warehouse would overflow at hour 23, collect lasting harvests next morning",
     "+69", "per game on 917 replays, 0 flips lost"),
]

PUBLIC_LAYERS = ["action repairs", "rival-sale racing", "goods carried home", "crop and herd switches",
                 "10 tomatoes (V219)", "six sheep (V233)", "fertilizer helper (R51)", "clearance sale"]
PATCHES = [("tomato gate: 2 early shops", "v10, v12_4"), ("18 tomatoes with 4+ tomato shops", "v11x, v12_15"),
           ("late tomato crews", "v12_18"), ("fertilizer gate by farm layout", "v12_19")]

CARD_Y0, CARD_H, CARD_GAP = 252, 122, 12
CX, CW = 690, X1 - 690
RAIL_X = 664


def body(theme, data):
    ink, t2, muted = tok(theme, "ink"), tok(theme, "text2"), tok(theme, "muted")
    base_b, base_t = fam(theme, "base")
    aq_b, aq_t = fam(theme, "fixes")
    h = []
    ov = []
    # ---------------- left column: the base
    h.append(div(X0, 180, 560, 28, '<span class="htr">The base · public code</span>'))
    h.append(div(X0, 214, None, 40, '<span class="chip mono" style="height:40px;border:1.5px solid var(--ink)">observation</span>'))
    ov.append(svg.arrow(X0 + 80, 256, X0 + 80, 290, width=4, head=14))
    bx, by, bw, bh = X0, 292, 556, 548
    inner = []
    inner.append(div(22, 20, 32, 32, icon("layers", base_b)))
    inner.append(div(66, 18, 300, 34, '<span class="s24 w7 t1">cha22</span>'))
    inner.append(div(160, 16, 360, 36, chip("public · Apache-2.0")))
    inner.append(div(22, 66, 512, 40, '<span class="s32 w8 t1">41 recorded routes</span>'))
    # mini timeline: 30 days
    tl_x, tl_y, tl_w = 22, 122, 508
    sx = lambda d: tl_x + d * tl_w / 30
    seg = [(0, 6, base_b, 1.0), (6, 27, base_b, 0.45), (27, 30, base_b, 0.75)]
    tl = []
    rx = lambda d: d * tl_w / 30  # noqa: E731
    for d0, d1, col, op in seg:
        tl.append(svg.rect(rx(d0) + (2 if d0 else 0), 0, rx(d1) - rx(d0) - (2 if d0 else 0), 18, col, rx=4,
                           extra=f'opacity="{op}"'))
    for d in (0, 6, 27, 30):
        tl.append(svg.text(rx(d), 42, str(d), size=20, fill=t2,
                           anchor="middle" if d not in (0, 30) else ("start" if d == 0 else "end"), mono=True, nc=False))
    inner.append(f'<svg class="abs" style="left:{tl_x}px;top:{tl_y}px" width="{tl_w}" height="48">'
                 + "".join(tl) + "</svg>")
    legend = [("days 0 to 5", "one opening for every game", 1.0),
              ("day 6", "mid-game route, by the first two shops", 0.45),
              ("day 27", "endgame route", 0.75)]
    ly = 178
    for lab, txt, op in legend:
        inner.append(div(22, ly + 6, 14, 14, "", style=f"background:{base_b};opacity:{op};border-radius:3px"))
        inner.append(div(46, ly, 490, 28, f'<span class="mono s20 t1">{esc(lab)}</span>'
                                        f'<span class="s20 t2">&nbsp;&nbsp;{esc(txt)}</span>', fit=True, style="white-space:nowrap;overflow:hidden"))
        ly += 30
    inner.append(div(22, ly + 2, 500, 28, '<span class="s20 t2">64 shop pairs mapped to routes</span>'))
    inner.append(div(22, ly + 44, 500, 28, '<span class="s20 w6 t2">Public reactive layers on top</span>'))
    chips = "".join(chip(esc(c), extra_style="margin:0 8px 8px 0") for c in PUBLIC_LAYERS)
    inner.append(div(22, ly + 78, 520, 172, f'<div style="display:flex;flex-wrap:wrap">{chips}</div>', fit=True,
                     style="overflow:hidden"))
    bh = ly + 78 + 172 + 4
    h.append(card(theme, bx, by, bw, bh, "base", "".join(inner)))
    # aqua inset: patched inside the source
    iy = by + bh + 16
    pin = [div(18, 14, 516, 28, '<div style="display:flex;justify-content:space-between">'
                                '<span class="s20 w7 t1 caps">Source patches in <span class="nocaps">cha22</span></span>'
                                '<span class="s20 t2">off unless triggered</span></div>')]
    py = 50
    for txt, ver in PATCHES:
        pin.append(div(18, py, 500, 34, chip(f'{esc(txt)} <span class="mono t2">&nbsp;· {esc(ver)}</span>')))
        py += 40
    ih = py + 8
    h.append(card(theme, bx, iy, bw, ih, "fixes", "".join(pin), radius=12))
    # why this base
    wy = iy + ih + 16
    why = [div(20, 14, 500, 26, '<span class="htr">Why this base</span>'),
           div(20, 44, 500, 40, '<span class="s32 w8 t1">826 W / 14 L</span>'),
           div(20, 88, 516, 56, '<span class="s20 t2">cha22 with our first layer, against the 21 distinct codes '
                                'among the top 30 public notebooks (local)</span>', fit=True),
           div(20, 152, 516, 56, '<span class="s20 t2">Our own planner stalled at a live rating of 1014.5; '
                                 'the public route agents we uploaded reached 1992 to 2534.</span>', fit=True)]
    wh = 222
    h.append(card(theme, bx, wy, bw, wh, None, "".join(why), style="border-width:1px"))
    assert wy + wh <= HEIGHT - 84 - 10, wy + wh
    # ---------------- right column: wrappers
    h.append(div(CX, 180, 440, 28, '<span class="htr">Our wrappers · inner to outer</span>'))
    h.append(div(1044, 180, 500, 28, '<div class="s20 t2" style="text-align:right">each one edits the action of the one inside it</div>'))
    keys = [("selling", "selling"), ("fixes", "fixes and production"), ("wheat", "wheat arbitrage"),
            ("counter", "counter-arbitrage")]
    kh = "".join(f'<span class="s20 t2" style="white-space:nowrap"><span style="display:inline-block;width:14px;'
                 f'height:14px;border-radius:3px;background:{fam(theme, k)[0]};vertical-align:-1px;margin-right:8px">'
                 f'</span>{lab}</span>' for k, lab in keys)
    h.append(div(CX, 214, CW, 28, f'<div style="display:flex;gap:24px">{kh}</div>', fit=True))
    centers = []
    for i, (family, ic, title, ver, desc, big, ctx) in enumerate(WRAPPERS):
        y = CARD_Y0 + i * (CARD_H + CARD_GAP)
        b, _ = fam(theme, family)
        c = [div(24, 16, 32, 32, icon(ic, b)),
             div(70, 14, 470, 32, f'<span class="s24 w7 t1">{esc(title)}</span>'
                                  f'<span class="chip mono" style="height:30px;margin-left:12px;vertical-align:3px">{esc(ver)}</span>'),
             div(70, 52, 466, 56, f'<div class="s20 t2" style="line-height:1.3">{esc(desc)}</div>', fit=True),
             div(552, 14, 1.5, CARD_H - 28, "", style=f"background:{b};opacity:.35"),
             div(570, 14, 272, 36, f'<span class="s26 w8 t1">{esc(big)}</span>', fit=True),
             div(570, 52, 272, 56, f'<div class="s20 t2" style="line-height:1.3">{esc(ctx)}</div>', fit=True)]
        h.append(card(theme, CX, y, CW, CARD_H, family, "".join(c), bar=True))
        centers.append(y + CARD_H / 2)
    out_y = wy + wh - 52
    h.append(div(CX, out_y, CW, 52, '<div style="height:52px;border-radius:26px;background:var(--ink);color:var(--surface);'
                                    'display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700;letter-spacing:.04em">'
                                    'ACTION: one move per worker + up to 10 market orders</div>'))
    assert out_y + 52 <= HEIGHT - 84 - 10
    # rail and stubs
    ov.append(svg.arrow(bx + bw, centers[0], RAIL_X, centers[0], width=4, head=1))
    ov.append(svg.line(RAIL_X, centers[0] - 2, RAIL_X, out_y + 26 - 2, stroke=tok(theme, "arrow"), width=4, cap="butt"))
    ov.append(svg.arrow(RAIL_X - 2, out_y + 26, CX - 2, out_y + 26, width=4, head=14))
    for ca, cb in zip(centers, centers[1:]):
        ov.append(svg.tri(RAIL_X, (ca + cb) / 2 + 2, up=False, size=16, fill=tok(theme, "arrow")))
    for cy in centers:
        ov.append(svg.circle(RAIL_X, cy, 6, tok(theme, "arrow")))
        ov.append(svg.line(RAIL_X, cy, CX, cy, stroke=tok(theme, "arrow"), width=2))
    return "\n".join(h), "\n".join(ov)
