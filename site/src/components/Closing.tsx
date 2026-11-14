"use client";

import { useRef } from "react";
import { CDN, DOWNLOAD, HAIRLINE, INTER, REPO, VERSION } from "@/data/site";
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
            <a className="btn btn--solid" href={DOWNLOAD} data-oa-event="download" data-oa-prop-location="closing">
              Download {VERSION}
              <span className="btn__dot">
                <Arrow dir="down" />
              </span>
            </a>
            <a className="btn btn--soft" href={REPO} data-oa-event="github" data-oa-prop-location="closing">
              GitHub
            </a>
          </div>
          <div className="cdn">
            <span className="cdn__k mono">$</span>
            <code className="mono">cdn.jsdelivr.net/gh/Hairline-UI/inrond@v1.0</code>
            <CopyButton text={`<link rel="stylesheet" href="${CDN}/inrond.css">`} label="Copy the stylesheet link tag" track="cdn-link" />
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
          <a href={REPO} data-oa-event="github" data-oa-prop-location="footer">
            Repository
          </a>
          <a href={DOWNLOAD} data-oa-event="download" data-oa-prop-location="footer">
            Releases
          </a>
          <a href={`${REPO}/issues`}>Issues</a>
          <a href={`${REPO}/tree/main/qa`}>Test reports</a>
        </nav>
      </footer>
      <div className="wrap footbar">
        <a
          className="maker"
          href={HAIRLINE}
          aria-label="Inrond is made by Hairline UI, visit hairlineui.com"
          data-oa-event="hairline_ui"
          data-oa-prop-location="footer"
        >
          <span>Inrond is made by</span>
          <svg className="maker__mark" viewBox="0 0 64 64" width="22" height="22" aria-hidden>
            <path className="maker__bg" d="M32 1.5c13.6 0 21.4 0 25.9 4.6 4.6 4.5 4.6 12.3 4.6 25.9s0 21.4-4.6 25.9c-4.5 4.6-12.3 4.6-25.9 4.6s-21.4 0-25.9-4.6C1.5 53.4 1.5 45.6 1.5 32S1.5 10.6 6.1 6.1C10.6 1.5 18.4 1.5 32 1.5Z" />
            <path className="maker__tile" d="M16.5 7.5H21.2Q22.4 7.5 22.4 8.7V55.3Q22.4 56.5 21.2 56.5H16.5Q7.5 56.5 7.5 47.5V16.5Q7.5 7.5 16.5 7.5ZM42.8 7.5H47.5Q56.5 7.5 56.5 16.5V47.5Q56.5 56.5 47.5 56.5H42.8Q41.6 56.5 41.6 55.3V8.7Q41.6 7.5 42.8 7.5ZM26.2 7.5H37.8Q39 7.5 39 8.7V29.5Q39 30.7 37.8 30.7H26.2Q25 30.7 25 29.5V8.7Q25 7.5 26.2 7.5ZM26.2 33.3H37.8Q39 33.3 39 34.5V55.3Q39 56.5 37.8 56.5H26.2Q25 56.5 25 55.3V34.5Q25 33.3 26.2 33.3Z" />
          </svg>
          <strong>Hairline UI</strong>
          <Arrow dir="up-right" />
        </a>
        <span className="footbar__c">© 2026 Hairline UI</span>
      </div>
    </section>
  );
}
