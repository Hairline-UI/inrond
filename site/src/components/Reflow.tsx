"use client";

import { useCallback, useRef, useState } from "react";
import { getDial, isPlaying, playDial, reducedMotion, useDial, useOnce } from "@/lib/dial";
import { Head } from "@/components/Frame";
import { Plate } from "@/components/Kit";
import { Dial, DialValue } from "@/components/Dial";

const TEXT =
  "Switch a product from Inter to Inrond and nothing moves. Every letter keeps Inter’s exact width at every roundness, so a label that fitted still fits, a table column stays put and each line breaks on the same word.";

/** Right edges of each rendered line of a text block, relative to the block. */
function lineEnds(el: HTMLElement) {
  const node = el.firstChild;
  if (!node) return [];
  const r = document.createRange();
  r.selectNodeContents(node);
  const box = el.getBoundingClientRect();
  const lines = new Map<number, number>();
  for (const rect of Array.from(r.getClientRects())) {
    if (rect.width < 1) continue;
    const top = Math.round(rect.top - box.top);
    lines.set(top, Math.max(lines.get(top) ?? 0, rect.right - box.left));
  }
  return [...lines.entries()].sort((a, b) => a[0] - b[0]);
}

export function Reflow() {
  const live = useRef<HTMLParagraphElement>(null);
  const ghost = useRef<HTMLParagraphElement>(null);
  const ticks = useRef<HTMLDivElement>(null);
  const block = useRef<HTMLDivElement>(null);
  const [playing, setPlaying] = useState(false);
  const out = {
    lines: useRef<HTMLSpanElement>(null),
    moved: useRef<HTMLSpanElement>(null),
    widest: useRef<HTMLSpanElement>(null),
  };

  const measure = useCallback(() => {
    const a = live.current;
    const b = ghost.current;
    if (!a || !b) return;
    const la = lineEnds(a);
    const lb = lineEnds(b);
    let moved = la.length === lb.length ? 0 : Infinity;
    la.forEach(([, x], i) => (moved = Math.max(moved, Math.abs(x - (lb[i]?.[1] ?? x)))));
    const widest = Math.max(...la.map(([, x]) => x));
    if (out.lines.current) out.lines.current.textContent = String(la.length);
    if (out.moved.current) out.moved.current.textContent = Number.isFinite(moved) ? moved.toFixed(2) : "reflowed";
    if (out.widest.current) out.widest.current.textContent = widest.toFixed(1);
    if (ticks.current) {
      const html = la.map(([top, x]) => `<i style="top:${top}px;left:${x.toFixed(1)}px"></i>`).join("");
      if (ticks.current.innerHTML !== html) ticks.current.innerHTML = html;
    }
  }, []);

  // Measured in this browser on every frame the dial moves, while the paragraph is on screen.
  useDial(measure, block);

  const play = useCallback(() => {
    if (reducedMotion() || isPlaying()) return;
    const from = getDial();
    setPlaying(true);
    playDial([from, 0, 100, from], 4200, () => setPlaying(false));
  }, []);

  const stage = useOnce(play, 0.45, 400);

  return (
    <section id="reflow" className="sec" aria-labelledby="reflow-title">
      <Head
        label="No reflow"
        id="reflow-title"
        title={
          <>
            Round it as much as you like. <span className="mute">Nothing on the page moves.</span>
          </>
        }
        text="Rounded fonts are usually separate designs with their own letter widths, so switching to one re-wraps paragraphs and pushes buttons out of shape. Inrond keeps Inter's exact widths at every roundness. Press play, or drag, and watch the marks at the end of each line: the letters change, the marks don't move."
      />
      <div className="wrap reflow" ref={stage}>
        <Plate
          className="reflow__plate"
          bar={
            <>
              <span className="bar__name">
                <span className="glyphmark" aria-hidden>
                  ¶
                </span>
                Paragraph <span className="dim">· line ends marked</span>
              </span>
              <span className={playing ? "rcount is-live" : "rcount"}>
                ROND <DialValue />
              </span>
            </>
          }
          foot={
            <div className="reflow__controls">
              <button type="button" className="btn btn--solid btn--sm" onClick={play} aria-pressed={playing}>
                <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden>
                  <path d="M3 1.8v8.4L10 6z" fill="currentColor" />
                </svg>
                {playing ? "Playing 0 → 100" : "Play 0 → 100"}
              </button>
              <div className="reflow__dial">
                <Dial id="dial-reflow" compact label="Roundness of the whole page" />
              </div>
            </div>
          }
        >
          <div className="reflow__block" ref={block}>
            <p className="reflow__ghost" ref={ghost} aria-hidden>
              {TEXT}
            </p>
            <p className="reflow__live" ref={live}>
              {TEXT}
            </p>
            <div className="reflow__ticks" ref={ticks} aria-hidden />
          </div>
        </Plate>
        <aside className="reflow__side" aria-label="Measured in your browser">
          <p className="side__k">Measured in your browser, every frame</p>
          <div className="moved">
            <span className="moved__v">
              <span ref={out.moved}>0.00</span>
              <small>px</small>
            </span>
            <span className="moved__k">the furthest any line end has moved from where Inter puts it</span>
          </div>
          <dl className="readouts">
            <div>
              <dt>Roundness now</dt>
              <dd>
                <DialValue />
              </dd>
            </div>
            <div>
              <dt>Lines</dt>
              <dd>
                <span ref={out.lines}>–</span>
              </dd>
            </div>
            <div>
              <dt>Widest line</dt>
              <dd>
                <span ref={out.widest}>–</span>
                <small> px</small>
              </dd>
            </div>
          </dl>
          <p className="side__note">
            The light grey under the text is the same paragraph at ROND 0, which is Inter. You only see it at the corners the
            rounding removes.
          </p>
        </aside>
      </div>
    </section>
  );
}
