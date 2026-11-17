"use client";

import { useRef } from "react";
import { CHECKS, REPO } from "@/data/site";
import { useOnce } from "@/lib/dial";
import { Head } from "@/components/Frame";
import { FileMark } from "@/components/Kit";

export function Checks() {
  const sheet = useRef<HTMLDivElement>(null);
  const stage = useOnce(() => sheet.current?.classList.add("is-run"), 0.3);
  return (
    <section id="checks" className="sec" aria-labelledby="checks-title">
      <Head
        label="Tests"
        id="checks-title"
        title={
          <>
            Checked against Inter, <span className="mute">glyph by glyph.</span>
          </>
        }
        text="A test suite rasterises every glyph with FreeType at 1,024 pixels per em and compares it with Inter at seven weight and optical size locations, at roundness 0, 35, 70 and 100. Both styles pass all six checks."
      />
      <div className="wrap report-wrap" ref={stage}>
        <div className="plate report" ref={sheet}>
          <div className="plate__bar">
            <span className="bar__name mono">
              <FileMark name="verify.py" />
              tests/verify.py
            </span>
            <span className="report__meta mono">
              <span>2,915 roman · 2,879 italic glyphs</span>
              <span className="chip chip--on">6 of 6 pass</span>
            </span>
          </div>
          <div className="sheet report__sheet">
          <table>
            <thead>
              <tr>
                <th scope="col">Check</th>
                <th scope="col">What it proves</th>
                <th scope="col">Fails at</th>
                <th scope="col">Roman</th>
                <th scope="col">Italic</th>
                <th scope="col">
                  <span className="sr">Result</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {CHECKS.map((c, i) => (
                <tr key={c.name} style={{ ["--i" as string]: i }}>
                  <th scope="row">
                    <span className="mono dim">{i + 1}</span> {c.name}
                  </th>
                  <td>{c.rule}</td>
                  <td className="dim">{c.limit}</td>
                  <td className="mono">{c.roman}</td>
                  <td className="mono">{c.italic}</td>
                  <td>
                    <span className="pass">
                      <svg viewBox="0 0 16 16" width="15" height="15" aria-hidden>
                        <circle cx="8" cy="8" r="7" />
                        <path d="M5 8.2 7 10.2 11 6" />
                      </svg>
                      Pass
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
          <div className="report__end">
            <p className="report__ok">All checks passed, roman and italic.</p>
            <p className="dim">
              Below the limits, reported and not hidden: round stroke ends pass Inter&rsquo;s outline by up to 24 units, as far as
              Inter&rsquo;s own o passes the baseline; the median glyph loses 1.0% of its ink at ROND 100. FontBakery&rsquo;s universal profile: 3 fails, all inherited from
              Inter and kept on purpose, against Inter&rsquo;s 6.{" "}
              <a href={`${REPO}/tree/main/qa`}>Read the reports</a>
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
