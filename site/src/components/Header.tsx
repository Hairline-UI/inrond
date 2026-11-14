"use client";

import { useEffect, useState } from "react";
import { DOWNLOAD, REPO } from "@/data/site";
import { Dial, DialValue } from "@/components/Dial";
import { ThemeToggle } from "@/components/Kit";

const NAV = [
  ["No reflow", "#reflow"],
  ["One token", "#token"],
  ["Coverage", "#coverage"],
  ["The rule", "#rule"],
  ["Compare", "#compare"],
  ["Size", "#size"],
  ["Use it", "#use"],
] as const;

export function Header() {
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (!open) return;
    const k = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    addEventListener("keydown", k);
    return () => removeEventListener("keydown", k);
  }, [open]);

  return (
    <header className={open ? "top top--open" : "top"}>
      <div className="wrap top__bar">
        <a href="#" className="mark" aria-label="Inrond, back to top">
          <span className="mark__node" aria-hidden />
          Inrond
        </a>
        <nav className="top__nav" aria-label="Sections">
          {NAV.map(([n, h]) => (
            <a key={h} href={h}>
              {n}
            </a>
          ))}
        </nav>
        <div className="top__end">
          <div className="top__dial">
            <span className="mono top__lbl">ROND</span>
            <Dial id="dial-top" compact label="Roundness for the whole page" />
            <span className="mono top__val">
              <DialValue />
            </span>
          </div>
          <ThemeToggle />
          <a className="btn btn--solid btn--sm top__dl" href={DOWNLOAD}>
            Download
          </a>
          <button
            type="button"
            className="btn btn--soft btn--sm top__menu"
            aria-expanded={open}
            aria-controls="menu"
            onClick={() => setOpen((o) => !o)}
          >
            {open ? "Close" : "Menu"}
          </button>
        </div>
      </div>
      <div id="menu" className="menu" hidden={!open}>
        <div className="wrap">
          <nav aria-label="Sections">
            {NAV.map(([n, h], i) => (
              <a key={h} href={h} onClick={() => setOpen(false)}>
                <span className="mono dim">{String(i + 1).padStart(2, "0")}</span>
                {n}
              </a>
            ))}
            <a href={REPO} onClick={() => setOpen(false)}>
              <span className="mono dim">↗</span>
              GitHub
            </a>
          </nav>
          <div className="menu__dial">
            <span className="mono dim">
              ROND <DialValue />
            </span>
            <Dial id="dial-menu" compact label="Roundness for the whole page" />
          </div>
        </div>
      </div>
    </header>
  );
}
