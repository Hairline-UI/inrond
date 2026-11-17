"""Outlines for the landing page's weight x roundness pad.

python site/scripts/pad-data.py   (from the repository root)
Writes site/src/data/pad.json: the word at every weight and roundness where the
font's own interpolation changes direction (its masters and roundness stops), at
optical size 32. Between those samples the font interpolates linearly, so the page
interpolates the same way and draws what the font draws.
"""
import json
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.varLib.models import piecewiseLinearMap

SRC = "fonts/variable/Inrond[ROND,opsz,wght].ttf"
WORD = "Sugar"
OPSZ = 32
RONDS = [0, 25, 50, 75, 100]

font = TTFont(SRC)
avar = font["avar"].segments["wght"]
inv = {v: k for k, v in avar.items()}
# user weight for a normalized (post-avar) weight
def user(n):
    pre = piecewiseLinearMap(n, inv)
    return 400 + pre * (500 if pre > 0 else 300)
# breakpoints: avar's own points, plus the helper master at normalized 0.5
norms = sorted(set(list(avar.values()) + [0.5]))
WEIGHTS = sorted({round(user(n), 1) for n in norms if n >= -1})
cmap = font.getBestCmap()
names = [cmap[ord(c)] for c in WORD]
blob = hb.Blob.from_file_path(SRC)
face = hb.Face(blob)
upm = font["head"].unitsPerEm
os2 = font["OS/2"]

def nums_of(rec):
    out = []
    for op, pts in rec.value:
        for x, y in pts:
            out += [round(x), round(y)]
    return out

cmds = None
inst = []
for w in WEIGHTS:
    row = []
    for r in RONDS:
        loc = {"wght": w, "opsz": OPSZ, "ROND": r}
        gs = font.getGlyphSet(location=loc)
        hf = hb.Font(face)
        hf.set_variations(loc)
        buf = hb.Buffer()
        buf.add_str(WORD)
        buf.guess_segment_properties()
        hb.shape(hf, buf, {"kern": True, "liga": False, "calt": False})
        xs, x = [], 0
        for p in buf.glyph_positions:
            xs.append(x + p.x_offset)
            x += p.x_advance
        glyphs, these = [], []
        for n in names:
            rec = RecordingPen()
            gs[n].draw(rec)
            these.append([[op, len(pts)] for op, pts in rec.value])
            glyphs.append(nums_of(rec))
        if cmds is None:
            cmds = these
        assert these == cmds, (w, r)
        row.append({"x": xs + [x], "g": glyphs})
    inst.append(row)
out = {
    "word": WORD, "upm": upm, "opsz": OPSZ, "weights": WEIGHTS, "ronds": RONDS, "cmds": cmds,
    "metrics": {"ascender": font["hhea"].ascent, "cap": os2.sCapHeight, "x": os2.sxHeight, "descender": font["hhea"].descent},
    "inst": inst,
}
json.dump(out, open("site/src/data/pad.json", "w"), separators=(",", ":"))
print("weights", WEIGHTS, "points per instance", sum(len(g) for g in inst[0][0]["g"]) // 2)
