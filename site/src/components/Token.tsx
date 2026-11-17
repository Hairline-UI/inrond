"use client";

import { useRef, useState } from "react";
import { glide, useDial } from "@/lib/dial";
import { Head } from "@/components/Frame";
import { CodePanel, Plate } from "@/components/Kit";
import { Thumb } from "@/components/Thumb";

const RADII = [0, 2, 4, 6, 8, 10, 12];

const CODE = `:root { --round: 0.64; }

.button, .field {
  /* 7.7px */
  border-radius: calc(var(--round) * 12px);
}
body {
  /* ROND 64 */
  font-variation-settings:
    "ROND" calc(var(--round) * 100);
}`;

export function Token() {
  const radii = useRef<HTMLDivElement>(null);
  const round = useRef<HTMLSpanElement>(null);
  const px = useRef<HTMLSpanElement>(null);
  const pct = useRef<HTMLSpanElement>(null);
  const [role, setRole] = useState("Member");

  useDial((v) => {
    const r = v / 100;
    if (round.current) round.current.textContent = r.toFixed(2);
    if (px.current) px.current.textContent = (r * 12).toFixed(1);
    if (pct.current) pct.current.textContent = String(Math.round(v));
    radii.current?.querySelectorAll<HTMLButtonElement>("button").forEach((b) => {
      const on = String(Math.abs((Number(b.dataset.r) / 12) * 100 - v) < 0.6);
      if (b.getAttribute("aria-pressed") !== on) b.setAttribute("aria-pressed", on);
    });
  });

  const live = (
    <pre className="code__pre">
      <code>
        <span className="ln">
          <span className="t-sel">:root</span> <span className="t-punct">{"{"}</span> <span className="t-key">--round</span>
          <span className="t-punct">:</span>{" "}
          <span className="t-num t-live" ref={round}>
            0.64
          </span>
          <span className="t-punct">; {"}"}</span>
          {"\n"}
        </span>
        <span className="ln">{"\n"}</span>
        <span className="ln">
          <span className="t-sel">.button</span>
          <span className="t-punct">,</span> <span className="t-sel">.field</span> <span className="t-punct">{"{"}</span>
          {"\n"}
        </span>
        <span className="ln">
          {"  "}
          <span className="t-comment">
            /* <span ref={px}>7.7</span>px */
          </span>
          {"\n"}
        </span>
        <span className="ln">
          {"  "}
          <span className="t-key">border-radius</span>
          <span className="t-punct">:</span> <span className="t-fn">calc</span>(<span className="t-fn">var</span>(<span className="t-key">--round</span>) <span className="t-punct">*</span> <span className="t-num">12px</span>)
          <span className="t-punct">;</span>
          {"\n"}
        </span>
        <span className="ln">
          <span className="t-punct">{"}"}</span>
          {"\n"}
        </span>
        <span className="ln">
          <span className="t-sel">body</span> <span className="t-punct">{"{"}</span>
          {"\n"}
        </span>
        <span className="ln">
          {"  "}
          <span className="t-comment">
            /* ROND <span ref={pct}>64</span> */
          </span>
          {"\n"}
        </span>
        <span className="ln">
          {"  "}
          <span className="t-key">font-variation-settings</span>
          <span className="t-punct">:</span>
          {"\n"}
        </span>
        <span className="ln">
          {"    "}
          <span className="t-string">&quot;ROND&quot;</span> <span className="t-fn">calc</span>(<span className="t-fn">var</span>(<span className="t-key">--round</span>) <span className="t-punct">*</span>{" "}
          <span className="t-num">100</span>)<span className="t-punct">;</span>
          {"\n"}
        </span>
        <span className="ln">
          <span className="t-punct">{"}"}</span>
        </span>
      </code>
    </pre>
  );

  return (
    <section id="token" className="sec" aria-labelledby="token-title">
      <Head
        label="One token"
        id="token-title"
        title={
          <>
            One number for your corners <span className="mute">and your letters.</span>
          </>
        }
        text="Use one value for both your corner radius and the roundness of your text. Change it once and buttons, fields and words round together. This page works that way: pick a radius and watch everything follow."
      />
      <div className="wrap grid sec-body">
        <div className="span-main token__controls">
          <div className="token__k">
            <span>Pick a corner radius</span>
            <span className="dim">the whole page follows</span>
          </div>
          <div className="seg seg--radii" role="group" aria-label="Corner radius" ref={radii}>
            <Thumb />
            {RADII.map((r) => (
              <button key={r} type="button" className="seg__b" data-r={r} onClick={() => glide((r / 12) * 100)}>
                <svg viewBox="0 0 24 24" aria-hidden>
                  <path d={`M4 21V${4 + r * 1.2}${r ? `A${r * 1.2} ${r * 1.2} 0 0 1 ${4 + r * 1.2} 4` : ""}H21`} />
                </svg>
                <span className="mono">{r}</span>
              </button>
            ))}
          </div>
          <CodePanel files={[{ name: "tokens.css", code: CODE }]} live={live} />
        </div>

        <Plate
          className="span-side token__plate"
          sheetClass="token__stage"
          bar={
            <>
              <span className="bar__name">
                <span className="glyphmark" aria-hidden>
                  ▢
                </span>
                Example <span className="dim">· corners and text share one value</span>
              </span>
            </>
          }
        >
          <div className="app app--compact" role="group" aria-label="Example product panel">
            <div className="app__top">
              <span className="app__ws" aria-hidden>
                NS
              </span>
              <div>
                <p className="app__t">Invite to Northwind</p>
                <p className="app__s">14 members on the Pro plan</p>
              </div>
            </div>
            <div className="app__field">
              <span className="app__lbl">Email</span>
              <div className="app__input">
                <span className="tag">mira@northwind.studio</span>
                <span className="caret" aria-hidden />
              </div>
            </div>
            <div className="app__field">
              <span className="app__lbl">Role</span>
              <div className="seg" role="radiogroup" aria-label="Role">
                <Thumb />
                {["Member", "Admin", "Guest"].map((r) => (
                  <button key={r} type="button" className="seg__b" role="radio" aria-checked={role === r} onClick={() => setRole(r)}>
                    {r}
                  </button>
                ))}
              </div>
            </div>
            <div className="app__foot">
              <span className="btn btn--soft btn--sm">Cancel</span>
              <span className="btn btn--solid btn--sm">Send invite</span>
            </div>
          </div>
        </Plate>
      </div>
    </section>
  );
}
