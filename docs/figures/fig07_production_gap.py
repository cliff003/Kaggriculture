"""07 · THE PRODUCTION GAP: the top five against cha22, unreal against our final agent, and what we tried."""
from frame import X0, X1, card, div, esc, fam, section_bar, tok
import svg

NN = "07"
STEM = "production_gap"
TITLE = "The production gap"
SUBTITLE = "The teams above us out-produced us (tomatoes, geese, early land); our attempts to copy them fell far short."
TAG = "POST-MORTEM"
HEIGHT = 1264
CAPTION = ("Sources: docs/postmortem.md (The gap to the top), docs/experiments.md (New engines, Copying the top teams). "
           "On replay: unreal's live games with our agent in its opponents' seats; unreal plays its recorded moves.")
ALT = ("The top five against cha22 (tomatoes in 98% of games against 11%), unreal against our final agent (66 to 9 on "
       "replays; +6.2k eggs, +3.6k strawberries, +3.2k carrots a game) and our failed attempts to close the gap.")
ALLOW = [6, 7, 10, 12, 14, 40, 60, 70, 7.3]

TOP5 = [
    ("Games with tomatoes", "98%", "11%", "top five: about 10 tiles, days 18 to 20"),
    ("Geese on day 15", "5", "3", ""),
    ("Fertilizer applications", "204", "117", "top five bought none; cha22 bought 88, sold 336"),
    ("Idle helper steps", "190", "471", ""),
    ("Cash on day 9", "261", "2,833", "top five: everything invested"),
    ("Final money", "109.8k", "100.4k", "about, per game"),
]
EARNED = [("eggs", 6.2), ("strawberries", 3.6), ("carrots", 3.2), ("wheat", 1.5)]
FARM = [  # label, unreal, us, lo, hi, fmt
    ("Second land bought on day", 8, 11, 0, 14, "{:g}"),
    ("Peak geese", 8.4, 2.6, 0, 10, "{:g}"),
    ("Tiles in use by day 8", 65.5, 50, 0, 80, "{:g}"),
]
TRIED = [
    ("-11.5k a game", "local: the best of about 60 from-scratch schedulers, vs cha22"),
    ("0 wins", "local: cloning DSM (final #3), 0.88 action accuracy, vs cha22 and v9"),
    ("-7.9k a game", "local: our production agent p6 vs v7c"),
    ("-19.1k a game", "on replay: p6 running a strong team's own plan (that team: +7.3k)"),
]


