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
            All of Inter, <span className="mute">rounded by the same rule.</span>
          </>
        }
        text="2,937 glyphs and 2,852 characters: Latin with Vietnamese, 249 Cyrillic, 105 Greek, figures, arrows and symbols, the optical size axis and Inter's drawn italic. Every one of them has the axis. Point at a letter to inspect it."
      />
      <div className="wrap" ref={stage}>
        <Plate
          dark
          className="cov"
          sheetClass="cov__sheet"
          bar={
            <>
              <span className="bar__name">
                <span className="glyphmark" aria-hidden>
                  ж
                </span>
                48 of 2,937 glyphs <span className="dim">· weight 560 · ROND <DialValue /></span>
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
                ["1,106", "glyphs with rounded corners"],
                ["6,936", "corners rounded, roman"],
                ["72", "composites rounded whole"],
                ["16", "joining ends kept sharp"],
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
          <div className="inspect__stage">
            <span className="inspect__ghost" aria-hidden>
              {cell.c}
            </span>
            <span className="inspect__c">{cell.c}</span>
            <span className="inspect__base" aria-hidden />
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
              <dt>Glyph</dt>
              <dd className="mono">{cell.n}</dd>
            </div>
            <div>
              <dt>Advance</dt>
              <dd>
                <span className="mono">{cell.adv.toLocaleString("en-US")} u</span>, as in Inter
              </dd>
            </div>
            <div>
              <dt>Shown at</dt>
              <dd>
                <span className="mono">
                  ROND <DialValue />
                </span>
                , over ROND 0 in grey
              </dd>
            </div>
          </dl>
        </div>
        </Plate>
      </div>
    </section>
  );
}
