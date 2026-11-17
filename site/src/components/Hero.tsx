"use client";

import { useEffect, useMemo, useRef } from "react";
import { G, WORD, build, data, f, numsAt } from "@/lib/glyph";
import { DOWNLOAD, INTER, VERSION } from "@/data/site";
import { DEFAULT_ROND, playDial, useDial } from "@/lib/dial";
import { Dial, DialValue, Presets } from "@/components/Dial";
import { Arrow, Plate } from "@/components/Kit";
import { StarButton } from "@/components/Stars";

const ADV = WORD.map((c) => G[c].adv);
const X0 = [0, ADV[0]];
const WIDTH = ADV[0] + ADV[1];
const TOP = 1700;
const BOTTOM = 820;
const PADX = 70;

function GlyphDrawing() {
  const fill = useRef<SVGPathElement>(null);
  const handles = useRef<SVGPathElement>(null);
  const onPts = useRef<SVGPathElement>(null);
  const offPts = useRef<SVGPathElement>(null);
  const svg = useRef<SVGSVGElement>(null);

  const sharp = useMemo(() => WORD.map((c, i) => build(G[c], G[c].paths[0], X0[i]).d).join(""), []);

  useDial((v) => {
    let d = "";
    let h = "";
    let onD = "";
    let offD = "";
    WORD.forEach((c, i) => {
      const b = build(G[c], numsAt(G[c], v), X0[i]);
      d += b.d;
      h += b.handles;
      for (let k = 0; k < b.on.length; k += 2) onD += `M${f(b.on[k] - 11)} ${f(b.on[k + 1] - 11)}h22v22h-22z`;
      for (let k = 0; k < b.off.length; k += 2) offD += `M${f(b.off[k] - 9)} ${f(b.off[k + 1])}a9 9 0 1 0 18 0a9 9 0 1 0 -18 0`;
    });
    fill.current?.setAttribute("d", d);
    handles.current?.setAttribute("d", h);
    onPts.current?.setAttribute("d", onD);
    offPts.current?.setAttribute("d", offD);
  }, svg);

  const lines: [number, string][] = [
    [data.capHeight, "cap height"],
    [data.xHeight, "x-height"],
    [0, "baseline"],
    [data.descender, "descender"],
  ];
  const dimY = -data.descender + 190;

  return (
    <svg
      ref={svg}
      className="drawing"
      viewBox={`${-PADX} ${-TOP} ${WIDTH + PADX * 2} ${TOP + BOTTOM}`}
      role="img"
      aria-label="Outline drawing of the letters a and s from Inrond at the current roundness. The ink the rounding removes is hatched; the advance widths stay 1,162 and 1,103 units."
    >
      <defs>
        <pattern id="hatch" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect className="hatch__bg" width="22" height="22" />
          <line className="hatch__line" x1="0" y1="0" x2="0" y2="22" />
        </pattern>
      </defs>
      <g className="drawing__metrics">
        {lines.map(([y, n]) => (
          <g key={n}>
            <line x1={-PADX} x2={WIDTH + PADX} y1={-y} y2={-y} />
            <text x={WIDTH + PADX - 8} y={-y - 18} textAnchor="end">
              {n} {y.toLocaleString("en-US").replace("-", "−")}
            </text>
          </g>
        ))}
        {[0, ADV[0], WIDTH].map((x) => (
          <line key={x} x1={x} x2={x} y1={-TOP} y2={dimY + 40} className="drawing__side" />
        ))}
      </g>
      <path className="drawing__removed" d={sharp} fill="url(#hatch)" />
      <path ref={fill} className="drawing__ink" />
      <path ref={handles} className="drawing__handles" />
      <path ref={offPts} className="drawing__off" />
      <path ref={onPts} className="drawing__on" />
      <g className="drawing__dims">
        {WORD.map((c, i) => (
          <g key={c}>
            <line x1={X0[i] + 6} x2={X0[i] + ADV[i] - 6} y1={dimY} y2={dimY} />
            <path d={`M${X0[i] + 6} ${dimY - 26}v52M${X0[i] + ADV[i] - 6} ${dimY - 26}v52`} />
            <rect x={X0[i] + ADV[i] / 2 - 150} y={dimY - 34} width={300} height={68} />
            <text x={X0[i] + ADV[i] / 2} y={dimY + 17} textAnchor="middle">
              {ADV[i].toLocaleString("en-US")} u
            </text>
          </g>
        ))}
      </g>
    </svg>
  );
}

