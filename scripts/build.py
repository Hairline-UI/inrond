"""Build a variable font with a Roundness (ROND) axis from an existing variable font.

    python scripts/build.py SOURCE.ttf OUTPUT.ttf [--italic]

Every master of the source is rounded with scripts/roundlib.py, then the sharp
and the rounded outlines are stored as one design space: the source axes plus
ROND 0..100. Layout, metrics, kerning and anchors are untouched, so text set at
any roundness has exactly the line breaks of the source design.

How the outlines are stored
  base        sharp and fully round outline of every source master
  corrections the exact outline at roundness 25, 50 and 75 and at a mid weight. A cap's
              end travels along its stroke as the cap grows; plain interpolation
              would cut that path short. Stored as sparse deltas on top of the
              base and dropped where they are zero, so they cost little.
"""
import argparse
import sys
import time
from array import array
from functools import partial
from pathlib import Path

from fontTools.misc.roundTools import otRound
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._f_v_a_r import Axis
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.varLib.iup import iup_delta, iup_delta_optimize
from fontTools.varLib.models import VariationModel, supportScalar

sys.path.insert(0, str(Path(__file__).parent))
import naming  # noqa: E402
from roundlib import GlyphRounder, bbox, covered, flatten  # noqa: E402

ROND = "ROND"
ROUND = partial(GlyphCoordinates.__round__, round=otRound)


# --------------------------------------------------------------------------- source masters
def master_locations(font):
    """Normalised master locations of the source: the default plus every gvar peak."""
    axes = [a.axisTag for a in font["fvar"].axes]
    peaks = {tuple(0.0 for _ in axes)}
    for tvs in font["gvar"].variations.values():
        for tv in tvs:
            peaks.add(tuple(round(tv.axes.get(a, (0, 0, 0))[1], 4) for a in axes))
    return [dict(zip(axes, p)) for p in sorted(peaks, key=lambda p: (sum(1 for v in p if v), p))]


def mid_weight_locations(masters, at=0.5):
    """Extra locations halfway up the bold side of the weight axis, where round
    caps grow fastest and interpolation needs help."""
    out = []
    if not masters or "wght" not in masters[0]:
        return out
    for m in masters:
        if m["wght"] == 1.0 and dict(m, wght=0.0) in masters:
            out.append(dict(m, wght=at))
    return out


class Source:
    def __init__(self, font, mid=0.5):
        self.font = font
        self.glyf = font["glyf"]
        self.gvar = font["gvar"]
        self.hmtx = font["hmtx"].metrics
        self.masters = master_locations(font)
        self.extra = mid_weight_locations(self.masters, mid) if mid else []
        self.locs = self.masters + self.extra
        self._cache = {}

    def coords(self, name):
        """[GlyphCoordinates incl. phantoms, one per location], controls."""
        if name in self._cache:
            return self._cache[name]
        base, control = self.glyf._getCoordinatesAndControls(name, self.hmtx)
        tvs = self.gvar.variations.get(name, [])
        filled = []
        for tv in tvs:
            d = tv.coordinates
            if None in d:
                d = iup_delta(d, base, control.endPts)
            filled.append(GlyphCoordinates(d))
        out = []
        for loc in self.locs:
            c = GlyphCoordinates(base)
            for tv, d in zip(tvs, filled):
                s = supportScalar(loc, tv.axes)
                if s:
                    c += d * s
            out.append(c)
        self._cache[name] = (out, control)
        return out, control

    def contours(self, name):
        """Per location: list of contours [(x, y), ...]; plus on-curve flags and phantoms."""
        coords, control = self.coords(name)
        ends = control.endPts
        flags = [f & 1 for f in control.flags]
        on, start = [], 0
        for e in ends:
            on.append([bool(f) for f in flags[start:e + 1]])
            start = e + 1
        masters, phantoms = [], []
        for c in coords:
            cs, start = [], 0
            for e in ends:
                cs.append([c[i] for i in range(start, e + 1)])
                start = e + 1
            masters.append(cs)
            phantoms.append([c[i] for i in range(len(c) - 4, len(c))])
        return masters, on, phantoms


