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
import { TICKER } from "@/data/site";

export default function Home() {
  return (
    <div className="page">
      <a className="skip" href="#main">
        Skip to content
      </a>
      <Header />
      <main id="main">
        <Hero />
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
