"""05 · THE STANDING: our live rank over the last days of submissions and the evaluation, then the final board."""
from datetime import datetime

from frame import X1, div, tok
import svg

NN = "05"
STEM = "standing"
TITLE = "The standing"
SUBTITLE = ("We were live #128 on Sep 26 and still inside silver on Oct 8; the final board put us 46 places below "
            "the silver line.")
TAG = "RESULT"
HEIGHT = 900
CAPTION = ("Live ranks from 18 leaderboard snapshots (docs/postmortem.md), dotted where snapshots are 3 or more days "
           "apart or the line crosses the deadline, where the time scale changes. Zones use the final cut-offs (#30, "
           "#507, #1014 of 10,148).")
ALT = ("Team 42's live rank from #128 on Sep 26 to #547 on Oct 16, still inside the silver zone on Oct 8; final "
       "board #553.")
ALLOW = [18, 10148]

Y0, Y1, R1 = 292, 756, 700            # rank 1 at Y0, rank 700 at Y1
LX0, LX1 = 150, 1010                  # Sep 26 00:00 .. Oct 1 00:00
RX0, PXD = 1050, 22                   # Oct 1 00:00, px per day
RX1 = RX0 + 16 * PXD                  # Oct 17 00:00
FX = 1440                             # final column
UPLOADS_T1 = ["v8", "v10", "v11", "V12_AventadorSVJ", "v12_19"]   # labels just above the plot
UPLOADS_T2 = ["v9", "V10_CarreraGT"]                              # labels one row higher


