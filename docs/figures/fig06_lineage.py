"""06 · LINEAGE: all uploads and packages in four lanes, from the first planner to the final board."""
from frame import BAND, X0, X1, div, esc, fam, tok
import svg

NN = "06"
STEM = "lineage"
TITLE = "Lineage"
SUBTITLE = "39 uploads and 34 packages: the live line changed a few layers per upload; the FADE line was held back."
TAG = "HISTORY"
CAPTION = ("Sources: docs/history.md (uploads, frozen live ratings), docs/changelog_0927_1016.md (build times), "
           "submissions/README.md (34 packages). Ratings are live ratings; the final Bradley-Terry score uses another "
           "scale. The Oct cards repeat the two finals.")
ALT = ("Lineage of all 39 uploads and 34 packages from Sep 16 to Oct 16, ending with the final pair "
       "V12_AventadorSVJ and v12_19 and the final board #553.")
ALLOW = [2240, 433.5, 23, 59]

LANES = [("pre", "base", "Starting points", "own planner, then public code"),
         ("live", "selling", "Live line", "order-slot, then layers"),
         ("public", "wheat", "Public line", "no FADE; built on v10"),
         ("ace", "counter", "Ace line", "FADE, held back")]
LW, LG, LX = 318, 20, 208
DATE_X = X0
UP_H, ONE_H, SEALED_H, GAP, PAD = 72, 44, 44, 8, 12
ROWS_TOP = 180 + 64 + 12 + 48 + 16

# item kinds: up (version, right, change[, key]), one (version, right[, key]), sealed (version, change[, sub lines,
# key]), rej (version, change), note (text)
ROWS = [
    ("Sep 16 to 21", {"pre": [("up", "Frank v1 to v19", "1014.5", "own planner, 19 uploads"),
                              ("note", "later lost all 2,240 local games to public agents (Sep 24)")]}),
    ("Sep 22 to 23", {"pre": [("one", "farm2945", "1992.1"), ("one", "rescue", "2534.0", "k_rescue"),
                              ("one", "morewheat", "2368.5"), ("one", "herdsafe_race", "2317.6")],
                      "callout": ("Same code, two days apart.", "rescue uploaded on Sep 22 froze at 2534.0; the same code "
                                  "uploaded on Sep 24 reached 2100.5. After that we compared ratings only within one "
                                  "window.")}),
    ("Sep 24", {"pre": [("up", "rescue", "2100.5", "Sep 22 code, 433.5 lower"),
                        ("up", "cha22", "2333.4", "the base we chose", "k_cha22")],
                "live": [("up", "v3", "2180.5", "rescue + order-slot", "k_v3"),
                         ("up", "v4", "2504.5", "cha22 + order-slot", "k_v4")]}),
    ("Sep 25", {"live": [("up", "v6", "2419.1", "+ eager sell, sell ordering"),
                         ("up", "v7", "2111.7*", "band 0.2× to 1.4× + wheat lead"),
                         ("up", "v6b", "2311.1*", "v6 without eager ceiling"),
                         ("up", "v7b", "2590.8", "+ wheat lead"),
                         ("up", "v7c", "2563.5", "+ base fixes")],
                "callout": ("Only the 2 latest uploads play.", "Each new upload retires the older one and freezes its "
                            "rating; * marks a version replaced while still climbing.")}),
    ("Sep 26", {"live": [("up", "v8", "2545.4", "+ TICK  · peak 2679", "k_v8"),
                         ("up", "v9", "2490.6", "+ trap guard")],
                "ace": [("sealed", "v12", "v8 + FADE", None, "k_v12"), ("sealed", "v12_1", "TICK from day 13"),
                        ("sealed", "v12_2", "+ scheduled fade"), ("sealed", "v12_3", "+ trap guard")]}),
    ("Sep 27", {"live": [("up", "v10", "2494.4", "+ tomato gate", "k_v10")],
                "public": [("sealed", "v11a", "+ pre-buy trap rule", None, "k_v11a")],
                "ace": [("sealed", "v12_4", "+ tomato gate"), ("sealed", "v12_5", "+ P&L guard"),
                        ("sealed", "v12_6", "+ fade phases 1 to 3"), ("sealed", "v12_7", "+ pre-buy trap rule")]}),
    ("Sep 28", {"public": [("up", "v11", "2021.5*", "+ harvest deferral, rev_guard"),
                           ("up", "V10_CarreraGT", "2206.9", "+ 18 tomatoes, TICK day 8", "k_carrera")],
                "ace": [("sealed", "v12_8", "+ harvest deferral"),
                        ("sealed", "v12_9 to v12_14", "6 builds",
                         ["fade size, wind-down,", "room, sell cap", "<s>v12_10</s> rejected"]),
                        ("sealed", "v12_15", "+ 18 tomatoes", None, "k_v1215"),
                        ("up", "V12_AventadorSVJ", "", "= v12_15, uploaded 18:47"),
                        ("rej", "v12_16", "+ strawberry block")]}),
    ("Sep 29", {"ace": [("sealed", "v12_17", "+ sheep cash reserve")]}),
    ("Sep 30", {"public": [("note", "V10_CarreraGT replaced by v12_19 (uploaded 16:41)")],
                "ace": [("sealed", "v12_18", "+ late tomato crews"),
                        ("up", "v12_19", "16:41", "+ layout-adaptive fertilizer")]}),
    ("DEADLINE", {}),
    ("Oct 1 to 16", {"span": "Code frozen; both finals played on for two weeks. A team is ranked by its better "
                             "submission.",
                     "ace": [("up", "V12_AventadorSVJ", "2046.0", "final live rating"),
                             ("up", "v12_19", "2065.7", "final live rating, team best")]}),
    ("Final, Oct 16", {"final": True}),
]


