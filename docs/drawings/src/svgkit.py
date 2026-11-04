"""Tiny SVG helper for engineering-style drawings."""
from xml.sax.saxutils import escape

FONT = "Arial, Helvetica, 'DejaVu Sans', sans-serif"

COL = {
    "ink": "#111111",
    "grey": "#8a8a8a",
    "light": "#f3f4f6",
    "panel": "#fbfbf7",
    "bus": "#1f5fbf",
    "mains": "#c62828",
    "vac": "#c25e00",
    "loop": "#1a7f37",
    "water": "#dbeafe",
    "waterline": "#2b6cb0",
    "air": "#6b7280",
}


class SVG:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.el = []

    def _style(self, stroke, sw, dash, fill):
        s = f'stroke="{stroke}" stroke-width="{sw}" fill="{fill}"'
        if dash:
            s += f' stroke-dasharray="{dash}"'
        return s

    def rect(self, x, y, w, h, stroke=COL["ink"], fill="none", sw=1.2, dash=None, rx=0):
        self.el.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" {self._style(stroke, sw, dash, fill)}/>')

    def line(self, x1, y1, x2, y2, stroke=COL["ink"], sw=1.2, dash=None, end=None, start=None):
        m = ""
        if end:
            m += f' marker-end="url(#{end})"'
        if start:
            m += f' marker-start="url(#{start})"'
        self.el.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {self._style(stroke, sw, dash, "none")}{m}/>')

    def poly(self, pts, stroke=COL["ink"], sw=1.2, dash=None, fill="none", end=None, closed=False):
        p = " ".join(f"{x},{y}" for x, y in pts)
        tag = "polygon" if closed else "polyline"
        m = f' marker-end="url(#{end})"' if end else ""
        self.el.append(f'<{tag} points="{p}" {self._style(stroke, sw, dash, fill)}{m}/>')

    def circle(self, cx, cy, r, stroke=COL["ink"], fill="white", sw=1.2, dash=None):
        self.el.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" {self._style(stroke, sw, dash, fill)}/>')

    def path(self, d, stroke=COL["ink"], fill="none", sw=1.2, dash=None):
        self.el.append(f'<path d="{d}" {self._style(stroke, sw, dash, fill)}/>')

    def text(self, x, y, t, size=11, anchor="start", weight="normal", fill=COL["ink"], italic=False, family=FONT):
        st = ' font-style="italic"' if italic else ""
        self.el.append(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" fill="{fill}"{st}>{escape(t)}</text>'
        )

    def raw(self, s):
        self.el.append(s)

    def save(self, path, title):
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}">\n<title>{escape(title)}</title>\n'
            "<defs>"
            '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{COL["ink"]}"/></marker>'
            '<marker id="arrb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{COL["waterline"]}"/></marker>'
            '<marker id="arrg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{COL["air"]}"/></marker>'
            "</defs>\n"
            f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="white"/>\n'
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(head + "\n".join(self.el) + "\n</svg>\n")


def title_block(s, x, y, w, h, rows):
    """rows: list of (label, value, bold)."""
    s.rect(x, y, w, h, sw=1.6)
    rh = h / len(rows)
    for i, (lab, val, bold) in enumerate(rows):
        yy = y + i * rh
        if i:
            s.line(x, yy, x + w, yy, sw=0.8)
        s.text(x + 8, yy + rh / 2 + 4, lab, size=9.5, fill=COL["grey"])
        s.text(x + 120, yy + rh / 2 + 4, val, size=12 if bold else 11, weight="bold" if bold else "normal")
    s.line(x + 112, y, x + 112, y + h, sw=0.8)
