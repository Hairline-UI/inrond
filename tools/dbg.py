"""Dump corner analysis for a glyph in one master: dbg.py font glyph master_index"""
import math
import sys
sys.path.insert(0, "scripts")
from fontTools.ttLib import TTFont
import build
from roundlib import GlyphRounder

font = TTFont(sys.argv[1])
src = build.Source(font)
stems, _ = build.reference_stems(src)
name, m = sys.argv[2], int(sys.argv[3])
masters, on, ph = src.contours(name)
gr = GlyphRounder(masters, on, stems, font["head"].unitsPerEm)
rr = [gr.radii(m, ci) if st else None for ci, st in enumerate(gr.structs)]
print(name, "master", src.locs[m], "stem %.0f cap %.1f" % (stems[m], gr.caps[m]))
for ci, st in enumerate(gr.structs):
    if st is None:
        continue
    P, C = gr.geo[m][ci]
    print(" contour", ci, "nodes", st.count)
    for k in range(st.count):
        cr = gr.cor[m][ci][k]
        seg = "line" if C[k] is None else "quad c=(%.0f,%.0f)" % C[k]
        print("  %2d %-3s (%6.0f,%6.0f) turn %6.1f %s %s r=%5.1f -> %s" % (
            k, st.nodes[k][0], P[k][0], P[k][1], math.degrees(cr.turn), "cvx" if cr.convex else "ccv",
            "ROUND" if gr.rounded[ci][k] else "     ", rr[ci][k], seg))