def item_h(it):
    k = it[0]
    if k == "up":
        return UP_H
    if k == "one":
        return ONE_H
    if k == "sealed":
        return SEALED_H + (26 * len(it[3]) if len(it) > 3 and it[3] else 0)
    if k == "rej":
        return SEALED_H
    if k == "note":
        return 56
    raise ValueError(k)


def lane_x(i):
    return LX + i * (LW + LG)


def layout():
    y = ROWS_TOP
    out = []
    for label, lanes in ROWS:
        if label == "DEADLINE":
            out.append((label, lanes, y, 44))
            y += 44
            continue
        if lanes.get("final"):
            out.append((label, lanes, y, 96))
            y += 96
            continue
        hmax = 44
        for key, *_ in LANES:
            items = lanes.get(key, [])
            hmax = max(hmax, sum(item_h(it) for it in items) + GAP * max(0, len(items) - 1))
        if "span" in lanes:
            hmax = max(hmax, 2 * UP_H + GAP)
        out.append((label, lanes, y, hmax + 2 * PAD))
        y += hmax + 2 * PAD
    return out, y + 24 + 84


ROW_LAYOUT, HEIGHT = layout()


def body(theme, data):
    ink, t2, muted, hair, surf, cardc = (tok(theme, k) for k in ("ink", "text2", "muted", "hairline", "surface", "card"))
    h, u, o = [], [], []
    pos = {}

    # lane headers
    for i, (key, fm, title, sub) in enumerate(LANES):
        b, t = fam(theme, fm)
        h.append(div(lane_x(i), 180, LW, 64,
                     f'<div class="s20 w7 caps t1">{esc(title)}</div><div class="s20 t2">{esc(sub)}</div>',
                     style=f"background:{t};border:2px solid {b};border-radius:10px;padding:6px 14px", fit=True))
    # how to read
    smp = "display:inline-block;width:30px;height:18px;border-radius:5px;vertical-align:-3px;margin-right:8px;"
    legend = ['<span class="htr" style="margin-right:6px">How to read</span>',
              f'<span style="{smp}border:2px solid {t2}"></span>ran live; rating frozen when replaced',
              '<b class="t1">*</b>&nbsp;replaced while still climbing',
              f'<span style="{smp}border:2px dashed {t2}"></span>sealed, not uploaded',
              '<s>struck</s>&nbsp;rejected', 'colour = line']
    h.append(div(DATE_X, 256, X1 - DATE_X, 48,
                 '<div style="display:flex;gap:24px;align-items:center;height:100%;padding:0 18px">' +
                 "".join(f'<span class="s20 t2" style="white-space:nowrap">{l}</span>' for l in legend) + "</div>",
                 style=f"background:{cardc};border:1px solid {tok(theme, 'frame')};border-radius:10px", fit=True))

    # rows
    for ri, (label, lanes, y, rh) in enumerate(ROW_LAYOUT):
        if label == "DEADLINE":
            u.append(svg.line(DATE_X + 296, y + 22, X1, y + 22, stroke=ink, width=2, dash="8 6"))
            h.append(div(DATE_X, y + 8, 290, 28, '<span class="s20 w7 t1">deadline Sep 30 23:59 UTC</span>'))
            continue
        band = surf if ri % 2 == 0 else tok(theme, "band_alt")
        u.append(svg.rect(DATE_X - 8, y, X1 - DATE_X + 16, rh, band))
        u.append(svg.line(DATE_X - 8, y, X1 + 8, y, stroke=hair, width=1))
        if lanes.get("final"):
            fy = y + 14
            h.append(div(DATE_X, fy + 20, 150, 30, f'<span class="s22 w7 t1">{label}</span>'))
            ring = tok(theme, "bronze_label")
            border = "border:1.5px solid #3a557d;" if theme == "dark" else ""
            h.append(div(LX, fy, X1 - LX, 68,
                         f'<div style="display:flex;align-items:center;gap:16px;height:100%;padding-left:22px">'
                         f'<span style="width:18px;height:18px;border-radius:9px;background:#ffffff;'
                         f'box-shadow:0 0 0 5px {ring}"></span>'
                         f'<span class="s24 w8" style="color:#ffffff;letter-spacing:.04em">FINAL BRADLEY-TERRY BOARD · '
                         f'#553 OF 10,148 · SCORE 4499.2 · BRONZE</span></div>',
                         style=f"background:{BAND['fill']};border-radius:12px;{border}", fit=True))
            continue
        h.append(div(DATE_X, y + PAD + 2, 140, 30, f'<span class="s22 w7 t1">{label}</span>'))
        if "span" in lanes:
            h.append(div(LX, y + PAD, 3 * LW + 2 * LG, 2 * UP_H + GAP,
                         f'<div class="s20 t2" style="line-height:1.35;max-width:640px">{esc(lanes["span"])}</div>',
                         style="display:flex;align-items:center;padding:0 16px", fit=True))
        if "callout" in lanes:
            lead, text = lanes["callout"]
            h.append(div(lane_x(2), y + PAD, 2 * LW + LG, 132,
                         f'<div class="s20 w7 t1">{esc(lead)}</div>'
                         f'<div class="s20 t2" style="line-height:1.3;margin-top:2px">{esc(text)}</div>',
                         style=f"background:{cardc};border:1px solid {tok(theme, 'frame')};border-radius:10px;"
                               "padding:12px 16px", fit=True))
        for li, (key, fm, *_x) in enumerate(LANES):
            b, t = fam(theme, fm)
            cy = y + PAD
            for it in lanes.get(key, []):
                k = it[0]
                ih = item_h(it)
                x = lane_x(li)
                key_ = None
                if k in ("up", "one"):
                    ver, right = it[1], it[2]
                    change = it[3] if k == "up" else None
                    key_ = it[4] if k == "up" and len(it) > 4 else (it[3] if k == "one" and len(it) > 3 else None)
                    star = right.endswith("*")
                    rv = right.rstrip("*")
                    is_time = ":" in rv
                    rhtml = ("" if not rv else f'<span class="s20 t2">uploaded {rv}</span>' if is_time else
                             f'<span class="s22 w8 t1 tnum">{rv}{"*" if star else ""}</span>')
                    l2 = f'<div class="s20 t2" style="line-height:1.25;margin-top:2px">{esc(change)}</div>' if change else ""
                    h.append(div(x, cy, LW, ih,
                                 f'<div style="display:flex;justify-content:space-between;align-items:baseline">'
                                 f'<span class="mono s20 w7 t1">{esc(ver)}</span>{rhtml}</div>{l2}',
                                 style=f"background:{t};border:2px solid {b};border-radius:10px;padding:6px 12px",
                                 fit=True))
                elif k in ("sealed", "rej"):
                    ver, change = it[1], it[2]
                    sub = it[3] if k == "sealed" and len(it) > 3 else None
                    key_ = it[4] if k == "sealed" and len(it) > 4 else None
                    strike = "text-decoration:line-through;" if k == "rej" else ""
                    vcls = "tm" if k == "rej" else "t1"
                    ccls = "tm" if k == "rej" else "t2"
                    s2 = "".join(f'<div class="s20 t2">{x_}</div>' for x_ in (sub or []))
                    h.append(div(x, cy, LW, ih,
                                 f'<div style="{strike}white-space:nowrap"><span class="mono s20 w7 {vcls}">{esc(ver)}</span>'
                                 f'<span class="s20 {ccls}"> · {esc(change)}</span></div>{s2}',
                                 style=f"background:{cardc};border:2px dashed {b if k == 'sealed' else muted};"
                                       f"border-radius:10px;padding:7px 12px", fit=True))
                elif k == "note":
                    h.append(div(x, cy, LW, ih, f'<div class="s20 t2" style="line-height:1.3">{esc(it[1])}</div>',
                                 style="padding:2px 4px", fit=True))
                if key_:
                    pos[key_] = (x, cy, LW, ih)
                cy += ih + GAP

    # connectors, anchored at the first text line of each card; cards and chips mask them
    def a_right(k):
        x, y, w, hh = pos[k]
        return x + w, y + 22

    def a_left(k):
        x, y, w, hh = pos[k]
        return x, y + 22

    def arrow_path(d, end, ang):
        u.append(svg.path_arrow(d, end, ang, color=t2, width=2.5, head=12, dash="6 4"))

    def pill(x, y, w, text, justify="center"):
        h.append(div(x, y - 17, w, 34, f'<span class="chip" style="color:{t2}">{esc(text)}</span>',
                     style=f"display:flex;justify-content:{justify}"))

    # rescue (Sep 22) to v3: across into the empty live lane, then down into v3's top edge
    x1, y1 = a_right("k_rescue")
    vx, vy, vw, vh = pos["k_v3"]
    xd = vx + 46
    arrow_path(f"M{x1:.1f} {y1:.1f} H{xd:.1f} V{vy - 2:.1f}", (xd, vy - 1), 90)
    # same-row links
    for a, b in (("k_cha22", "k_v4"), ("k_v10", "k_v11a")):
        (x1, y1), (x2, y2) = a_right(a), a_left(b)
        arrow_path(f"M{x1:.1f} {y1:.1f} H{x2 - 2:.1f}", (x2 - 1, y2), 0)
    (x1, y1), (x2, y2) = a_right("k_v8"), a_left("k_v12")
    arrow_path(f"M{x1:.1f} {y1:.1f} H{x2 - 2:.1f}", (x2 - 1, y2), 0)
    pill(lane_x(2) + 24, y1, LW - 48, "fork, kept off the ladder")
    # CarreraGT to v12_15: down from the card, then right; pill on the horizontal run
    x, y, w, hh = pos["k_carrera"]
    tx, ty = a_left("k_v1215")
    px = x + 60
    arrow_path(f"M{px:.1f} {y + hh:.1f} V{ty:.1f} H{tx - 2:.1f}", (tx - 1, ty), 0)
    pill(px + 20, ty, tx - px - 40, "18 tomatoes ported")

    under = (f'<svg class="abs" style="left:0;top:0" width="1600" height="{HEIGHT}" viewBox="0 0 1600 {HEIGHT}" '
             f'xmlns="http://www.w3.org/2000/svg">' + "\n".join(u) + "</svg>")
    return under + "\n" + "\n".join(h), "\n".join(o)
