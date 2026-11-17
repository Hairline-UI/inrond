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
        text="Google Sans Flex also has a roundness axis, with more axes and smaller files. Pick Inrond if you want Inter itself, or need Cyrillic, Greek and a real italic."
      />
      <div className="wrap grid sec-body" style={{ ["--rival" as string]: rival + 2 }}>
        <Plate
          className="span-full cmp"
          foot={<p className="fine compare__note">Goeist is left out: it rounds Geist, not Inter.</p>}
          bar={
            <>
              <span className="bar__name">
                <span className="glyphmark" aria-hidden>
                  ≡
                </span>
                Side by side <span className="dim">· read from each font&rsquo;s files</span>
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
      </div>
    </section>
  );
}
