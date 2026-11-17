"use client";

import { useRef } from "react";
import { glide, setDial, useDial } from "@/lib/dial";
import { Thumb } from "@/components/Thumb";

/** The page's roundness control. Every copy drives the same value; the page eases to it frame by frame. */
export function Dial({ id, compact = false, label = "Roundness" }: { id: string; compact?: boolean; label?: string }) {
  const input = useRef<HTMLInputElement>(null);
  const dragging = useRef(false);
  useDial((v) => {
    const el = input.current;
    if (el && !dragging.current) el.value = v.toFixed(1);
  }, input);
  return (
    <div className={compact ? "dial dial--compact" : "dial"}>
      <label htmlFor={id} className="sr">
        {label} (ROND axis, 0 to 100)
      </label>
      <input
        ref={input}
        id={id}
        type="range"
        min={0}
        max={100}
        step="any"
        defaultValue={64}
        onPointerDown={() => (dragging.current = true)}
        onPointerUp={() => (dragging.current = false)}
        onPointerCancel={() => (dragging.current = false)}
        onBlur={() => (dragging.current = false)}
        onInput={(e) => setDial(Number((e.target as HTMLInputElement).value))}
      />
      {!compact && (
        <div className="dial__scale" aria-hidden>
          {[0, 25, 50, 75, 100].map((s) => (
            <span key={s} style={{ left: `${s}%` }}>
              {s}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

/** The live value, printed. */
export function DialValue({ className = "" }: { className?: string }) {
  const el = useRef<HTMLSpanElement>(null);
  useDial((v) => {
    const t = String(Math.round(v));
    if (el.current && el.current.textContent !== t) el.current.textContent = t;
  });
  return (
    <span ref={el} className={className} suppressHydrationWarning>
      64
    </span>
  );
}

/** Preset stops as a segmented tray; the white chip sits on the stop the dial is at, and glides between them. */
export function Presets() {
  const row = useRef<HTMLDivElement>(null);
  const sets: [string, number][] = [
    ["Inter", 0],
    ["Soft", 50],
    ["Round", 100],
  ];
  useDial((v) => {
    row.current?.querySelectorAll<HTMLButtonElement>("button").forEach((b) => {
      const on = String(Math.abs(Number(b.dataset.v) - v) < 0.5);
      if (b.getAttribute("aria-pressed") !== on) b.setAttribute("aria-pressed", on);
    });
  });
  return (
    <div className="seg" role="group" aria-label="Jump to a setting" ref={row}>
      <Thumb />
      {sets.map(([n, x]) => (
        <button key={n} type="button" className="seg__b" data-v={x} onClick={() => glide(x)}>
          {n}
          <span className="mono">{x}</span>
        </button>
      ))}
    </div>
  );
}
