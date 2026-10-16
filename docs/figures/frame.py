"""Shared visual system for the figures: design tokens (light and dark), fonts, the slide frame and HTML helpers.

Every figure is a 1600 x H CSS-pixel page: a navy header band, a body with absolutely positioned cards and an
inline SVG overlay, and a caption bar. build.py renders it with headless Chrome at device scale 2 (3200 px wide).
"""
import base64
import html as _html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W = 1600
BAND_H = 152
CAPTION_H = 84
X0, X1 = 56, 1544  # content area

# ---------------------------------------------------------------- tokens
TOKENS = {
    "light": {
        "surface": "#fcfcfb", "card": "#ffffff", "caption": "#f1f0ec", "frame": "#d9d7cf",
        "ink": "#0b0b0b", "text2": "#52514e", "muted": "#6f6d68", "hairline": "#e1e0d9", "axis": "#c3c2b7",
        "arrow": "#3d3c39", "up": "#008300", "down": "#e34948", "halo": "#eda100", "band_alt": "#f6f5f1",
        "gold_wash": "#f8eccb", "silver_wash": "#eeede9", "bronze_wash": "#f5e3d3",
        "gold_label": "#7a5a00", "silver_label": "#52514e", "bronze_label": "#84461a",
        "pageno": "#13233d", "hatch": "#b9b7af", "grid": "#dcdad2",
    },
    "dark": {
        "surface": "#1a1a19", "card": "#232321", "caption": "#222220", "frame": "#3a3936",
        "ink": "#f0efec", "text2": "#c3c2b7", "muted": "#908e88", "hairline": "#2c2c2a", "axis": "#3a3936",
        "arrow": "#c3c2b7", "up": "#0ca30c", "down": "#e66767", "halo": "#c98500", "band_alt": "#1f1f1d",
        "gold_wash": "#2a2618", "silver_wash": "#262624", "bronze_wash": "#2c231d",
        "gold_label": "#e2c36b", "silver_label": "#c3c2b7", "bronze_label": "#e0a57a",
        "pageno": "#c3d3ea", "hatch": "#5a5955", "grid": "#34332f",
    },
}

# layer families on the mechanism figures: (mark/border, tint) per theme
FAMILY = {
    "base": {"light": ("#898781", "#f3f2ee"), "dark": ("#898781", "#262624")},
    "selling": {"light": ("#2a78d6", "#eaf2fc"), "dark": ("#3987e5", "#18283c")},
    "fixes": {"light": ("#1baf7a", "#e8f7f1"), "dark": ("#199e70", "#13291f")},
    "wheat": {"light": ("#eb6834", "#fdf0e9"), "dark": ("#d95926", "#36221a")},
    "counter": {"light": ("#6250d6", "#f0eefc"), "dark": ("#9085e9", "#25213d")},
}

# approaches on the data figures
APPROACH = {
    "learned": {"light": "#2a78d6", "dark": "#3987e5"},
    "production": {"light": "#1baf7a", "dark": "#199e70"},
    "market": {"light": "#eb6834", "dark": "#d95926"},
    "other": {"light": "#898781", "dark": "#898781"},
}

TAG_COLOR = {"MECHANISM": "#3987e5", "RESULT": "#eda100", "HISTORY": "#9085e9", "POST-MORTEM": "#1baf7a"}

BAND = {"fill": "#13233d", "eyebrow": "#8fa6c8", "title": "#ffffff", "num": "#8fb8ec", "sub": "#c7d3e6",
        "tag_border": "#3a557d", "tag_text": "#e8eef7", "bar": "#1d3354", "bar_note": "#b9c7dc"}

N_FIGURES = 7


def tok(theme, name):
    return TOKENS[theme][name]


def fam(theme, family):
    return FAMILY[family][theme]


def esc(s):
    return _html.escape(str(s), quote=False)


def fmt(n, dec=0):
    """Thousands separators; keeps a sign if given as a string."""
    if isinstance(n, str):
        return n
    return f"{n:,.{dec}f}"


# ---------------------------------------------------------------- fonts
_FONT_CSS = None


def _font_face():
    global _FONT_CSS
    if _FONT_CSS is None:
        def b64(name):
            with open(os.path.join(HERE, "fonts", name), "rb") as f:
                return base64.b64encode(f.read()).decode("ascii")
        _FONT_CSS = (
            "@font-face{font-family:'InterV';src:url(data:font/woff2;base64," + b64("InterVariable.woff2") +
            ") format('woff2');font-weight:100 900;font-style:normal;}\n"
            "@font-face{font-family:'JBM';src:url(data:font/woff2;base64," + b64("JetBrainsMono-Medium.woff2") +
            ") format('woff2');font-weight:500;}\n"
            "@font-face{font-family:'JBM';src:url(data:font/woff2;base64," + b64("JetBrainsMono-Bold.woff2") +
            ") format('woff2');font-weight:700;}\n"
            "@font-face{font-family:'NotoSC';src:local('Noto Sans SC'),local('NotoSansSC-Regular'),"
            "local('Noto Sans SC Regular');}\n")
    return _FONT_CSS


