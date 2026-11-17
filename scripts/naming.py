"""Family naming and metadata. Change FAMILY here to rename the whole project."""
from fontTools.ttLib import newTable
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables import ttProgram

FAMILY = "Inrond"
VERSION = "1.000"
VENDOR = "INRD"
SOURCE_FAMILY = "Inter"
SOURCE_VERSION = "4.1"
COPYRIGHT = ("Copyright 2026 The %s Project Authors. "
             "Based on Inter, Copyright 2016 The Inter Project Authors (https://github.com/rsms/inter)" % FAMILY)
DESIGNER = "The %s Project Authors. Roundness axis derived from Inter by Rasmus Andersson" % FAMILY
LICENSE = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
           "This license is available with a FAQ at: https://openfontlicense.org")
LICENSE_URL = "https://openfontlicense.org"


def ps(s):
    return s.replace(" ", "")


def apply(font, italic, rond_name_id):
    name = font["name"]
    # Windows/Unicode names only
    name.names = [n for n in name.names if n.platformID == 3]

    src_var, src_ps = SOURCE_FAMILY + " Variable", SOURCE_FAMILY + "Variable"
    for n in name.names:
        s = n.toUnicode()
        t = s.replace(src_var, FAMILY).replace(src_ps, ps(FAMILY))
        if t != s:
            n.string = t

    style = "Italic" if italic else "Regular"

    def set_(i, s):
        name.setName(s, i, 3, 1, 0x409)

    set_(0, COPYRIGHT)
    set_(1, FAMILY)
    set_(2, style)
    set_(3, "%s;%s;%s-%s" % (VERSION, VENDOR, ps(FAMILY), style))
    set_(4, "%s %s" % (FAMILY, style))
    set_(5, "Version %s; based on %s %s" % (VERSION, SOURCE_FAMILY, SOURCE_VERSION))
    set_(6, "%s-%s" % (ps(FAMILY), style))
    set_(9, DESIGNER)
    set_(13, LICENSE)
    set_(14, LICENSE_URL)
    set_(25, ps(FAMILY) + ("Italic" if italic else ""))
    for i in (7, 8, 10, 11, 12, 16, 17):
        name.removeNames(nameID=i)

    font["OS/2"].achVendID = VENDOR
    font["head"].fontRevision = float(VERSION)

    # the default named instance must carry the font's own PostScript name
    fvar = font["fvar"]
    default = {a.axisTag: a.defaultValue for a in fvar.axes}
    for inst in fvar.instances:
        if inst.coordinates == default and inst.postscriptNameID not in (0xFFFF, None):
            name.setName("%s-%s" % (ps(FAMILY), style), inst.postscriptNameID, 3, 1, 0x409)

    # STAT: declare the axis (before ital, which has to stay last) and its two named stops
    stat = font["STAT"].table
    axes = stat.DesignAxisRecord.Axis
    rec = ot.AxisRecord()
    rec.AxisTag = "ROND"
    rec.AxisNameID = rond_name_id
    old_order = list(axes)
    at = next((i for i, a in enumerate(axes) if a.AxisTag in ("slnt", "ital")), len(axes))
    axes.insert(at, rec)
    stat.DesignAxisCount = len(axes)
    for i, a in enumerate(axes):
        a.AxisOrdering = i
    remap = {i: axes.index(a) for i, a in enumerate(old_order)}
    for v in stat.AxisValueArray.AxisValue:
        if v.Format == 4:
            for r in v.AxisValueRecord:
                r.AxisIndex = remap[r.AxisIndex]
        else:
            v.AxisIndex = remap[v.AxisIndex]
    for value, label, flags in ((0.0, "Default", 2), (100.0, "Round", 0)):
        v = ot.AxisValue()
        v.Format, v.AxisIndex, v.Flags, v.Value = 1, at, flags, value
        v.ValueNameID = name.addMultilingualName({"en": label}, font, mac=False, minNameID=256)
        stat.AxisValueArray.AxisValue.append(v)
    stat.AxisValueCount = len(stat.AxisValueArray.AxisValue)

    # Unhinted outlines: ask rasterisers for smart dropout control and smoothing at
    # every size (the Google Fonts convention for unhinted variable fonts).
    if "fpgm" not in font:
        prep = newTable("prep")
        prep.program = ttProgram.Program()
        prep.program.fromBytecode(bytes([0xB8, 0x01, 0xFF, 0x85, 0xB0, 0x04, 0x8D]))   # PUSHW 511, SCANCTRL, PUSHB 4, SCANTYPE
        font["prep"] = prep
        gasp = newTable("gasp")
        gasp.version = 1
        gasp.gaspRange = {0xFFFF: 15}
        font["gasp"] = gasp
        font["head"].flags |= 1 << 3