def reference_stems(src):
    """Stem width per location, measured on the simplest stem in the font."""
    for name in ("l", "I", "uni0406", "bar"):
        g = src.glyf[name] if name in src.glyf.keys() else None
        if g is None or g.isComposite() or g.numberOfContours != 1 or len(g.coordinates) != 4:
            continue
        masters, _, _ = src.contours(name)
        out = []
        for m in masters:
            c = m[0]
            edges = [((c[i][0] - c[i - 1][0]) ** 2 + (c[i][1] - c[i - 1][1]) ** 2) ** 0.5 for i in range(4)]
            area = abs(sum(c[i - 1][0] * c[i][1] - c[i][0] * c[i - 1][1] for i in range(4))) / 2
            out.append(area / max(edges))       # perpendicular width, also when slanted
        return out, name
    raise SystemExit("no reference stem glyph found")


# --------------------------------------------------------------------------- composites
def flatten_components(src, name, m, depth=0):
    """[(base glyph name, affine 2x3)] for one location of a composite glyph."""
    g = src.glyf[name]
    coords, _ = src.coords(name)
    out = []
    for i, comp in enumerate(g.components):
        dx, dy = coords[m][i]
        if hasattr(comp, "transform"):
            (a, b), (c, d) = comp.transform
        else:
            a, b, c, d = 1.0, 0.0, 0.0, 1.0
        t = (a, b, c, d, dx, dy)
        sub = src.glyf[comp.glyphName]
        if sub.isComposite():
            if depth > 6:
                continue
            for bn, t2 in flatten_components(src, comp.glyphName, m, depth + 1):
                out.append((bn, compose(t2, t)))
        elif sub.numberOfContours > 0:
            out.append((comp.glyphName, t))
    return out


def compose(inner, outer):
    a1, b1, c1, d1, e1, f1 = inner
    a2, b2, c2, d2, e2, f2 = outer
    return (a1 * a2 + b1 * c2, a1 * b2 + b1 * d2, c1 * a2 + d1 * c2, c1 * b2 + d1 * d2,
            e1 * a2 + f1 * c2 + e2, e1 * b2 + f1 * d2 + f2)


def apply(t, p):
    a, b, c, d, e, f = t
    return (p[0] * a + p[1] * c + e, p[0] * b + p[1] * d + f)


def text_glyphs(font):
    """Glyphs a user can actually get in text: mapped in cmap or produced by GSUB."""
    out = set(font.getBestCmap().values())
    if "GSUB" not in font:
        return out
    for lookup in font["GSUB"].table.LookupList.Lookup:
        for st in lookup.SubTable:
            if st.LookupType == 7:
                st = st.ExtSubTable
            if hasattr(st, "mapping"):
                for v in st.mapping.values():
                    out.update([v] if isinstance(v, str) else v)
            if hasattr(st, "alternates"):
                for v in st.alternates.values():
                    out.update(v)
            if hasattr(st, "ligatures"):
                for ligs in st.ligatures.values():
                    out.update(l.LigGlyph for l in ligs)
    return out


