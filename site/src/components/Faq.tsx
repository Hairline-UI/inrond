const QA: [string, string][] = [
  [
    "Google Sans Flex already has a roundness axis. Why this?",
    "It does, and it is a fine font: hand-designed, with width, slant and a wide optical size range, and a more compact roundness axis. Pick Inrond if you want Inter itself, need Cyrillic or Greek (the measured Google Sans Flex file covers Latin only), or want a drawn italic instead of a slant.",
  ],
  [
    "Isn’t it just Inter?",
    "At ROND 0, yes, outline for outline; that is the point. The design is Inter’s, by Rasmus Andersson. Inrond adds the axis, the rule behind it and the tests that hold it to Inter.",
  ],
  [
    "It’s more than twice the size of Inter.",
    "With the axis live, yes: 257 KB of Latin against 103. If you need one roundness, the frozen Round and Soft builds are about 1.6 times Inter, and scripts/pin.py freezes any other value.",
  ],
  [
    "Was it drawn or tuned by hand?",
    "No. Every outline comes from one rule applied by a script, and a test suite checks every glyph against Inter. A type designer would probably adjust a few heavy weights by eye; we would rather show you the measurements than claim craftsmanship.",
  ],
  [
    "Can I use it in commercial work?",
    "Yes. It is under the SIL Open Font License 1.1: use it, embed it, modify it and redistribute it. The one thing the licence forbids is selling the font by itself.",
  ],
  [
    "Is it hinted?",
    "No, like Inter’s variable fonts. It renders well on modern screens; very small text on old Windows displays may look softer than a hinted static font.",
  ],
];

export function Faq() {
  return (
    <section id="faq" className="sec" aria-labelledby="faq-title">
      <div className="wrap faq">
        <div className="faq__title">
          <p className="label">Questions</p>
          <h2 id="faq-title" className="h2">
            Questions people ask, <span className="mute">answered plainly.</span>
          </h2>
          <p className="dim">Anything else goes to the issue tracker on GitHub, where the answers stay public.</p>
        </div>
        <dl className="faq__list">
          {QA.map(([q, a]) => (
            <div key={q} className="qa">
              <dt>{q}</dt>
              <dd>{a}</dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
