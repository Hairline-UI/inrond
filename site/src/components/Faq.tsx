import { Head } from "@/components/Frame";

const QA: [string, string][] = [
  [
    "Google Sans Flex already has a roundness axis. Why this?",
    "It does, and it is a fine font, with more axes and smaller files. Pick Inrond if you want Inter itself, need Cyrillic or Greek (Google Sans Flex covers Latin only), or want a real italic rather than slanted letters.",
  ],
  [
    "Isn’t it just Inter?",
    "At roundness 0, yes, letter for letter; that is the point. The design is Inter’s, by Rasmus Andersson. Inrond adds the roundness and the tests that keep it true to Inter.",
  ],
  [
    "It’s more than twice the size of Inter.",
    "With adjustable roundness, yes: 257 KB for English against Inter’s 103. If your site uses one roundness, the fixed Round and Soft files are about 1.6 times Inter.",
  ],
  [
    "Was it drawn by hand?",
    "No. A script rounds every letter by the same rules, and tests check every letter against Inter. A type designer might fine-tune a few heavy weights by eye; we would rather show you what we checked than claim handcraft.",
  ],
  [
    "Can I use it in commercial work?",
    "Yes. It is under the SIL Open Font License: use it, embed it, change it and share it. The only thing you cannot do is sell the font on its own.",
  ],
  [
    "Is it hinted?",
    "No, like Inter’s variable fonts. It looks right on modern screens; very small text on older Windows displays may look slightly softer than a hinted font.",
  ],
];

export function Faq() {
  return (
    <section id="faq" className="sec" aria-labelledby="faq-title">
      <Head
        label="Questions"
        id="faq-title"
        title={
          <>
            Questions people ask, <span className="mute">answered plainly.</span>
          </>
        }
        text="Anything else goes to the issue tracker on GitHub, where the answers stay public."
      />
      <div className="wrap grid sec-body">
        <dl className="span-full faq__list">
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
