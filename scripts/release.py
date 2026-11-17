"""Produce every shipped file from the two source fonts.

    python scripts/release.py [--skip-build] [--no-static] [--no-pinned]

fonts/variable/   Inrond[ROND,opsz,wght].ttf, Inrond-Italic[ROND,opsz,wght].ttf, and the
                  fixed-roundness variable fonts InrondRound / InrondSoft [opsz,wght]
fonts/webfonts/   all of them as woff2, plus unicode-range subsets and one css per family
fonts/static/     fixed-roundness families for apps without variable font support
"""
import argparse
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.varLib import instancer

sys.path.insert(0, str(Path(__file__).parent))
import build  # noqa: E402
import naming  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources"
FONTS = ROOT / "fonts"
F = naming.FAMILY
AXES = "[ROND,opsz,wght]"

# Same slices Google Fonts serves, so a page only downloads what it uses.
SUBSETS = {
    "latin": "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,"
             "U+20AC,U+2122,U+2190-2193,U+2212,U+2215,U+FEFF,U+FFFD",
    "latin-ext": "U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,"
                 "U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,U+2C60-2C7F,U+A720-A7FF",
    "vietnamese": "U+0102-0103,U+0110-0111,U+0128-0129,U+0168-0169,U+01A0-01A1,U+01AF-01B0,U+0300-0301,"
                  "U+0303-0304,U+0308-0309,U+0323,U+0329,U+1EA0-1EF9,U+20AB",
    "cyrillic": "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116",
    "cyrillic-ext": "U+0460-052F,U+1C80-1C8A,U+20B4,U+2DE0-2DFF,U+A640-A69F,U+FE2E-FE2F",
    "greek": "U+0370-0377,U+037A-037F,U+0384-038A,U+038C,U+038E-03A1,U+03A3-03FF",
    "greek-ext": "U+1F00-1FFF",
}
WEIGHTS = [(100, "Thin"), (200, "ExtraLight"), (300, "Light"), (400, "Regular"), (500, "Medium"),
           (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"), (900, "Black")]
STATIC = [("Round", 100), ("Soft", 50)]
PINNED = STATIC     # the same two settings as variable fonts that keep weight and optical size


def woff2(font, path):
    font.flavor = "woff2"
    font.save(path)
    font.flavor = None
    return path.stat().st_size


def rename(font, family):
    """Give a font derived from the main build its own family name."""
    name = font["name"]
    for n in name.names:
        if n.nameID in (0, 5, 9, 13, 14):
            continue
        s = n.toUnicode()
        psf = family.replace(" ", "")
        if n.nameID == 25:
            t = s.replace(F, psf, 1)
        elif s == F:
            t = family
        else:
            t = s.replace(F + "Italic-", psf + "Italic-").replace(F + "-", psf + "-").replace(F + " ", family + " ")
        if t != s:
            n.string = t


def make_pinned(ttf, italic, label, rond, css, out_dir=None):
    """One roundness, frozen: a variable font that keeps weight and optical size
    and costs about a third less than the full design space."""
    family = "%s %s" % (F, label)
    stem = family.replace(" ", "") + ("-Italic" if italic else "")
    font = TTFont(ttf)
    for inst in font["fvar"].instances:         # keep the nine named weights
        inst.coordinates["ROND"] = rond
    font = instancer.instantiateVariableFont(font, {"ROND": rond})
    rename(font, family + " VF")     # not the name of the static family, so both can be installed
    # STAT keeps the roundness axis so the family relates to its siblings. Say where
    # on it this font sits; the family name already carries the word, so it is elided.
    stat = font["STAT"].table
    at = next(i for i, a in enumerate(stat.DesignAxisRecord.Axis) if a.AxisTag == "ROND")
    values = stat.AxisValueArray.AxisValue
    mine = [v for v in values if v.Format == 1 and v.AxisIndex == at]
    if not mine:
        v = ot.AxisValue()
        v.Format, v.AxisIndex, v.Flags, v.Value = 1, at, 0, float(rond)
        v.ValueNameID = font["name"].addMultilingualName({"en": label}, font, mac=False, minNameID=256)
        values.append(v)
        stat.AxisValueCount = len(values)
        mine = [v]
    for v in mine:
        v.Flags |= 2
    var_dir = out_dir or FONTS / "variable"
    web_dir = out_dir or FONTS / "webfonts"
    target = var_dir / (stem + "[opsz,wght].ttf")
    font.save(target)
    size = woff2(TTFont(target), web_dir / (stem + "[opsz,wght].woff2"))
    print("%s  %d KB ttf, %d KB woff2" % (target.name, target.stat().st_size // 1024, size // 1024))
    make_subsets(target, stem, italic, css, family=family, out=web_dir)


def make_subsets(ttf, stem, italic, css, family=F, out=None):
    out = out or FONTS / "webfonts"
    for name, ranges in SUBSETS.items():
        opts = subset.Options()
        opts.layout_features = ["*"]
        opts.flavor = "woff2"
        opts.name_IDs = ["*"]
        opts.notdef_outline = True
        opts.glyph_names = False
        font = TTFont(ttf)
        unicodes = subset.parse_unicodes(ranges)
        if not set(unicodes) & set(font.getBestCmap()):
            continue
        s = subset.Subsetter(opts)
        s.populate(unicodes=unicodes)
        s.subset(font)
        target = out / ("%s.%s.woff2" % (stem, name))
        font.flavor = "woff2"
        font.save(target)
        css.append("/* %s */\n@font-face {\n  font-family: '%s';\n  font-style: %s;\n  font-weight: 100 900;\n"
                   "  font-display: swap;\n  src: url('%s') format('woff2');\n  unicode-range: %s;\n}\n" % (
                       name, family, "italic" if italic else "normal", target.name, ranges.replace(",", ", ")))
        print("  %-34s %4d KB" % (target.name, target.stat().st_size // 1024))


def make_static(ttf, italic):
    out = FONTS / "static"
    out.mkdir(parents=True, exist_ok=True)
    for label, rond in STATIC:
        family = "%s %s" % (F, label)
        for wght, wname in WEIGHTS:
            font = TTFont(ttf)
            font = instancer.instantiateVariableFont(font, {"wght": wght, "opsz": 14, "ROND": rond})
            style = wname + (" Italic" if italic else "")
            if style == "Regular Italic":
                style = "Italic"
            ps = "%s-%s" % (family.replace(" ", ""), style.replace(" ", ""))
            ribbi = wname in ("Regular", "Bold")
            name = font["name"]

            def set_(i, s):
                name.setName(s, i, 3, 1, 0x409)

            for i in (16, 17, 21, 22, 25):
                name.removeNames(nameID=i)
            name.names = [n for n in name.names if n.nameID < 256]
            if ribbi:
                set_(1, family)
                set_(2, style)
            else:
                set_(1, "%s %s" % (family, wname))
                set_(2, "Italic" if italic else "Regular")
                set_(16, family)
                set_(17, style)
            set_(3, "%s;%s;%s" % (naming.VERSION, naming.VENDOR, ps))
            set_(4, "%s %s" % (family, style))
            set_(6, ps)
            os2 = font["OS/2"]
            os2.usWeightClass = wght
            sel = os2.fsSelection & ~0b1100001          # clear italic, bold, regular
            if italic:
                sel |= 1
            if wname == "Bold":
                sel |= 1 << 5
            if wname != "Bold" and not italic:      # name ID 2 is "Regular" for every upright non-bold style
                sel |= 1 << 6
            os2.fsSelection = sel
            font["head"].macStyle = (1 if wname == "Bold" else 0) | (2 if italic else 0)
            for tag in ("STAT", "avar", "fvar", "gvar", "HVAR", "MVAR"):
                if tag in font:
                    del font[tag]
            font.save(out / (ps + ".ttf"))
    print("  static: %d files for %s" % (len(STATIC) * len(WEIGHTS), "italic" if italic else "roman"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-build", action="store_true")
    ap.add_argument("--no-static", action="store_true")
    ap.add_argument("--no-pinned", action="store_true")
    ap.add_argument("--no-subsets", action="store_true", help="skip the subsets of the main fonts (inrond.css is left as it is)")
    a = ap.parse_args()
    (FONTS / "variable").mkdir(parents=True, exist_ok=True)
    (FONTS / "webfonts").mkdir(parents=True, exist_ok=True)
    css = ["/* %s %s. Latin-first unicode-range subsets; every axis is available:\n"
           "   font-variation-settings: 'ROND' 0..100; font-weight: 100..900; opsz follows font-size. */\n" % (
               F, naming.VERSION)]
    pinned_css = {label: ["/* %s %s %s: roundness fixed at %d. font-weight: 100..900; opsz follows font-size. */\n" % (
        F, label, naming.VERSION, rond)] for label, rond in PINNED}
    for italic in (False, True):
        stem = F + ("-Italic" if italic else "")
        source = SOURCES / ("InterVariable-Italic.ttf" if italic else "InterVariable.ttf")
        ttf = FONTS / "variable" / (stem + AXES + ".ttf")
        if not a.skip_build:
            print("building", ttf.name)
            build.build(str(source), str(ttf), italic=italic)
        size = woff2(TTFont(ttf), FONTS / "webfonts" / (stem + AXES + ".woff2"))
        print("%s  %d KB ttf, %d KB woff2" % (ttf.name, ttf.stat().st_size // 1024, size // 1024))
        if not a.no_subsets:
            make_subsets(ttf, stem, italic, css)
        if not a.no_pinned:
            for label, rond in PINNED:
                make_pinned(ttf, italic, label, rond, pinned_css[label])
        if not a.no_static:
            make_static(ttf, italic)
    if not a.no_subsets:
        (FONTS / "webfonts" / (F.lower() + ".css")).write_text("\n".join(css), encoding="utf-8")
    if not a.no_pinned:
        for label, lines in pinned_css.items():
            (FONTS / "webfonts" / ("%s-%s.css" % (F.lower(), label.lower()))).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