# ---------------------------------------------------------------- css
def css(theme, height):
    t = TOKENS[theme]
    v = "".join(f"--{k}:{val};" for k, val in t.items())
    for f, d in FAMILY.items():
        v += f"--{f}:{d[theme][0]};--{f}-tint:{d[theme][1]};"
    for a, d in APPROACH.items():
        v += f"--ap-{a}:{d[theme]};"
    return _font_face() + f"""
:root{{{v}}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{background:transparent;width:{W}px;height:{height}px;overflow:hidden;}}
body{{font-family:'InterV','NotoSC','Segoe UI',sans-serif;color:var(--ink);font-size:20px;line-height:1.3;
  -webkit-font-smoothing:antialiased;text-rendering:geometricPrecision;}}
.tnum{{font-feature-settings:'tnum' 1;}}
.canvas{{position:relative;width:{W}px;height:{height}px;border-radius:20px;overflow:hidden;
  background:var(--surface);}}
.canvas::after{{content:'';position:absolute;left:0;top:0;width:{W}px;height:{height}px;border-radius:20px;
  border:1.5px solid var(--frame);pointer-events:none;z-index:50;}}
.abs{{position:absolute;}}
.band{{position:absolute;left:0;top:0;width:{W}px;height:{BAND_H}px;background:{BAND['fill']};}}
.eyebrow{{position:absolute;left:{X0}px;top:26px;font-size:20px;font-weight:600;letter-spacing:.14em;
  color:{BAND['eyebrow']};text-transform:uppercase;}}
.btitle{{position:absolute;left:{X0}px;top:54px;font-size:44px;font-weight:800;letter-spacing:.01em;
  color:{BAND['title']};text-transform:uppercase;line-height:1.1;}}
.btitle .nn{{color:{BAND['num']};}}
.bsub{{position:absolute;left:{X0}px;top:110px;font-size:22px;font-weight:400;color:{BAND['sub']};
  white-space:nowrap;}}
.tag{{position:absolute;right:{W - X1}px;top:28px;height:38px;border-radius:19px;border:1.5px solid {BAND['tag_border']};
  background:rgba(255,255,255,.06);padding:0 16px 0 14px;display:flex;align-items:center;gap:10px;
  font-size:20px;font-weight:700;letter-spacing:.08em;color:{BAND['tag_text']};}}
.tag i{{width:10px;height:10px;border-radius:5px;display:inline-block;}}
.capbar{{position:absolute;left:0;bottom:0;width:{W}px;height:{CAPTION_H}px;background:var(--caption);
  border-top:1px solid var(--hairline);}}
.capbar .src{{position:absolute;left:{X0}px;top:12px;width:1300px;font-size:20px;color:var(--text2);line-height:1.3;}}
.capbar .pg{{position:absolute;right:{W - X1}px;top:24px;font-size:24px;font-weight:800;color:var(--pageno);}}
.sbar{{position:absolute;left:{X0}px;width:{X1 - X0}px;height:44px;border-radius:8px;background:{BAND['bar']};
  display:flex;align-items:center;}}
.sbar .let{{width:28px;height:28px;border-radius:14px;margin-left:10px;color:#fff;font-size:18px;font-weight:800;
  display:flex;align-items:center;justify-content:center;}}
.sbar .lab{{margin-left:14px;font-size:20px;font-weight:700;letter-spacing:.08em;color:#fff;text-transform:uppercase;}}
.sbar .note{{margin-left:auto;margin-right:16px;font-size:20px;color:{BAND['bar_note']};}}
.card{{position:absolute;border-radius:14px;border:2px solid var(--frame);background:var(--card);}}
.chip{{display:inline-flex;align-items:center;height:34px;padding:0 12px;border-radius:17px;background:var(--card);
  border:1px solid var(--frame);font-size:20px;color:var(--ink);white-space:nowrap;}}
.mono{{font-family:'JBM',Consolas,monospace;font-weight:500;letter-spacing:-.01em;}}
.caps{{text-transform:uppercase;letter-spacing:.08em;}}
.nocaps{{text-transform:none;letter-spacing:0;}}
.t1{{color:var(--ink);}} .t2{{color:var(--text2);}} .tm{{color:var(--muted);}}
.s20{{font-size:20px;}} .s22{{font-size:22px;}} .s24{{font-size:24px;}} .s26{{font-size:26px;}}
.s28{{font-size:28px;}} .s32{{font-size:32px;}} .s44{{font-size:44px;}} .s64{{font-size:64px;}}
.w4{{font-weight:400;}} .w5{{font-weight:500;}} .w6{{font-weight:600;}} .w7{{font-weight:700;}} .w8{{font-weight:800;}}
.htr{{font-size:20px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--text2);}}
svg text{{font-family:'InterV','NotoSC','Segoe UI',sans-serif;}}
svg .mono{{font-family:'JBM',Consolas,monospace;}}
"""


