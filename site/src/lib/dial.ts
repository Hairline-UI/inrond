"use client";

// The page's one dial. The value lives in a CSS variable on <html> (--rond), so type,
// corners and frame nodes follow it without React re-rendering. Components that draw
// from it (the outline drawing, readouts) subscribe and write to the DOM through refs.

import { useEffect, useRef, useState } from "react";

export const DEFAULT_ROND = 64;

let value = DEFAULT_ROND;
const listeners = new Set<(v: number) => void>();
let intro: number | null = null;

export const clamp = (v: number, lo = 0, hi = 100) => Math.min(hi, Math.max(lo, v));

export function getDial() {
  return value;
}

/** Sets the dial. Anything the visitor does passes user=true, which stops the opening sweep. */
export function setDial(v: number, user = true) {
  if (user && intro !== null) {
    cancelAnimationFrame(intro);
    intro = null;
  }
  value = clamp(v);
  document.documentElement.style.setProperty("--rond", value.toFixed(2));
  listeners.forEach((l) => l(value));
}

export function subscribe(l: (v: number) => void) {
  listeners.add(l);
  return () => {
    listeners.delete(l);
  };
}

/** Calls fn now and on every change, without re-rendering. */
export function useDial(fn: (v: number) => void) {
  const ref = useRef(fn);
  ref.current = fn;
  useEffect(() => {
    const l = (v: number) => ref.current(v);
    l(value);
    return subscribe(l);
  }, []);
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

export const reducedMotion = () =>
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

/** Plays the dial through key values once (the hero's opening sweep). Any visitor input stops it. */
export function playDial(keys: number[], ms: number) {
  if (reducedMotion()) return;
  if (intro !== null) cancelAnimationFrame(intro);
  const seg = ms / (keys.length - 1);
  const t0 = performance.now();
  const step = (now: number) => {
    const e = now - t0;
    const i = Math.min(keys.length - 2, Math.floor(e / seg));
    const t = Math.min(1, (e - i * seg) / seg);
    setDial(keys[i] + (keys[i + 1] - keys[i]) * ease(t), false);
    if (e < ms) intro = requestAnimationFrame(step);
    else intro = null;
  };
  intro = requestAnimationFrame(step);
}

/** Moves the dial to a value with a short glide (instant under reduced motion). */
export function glide(to: number, ms = 520) {
  if (reducedMotion()) return setDial(to);
  playDial([value, to], ms);
}

/** Runs fn once when el is at least 30% on screen. */
export function useOnce(fn: () => void, threshold = 0.3) {
  const ref = useRef<HTMLDivElement>(null);
  const cb = useRef(fn);
  cb.current = fn;
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          cb.current();
          io.disconnect();
        }
      },
      { threshold }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [threshold]);
  return ref;
}