export function Hero({ stars }: { stars: number | null }) {
  const ink = useRef<HTMLSpanElement>(null);
  const inkBar = useRef<HTMLSpanElement>(null);

  // The roundness readout follows the dial on its own, whether or not the drawing is on screen.
  useDial((v) => {
    const t = String(Math.round(v));
    if (ink.current && ink.current.textContent !== t) ink.current.textContent = t;
    if (inkBar.current) inkBar.current.style.transform = `scaleX(${(v / 100).toFixed(3)})`;
  });

  useEffect(() => {
    // Opening sweep: from the painted setting through round and sharp, back where it started.
    const t = setTimeout(() => playDial([DEFAULT_ROND, 100, 0, DEFAULT_ROND], 2800), 450);
    return () => clearTimeout(t);
  }, []);

  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="wrap grid hero__grid">
        <div className="span-main hero__words">
          <p className="eyebrow">
            <span className="chip">v{VERSION}</span> Free and open source
          </p>
          <h1 id="hero-title" className="display">
            Inter, with a <span className="mute">roundness axis.</span>
          </h1>
          <p className="lede">
            Choose how round your letters are, from 0 (plain Inter) to 100 (fully round). Use the same number as your corner
            radius and your text matches your buttons. Every letter keeps Inter&rsquo;s width, so nothing on your page moves.
          </p>
          <div className="hero__cta">
            <a className="btn btn--solid" href={DOWNLOAD} data-oa-event="download" data-oa-prop-location="hero">
              Download {VERSION}
              <span className="btn__dot">
                <Arrow dir="down" />
              </span>
            </a>
            <StarButton initial={stars} />
          </div>
          <p className="fine">
            Built on <a href={INTER}>Inter 4.1</a> by Rasmus Andersson. Not affiliated with the Inter project.
          </p>
        </div>

        <Plate
          className="span-side hero__plate"
          bar={
            <>
              <span className="bar__name">
                <span className="glyphmark" aria-hidden>
                  a
                </span>
                a s <span className="dim">· ExtraBold</span>
              </span>
              <span className="legend">
                <i className="legend__hatch" aria-hidden /> rounded off
              </span>
            </>
          }
          foot={
            <div className="hero__controls">
              <div className="hero__dial">
                <div className="hero__dialhead">
                  <span>Roundness</span>
                  <span className="mono hero__val">
                    ROND <DialValue />
                  </span>
                </div>
                <Dial id="dial-hero" />
              </div>
              <Presets />
            </div>
          }
        >
          <GlyphDrawing />
        </Plate>
      </div>

      <div className="wrap grid">
        <div className="span-full stats">
          <div className="span-3 stat">
            <span className="stat__k">Roundness now</span>
            <span className="stat__v">
              <span ref={ink}>64</span>
              <small> of 100</small>
            </span>
            <span className="meter" aria-hidden>
              <span ref={inkBar} />
            </span>
          </div>
          <div className="span-3 stat">
            <span className="stat__k">Change in letter width</span>
            <span className="stat__v">0</span>
            <span className="stat__n">the same as Inter at every setting</span>
          </div>
          <div className="span-3 stat">
            <span className="stat__k">Characters</span>
            <span className="stat__v">2,852</span>
            <span className="stat__n">Latin, Cyrillic, Greek, Vietnamese</span>
          </div>
          <div className="span-3 stat">
            <span className="stat__k">Styles</span>
            <span className="stat__v">2</span>
            <span className="stat__n">roman and a drawn italic, 100 to 900</span>
          </div>
        </div>
      </div>
    </section>
  );
}
