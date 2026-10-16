"""Small SVG helpers: scales, axes, text, arrows, unit bars, brackets, callouts. Coordinates are CSS px."""
import math

from frame import esc


def lin(d0, d1, r0, r1):
    def f(v):
        return r0 + (v - d0) * (r1 - r0) / (d1 - d0)
    return f


def logscale(d0, d1, r0, r1):
    l0, l1 = math.log10(d0), math.log10(d1)

    def f(v):
        return r0 + (math.log10(v) - l0) * (r1 - r0) / (l1 - l0)
    return f


def text(x, y, s, size=20, weight=400, fill="var(--text2)", anchor="start", mono=False, nc=True, extra=""):
    cls = ' class="mono"' if mono else ""
    ncattr = ' data-nc="1"' if nc else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{cls}{ncattr} {extra}>{esc(s)}</text>')


def rich(x, y, parts, size=20, anchor="start", nc=True):
    """parts: list of (text, weight, fill)."""
    spans = "".join(f'<tspan font-weight="{w}" fill="{f}">{esc(t)}</tspan>' for t, w, f in parts)
    ncattr = ' data-nc="1"' if nc else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}"{ncattr}>{spans}</text>'


def line(x1, y1, x2, y2, stroke="var(--hairline)", width=1, dash=None, cap="round", opacity=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{width}" stroke-linecap="{cap}"{d}{o}/>')


def rect(x, y, w, h, fill, rx=0, stroke=None, sw=1, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{s} {extra}/>'


def circle(cx, cy, r, fill, stroke=None, sw=2, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{s} {extra}/>'


def polyline(points, stroke, width=2, fill="none", dash=None):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round"{d}/>')


def arrow(x1, y1, x2, y2, color="var(--arrow)", width=4, head=16, dash=None):
    """Straight arrow with a solid triangular head at (x2, y2)."""
    ang = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    hw = head * 0.48
    p1 = (hx + hw * math.sin(ang), hy - hw * math.cos(ang))
    p2 = (hx - hw * math.sin(ang), hy + hw * math.cos(ang))
    return (line(x1, y1, hx, hy, stroke=color, width=width, dash=dash, cap="butt") +
            f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


def path_arrow(d, end, ang_deg, color="var(--arrow)", width=4, head=16, dash=None):
    """Arbitrary path d plus an arrowhead at end pointing at angle ang_deg (0 = right, 90 = down)."""
    ang = math.radians(ang_deg)
    x2, y2 = end
    hx, hy = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
    hw = head * 0.48
    p1 = (hx + hw * math.sin(ang), hy - hw * math.cos(ang))
    p2 = (hx - hw * math.sin(ang), hy + hw * math.cos(ang))
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="butt"{dd}/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


def hatch_def(pid, color, bg):
    return (f'<pattern id="{pid}" patternUnits="userSpaceOnUse" width="8" height="8" patternTransform="rotate(45)">'
            f'<rect width="8" height="8" fill="{bg}"/><line x1="0" y1="0" x2="0" y2="8" stroke="{color}" stroke-width="2.5"/></pattern>')


def bracket_below(x1, x2, y, depth=10, color="var(--text2)", width=1.5):
    return (f'<path d="M{x1:.1f} {y:.1f} v{depth} H{x2:.1f} v-{depth}" fill="none" stroke="{color}" '
            f'stroke-width="{width}"/>')


def leader(x1, y1, x2, y2, color="var(--text2)", width=1.5, dot=True):
    s = line(x1, y1, x2, y2, stroke=color, width=width)
    if dot:
        s += circle(x2, y2, 3, color)
    return s


def tri(x, y, up=True, size=10, fill="var(--up)"):
    h = size * 0.9
    if up:
        pts = f"{x:.1f},{y - h / 2:.1f} {x - size / 2:.1f},{y + h / 2:.1f} {x + size / 2:.1f},{y + h / 2:.1f}"
    else:
        pts = f"{x:.1f},{y + h / 2:.1f} {x - size / 2:.1f},{y - h / 2:.1f} {x + size / 2:.1f},{y - h / 2:.1f}"
    return f'<polygon points="{pts}" fill="{fill}"/>'
