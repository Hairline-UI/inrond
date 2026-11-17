"""Benchmark candidate / rival fonts on measurable, production-relevant facts."""
import io
import sys
from fontTools.ttLib import TTFont

FONTS = sys.argv[1:]

VIET = "ẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼẾỀỂỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰỲỴỶỸơư"


def rng(cmap, a, b):
    return sum(1 for c in cmap if a <= c <= b)


def woff2_size(font):
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    font.flavor = None
    return buf.tell()


def feats(font, tag):
    if tag not in font or not font[tag].table.FeatureList:
        return []
    return sorted({f.FeatureTag for f in font[tag].table.FeatureList.FeatureRecord})


def master_peaks(font):
    if "gvar" not in font:
        return []
    axes = [a.axisTag for a in font["fvar"].axes]
    peaks = set()
    for g, tvs in font["gvar"].variations.items():
        for tv in tvs:
            peaks.add(tuple(round(tv.axes.get(a, (0, 0, 0))[1], 3) for a in axes))
        if len(peaks) > 64:
            break
    return sorted(peaks)


for path in FONTS:
    f = TTFont(path)
    cmap = f.getBestCmap()
    print("=" * 100)
    print(path.split("refs/")[-1])
    name = f["name"]
    print("  family:", name.getDebugName(16) or name.getDebugName(1), "| version:", name.getDebugName(5))
    import os
    print("  size: %d KB ttf/otf | %d KB woff2" % (os.path.getsize(path) // 1024, woff2_size(f) // 1024))
    if "fvar" in f:
        for a in f["fvar"].axes:
            print("  axis %s %g..%g (default %g)" % (a.axisTag, a.minValue, a.maxValue, a.defaultValue))
        print("  named instances:", len(f["fvar"].instances), "| gvar regions(peaks):", len(master_peaks(f)), master_peaks(f)[:24])
    else:
        print("  STATIC (no fvar)")
    print("  glyphs:", f["maxp"].numGlyphs, "| codepoints:", len(cmap), "| outlines:", "TrueType" if "glyf" in f else "CFF")
    upm = f["head"].unitsPerEm
    os2 = f["OS/2"]
    print("  upm %d | xHeight %.3f | capHeight %.3f | asc %.3f desc %.3f lineGap %.3f" % (
        upm, os2.sxHeight / upm, os2.sCapHeight / upm, f["hhea"].ascent / upm, f["hhea"].descent / upm, f["hhea"].lineGap / upm))
    print("  coverage: LatinExtA %d/128 | LatinExtB %d | LatinExtAdd %d/256 | Vietnamese %s | Greek %d | Cyrillic %d | arrows %d | math %d | boxdraw %d" % (
        rng(cmap, 0x100, 0x17F), rng(cmap, 0x180, 0x24F), rng(cmap, 0x1E00, 0x1EFF),
        "yes" if all(ord(c) in cmap for c in VIET) else "no",
        rng(cmap, 0x370, 0x3FF), rng(cmap, 0x400, 0x52F), rng(cmap, 0x2190, 0x21FF), rng(cmap, 0x2200, 0x22FF), rng(cmap, 0x2500, 0x257F)))
    gs, gp = feats(f, "GSUB"), feats(f, "GPOS")
    print("  GSUB (%d): %s" % (len(gs), " ".join(gs)))
    print("  GPOS (%d): %s" % (len(gp), " ".join(gp)))
    print("  hinted:", "fpgm" in f, "| STAT:", "STAT" in f, "| avar:", "avar" in f, "| HVAR:", "HVAR" in f, "| MVAR:", "MVAR" in f)
