"use client";

import { useRef, useState } from "react";
import { getDial, setDial, useDial } from "@/lib/dial";
import { useEased } from "@/lib/ease";
import { Head } from "@/components/Frame";
import { Plate } from "@/components/Kit";
import { Thumb } from "@/components/Thumb";

const SAMPLES: Record<string, string> = {
  Headline: "Good things come in round letters.",
  Pangram: "Quick wafting zephyrs vex bold Jim.",
  Numbers: "0123456789 · 3/4 · €1,240.50 · 12:30",
  Body: "Rounded corners on buttons, cards and fields make an interface feel friendlier. Now the text can follow: set one number and every letter rounds with your corners, without a single line moving.",
  Cyrillic: "Съешь же ещё этих мягких французских булок.",
  Greek: "Ξεσκεπάζω την ψυχοφθόρα βδελυγμία.",
};

const SWEEP = 270; // degrees of travel, open at the bottom
const R = 26;

function arc(f: number) {
  const a0 = (135 * Math.PI) / 180;
  const a1 = a0 + (SWEEP * Math.PI * f) / 180;
  const x0 = 32 + R * Math.cos(a0);
  const y0 = 32 + R * Math.sin(a0);
  const x1 = 32 + R * Math.cos(a1);
  const y1 = 32 + R * Math.sin(a1);
  return { d: `M${x0.toFixed(2)} ${y0.toFixed(2)}A${R} ${R} 0 ${SWEEP * f > 180 ? 1 : 0} 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`, x1, y1 };
}
const TRACK = arc(1).d;

type KnobProps = {
  label: string;
  min: number;
  max: number;
  start: number;
  format: (v: number) => string;
  apply: (v: number) => void;
  /** The roundness knob is the page's dial. */
  dial?: boolean;
};

/** A turning knob: drag up or right to raise, down or left to lower; arrow keys step. */
function Knob({ label, min, max, start, format, apply, dial }: KnobProps) {
  const fill = useRef<SVGPathElement>(null);
  const dot = useRef<SVGCircleElement>(null);
  const out = useRef<HTMLSpanElement>(null);
  const el = useRef<HTMLDivElement>(null);
  const drag = useRef<{ f: number } | null>(null);

  const paint = (v: number) => {
    const f = (v - min) / (max - min);
    const a = arc(Math.max(0.0001, f));
    fill.current?.setAttribute("d", a.d);
    dot.current?.setAttribute("cx", a.x1.toFixed(2));
    dot.current?.setAttribute("cy", a.y1.toFixed(2));
    const t = format(v);
    if (out.current && out.current.textContent !== t) out.current.textContent = t;
    el.current?.setAttribute("aria-valuenow", String(Math.round(v)));
    el.current?.setAttribute("aria-valuetext", t);
    apply(v);
  };
  const local = useEased(start, paint, 0.035);
  useDial((v) => dial && paint(v));
  const get = () => (dial ? getDial() : local.get());
  const set = (v: number) => {
    const c = Math.min(max, Math.max(min, v));
    if (dial) setDial(c);
    else local.set(c);
  };
  const span = max - min;
  // The value follows the pointer's angle around the dial, like turning a real knob. The gap at the bottom snaps to
  // the nearer end, and a turn never jumps from one end to the other across it.
  const turn = (e: React.PointerEvent<HTMLDivElement>, press = false) => {
    const d = drag.current;
    const box = e.currentTarget.querySelector(".knob__dial")?.getBoundingClientRect();
    if (!d || !box) return;
    const a = (Math.atan2(e.clientY - (box.top + box.height / 2), e.clientX - (box.left + box.width / 2)) * 180) / Math.PI;
    const rel = (a - 135 + 720) % 360;
    let f = rel <= SWEEP ? rel / SWEEP : rel < SWEEP + (360 - SWEEP) / 2 ? 1 : 0;
    // A press goes straight to where it lands; a drag that runs off one end through the gap stays at that end.
    if (!press && Math.abs(f - d.f) > 0.5 && (d.f < 0.2 || d.f > 0.8)) f = d.f > 0.5 ? 1 : 0;
    d.f = f;
    set(min + f * span);
  };

  return (
    <div
      ref={el}
      className="knob"
      role="slider"
      tabIndex={0}
      aria-label={label}
      aria-valuemin={min}
      aria-valuemax={max}
      aria-valuenow={start}
      onPointerDown={(e) => {
        e.preventDefault();
        e.currentTarget.setPointerCapture(e.pointerId);
        e.currentTarget.focus({ preventScroll: true });
        drag.current = { f: (get() - min) / span };
        turn(e, true);
      }}
      onPointerMove={(e) => drag.current && turn(e)}
      onPointerUp={() => (drag.current = null)}
      onPointerCancel={() => (drag.current = null)}
      onKeyDown={(e) => {
        const s = span / 40;
        const d = { ArrowRight: s, ArrowUp: s, ArrowLeft: -s, ArrowDown: -s, PageUp: s * 5, PageDown: -s * 5 }[e.key];
        if (e.key === "Home") set(min);
        else if (e.key === "End") set(max);
        else if (d) set(get() + d);
        else return;
        e.preventDefault();
      }}
    >
      <span className="knob__dial">
        <svg viewBox="0 0 64 64" aria-hidden>
          <path className="knob__track" d={TRACK} />
          <path className="knob__fill" ref={fill} />
          <circle className="knob__dot" ref={dot} r="4.2" />
        </svg>
        <span className="knob__v mono" ref={out}>
          {format(start)}
        </span>
      </span>
      <span className="knob__k">{label}</span>
    </div>
  );
}

