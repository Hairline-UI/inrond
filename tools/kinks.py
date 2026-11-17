"""kinks.py FONT glyph[,glyph] wght opsz — list small direction breaks per roundness."""
import math
import sys
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

font = TTFont(sys.argv[1])
wght, opsz = float(sys.argv[3]), float(sys.argv[4])


def breaks(gs, name, lo=8.0, hi=20.0):
    pen = DecomposingRecordingPen(gs)
    gs[name].draw(pen)
    out, contour = [], []

    def flush(c):
        segs, cur = [], None
        for kind, args in c:
            if kind == "moveTo":
                cur = args[0]
            elif kind == "lineTo":
                segs.append((cur, [], args[0]))
                cur = args[0]
            elif kind == "qCurveTo":
                offs, end = list(args[:-1]), args[-1]
                prev = cur
                for i, o in enumerate(offs):
                    nxt = end if i == len(offs) - 1 else ((o[0] + offs[i + 1][0]) / 2, (o[1] + offs[i + 1][1]) / 2)
                    segs.append((prev, [o], nxt))
                    prev = nxt
                cur = end
        segs = [s for s in segs if math.hypot(s[2][0] - s[0][0], s[2][1] - s[0][1]) >= 3]
        m = len(segs)
        for i in range(m):
            a, b = segs[i], segs[(i + 1) % m]
            if math.hypot(b[0][0] - a[2][0], b[0][1] - a[2][1]) > 1.5:
                continue
            p_in = a[1][-1] if a[1] else a[0]
            p_out = b[1][0] if b[1] else b[2]
            v1 = (a[2][0] - p_in[0], a[2][1] - p_in[1])
            v2 = (p_out[0] - b[0][0], p_out[1] - b[0][1])
            l1, l2 = math.hypot(*v1), math.hypot(*v2)
            if l1 < 2 or l2 < 2:
                continue
            ang = math.degrees(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1]))
            if lo <= abs(ang) <= hi:
                out.append((round(a[2][0]), round(a[2][1]), round(ang, 1), round(l1), round(l2)))

    for kind, args in pen.value:
        if kind == "moveTo" and contour:
            flush(contour)
            contour = []
        contour.append((kind, args))
    if contour:
        flush(contour)
    return out


for name in sys.argv[2].split(","):
    for r in (0, 20, 35, 50, 70, 100):
        gs = font.getGlyphSet(location={"wght": wght, "opsz": opsz, "ROND": r})
        b = breaks(gs, name)
        print("%-10s ROND %3d: %d breaks %s" % (name, r, len(b), b[:10]))
