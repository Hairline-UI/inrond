"use client";

import { useEffect, useRef, useState } from "react";
import { DOWNLOAD, REPO, VERSION } from "@/data/site";
import { Dial, DialValue } from "@/components/Dial";
import { Arrow, ThemeToggle } from "@/components/Kit";
import { Thumb } from "@/components/Thumb";

const NAV = [
  ["No reflow", "reflow"],
  ["One token", "token"],
  ["Coverage", "coverage"],
  ["The rule", "rule"],
  ["Compare", "compare"],
  ["Size", "size"],
  ["Use it", "use"],
] as const;

/** Marks the nav link of the section in the middle of the screen (aria-current), without React state. */
function useSpy(nav: React.RefObject<HTMLElement | null>) {
  useEffect(() => {
    const links = nav.current?.querySelectorAll<HTMLAnchorElement>("a[data-id]");
    if (!links?.length) return;
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (!e.isIntersecting) continue;
          links.forEach((a) => a.setAttribute("aria-current", String(a.dataset.id === e.target.id)));
        }
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    NAV.forEach(([, id]) => {
      const s = document.getElementById(id);
      if (s) io.observe(s);
    });
    const hero = document.querySelector(".hero");
    const clear = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) links.forEach((a) => a.setAttribute("aria-current", "false"));
    }, { rootMargin: "-45% 0px -50% 0px" });
    if (hero) clear.observe(hero);
    return () => {
      io.disconnect();
      clear.disconnect();
    };
  }, [nav]);
}

export function Header() {
  const [open, setOpen] = useState(false);
  const nav = useRef<HTMLElement>(null);
  const button = useRef<HTMLButtonElement>(null);
  const first = useRef<HTMLAnchorElement>(null);
  useSpy(nav);

  useEffect(() => {
    if (!open) return;
    const root = document.documentElement;
    root.classList.add("is-locked");
    first.current?.focus({ preventScroll: true });
    const k = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    addEventListener("keydown", k);
    return () => {
      root.classList.remove("is-locked");
      removeEventListener("keydown", k);
      button.current?.focus({ preventScroll: true });
    };
  }, [open]);

  return (
    <>
      <header className="top">
        <div className="wrap top__bar">
          <a href="#" className="mark" aria-label="Inrond, back to top">
            <span className="mark__node" aria-hidden />
            Inrond
          </a>
          <nav className="top__nav" aria-label="Sections" ref={nav}>
            <Thumb />
            {NAV.map(([n, id]) => (
              <a key={id} href={`#${id}`} data-id={id} aria-current="false">
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
            <a className="btn btn--solid btn--sm top__dl" href={DOWNLOAD} data-oa-event="download" data-oa-prop-location="header">
              Download
            </a>
            <button
              ref={button}
              type="button"
              className={open ? "burger is-open" : "burger"}
              aria-expanded={open}
              aria-controls="menu"
              aria-label={open ? "Close menu" : "Open menu"}
              onClick={() => setOpen((o) => !o)}
            >
              <i />
              <i />
            </button>
          </div>
        </div>
      </header>

      <div id="menu" className={open ? "menu is-open" : "menu"} aria-hidden={!open} inert={!open}>
        <button type="button" className="menu__scrim" aria-label="Close menu" tabIndex={-1} onClick={() => setOpen(false)} />
        <div className="menu__panel plate" role="dialog" aria-modal="true" aria-label="Menu">
          <nav className="sheet menu__nav" aria-label="Sections">
            {NAV.map(([n, id], i) => (
              <a key={id} ref={i === 0 ? first : undefined} href={`#${id}`} onClick={() => setOpen(false)} style={{ ["--i" as string]: i }}>
                <span className="mono menu__n">{String(i + 1).padStart(2, "0")}</span>
                <span className="menu__t">{n}</span>
                <Arrow dir="right" />
              </a>
            ))}
          </nav>
          <div className="menu__dial">
            <div className="menu__dialhead">
              <span>Roundness of this page</span>
              <span className="mono">
                ROND <DialValue />
              </span>
            </div>
            <Dial id="dial-menu" compact label="Roundness for the whole page" />
          </div>
          <div className="menu__foot">
            <a className="btn btn--solid" href={DOWNLOAD} data-oa-event="download" data-oa-prop-location="menu">
              Download {VERSION}
              <span className="btn__dot">
                <Arrow dir="down" />
              </span>
            </a>
            <a className="btn btn--soft" href={REPO} data-oa-event="github" data-oa-prop-location="menu">
              GitHub
            </a>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </>
  );
}