export function Tester() {
  const [sample, setSample] = useState("Headline");
  const [italic, setItalic] = useState(false);
  const [align, setAlign] = useState<"left" | "center">("left");
  // The dials write CSS variables on the text; they are kept here too, so a new sample starts with the same settings.
  const text = useRef<HTMLDivElement | null>(null);
  const vars = useRef<Record<string, string>>({});
  const css = (k: string) => (v: string) => {
    vars.current[k] = v;
    text.current?.style.setProperty(k, v);
  };
  const attach = (el: HTMLDivElement | null) => {
    text.current = el;
    if (el) for (const [k, v] of Object.entries(vars.current)) el.style.setProperty(k, v);
  };

  return (
    <section id="tester" className="sec" aria-labelledby="tester-title">
      <Head
        label="Try it"
        id="tester-title"
        title={
          <>
            Try it with your own words. <span className="mute">In three alphabets.</span>
          </>
        }
        text="Pick a sample or click the text and type. Change the weight, roundness, size, line height and spacing to see how it reads."
      />
      <div className="wrap grid sec-body">
        <Plate
          className="span-full tester"
          sheetClass="tester__sheet"
          bar={
            <>
              <div className="seg tester__samples" role="radiogroup" aria-label="Sample text">
                <Thumb />
                {Object.keys(SAMPLES).map((s) => (
                  <button key={s} type="button" className="seg__b" role="radio" aria-checked={sample === s} onClick={() => setSample(s)}>
                    {s}
                  </button>
                ))}
              </div>
              <div className="tester__opts">
                <div className="seg" role="radiogroup" aria-label="Style">
                  <Thumb />
                  {["Roman", "Italic"].map((s) => (
                    <button key={s} type="button" className="seg__b" role="radio" aria-checked={(s === "Italic") === italic} onClick={() => setItalic(s === "Italic")}>
                      {s}
                    </button>
                  ))}
                </div>
                <div className="seg" role="radiogroup" aria-label="Alignment">
                  <Thumb />
                  {(["left", "center"] as const).map((a) => (
                    <button key={a} type="button" className="seg__b seg__b--icon" role="radio" aria-checked={align === a} aria-label={`Align ${a}`} onClick={() => setAlign(a)}>
                      <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden>
                        {a === "left" ? <path d="M2 4h12M2 8h8M2 12h11" /> : <path d="M2 4h12M4 8h8M2.5 12h11" />}
                      </svg>
                    </button>
                  ))}
                </div>
              </div>
            </>
          }
        >
          <div className="knobs">
            <Knob label="Weight" min={100} max={900} start={600} format={(v) => String(Math.round(v))} apply={(v) => css("--tw")(String(Math.round(v)))} />
            <Knob label="Roundness" min={0} max={100} start={64} format={(v) => String(Math.round(v))} apply={() => {}} dial />
            <Knob label="Size" min={16} max={160} start={88} format={(v) => `${Math.round(v)}`} apply={(v) => css("--ts")(`${(Math.round(v * 2) / 2).toFixed(1)}px`)} />
            <Knob label="Line height" min={90} max={160} start={105} format={(v) => `${Math.round(v)}%`} apply={(v) => css("--tl")((v / 100).toFixed(3))} />
            <Knob label="Spacing" min={-6} max={10} start={-3} format={(v) => `${v.toFixed(1)}%`} apply={(v) => css("--tk")(`${(v / 100).toFixed(4)}em`)} />
          </div>
          <div
            key={sample}
            ref={attach}
            className="tester__text"
            contentEditable
            suppressContentEditableWarning
            spellCheck={false}
            aria-label="Editable sample text"
            role="textbox"
            aria-multiline
            style={{ fontStyle: italic ? "italic" : "normal", textAlign: align }}
          >
            {SAMPLES[sample]}
          </div>
        </Plate>
      </div>
    </section>
  );
}