def ts(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M")


def body(theme, data):
    ink, t2, muted, surf = (tok(theme, k) for k in ("ink", "text2", "muted", "surface"))
    halo = tok(theme, "halo")
    ry = svg.lin(1, R1, Y0, Y1)
    sep26, oct1 = ts("2026-09-26 00:00"), ts("2026-10-01 00:00")

    def tx(t):
        if t < oct1:
            return LX0 + (LX1 - LX0) * (t - sep26).total_seconds() / (5 * 86400)
        return RX0 + PXD * (t - oct1).total_seconds() / 86400

    h, u, o = [], [], []
    # panel titles
    h.append(div(LX0, 180, 600, 28, '<span class="htr">Last days of submissions</span>'))
    h.append(div(RX0, 180, RX1 - RX0 + 20, 28, '<span class="htr">Evaluation · code frozen</span>', fit=True))
    h.append(div(FX - 16, 180, X1 - FX + 16, 28, '<span class="htr">Final</span>'))

    # zones (full width), grid, ticks
    for r0, r1, z in [(1, 30, "gold"), (30, 507, "silver"), (507, R1, "bronze")]:
        u.append(svg.rect(LX0, ry(r0), X1 - LX0, ry(r1) - ry(r0), tok(theme, f"{z}_wash")))
    for r in range(100, 701, 100):
        u.append(svg.line(LX0, ry(r), X1, ry(r), stroke=tok(theme, "grid"), width=1))
        u.append(svg.text(140, ry(r) + 7, f"#{r}", size=20, fill=t2, anchor="end", mono=True, nc=False))
    # the gutter between the two time scales
    u.append(svg.rect(LX1 + 4, Y0 - 2, RX0 - LX1 - 8, Y1 - Y0 + 4, surf))
    for zx in (LX1 + 14, LX1 + 24):
        u.append(svg.line(zx - 4, Y1 + 8, zx + 4, Y1 - 8, stroke=t2, width=1.5))
    for txt, rank, z, dy in (("GOLD (to #30)", 1, "gold", 16), ("SILVER (to #507)", 30, "silver", 26)):
        o.append(svg.text(RX1 - 4, ry(rank) + dy, txt, size=20, weight=700, fill=tok(theme, f"{z}_label"),
                          anchor="end", extra='letter-spacing="1"'))
    o.append(svg.text(RX1 - 4, Y1 - 10, "BRONZE (to #1014)", size=20, weight=700,
                      fill=tok(theme, "bronze_label"), anchor="end", extra='letter-spacing="1"'))
    ys = ry(507)
    o.append(svg.line(LX0, ys, LX1, ys, stroke=ink, width=1.5, opacity=0.45))
    o.append(svg.line(RX0, ys, X1, ys, stroke=ink, width=1.5, opacity=0.45))
    o.append(svg.text(LX0 + 8, ys - 10, "silver line · #507", size=20, weight=700, fill=ink))
    # x axis: dates on their midnight ticks
    for d in range(26, 31):
        x = tx(ts(f"2026-09-{d} 00:00"))
        u.append(svg.line(x, Y1, x, Y1 + 6, stroke=tok(theme, "axis"), width=1.5))
        o.append(svg.text(x, Y1 + 30, f"Sep {d}", size=20, fill=t2, anchor="start" if d == 26 else "middle", nc=False))
    for d in (1, 4, 8, 12, 16):
        x = tx(ts(f"2026-10-{d:02d} 00:00"))
        u.append(svg.line(x, Y1, x, Y1 + 6, stroke=tok(theme, "axis"), width=1.5))
        o.append(svg.text(x, Y1 + 30, f"Oct {d}", size=20, fill=t2, anchor="middle", nc=False))
    u.append(svg.line(LX0, Y1, LX1, Y1, stroke=tok(theme, "axis"), width=1.5))
    u.append(svg.line(RX0, Y1, RX1, Y1, stroke=tok(theme, "axis"), width=1.5))
    # deadline
    o.append(svg.line(LX1, Y0 - 10, LX1, Y1, stroke=t2, width=1.5))
    o.append(svg.text(LX1 - 10, Y1 - 12, "deadline · Sep 30 23:59 UTC", size=20, weight=700, fill=ink, anchor="end"))

    # uploads: triangles on the top edge, labels above the plot in two rows
    up = {r["version"]: ts(r["time_utc"]) for r in data["uploads"]}
    finals = {"V12_AventadorSVJ", "v12_19"}
    for tier, names, base in ((1, UPLOADS_T1, Y0 - 24), (2, UPLOADS_T2, Y0 - 52)):
        for v in names:
            x = tx(up[v])
            o.append(svg.tri(x, Y0 - 7, up=False, size=12, fill=ink))
            if tier == 2:
                o.append(svg.line(x, base + 6, x, Y0 - 14, stroke=t2, width=1.5))
            anchor = "start" if v == "V12_AventadorSVJ" else "middle"
            o.append(svg.text(x - (6 if anchor == "start" else 0), base, v, size=20, mono=True,
                              weight=700 if v in finals else 500, fill=ink if v in finals else t2, anchor=anchor))
    o.append(svg.tri(RX0 + 8, Y0 - 31, up=False, size=12, fill=ink))
    o.append(svg.rich(RX0 + 22, Y0 - 24, [("upload; ", 400, t2), ("bold", 700, ink), (": the final pair", 400, t2)],
                      size=20, nc=False))

    # series
    pts = [(tx(ts(r["time_utc"])), ry(int(r["rank"])), r) for r in data["standing"]]
    for (xa, ya, ra), (xb, yb, rb) in zip(pts, pts[1:]):
        gap = ts(rb["time_utc"]) - ts(ra["time_utc"])
        dotted = (xa < LX1 < xb) or gap.days >= 3
        o.append(svg.line(xa, ya, xb, yb, stroke=ink, width=2 if dotted else 3, dash="2 6" if dotted else None))
    for x, y, r in pts:
        o.append(svg.circle(x, y, 5, ink, stroke=surf, sw=2))
    xl, yl, _ = pts[-1]
    o.append(svg.text(xl + 6, yl + 30, "#547 live", size=20, fill=t2, anchor="end"))
    # final
    yf = ry(553)
    o.append(svg.circle(FX, yf, 14, halo))
    o.append(svg.circle(FX, yf, 8, ink, stroke=surf, sw=2))
    o.append(svg.text(FX + 22, yf + 8, "#553", size=22, weight=800, fill=ink))
    o.append(svg.text(FX - 16, yf + 44, "final board,", size=20, fill=t2))
    o.append(svg.text(FX - 16, yf + 68, "46 places", size=20, fill=t2))
    o.append(svg.text(FX - 16, yf + 92, "below silver", size=20, fill=t2))

    # annotations
    def at(time_s):
        for x, y, r in pts:
            if r["time_utc"] == time_s:
                return x, y
        raise KeyError(time_s)
    x, y = at("2026-09-26 10:23")
    o.append(svg.line(x, y + 8, x, 452, stroke=t2, width=1.5))
    h.append(div(x - 12, 458, 360, 84, '<div class="s20 w7 t1">#128 on Sep 26</div>'
                                       '<div class="s20 t2" style="line-height:1.3">v8 with TICK; its own rating had '
                                       'peaked at 2679 that morning</div>', fit=True))
    x, y = at("2026-09-29 13:32")
    o.append(svg.line(x, y + 8, x, 534, stroke=t2, width=1.5))
    h.append(div(x - 150, 540, 380, 84, '<div class="s20 w7 t1">#235 on Sep 29</div>'
                                        '<div class="s20 t2" style="line-height:1.3">20 W / 52 L against rival '
                                        'submissions uploaded after Sep 28 18:47</div>', fit=True))
    x, y = at("2026-10-08 06:58")
    o.append(svg.line(x + 4, y - 8, x + 14, y - 40, stroke=t2, width=1.5))
    h.append(div(x + 4, y - 96, RX1 - x, 56, '<div class="s20 w7 t1">#490 on Oct 8,</div>'
                                             '<div class="s20 t2">still inside silver</div>', fit=True))
    under = (f'<svg class="abs" style="left:0;top:0" width="1600" height="{HEIGHT}" viewBox="0 0 1600 {HEIGHT}" '
             f'xmlns="http://www.w3.org/2000/svg">' + "\n".join(u) + "</svg>")
    return under + "\n" + "\n".join(h), "\n".join(o)
