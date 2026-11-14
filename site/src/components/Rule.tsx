"use client";

import { useRef } from "react";
import { useDial } from "@/lib/dial";
import { Head } from "@/components/Frame";
import { Plate } from "@/components/Kit";

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
      <path className="cons__dim" d="M110 30H210M110 24v12M210 24v12" />
      <text x="160" y="20" textAnchor="middle">
        w
      </text>
      <path className="cons__dim cons__r" d="M160 104L195.4 68.6" />
      <text x="222" y="118">
        r = ½ w
      </text>
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
      <path className="cons__dim" d="M300 60V140M294 60h12M294 140h12" />
      <text x="288" y="106" textAnchor="end" className="cons__inv">
        local stroke
      </text>
      <circle className="cons__keep" cx="130" cy="140" r="7" />
      <text x="146" y="172">
        inner corner: sharp
      </text>
    </svg>
  );
}

function Join() {
  return (
    <svg viewBox="0 0 320 250" className="cons" aria-hidden>
      <path className="cons__ink" d="M-10 60H330V130H195V250H125V130H-10Z" />
      <circle className="cons__keep" cx="125" cy="130" r="7" />
      <circle className="cons__keep" cx="195" cy="130" r="7" />
      <text x="160" y="40" textAnchor="middle">
        the same at every setting
      </text>
    </svg>
  );
}

export function Rule() {
  const mark = useRef<HTMLSpanElement>(null);
  useDial((v) => mark.current?.style.setProperty("left", `${v}%`));
  const cells = [
    {
      n: "01",
      k: "Stroke end",
      v: "r = w / 2",
      t: "A stroke end gets a round cap.",
      d: "The circle inscribed between the stroke's two sides, as a round pen would leave it.",
      art: <Cap />,
    },
    {
      n: "02",
      k: "Outer corner",
      v: "r = stroke / 2",
      t: "An outer corner gets half the stroke.",
      d: "Its radius is half the local stroke width, so a hairline and a Black stem round in proportion.",
      art: <Corner />,
    },
    {
      n: "03",
      k: "Join",
      v: "r = 0",
      t: "Joins, crotches and counters stay crisp.",
      d: "Where strokes meet, nothing is rounded. That keeps Inter's joins, and its colour on the page.",
      art: <Join />,
    },
  ];
  return (
    <section id="rule" className="sec" aria-labelledby="rule-title">
      <Head
        label="The rule"
        id="rule-title"
        title={
          <>
            How the rounding works. <span className="mute">One rule, applied by a script.</span>
          </>
        }
        text="A script applies the path of a round pen to every master of Inter. No letter was tuned by eye, which is the point: every outline can be checked against the rule, and the same rule runs on all 2,937 glyphs. The drawings below follow the dial."
      />
      <div className="wrap rulegrid">
        {cells.map((c) => (
          <figure key={c.n} className="rulecell">
            <Plate
              bar={
                <>
                  <span className="bar__name">
                    <span className="mono dim">{c.n}</span> {c.k}
                  </span>
                  <span className="mono dim">{c.v}</span>
                </>
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
      <div className="wrap stops">
        <div className="stops__text">
          <p className="side__k">How it becomes an axis</p>
          <p>
            The sharp and the round outline of a glyph share one point structure: in the sharp one each fillet collapses onto its
            corner. Exact outlines are also solved at 25, 50 and 75 and stored as small corrections, because a cap that grows along
            a curved stroke would otherwise cut the corner short.
          </p>
        </div>
        <div className="stops__ruler" aria-label="Solved stops on the axis">
          <div className="stops__track">
            <span className="stops__mark" ref={mark} aria-hidden />
            {[0, 25, 50, 75, 100].map((s) => (
              <span key={s} className="stops__stop" style={{ left: `${s}%` }}>
                <i />
                <b className="mono">{s}</b>
                <em>{s === 0 ? "Inter" : "solved"}</em>
              </span>
            ))}
          </div>
          <dl className="stops__figs">
            <div>
              <dt>Outline points, roman</dt>
              <dd className="mono">28,475 → 57,141</dd>
            </div>
            <div>
              <dt>Corrections dropped below</dt>
              <dd className="mono">1 unit</dd>
            </div>
            <div>
              <dt>Italic glyphs rounded gently</dt>
              <dd className="mono">ɢ ʛ ₢ at 75%</dd>
            </div>
          </dl>
        </div>
      </div>
    </section>
  );
}
