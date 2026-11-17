"""Interpolation-compatible corner rounding for TrueType (quadratic) outlines.

The model is a round pen: every *convex* corner of the filled shape is replaced
by a circular fillet. A stroke end gets the circle inscribed between its two
sides, so it becomes a true round cap; an outer corner gets a radius of half the
local stroke width. Concave corners (joins, crotches, counters) stay sharp,
exactly as a round nib would leave them.

Everything is computed for all masters of a glyph at once so that the sharp and
the rounded outline of every master share one point structure. In the sharp
outline each fillet collapses onto its corner; in the rounded outline the same
four points spread into an arc. Interpolating between the two scales the fillet
about the corner, which is what makes a continuous roundness axis possible.
"""
import math

import numpy as np

EPS = 1e-6
INF = float("inf")
MIN_TURN = math.radians(20)      # smaller direction changes are not treated as corners
MAX_TURN = math.radians(172)
SMOOTH_TURN = math.radians(8)    # a fillet may run through nodes smoother than this
HELPER_TURN = math.radians(12.5) # ... or, in an interpolated helper master, smoother than this
REVERSAL = math.radians(150)     # a turn sharper than this is an outline doubling back, not a corner
TERMINAL_TURN = math.radians(50)
END_TURN = math.radians(20)      # ... its other corner may be as blunt as this (the top right of 7)
TERMINAL_WIDTH = 2.2           # a stroke end is at most this many local stroke widths wide
CORNER = 0.93              # radius of an outer corner, as a share of the largest circle that fits in it
CORNER_MAX = 0.62                # ... and at most this many reference stems
DISC_GAIN = 1.4                  # the circle in a corner beside a curve may be this much larger than between its tangents
VISIBLE = 0.93                   # share of an edge a fillet may take before the edge runs into another contour
THICK_MAX = 1.15                 # a stroke counts as at most this many reference stems thick
SAMPLES = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
CURVE_REACH = 0.70               # share of the last curve segment a fillet may consume
SPLIT_REACH = 0.94               # ... where the run was divided between two corners: the rest belongs to neither
MAX_CHAIN = 5
OV_SHARE = 0.16                  # a round cap may pass its cut by this share of its radius ...
PIN_COS = math.cos(math.radians(30))    # a cap may start at a crotch if it leaves the side by less than this
EXTEND = 0.3                     # a side may be carried on past a crotch by this many cap radii ...
EXTEND_FAR = 0.6                 # ... or this many, where the circle cannot start at the crotch either
FULLER = 0.003                   # how much longer than a circle's the handles of a cap are, per degree its arcs differ from half a turn
FRONT = 60.0                     # a cap with less room than this in front of it (units of a 2048 em) does not pass its cut
MIN_RATIO = 0.15                 # the stroke-side handle of a join is at least this share of the fillet's
JOIN_SHARE = 0.6                 # share of the run the first piece next to a fillet may take
ROUND_TOL = 0.5                  # a cap whose two arcs meet within this many units is one circle
TINY = 10.0                      # an edge shorter than this between two corners is one corner drawn with two points
SQUARE = 1.1                     # two ends that share a corner and differ in width by less than this: a square dot


# --------------------------------------------------------------------------- vector helpers
def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, s):
    return (a[0] * s, a[1] * s)


def length(v):
    return math.hypot(v[0], v[1])


def unit(v):
    l = math.hypot(v[0], v[1])
    return (v[0] / l, v[1] / l) if l > EPS else None


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def left(u):
    return (-u[1], u[0])


def quad_pt(p0, c, p2, t):
    m = 1 - t
    return (m * m * p0[0] + 2 * m * t * c[0] + t * t * p2[0],
            m * m * p0[1] + 2 * m * t * c[1] + t * t * p2[1])


def quad_tan(p0, c, p2, t):
    m = 1 - t
    return (m * (c[0] - p0[0]) + t * (p2[0] - c[0]), m * (c[1] - p0[1]) + t * (p2[1] - c[1]))


def quad_blossom(p0, c, p2, t1, t2):
    """Control point of the sub-curve [t1, t2] of a quadratic."""
    a, b, d = (1 - t1) * (1 - t2), t1 * (1 - t2) + t2 * (1 - t1), t1 * t2
    return (a * p0[0] + b * c[0] + d * p2[0], a * p0[1] + b * c[1] + d * p2[1])


def line_intersection(p, d1, q, d2):
    den = cross(d1, d2)
    if abs(den) < 1e-9:
        return None
    t = cross(sub(q, p), d2) / den
    return (p[0] + d1[0] * t, p[1] + d1[1] * t)


_ARC = {}


def arc_handle(phi):
    """Where the two handles of a fillet sit between its ends and the meeting
    point of its tangents. The fillet is two quadratics; with the textbook
    handle their joint lies on the circle and both bulge outside it (by 1.4% of
    the radius on a 128 degree arc). A slightly shorter handle spreads the error
    evenly inside and outside and halves it."""
    key = round(phi, 2)
    if key in _ARC:
        return _ARC[key]
    half = key / 2
    A = (math.cos(half), math.sin(half))            # unit circle, arc centred on the x axis
    X = (1 / math.cos(half), 0.0) if abs(math.cos(half)) > 1e-9 else None
    base = math.tan(key / 4) / math.tan(key / 2)
    if X is None:
        _ARC[key] = base
        return base

    def err(kk):
        F1 = lerp(A, X, kk)
        mid = (F1[0], 0.0)
        worst = 0.0
        for i in range(0, 9):
            p = quad_pt(A, F1, mid, i / 8)
            worst = max(worst, abs(math.hypot(p[0], p[1]) - 1))
        return worst

    lo, hi = base * 0.9, base
    for _ in range(30):
        a, b = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        if err(a) < err(b):
            hi = b
        else:
            lo = a
    _ARC[key] = (lo + hi) / 2
    return _ARC[key]


