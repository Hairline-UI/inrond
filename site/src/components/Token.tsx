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
  const [publish, setPublish] = useState(true);

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
        text="Drive the axis from the same token that sets your border-radius. Buttons, fields and type then round together, and changing one number restyles all of them. This page works that way."
      />
      <div className="wrap token">
        <div className="token__controls">
          <div className="token__k">
            <span>Pick a radius</span>
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
          className="token__plate"
          sheetClass="token__stage"
          bar={
            <>
              <span className="bar__name">
                <span className="glyphmark" aria-hidden>
                  ▢
                </span>
                Invite dialog <span className="dim">· every corner reads --round</span>
              </span>
            </>
          }
        >
          <div className="app" role="group" aria-label="Example product panel">
            <div className="app__top">
              <span className="app__ws" aria-hidden>
                NS
              </span>
              <div>
                <p className="app__t">Invite people to Northwind Studio</p>
                <p className="app__s">They&rsquo;ll join 14 members on the Pro plan</p>
              </div>
              <span className="app__x" aria-hidden>
                Esc
              </span>
            </div>
            <div className="app__field">
              <span className="app__lbl">Email addresses</span>
              <div className="app__input">
                <span className="tag">mira.okafor@northwind.studio</span>
                <span className="tag">theo@lindqvist.se</span>
                <span className="tag tag--warn">jun.park@northwind</span>
                <span className="caret" aria-hidden />
              </div>
              <span className="app__hint">jun.park@northwind needs a domain ending, like .studio</span>
            </div>
            <div className="app__row">
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
              <div className="app__field">
                <span className="app__lbl">Seats after invite</span>
                <p className="app__big">
                  16 <span>of 20</span>
                </p>
              </div>
            </div>
            <button type="button" className="switch" role="switch" aria-checked={publish} onClick={() => setPublish((p) => !p)}>
              <span className="switch__t">
                Can publish to production
                <small>Admins can change this later in Settings → Roles</small>
              </span>
              <span className="switch__k" aria-hidden>
                <i />
              </span>
            </button>
            <div className="app__foot">
              <span className="app__link">Copy invite link</span>
              <div className="app__btns">
                <span className="btn btn--soft btn--sm">Cancel</span>
                <span className="btn btn--solid btn--sm">Send 2 invites</span>
              </div>
            </div>
          </div>
          <div className="toast" aria-hidden>
            <span className="toast__dot" />
            Invites sent to Mira and Theo
            <span className="toast__undo">Undo</span>
          </div>
        </Plate>
      </div>
    </section>
  );
}
