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
from statistics import median

EPS = 1e-6
INF = float("inf")
MIN_TURN = math.radians(20)      # smaller direction changes are not treated as corners
MAX_TURN = math.radians(172)
SMOOTH_TURN = math.radians(8)    # a fillet may run through nodes smoother than this
TERMINAL_TURN = math.radians(50)
TERMINAL_WIDTH = 1.5             # a stroke end is at most this many stems wide
CURVE_REACH = 0.70               # share of the last curve segment a fillet may consume
MAX_CHAIN = 5


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
    __slots__ = ("k", "sign", "segs", "far", "shared", "straight")

    def point(self, P, C, N, tau):
        """Point and travel-direction tangent at chain parameter tau (0 = corner)."""
        n = len(self.segs)
        idx = min(int(tau), n - 1)
        frac = min(max(tau - idx, 0.0), 1.0)
        s = self.segs[idx]
        a, b = P[s], P[(s + 1) % N]
        t = frac if self.sign > 0 else 1 - frac
        if C[s] is None:
            return lerp(a, b, t), unit(sub(b, a)), idx, t
        tg = unit(quad_tan(a, C[s], b, t)) or unit(sub(b, a))
        return quad_pt(a, C[s], b, t), tg, idx, t

    def tau_max(self, C):
        n = len(self.segs)
        if self.shared:
            return float(n) if self.straight else 0.5
        if C[self.segs[-1]] is None:
            return float(n)
        return n - (1 - CURVE_REACH)

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

    def __init__(self, masters, on_flags, stems, upm, factor=1.0, blocked=(), stops=(1.0,)):
        self.masters = masters
        self.stems = stems
        self.eps = upm * 0.002
        self.factor = factor
        self.blocked = set(blocked)
        self.on_flags = on_flags
        self.structs = [Structure(f) if len(f) >= 3 else None for f in on_flags]
        self.M = len(masters)
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
        self.rounded = self._candidates()
        self._drop_hidden()
        self.chains = self._chains()
        self.caps = [self._cap(m) for m in range(self.M)]
        self._solutions = {}
        self._radii = {}
        self._tau = None
        self._joined = False
        self.stops = tuple(stops)

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
                    for m in range(self.M):
                        cr = self.cor[m][ci][k]
                        if not cr.convex or cr.turn < MIN_TURN:
                            ok = False
                            break
                flags.append(ok)
            out.append(flags)
        return out

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
        for m in range(self.M):
            polys = [flatten(st, *self.geo[m][ci]) for ci, st in enumerate(self.structs) if st is not None]
            boxes = [bbox(p) for p in polys]
            for ci, st in enumerate(self.structs):
                if st is None:
                    continue
                for k in range(st.count):
                    if self.rounded[ci][k] and any(covered(p, polys, boxes) for p in self.near_probes(m, ci, k)):
                        self.rounded[ci][k] = False

    # -- where a fillet may run on each side of a corner
    def _smooth(self, ci, k):
        st = self.structs[ci]
        if st.nodes[k][0] == "imp":
            return True
        return all(self.cor[m][ci][k].turn < SMOOTH_TURN for m in range(self.M))

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
                    ch.k, ch.sign, ch.segs, ch.shared = k, sign, [], False
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
                        # two corners joined by a run with curves in it: each keeps its half
                        ch.segs = ch.segs[:max(1, len(ch.segs) // 2)]
                        ch.straight = all(st.ctrl[s] is None for s in ch.segs)
                    if not ch.shared:
                        ch.segs = ch.segs[:MAX_CHAIN]
                        ch.straight = all(st.ctrl[s] is None for s in ch.segs)
                    last = ch.segs[-1]
                    ch.far = (last + 1) % N if sign > 0 else last
                    pair.append(ch)
                per[k] = pair
            out.append(per)
        return out

    def _terminal_width(self, m, ci, k, far):
        """Diameter of the circle inscribed in the stroke end between two corners, or None."""
        P, _ = self.geo[m][ci]
        a, b = self.cor[m][ci][k], self.cor[m][ci][far]
        if a.turn < TERMINAL_TURN or b.turn < TERMINAL_TURN:
            return None
        w = 2 * length(sub(P[far], P[k])) / (a.tan + b.tan)
        return w if w <= TERMINAL_WIDTH * self.stems[m] else None

    # -- radius cap for outer corners: half the local stroke width
    def _cap(self, m):
        stem = self.stems[m]
        ends = []
        for ci, st in enumerate(self.structs):
            if st is None:
                continue
            for k in range(st.count):
                if self.rounded[ci][k]:
                    ch = self.chains[ci][k][1]
                    if ch.shared and ch.straight:
                        w = self._terminal_width(m, ci, k, ch.far)
                        if w:
                            ends.append(w)
        est = median(ends) if ends else stem
        est = min(max(est, 0.3 * stem), 1.15 * stem)
        return 0.5 * est

    def _estimate(self, m, ci):
        """First guess of every radius, treating the sides as straight lines."""
        st = self.structs[ci]
        P, C = self.geo[m][ci]
        N, cor, rnd = st.count, self.cor[m][ci], self.rounded[ci]
        r = [INF if rnd[k] else 0.0 for k in range(N)]
        term = [False] * N
        for k in range(N):
            if not rnd[k]:
                continue
            for ch in self.chains[ci][k]:
                if ch.shared and ch.straight:
                    lim = length(sub(P[ch.far], P[k])) / (cor[k].tan + cor[ch.far].tan)
                    if self._terminal_width(m, ci, k, ch.far):
                        term[k] = True
                else:
                    reach = length(sub(ch.point(P, C, N, ch.tau_max(C))[0], P[k]))
                    lim = reach / cor[k].tan
                r[k] = min(r[k], lim)
        cap = self.caps[m]
        for k in range(N):
            if rnd[k] and not term[k]:
                r[k] = min(r[k], cap)
        return r, term

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
                is_end = term[k] and term[far] and self._terminal_width(m, ci, k, far)
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
        for k in range(N):                  # two fillets on one straight edge must not cross
            if rnd[k]:
                ch = self.chains[ci][k][1]
                if ch.shared and ch.straight:
                    n = len(ch.segs)
                    a, b = taus[k][1], taus[ch.far][0]
                    if a + b > n:
                        f = n / (a + b)
                        taus[k] = (taus[k][0], a * f)
                        taus[ch.far] = (b * f, taus[ch.far][1])
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

    def _refit(self, sol, st, P, C, ch, J, tau):
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
        knots = [tau + (top - tau) * i / nq for i in range(nq + 1)]
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
        sol.P, sol.C = list(P), list(C)
        sol.C2 = {s: self._halves(P, C, N, s) for s in self.split[ci]}
        sol.fillets = [None] * N
        sol.touched = set()
        sol.joins = []
        trim = {}
        for k in range(N):
            if not rnd[k]:
                continue
            f = Fillet()
            chains = self.chains[ci][k]
            ends = [ch.point(P, C, N, tau)[:2] for ch, tau in zip(chains, taus[k])]
            (f.A, f.tanA), (f.S, f.tanS) = ends
            reach = max(length(sub(f.A, P[k])), length(sub(f.S, P[k])), 1.0)
            X = line_intersection(f.A, f.tanA, f.S, f.tanS) or P[k]
            if length(sub(X, P[k])) > 3 * reach:        # near-parallel tangents
                X = P[k]
            phi = math.atan2(abs(cross(f.tanA, f.tanS)), dot(f.tanA, f.tanS))
            phi = min(max(phi, 1e-3), MAX_TURN)
            kk = math.tan(phi / 4) / math.tan(phi / 2)
            f.F1, f.F2 = lerp(f.A, X, kk), lerp(f.S, X, kk)
            sol.fillets[k] = f
            for side, (ch, tau) in enumerate(zip(chains, taus[k])):
                _, _, idx, t = ch.point(P, C, N, tau)
                s = ch.segs[idx]
                if ch.straight:
                    if not ch.shared and idx > 0:
                        self._slide(sol, P, C, N, ch, tau)
                elif not ch.shared:
                    self._refit(sol, st, P, C, ch, self.reach[(ci, k, side)], tau)
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
        self._solutions[key] = sol
        return sol

    # -- output
    def n_rounded(self):
        return sum(sum(r) for r in self.rounded if r)

    def _emit(self, ci, P, C, C2, explicit, fillets=None):
        st = self.structs[ci]
        rounded, split = self.rounded[ci], self.split[ci]
        pts, flags = [], []
        for k in range(st.count):
            if rounded[k]:
                f = fillets[k] if fillets else None
                pts.extend([f.A, f.F1, f.F2, f.S] if f else [P[k]] * 4)
                flags.extend([1, 0, 0, 1])
            elif st.nodes[k][0] == "on" or explicit[k]:
                pts.append(P[k])
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
                        if ch.sign > 0:
                            fl.S = lerp(fl.F2, near, 0.5)
                        else:
                            fl.A = lerp(fl.F1, near, 0.5)

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
                pts, fl = self._emit(ci, P, C, halves, explicit[ci])
                per_layer[0].append(pts)
                for i, f in enumerate(stops):
                    sol = self.solution(m, ci, f)
                    rp, rf = self._emit(ci, sol.P, sol.C, sol.C2, explicit[ci], sol.fillets)
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
