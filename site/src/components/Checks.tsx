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
            Checked against Inter, <span className="mute">letter by letter.</span>
          </>
        }
        text="Every letter is drawn and compared with Inter, pixel by pixel, at seven weights and sizes and four roundness settings. Roman and italic both pass all six checks."
      />
      <div className="wrap grid sec-body" ref={stage}>
        <div className="span-full plate report" ref={sheet}>
          <div className="plate__bar">
            <span className="bar__name">
              <FileMark name="verify.py" />
              Test report <span className="dim">· every letter, both styles</span>
            </span>
            <span className="report__meta mono">
              <span>2,915 roman · 2,879 italic</span>
              <span className="chip chip--on">6 of 6 pass</span>
            </span>
          </div>
          <div className="sheet report__sheet">
          <table>
            <thead>
              <tr>
                <th scope="col">Check</th>
                <th scope="col">What it means</th>
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
            <p className="report__ok">All six checks pass, in roman and italic.</p>
            <p className="dim">
              FontBakery, the standard font checker, flags 3 small issues. All three come from Inter itself (it flags 6 in
              Inter) and are left alone so Inrond stays a drop-in. <a href={`${REPO}/tree/main/qa`}>Read the full reports</a>
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
