import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { Reflow } from "@/components/Reflow";
import { Token } from "@/components/Token";
import { Sheet } from "@/components/Sheet";
import { Rule } from "@/components/Rule";
import { Checks } from "@/components/Checks";
import { Compare } from "@/components/Compare";
import { Size } from "@/components/Size";
import { Use } from "@/components/Use";
import { Tester } from "@/components/Tester";
import { Faq } from "@/components/Faq";
import { Closing } from "@/components/Closing";
import { REPO_API, TICKER } from "@/data/site";

// The star count at build time; the button refreshes it in the browser.
async function getStars(): Promise<number | null> {
  try {
    const r = await fetch(REPO_API, { headers: { Accept: "application/vnd.github+json" }, cache: "force-cache" });
    if (!r.ok) return null;
    const j = await r.json();
    return typeof j.stargazers_count === "number" ? j.stargazers_count : null;
  } catch {
    return null;
  }
}

export default async function Home() {
  const stars = await getStars();
  return (
    <div className="page">
      <a className="skip" href="#main">
        Skip to content
      </a>
      <Header />
      <main id="main">
        <Hero stars={stars} />
        <div className="sec ticker" aria-label="What is in the font">
          <ul className="wrap ticker__row">
            {TICKER.map(([v, k]) => (
              <li key={k}>
                <span className="mono">{v}</span> {k}
              </li>
            ))}
          </ul>
        </div>
        <Reflow />
        <Token />
        <Sheet />
        <Rule />
        <Checks />
        <Compare />
        <Size />
        <Use />
        <Tester />
        <Faq />
        <Closing />
      </main>
    </div>
  );
}
