"""Feasibility analysis of a source variable font for corner rounding."""
import math
import sys
from collections import Counter
from fontTools.ttLib import TTFont

path = sys.argv[1]
f = TTFont(path)
glyf = f["glyf"]
order = f.getGlyphOrder()

simple = composite = empty = 0
pts_total = 0
corner_convex = corner_concave = 0
dir_bad = 0
allOff = 0
overlap_glyphs = []
hidden_corners = 0


def contours(g):
    out, start = [], 0
    coords, ends, flags = g.getCoordinates(glyf)
    for e in ends:
        out.append([(coords[i][0], coords[i][1], flags[i] & 1) for i in range(start, e + 1)])
        start = e + 1
    return out


def area(c):
    return sum(c[i][0] * c[(i + 1) % len(c)][1] - c[(i + 1) % len(c)][0] * c[i][1] for i in range(len(c))) / 2


def flatten(c):
    """on/off TrueType contour -> polyline (coarse)."""
    n = len(c)
    pts = []
    # expand implied on-curves
    ex = []
    for i, p in enumerate(c):
        q = c[(i + 1) % n]
        ex.append(p)
        if not p[2] and not q[2]:
            ex.append(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, 1))
    if not any(p[2] for p in ex):
        return [(p[0], p[1]) for p in ex]
    s = next(i for i, p in enumerate(ex) if p[2])
    ex = ex[s:] + ex[:s]
    m = len(ex)
    i = 0
    while i < m:
        p = ex[i]
        nxt = ex[(i + 1) % m]
        if nxt[2]:
            pts.append((p[0], p[1]))
            i += 1
        else:
            e = ex[(i + 2) % m]
            for k in range(6):
                t = k / 6
                pts.append(((1 - t) ** 2 * p[0] + 2 * t * (1 - t) * nxt[0] + t * t * e[0],
                            (1 - t) ** 2 * p[1] + 2 * t * (1 - t) * nxt[1] + t * t * e[1]))
            i += 2
    return pts


def inside(pt, poly):
    x, y = pt
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


turns = Counter()
for name in order:
    g = glyf[name]
    if g.isComposite():
        composite += 1
        continue
    if g.numberOfContours == 0:
        empty += 1
        continue
    simple += 1
    cs = contours(g)
    polys = [flatten(c) for c in cs]
    # largest contour should be clockwise (negative area) in TrueType
    areas = [area([(p[0], p[1]) for p in poly] and [(p[0], p[1], 1) for p in poly]) for poly in polys]
    big = max(range(len(cs)), key=lambda i: abs(areas[i]))
    if areas[big] > 0:
        dir_bad += 1
    g_hidden = 0
    for ci, c in enumerate(cs):
        n = len(c)
        pts_total += n
        if not any(p[2] for p in c):
            allOff += 1
            continue
        for i, p in enumerate(c):
            if not p[2]:
                continue
            a, b = c[i - 1], c[(i + 1) % n]
            v1 = (p[0] - a[0], p[1] - a[1])
            v2 = (b[0] - p[0], b[1] - p[1])
            l1, l2 = math.hypot(*v1), math.hypot(*v2)
            if l1 == 0 or l2 == 0:
                continue
            cross = (v1[0] * v2[1] - v1[1] * v2[0]) / (l1 * l2)
            dot = (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2)
            ang = math.degrees(math.atan2(cross, dot))
            if abs(ang) < 12:
                continue
            turns[int(abs(ang) // 15) * 15] += 1
            if ang < 0:
                corner_convex += 1
                # outward probe: is this convex corner covered by another contour?
                bx, by = v1[0] / l1 - v2[0] / l2, v1[1] / l1 - v2[1] / l2
                bl = math.hypot(bx, by) or 1
                probe = (p[0] + 3 * bx / bl, p[1] + 3 * by / bl)
                for cj, poly in enumerate(polys):
                    if cj != ci and areas[cj] < 0 and inside(probe, poly):
                        g_hidden += 1
                        break
            else:
                corner_concave += 1
    if g_hidden:
        hidden_corners += g_hidden
        overlap_glyphs.append((name, g_hidden))

print("glyphs: simple %d composite %d empty %d" % (simple, composite, empty))
print("points in simple glyphs:", pts_total)
print("corners: convex %d concave %d" % (corner_convex, corner_concave))
print("turn histogram (deg bucket):", sorted(turns.items()))
print("glyphs whose largest contour is counter-clockwise:", dir_bad)
print("all-off-curve contours:", allOff)
print("glyphs with convex corners covered by another clockwise contour: %d (corners %d)" % (len(overlap_glyphs), hidden_corners))
print(" ", overlap_glyphs[:60])
flags_overlap = sum(1 for n in order if not glyf[n].isComposite() and glyf[n].numberOfContours > 0 and glyf[n].flags[0] & 0x40)
print("glyphs flagged OVERLAP_SIMPLE:", flags_overlap)
print("GSUB FeatureVariations:", bool(getattr(f["GSUB"].table, "FeatureVariations", None)))
print("tables:", " ".join(sorted(f.keys())))
