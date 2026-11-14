"use client";

import { useState } from "react";
import { Dial, DialValue } from "@/components/Dial";
import { Head } from "@/components/Frame";
import { Plate } from "@/components/Kit";

const SAMPLES: Record<string, string> = {
  Latin: "Quick wafting zephyrs vex bold Jim, 0123456789.",
  Cyrillic: "Съешь же ещё этих мягких французских булок.",
  Greek: "Ξεσκεπάζω την ψυχοφθόρα βδελυγμία.",
  Vietnamese: "Tiếng Việt có dấu, rõ ràng ở mọi cỡ chữ.",
};

export function Tester() {
  const [wght, setWght] = useState(560);
  const [size, setSize] = useState(88);
  const [italic, setItalic] = useState(false);
  const [script, setScript] = useState("Latin");
  return (
    <section id="tester" className="sec" aria-labelledby="tester-title">
      <Head
        label="Tester"
        id="tester-title"
        title={
          <>
            Type your own words. <span className="mute">In four scripts.</span>
          </>
        }
        text="Every control drives the real font files this page loaded. The roundness here is the page's dial, so the page follows too."
      />
      <div className="wrap">
        <Plate
          className="tester"
          sheetClass="tester__sheet"
          bar={
            <>
              <div className="seg" role="radiogroup" aria-label="Script">
                {Object.keys(SAMPLES).map((s) => (
                  <button key={s} type="button" className="seg__b" role="radio" aria-checked={script === s} onClick={() => setScript(s)}>
                    {s}
                  </button>
                ))}
              </div>
              <div className="seg" role="radiogroup" aria-label="Style">
                {["Roman", "Italic"].map((s) => (
                  <button
                    key={s}
                    type="button"
                    className="seg__b"
                    role="radio"
                    aria-checked={(s === "Italic") === italic}
                    onClick={() => setItalic(s === "Italic")}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </>
          }
          foot={
            <div className="tester__bar">
              <label className="tcell">
                <span className="tcell__k">
                  Weight <span className="mono">{wght}</span>
                </span>
                <input className="range" type="range" min={100} max={900} step={10} value={wght} onChange={(e) => setWght(+e.target.value)} />
              </label>
              <label className="tcell">
                <span className="tcell__k">
                  Size <span className="mono">{size}px</span>
                </span>
                <input className="range" type="range" min={20} max={180} step={1} value={size} onChange={(e) => setSize(+e.target.value)} />
              </label>
              <div className="tcell">
                <span className="tcell__k">
                  Roundness <DialValue className="mono" />
                </span>
                <Dial id="dial-tester" compact label="Roundness" />
              </div>
            </div>
          }
        >
          <div
            key={script}
            className="tester__text"
            contentEditable
            suppressContentEditableWarning
            spellCheck={false}
            aria-label="Editable sample text"
            role="textbox"
            aria-multiline
            style={{ fontWeight: wght, ["--ts" as string]: `${size}px`, fontSize: "var(--ts)", fontStyle: italic ? "italic" : "normal" }}
          >
            {SAMPLES[script]}
          </div>
        </Plate>
      </div>
    </section>
  );
}