def find_joins(src, rounders, composite, log):
    """A fillet must never open a gap where one component joins another (ogonek,
    cedilla, horn, Cyrillic tails ...). Returns (blocked corners per glyph,
    composites that have to be rounded as outlines of their own)."""
    M = len(src.locs)
    conflicts, users = {}, {}
    for name in composite:
        for m in range(M):
            parts = flatten_components(src, name, m)
            if m == 0:
                for bn, _ in parts:
                    users.setdefault(bn, set()).add(name)
            if len(parts) < 2:
                break
            polys = []
            for bn, t in parts:
                gr = rounders[bn][0]
                polys.append([[apply(t, p) for p in flatten(st, *gr.geo[m][ci])]
                              for ci, st in enumerate(gr.structs) if st is not None])
            for pi, (bn, t) in enumerate(parts):
                gr = rounders[bn][0]
                others = [p for pj, ps in enumerate(polys) if pj != pi for p in ps]
                boxes = [bbox(p) for p in others]
                for ci, st in enumerate(gr.structs):
                    if st is None:
                        continue
                    for k in range(st.count):
                        if not gr.rounded[ci][k]:
                            continue
                        near = [covered(apply(t, p), others, boxes) for p in gr.near_probes(m, ci, k)]
                        far = [covered(apply(t, p), others, boxes) for p in gr.far_probes(m, ci, k)]
                        # harmful: a buried corner whose fillet would surface, or a
                        # visible corner that butts against the other component
                        if (near[0] and not all(far)) or (not near[0] and any(near[1:])):
                            conflicts.setdefault(name, set()).add((bn, ci, k))
    # A part that joins in most of its uses and is never typed on its own (ogonek,
    # tail, combining cedilla) simply keeps that end sharp. A letter that is
    # joined in a few composites stays fully round; those composites are rounded
    # as outlines of their own instead.
    hit = {}
    for name, items in conflicts.items():
        for bn, ci, k in items:
            hit.setdefault(bn, set()).add(name)
    typed = text_glyphs(src.font)
    marks = set()
    if "GDEF" in src.font and src.font["GDEF"].table.GlyphClassDef:
        marks = {g for g, c in src.font["GDEF"].table.GlyphClassDef.classDefs.items() if c == 3}
    parts_only = {bn for bn, gs in hit.items()
                  if len(gs) * 2 >= len(users[bn]) and (bn not in typed or bn in marks)}
    blocked, decompose = {}, []
    for name, items in conflicts.items():
        for bn, ci, k in items:
            if bn in parts_only:
                blocked.setdefault(bn, set()).add((ci, k))
        if any(bn not in parts_only for bn, _, _ in items):
            decompose.append(name)
    if blocked:
        log("joining parts kept sharp at the join: %d corners in %d glyphs: %s" % (
            sum(len(v) for v in blocked.values()), len(blocked), " ".join(sorted(blocked))))
    if decompose:
        log("composites rounded as their own outlines: %d" % len(decompose))
    return blocked, decompose


def decomposed(src, name):
    """Contours of a composite glyph at every location, as if drawn in one piece."""
    masters, on = [], None
    for m in range(len(src.locs)):
        cs, flags = [], []
        for bn, t in flatten_components(src, name, m):
            bm, bon, _ = src.contours(bn)
            flip = t[0] * t[3] - t[1] * t[2] < 0
            for contour, f in zip(bm[m], bon):
                pts = [apply(t, p) for p in contour]
                cs.append(pts[::-1] if flip else pts)
                flags.append(f[::-1] if flip else f)
        masters.append(cs)
        on = flags
    coords, _ = src.coords(name)
    phantoms = [[c[i] for i in range(len(c) - 4, len(c))] for c in coords]
    return masters, on, phantoms


# --------------------------------------------------------------------------- output helpers
def flat(contours, phantoms):
    pts = [p for c in contours for p in c] + list(phantoms)
    return GlyphCoordinates([(otRound(x), otRound(y)) for x, y in pts])


def make_glyph(flags_per_contour):
    g = Glyph()
    g.numberOfContours = len(flags_per_contour)
    ends, n = [], 0
    for f in flags_per_contour:
        n += len(f)
        ends.append(n - 1)
    g.endPtsOfContours = ends
    g.flags = array("B", [f for c in flags_per_contour for f in c])
    g.program = ttProgram.Program()
    g.program.fromBytecode(b"")
    return g, ends


NOISE = 1       # corrections of a single unit are rounding noise, not shape

# Rare glyphs whose arms are too short for a full-strength cap at the heaviest
# italic weight: full strength turns the arm into a spike that leaves the source
# outline. They are rounded at reduced strength instead. Specific to Inter.
GENTLE_ITALIC = {"g.sc": 0.75, "uni0260.sc": 0.75, "uni20A2": 0.75}


def quiet(delta):
    """Round a correction and drop what is too small to matter."""
    out = []
    for x, y in delta:
        x, y = otRound(x), otRound(y)
        out.append((0, 0) if abs(x) <= NOISE and abs(y) <= NOISE else (x, y))
    return GlyphCoordinates(out)


