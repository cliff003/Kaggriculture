"""04 · THE FINAL BOARD: score by rank with medal zones and labelled teams; our win rate by opponent rank band."""
from frame import APPROACH, W, X0, X1, div, fmt, tok
import svg

NN = "04"
STEM = "final_board"
TITLE = "The final board"
SUBTITLE = "Silver was 15.3 points away, but above the silver line we won only one game in three."
TAG = "RESULT"
HEIGHT = 1060
CAPTION = ("Final leaderboard via the Kaggle API, Oct 16. Win rates: our two finals' 1,623 counted games after "
           "Sep 30 (one, against a team below #1014, left out); teams are ranked by their better submission, and we may "
           "have met either. Data: docs/figures/data/.")
ALT = ("Final board: team 42 at #553 with 4499.2, 15.3 below the silver line at #507; learned-policy teams at the "
       "top; after the deadline we won 33% against ranks 31 to 507 and 62% against 508 to 1014.")
ALLOW = [3000, 3001, 3900, 4000, 4500, 5000, 5500, 6000, 10148, 1623, 1014, 507, 300, 30]

PX0, PX1, PY0, PY1 = 150, 990, 312, 846       # plot box
S0, S1, RMAX = 3900, 6000, 3000


def body(theme, data):
    ink, t2, muted, hair = tok(theme, "ink"), tok(theme, "text2"), tok(theme, "muted"), tok(theme, "hairline")
    surf, card, halo = tok(theme, "surface"), tok(theme, "card"), tok(theme, "halo")
    col = {k: v[theme] for k, v in APPROACH.items()}
    board = [(int(r["rank"]), float(r["score"])) for r in data["final_board"]]
    labels = {int(r["rank"]): r for r in data["labels"]}
    xs = svg.logscale(1, RMAX, PX0, PX1)
    ys = svg.lin(S0, S1, PY1, PY0)
    h, o, u = [], [], []          # html, overlay svg (top), underlay svg (below the html cards)

    def pt(rank):
        return xs(rank), ys(float(labels[rank]["score"]))

    # ---------------- left: heading and legend
    h.append(div(X0, 170, 960, 30, '<span class="s22 w7 t1">Final score by rank</span>'
                                    '<span class="s20 t2">&nbsp;&nbsp;Bradley-Terry fit on wins, 10,148 teams; '
                                    'ranks 1 to 3,000, log scale</span>', fit=True))

    def key(c, ring=False):
        st = f"border:3px solid {c};background:transparent" if ring else f"background:{c}"
        return (f'<span style="display:inline-block;width:14px;height:14px;border-radius:7px;{st};'
                f'vertical-align:-1px;margin-right:8px"></span>')
    leg = [key(col["learned"]) + "learned from replays (published)", key(col["production"]) + "production-heavy",
           key(col["market"]) + "market play", '<span class="tm">(by our replay study)</span>']
    h.append(div(X0, 208, 960, 30, '<div style="display:flex;gap:20px;flex-wrap:nowrap">' +
                 "".join(f'<span class="s20 t2" style="white-space:nowrap">{l}</span>' for l in leg) + "</div>",
                 fit=True))

    # ---------------- medal washes and the tier row above the plot
    for r0, r1, z in [(1, 30, "gold"), (30, 507, "silver"), (507, 1014, "bronze")]:
        u.append(svg.rect(xs(r0), PY0, xs(r1) - xs(r0), PY1 - PY0, tok(theme, f"{z}_wash")))
    tiers = [(30, "GOLD · #30 · 5099.6", "gold", 266), (1014, "BRONZE · #1014 · 4398.5", "bronze", 266),
             (507, "SILVER · #507 · 4514.5", "silver", 294)]
    for rank, txt, z, base in tiers:
        x = xs(rank)
        u.append(svg.text(x - 8, base, txt, size=20, weight=700, fill=tok(theme, f"{z}_label"), anchor="end"))
        u.append(svg.line(x, base - 16, x, PY0, stroke=tok(theme, f"{z}_label"), width=1.5))

    # grid and axes
    for s in range(4000, 6001, 500):
        u.append(svg.line(PX0, ys(s), PX1, ys(s), stroke=tok(theme, "grid"), width=1))
        u.append(svg.text(PX0 - 12, ys(s) + 7, fmt(s), size=20, fill=muted, anchor="end", nc=False))
    u.append(svg.line(PX0, PY1, PX1, PY1, stroke=tok(theme, "axis"), width=1.5))
    for r in (1, 10, 30, 100, 300, 507, 1014, 3000):
        x = xs(r)
        u.append(svg.line(x, PY1, x, PY1 + 6, stroke=tok(theme, "axis"), width=1.5))
        u.append(svg.text(x, PY1 + 30, str(r), size=20, fill=muted, anchor="middle", nc=False))
    u.append(svg.text((PX0 + PX1) / 2, PY1 + 60, "final rank (log scale)", size=20, fill=t2, anchor="middle",
                      nc=False))
    u.append(svg.text(X0, PY0 - 18, "score", size=20, fill=t2, nc=False))

    # curve
    u.append(svg.polyline([(xs(r), ys(s)) for r, s in board if r <= RMAX], t2, width=2))

    # ---------------- points
    for rank, lab in labels.items():
        if rank > RMAX:
            continue
        x, y = pt(rank)
        ap = lab["approach"]
        if ap == "us":
            o.append(svg.circle(x, y, 14, halo))
            o.append(svg.circle(x, y, 8, ink, stroke=surf, sw=2))
        else:
            ap = "production" if ap == "production_np" else ap
            o.append(svg.circle(x, y, 7, col.get(ap, col["other"]), stroke=surf, sw=2))

    # learned cluster: one callout box in the empty upper right, one leader to the cluster
    names = ["#1 M &amp; M &amp; P &amp; Q", "#4 Farmcore", "#5 有辣条有权", "#7 DECEM", "#12 Unknown Mother-Goose",
             "#13 MarvinTMB", "#24 abozten"]
    learned = ", ".join(f'<span style="white-space:nowrap">{n}</span>' for n in names)
    bx0, by0, bw = 538, 326, 448
    h.append(div(bx0, by0, bw, 200,
                 '<div class="s20 w7 t1" style="line-height:1.3">Top 25 with a published method: '
                 'all learned from replays</div>'
                 '<div class="s20 t2" style="line-height:1.3;margin-top:6px">' + learned + '</div>', fit=True,
                 style=f"padding:12px 16px;border-radius:10px;border:2px solid {col['learned']};background:{card}"))
    x24, y24 = pt(24)
    o.append(svg.line(bx0, 452, x24 + 9, y24 - 7, stroke=col["learned"], width=2))

    # production (labels around the dots, away from the curve)
    x3, y3 = pt(3)
    o.append(svg.text(x3 + 16, y3 - 30, "#3 DSM", size=20, fill=ink))
    o.append(svg.text(x3 + 16, y3 - 6, "method not published", size=20, fill=t2))
    x21, y21 = pt(21)
    o.append(svg.leader(x21 - 4, y21 + 9, x21 - 18, y21 + 32, dot=False))
    o.append(svg.text(x21 - 18, y21 + 54, "#21 Vadim Vasilenko", size=20, fill=ink, anchor="end"))
    x54, y54 = pt(54)
    o.append(svg.leader(x54 - 6, y54 + 8, x54 - 20, y54 + 26, dot=False))
    o.append(svg.text(x54 - 20, y54 + 48, "#54 unreal", size=20, fill=ink, anchor="end"))
    x76, y76 = pt(76)
    o.append(svg.leader(x76 - 2, y76 + 10, x76 - 4, y76 + 50, dot=False))
    o.append(svg.text(x76 - 4, y76 + 72, "#76 Ryo Hasegawa", size=20, fill=ink, anchor="end"))
    o.append(svg.text(x76 - 4, y76 + 96, "replay base with tomatoes", size=20, fill=t2, anchor="end"))

    # market
    x92, y92 = pt(92)
    o.append(svg.leader(x92 + 2, y92 - 10, x92 + 6, y92 - 34, dot=False))
    o.append(svg.text(x92 - 8, y92 - 66, "#92 Otter Vibe", size=20, fill=ink))
    o.append(svg.text(x92 - 8, y92 - 42, "where we learned TICK", size=20, fill=t2))
    xa, xb = pt(429)[0], pt(802)[0]
    ytop = min(pt(r)[1] for r in (429, 464, 681, 802)) - 16
    o.append(f'<path d="M{xa - 8:.1f} {ytop + 8:.1f} V{ytop:.1f} H{xb + 8:.1f} V{ytop + 8:.1f}" fill="none" '
             f'stroke="{t2}" stroke-width="1.5"/>')
    o.append(svg.line((xa + xb) / 2, ytop, (xa + xb) / 2, ytop - 10, stroke=t2, width=1.5))
    o.append(svg.text(PX1, ytop - 42, "#429 to #802: four teams", size=20, fill=ink, anchor="end"))
    o.append(svg.text(PX1, ytop - 18, "that traded against TICK", size=20, fill=t2, anchor="end"))

    # team 42 (empty lower left)
    xu, yu = pt(553)
    cx0, cy0, cw = 466, 718, 282
    h.append(div(cx0, cy0, cw, 62, '<div class="s22 w8 t1" style="line-height:1.3">team 42 · #553 · 4499.2</div>'
                                   '<div class="s20 t2" style="line-height:1.3">15.3 below silver: 46 places</div>',
                 fit=True))
    o.append(svg.line(cx0 + cw + 6, cy0 + 14, xu - 11, yu + 9, stroke=ink, width=1.5))

    # author of the base
    xa2, ya2 = pt(2142)
    o.append(svg.leader(xa2 - 5, ya2 + 6, xa2 - 12, ya2 + 18, dot=False))
    o.append(svg.text(xa2 - 12, ya2 + 40, "#2142 Abhinav0370", size=20, fill=ink, anchor="end"))
    o.append(svg.text(xa2 - 12, ya2 + 64, "author of cha22, our base", size=20, fill=t2, anchor="end"))

    # ---------------- right: win rate by opponent rank band
    RX = 1040
    h.append(div(RX, 170, X1 - RX, 30, '<span class="s22 w7 t1">Our games after the deadline</span>'))
    h.append(div(RX, 206, X1 - RX, 28, '<span class="s20 t2">win rate by opponent\'s final rank, 90% intervals</span>',
                 fit=True))
    bands = [b for b in data["winrate_bands"] if int(b["lo"]) < 1015]
    gx = svg.lin(0, 100, RX + 218, X1 - 76)
    y = 262
    o.append(svg.text(RX, y, "opponents", size=20, fill=muted, nc=False))
    o.append(svg.text(RX + 190, y, "games", size=20, fill=muted, anchor="end", nc=False))
    o.append(svg.text(X1, y, "won", size=20, fill=muted, anchor="end", nc=False))
    for v in (0, 50, 100):
        o.append(svg.text(gx(v), y, f"{v}%", size=20, fill=muted, anchor="middle", nc=False))
    y += 14
    row_h = 46
    for b in bands:
        lo, hi = int(b["lo"]), int(b["hi"])
        if lo == 508:
            o.append(svg.line(RX - 6, y + 4, X1 + 6, y + 4, stroke=ink, width=1.5))
            o.append(svg.text(RX, y + 30, "silver line · #507", size=20, weight=700, fill=ink, nc=False))
            y += 40
        if lo == 554:
            o.append(svg.line(RX - 6, y + 4, X1 + 6, y + 4, stroke=ink, width=1.5, dash="6 5"))
            o.append(svg.circle(RX + 8, y + 23, 9, halo))
            o.append(svg.circle(RX + 8, y + 23, 5, ink))
            o.append(svg.text(RX + 28, y + 30, "team 42 · #553", size=20, weight=700, fill=ink, nc=False))
            y += 40
        wash = tok(theme, "silver_wash") if hi <= 507 else tok(theme, "bronze_wash")
        o.append(svg.rect(RX - 6, y + 2, X1 - RX + 12, row_h - 4, wash, rx=6))
        cy = y + row_h / 2
        o.append(svg.text(RX + 6, cy + 7, f"#{lo} to #{hi}", size=20, fill=ink, nc=False))
        o.append(svg.text(RX + 190, cy + 7, fmt(int(b["games"])), size=20, fill=t2, anchor="end", nc=False))
        o.append(svg.line(gx(50), y + 6, gx(50), y + row_h - 6, stroke=muted, width=1.5, dash="3 4"))
        lo_ci, hi_ci, win = int(b["ci_lo"]), int(b["ci_hi"]), int(b["win"])
        o.append(svg.line(gx(lo_ci), cy, gx(hi_ci), cy, stroke=ink, width=2))
        if gx(hi_ci) - gx(lo_ci) > 18:
            o.append(svg.line(gx(lo_ci), cy - 6, gx(lo_ci), cy + 6, stroke=ink, width=2))
            o.append(svg.line(gx(hi_ci), cy - 6, gx(hi_ci), cy + 6, stroke=ink, width=2))
        few = int(b["games"]) < 10
        o.append(svg.circle(gx(win), cy, 5, surf if few else ink, stroke=ink, sw=2))
        o.append(svg.text(X1, cy + 7, f"{win}%", size=20, weight=400 if few else 700, fill=muted if few else ink,
                          anchor="end", nc=False))
        y += row_h
    y += 16
    h.append(div(RX, y, X1 - RX, 28, '<span class="s20 w7 t1">Silver zone #31 to #507:</span>'
                                     '<span class="s20 t2"> 233 W / 472 L, 33%</span>', fit=True))
    h.append(div(RX, y + 30, X1 - RX, 28, '<span class="s20 w7 t1">Bronze zone #508 to #1014:</span>'
                                          '<span class="s20 t2"> 572 W / 344 L / 1 D, 62%</span>', fit=True))
    h.append(div(RX, y + 60, X1 - RX, 28, '<span class="s20 tm">hollow dot: 3 games, too few to read</span>',
                 fit=True))
    assert y + 90 <= HEIGHT - 84 - 6, y + 90
    under = (f'<svg class="abs" style="left:0;top:0" width="{W}" height="{HEIGHT}" viewBox="0 0 {W} {HEIGHT}" '
             f'xmlns="http://www.w3.org/2000/svg">' + "\n".join(u) + "</svg>")
    return under + "\n" + "\n".join(h), "\n".join(o)
