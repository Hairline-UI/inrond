"use client";

import { useState } from "react";
import { COMPARE } from "@/data/site";
import { Head } from "@/components/Frame";
import { Plate } from "@/components/Kit";
import { Thumb } from "@/components/Thumb";

export function Compare() {
  const [rival, setRival] = useState(2);
  return (
    <section id="compare" className="sec" aria-labelledby="compare-title">
      <Head
        label="Compare"
        id="compare-title"
        title={
          <>
            How it compares <span className="mute">with the fonts you’d pick instead.</span>
          </>
        }
        text="Google Sans Flex has a roundness axis too, hand-designed, with far more axes and a more compact build. Inrond is for teams that want Inter specifically, or need Cyrillic, Greek and a drawn italic. Every figure here is read from the font files."
      />
      <div className="wrap compare" style={{ ["--rival" as string]: rival + 2 }}>
        <Plate
          className="cmp"
          bar={
            <>
              <span className="bar__name">
                <span className="glyphmark" aria-hidden>
                  ≡
                </span>
                Read from the font files
              </span>
              <div className="seg rivals" role="radiogroup" aria-label="Compare Inrond with">
                <Thumb />
                {COMPARE.head.slice(1).map((h, i) => (
                  <button key={h} type="button" className="seg__b" role="radio" aria-checked={rival === i + 1} onClick={() => setRival(i + 1)}>
                    {h}
                  </button>
                ))}
              </div>
            </>
          }
        >
        <div className="table-scroll">
          <table className="ctable">
            <thead>
              <tr>
                <td />
                {COMPARE.head.map((h, i) => (
                  <th key={h} scope="col" className={i === 0 ? "us" : i === rival ? "is-rival" : ""}>
                    {i === 0 ? <span className="chip chip--ink">{h}</span> : h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {COMPARE.rows.map(([k, ...cells]) => (
                <tr key={k}>
                  <th scope="row">{k}</th>
                  {cells.map((c, i) => (
                    <td key={i} className={i === 0 ? "us" : i === rival ? "is-rival" : ""}>
                      {c}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        </Plate>
        <p className="fine compare__note">
          Open Runde and Intern figures are from an earlier measurement session; Inrond, Inter and Google Sans Flex were re-measured
          for this release. Not compared: Goeist, which rounds Geist rather than Inter.
        </p>
      </div>
    </section>
  );
}