# --------------------------------------------------------------------------- topology
class Structure:
    """Topology of one contour: on-curve nodes (explicit or implied) and the
    segment that leaves each node (a line, or a quadratic with one control)."""

    def __init__(self, on_flags):
        n = len(on_flags)
        seq = []
        for i in range(n):
            j = (i + 1) % n
            seq.append(("on" if on_flags[i] else "off", i))
            if not on_flags[i] and not on_flags[j]:
                seq.append(("imp", i, j))
        start = next(k for k, e in enumerate(seq) if e[0] != "off")
        seq = seq[start:] + seq[:start]
        self.nodes, self.ctrl = [], []
        k = 0
        while k < len(seq):
            self.nodes.append(seq[k])
            if k + 1 < len(seq) and seq[k + 1][0] == "off":
                self.ctrl.append(seq[k + 1][1])
                k += 2
            else:
                self.ctrl.append(None)
                k += 1
        self.count = len(self.nodes)

    def geometry(self, pts):
        P = []
        for nd in self.nodes:
            if nd[0] == "on":
                P.append(pts[nd[1]])
            else:
                a, b = pts[nd[1]], pts[nd[2]]
                P.append(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
        C = [pts[c] if c is not None else None for c in self.ctrl]
        return P, C


class Corner:
    __slots__ = ("u_in", "u_out", "turn", "convex", "tan")


def analyse(struct, P, C):
    """Tangent directions and turning angle at every node of one master."""
    out = []
    N = struct.count
    for k in range(N):
        kp, kn = (k - 1) % N, (k + 1) % N
        cin, cout = C[kp], C[k]
        d_in = sub(P[k], cin) if cin is not None else sub(P[k], P[kp])
        if cin is not None and length(d_in) < EPS:
            d_in = sub(P[k], P[kp])
        d_out = sub(cout, P[k]) if cout is not None else sub(P[kn], P[k])
        if cout is not None and length(d_out) < EPS:
            d_out = sub(P[kn], P[k])
        c = Corner()
        c.u_in, c.u_out = unit(d_in), unit(d_out)
        if c.u_in is None or c.u_out is None:
            c.turn, c.convex, c.tan = 0.0, False, 0.0
        else:
            ang = math.atan2(cross(c.u_in, c.u_out), dot(c.u_in, c.u_out))
            c.turn = min(abs(ang), MAX_TURN)
            c.convex = ang < 0          # right turn: TrueType fills to the right
            c.tan = math.tan(c.turn / 2)
        out.append(c)
    return out


class Chain:
    """The run of segments a fillet may travel along on one side of a corner."""
    __slots__ = ("k", "sign", "segs", "far", "shared", "straight", "hard", "split")

    def point(self, P, C, N, tau):
        """Point and travel-direction tangent at chain parameter tau (0 = corner)."""
        n = len(self.segs)
        idx = min(int(tau), n - 1)
        frac = min(max(tau - idx, 0.0), 1.0)
        s = self.segs[idx]
        a, b = P[s], P[(s + 1) % N]
        t = frac if self.sign > 0 else 1 - frac
        # (a piece may have no length in one master; any direction will do there)
        if C[s] is None:
            return lerp(a, b, t), unit(sub(b, a)) or (1.0, 0.0), idx, t
        tg = unit(quad_tan(a, C[s], b, t)) or unit(sub(b, a)) or (1.0, 0.0)
        return quad_pt(a, C[s], b, t), tg, idx, t

    def tau_max(self, C):
        n = len(self.segs)
        if self.shared:
            return float(n) if self.straight else 0.5
        if C[self.segs[-1]] is None:
            return float(n)
        return n - (1 - (SPLIT_REACH if self.split else CURVE_REACH))

    def closest(self, P, C, N, c):
        """(distance, tau) of the point of the chain nearest to c."""
        best = (INF, 0.0)
        top = self.tau_max(C)
        fwd = self.sign > 0
        for idx, s in enumerate(self.segs):
            a, b = P[s], P[(s + 1) % N]
            hi = min(1.0, top - idx)
            if hi <= 0:
                break
            if C[s] is None:
                ab = sub(b, a)
                den = dot(ab, ab)
                t = dot(sub(c, a), ab) / den if den > EPS else 0.0
                f = min(max(t if fwd else 1 - t, 0.0), hi)
                cand = (length(sub(lerp(a, b, f if fwd else 1 - f), c)), idx + f)
            else:
                ctl = C[s]

                def dist(f):
                    return length(sub(quad_pt(a, ctl, b, f if fwd else 1 - f), c))

                steps = 8
                i0 = min(range(steps + 1), key=lambda i: dist(hi * i / steps))
                lo_, hi_ = max(0.0, hi * (i0 - 1) / steps), min(hi, hi * (i0 + 1) / steps)
                for _ in range(18):
                    m1, m2 = lo_ + (hi_ - lo_) / 3, hi_ - (hi_ - lo_) / 3
                    if dist(m1) < dist(m2):
                        hi_ = m2
                    else:
                        lo_ = m1
                f = (lo_ + hi_) / 2
                cand = (dist(f), idx + f)
            if cand[0] < best[0]:
                best = cand
        return best


class Fillet:
    __slots__ = ("A", "F1", "F2", "S", "tanA", "tanS")


class Solution:
    """Rounded geometry of one contour in one master."""
    __slots__ = ("P", "C", "C2", "fillets", "touched", "joins")


# --------------------------------------------------------------------------- coverage tests
def flatten(struct, P, C, steps=8):
    poly = []
    N = struct.count
    for k in range(N):
        poly.append(P[k])
        if C[k] is not None:
            b = P[(k + 1) % N]
            for s in range(1, steps):
                poly.append(quad_pt(P[k], C[k], b, s / steps))
    return poly


def bbox(poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return (min(xs), min(ys), max(xs), max(ys))


def winding(pt, poly):
    x, y = pt
    w = 0
    x1, y1 = poly[-1]
    for x2, y2 in poly:
        if y1 <= y:
            if y2 > y and (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1) > 0:
                w += 1
        elif y2 <= y and (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1) < 0:
            w -= 1
        x1, y1 = x2, y2
    return w


def covered(pt, polys, boxes):
    w = 0
    for poly, b in zip(polys, boxes):
        if b[0] <= pt[0] <= b[2] and b[1] <= pt[1] <= b[3]:
            w += winding(pt, poly)
    return w != 0


# --------------------------------------------------------------------------- glyph level
class GlyphRounder:
    """Rounds one simple glyph given the outlines of all of its masters.

    masters: list (one per master) of contours; a contour is a list of (x, y).
    on_flags: list of contours; a contour is a list of bools (shared by masters).
    stems: per-master reference stem width.
    blocked: (contour, node) pairs that must stay sharp.
    """

    def __init__(self, masters, on_flags, stems, upm, factor=1.0, blocked=(), stops=(1.0,),
                 caps=True, overshoot=None, helpers=0):
        self.stems = stems
        self.eps = upm * 0.002
        self.unit = upm / 2048.0
        self.factor = factor
        self.blocked = set(blocked)
        self.M = len(masters)
        masters, on_flags, self.extra = self._merge_tiny(masters, on_flags)
        self.masters = masters
        self.helpers = helpers          # how many of the last masters are interpolated helpers
        self.on_flags = on_flags
        self.structs = [Structure(f) if len(f) >= 3 else None for f in on_flags]
        self.geo, self.cor = [], []
        for m in range(self.M):
            g, c = [], []
            for ci, st in enumerate(self.structs):
                if st is None:
                    g.append(None)
                    c.append(None)
                    continue
                P, C = st.geometry(masters[m][ci])
                g.append((P, C))
                c.append(analyse(st, P, C))
            self.geo.append(g)
            self.cor.append(c)
        self._segs, self._thk, self._needs = {}, {}, {}
        self._own, self._vis, self._discs, self._visd = {}, {}, {}, {}
        self.rounded = self._candidates()
        self._drop_hidden()
        self.chains = self._chains()
        self.overshoot = overshoot
        self.ends = self._end_pairs() if caps else {}
        self._endset = {(ci, k, far) for ci, pairs in self.ends.items() for k, far in pairs} if caps else None
        self._capfull = {}
        self._fil = {}
        self._ratios = {}
        self._cut = {}
        self._solutions = {}
        self._radii = {}
        self._tau = None
        self._joined = False
        self.stops = tuple(stops)

    # -- how thick the shape is behind an edge
    def _segments(self, m):
        if m not in self._segs:
            rows, owner = [], []
            for ci, st in enumerate(self.structs):
                if st is None:
                    continue
                poly = flatten(st, *self.geo[m][ci], steps=6)
                rows += [poly[i - 1] + poly[i] for i in range(len(poly))]
                owner += [ci] * len(poly)
            self._segs[m] = np.array(rows, dtype=float) if rows else np.zeros((0, 4))
            self._own[m] = np.array(owner, dtype=int)
        return self._segs[m]

    def _winding(self, m, pts):
        """Winding number of each point (n, 2) in master m."""
        S = self._segments(m)
        x, y = pts[:, 0][:, None], pts[:, 1][:, None]
        x1, y1, x2, y2 = S[:, 0][None, :], S[:, 1][None, :], S[:, 2][None, :], S[:, 3][None, :]
        side = (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1)
        return ((y1 <= y) & (y2 > y) & (side > 0)).sum(1) - ((y1 > y) & (y2 <= y) & (side < 0)).sum(1)

    def _outline(self, m):
        """The segments of master m that really bound the shape (not the parts
        of a contour that lie inside another one)."""
        if m not in self._vis:
            S = self._segments(m)
            if not len(S):
                self._vis[m] = S
            else:
                # long edges are cut up first: an edge may be covered for part of its length
                d = S[:, 2:4] - S[:, 0:2]
                n = np.maximum(1, np.ceil(np.hypot(d[:, 0], d[:, 1]) / 24.0)).astype(int)
                idx = np.repeat(np.arange(len(S)), n)
                step = np.concatenate([np.arange(c) for c in n]) / n[idx]
                a = S[idx, 0:2] + d[idx] * step[:, None]
                b = a + d[idx] / n[idx][:, None]
                S = np.concatenate([a, b], axis=1)
                mid = (S[:, 0:2] + S[:, 2:4]) / 2
                d = S[:, 2:4] - S[:, 0:2]
                ln = np.maximum(np.hypot(d[:, 0], d[:, 1]), 1e-9)
                nrm = np.stack([-d[:, 1] / ln, d[:, 0] / ln], axis=1)       # left of travel: outside
                self._vis[m] = S[self._winding(m, mid + nrm * 0.75) == 0]
        return self._vis[m]

    def _clearance(self, m, c):
        """Distance from point c to the nearest piece of the outline."""
        S = self._outline(m)
        if not len(S):
            return INF
        ax, ay = S[:, 0], S[:, 1]
        dx, dy = S[:, 2] - ax, S[:, 3] - ay
        den = np.maximum(dx * dx + dy * dy, 1e-12)
        t = np.clip(((c[0] - ax) * dx + (c[1] - ay) * dy) / den, 0.0, 1.0)
        return float(np.hypot(ax + t * dx - c[0], ay + t * dy - c[1]).min())

    def _disc(self, m, ci, k):
        """Radius of the largest circle that sits in corner k, touches both of its
        sides and stays inside the shape."""
        key = (m, ci, k)
        if key not in self._discs:
            P, _ = self.geo[m][ci]
            cr = self.cor[m][ci][k]
            bis = unit(sub(cr.u_out, cr.u_in))                  # towards the inside of the corner
            half = (math.pi - cr.turn) / 2
            hi = CORNER_MAX * self.stems[m] / CORNER
            if bis is None or math.sin(half) < 1e-6:
                self._discs[key] = hi
            else:
                N = self.structs[ci].count
                cin, cout = self.chains[ci][k]
                C = self.geo[m][ci][1]
                room = INF                      # how far both sides run straight from the corner
                for ch in (cin, cout):
                    sg = ch.segs[0]
                    room = min(room, length(sub(P[(sg + 1) % N], P[sg])) if C[sg] is None else 0.0)

                def flat(r):                    # the circle between the two tangents at the corner
                    return self._clearance(m, add(P[k], mul(bis, r / math.sin(half)))) >= r - 0.75

                def real(r):                    # a side curves away: sit the circle on the real outline
                    if r * cr.tan <= room:
                        return flat(r)
                    t = self._tangent(m, ci, k, r)
                    if t is None:
                        return False
                    pt, tg, _, _ = cin.point(P, C, N, t[0])
                    return self._clearance(m, (pt[0] + r * tg[1], pt[1] - r * tg[0])) >= r - 0.75

                def largest(fits, top):
                    if fits(top):
                        return top
                    lo, up = 0.0, top
                    for _ in range(10):
                        mid = (lo + up) / 2
                        if fits(mid):
                            lo = mid
                        else:
                            up = mid
                    return lo

                # Next to a curve the real circle is larger than the one between the
                # tangents (the lower lip of e); it is trusted only so far, because on
                # a blob of ink (the bowl of the pilcrow) it would grow without end.
                size = largest(flat, hi)
                if size * cr.tan > room and size < hi:
                    size = largest(real, min(hi, DISC_GAIN * size))
                self._discs[key] = size
        return self._discs[key]

    def _visible(self, m, ci, k, side):
        """How far the straight edge on one side of corner k runs before another
        contour of the glyph covers it, or None if it never does. Where a stem is
        drawn over a bowl (D, the 4, the M of the trade mark) the eye sees the
        edge end there, so the fillet has to fit in that part."""
        key = (m, ci, k, side)
        if key in self._visd:
            return self._visd[key]
        out = None
        ch = self.chains[ci][k][side]
        P, C = self.geo[m][ci]
        N = self.structs[ci].count
        s0 = ch.segs[0]
        S = self._segments(m)
        if C[s0] is None and len(S):
            a = P[k]
            b = P[(s0 + 1) % N] if ch.sign > 0 else P[s0]
            L = length(sub(b, a))
            u = unit(sub(b, a))
            if u is not None and L > 4:
                fwd = u if ch.sign > 0 else mul(u, -1)          # contour direction: ink on its right
                inn = (fwd[1], -fwd[0])
                p = add(add(a, mul(u, 1.0)), mul(inn, 1.0))     # just inside the edge, just past the corner
                other = self._own[m] != ci
                T = S[other]
                if len(T):
                    ax, ay = T[:, 0] - p[0], T[:, 1] - p[1]
                    dx, dy = T[:, 2] - T[:, 0], T[:, 3] - T[:, 1]
                    den = u[0] * dy - u[1] * dx
                    ok = np.abs(den) > 1e-9
                    safe = np.where(ok, den, 1.0)
                    t = (ax * dy - ay * dx) / safe
                    w = (ax * u[1] - ay * u[0]) / safe
                    ok &= (t > 0) & (t < L - 2.0) & (w >= 0) & (w < 1)
                    if ok.any():
                        out = float(t[ok].min()) + 1.0
        self._visd[key] = out
        return out

    def _depth(self, m, p, n):
        """How far the ink reaches from p in direction n: the first place the ray
        leaves the filled shape. Outlines hidden inside other contours (the stem of
        D lies over its bowl) are passed through."""
        S = self._segments(m)
        if not len(S):
            return None
        ax, ay = S[:, 0] - p[0], S[:, 1] - p[1]
        dx, dy = S[:, 2] - S[:, 0], S[:, 3] - S[:, 1]
        den = n[0] * dy - n[1] * dx
        ok = np.abs(den) > 1e-9
        safe = np.where(ok, den, 1.0)
        t = (ax * dy - ay * dx) / safe
        u = (ax * n[1] - ay * n[0]) / safe
        ok &= (t > 0.5) & (u >= 0) & (u < 1)
        if not ok.any():
            return None
        t, sign = t[ok], np.sign(den[ok])
        order = np.argsort(t)
        t, sign = t[order], sign[order]
        wind = np.cumsum(sign) - sign.sum()             # winding number just after each crossing
        out = np.nonzero(wind == 0)[0]
        return float(t[out[0]]) if len(out) else float(t[-1])

    def _front(self, m, ci, k, far):
        """How much room there is in front of the cut between corners k and far
        before the next outline (the bar of e above its terminal, the dot of i)."""
        P, _ = self.geo[m][ci]
        d = unit(sub(P[far], P[k]))
        S = self._segments(m)
        if d is None or not len(S):
            return INF
        p = lerp(P[k], P[far], 0.5)
        n = (-d[1], d[0])                               # out of the stroke
        ax, ay = S[:, 0] - p[0], S[:, 1] - p[1]
        dx, dy = S[:, 2] - S[:, 0], S[:, 3] - S[:, 1]
        den = n[0] * dy - n[1] * dx
        ok = np.abs(den) > 1e-9
        safe = np.where(ok, den, 1.0)
        t = (ax * dy - ay * dx) / safe
        u = (ax * n[1] - ay * n[0]) / safe
        ok &= (t > 0.5) & (u >= 0) & (u < 1)
        return float(t[ok].min()) if ok.any() else INF

    def _thick(self, m, ci, k, side):
        """Thickness of the stroke whose edge is the given side of corner k: the
        least depth of ink behind a handful of points along that side."""
        key = (m, ci, k, side)
        if key in self._thk:
            return self._thk[key]
        ch = self.chains[ci][k][side]
        P, C = self.geo[m][ci]
        N = self.structs[ci].count
        top = float(len(ch.segs)) if (ch.shared and ch.straight) else ch.tau_max(C)
        got = []
        for f in SAMPLES:
            pt, tg, _, _ = ch.point(P, C, N, top * f)
            d = self._depth(m, pt, (tg[1], -tg[0]))
            if d is not None:
                got.append(d)
        # the middle value: near a corner the ray leaves through the end of the
        # stroke (too short) or runs on into the next stroke (too long)
        lim = THICK_MAX * self.stems[m]
        best = lim if not got else min(sorted(got)[len(got) // 2], lim)
        self._thk[key] = best
        return best

    def _stroke(self, m, ci, k, far):
        """Local stroke width at the end between corners k and far: the mean
        thickness behind its two sides."""
        return 0.5 * (self._thick(m, ci, k, 0) + self._thick(m, ci, far, 1))

    # -- corners drawn with two points
    def _merge_tiny(self, masters, on_flags):
        """The tip of a circumflex or caron is cut off by an edge one unit long: two
        points, two blunt corners, where the eye sees one sharp corner. The solver
        works on the corner where the two long sides meet; the second point is kept
        aside and put back when the outline is written (extra[contour][point] =
        the original positions of both points in every master), so the sharp
        outline still is the source outline, point for point."""
        out_m = [[] for _ in range(self.M)]
        out_f, extra = [], []
        for ci, flags in enumerate(on_flags):
            n = len(flags)
            drop, moved = set(), {}
            if n >= 5:
                for i in range(n):
                    j, h, q = (i + 1) % n, (i - 1) % n, (i + 2) % n
                    if not (flags[i] and flags[j]) or i in drop or h in drop or j in moved or q in moved:
                        continue
                    xs = []
                    for m in range(self.M):
                        c = masters[m][ci]
                        a, b = c[i], c[j]
                        if length(sub(b, a)) > TINY:
                            break
                        u1, u2, ue = unit(sub(a, c[h])), unit(sub(c[q], b)), unit(sub(b, a))
                        if u1 is None or u2 is None:
                            break
                        if ue is not None and (cross(u1, ue) > -1e-6 or cross(ue, u2) > -1e-6):
                            break                           # not two right turns: a step, not a tip
                        if cross(u1, u2) > -math.sin(MIN_TURN):
                            break
                        x = line_intersection(a, u1, b, u2)
                        if x is None or length(sub(x, a)) > 2 * TINY or length(sub(x, b)) > 2 * TINY:
                            break
                        xs.append(x)
                    else:
                        drop.add(j)
                        moved[i] = xs
            keep = [i for i in range(n) if i not in drop]
            index = {i: r for r, i in enumerate(keep)}
            out_f.append([flags[i] for i in keep])
            for m in range(self.M):
                c = masters[m][ci]
                out_m[m].append([moved[i][m] if i in moved else c[i] for i in keep])
            extra.append({index[i]: ([masters[m][ci][i] for m in range(self.M)],
                                     [masters[m][ci][(i + 1) % n] for m in range(self.M)]) for i in moved})
        return out_m, out_f, extra

    # -- which corners can be rounded at all
    def _candidates(self):
        out = []
        for ci, st in enumerate(self.structs):
            if st is None:
                out.append(None)
                continue
            flags = []
            for k in range(st.count):
                ok = st.nodes[k][0] == "on" and (ci, k) not in self.blocked
                if ok:
                    # A corner in most masters is rounded; in a master where it is
                    # smooth or turns the other way (the crotch corner of the small 5
                    # at light weights) its fillet simply stays closed.
                    ok = sum(self._live(m, ci, k) for m in range(self.M)) * 2 > self.M
                flags.append(ok)
            out.append(flags)
        return out

    def _live(self, m, ci, k):
        """Is node k a corner worth rounding in master m?"""
        cr = self.cor[m][ci][k]
        return cr.convex and cr.turn >= MIN_TURN

    def near_probes(self, m, ci, k):
        """Points just outside the fill: at the corner and a little way along each side."""
        st = self.structs[ci]
        P, C = self.geo[m][ci]
        N = st.count
        cr = self.cor[m][ci][k]
        e = self.eps
        bis = unit(sub(cr.u_in, cr.u_out))
        if bis is None:
            return []
        out = [add(P[k], mul(bis, e))]
        kp, kn = (k - 1) % N, (k + 1) % N
        step_in = min(3 * e, 0.5 * length(sub(P[k], P[kp])))
        step_out = min(3 * e, 0.5 * length(sub(P[kn], P[k])))
        out.append(add(sub(P[k], mul(cr.u_in, step_in)), mul(left(cr.u_in), e)))
        out.append(add(add(P[k], mul(cr.u_out, step_out)), mul(left(cr.u_out), e)))
        return out

    def far_probes(self, m, ci, k):
        """Points just outside the two ends of the fillet that replaces corner k."""
        f = self.solution(m, ci).fillets[k]
        e = self.eps
        return [add(f.A, mul(left(f.tanA), e)), add(f.S, mul(left(f.tanS), e))]

    # -- drop corners that are buried in, or butt against, other outline parts
    def _drop_hidden(self):
        """A corner that is buried or butts against another part in at least half
        of the masters where it is a corner stays sharp. (In one or two heavy
        masters a terminal may all but touch its neighbour; that is not a join.)"""
        hits, seen = {}, {}
        for m in range(self.M):
            polys = [flatten(st, *self.geo[m][ci]) for ci, st in enumerate(self.structs) if st is not None]
            boxes = [bbox(p) for p in polys]
            for ci, st in enumerate(self.structs):
                if st is None:
                    continue
                for k in range(st.count):
                    if self.rounded[ci][k] and self._live(m, ci, k):
                        seen[(ci, k)] = seen.get((ci, k), 0) + 1
                        if any(covered(p, polys, boxes) for p in self.near_probes(m, ci, k)):
                            hits[(ci, k)] = hits.get((ci, k), 0) + 1
        for (ci, k), n in hits.items():
            if n * 2 >= seen[(ci, k)]:
                self.rounded[ci][k] = False

    # -- where a fillet may run on each side of a corner
    def _smooth(self, ci, k):
        st = self.structs[ci]
        if st.nodes[k][0] == "imp":
            return True
        # In a light master two points of a tight spot may swap places (the flag of
        # the alternate 1, the tail of the small y): the outline doubles back on
        # itself there. Such a node is still smooth if it is in most masters. A
        # real kink in any master, however slight, is not.
        # The helper masters at mid weight are interpolations. Where two points
        # sit a few units apart in the light master, interpolation alone can bend
        # the outline there by a few degrees more than any drawn master does
        # (8.5 degrees on the italic s, against 4.7 as drawn, which left its upper
        # terminal flat). So a helper master is given a little more room.
        turns = [self.cor[m][ci][k].turn for m in range(self.M)]
        drawn = self.M - self.helpers
        if any(SMOOTH_TURN <= t < REVERSAL for t in turns[:drawn]):
            return False
        if any(HELPER_TURN <= t < REVERSAL for t in turns[drawn:]):
            return False
        return sum(t < SMOOTH_TURN for t in turns) * 2 > self.M

    def _chains(self):
        out = []
        for ci, st in enumerate(self.structs):
            if st is None:
                out.append(None)
                continue
            N, rnd = st.count, self.rounded[ci]
            per = [None] * N
            for k in range(N):
                if not rnd[k]:
                    continue
                # the longest tangent a fillet at this corner could ask for
                need = [1.5 * self.stems[m] * max(1.0, self.cor[m][ci][k].tan) for m in range(self.M)]
                pair = []
                for sign in (-1, 1):
                    ch = Chain()
                    ch.k, ch.sign, ch.segs, ch.shared, ch.hard, ch.split = k, sign, [], False, False, False
                    i = k if sign > 0 else k - 1
                    meets = False
                    for _ in range(N):
                        s = i % N
                        ch.segs.append(s)
                        far = (s + 1) % N if sign > 0 else s
                        if far == k or rnd[far]:
                            meets = True
                            break
                        if not self._smooth(ci, far):
                            ch.hard = True
                            break
                        i += sign
                        if st.ctrl[s] is None and st.ctrl[i % N] is not None:
                            # a straight run flows into a curve: only follow it if the
                            # straight part alone could be too short for the fillet
                            if all(length(sub(self.geo[m][ci][0][far], self.geo[m][ci][0][k])) >= need[m]
                                   for m in range(self.M)):
                                break
                    ch.straight = all(st.ctrl[s] is None for s in ch.segs)
                    if meets and (ch.straight or len(ch.segs) == 1) and far != k:
                        ch.shared = True
                    elif meets:
                        # two corners joined by a run with curves in it: each keeps its part
                        ch.segs = ch.segs[:self._share(ci, k, far, ch.segs, sign, need)]
                        ch.straight = all(st.ctrl[s] is None for s in ch.segs)
                        ch.split = True
                    if not ch.shared:
                        if len(ch.segs) > MAX_CHAIN:
                            ch.hard = False
                        ch.segs = ch.segs[:MAX_CHAIN]
                        ch.straight = all(st.ctrl[s] is None for s in ch.segs)
                    last = ch.segs[-1]
                    ch.far = (last + 1) % N if sign > 0 else last
                    pair.append(ch)
                per[k] = pair
            out.append(per)
        return out

    def _share(self, ci, k, other, segs, sign, need):
        """A run of segments with curves in it joins corner k to another rounded
        corner. How many of its segments, counted from k, belong to k: the run is
        cut at the node that leaves both corners the largest share of the length
        their fillets could ask for. (Cutting it in the middle by count starved
        the short side of a hook or tail that runs into a long stem.)"""
        n = len(segs)
        if n < 2:
            return 1
        N = self.structs[ci].count
        order = segs if sign > 0 else segs[::-1]            # contour order, so that both ends agree
        first, last = (k, other) if sign > 0 else (other, k)
        best, cut = -1.0, n // 2
        for j in range(1, n):
            score = INF
            for m in range(self.M):
                P = self.geo[m][ci][0]
                lens = [length(sub(P[(q + 1) % N], P[q])) for q in order]
                a, b = sum(lens[:j]), sum(lens[j:])
                want = [1.5 * self.stems[m] * max(1.0, self.cor[m][ci][c].tan) for c in (first, last)]
                score = min(score, a / want[0], b / want[1])
            score = min(score, 1.0)
            if score > best + 1e-9 or (abs(score - best) <= 1e-9 and abs(j - n / 2) < abs(cut - n / 2)):
                best, cut = score, j
        return cut if sign > 0 else n - cut

    def _terminal_width(self, m, ci, k, far):
        """Diameter of the circle inscribed in the stroke end between two corners, or None."""
        P, _ = self.geo[m][ci]
        a, b = self.cor[m][ci][k], self.cor[m][ci][far]
        if not (self._live(m, ci, k) and self._live(m, ci, far)):
            return None
        if min(a.turn, b.turn) < END_TURN or max(a.turn, b.turn) < TERMINAL_TURN:
            return None
        w = 2 * length(sub(P[far], P[k])) / (a.tan + b.tan)
        return w if w <= TERMINAL_WIDTH * self._stroke(m, ci, k, far) else None

    def _estimate(self, m, ci):
        """First guess of every radius, treating the sides as straight lines."""
        st = self.structs[ci]
        P, C = self.geo[m][ci]
        N, cor, rnd = st.count, self.cor[m][ci], self.rounded[ci]
        r = [INF if rnd[k] else 0.0 for k in range(N)]
        term = [False] * N
        for k in range(N):
            if not rnd[k] or not self._live(m, ci, k):
                continue
            for ch in self.chains[ci][k]:
                if ch.shared and ch.straight:
                    lim = length(sub(P[ch.far], P[k])) / (cor[k].tan + cor[ch.far].tan)
                    if self._capped(m, ci, *((k, ch.far) if ch.sign > 0 else (ch.far, k))):
                        term[k] = True
                else:
                    reach = length(sub(ch.point(P, C, N, ch.tau_max(C))[0], P[k]))
                    lim = reach / cor[k].tan
                r[k] = min(r[k], lim)
        for k in range(N):
            if rnd[k] and not self._live(m, ci, k):
                r[k] = 0.0
            elif rnd[k] and not term[k]:
                r[k] = min(r[k], self._corner(m, ci, k))
        return r, term

    def _capped(self, m, ci, k, far):
        """Do corners k and far carry one round cap in master m?"""
        if self._endset is None:
            return bool(self._terminal_width(m, ci, k, far))
        return (ci, k, far) in self._endset and self.cap(m, ci, k, far) is not None

    def _corner(self, m, ci, k):
        """Radius of an outer corner that is not part of a stroke end: a little
        less than the largest circle that fits in the corner, and no more than
        fits on the part of each edge that is not covered by another contour."""
        r = CORNER * self._disc(m, ci, k)
        tan = self.cor[m][ci][k].tan
        for side in (0, 1):
            v = self._visible(m, ci, k, side)
            if v is not None and tan > EPS:
                r = min(r, VISIBLE * v / tan)
        return r

    def _tangent(self, m, ci, k, r):
        """Chain parameters (tau_in, tau_out) where the circle of radius r that
        sits in corner k touches its two sides, or None if it does not fit."""
        st = self.structs[ci]
        P, C = self.geo[m][ci]
        N, cr = st.count, self.cor[m][ci][k]
        cin, cout = self.chains[ci][k]
        if r <= 0:
            return (0.0, 0.0)
        d = r * cr.tan
        if C[cin.segs[0]] is None and C[cout.segs[0]] is None:
            l_in = length(sub(P[k], P[cin.segs[0]]))
            l_out = length(sub(P[(cout.segs[0] + 1) % N], P[k]))
            if d <= l_in + 1e-6 and d <= l_out + 1e-6:
                return (min(d / l_in, 1.0), min(d / l_out, 1.0))
        top_in, top_out = cin.tau_max(C), cout.tau_max(C)

        def gap(tau):
            pt, tg, _, _ = cin.point(P, C, N, tau)
            c = (pt[0] + r * tg[1], pt[1] - r * tg[0])      # centre: r towards the fill
            dist, tb = cout.closest(P, C, N, c)
            return dist - r, tb

        g, tb = gap(top_in)
        if g < 0:
            return None
        lo, hi = 0.0, top_in
        for _ in range(26):
            mid = (lo + hi) / 2
            g, tb_mid = gap(mid)
            if g < 0:
                lo = mid
            else:
                hi, tb = mid, tb_mid
        if tb >= top_out - 1e-4 and not (cout.shared and cout.straight):
            return None
        return (hi, tb)

    # -- stroke ends: one circle between the two sides
    def _end_pairs(self):
        """Stroke ends per contour: (first corner, second corner) joined by a straight
        cut. A corner that belongs to two ends (a square dot) is left to the corner
        rule, which already turns it into a circle."""
        out = {}
        for ci, st in enumerate(self.structs):
            if st is None:
                continue
            cand = []
            for k in range(st.count):
                if not self.rounded[ci][k]:
                    continue
                ch = self.chains[ci][k][1]
                if ch.shared and ch.straight and ch.far != k and self.rounded[ci][ch.far]:
                    if any(self._terminal_width(m, ci, k, ch.far) for m in range(self.M)):
                        cand.append((k, ch.far))
            # A corner can sit between two candidate ends: the end of the arm of a
            # bracket and the edge that runs on to the next corner. The narrower one
            # is the stroke end; the other is an edge between two plain corners. Where
            # the two are about equally wide (a square dot) neither is an end and the
            # corner rule, which turns a square into a circle, is left to work.
            def width(pair):
                return max(self._terminal_width(m, ci, *pair) or 0.0 for m in range(self.M))

            def rank(pair):                 # how end-like: width in local strokes, then plain width
                P = [self.geo[m][ci][0] for m in range(self.M)]
                rel = [2 * length(sub(P[m][pair[1]], P[m][pair[0]]))
                       / max(self.cor[m][ci][pair[0]].tan + self.cor[m][ci][pair[1]].tan, 1e-6)
                       / max(self._stroke(m, ci, *pair), 1.0) for m in range(self.M)]
                return (round(sum(rel) / len(rel), 2), width(pair))

            taken, picked = {}, []
            for pair in sorted(cand, key=rank):
                w = width(pair)
                clash = [taken[q] for q in pair if q in taken]
                if clash:
                    for other in clash:
                        if w < SQUARE * width(other) and other in picked:
                            picked.remove(other)
                    continue
                picked.append(pair)
                for q in pair:
                    taken[q] = pair
            out[ci] = picked
        return out

    def _need(self, m, ci, k):
        """Roughly how much of a side the fillet at corner k asks for."""
        key = (m, ci, k)
        if key not in self._needs:
            P, _ = self.geo[m][ci]
            cr = self.cor[m][ci][k]
            r = None
            for a, b in self.ends.get(ci, ()):
                if k in (a, b):
                    r = length(sub(P[b], P[a])) / max(self.cor[m][ci][a].tan + self.cor[m][ci][b].tan, 1e-6)
            if r is None:
                r = self._corner(m, ci, k)
            self._needs[key] = max(r * cr.tan, 1.0)
        return self._needs[key]

    def _side_top(self, m, ci, ch):
        """How far along its side a cap may reach. A straight side shared with
        another corner is divided in proportion to what the two ask for (halving
        it starved the wide end of a wedge: acute, comma accent, caron)."""
        if ch.shared and ch.straight:
            a, b = self._need(m, ci, ch.k), self._need(m, ci, ch.far)
            return len(ch.segs) * a / (a + b)
        return ch.tau_max(self.geo[m][ci][1])

    def _fit(self, m, ci, ch, r, M, nu, top):
        """Where the circle of radius r that touches the side chain also touches the
        line through M whose inward normal is nu. Returns (tau, centre, touch point
        on the line, tangent at the side end or None), or None if the side is too
        short for it.

        A side that ends in a crotch (the stem of p under its bowl, the foot of a)
        may be shorter than the cap is deep. If the circle would touch it only a
        little way past the crotch, the side is carried on straight (_extend) and
        the cap stays a full circle; further than that, the circle starts at the
        crotch itself (_pin). Either way nothing is flattened or pushed out."""
        P, C = self.geo[m][ci]
        N = self.structs[ci].count

        def h(tau):
            pt, tg, _, _ = ch.point(P, C, N, tau)
            c = (pt[0] + r * tg[1], pt[1] - r * tg[0])
            return dot(sub(c, M), nu) - r, c

        stop = float(len(ch.segs)) if (ch.hard and not ch.shared) else None
        if stop is not None:                        # a side that ends in a crotch counts to its very end
            top = max(top, stop)
        h0, c0 = h(0.0)
        if h0 >= 0:                                 # the line lies beyond the end of the side
            return (0.0, c0, sub(c0, mul(nu, dot(sub(c0, M), nu))), None)
        # the first place along the side where the circle clears the line; a long
        # side may wander anywhere further on, so walk it instead of testing its end
        lo, hi, c = 0.0, None, None
        steps = max(2, int(math.ceil(top * 6)))
        for i in range(1, steps + 1):
            t = top * i / steps
            ht, ct = h(t)
            if ht >= 0:
                hi, c = t, ct
                break
            lo = t
        if hi is None:
            if stop is None:
                return None
            return (self._extend(m, ci, ch, r, M, nu, stop, EXTEND) or self._pin(m, ci, ch, r, M, nu)
                    or self._extend(m, ci, ch, r, M, nu, stop, EXTEND_FAR))
        for _ in range(24):
            mid = (lo + hi) / 2
            hm, cm = h(mid)
            if hm < 0:
                lo = mid
            else:
                hi, c = mid, cm
        return (hi, c, sub(c, mul(nu, r)), None)

    def _extend(self, m, ci, ch, r, M, nu, tau, reach):
        """A side that stops before the circle touches it (the stem of p under its
        bowl, the foot of a, the tail of l) is carried on straight, as the stroke
        itself would run on under the part that joins it. The circle touches that
        line inside the joining part, and the outline runs back along the line to
        where the side stopped: a full, even cap, and the crotch a little deeper."""
        P, C = self.geo[m][ci]
        N = self.structs[ci].count
        Z, tg, _, _ = ch.point(P, C, N, tau)
        e = tg if ch.sign > 0 else mul(tg, -1)          # travel direction, away from the corner
        c0 = (Z[0] + r * tg[1], Z[1] - r * tg[0])
        h0 = dot(sub(c0, M), nu) - r
        rate = dot(e, nu)
        if h0 >= 0:
            return (tau, c0, sub(c0, mul(nu, r)), (Z, tg))
        if rate < 0.05:
            return None
        dist = -h0 / rate
        if dist > reach * r:
            return None
        T = add(Z, mul(e, dist))
        if int(self._winding(m, np.array([add(T, mul(e, 1.5))]))[0]) == 0:
            return None                                 # nothing there to run under
        c = add(c0, mul(e, dist))
        return (tau, c, sub(c, mul(nu, r)), (T, tg))

    def _return(self, sol, st, P, C, ch, tau, T):
        """The side was carried on to T, past where it stops (chain parameter
        tau): the points of the side between the corner and there lie on the
        straight way back from T."""
        N = st.count
        fwd = ch.sign > 0
        j = int(round(tau))
        if j <= 0:
            return
        Z = ch.point(P, C, N, float(j))[0]
        for i in range(j):
            sg = ch.segs[i]
            lo = i / j
            if sg in sol.C2:
                near, far = lerp(T, Z, lo + 0.25 / j), lerp(T, Z, lo + 0.75 / j)
                sol.C2[sg] = (near, far) if fwd else (far, near)
            elif C[sg] is not None:
                sol.C[sg] = lerp(T, Z, lo + 0.5 / j)
            if i < j - 1:
                sol.P[(sg + 1) % N if fwd else sg] = lerp(T, Z, (i + 1) / j)

    def _pin(self, m, ci, ch, r, M, nu):
        """The circle of radius r that touches the line and starts at the hard end of
        the side, provided it leaves the side there by less than 30 degrees."""
        if not ch.hard or ch.shared:
            return None
        P, C = self.geo[m][ci]
        N = self.structs[ci].count
        n = float(len(ch.segs))
        Z, tg, _, _ = ch.point(P, C, N, n)
        d = (-nu[1], nu[0])                         # along the cut, in contour direction
        zn = dot(sub(Z, M), nu)
        if zn <= 0 or zn >= r:
            return None
        dx = math.sqrt(zn * (2 * r - zn))
        c = add(add(M, mul(nu, r)), mul(d, dot(sub(Z, M), d) - ch.sign * dx))
        v = sub(Z, c)
        tan = unit((v[1], -v[0]))
        if tan is None or dot(tan, tg) < PIN_COS:
            return None
        return (n, c, sub(c, mul(nu, r)), (Z, tan))

    def _cap_best(self, m, ci, k, far, s, r_hi):
        """Largest radius, up to r_hi, at which a fillet fits on each side of the end
        with the cut moved out by s, the two not overlapping. Returns
        (radius, gap left between the two on the cut, fit on side a, fit on side b)."""
        P, C = self.geo[m][ci]
        d = unit(sub(P[far], P[k]))
        nu = (d[1], -d[0])
        M = sub(P[k], mul(nu, s))
        sa, sb = self.chains[ci][k][0], self.chains[ci][far][1]
        ta, tb = self._side_top(m, ci, sa), self._side_top(m, ci, sb)

        def at(r):
            fa = self._fit(m, ci, sa, r, M, nu, ta)
            fb = self._fit(m, ci, sb, r, M, nu, tb) if fa else None
            if not fb:
                return None
            return (r, dot(sub(fb[2], fa[2]), d), fa, fb)

        res = at(r_hi)
        if res and res[1] >= 0:
            return res
        lo, hi, res = 0.0, r_hi, None
        for _ in range(26):
            mid = (lo + hi) / 2
            got = at(mid)
            if got is None or got[1] < 0:
                hi = mid
            else:
                lo, res = mid, got
        return res

    def cap(self, m, ci, k, far):
        """The fully round end between corners k and far in master m: (push, radius,
        gap), or None where this is not a stroke end in this master. The cap is the
        circle that touches both sides of the stroke and the cut; the cut is moved
        out by the overshoot, and further only as far as it takes for the whole
        circle to fit where a side is short."""
        key = (m, ci, k)
        if key in self._capfull:
            return self._capfull[key]
        out = None
        if self._terminal_width(m, ci, k, far):
            P, _ = self.geo[m][ci]
            a, b = self.cor[m][ci][k], self.cor[m][ci][far]
            est = length(sub(P[far], P[k])) / (a.tan + b.tan)
            # The cut is moved out by a share of the cap's radius, and no further than
            # the round letters of the font pass the baseline. Where something sits
            # right in front of the cut (the bar of a small e, the dot of i) it stays.
            ov = self.overshoot[m] if self.overshoot else 0.0
            if ov and self._front(m, ci, k, far) < FRONT * self.unit:
                ov = 0.0
            s = min(OV_SHARE * est, ov)
            got = self._cap_best(m, ci, k, far, s, 2 * est)
            for _ in range(2):
                if not got or not ov:
                    break
                again = min(OV_SHARE * got[0], ov)
                if abs(again - s) < 0.25:
                    break
                s = again
                got = self._cap_best(m, ci, k, far, s, 2 * est)
            # an end that cannot be one circle (the stub of a caron) is left to the corner rule
            if got and got[0] > 0 and got[1] <= ROUND_TOL:
                if int(self._winding(m, np.array([got[2][1]]))[0]) != 0:
                    out = (s, got[0], got[1])
        self._capfull[key] = out
        return out

    def _cap_taus(self, m, ci, g, taus):
        """Replace what the corner rule gave the corners of every stroke end by the
        cap at share g of full roundness: the cut moved out by g of the push,
        fillets of g times the cap radius."""
        cut = {}
        st = self.structs[ci]
        P, C = self.geo[m][ci]
        for k, far in self.ends.get(ci, ()):
            full = self.cap(m, ci, k, far)
            if full is None:
                continue
            s, r, _ = full
            got = self._cap_best(m, ci, k, far, s * g, r * g)
            if got is None:
                continue
            _, _, fa, fb = got
            d = unit(sub(P[far], P[k]))
            n = len(self.chains[ci][k][1].segs)
            L = length(sub(P[far], P[k]))
            ca = min(max(dot(sub(fa[2], P[k]), d) / L, 0.0), 1.0) * n
            cb = min(max(dot(sub(P[far], fb[2]), d) / L, 0.0), 1.0) * n
            if ca + cb > n:
                ca, cb = ca * n / (ca + cb), cb * n / (ca + cb)
            taus[k] = (fa[0], ca)
            taus[far] = (cb, fb[0])
            cut[k] = (fa[2], d, 1, fa[3])
            cut[far] = (fb[2], d, 0, fb[3])
        return cut

    def _uncross(self, ci, taus):
        """Two fillets on one straight edge must not cross."""
        st = self.structs[ci]
        for k in range(st.count):
            if self.rounded[ci][k]:
                ch = self.chains[ci][k][1]
                if ch.shared and ch.straight:
                    n = len(ch.segs)
                    a, b = taus[k][1], taus[ch.far][0]
                    if a + b > n:
                        f = n / (a + b)
                        taus[k] = (taus[k][0], a * f)
                        taus[ch.far] = (b * f, taus[ch.far][1])

    def radii(self, m, ci):
        """Full-roundness radius of every corner of one contour in one master."""
        key = (m, ci)
        if key in self._radii:
            return self._radii[key]
        st = self.structs[ci]
        P, C = self.geo[m][ci]
        N, rnd = st.count, self.rounded[ci]
        r, term = self._estimate(m, ci)
        cache = {}

        def tangent(k):
            q = (k, round(r[k], 3))
            if q not in cache:
                cache[q] = self._tangent(m, ci, k, r[k])
            return cache[q]

        def chord(ch, tau):
            return length(sub(ch.point(P, C, N, tau)[0], P[ch.k]))

        locked = [False] * N
        for _ in range(6):
            changed = False
            for k in range(N):
                if not rnd[k]:
                    continue
                ch = self.chains[ci][k][1]
                if not (ch.shared and ch.straight):
                    continue
                far = ch.far
                ta, tb = tangent(k), tangent(far)
                if ta is None or tb is None:
                    for q, t in ((k, ta), (far, tb)):
                        if t is None:
                            r[q] *= 0.85
                            locked[q] = True
                    if term[k] and term[far]:
                        r[k] = r[far] = min(r[k], r[far])
                    changed = True
                    continue
                L = length(sub(P[far], P[k]))
                used = chord(ch, ta[1]) + chord(self.chains[ci][far][0], tb[0])
                is_end = term[k] and term[far] and self._capped(m, ci, k, far)
                if used > L + 0.2 or (is_end and used < L - 0.2 and not (locked[k] or locked[far])):
                    f = L / used
                    r[k] *= f
                    r[far] *= f
                    changed = True
            if not changed:
                break
        for k in range(N):
            if rnd[k]:
                for _ in range(24):
                    if tangent(k) is not None:
                        break
                    r[k] *= 0.85
                else:
                    r[k] = 0.0
        self._radii[key] = r
        return r

    def _taus(self, m, ci, r):
        st = self.structs[ci]
        N, rnd = st.count, self.rounded[ci]
        taus = [None] * N
        for k in range(N):
            if not rnd[k]:
                continue
            rk, t = r[k], None
            for _ in range(24):
                t = self._tangent(m, ci, k, rk)
                if t is not None:
                    break
                rk *= 0.85
            taus[k] = t or (0.0, 0.0)
        self._uncross(ci, taus)
        return taus

    # -- shared structure
    def _plan(self):
        """Solve every master at every roundness stop, then decide the point
        structure all of them share.

        A fillet that lands on a curve is followed by a short run of quadratics
        whose joints are all implied on-curve points. Implied joints are smooth
        under any interpolation, so the join between cap and stroke cannot kink
        at in-between weights or in-between roundness. To have enough control
        points for that, every curve segment the fillet may travel over is
        stored as two half-segments (an exact split, invisible when sharp)."""
        if self._tau is not None:
            return
        self._tau = {}
        reach = {}
        for ci, st in enumerate(self.structs):
            if st is None:
                continue
            N, rnd = st.count, self.rounded[ci]
            for m in range(self.M):
                P, C = self.geo[m][ci]
                base = self.radii(m, ci)
                for f in self.stops:
                    taus = self._taus(m, ci, [x * f * self.factor for x in base])
                    self._cut[(m, ci, f)] = self._cap_taus(m, ci, f * self.factor, taus)
                    self._uncross(ci, taus)
                    self._tau[(m, ci, f)] = taus
                    for k in range(N):
                        if rnd[k]:
                            for side, ch in enumerate(self.chains[ci][k]):
                                if not ch.straight and not ch.shared:
                                    j = ch.point(P, C, N, taus[k][side])[2]
                                    q = (ci, k, side)
                                    reach[q] = max(reach.get(q, 0), j)
        self.reach = reach
        self.split = [set() for _ in self.structs]
        self.pinned = [set() for _ in self.structs]
        for (ci, k, side), J in reach.items():
            ch = self.chains[ci][k][side]
            N = self.structs[ci].count
            self.split[ci].update(ch.segs[:J + 1])
            last = ch.segs[J]
            self.pinned[ci].add((last + 1) % N if ch.sign > 0 else last)

    @staticmethod
    def _ctl(P, C, N, s):
        """Control point of segment s; a line counts as a curve bent by nothing."""
        return C[s] if C[s] is not None else lerp(P[s], P[(s + 1) % N], 0.5)

    @classmethod
    def _halves(cls, P, C, N, s):
        """The two controls of segment s cut at its middle, in contour order."""
        c = cls._ctl(P, C, N, s)
        return lerp(P[s], c, 0.5), lerp(c, P[(s + 1) % N], 0.5)

    @staticmethod
    def _ruler(P, C, N, ch, t0, t1, per=10):
        """A function from a share (0..1) of the length of the chain between
        parameters t0 and t1 to the chain parameter there."""
        if t1 - t0 < 1e-9:
            return lambda share: t1
        n = max(2, int(math.ceil((t1 - t0) * per)))
        ts = [t0 + (t1 - t0) * i / n for i in range(n + 1)]
        pts = [ch.point(P, C, N, t)[0] for t in ts]
        cum = [0.0]
        for a, b in zip(pts, pts[1:]):
            cum.append(cum[-1] + length(sub(b, a)))
        total = cum[-1]
        if total < 1e-9:
            return lambda share: t0 + (t1 - t0) * share

        def at(share):
            want = min(max(share, 0.0), 1.0) * total
            lo, hi = 0, n
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if cum[mid] <= want:
                    lo = mid
                else:
                    hi = mid
            span = cum[hi] - cum[lo]
            f = (want - cum[lo]) / span if span > 1e-12 else 0.0
            return ts[lo] + (ts[hi] - ts[lo]) * f
        return at

    def _refit(self, sol, st, P, C, ch, J, tau, handle=None):
        """Lay the chain's control points along the original curve from the
        fillet end to the pinned node, evenly in chain parameter so the layout
        changes smoothly from master to master."""
        N = st.count
        fwd = ch.sign > 0
        top = J + 1.0
        nq = 2 * (J + 1)
        # Spread the control points evenly, in chain parameter, over what is left
        # of the run. Measured against the alternatives (keeping far points fixed
        # and crowding the rest near the fillet) this keeps the outline closest
        # to the source between masters.
        # ... evenly by length. A run counts its segments, and a segment may be a
        # few units long in a light master and thirty in a heavy one (the end of the
        # italic s): spread by count, the points then sit in quite different places
        # from master to master and the weights in between come out bent.
        ruler = self._ruler(P, C, N, ch, tau, top)
        knots = [ruler(i / nq) for i in range(nq + 1)]
        if handle and nq > 1 and top - tau > 1e-6:
            # The join between fillet and stroke is drawn midway between its two
            # handles (see _smooth_joins). That only leaves it where the circle
            # touches the stroke if the two handles are equally long; a short
            # handle on the stroke side drags the join out along the tangent and
            # the cap grows a shoulder there. So the first piece of the stroke is
            # made as long as it takes for its handle to match the fillet's.
            def reach(k1):
                return self._handle(P, C, N, ch, tau, k1)

            lo, hi = tau, tau + (top - tau) * JOIN_SHARE
            if reach(hi) > handle:
                for _ in range(22):
                    mid = (lo + hi) / 2
                    if reach(mid) < handle:
                        lo = mid
                    else:
                        hi = mid
            k1 = hi
            rest = self._ruler(P, C, N, ch, k1, top)
            knots = [tau, k1] + [rest(i / (nq - 1)) for i in range(1, nq)]
        away = []
        for i in range(nq):
            k0, k1 = knots[i], knots[i + 1]
            idx = min(int(k0 + 1e-9), J)
            if k1 <= idx + 1 + 1e-9:                    # both ends on one segment: exact
                s = ch.segs[idx]
                f0, f1 = k0 - idx, min(k1 - idx, 1.0)
                t0, t1 = (f0, f1) if fwd else (1 - f1, 1 - f0)
                away.append(quad_blossom(P[s], self._ctl(P, C, N, s), P[(s + 1) % N], t0, t1))
                continue
            pa, ta, _, _ = ch.point(P, C, N, k0)
            pb, tb, _, _ = ch.point(P, C, N, k1)
            if not fwd:
                ta, tb = mul(ta, -1), mul(tb, -1)
            X = line_intersection(pa, ta, pb, tb)
            span = length(sub(pb, pa))
            if X is None or dot(sub(X, pa), ta) <= 0 or dot(sub(pb, X), tb) <= 0 or length(sub(X, pa)) > 2 * span:
                X = lerp(pa, pb, 0.5)
            away.append(X)
        for i in range(J + 1):
            near, far = away[2 * i], away[2 * i + 1]
            sol.C2[ch.segs[i]] = (near, far) if fwd else (far, near)
        # explicit smooth nodes inside the run keep the proportions they have when sharp
        for i in range(J):
            s, s2 = ch.segs[i], ch.segs[i + 1]
            node = (s + 1) % N if fwd else s
            if st.nodes[node][0] != "on":
                continue
            h1, h2 = self._halves(P, C, N, s), self._halves(P, C, N, s2)
            before, after = (h1[1], h2[0]) if fwd else (h1[0], h2[1])
            span = length(sub(after, before))
            lam = length(sub(P[node], before)) / span if span > EPS else 0.5
            sol.P[node] = lerp(away[2 * i + 1], away[2 * i + 2], lam)

    def curved(self):
        """True if any fillet of this glyph lands on a curve."""
        for ci, st in enumerate(self.structs):
            if st is None:
                continue
            for k in range(st.count):
                if self.rounded[ci][k] and not all(ch.straight for ch in self.chains[ci][k]):
                    return True
        return False

    def _slide(self, sol, P, C, N, ch, tau):
        """A fillet on a straight run has passed j nodes: spread them over what
        is left of the run."""
        _, _, j, t = ch.point(P, C, N, tau)
        fwd = ch.sign > 0
        frac = t if fwd else 1 - t
        sj = ch.segs[j]
        a, b = P[sj], P[(sj + 1) % N]
        for i in range(j):
            v = frac + (1 - frac) * (i + 1) / (j + 1)
            s = ch.segs[i]
            sol.P[(s + 1) % N if fwd else s] = lerp(a, b, v if fwd else 1 - v)

    def _fillets(self, m, ci, scale):
        """The fillet of every rounded corner of one contour in one master at a
        share of full roundness, before joins are settled."""
        key = (m, ci, scale)
        if key in self._fil:
            return self._fil[key]
        st = self.structs[ci]
        P, C = self.geo[m][ci]
        N, rnd = st.count, self.rounded[ci]
        taus, cut = self._tau[key], self._cut[key]
        out = [None] * N
        shape = {}
        for k in range(N):
            if not rnd[k]:
                continue
            f = Fillet()
            chains = self.chains[ci][k]
            ends = [ch.point(P, C, N, tau)[:2] for ch, tau in zip(chains, taus[k])]
            if k in cut:                        # a stroke end: this fillet is half of its cap
                ends[cut[k][2]] = cut[k][:2]
                if cut[k][3]:                   # it starts at a crotch, not on a tangent
                    ends[1 - cut[k][2]] = cut[k][3]
            (f.A, f.tanA), (f.S, f.tanS) = ends
            reach = max(length(sub(f.A, P[k])), length(sub(f.S, P[k])), 1.0)
            X = line_intersection(f.A, f.tanA, f.S, f.tanS) or P[k]
            if length(sub(X, P[k])) > 3 * reach:        # near-parallel tangents
                X = P[k]
            phi = math.atan2(abs(cross(f.tanA, f.tanS)), dot(f.tanA, f.tanS))
            phi = min(max(phi, 1e-3), MAX_TURN)
            kk = arc_handle(phi)
            f.F1, f.F2 = lerp(f.A, X, kk), lerp(f.S, X, kk)
            out[k] = f
            shape[k] = (X, phi)
        # The two halves of a cap whose sides are parallel add up to half a turn
        # and are drawn as a circle. Where the sides converge or spread (the top
        # of A, the terminal of s) the cap is drawn a little fuller than a circle,
        # the more so the further the two arcs are from half a turn. This is how
        # Intern draws them (measured on 90 ends: the handles are 0.3% longer per
        # degree), and it is what keeps a wide or tapered end from looking pinched.
        for a, b in self.ends.get(ci, ()):
            if a in cut and b in cut and out[a] and out[b]:
                off = abs(math.pi - shape[a][1] - shape[b][1])
                gain = 1.0 + FULLER * math.degrees(off)
                for q in (a, b):
                    X, phi = shape[q]
                    if phi < 0.05 or phi > math.radians(170):
                        continue
                    kk = min(math.tan(phi / 4) / math.tan(phi / 2) * gain, 0.9)
                    out[q].F1, out[q].F2 = lerp(out[q].A, X, kk), lerp(out[q].S, X, kk)
        self._fil[key] = out
        return out

    def _ratio(self, ci, k, side):
        """How long the stroke-side handle of a join is, as a share of the fillet's
        handle: one number for all masters and all roundness stops. With a fixed
        share the join is a fixed blend of its two handles everywhere, which is
        what keeps it smooth under interpolation, and it sits exactly where the
        circle touches the stroke. (It used to sit midway between the handles
        whatever their lengths, which dragged it up to 40 units along the
        tangent at heavy weights and left a shoulder on c, e, s, 3, 5.)"""
        key = (ci, k, side)
        if key in self._ratios:
            return self._ratios[key]
        ch = self.chains[ci][k][side]
        top = self.reach[key] + 1.0
        N = self.structs[ci].count
        rho = 1.0
        for m in range(self.M):
            P, C = self.geo[m][ci]
            for f in self.stops:
                fl = self._fillets(m, ci, f)[k]
                h = length(sub(fl.F1, fl.A)) if side == 0 else length(sub(fl.F2, fl.S))
                tau = self._tau[(m, ci, f)][k][side]
                if h < 1e-6 or top - tau < 1e-6:
                    continue
                rho = min(rho, self._handle(P, C, N, ch, tau, tau + (top - tau) * JOIN_SHARE) / h)
        rho = max(rho, MIN_RATIO)
        self._ratios[key] = rho
        return rho

    @staticmethod
    def _handle(P, C, N, ch, t0, t1):
        """Length of the handle at t0 of the single curve that replaces the chain from t0 to t1."""
        pa, ta, _, _ = ch.point(P, C, N, t0)
        pb, tb, _, _ = ch.point(P, C, N, t1)
        X = line_intersection(pa, ta, pb, tb)
        span = length(sub(pb, pa))
        if X is None or length(sub(X, pa)) > 2 * span:
            return span / 2
        return length(sub(X, pa))

    def solution(self, m, ci, scale=1.0):
        """Rounded geometry of one contour in one master at a share of full roundness."""
        self._plan()
        key = (m, ci, scale)
        if key in self._solutions:
            return self._solutions[key]
        st = self.structs[ci]
        P, C = self.geo[m][ci]
        N, rnd = st.count, self.rounded[ci]
        sol = Solution()
        taus = self._tau[key]
        cut = self._cut[key]
        sol.P, sol.C = list(P), list(C)
        sol.C2 = {s: self._halves(P, C, N, s) for s in self.split[ci]}
        sol.fillets = [None] * N
        sol.touched = set()
        sol.joins = []
        trim = {}
        for k in range(N):
            if not rnd[k]:
                continue
            src = self._fillets(m, ci, scale)[k]
            f = Fillet()
            f.A, f.F1, f.F2, f.S, f.tanA, f.tanS = src.A, src.F1, src.F2, src.S, src.tanA, src.tanS
            chains = self.chains[ci][k]
            sol.fillets[k] = f
            for side, (ch, tau) in enumerate(zip(chains, taus[k])):
                _, _, idx, t = ch.point(P, C, N, tau)
                s = ch.segs[idx]
                if k in cut and cut[k][3] is not None and side != cut[k][2]:
                    self._return(sol, st, P, C, ch, tau, cut[k][3][0])
                    continue
                if ch.straight:
                    if not ch.shared and idx > 0:
                        self._slide(sol, P, C, N, ch, tau)
                elif not ch.shared:
                    h = length(sub(f.F1, f.A)) if side == 0 else length(sub(f.F2, f.S))
                    self._refit(sol, st, P, C, ch, self.reach[(ci, k, side)], tau,
                                h * self._ratio(ci, k, side))
                    if not (k in cut and cut[k][3] and side != cut[k][2]):
                        sol.joins.append((k, side))
                else:                           # one curve shared by two corners
                    lo, hi = trim.get(s, (0.0, 1.0))
                    trim[s] = (max(lo, t), hi) if ch.sign > 0 else (lo, min(hi, t))
                    sol.touched.update((s, (s + 1) % N))
        for s, (lo, hi) in trim.items():
            if (lo, hi) != (0.0, 1.0):
                sol.C[s] = quad_blossom(P[s], C[s], P[(s + 1) % N], lo, max(hi, lo))
        for k in range(N):      # nodes on a straight edge between two fillets
            if not rnd[k]:
                continue
            ch = self.chains[ci][k][1]
            n = len(ch.segs)
            if not (ch.shared and ch.straight and n > 1):
                continue
            lo, hi = taus[k][1], n - taus[ch.far][0]
            hi = max(hi, lo)
            free = [i for i in range(1, n) if lo < i < hi]         # untouched: they keep their place
            first, last = (free[0], free[-1]) if free else (hi, lo)
            head = [i for i in range(1, n) if i <= lo]
            tail = [i for i in range(1, n) if i >= hi and i > lo]
            for r, i in enumerate(head):
                at = lo + (first - lo) * (r + 1) / (len(head) + 1)
                sol.P[ch.segs[i]] = ch.point(P, C, N, at)[0]
            for r, i in enumerate(reversed(tail)):
                at = hi - (hi - last) * (r + 1) / (len(tail) + 1)
                sol.P[ch.segs[i]] = ch.point(P, C, N, at)[0]
        for k, far in self.ends.get(ci, ()):    # nodes on the cut of a stroke end
            if k in cut:
                ch = self.chains[ci][k][1]
                n = len(ch.segs)
                for i in range(1, n):
                    sol.P[ch.segs[i]] = lerp(cut[k][0], cut[far][0], i / n)
        self._solutions[key] = sol
        return sol

    # -- output
    def n_rounded(self):
        return sum(sum(r) for r in self.rounded if r)

    def _emit(self, ci, P, C, C2, explicit, fillets=None, m=0):
        st = self.structs[ci]
        rounded, split = self.rounded[ci], self.split[ci]
        extra = self.extra[ci]
        pts, flags = [], []
        for k in range(st.count):
            two = extra.get(st.nodes[k][1]) if st.nodes[k][0] == "on" else None
            here = two[0][m] if two else P[k]           # a corner drawn with two points: the first one
            if rounded[k]:
                f = fillets[k] if fillets else None
                pts.extend([f.A, f.F1, f.F2, f.S] if f else [here] * 4)
                flags.extend([1, 0, 0, 1])
                if two:                                 # ... and the second, which rides on the end of the fillet
                    pts.append(f.S if f else two[1][m])
                    flags.append(1)
            elif st.nodes[k][0] == "on" or explicit[k]:
                pts.append(here)
                flags.append(1)
                if two:
                    pts.append(two[1][m])
                    flags.append(1)
            if k in split:
                pts.extend(C2[k])
                flags.extend([0, 0])
            elif C[k] is not None:
                pts.append(C[k])
                flags.append(0)
        return pts, flags

    def _smooth_joins(self):
        """Where a fillet runs into a curve, the join has a handle on each side,
        both on the tangent there. A point that sits midway between its two
        handles in every master stays smooth at every weight, size and roundness
        in between, so that is where each join is put. It moves along the tangent
        by a unit or two; the outline barely notices. (Measured against keeping
        the join on the exact tangency point: visible direction breaks at
        in-between weights drop from 246 to 12 across the font.)"""
        if self._joined:
            return
        self._joined = True
        for ci, st in enumerate(self.structs):
            if st is None:
                continue
            for m in range(self.M):
                for f in self.stops:
                    sol = self.solution(m, ci, f)
                    for k, side in sol.joins:
                        ch = self.chains[ci][k][side]
                        fl = sol.fillets[k]
                        near = sol.C2[ch.segs[0]][0 if ch.sign > 0 else 1]
                        w = 1.0 / (1.0 + self._ratio(ci, k, side))
                        if ch.sign > 0:
                            fl.S = lerp(fl.F2, near, w)
                        else:
                            fl.A = lerp(fl.F1, near, w)

    def build(self):
        """Returns (flags_per_contour, layers) where layers[0] holds the sharp
        outline of every master and layers[i] the outline at self.stops[i - 1]
        of full roundness. All layers share one point structure."""
        self._plan()
        self._smooth_joins()
        stops = self.stops
        explicit = []
        for ci, st in enumerate(self.structs):
            if st is None:
                explicit.append(None)
                continue
            touched = set(self.pinned[ci])
            for m in range(self.M):
                for f in stops:
                    touched |= self.solution(m, ci, f).touched
            explicit.append([st.nodes[k][0] == "imp" and k in touched for k in range(st.count)])
        flags_out = None
        layers = [[] for _ in range(len(stops) + 1)]
        for m in range(self.M):
            per_layer = [[] for _ in layers]
            f_contours = []
            for ci, st in enumerate(self.structs):
                if st is None:
                    for lay in per_layer:
                        lay.append(list(self.masters[m][ci]))
                    f_contours.append([1 if f else 0 for f in self.on_flags[ci]])
                    continue
                P, C = self.geo[m][ci]
                halves = {s: self._halves(P, C, st.count, s) for s in self.split[ci]}
                pts, fl = self._emit(ci, P, C, halves, explicit[ci], m=m)
                per_layer[0].append(pts)
                for i, f in enumerate(stops):
                    sol = self.solution(m, ci, f)
                    rp, rf = self._emit(ci, sol.P, sol.C, sol.C2, explicit[ci], sol.fillets, m=m)
                    assert rf == fl
                    per_layer[i + 1].append(rp)
                f_contours.append(fl)
            for lay, got in zip(layers, per_layer):
                lay.append(got)
            if flags_out is None:
                flags_out = f_contours
            else:
                assert flags_out == f_contours
        return flags_out, layers
