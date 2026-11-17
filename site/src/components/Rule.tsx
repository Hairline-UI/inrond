"use client";

import { useEffect, useRef, useState } from "react";
import { getDial, reducedMotion, useDial } from "@/lib/dial";
import { useEased } from "@/lib/ease";
import { build, type Glyph } from "@/lib/glyph";
import { Head } from "@/components/Frame";
import { Plate } from "@/components/Kit";

/* ---------- The pad: the word at any weight (left to right) and any roundness (bottom to top) ---------- */

type Inst = { x: number[]; g: number[][] };
type PadData = {
  word: string;
  weights: number[];
  ronds: number[];
  cmds: [string, number][][];
  metrics: { ascender: number; cap: number; x: number; descender: number };
  inst: Inst[][];
};

const WMIN = 100;
const WMAX = 900;

function bracket(stops: number[], v: number) {
  let i = 0;
  while (i < stops.length - 2 && v > stops[i + 1]) i++;
  const t = (v - stops[i]) / (stops[i + 1] - stops[i]);
  return [i, Math.min(1, Math.max(0, t))] as const;
}

/** The font interpolates linearly between these samples, so mixing the four around a point gives the font's own outline. */
function mix(d: PadData, w: number, r: number) {
  const [i, t] = bracket(d.weights, w);
  const [j, u] = bracket(d.ronds, r);
  const a = d.inst[i][j];
  const b = d.inst[i + 1][j];
  const c = d.inst[i][j + 1];
  const e = d.inst[i + 1][j + 1];
  const k0 = (1 - t) * (1 - u);
  const k1 = t * (1 - u);
  const k2 = (1 - t) * u;
  const k3 = t * u;
  const lerp = (p: number[], q: number[], s: number[], z: number[]) => p.map((_, n) => p[n] * k0 + q[n] * k1 + s[n] * k2 + z[n] * k3);
  return { x: lerp(a.x, b.x, c.x, e.x), g: a.g.map((_, n) => lerp(a.g[n], b.g[n], c.g[n], e.g[n])) };
}

const PX = 300; // margin in font units, left and right of the widest word
const PY = 330;

