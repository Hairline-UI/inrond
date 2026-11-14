"use client";

import { useRef } from "react";
import { CDN, DOWNLOAD, INTER, REPO, VERSION } from "@/data/site";
import { useDial } from "@/lib/dial";
import { Arrow, CopyButton } from "@/components/Kit";
import { DialValue } from "@/components/Dial";

const WORD = "Inrond".split("");

export function Closing() {
  const row = useRef<HTMLDivElement>(null);
  useDial((v) => {
    const k = Math.round(v / 20);
    row.current?.querySelectorAll(".wordmark__l").forEach((el, i) => el.classList.toggle("is-here", i === k));
  });
  return (
    <section className="sec end" aria-labelledby="end-title">
      <div className="wrap end__head">
        <h2 id="end-title" className="h2">
          The whole axis, <span className="mute">in one word.</span>
        </h2>
        <div className="end__cta">
          <div className="end__btns">
            <a className="btn btn--solid" href={DOWNLOAD}>
              Download {VERSION}
              <span className="btn__dot">
                <Arrow dir="down" />
              </span>
            </a>
            <a className="btn btn--soft" href={REPO}>
              GitHub
            </a>
          </div>
          <div className="cdn">
            <span className="cdn__k mono">$</span>
            <code className="mono">cdn.jsdelivr.net/gh/Hairline-UI/inrond@v1.0</code>
            <CopyButton text={`<link rel="stylesheet" href="${CDN}/inrond.css">`} label="Copy the stylesheet link tag" />
          </div>
        </div>
      </div>
      <div className="wordmark" aria-label="Inrond, set at ROND 0, 20, 40, 60, 80 and 100">
        <div className="wrap wordmark__row" ref={row} aria-hidden>
          {WORD.map((c, i) => (
            <span key={i} className="wordmark__l" style={{ fontVariationSettings: `"ROND" ${i * 20}` }}>
              {c}
              <b className="mono">{i * 20}</b>
            </span>
          ))}
        </div>
      </div>
      <footer className="wrap colophon">
        <div className="colophon__cell">
          <p className="side__k">Colophon</p>
          <p>
            This page is set in Inrond {VERSION} at the roundness you chose, now <DialValue className="mono" />. Figures and
            code are in Geist Mono.
          </p>
        </div>
        <div className="colophon__cell">
          <p className="side__k">Credit</p>
          <p>
            Inrond is derived from <a href={INTER}>Inter</a> by Rasmus Andersson and the Inter Project Authors. It is not affiliated
            with or endorsed by the Inter project. &ldquo;Inter&rdquo; is a trademark of rsms.
          </p>
        </div>
        <div className="colophon__cell">
          <p className="side__k">Licence</p>
          <p>
            Fonts: <a href={`${REPO}/blob/main/OFL.txt`}>SIL Open Font License 1.1</a>. Free to use, modify and redistribute; not
            to be sold by itself.
          </p>
        </div>
        <nav className="colophon__cell colophon__links" aria-label="Links">
          <p className="side__k">Links</p>
          <a href={REPO}>Repository</a>
          <a href={DOWNLOAD}>Releases</a>
          <a href={`${REPO}/issues`}>Issues</a>
          <a href={`${REPO}/tree/main/qa`}>Test reports</a>
        </nav>
      </footer>
    </section>
  );
}
