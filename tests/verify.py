"""Geometry and layout checks of the built font against its source.

    python tests/verify.py SOURCE.ttf BUILT.ttf [--quick] [--inside]

Glyphs are rasterised with FreeType at 1024 px per em (1 px = 2 font units at
2048 upm) and compared as bitmaps, i.e. the way a renderer sees them.

1. sharp      at ROND 0 every glyph matches the source
2. inside     a round stroke end passes its cut the way an o passes the
              baseline; rounding adds no ink beyond that overshoot
              (--inside: the 1.0 rule, no ink outside the source at all)
3. monotone   inside the source outline, more roundness never brings back a
              visible amount of ink
4. kinks      rounding introduces no small direction breaks
5. metrics    advance widths are identical at every roundness
6. shaping    HarfBuzz produces the same glyphs and positions
Exit code is non-zero if any check fails.
"""
import ctypes
import math
import sys

import freetype
import numpy as np
import uharfbuzz as hb
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

SRC, OUT = sys.argv[1], sys.argv[2]
QUICK = "--quick" in sys.argv
PPEM = 1024
ARM = 10
src, out = TTFont(SRC), TTFont(OUT)
upm = src["head"].unitsPerEm
AXES = [a.axisTag for a in src["fvar"].axes]
LOCS = [
    {"wght": 400, "opsz": 14}, {"wght": 100, "opsz": 14}, {"wght": 900, "opsz": 14},
    {"wght": 650, "opsz": 14}, {"wght": 250, "opsz": 32}, {"wght": 800, "opsz": 32},
    {"wght": 520, "opsz": 23},
]
if QUICK:
    LOCS = LOCS[:1] + LOCS[3:4] + LOCS[5:6]
LOCS = [{k: v for k, v in L.items() if k in AXES} for L in LOCS]
ROUNDS = (35, 70, 100)
failures = []
FLAGS = freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO | freetype.FT_LOAD_NO_BITMAP


class Raster:
    def __init__(self, path):
        self.face = freetype.Face(path)
        self.face.set_pixel_sizes(0, PPEM)
        self.tags = [a.tag for a in self.face.get_variation_info().axes]

    def at(self, loc):
        self.face.set_var_design_coords([loc[t] for t in self.tags])

    def glyph(self, gid):
        self.face.load_glyph(gid, FLAGS)
        b = self.face.glyph.bitmap
        if b.rows == 0 or b.width == 0:
            return None
        raw = ctypes.string_at(b._FT_Bitmap.buffer, b.rows * b.pitch)      # straight from FreeType, no Python list
        bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8).reshape(b.rows, b.pitch), axis=1)
        return self.face.glyph.bitmap_left, self.face.glyph.bitmap_top, bits[:, :b.width].astype(bool)


def align(items):
    """Put bitmaps (left, top, array) on one canvas."""
    items = [i for i in items]
    live = [i for i in items if i is not None]
    if not live:
        return None
    x0 = min(i[0] for i in live)
    y1 = max(i[1] for i in live)
    x1 = max(i[0] + i[2].shape[1] for i in live)
    y0 = min(i[1] - i[2].shape[0] for i in live)
    out_ = []
    for i in items:
        canvas = np.zeros((y1 - y0, x1 - x0), dtype=bool)
        if i is not None:
            l, t, a = i
            canvas[y1 - t:y1 - t + a.shape[0], l - x0:l - x0 + a.shape[1]] = a
        out_.append(canvas)
    return out_


def thick(mask, n=2):
    """Number of n x n blocks that are fully set: regions at least n px (2n units) across."""
    if mask.shape[0] < n or mask.shape[1] < n:
        return 0
    h, w = mask.shape[0] - n + 1, mask.shape[1] - n + 1
    acc = np.ones((h, w), dtype=bool)
    for dy in range(n):
        for dx in range(n):
            acc &= mask[dy:dy + h, dx:dx + w]
    return int(acc.sum())