def body(theme, data):
    ink, t2, muted, surf = (tok(theme, k) for k in ("ink", "text2", "muted", "surface"))
    aq, aq_t = fam(theme, "fixes")
    grey, _ = fam(theme, "base")
    halo, down = tok(theme, "halo"), tok(theme, "down")
    h, o = [], []

    # ================= A
    h.append(section_bar(180, "A", "The live top five (Sep 22) against <span class='nocaps'>cha22</span>",
                         "547 player-games", aq, raw=True))
    CW, CH, GX, GY = 480, 124, 24, 12
    for i, (lab, top, base, note) in enumerate(TOP5):
        x = X0 + (i % 3) * (CW + GX)
        y = 240 + (i // 3) * (CH + GY)

        def val(mini, v, color, ul):
            return (f'<div style="display:flex;flex-direction:column;margin-right:26px">'
                    f'<span class="s20 t2" style="line-height:1.2">{mini}</span>'
                    f'<span class="s32 w8 tnum" style="color:{color};line-height:1.15;border-bottom:4px solid {ul};'
                    f'padding-bottom:2px;align-self:flex-start">{v}</span></div>')
        inner = (f'<div class="fit" style="position:absolute;inset:0;padding:12px 18px">'
                 f'<div class="htr" style="margin-bottom:6px">{esc(lab)}</div>'
                 f'<div style="display:flex;align-items:flex-end">{val("top five", top, ink, aq)}'
                 f'{val("cha22", base, t2, grey)}'
                 f'<div class="s20 t2" style="line-height:1.25;flex:1;padding-bottom:4px">{esc(note)}</div></div></div>')
        h.append(card(theme, x, y, CW, CH, None, inner))

    # ================= B
    SB = 530
    h.append(section_bar(SB, "B", "<span class='nocaps'>unreal</span> (final #54) against our final agent",
                         "on replay: 75 of unreal's live games, our agent in its opponents' seats", aq, raw=True))
    ly = SB + 58
    us_dot = (f'<span style="display:inline-block;width:14px;height:14px;border-radius:7px;background:{ink};'
              f'box-shadow:0 0 0 4px {halo};vertical-align:-1px;margin:0 10px 0 4px"></span>')
    aq_dot = (f'<span style="display:inline-block;width:14px;height:14px;border-radius:7px;background:{aq};'
              f'vertical-align:-1px;margin-right:8px"></span>')
    h.append(div(X0, ly, X1 - X0, 28, f'<div style="display:flex;gap:28px"><span class="s20 t2">{aq_dot}unreal '
                                      f'(production planner)</span><span class="s20 t2">{us_dot}our final agent '
                                      f'(v12_15, the code of V12_AventadorSVJ)</span></div>', fit=True))
    cy, chh = ly + 40, 326
    # B1 wins
    b1 = (f'<div class="fit" style="position:absolute;inset:0;padding:14px 18px">'
          f'<div class="htr" style="margin-bottom:8px">Wins</div>'
          f'<div style="display:flex;align-items:center;gap:12px;line-height:1">'
          f'<span style="width:18px;height:18px;border-radius:9px;background:{aq}"></span>'
          f'<span class="s64 w8 t1 tnum">66</span><span class="s44 w8 tm">:</span>'
          f'<span style="width:18px;height:18px;border-radius:9px;background:{ink};box-shadow:0 0 0 4px {halo}"></span>'
          f'<span class="s64 w8 t1 tnum">9</span></div>'
          f'<div class="s20 t2" style="margin-top:6px">unreal : our final agent</div>'
          f'<div class="s20 t2">on replay, 75 games</div>'
          f'<div class="s20 t2" style="margin-top:12px;line-height:1.3">V10_CarreraGT (replaced Sep 30) also won 9.</div>'
          f'<div class="s20 t2" style="margin-top:8px;line-height:1.3">Live: unreal went 28 W / 3 L against '
          f'cha22-based farms, +15.7k a game.</div></div>')
    h.append(card(theme, X0, cy, 340, chh, None, b1))
    # B2 bars
    bx, bw = 420, 580
    h.append(card(theme, bx, cy, bw, chh, None,
                  '<div style="padding:14px 18px"><div class="htr">Where unreal earned more, per game</div></div>'))
    lx0, lx1 = bx + 160, bx + bw - 90
    sc = svg.lin(0, 7, lx0, lx1)
    by0 = cy + 62
    for v in (0, 2, 4, 6):
        o.append(svg.line(sc(v), by0 - 8, sc(v), by0 + 4 * 42 - 8, stroke=tok(theme, "hairline"), width=1))
        o.append(svg.text(sc(v), by0 + 4 * 42 + 14, "0" if v == 0 else f"{v}k", size=20, fill=muted,
                          anchor="middle", nc=False))
    for i, (g, v) in enumerate(EARNED):
        y = by0 + i * 42
        o.append(svg.text(lx0 - 14, y + 21, g, size=20, fill=ink, anchor="end", nc=False))
        o.append(svg.rect(lx0, y + 4, sc(v) - lx0, 24, aq, rx=4))
        o.append(svg.text(sc(v) + 10, y + 23, f"+{v}k", size=20, weight=700, fill=ink, nc=False))
    h.append(div(bx + 18, cy + chh - 38, bw - 36, 28,
                 '<span class="s20 t2">We were ahead only in milk, melons and tomatoes.</span>', fit=True))
    # B3 dumbbells
    dx, dw = 1024, X1 - 1024
    h.append(card(theme, dx, cy, dw, chh, None,
                  '<div style="padding:14px 18px"><div class="htr">How its farm differed</div></div>'))
    mx0, mx1 = dx + 70, dx + dw - 70
    for i, (lab, un, us, lo, hi, f) in enumerate(FARM):
        y = cy + 64 + i * 84
        o.append(svg.rich(dx + 18, y + 16, [(lab, 600, ink), (f"  scale {f.format(lo)} to {f.format(hi)}", 400, muted)],
                          size=20, nc=False))
        s = svg.lin(lo, hi, mx0, mx1)
        yy = y + 44
        o.append(svg.line(s(lo), yy, s(hi), yy, stroke=tok(theme, "axis"), width=1.5))
        for v_ in (lo, hi):
            o.append(svg.line(s(v_), yy - 5, s(v_), yy + 5, stroke=tok(theme, "axis"), width=1.5))
        o.append(svg.line(s(un), yy, s(us), yy, stroke=grey, width=3))
        o.append(svg.circle(s(us), yy, 10, halo))
        o.append(svg.circle(s(us), yy, 6, ink, stroke=surf, sw=1.5))
        o.append(svg.circle(s(un), yy, 7, aq, stroke=surf, sw=2))
        lo_v, hi_v = (un, us) if un < us else (us, un)
        knock = f'paint-order="stroke" stroke="{tok(theme, "card")}" stroke-width="8" stroke-linejoin="round"'
        o.append(svg.text(s(lo_v) - 16, yy + 7, f.format(lo_v), size=20, weight=700, fill=ink, anchor="end", nc=False,
                          extra=knock))
        o.append(svg.text(s(hi_v) + 16, yy + 7, f.format(hi_v), size=20, weight=700, fill=ink, nc=False, extra=knock))

    # ================= C
    SC = cy + chh + 26
    h.append(section_bar(SC, "C", "What we tried to close it", "docs/experiments.md", aq))
    tw, tg = 357, 20
    for i, (num, txt) in enumerate(TRIED):
        x = X0 + i * (tw + tg)
        inner = (f'<div class="fit" style="position:absolute;inset:0;padding:12px 16px">'
                 f'<div style="display:flex;align-items:center;gap:10px">'
                 f'<span style="color:{down};font-size:20px">▼</span>'
                 f'<span class="s26 w8 t1">{esc(num)}</span></div>'
                 f'<div class="s20 t2" style="line-height:1.3;margin-top:4px">{esc(txt)}</div></div>')
        h.append(card(theme, x, SC + 60, tw, 124, None, inner))
    assert SC + 184 <= HEIGHT - 84 - 16, SC + 184
    return "\n".join(h), "\n".join(o)
