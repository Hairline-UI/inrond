"use client";

import { useCallback, useRef } from "react";
import { getDial, reducedMotion, useDial, useOnce } from "@/lib/dial";
import { Head } from "@/components/Frame";
import { Plate } from "@/components/Kit";

const TEXT =
  "Switch a product from Inter to Inrond and nothing in the layout moves. Each letter keeps Inter’s advance width, kerning and shaping at every setting of the axis, so a label that fitted still fits, a table column stays put and a line break lands on the same word. Turn the dial anywhere on this page and watch the ends of these lines.";

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
  const out = {
    set: useRef<HTMLSpanElement>(null),
    lines: useRef<HTMLSpanElement>(null),
    moved: useRef<HTMLSpanElement>(null),
    widest: useRef<HTMLSpanElement>(null),
  };
  const sweeping = useRef(false);
  const frame = useRef(0);

  const measure = useCallback((v: number) => {
    const a = live.current;
    const b = ghost.current;
    if (!a || !b) return;
    const la = lineEnds(a);
    const lb = lineEnds(b);
    let moved = 0;
    la.forEach(([, x], i) => (moved = Math.max(moved, Math.abs(x - (lb[i]?.[1] ?? x)))));
    if (la.length !== lb.length) moved = Infinity;
    const widest = Math.max(...la.map(([, x]) => x));
    if (out.set.current) out.set.current.textContent = String(Math.round(v));
    if (out.lines.current) out.lines.current.textContent = String(la.length);
    if (out.moved.current) out.moved.current.textContent = Number.isFinite(moved) ? moved.toFixed(2) : "reflowed";
    if (out.widest.current) out.widest.current.textContent = widest.toFixed(1);
    if (ticks.current) {
      ticks.current.innerHTML = la
        .map(([top, x]) => `<i style="top:${top}px;left:${x.toFixed(1)}px"></i>`)
        .join("");
    }
  }, []);

  const apply = useCallback(
    (v: number) => {
      block.current?.style.setProperty("--prond", v.toFixed(2));
      cancelAnimationFrame(frame.current);
      frame.current = requestAnimationFrame(() => measure(v));
    },
    [measure]
  );

  useDial((v) => {
    if (!sweeping.current) apply(v);
  });

  const sweep = useCallback(() => {
    if (reducedMotion()) return;
    sweeping.current = true;
    const keys = [getDial(), 0, 100, getDial()];
    const ms = 3600;
    const t0 = performance.now();
    const step = (now: number) => {
      const e = Math.min(1, (now - t0) / ms);
      const seg = Math.min(2, Math.floor(e * 3));
      const t = e * 3 - seg;
      const s = t * t * (3 - 2 * t);
      const v = keys[seg] + (keys[seg + 1] - keys[seg]) * s;
      block.current?.style.setProperty("--prond", v.toFixed(2));
      measure(v);
      if (e < 1) requestAnimationFrame(step);
      else sweeping.current = false;
    };
    requestAnimationFrame(step);
  }, [measure]);

  const stage = useOnce(sweep, 0.35);

  return (
    <section id="reflow" className="sec" aria-labelledby="reflow-title">
      <Head
        label="No reflow"
        id="reflow-title"
        title={
          <>
            The corners change. <span className="mute">The line breaks don’t.</span>
          </>
        }
        text="Rounded fonts are usually separate designs with their own widths, so switching to one re-wraps every paragraph and every button. Inrond is measured against Inter glyph by glyph: zero advance widths differ, at any roundness."
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
                Paragraph <span className="dim">· 450 · line ends marked</span>
              </span>
              <span className="legend">
                <i className="legend__ghost" aria-hidden /> ROND 0 underneath
              </span>
            </>
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
          <dl className="readouts">
            <div>
              <dt>This paragraph at ROND</dt>
              <dd>
                <span ref={out.set}>64</span>
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
            <div>
              <dt>Furthest a line end moved from ROND 0</dt>
              <dd>
                <span ref={out.moved}>0.00</span>
                <small> px</small>
              </dd>
            </div>
          </dl>
          <p className="side__note">
            The grey underneath is the same paragraph set at ROND 0. It shows only at the corners the round pen took away; the
            line ends never part.
          </p>
          <button type="button" className="btn btn--soft btn--sm" onClick={sweep}>
            Run 0 to 100 again
          </button>
        </aside>
      </div>
    </section>
  );
}