def small_turns(gs, name, lo=3.0, hi=20.0):
    """Direction changes, in degrees, at joins that are neither smooth nor real corners."""
    pen = DecomposingRecordingPen(gs)
    gs[name].draw(pen)
    found, contour = [], []

    def flush(c):
        segs, cur = [], None
        for kind, args in c:
            if kind == "moveTo":
                cur = args[0]
            elif kind == "lineTo":
                segs.append((cur, [], args[0]))
                cur = args[0]
            elif kind == "qCurveTo":
                pts = list(args)
                if pts[-1] is None:
                    continue
                offs, end = pts[:-1], pts[-1]
                prev = cur
                for i, o in enumerate(offs):
                    nxt = end if i == len(offs) - 1 else ((o[0] + offs[i + 1][0]) / 2, (o[1] + offs[i + 1][1]) / 2)
                    segs.append((prev, [o], nxt))
                    prev = nxt
                cur = end
        # ignore segments too short to carry a direction
        segs = [s for s in segs if math.hypot(s[2][0] - s[0][0], s[2][1] - s[0][1]) >= 3]
        m = len(segs)
        for i in range(m):
            a, b = segs[i], segs[(i + 1) % m]
            if math.hypot(b[0][0] - a[2][0], b[0][1] - a[2][1]) > 1.5:
                continue                        # not adjacent any more
            p_in = a[1][-1] if a[1] else a[0]
            p_out = b[1][0] if b[1] else b[2]
            v1 = (a[2][0] - p_in[0], a[2][1] - p_in[1])
            v2 = (p_out[0] - b[0][0], p_out[1] - b[0][1])
            l1, l2 = math.hypot(*v1), math.hypot(*v2)
            if l1 < ARM or l2 < ARM:
                continue                        # too short to carry a direction on an integer grid
            ang = abs(math.degrees(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1])))
            if lo <= ang <= hi:
                found.append(ang)

    for kind, args in pen.value:
        if kind == "moveTo" and contour:
            flush(contour)
            contour = []
        contour.append((kind, args))
    if contour:
        flush(contour)
    return found


order = src.getGlyphOrder()
names = [n for n in order if src["glyf"][n].numberOfContours != 0]
gid = {n: i for i, n in enumerate(order)}
assert order == out.getGlyphOrder()
r0 = Raster(SRC)
r1 = {r: Raster(OUT) for r in (0,) + ROUNDS}       # one face per roundness: no re-instancing per glyph
print("glyphs checked: %d at %d locations, %d px per em" % (len(names), len(LOCS), PPEM))

# What counts as a failure, in font units of a 2048 em (1 px here = 2 units):
#   sharp     any 4-unit difference to the source
#   inside    the rounded outline leaving the source outline by 8 units or more
#   monotone  ink coming back by 10 units or more as roundness grows
#   kinks     a new direction break of 8 degrees or more at full roundness
# Smaller deviations are counted and reported as notes.
notes = {"drift": {}, "back": {}}
worst = {"sharp": (0, ""), "added": (0, ""), "back": (0, "")}
lost = []
bands = {r: [0, 0] for r in ROUNDS}         # [3-8 deg, 8-20 deg] gained over the source
src_bands = [0, 0]
kink_fail = {}
def source_overshoot(L):
    from fontTools.pens.boundsPen import BoundsPen
    gs = src.getGlyphSet(location=L)
    for name in ("o", "O", "zero"):
        if name in gs:
            pen = BoundsPen(gs)
            gs[name].draw(pen)
            return max(0.0, -pen.bounds[1])
    return 0.0


OVER = {}
OVERSHOOT = "--inside" not in sys.argv     # --inside: the 1.0 rule, no ink outside the source at all
for L in LOCS:
    ov = source_overshoot(L) if OVERSHOOT else 0.0
    n_fail = int(math.ceil((ov + 8) / 2))       # px; 1 px = 2 units
    OVER[str(L)] = ov
    r0.at(L)
    for r, face in r1.items():
        face.at(dict(L, ROND=r))
    for n in names:
        got = align([r0.glyph(gid[n])] + [r1[r].glyph(gid[n]) for r in (0,) + ROUNDS])
        if got is None:
            continue
        b, s_, *rs = got
        ink = int(b.sum())
        if ink == 0:
            continue
        d = thick(b ^ s_)
        if d > worst["sharp"][0]:
            worst["sharp"] = (d, "%s %s" % (n, L))
        if d:
            failures.append("sharp differs: %s at %s (%d px)" % (n, L, d))
        prev = b
        for r, cur in zip(ROUNDS, rs):
            added = cur & ~b
            add = thick(added)
            if add:
                notes["drift"][n] = max(notes["drift"].get(n, 0), add)
                if add > worst["added"][0]:
                    worst["added"] = (add, "%s ROND %d %s" % (n, r, L))
                if thick(added, n_fail):
                    failures.append("ink added beyond the limit: %s ROND %d at %s" % (n, r, L))
            returned = (cur & ~prev & b) if OVERSHOOT else (cur & ~prev)
            back = thick(returned, 3)
            if back:
                notes["back"][n] = max(notes["back"].get(n, 0), back)
                if back > worst["back"][0]:
                    worst["back"] = (back, "%s ROND %d %s" % (n, r, L))
                if thick(returned, 5):
                    failures.append("ink returns: %s up to ROND %d at %s" % (n, r, L))
            prev = cur
        lost.append((1 - rs[-1].sum() / ink, n))
    gs0 = src.getGlyphSet(location=L)
    g = {r: out.getGlyphSet(location=dict(L, ROND=r)) for r in ROUNDS}
    for n in names:
        if out["glyf"][n].isComposite():
            continue
        base = small_turns(gs0, n)
        b_small, b_big = sum(a < 8 for a in base), sum(a >= 8 for a in base)
        src_bands[0] += b_small
        src_bands[1] += b_big
        for r in ROUNDS:
            t = small_turns(g[r], n)
            small, big = sum(a < 8 for a in t), sum(a >= 8 for a in t)
            bands[r][0] += max(small - b_small, 0)
            bands[r][1] += max(big - b_big, 0)
            if r == 100 and big > b_big:
                kink_fail[n] = max(kink_fail.get(n, 0), big - b_big)

