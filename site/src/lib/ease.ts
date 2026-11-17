"use client";

import { useEffect, useRef } from "react";
import { reducedMotion } from "@/lib/dial";

// A local value that eases toward its target once per animation frame, like the page's dial, for controls that
// do not drive the whole page (the axis rows, the weight x roundness pad, the tester's dials). paint() is called
// with every new value and is where the caller writes to the DOM; nothing re-renders.

const curve = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

export type Eased = {
  get(): number;
  /** Sets the target. instant skips the ease (and reduced motion always does). */
  set(v: number, instant?: boolean): void;
  /** Plays through key values over ms; anything that calls set() stops it. */
  play(keys: number[], ms: number): void;
};

export function useEased(initial: number, paint: (v: number) => void, tau = 0.07): Eased {
  const p = useRef(paint);
  p.current = paint;
  const ctl = useRef<Eased & { stop(): void }>(null);
  if (!ctl.current) {
    const s = { v: initial, t: initial, raf: 0, last: 0, tl: 0 };
    const frame = (now: number) => {
      const dt = Math.max(0, Math.min(0.05, (now - s.last) / 1000));
      s.last = now;
      const n = s.v + (s.t - s.v) * (1 - Math.exp(-dt / tau));
      s.v = Math.abs(s.t - n) < 0.005 ? s.t : n;
      p.current(s.v);
      s.raf = s.v === s.t ? 0 : requestAnimationFrame(frame);
    };
    const stopTl = () => {
      if (s.tl) cancelAnimationFrame(s.tl);
      s.tl = 0;
    };
    ctl.current = {
      get: () => s.v,
      set(v, instant) {
        if (!Number.isFinite(v)) return;
        stopTl();
        s.t = v;
        if (instant || reducedMotion()) {
          if (s.raf) cancelAnimationFrame(s.raf);
          s.raf = 0;
          s.v = v;
          p.current(v);
          return;
        }
        if (!s.raf) {
          s.last = performance.now();
          s.raf = requestAnimationFrame(frame);
        }
      },
      play(keys, ms) {
        if (reducedMotion() || keys.length < 2) return;
        stopTl();
        if (s.raf) cancelAnimationFrame(s.raf);
        s.raf = 0;
        const seg = ms / (keys.length - 1);
        const t0 = performance.now();
        const step = (now: number) => {
          const e = Math.max(0, now - t0);
          const i = Math.max(0, Math.min(keys.length - 2, Math.floor(e / seg)));
          const t = Math.min(1, (e - i * seg) / seg);
          s.v = s.t = keys[i] + (keys[i + 1] - keys[i]) * curve(t);
          p.current(s.v);
          s.tl = e < ms ? requestAnimationFrame(step) : 0;
        };
        s.tl = requestAnimationFrame(step);
      },
      stop() {
        stopTl();
        if (s.raf) cancelAnimationFrame(s.raf);
        s.raf = 0;
      },
    };
  }
  useEffect(() => {
    const c = ctl.current!;
    p.current(c.get());
    return () => c.stop();
  }, []);
  return ctl.current;
}

/** Value at a pointer position along an element, between min and max. */
export function fromPointer(el: Element, clientX: number, min: number, max: number) {
  const r = el.getBoundingClientRect();
  const f = Math.min(1, Math.max(0, (clientX - r.left) / Math.max(1, r.width)));
  return min + f * (max - min);
}
