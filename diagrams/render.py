"""Regenerate the two editable SVGs and WebPs using Pillow and Inkscape."""
from base64 import b64encode
from io import BytesIO
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from matching import response
from scenes import scene

OUT = Path(__file__).resolve().parent
INK = "#172d3e"
TEAL = "#067666"
RED = "#9e3b32"


def txt(x, y, s, size=26, color=INK, bold=False):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}"'
            f' font-weight="{"700" if bold else "400"}">{s}</text>')


def rect(x, y, w, h, stroke=TEAL, fill="none", thickness=3, dash=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"'
            f' stroke="{stroke}" stroke-width="{thickness}" stroke-dasharray="{dash}"/>')


def png(a, k, x, y):
    img = Image.fromarray(a).resize((a.shape[1]*k, a.shape[0]*k), Image.Resampling.NEAREST)
    data = BytesIO()
    img.save(data, format="PNG", optimize=True)
    uri = b64encode(data.getvalue()).decode()
    return f'<image x="{x}" y="{y}" width="{img.width}" height="{img.height}" xlink:href="data:image/png;base64,{uri}"/>'


def save(name, title, desc, body):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
           f' width="960" height="520" viewBox="0 0 960 520"><title>{title}</title><desc>{desc}</desc>'
           f'<rect width="960" height="520" rx="20" fill="#edf7f4"/>'
           f'<g font-family="DejaVu Sans, sans-serif">{body}</g></svg>\n')
    source = OUT / f"{name}.svg"
    source.write_text(svg, encoding="utf-8")
    with TemporaryDirectory() as scratch:
        raster = Path(scratch) / "render.png"
        run(["inkscape", str(source), f"--export-filename={raster}"], check=True)
        with Image.open(raster) as bitmap:
            bitmap.convert("RGB").save(OUT / f"{name}.webp", quality=88, method=6)


frame, mark = scene("shift")
x0, y0, k = 36, 118, 7
x, y = x0 + 47*k, y0 + 11*k
b = txt(36, 54, "Find the template origin", 37, bold=True)
b += txt(36, 96, "Frame: 78 × 52 pixels", 25, bold=True)
b += png(frame, k, x0, y0)
b += rect(x-2, y-2, 67, 67, "#f6ef6c", thickness=4)
b += f'<circle cx="{x}" cy="{y}" r="6" fill="#fff985" stroke="#172d3e" stroke-width="2"/>'
b += f'<path d="M {x+4} {y-5} L 610 178" fill="none" stroke="#fff985" stroke-width="3"/>'
b += txt(610, 175, "Origin (47, 11)", 28, bold=True)
b += txt(610, 209, "x right, y down", 23)
b += txt(610, 270, "Template: 9 × 9", 25, bold=True)
b += png(mark, 13, 610, 292)
b += txt(610, 448, "Response grid", 24, bold=True)
b += txt(610, 479, "70 columns × 44 rows", 23)
save("template-match-window", "Find the template origin",
     "Synthetic frame, its template, and the winning top left coordinate.", b)

frame, mark = scene("repeat")
r = response(frame, mark)
left, right, top, bottom = 92, 910, 120, 405
xs = lambda x: left + (right-left)*x/69
ys = lambda y: bottom - (bottom-top)*(y+.55)/1.65
b = txt(36, 54, "A high score can still be ambiguous", 36, bold=True)
b += txt(36, 94, "Two horizontal slices of the repeat response", 24)
for tick in [-.5, 0, .5, .87, 1]:
    y = ys(tick)
    color = "#9d580d" if tick == .87 else "#b9cbc7"
    dash = ' stroke-dasharray="8 5"' if tick == .87 else ""
    b += f'<path d="M{left} {y:.2f}H{right}" stroke="{color}" stroke-width="2"{dash}/>'
    b += txt(22, y+7, f"{tick:g}", 19, color if tick == .87 else INK)
for row, color, dash in ((11, TEAL, ""), (34, RED, "8 5")):
    points = " ".join(f"{xs(x):.2f},{ys(float(v)):.2f}" for x, v in enumerate(r[row]))
    b += f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3.5" stroke-dasharray="{dash}"/>'
for x, color in ((13, RED), (47, TEAL)):
    b += f'<circle cx="{xs(x):.2f}" cy="{ys(1):.2f}" r="6" fill="{color}"/>'
    b += txt(xs(x)+9, ys(1)-6, f"x = {x}", 19, color, True)
for x in [0, 20, 40, 60, 69]:
    b += txt(xs(x)-7, 430, str(x), 19)
b += txt(316, 462, "Template origin x (pixels)", 23, bold=True)
b += txt(90, 500, "Solid: y = 11", 22, TEAL, True)
b += txt(307, 500, "Dashed: y = 34", 22, RED, True)
b += txt(620, 500, "Minimum: 0.87", 22, "#86480b", True)
save("template-match-ambiguity", "Two competing template matches",
     "Response slices at y 11 and y 34. Separate peaks at x 47 and x 13 both reach 1.", b)
