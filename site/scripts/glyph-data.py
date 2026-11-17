"""Extracts real outlines from the built font for the landing page's hero drawing.

python site/scripts/glyph-data.py   (from the repository root)
Writes site/src/data/glyphs.json: for each glyph, its path at ROND 0..100 in steps
of 5 (wght 800, opsz 32), the advance width, and the ink area at each step.
Every step has the same point structure, so the page interpolates between neighbours.
"""
import json, sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.recordingPen import RecordingPen

SRC = "fonts/variable/Inrond[ROND,opsz,wght].ttf"
CHARS = sys.argv[1] if len(sys.argv) > 1 else "a"
WGHT, OPSZ = 800, 32
STEPS = list(range(0, 101, 5))

base = TTFont(SRC)
partial = instantiateVariableFont(base, {"wght": WGHT, "opsz": OPSZ})
cmap = partial.getBestCmap()
out = {"wght": WGHT, "opsz": OPSZ, "upm": partial["head"].unitsPerEm, "steps": STEPS,
       "ascender": partial["hhea"].ascent, "descender": partial["hhea"].descent, "glyphs": {}}
for ch in CHARS:
    out["glyphs"][ch] = {"paths": [], "area": [], "adv": None}
for r in STEPS:
    inst = instantiateVariableFont(partial, {"ROND": r})
    gs = inst.getGlyphSet()
    for ch in CHARS:
        name = cmap[ord(ch)]
        rec = RecordingPen(); gs[name].draw(rec)
        # flat list of numbers so the page can interpolate
        nums, cmds = [], []
        for op, pts in rec.value:
            cmds.append([op, len(pts)])
            for x, y in pts: nums += [round(x, 1), round(y, 1)]
        ap = AreaPen(); gs[name].draw(ap)
        g = out["glyphs"][ch]
        g["paths"].append(nums); g["area"].append(round(abs(ap.value)))
        g["cmds"] = cmds
        g["adv"] = inst["hmtx"][name][0]
    print("ROND", r, file=sys.stderr)
json.dump(out, open("site/src/data/glyphs.json", "w"), separators=(",", ":"))
for ch, g in out["glyphs"].items():
    print(ch, "adv", g["adv"], "area 0/100", g["area"][0], g["area"][-1], "removed %.1f%%" % (100 - 100 * g["area"][-1] / g["area"][0]), "nums", len(g["paths"][0]))
