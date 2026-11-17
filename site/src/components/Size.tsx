"use client";

import { useRef } from "react";
import { SIZES } from "@/data/site";
import { useOnce } from "@/lib/dial";
import { Head } from "@/components/Frame";
import { Plate } from "@/components/Kit";

const MAX = 266;

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
        text={
          <>
            Rounding doubles the outline points, so with the axis live Inrond is 2.5 times Inter&rsquo;s Latin file. If your site
            needs one roundness, ship Round or Soft at about 1.6 times Inter, or freeze any value with{" "}
            <code className="mono">scripts/pin.py</code>.
          </>
        }
      />
      <div className="wrap size" ref={stage}>
        <div className="size__text">
          <div className="pick">
            <p className="side__k">Which file to ship</p>
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
                <dt>Themes, hover states, animation</dt>
                <dd>
                  <span>
                    <code className="mono">inrond.css</code>, axis live
                  </span>
                  <span className="mono dim">257 KB</span>
                </dd>
              </div>
              <div>
                <dt>Roman and italic, both live</dt>
                <dd>
                  <span>Freeze one, or load the italic lazily</span>
                  <span className="mono dim">539 KB</span>
                </dd>
              </div>
            </dl>
          </div>
          <div className="math">
            <p className="side__k">What that means for a first visit</p>
            <p>
              <span className="mono">+154 KB</span> of Latin font over Inter with the axis live. At the 1.6 Mbit/s Lighthouse uses
              for slow 4G that is about <span className="mono">0.77 s</span>; at 10 Mbit/s about <span className="mono">0.1 s</span>.
              Text shows in the fallback until it arrives (<span className="mono">font-display: swap</span>), and the file is cached
              after.
            </p>
            <p className="fine">Arithmetic from the file sizes, not a measurement on a live site.</p>
          </div>
        </div>
        <div className="bars" ref={bars}>
          <Plate
            bar={
              <>
                <span className="bar__name">
                  <span className="glyphmark" aria-hidden>
                    ▤
                  </span>
                  woff2 <span className="dim">· Latin subset, bars to scale</span>
                </span>
                <span className="mono dim">full font</span>
              </>
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
          <div className="bars__aside">
            <p>
              <strong>Honest comparison.</strong> Google Sans Flex cut to the same three axes (weight, optical size and roundness)
              is <span className="mono">202 KB</span> of Latin; Inrond is <span className="mono">257 KB</span>. Inrond is not the
              smaller choice; it is the Inter-compatible one.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
