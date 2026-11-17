"use client";

import { useEffect, useRef } from "react";
import { getDial, setDial, useDial, useOnce } from "@/lib/dial";
import { fromPointer, useEased } from "@/lib/ease";
import { Head } from "@/components/Frame";
import { Plate } from "@/components/Kit";

type Axis = {
  tag: string;
  name: string;
  note: string;
  min: number;
  max: number;
  start: number;
  lo: string;
  hi: string;
  digits: number;
  /** The roundness row is the page's own dial. */
  dial?: boolean;
  sweep?: number[];
};

const AXES: Axis[] = [
  { tag: "wght", name: "Weight", note: "Thin to Black", min: 100, max: 900, start: 560, lo: "100", hi: "900", digits: 0, sweep: [560, 100, 900, 560] },
  { tag: "ROND", name: "Roundness", note: "Inter to fully round", min: 0, max: 100, start: 64, lo: "0  Inter", hi: "Round  100", digits: 0, dial: true },
  { tag: "opsz", name: "Optical size", note: "Set by the text size", min: 14, max: 32, start: 32, lo: "14  Text", hi: "Display  32", digits: 1, sweep: [32, 14, 32] },
];

function settings(a: Axis, v: number) {
  if (a.tag === "wght") return `"wght" ${v.toFixed(1)}, "opsz" 32, "ROND" var(--rond-i)`;
  if (a.tag === "opsz") return `"wght" 600, "opsz" ${v.toFixed(2)}, "ROND" var(--rond-i)`;
  return `"wght" 600, "opsz" 32, "ROND" ${v.toFixed(2)}`;
}

function Row({ a, plays }: { a: Axis; plays: React.RefObject<(() => void)[]> }) {
  const word = useRef<HTMLSpanElement>(null);
  const knob = useRef<HTMLSpanElement>(null);
  const out = useRef<HTMLSpanElement>(null);
  const track = useRef<HTMLDivElement>(null);

  const paint = (v: number) => {
    const f = (v - a.min) / (a.max - a.min);
    if (word.current) word.current.style.fontVariationSettings = settings(a, v);
    if (knob.current) knob.current.style.left = `${(f * 100).toFixed(3)}%`;
    const t = v.toFixed(a.digits);
    if (out.current && out.current.textContent !== t) out.current.textContent = t;
    track.current?.setAttribute("aria-valuenow", t);
  };
  const local = useEased(a.start, paint);
  // The roundness row reads and writes the page's dial instead of a value of its own.
  useDial((v) => a.dial && paint(v), track);
  useEffect(() => {
    if (!a.sweep) return;
    const fn = () => local.play(a.sweep!, 3600);
    plays.current.push(fn);
    return () => {
      plays.current = plays.current.filter((f) => f !== fn);
    };
  }, [a, local, plays]);

  const set = (v: number) => (a.dial ? setDial(v) : local.set(v));
  const get = () => (a.dial ? getDial() : local.get());
  const step = (a.max - a.min) / 50;

  return (
    <div className="axis">
      <div className="axis__k">
        <span className="axis__tag mono">{a.tag}</span>
        <span className="axis__name">{a.name}</span>
        <span className="axis__note">{a.note}</span>
      </div>
      <div className="axis__word">
        <span ref={word} style={{ fontVariationSettings: settings(a, a.start) }}>
          {a.name}
        </span>
      </div>
      <div className="axis__ctl">
        <div
          ref={track}
          className="ruler"
          role="slider"
          tabIndex={0}
          aria-label={a.name}
          aria-valuemin={a.min}
          aria-valuemax={a.max}
          aria-valuenow={a.start}
          onPointerDown={(e) => {
            e.currentTarget.setPointerCapture(e.pointerId);
            set(fromPointer(e.currentTarget, e.clientX, a.min, a.max));
          }}
          onPointerMove={(e) => {
            if (e.currentTarget.hasPointerCapture(e.pointerId)) set(fromPointer(e.currentTarget, e.clientX, a.min, a.max));
          }}
          onKeyDown={(e) => {
            const d = { ArrowRight: step, ArrowUp: step, ArrowLeft: -step, ArrowDown: -step, PageUp: step * 5, PageDown: -step * 5 }[e.key];
            if (e.key === "Home") set(a.min);
            else if (e.key === "End") set(a.max);
            else if (d) set(Math.min(a.max, Math.max(a.min, get() + d)));
            else return;
            e.preventDefault();
          }}
        >
          <span className="ruler__ticks" aria-hidden />
          <span className="ruler__knob" ref={knob} style={{ left: `${((a.start - a.min) / (a.max - a.min)) * 100}%` }} aria-hidden />
        </div>
        <div className="ruler__ends mono" aria-hidden>
          <span>{a.lo}</span>
          <span>{a.hi}</span>
        </div>
      </div>
      <span className="axis__v mono" ref={out}>
        {a.start.toFixed(a.digits)}
      </span>
    </div>
  );
}

export function Axes() {
  const plays = useRef<(() => void)[]>([]);
  const stage = useOnce(() => plays.current.forEach((p, i) => setTimeout(p, i * 240)), 0.45, 200);
  return (
    <section id="axes" className="sec" aria-labelledby="axes-title">
      <Head
        label="Adjust"
        id="axes-title"
        title={
          <>
            Light or bold, sharp or round. <span className="mute">Any mix you need.</span>
          </>
        }
        text="Set the weight anywhere from Thin to Black and the roundness anywhere from plain Inter to fully round. Spacing adjusts itself too: a little more room in small text, a little tighter in headlines."
      />
      <div className="wrap grid sec-body" ref={stage}>
        <Plate
          className="span-full axes"
          sheetClass="axes__sheet"
          bar={
            <>
              <span className="bar__name">
                <span className="glyphmark" aria-hidden>
                  ↔
                </span>
                Inrond <span className="dim">· one font, every setting</span>
              </span>
            </>
          }
        >
          {AXES.map((a) => (
            <Row key={a.tag} a={a} plays={plays} />
          ))}
        </Plate>
      </div>
    </section>
  );
}