class Space:
    """The design space of the output font and how glyph outlines are stored in it."""

    def __init__(self, src, axis_tags, stops):
        self.n_orig = len(src.masters)
        self.locs = [{k: v for k, v in L.items() if v} for L in src.locs]
        self.stops = stops
        self.order = axis_tags + [ROND]
        base = []
        for L in self.locs[:self.n_orig]:
            base.append(dict(L))
            base.append(dict(L, **{ROND: 1.0}))
        self.base = VariationModel(base, axisOrder=self.order)
        self.field = VariationModel(self.locs, axisOrder=axis_tags)

    def variations(self, layers, ends):
        """layers[i][m]: GlyphCoordinates of layer i (0 sharp, then one per stop)
        at location m. Returns (default coordinates, [TupleVariation])."""
        full = len(self.stops)
        items = []
        for m in range(self.n_orig):
            items += [layers[0][m], layers[full][m]]
        deltas, supports = self.base.getDeltasAndSupports(items, round=ROUND)
        default = deltas[0]
        pairs = list(zip(supports[1:], deltas[1:]))
        def base_at(m, r):
            return self.base.interpolateFromDeltas(dict(self.locs[m], **{ROND: r}), deltas)

        n = len(self.locs)
        # exact outlines at the in-between roundness stops, at every location. Each
        # is a tent that peaks at its stop and is zero at its neighbours, so the
        # stops do not disturb one another.
        marks = [0.0] + list(self.stops)
        for i in range(1, full):
            vals = [quiet(layers[i][m] - base_at(m, marks[i])) for m in range(n)]
            d, s = self.field.getDeltasAndSupports(vals, round=ROUND)
            tent = (marks[i - 1], marks[i], marks[i + 1])
            pairs += [(dict(sup, **{ROND: tent}), dl) for sup, dl in zip(s, d)]
        if n > self.n_orig:                 # exact fully round outlines at the mid weights
            zero = GlyphCoordinates.zeros(len(default))
            vals = [zero] * self.n_orig + [quiet(layers[full][m] - base_at(m, 1.0))
                                           for m in range(self.n_orig, n)]
            d, s = self.field.getDeltasAndSupports(vals, round=ROUND)
            tent = (marks[full - 1], 1.0, 1.0)
            pairs += [(dict(sup, **{ROND: tent}), dl) for sup, dl in zip(s, d)]
        out = []
        for support, delta in pairs:
            if all(v == 0 for v in delta.array):
                continue
            var = TupleVariation(support, delta)
            opt = iup_delta_optimize(delta, default, ends, tolerance=0.5)
            if None in opt:
                if all(d is None for d in opt):
                    opt = [(0, 0)] + [None] * (len(opt) - 1)
                var_opt = TupleVariation(support, opt)
                tags = sorted(support.keys())
                a, b = var.compile(tags), var_opt.compile(tags)
                if len(b[0]) + len(b[1]) < len(a[0]) + len(a[1]):
                    var = var_opt
            out.append(var)
        return default, out


def add_axis_to_store(store):
    rl = store.VarRegionList
    for region in rl.Region:
        ax = ot.VarRegionAxis()
        ax.StartCoord = ax.PeakCoord = ax.EndCoord = 0
        region.VarRegionAxis.append(ax)
    rl.RegionAxisCount += 1