function Pad() {
  const [data, setData] = useState<PadData | null>(null);
  const box = useRef<HTMLDivElement>(null);
  const svg = useRef<SVGSVGElement>(null);
  const els = {
    ink: useRef<SVGPathElement>(null),
    line: useRef<SVGPathElement>(null),
    hand: useRef<SVGPathElement>(null),
    on: useRef<SVGPathElement>(null),
    off: useRef<SVGPathElement>(null),
    clipL: useRef<SVGRectElement>(null),
    clipR: useRef<SVGRectElement>(null),
    split: useRef<HTMLDivElement>(null),
    w: useRef<HTMLSpanElement>(null),
    r: useRef<HTMLSpanElement>(null),
    wIn: useRef<HTMLInputElement>(null),
    rIn: useRef<HTMLInputElement>(null),
  };
  const touched = useRef(false);
  const unit = useRef(4); // font units per CSS pixel, kept current by a resize observer
  const pos = useRef({ w: 560, r: 64 });

  useEffect(() => {
    let live = true;
    import("@/data/pad.json").then((m) => live && setData(m.default as unknown as PadData));
    return () => {
      live = false;
    };
  }, []);

  const geo = data && (() => {
    const widest = Math.max(...data.inst.flat().map((n) => n.x[n.x.length - 1]));
    const top = data.metrics.ascender + PY;
    const bottom = data.metrics.descender - PY;
    return { widest, vw: widest + PX * 2, top, vh: top - bottom };
  })();

  const draw = () => {
    if (!data || !geo) return;
    const { w, r } = pos.current;
    const m = mix(data, w, r);
    const total = m.x[m.x.length - 1];
    const shift = (geo.widest - total) / 2;
    let d = "";
    let hand = "";
    const on: number[] = [];
    const off: number[] = [];
    m.g.forEach((nums, n) => {
      const b = build({ cmds: data.cmds[n] } as unknown as Glyph, nums, m.x[n] + shift);
      d += b.d;
      hand += b.handles;
      on.push(...b.on);
      off.push(...b.off);
    });
    const s = unit.current;
    // On a phone the word is small: smaller squares, and no handle dots, so the points do not pile up.
    const small = s > 9;
    const q = (small ? 2.2 : 3.5) * s;
    const c = 2.6 * s;
    let onD = "";
    for (let k = 0; k < on.length; k += 2) onD += `M${(on[k] - q).toFixed(1)} ${(on[k + 1] - q).toFixed(1)}h${2 * q}v${2 * q}h${-2 * q}z`;
    let offD = "";
    for (let k = 0; !small && k < off.length; k += 2) offD += `M${(off[k] - c).toFixed(1)} ${off[k + 1].toFixed(1)}a${c} ${c} 0 1 0 ${2 * c} 0a${c} ${c} 0 1 0 ${-2 * c} 0`;
    els.ink.current?.setAttribute("d", d);
    els.line.current?.setAttribute("d", d);
    els.hand.current?.setAttribute("d", small ? "" : hand);
    els.on.current?.setAttribute("d", onD);
    els.off.current?.setAttribute("d", offD);
    // The split follows the weight: filled to its left, drawn to its right.
    const f = (w - WMIN) / (WMAX - WMIN);
    const sx = -PX + f * geo.vw;
    els.clipL.current?.setAttribute("width", String(Math.max(0, sx + PX)));
    els.clipR.current?.setAttribute("x", String(sx));
    els.clipR.current?.setAttribute("width", String(Math.max(0, geo.vw - (sx + PX))));
    const el = els.split.current;
    if (el) {
      el.style.left = `${(f * 100).toFixed(3)}%`;
      el.style.setProperty("--y", `${(100 - r).toFixed(3)}%`);
      el.classList.toggle("is-right", f > 0.72);
    }
    if (els.w.current) els.w.current.textContent = String(Math.round(w));
    if (els.r.current) els.r.current.textContent = String(Math.round(r));
    if (els.wIn.current && document.activeElement !== els.wIn.current) els.wIn.current.value = String(Math.round(w));
    if (els.rIn.current && document.activeElement !== els.rIn.current) els.rIn.current.value = String(Math.round(r));
  };

  const W = useEased(560, (v) => {
    pos.current.w = v;
    draw();
  }, 0.09);
  const R = useEased(64, (v) => {
    pos.current.r = v;
    draw();
  }, 0.09);

  // Marker sizes stay the same on screen whatever the pad's width.
  useEffect(() => {
    const el = svg.current;
    if (!el || !geo) return;
    const ro = new ResizeObserver(() => {
      unit.current = geo.vw / Math.max(1, el.clientWidth);
      draw();
    });
    ro.observe(el);
    return () => ro.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  // Before anyone touches it, the pad starts from the page's roundness and drifts slowly while on screen.
  useEffect(() => {
    if (!data) return;
    R.set(getDial(), true);
    draw();
    if (reducedMotion()) return;
    let raf = 0;
    let seen = false;
    const t0 = performance.now();
    const io = new IntersectionObserver(([e]) => {
      seen = e.isIntersecting;
      if (seen && !raf) raf = requestAnimationFrame(tick);
    });
    const tick = (now: number) => {
      raf = 0;
      if (touched.current || !seen) return;
      const t = (now - t0) / 1000;
      W.set(500 + 330 * Math.sin(t * 0.42), true);
      R.set(50 + 44 * Math.sin(t * 0.29 + 1.2), true);
      raf = requestAnimationFrame(tick);
    };
    if (box.current) io.observe(box.current);
    return () => {
      io.disconnect();
      cancelAnimationFrame(raf);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  // The page's dial still reaches the pad until the visitor takes it over.
  useDial((v) => {
    if (!touched.current && reducedMotion()) R.set(v, true);
  });

  const point = (e: React.PointerEvent<HTMLDivElement>) => {
    const b = e.currentTarget.getBoundingClientRect();
    const fx = Math.min(1, Math.max(0, (e.clientX - b.left) / b.width));
    const fy = Math.min(1, Math.max(0, (e.clientY - b.top) / b.height));
    touched.current = true;
    W.set(WMIN + fx * (WMAX - WMIN));
    R.set(100 * (1 - fy));
  };

  const asc = data?.metrics.ascender ?? 1984;
  const vb = geo ? `${-PX} ${-geo.top} ${geo.vw} ${geo.vh}` : "0 0 5600 3100";
  const yPct = (y: number) => (geo ? ((geo.top - y) / geo.vh) * 100 : 0);
  const metrics: [string, number][] = data
    ? [
        ["Ascender", data.metrics.ascender],
        ["Cap height", data.metrics.cap],
        ["x-height", data.metrics.x],
        ["Baseline", 0],
        ["Descender", data.metrics.descender],
      ]
    : [];

  return (
    <Plate
      className="span-full pad"
      sheetClass="pad__sheet"
      bar={
        <>
          <span className="bar__name">
            <span className="glyphmark" aria-hidden>
              ✥
            </span>
            {data?.word ?? "Sugar"}{" "}
            <span className="dim mono">
              · wght <span ref={els.w}>560</span> · ROND <span ref={els.r}>64</span>
            </span>
          </span>
          <span className="legend pad__legend">
            <i className="pad__key pad__key--ink" aria-hidden /> filled
            <i className="pad__key pad__key--line" aria-hidden /> outline and points
          </span>
        </>
      }
    >
      <div
        ref={box}
        className="pad__box"
        onPointerDown={(e) => {
          if (e.pointerType !== "touch") e.currentTarget.setPointerCapture(e.pointerId);
          point(e);
        }}
        onPointerMove={(e) => {
          if (e.pointerType === "mouse" || e.currentTarget.hasPointerCapture(e.pointerId)) point(e);
        }}
        aria-hidden
      >
        <div className="pad__grid" />
        {metrics.map(([n, y]) => (
          <div key={n} className="pad__metric" style={{ top: `${yPct(y)}%` }}>
            <span>{n}</span>
            <span className="mono">{y === 0 ? "0" : y.toLocaleString("en-US").replace("-", "−")}</span>
          </div>
        ))}
        <svg ref={svg} className="pad__svg" viewBox={vb} preserveAspectRatio="xMidYMid meet">
          <defs>
            <clipPath id="pad-l">
              <rect ref={els.clipL} x={-PX} y={-(asc + PY)} width="0" height="99999" />
            </clipPath>
            <clipPath id="pad-r">
              <rect ref={els.clipR} x={-PX} y={-(asc + PY)} width="99999" height="99999" />
            </clipPath>
          </defs>
          <path ref={els.ink} className="pad__ink" clipPath="url(#pad-l)" />
          <g clipPath="url(#pad-r)">
            <path ref={els.line} className="pad__line" />
            <path ref={els.hand} className="pad__hand" />
            <path ref={els.off} className="pad__off" />
            <path ref={els.on} className="pad__on" />
          </g>
        </svg>
        <div className="pad__split" ref={els.split}>
          <i className="pad__dot" />
          <span className="pad__tag mono">
            <b>filled</b>
            <b>outline</b>
          </span>
        </div>
        <div className="pad__ax pad__ax--x mono">
          {[100, 200, 300, 400, 500, 600, 700, 800, 900].map((w) => (
            <span key={w} style={{ left: `${((w - WMIN) / (WMAX - WMIN)) * 100}%` }}>
              {w}
            </span>
          ))}
        </div>
        <div className="pad__ax pad__ax--y mono">
          {[25, 50, 75, 100].map((r) => (
            <span key={r} style={{ top: `${100 - r}%` }}>
              {r}
            </span>
          ))}
        </div>
      </div>
      <div className="sr">
        <label>
          Weight
          <input
            ref={els.wIn}
            type="range"
            min={WMIN}
            max={WMAX}
            defaultValue={560}
            onInput={(e) => {
              touched.current = true;
              W.set(Number((e.target as HTMLInputElement).value));
            }}
          />
        </label>
        <label>
          Roundness
          <input
            ref={els.rIn}
            type="range"
            min={0}
            max={100}
            defaultValue={64}
            onInput={(e) => {
              touched.current = true;
              R.set(Number((e.target as HTMLInputElement).value));
            }}
          />
        </label>
      </div>
    </Plate>
  );
}

/* ---------- The three rules, drawn ---------- */

/** Rectangle with chosen corners rounded by r. Corners: tl, tr, br, bl. */
function rr(x: number, y: number, w: number, h: number, r: [number, number, number, number]) {
  const [a, b, c, d] = r;
  return `M${x} ${y + a}${a ? `A${a} ${a} 0 0 1 ${x + a} ${y}` : ""}H${x + w - b}${b ? `A${b} ${b} 0 0 1 ${x + w} ${y + b}` : ""}V${
    y + h - c
  }${c ? `A${c} ${c} 0 0 1 ${x + w - c} ${y + h}` : ""}H${x + d}${d ? `A${d} ${d} 0 0 1 ${x} ${y + h - d}` : ""}Z`;
}

function Hatch({ id }: { id: string }) {
  return (
    <defs>
      <pattern id={id} width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
        <rect className="hatch__bg" width="6" height="6" />
        <line className="hatch__line hatch__line--sm" x1="0" y1="0" x2="0" y2="6" />
      </pattern>
    </defs>
  );
}

function useShape(fn: (t: number) => string) {
  const ref = useRef<SVGPathElement>(null);
  useDial((v) => ref.current?.setAttribute("d", fn(v / 100)));
  return ref;
}

function Cap() {
  const ink = useShape((t) => rr(110, 54, 100, 220, [50 * t, 50 * t, 0, 0]));
  return (
    <svg viewBox="0 0 320 250" className="cons" aria-hidden>
      <Hatch id="h1" />
      <path className="cons__removed" d={rr(110, 54, 100, 220, [0, 0, 0, 0])} fill="url(#h1)" />
      <path ref={ink} className="cons__ink" />
      <circle className="cons__pen" cx="160" cy="104" r="50" />
      <circle className="cons__c" cx="160" cy="104" r="3.5" />
    </svg>
  );
}

function Corner() {
  const ink = useShape((t) => {
    const r = 40 * t;
    return `M50 250V${60 + r}${r ? `A${r} ${r} 0 0 1 ${50 + r} 60` : ""}H330V140H130V250Z`;
  });
  return (
    <svg viewBox="0 0 320 250" className="cons" aria-hidden>
      <Hatch id="h2" />
      <path className="cons__removed" d="M50 250V60H330V140H130V250Z" fill="url(#h2)" />
      <path ref={ink} className="cons__ink" />
      <circle className="cons__pen" cx="90" cy="100" r="40" />
      <circle className="cons__c" cx="90" cy="100" r="3.5" />
      <circle className="cons__keep" cx="130" cy="140" r="7" />
    </svg>
  );
}

function Join() {
  return (
    <svg viewBox="0 0 320 250" className="cons" aria-hidden>
      <path className="cons__ink" d="M-10 60H330V130H195V250H125V130H-10Z" />
      <circle className="cons__keep" cx="125" cy="130" r="7" />
      <circle className="cons__keep" cx="195" cy="130" r="7" />
    </svg>
  );
}

const RULES = [
  { k: "Stroke ends", t: "Every stroke end becomes a half circle.", d: "The width of the stroke sets the size of the circle, so Thin and Black end the same way.", art: <Cap /> },
  { k: "Outer corners", t: "Outer corners round by about half the stroke.", d: "Thin weights get small corners and Black gets big ones, in proportion.", art: <Corner /> },
  { k: "Joins", t: "Where strokes meet, nothing changes.", d: "Joins and the insides of letters stay sharp, so text keeps Inter’s even texture.", art: <Join /> },
];

export function Rule() {
  return (
    <section id="rule" className="sec" aria-labelledby="rule-title">
      <Head
        label="How it is built"
        id="rule-title"
        title={
          <>
            See every letter take shape. <span className="mute">At any weight and roundness.</span>
          </>
        }
        text="Move across the board: left to right changes the weight, bottom to top the roundness. Left of the line you see the letters as they will look; right of it, the outlines they are drawn from."
      />
      <div className="wrap grid sec-body rulebody">
        <Pad />
        {RULES.map((c, i) => (
          <figure key={c.k} className="span-4 rulecell">
            <Plate
              bar={
                <span className="bar__name">
                  <span className="mono dim">{String(i + 1).padStart(2, "0")}</span> {c.k}
                </span>
              }
            >
              {c.art}
            </Plate>
            <figcaption>
              <strong>{c.t}</strong> {c.d}
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}
