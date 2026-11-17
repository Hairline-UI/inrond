"use client";

import { useEffect, useRef } from "react";

const SELECTED = '[aria-pressed="true"],[aria-checked="true"],[aria-selected="true"],[aria-current="true"]';

/**
 * The white chip of a segmented tray or tab row. Place it as the first child of the row; it finds the chosen item
 * (aria-pressed / checked / selected / current) and glides to it. It does not move the first time, and it does not
 * glide at all under reduced motion (the CSS drops the transition).
 */
export function Thumb() {
  const el = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    const thumb = el.current;
    const row = thumb?.parentElement;
    if (!thumb || !row) return;
    let placed = false;
    const place = () => {
      const on = row.querySelector<HTMLElement>(SELECTED);
      if (!on) {
        thumb.style.opacity = "0";
        return;
      }
      thumb.style.setProperty("--tx", `${on.offsetLeft}px`);
      thumb.style.setProperty("--ty", `${on.offsetTop}px`);
      thumb.style.setProperty("--tw", `${on.offsetWidth}px`);
      thumb.style.setProperty("--th", `${on.offsetHeight}px`);
      thumb.style.opacity = "1";
      if (!placed) {
        placed = true;
        requestAnimationFrame(() => thumb.classList.add("is-live"));
      }
    };
    place();
    const mo = new MutationObserver(place);
    mo.observe(row, { subtree: true, attributes: true, attributeFilter: ["aria-pressed", "aria-checked", "aria-selected", "aria-current"] });
    const ro = new ResizeObserver(place);
    ro.observe(row);
    document.fonts?.ready.then(place);
    return () => {
      mo.disconnect();
      ro.disconnect();
    };
  }, []);
  return <span ref={el} className="thumb" aria-hidden />;
}
