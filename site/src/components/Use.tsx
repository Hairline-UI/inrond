"use client";

import { useState } from "react";
import { CDN, DOWNLOAD, REPO } from "@/data/site";
import { Head } from "@/components/Frame";
import { CodePanel } from "@/components/Kit";

const STEPS = [
  {
    t: "Load it",
    d: "Unicode-range subsets, so a Latin page fetches only the Latin file. Or download the release and host the same files yourself.",
    file: { name: "index.html", label: "index.html", code: `<link\n  rel="stylesheet"\n  href="${CDN}/inrond.css"\n/>` },
  },
  {
    t: "Use it like Inter",
    d: "Same weights, the same optical size axis and the same 39 features. At ROND 0 it renders as Inter, outline for outline.",
    file: {
      name: "base.css",
      label: "base.css",
      code: `body {\n  font-family: "Inrond", "Inter", sans-serif;\n  font-optical-sizing: auto;\n}\n\nh1 { font-weight: 720; }`,
    },
  },
  {
    t: "Turn the axis",
    d: "Per element, per theme or animated. font-variation-settings transitions smoothly and never reflows.",
    file: {
      name: "button.css",
      label: "button.css",
      code: `.button {\n  font-variation-settings: "ROND" 100;\n  transition: font-variation-settings 0.3s;\n}\n\n.button:hover {\n  font-variation-settings: "ROND" 40;\n}`,
    },
  },
];

export function Use() {
  const [step, setStep] = useState(0);
  return (
    <section id="use" className="sec" aria-labelledby="use-title">
      <Head
        label="Use it"
        id="use-title"
        title={
          <>
            Three steps of CSS. <span className="mute">Nothing to build.</span>
          </>
        }
        text="The release has the variable fonts with the axis, frozen Round and Soft builds, web subsets and 36 static fonts. Everything is under the SIL Open Font License: use it in any project, commercial included, and redistribute it freely."
      />
      <div className="wrap use">
        <ol className="steps">
          {STEPS.map((s, i) => (
            <li key={s.t}>
              <button type="button" className="step" aria-pressed={step === i} onClick={() => setStep(i)}>
                <span className="step__n mono">{String(i + 1).padStart(2, "0")}</span>
                <span className="step__t">{s.t}</span>
                <span className="step__d">{s.d}</span>
              </button>
            </li>
          ))}
        </ol>
        <div className="use__code">
          <CodePanel files={STEPS.map((s) => s.file)} active={step} onPick={setStep} />
          <div className="extras">
            <div className="extra">
              <span className="extra__k">One roundness only</span>
              <span className="extra__v">
                <code className="mono">inrond-round.css</code> (100) or <code className="mono">inrond-soft.css</code> (50)
              </span>
            </div>
            <div className="extra">
              <span className="extra__k">Any other value</span>
              <span className="extra__v">
                <code className="mono">python scripts/pin.py 60</code>
              </span>
            </div>
            <a className="extra extra--link" href={DOWNLOAD}>
              <span className="extra__k">Desktop apps</span>
              <span className="extra__v">Variable and static TTFs in the release</span>
            </a>
            <a className="extra extra--link" href={REPO}>
              <span className="extra__k">Source</span>
              <span className="extra__v">The generator and tests on GitHub</span>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
