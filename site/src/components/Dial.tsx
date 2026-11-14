"use client";

import { useRef } from "react";
import { glide, setDial, useDial, useDialInt } from "@/lib/dial";

/** The page's roundness control. Every copy of it drives the same value. */
export function Dial({ id, compact = false, label = "Roundness" }: { id: string; compact?: boolean; label?: string }) {
  const input = useRef<HTMLInputElement>(null);
  useDial((v) => {
    const el = input.current;
    if (el && document.activeElement !== el) el.value = String(Math.round(v));
  });
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
        step={1}
        defaultValue={64}
        onInput={(e) => setDial(Number((e.target as HTMLInputElement).value))}
      />
      {!compact && (
        <div className="dial__scale" aria-hidden>
          {[0, 25, 50, 75, 100].map((s) => (
            <span key={s} style={{ left: `${s}%` }}>
              <i />
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
    if (el.current) el.current.textContent = String(Math.round(v));
  });
  return (
    <span ref={el} className={className} suppressHydrationWarning>
      64
    </span>
  );
}

/** Preset stops, as a segmented tray: the white chip sits on the one the dial is at. */
export function Presets() {
  const v = useDialInt();
  const sets: [string, number][] = [
    ["Inter", 0],
    ["Soft", 50],
    ["Round", 100],
  ];
  return (
    <div className="seg" role="group" aria-label="Jump to a setting">
      {sets.map(([n, x]) => (
        <button key={n} type="button" className="seg__b" aria-pressed={v === x} onClick={() => glide(x)}>
          {n}
          <span className="mono">{x}</span>
        </button>
      ))}
    </div>
  );
}
