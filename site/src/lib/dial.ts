"use client";

// The page's one dial. The value lives in a CSS variable on <html> (--rond), so type, corners and frame nodes follow
// it without React re-rendering. Input never writes it directly: it sets a target, and one animation frame at a time
// the rendered value eases toward that target. Drags are therefore smooth whatever the input's event rate, and each
// frame does the work once. Off-screen sections skip rendering (content-visibility in globals.css), and components
// that draw from the dial can ask to be called only while they are on screen.

import { useEffect, useRef, useState } from "react";

export const DEFAULT_ROND = 64;

let value = DEFAULT_ROND; // what is on screen
let target = DEFAULT_ROND; // where it is heading
let tau = 0.06; // seconds; time constant of the ease
let raf = 0;
let last = 0;
let timeline = 0; // the opening sweep and the reflow demo
const listeners = new Set<(v: number) => void>();

export const clamp = (v: number, lo = 0, hi = 100) => Math.min(hi, Math.max(lo, v));

export const reducedMotion = () =>
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function getDial() {
  return value;
}

// Body text (--rond-t) catches up once the dial comes to rest, 160 ms after the last move. Rendering a page of text at
// a roundness the browser has not seen costs a phone 100 ms or more, so during motion only the corners and the
// outline drawing (--rond, continuous) and the showcase text (--rond-i, whole numbers, cached after first use:
// headline, demo paragraph, glyph grid, tester, wordmark) move. Nothing heavy runs while anything is moving.
let stepped = DEFAULT_ROND;
let settle = 0;
function writeText(v: number) {
  if (v === stepped) return;
  stepped = v;
  document.documentElement.style.setProperty("--rond-t", String(v));
}

let whole = DEFAULT_ROND;
function write(v: number) {
  value = v;
  const root = document.documentElement.style;
  root.setProperty("--rond", v.toFixed(2));
  // Showcase text uses whole numbers: smooth to the eye, and every value is cached after its first use.
  const w = Math.round(v);
  if (w !== whole) {
    whole = w;
    root.setProperty("--rond-i", String(w));
  }
  clearTimeout(settle);
  settle = window.setTimeout(() => {
    if (!raf && !timeline) writeText(Math.round(value));
  }, 160);
  listeners.forEach((l) => l(v));
}

function frame(now: number) {
  // A frame's timestamp can be earlier than the moment the motion started: clamp it, never go backwards.
  const dt = Math.max(0, Math.min(0.05, (now - last) / 1000));
  last = now;
  const next = value + (target - value) * (1 - Math.exp(-dt / tau));
  write(Math.abs(target - next) < 0.03 ? target : next);
  raf = value === target ? 0 : requestAnimationFrame(frame);
}

function stopTimeline() {
  if (timeline) cancelAnimationFrame(timeline);
  timeline = 0;
}

/** Sets where the dial is heading. Anything the visitor does stops a running sweep. */
export function setDial(v: number, opts: { instant?: boolean; ease?: number } = {}) {
  if (!Number.isFinite(v)) return;
  stopTimeline();
  if (!Number.isFinite(value)) value = target;
  target = clamp(v);
  if (opts.instant || reducedMotion()) {
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
    write(target);
    return;
  }
  tau = opts.ease ?? 0.06;
  if (!raf) {
    last = performance.now();
    raf = requestAnimationFrame(frame);
  }
}

/** A longer, softer move, for presets and radius buttons. */
export function glide(to: number) {
  setDial(to, { ease: 0.13 });
}

export function subscribe(l: (v: number) => void) {
  listeners.add(l);
  return () => {
    listeners.delete(l);
  };
}

/**
 * Calls fn now and on every change, without re-rendering. With an element ref, fn runs only while that element is
 * on screen, and once more with the current value when it comes back.
 */
export function useDial(fn: (v: number) => void, when?: React.RefObject<Element | null>) {
  const ref = useRef(fn);
  ref.current = fn;
  useEffect(() => {
    let visible = !when;
    const l = (v: number) => {
      if (visible) ref.current(v);
    };
    let io: IntersectionObserver | undefined;
    if (when?.current) {
      io = new IntersectionObserver(([e]) => {
        visible = e.isIntersecting;
        if (visible) ref.current(value);
      }, { rootMargin: "200px 0px" });
      io.observe(when.current);
    } else {
      ref.current(value);
    }
    const off = subscribe(l);
    return () => {
      off();
      io?.disconnect();
    };
  }, [when]);
}

/** A rounded integer copy of the dial as React state, for text that may re-render. */
export function useDialInt() {
  const [v, setV] = useState(DEFAULT_ROND);
  useDial((x) => {
    const r = Math.round(x);
    setV((p) => (p === r ? p : r));
  });
  return v;
}

const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

/** Plays the dial through key values over ms (the opening sweep, the reflow demo). Any visitor input stops it. */
export function playDial(keys: number[], ms: number, done?: () => void) {
  if (reducedMotion()) return done?.();
  stopTimeline();
  if (raf) cancelAnimationFrame(raf);
  raf = 0;
  const seg = ms / (keys.length - 1);
  const t0 = performance.now();
  const step = (now: number) => {
    const e = Math.max(0, now - t0);
    const i = Math.max(0, Math.min(keys.length - 2, Math.floor(e / seg)));
    const t = Math.min(1, (e - i * seg) / seg);
    const v = keys[i] + (keys[i + 1] - keys[i]) * ease(t);
    target = v;
    write(v);
    if (e < ms) timeline = requestAnimationFrame(step);
    else {
      timeline = 0;
      done?.();
    }
  };
  timeline = requestAnimationFrame(step);
}

export const isPlaying = () => timeline !== 0;

/** Runs fn once when el is at least `threshold` on screen (and has stayed there for `dwell` ms). */
export function useOnce(fn: () => void, threshold = 0.3, dwell = 0) {
  const ref = useRef<HTMLDivElement>(null);
  const cb = useRef(fn);
  cb.current = fn;
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    let timer = 0;
    const io = new IntersectionObserver(
      ([e]) => {
        clearTimeout(timer);
        if (!e.isIntersecting) return;
        timer = window.setTimeout(() => {
          cb.current();
          io.disconnect();
        }, dwell);
      },
      { threshold }
    );
    io.observe(el);
    return () => {
      clearTimeout(timer);
      io.disconnect();
    };
  }, [threshold, dwell]);
  return ref;
}
