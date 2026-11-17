"use client";

import { useRef, useState } from "react";
import sheet from "@/data/sheet.json";
import { reducedMotion, useOnce } from "@/lib/dial";
import { Head } from "@/components/Frame";
import { DialValue } from "@/components/Dial";
import { Plate } from "@/components/Kit";

type Cell = { c: string; g: string; n: string; u: string; name: string; adv: number };
const CELLS = sheet as Cell[];
const START = CELLS.findIndex((x) => x.c === "ж");
// Where Inter's lines sit, in ems from the baseline (2048 units to the em).
const METRICS: [string, number][] = [
  ["Cap height", 1490 / 2048],
  ["x-height", 1118 / 2048],
  ["Baseline", 0],
  ["Descender", -494 / 2048],
];

export function Sheet() {
  const [sel, setSel] = useState(START);
  const grid = useRef<HTMLDivElement>(null);
  const stage = useOnce(() => {
    const el = grid.current;
    if (!el || reducedMotion()) return el?.classList.remove("is-pre");
    el.classList.remove("is-pre");
    el.classList.add("is-run");
    setTimeout(() => el.classList.remove("is-run"), 2400);
  }, 0.25);
  const cell = CELLS[sel];

  return (
    <section id="coverage" className="sec" aria-labelledby="coverage-title">
      <Head
        label="Coverage"
        id="coverage-title"
        title={
          <>
            Every letter Inter has, <span className="mute">rounded the same way.</span>
          </>
        }
        text="All 2,852 characters of Inter, from Vietnamese accents to Cyrillic, Greek, arrows and symbols, in roman and italic. Every one of them rounds. Point at a letter to see it large, with Inter's shape in grey behind it."
      />
      <div className="wrap grid sec-body" ref={stage}>
        <Plate
          dark
          className="span-full cov"
          sheetClass="cov__sheet"
          bar={
            <>
              <span className="bar__name">
                <span className="glyphmark" aria-hidden>
                  ж
                </span>
                48 letters of 2,852 <span className="dim">· at roundness <DialValue /></span>
              </span>
              <span className="cov__scripts">
                {["Latin", "Figures", "Vietnamese", "Greek", "Cyrillic", "Symbols"].map((g) => (
                  <span key={g} className={cell.g === g ? "chip chip--on" : "chip"}>
                    {g}
                  </span>
                ))}
              </span>
            </>
          }
          foot={
            <div className="cov__stats">
              {[
                ["2,937", "glyphs"],
                ["249", "Cyrillic characters"],
                ["105", "Greek characters"],
                ["39", "OpenType features"],
              ].map(([v, k]) => (
                <div key={k} className="cov__stat">
                  <span className="mono">{v}</span>
                  <span>{k}</span>
                </div>
              ))}
            </div>
          }
        >
        <div className="sheet__grid is-pre" ref={grid} role="listbox" aria-label="Glyphs" aria-activedescendant={`g-${sel}`}>
          {CELLS.map((x, i) => (
            <button
              key={x.u}
              id={`g-${i}`}
              type="button"
              role="option"
              aria-selected={i === sel}
              aria-label={`${x.name}, ${x.u}`}
              className="glyph"
              style={{ ["--i" as string]: (i % 8) + Math.floor(i / 8) * 0.5 }}
              onPointerEnter={() => setSel(i)}
              onFocus={() => setSel(i)}
              onClick={() => setSel(i)}
            >
              <span className="glyph__c">{x.c}</span>
              <span className="glyph__u">{x.u.slice(2)}</span>
                          </button>
          ))}
        </div>
        <div className="inspect" aria-live="polite">
          <div className="inspect__top mono">
            <span>{cell.u}</span>
            <span>
              wght 560 · ROND <DialValue />
            </span>
          </div>
          <div className="inspect__stage">
            <div className="inspect__metrics" aria-hidden>
              {METRICS.map(([n, y]) => (
                <span key={n} style={{ ["--y" as string]: y }}>
                  <b>{n}</b>
                </span>
              ))}
            </div>
            <span className="inspect__ghost" aria-hidden>
              {cell.c}
            </span>
            <span className="inspect__c">{cell.c}</span>
          </div>
          <dl className="inspect__dl">
            <div>
              <dt>Name</dt>
              <dd>{cell.name}</dd>
            </div>
            <div>
              <dt>Unicode</dt>
              <dd className="mono">{cell.u}</dd>
            </div>
            <div>
              <dt>Width</dt>
              <dd>
                <span className="mono">{cell.adv.toLocaleString("en-US")}</span> units, same as Inter
              </dd>
            </div>
          </dl>
        </div>
        </Plate>
      </div>
    </section>
  );
}
