"""inspect_glyph.py SRC OUT glyph wght opsz rond — render source vs built outline big, list small turns."""
import math
import sys
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

srcp, outp, name = sys.argv[1:4]
wght, opsz, rond = (float(x) for x in sys.argv[4:7])
png = sys.argv[7]
src, out = TTFont(srcp), TTFont(outp)
L = {"wght": wght, "opsz": opsz}
L = {k: v for k, v in L.items() if k in [a.axisTag for a in src["fvar"].axes]}
gs0 = src.getGlyphSet(location=L)
gs1 = out.getGlyphSet(location=dict(L, ROND=rond))


def polys(gs):
    pen = DecomposingRecordingPen(gs)
    gs[name].draw(pen)
    res, cur, pos = [], [], None
    nodes = []
    for kind, args in pen.value:
        if kind == "moveTo":
            if cur:
                res.append(cur)
            cur, pos = [args[0]], args[0]
            nodes.append((args[0], 1))
        elif kind == "lineTo":
            cur.append(args[0])
            pos = args[0]
            nodes.append((args[0], 1))
        elif kind == "qCurveTo":
            pts = list(args)
            offs, end = pts[:-1], pts[-1]
            prev = pos
            for i, o in enumerate(offs):
                nxt = end if i == len(offs) - 1 else ((o[0] + offs[i + 1][0]) / 2, (o[1] + offs[i + 1][1]) / 2)
                for s in range(1, 13):
                    t = s / 12
                    cur.append(((1 - t) ** 2 * prev[0] + 2 * t * (1 - t) * o[0] + t * t * nxt[0],
                                (1 - t) ** 2 * prev[1] + 2 * t * (1 - t) * o[1] + t * t * nxt[1]))
                nodes.append((o, 0))
                prev = nxt
            nodes.append((end, 1))
            pos = end
    if cur:
        res.append(cur)
    return res, nodes


p0, n0 = polys(gs0)
p1, n1 = polys(gs1)
xs = [x for p in p0 + p1 for x, y in p]
ys = [y for p in p0 + p1 for x, y in p]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
S = 1500 / max(x1 - x0, y1 - y0, 1)
W, H = int((x1 - x0) * S) + 80, int((y1 - y0) * S) + 80
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)


def T(p):
    return (40 + (p[0] - x0) * S, H - 40 - (p[1] - y0) * S)


for p in p0:
    d.line([T(q) for q in p] + [T(p[0])], fill=(200, 200, 200), width=5)
for p in p1:
    d.line([T(q) for q in p] + [T(p[0])], fill=(220, 30, 60), width=2)
for pt, on in n1:
    x, y = T(pt)
    d.ellipse([x - 4, y - 4, x + 4, y + 4], outline=(0, 90, 220) if on else (0, 160, 60), width=2)
img.save(png)
print("saved", png, img.size, "points: source %d built %d" % (len(n0), len(n1)))
g = out["glyf"][name]
print("composite" if g.isComposite() else "simple, %d contours, %d points" % (g.numberOfContours, len(g.coordinates)))