# ---------------------------------------------------------------- page assembly
CHECK_JS = r"""
<script>
(async () => {
  await Promise.all(["20px InterV", "500 20px JBM", "700 20px JBM"].map(f => document.fonts.load(f)));
  await document.fonts.ready;
  const r = {};
  const root = document.querySelector('.canvas');
  const H = root.getBoundingClientRect().height;
  r.h = Math.round(document.documentElement.scrollHeight);
  r.fonts = (document.fonts.check("20px InterV") && document.fonts.check("20px JBM")) ? 1 : 0;
  let over = 0, overList = [];
  document.querySelectorAll('.fit').forEach(e => {
    if (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1) { over++; overList.push((e.id || e.className) + ':' + e.textContent.slice(0, 40)); }
  });
  r.overflow = over;
  let out = 0, outList = [];
  const cw = root.getBoundingClientRect();
  document.querySelectorAll('.canvas *').forEach(e => {
    if (e.closest('defs') || e.tagName === 'tspan') return;
    const b = e.getBoundingClientRect();
    if (b.width === 0 && b.height === 0) return;
    if (b.left < cw.left - 0.5 || b.top < cw.top - 0.5 || b.right > cw.right + 0.5 || b.bottom > cw.bottom + 0.5) {
      out++; outList.push(e.tagName + ':' + (e.textContent || '').slice(0, 30));
    }
  });
  r.out = out;
  const nc = Array.from(document.querySelectorAll('[data-nc]')).map(e => [e, e.getBoundingClientRect()]);
  let col = 0, colList = [];
  for (let i = 0; i < nc.length; i++) for (let j = i + 1; j < nc.length; j++) {
    const a = nc[i][1], b = nc[j][1];
    if (a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1) {
      col++; colList.push(nc[i][0].textContent.slice(0, 25) + ' / ' + nc[j][0].textContent.slice(0, 25));
    }
  }
  r.collide = col;
  document.documentElement.setAttribute('data-check', JSON.stringify(r));
  document.documentElement.setAttribute('data-detail', JSON.stringify({overList, outList: outList.slice(0, 20), colList}));
  document.documentElement.setAttribute('data-text', root.innerText.replace(/\s+/g, ' '));
})();
</script>
"""


def page(theme, nn, title, subtitle, tag, height, body, caption, svg_overlay=""):
    """Full HTML document for one figure in one theme."""
    t = TOKENS[theme]
    tagc = TAG_COLOR[tag]
    overlay = (f'<svg class="abs" style="left:0;top:0;pointer-events:none" width="{W}" height="{height}" '
               f'viewBox="0 0 {W} {height}" xmlns="http://www.w3.org/2000/svg">{svg_overlay}</svg>') if svg_overlay else ""
    return f"""<!doctype html><html data-theme="{theme}"><head><meta charset="utf-8">
<style>{css(theme, height)}</style></head><body>
<div class="canvas">
<div class="band"><div class="eyebrow">Kaggriculture · Team 42</div>
<div class="btitle"><span class="nn">{nn}</span> · {esc(title)}</div>
<div class="bsub">{esc(subtitle)}</div>
<div class="tag"><i style="background:{tagc}"></i>{esc(tag)}</div></div>
{body}
{overlay}
<div class="capbar"><div class="src">{caption}</div><div class="pg">{nn} / {N_FIGURES:02d}</div></div>
</div>{CHECK_JS}</body></html>"""


# ---------------------------------------------------------------- body helpers
def div(x, y, w=None, h=None, inner="", cls="", style="", nc=False, fit=False):
    st = f"left:{x}px;top:{y}px;"
    if w is not None:
        st += f"width:{w}px;"
    if h is not None:
        st += f"height:{h}px;"
    c = "abs " + cls + (" fit" if fit else "")
    attr = ' data-nc="1"' if nc else ""
    return f'<div class="{c.strip()}" style="{st}{style}"{attr}>{inner}</div>'


def section_bar(y, letter, label, note, key_color, raw=False):
    lab = label if raw else esc(label)
    return (f'<div class="sbar" style="top:{y}px"><div class="let" style="background:{key_color}">{letter}</div>'
            f'<div class="lab">{lab}</div><div class="note">{esc(note)}</div></div>')


def card(theme, x, y, w, h, family=None, inner="", style="", bar=False, fill=None, border=None, radius=14):
    if family:
        b, tint = fam(theme, family)
    else:
        b, tint = tok(theme, "frame"), tok(theme, "card")
    b = border or b
    tint = fill or tint
    st = f"border-color:{b};background:{tint};border-radius:{radius}px;{style}"
    left_bar = (f'<div class="abs" style="left:-2px;top:-2px;bottom:-2px;width:8px;background:{b};'
                f'border-radius:{radius}px 0 0 {radius}px"></div>') if bar else ""
    return f'<div class="card" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{st}">{left_bar}{inner}</div>'


def chip(text, mono=False, bar_color=None, extra_style=""):
    cls = "chip mono" if mono else "chip"
    bar = f"box-shadow:inset 4px 0 0 {bar_color};padding-left:14px;border-radius:8px;" if bar_color else ""
    return f'<span class="{cls}" style="{bar}{extra_style}">{text}</span>'


def icon_svg(path_d, color, size=32, stroke=2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{stroke * 24 / size:.2f}" stroke-linecap="round" stroke-linejoin="round">{path_d}</svg>')