# --------------------------------------------------------------------------- main
def build(src_path, out_path, italic=False, only=None, factor=1.0, stops=(0.25, 0.5, 0.75, 1.0), mid=0.5, log=print):
    t0 = time.time()
    font = TTFont(src_path)
    src = Source(font, mid)
    glyf, gvar = font["glyf"], font["gvar"]
    upm = font["head"].unitsPerEm
    axis_tags = [a.axisTag for a in font["fvar"].axes]
    M = len(src.locs)
    stems, ref = reference_stems(src)
    log("source masters: %d, plus %d mid-weight helpers" % (len(src.masters), len(src.extra)))
    log("reference stem (%s): %s" % (ref, " ".join("%.0f" % s for s in stems)))

    order = font.getGlyphOrder()
    # Renderers place a glyph by its left side bearing and its bounding box
    # together; remember how the two relate in the source so it can be restored.
    hmtx = font["hmtx"].metrics
    bearing = {n: hmtx[n][1] - glyf[n].xMin for n in order if glyf[n].numberOfContours != 0}
    simple = [n for n in order if not glyf[n].isComposite() and glyf[n].numberOfContours > 0]
    composite = [n for n in order if glyf[n].isComposite()]
    if only:
        simple = [n for n in simple if n in only]
        composite = []

    gentle = GENTLE_ITALIC if italic else {}

    def rounder(name, parts, blocked=()):
        masters, on, phantoms = parts
        f = factor * gentle.get(name, 1.0)
        return (GlyphRounder(masters, on, stems, upm, f, blocked=blocked, stops=stops), masters, on, phantoms)

    rounders = {name: rounder(name, src.contours(name)) for name in simple}
    blocked, decompose = find_joins(src, rounders, composite, log)
    for bn, keys in blocked.items():
        rounders[bn] = rounder(bn, rounders[bn][1:], keys)
    for name in decompose:
        rounders[name] = rounder(name, decomposed(src, name))
        simple.append(name)
    if gentle:
        log("rounded at reduced strength: %s" % " ".join(sorted(n for n in gentle if n in rounders)))

    space = Space(src, axis_tags, stops)
    n_corners = n_before = n_after = n_curved = 0
    for name in simple:
        gr, _, _, phantoms = rounders[name]
        flags, layers = gr.build()
        coords = [[flat(lay[m], phantoms[m]) for m in range(M)] for lay in layers]
        old = glyf[name]
        was_simple = not old.isComposite()
        g, ends = make_glyph(flags)
        curved = gr.curved()
        default, variations = space.variations(coords, ends)
        g.coordinates = GlyphCoordinates(list(default)[:len(default) - 4])
        if was_simple and old.flags[0] & 0x40:
            g.flags[0] |= 0x40
        g.recalcBounds(glyf)
        glyf[name] = g
        gvar.variations[name] = variations
        n_corners += gr.n_rounded()
        n_before += len(old.coordinates) if was_simple else 0
        n_after += len(g.coordinates)
        n_curved += curved
    log("rounded %d corners in %d glyphs (%d with caps on curves); points %d -> %d" % (
        n_corners, len(simple), n_curved, n_before, n_after))

    # Splitting curves moves control points, which moves bounding boxes (they
    # include control points). Keep every side bearing in step with its box, for
    # rebuilt glyphs and for the composites that use them; otherwise FreeType
    # and friends would draw the glyph shifted sideways.
    done = set()
    for n in order:
        g = glyf[n]
        if g.numberOfContours == 0:
            continue
        g.recalcBounds(glyf, boundsDone=done)
        hmtx[n] = (hmtx[n][0], g.xMin + bearing[n])

    # the new axis
    name_table = font["name"]
    ax = Axis()
    ax.axisTag, ax.minValue, ax.defaultValue, ax.maxValue, ax.flags = ROND, 0, 0, 100, 0
    ax.axisNameID = name_table.addMultilingualName({"en": "Roundness"}, font, mac=False, minNameID=256)
    font["fvar"].axes.append(ax)
    for inst in font["fvar"].instances:
        inst.coordinates[ROND] = 0
    if "avar" in font:
        font["avar"].segments[ROND] = {-1.0: -1.0, 0.0: 0.0, 1.0: 1.0}
    for tag in ("HVAR", "MVAR", "VVAR", "GDEF", "BASE"):
        if tag in font and getattr(font[tag].table, "VarStore", None):
            add_axis_to_store(font[tag].table.VarStore)
    naming.apply(font, italic=italic, rond_name_id=ax.axisNameID)

    font["maxp"].recalc(font)
    font.save(out_path)
    log("saved %s (%.0f KB) in %.0fs" % (out_path, Path(out_path).stat().st_size / 1024, time.time() - t0))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--italic", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--factor", type=float, default=1.0)
    ap.add_argument("--stops", default="0.25,0.5,0.75,1", help="roundness stops solved exactly, as shares of full roundness")
    ap.add_argument("--mid", type=float, default=0.5, help="normalised weight of the helper master, 0 for none")
    a = ap.parse_args()
    build(a.src, a.out, a.italic, set(a.only.split(",")) if a.only else None, a.factor,
          tuple(float(x) for x in a.stops.split(",")), a.mid)
