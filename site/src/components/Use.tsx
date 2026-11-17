"use client";

import { useState } from "react";
import { CDN, DOWNLOAD, REPO } from "@/data/site";
import { Head } from "@/components/Frame";
import { CodePanel } from "@/components/Kit";
import { Thumb } from "@/components/Thumb";

const STEPS = [
  {
    t: "Load it",
    d: "One stylesheet. Each page downloads only the alphabets it uses. Or download the files and host them yourself.",
    file: { name: "index.html", label: "index.html", code: `<link\n  rel="stylesheet"\n  href="${CDN}/inrond.css"\n/>` },
  },
  {
    t: "Use it like Inter",
    d: "Same weights, same features, same spacing. At roundness 0 it is Inter.",
    file: {
      name: "base.css",
      label: "base.css",
      code: `body {\n  font-family: "Inrond", "Inter", sans-serif;\n  font-optical-sizing: auto;\n}\n\nh1 { font-weight: 720; }`,
    },
  },
  {
    t: "Round it",
    d: "Per element, per theme, or animated on hover. Text never re-wraps.",
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
            On your site in three steps. <span className="mute">No build step, no package.</span>
          </>
        }
        text="Free under the SIL Open Font License, for any project, commercial included. The download also has fixed Round and Soft versions and regular font files for desktop apps."
      />
      <div className="wrap grid sec-body">
        <div className="span-main use__code">
          <CodePanel files={STEPS.map((s) => s.file)} active={step} onPick={setStep} />
        </div>
        <div className="span-side steps" role="group" aria-label="Steps">
          <Thumb />
          {STEPS.map((s, i) => (
            <button key={s.t} type="button" className="step" aria-pressed={step === i} onClick={() => setStep(i)}>
              <span className="step__n mono">{String(i + 1).padStart(2, "0")}</span>
              <span className="step__t">{s.t}</span>
              <span className="step__d">{s.d}</span>
            </button>
          ))}
        </div>
        <div className="span-full extras">
          <div className="span-3 extra">
            <span className="extra__k">One roundness only</span>
            <span className="extra__v">Use the Round or Soft file</span>
          </div>
          <a className="span-3 extra extra--link" href={`${REPO}#one-roundness-only`} data-oa-event="github" data-oa-prop-location="use_pin">
            <span className="extra__k">Another fixed value</span>
            <span className="extra__v">Make your own</span>
          </a>
          <a className="span-3 extra extra--link" href={DOWNLOAD} data-oa-event="download" data-oa-prop-location="use_desktop">
            <span className="extra__k">Desktop apps</span>
            <span className="extra__v">Install the font files</span>
          </a>
          <a className="span-3 extra extra--link" href={REPO} data-oa-event="github" data-oa-prop-location="use_source">
            <span className="extra__k">Source</span>
            <span className="extra__v">See how it is made</span>
          </a>
        </div>
      </div>
    </section>
  );
}
