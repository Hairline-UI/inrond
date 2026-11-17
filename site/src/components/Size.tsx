"use client";

import { useRef } from "react";
import { SIZES } from "@/data/site";
import { useOnce } from "@/lib/dial";
import { Head } from "@/components/Frame";
import { Plate } from "@/components/Kit";

const MAX = Math.max(...SIZES.map((s) => s.latin));

export function Size() {
  const bars = useRef<HTMLDivElement>(null);
  const stage = useOnce(() => bars.current?.classList.add("is-run"), 0.3);
  return (
    <section id="size" className="sec" aria-labelledby="size-title">
      <Head
        label="Size"
        id="size-title"
        title={
          <>
            It’s bigger than Inter. <span className="mute">Here’s by how much, and how to shrink it.</span>
          </>
        }
        text="Rounded corners need more points per letter, so with roundness adjustable Inrond's file is 2.5 times Inter's. If your site uses one roundness, ship the fixed Round or Soft file instead: about 1.6 times Inter."
      />
      <div className="wrap grid sec-body" ref={stage}>
        <div className="span-main bars" ref={bars}>
          <Plate
            bar={
              <>
                <span className="bar__name">
                  <span className="glyphmark" aria-hidden>
                    ▤
                  </span>
                  Download size <span className="dim">· English and Western Europe, drawn to scale</span>
                </span>
                <span className="mono dim">all scripts</span>
              </>
            }
            foot={
              <p className="bars__aside">
                <strong>For comparison:</strong> Google Sans Flex with the same three axes is <span className="mono">202 KB</span>,
                Inrond <span className="mono">257 KB</span>. Inrond is not the smallest choice; it is the one that matches Inter.
              </p>
            }
          >
            {SIZES.map((s, i) => (
              <div key={s.build} className={`bar bar--${s.kind}`} style={{ ["--w" as string]: s.latin / MAX, ["--i" as string]: i }}>
                <div className="bar__name">
                  <strong>{s.build}</strong> <span className="dim">{s.note}</span>
                </div>
                <div className="bar__track">
                  <span className="bar__fill" />
                  <span className="bar__v mono">{s.latin} KB</span>
                </div>
                <span className="bar__full mono dim">{s.full} KB</span>
              </div>
            ))}
          </Plate>
        </div>
        <Plate
          className="span-side size__side"
          sheetClass="size__text"
          bar={
            <span className="bar__name">
              <span className="glyphmark" aria-hidden>
                ✓
              </span>
              Which file to use
            </span>
          }
        >
          <div className="pick">
          <dl>
            <div>
              <dt>One roundness for the whole site</dt>
              <dd>
                <span>
                  <code className="mono">inrond-round.css</code> or <code className="mono">-soft</code>
                </span>
                <span className="mono dim">159–163 KB</span>
              </dd>
            </div>
            <div>
              <dt>Roundness that changes: themes, hover, animation</dt>
              <dd>
                <span>
                  <code className="mono">inrond.css</code>
                </span>
                <span className="mono dim">257 KB</span>
              </dd>
            </div>
            <div>
              <dt>Both roman and italic, adjustable</dt>
              <dd>
                <span>Load the italic only where it is used</span>
                <span className="mono dim">539 KB</span>
              </dd>
            </div>
          </dl>
          </div>
          <div className="math">
            <p className="side__k">On a first visit</p>
            <p>
              Adjustable roundness adds <span className="mono">154 KB</span> over Inter: under a second on a slow phone
              connection, a tenth of a second on broadband. Your text shows in a fallback font until it arrives, and after the
              first visit the file is cached.
            </p>
          </div>
        </Plate>
      </div>
    </section>
  );
}