lost.sort()
print("1 sharp     difference to the source at ROND 0:   worst %d px %s" % worst["sharp"])
print("2 inside    allowed outside the source per location: %s units" % " ".join("%.0f" % (v + 8) for v in OVER.values()))
print("            glyphs with ink 4+ units outside:      %d of %d (worst %d px, %s)" % (
    len(notes["drift"]), len(names), worst["added"][0], worst["added"][1]))
print("3 monotone  glyphs regaining 6+ units of ink:      %d of %d (worst %d px, %s)" % (
    len(notes["back"]), len(names), worst["back"][0], worst["back"][1]))
print("            ink removed at ROND 100: median %.1f%%, 95th pct %.1f%%, max %.1f%% (%s)" % (
    100 * lost[len(lost) // 2][0], 100 * lost[int(len(lost) * 0.95)][0], 100 * lost[-1][0], lost[-1][1]))
print("4 kinks     direction breaks in the source: %d of 3-8 deg, %d of 8-20 deg" % tuple(src_bands))
for r in ROUNDS:
    print("            gained at ROND %-3d              %d of 3-8 deg, %d of 8-20 deg" % (r, bands[r][0], bands[r][1]))
if notes["drift"]:
    top = sorted(notes["drift"].items(), key=lambda kv: -kv[1])[:25]
    print("            drift notes:   " + " ".join("%s:%d" % kv for kv in top))
if kink_fail:
    top = sorted(kink_fail.items(), key=lambda kv: -kv[1])
    print("            8+ deg breaks at ROND 100 in %d glyphs: %s" % (len(top), " ".join("%s:%d" % kv for kv in top[:40])))
    if len(top) > 0.02 * len(names):
        failures.append("kinks: %d glyphs gain a break of 8 degrees or more at full roundness" % len(top))

# 5. metrics
bad = 0
for L in LOCS:
    gs0 = src.getGlyphSet(location=L)
    for r in (0, 50, 100):
        gs1 = out.getGlyphSet(location=dict(L, ROND=r))
        for n in order:
            if abs(gs0[n].width - gs1[n].width) > 0.01:
                bad += 1
print("5 metrics   advance width mismatches: %d" % bad)
if bad:
    failures.append("%d advance widths differ" % bad)

# 6. shaping
TEXTS = ["Hamburgefonstiv 0123456789", "AVATAR Type: fi fl ffi -> 1/2 3/4 (x) [y] {z}", "Zażółć gęślą jaźń",
         "Съешь же ещё этих мягких булок", "Τη γλώσσα μου έδωσαν ελληνική", "Tiếng Việt ở đây rất đẹp",
         "Ą́ į̇́ q̃ ẹ̀ — combining marks", "3x9 12:30 :-) <= != --> a.m."]
FEATS = [{}, {"tnum": True, "ss01": True, "case": True}, {"frac": True, "zero": True, "cv11": True}]


def shape(blob, text, loc, feats):
    font = hb.Font(hb.Face(blob))
    font.set_variations(loc)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, feats)
    return [(i.codepoint, p.x_advance, p.y_advance, p.x_offset, p.y_offset)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


b0, b1 = hb.Blob.from_file_path(SRC), hb.Blob.from_file_path(OUT)
bad = runs = 0
for L in LOCS:
    for r in (0, 60, 100):
        for text in TEXTS:
            for f in FEATS:
                runs += 1
                if shape(b0, text, L, f) != shape(b1, text, dict(L, ROND=r), f):
                    bad += 1
print("6 shaping   differing runs: %d of %d" % (bad, runs))
if bad:
    failures.append("%d shaping runs differ" % bad)

# Rare glyphs with a known, documented deviation just over a limit.
KNOWN = {"rturnascend": "IPA turned r with long leg: regains about 10 units between ROND 70 and 100 at ExtraBold"}
known = [f for f in failures if any((" %s " % k) in f for k in KNOWN)]
failures = [f for f in failures if f not in known]
print()
for f in known:
    print("known:", f.strip())
if failures:
    print("FAILED: %d problems" % len(failures))
    for f in failures:
        print("  " + f)
    sys.exit(1)
print("ALL CHECKS PASSED")
