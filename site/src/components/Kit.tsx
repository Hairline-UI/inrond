"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { Thumb } from "@/components/Thumb";

/* The page's small parts: the tray that holds a sheet, icons, the copy button, the code panel and the theme switch.
   Corners come from the dial (--rp tray, --rs sheet inside it, concentric). */

export function Plate({
  bar,
  foot,
  children,
  className = "",
  sheetClass = "",
  dark = false,
}: {
  bar?: ReactNode;
  foot?: ReactNode;
  children: ReactNode;
  className?: string;
  sheetClass?: string;
  dark?: boolean;
}) {
  return (
    <div className={`plate${dark ? " plate--dark" : ""} ${className}`}>
      {bar && <div className="plate__bar">{bar}</div>}
      <div className={`sheet ${sheetClass}`}>{children}</div>
      {foot && <div className="plate__foot">{foot}</div>}
    </div>
  );
}

export function CopyIcon({ done }: { done: boolean }) {
  return (
    <svg viewBox="0 0 20 20" width="16" height="16" aria-hidden className={done ? "copyicon is-done" : "copyicon"}>
      <rect className="copyicon__back" x="2.6" y="2.6" width="10.4" height="10.4" rx="3" />
      <rect className="copyicon__front" x="7" y="7" width="10.4" height="10.4" rx="3" />
      <path className="copyicon__check" d="M9.4 12.4 11.3 14.2 14.9 10" pathLength={1} />
    </svg>
  );
}

/** `track` names what is copied; it is sent to Open Analytics as the `copy_code` event's `file` property. */
export function CopyButton({ text, label, track }: { text: string; label: string; track: string }) {
  const [done, setDone] = useState(false);
  const t = useRef(0);
  useEffect(() => () => clearTimeout(t.current), []);
  return (
    <button
      type="button"
      className="iconbtn"
      aria-label={done ? "Copied" : label}
      data-oa-event="copy_code"
      data-oa-prop-file={track}
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(text);
          setDone(true);
          clearTimeout(t.current);
          t.current = window.setTimeout(() => setDone(false), 1600);
        } catch {}
      }}
    >
      <CopyIcon done={done} />
    </button>
  );
}

/** A small file mark: a folded sheet with the file's type under it. */
export function FileMark({ name }: { name: string }) {
  const ext = name.slice(name.lastIndexOf(".") + 1).toLowerCase();
  const tag = ext === "html" ? "<>" : ext === "css" ? "#" : ext === "py" ? "py" : ext === "sh" ? "$" : "·";
  return (
    <span className={`filemark filemark--${ext}`} aria-hidden>
      <span className="filemark__tag">{tag}</span>
    </span>
  );
}

/* Syntax colours (the one place on the page with hue, at the owner's request). */
type Tok = [kind: string, text: string];
const RULES: [string, RegExp][] = [
  ["comment", /^\/\*[\s\S]*?\*\/|^#.*$/],
  ["string", /^"[^"]*"|^'[^']*'/],
  ["tag", /^<\/?[a-zA-Z][\w-]*|^\/?>/],
  ["fn", /^[a-z-]+(?=\()/],
  ["attr", /^[a-z-]+(?==)/],
  ["key", /^[a-z-]+(?=\s*:)|^--[\w-]+/],
  ["num", /^-?\d*\.?\d+(px|ms|s|%|em|rem)?/],
  ["sel", /^[.:@]?[a-zA-Z][\w-]*(?=[^;"]*\{)/],
  ["punct", /^[{}();:,=*/]/],
  ["plain", /^[^\s"'<>{}();:,=*/.]+|^\s+|^./],
];
function tokenize(line: string): Tok[] {
  const out: Tok[] = [];
  let s = line;
  while (s.length) {
    for (const [k, re] of RULES) {
      const m = s.match(re);
      if (m && m[0].length) {
        out.push([k, m[0]]);
        s = s.slice(m[0].length);
        break;
      }
    }
  }
  return out;
}

export type CodeFile = { name: string; code: string; label?: string };

/** Code on a sheet inside a tray: file tabs (or one file's mark and name), line count, copy; line numbers. */
export function CodePanel({
  files,
  active = 0,
  onPick,
  live,
}: {
  files: CodeFile[];
  active?: number;
  onPick?: (i: number) => void;
  live?: ReactNode;
}) {
  const f = files[Math.min(active, files.length - 1)];
  const lines = f.code.split("\n");
  return (
    <figure className="plate code">
      <figcaption className="plate__bar code__bar">
        {files.length > 1 ? (
          <div className="tabs" role="tablist" aria-label="Files">
            <Thumb />
            {files.map((x, i) => (
              <button
                key={x.name + i}
                type="button"
                role="tab"
                aria-selected={i === active}
                className="tab"
                onClick={() => onPick?.(i)}
              >
                <FileMark name={x.name} />
                {x.label ?? x.name}
              </button>
            ))}
          </div>
        ) : (
          <span className="code__file">
            <FileMark name={f.name} />
            {f.name}
          </span>
        )}
        <span className="code__end">
          <span className="code__count">{lines.length} lines</span>
          <CopyButton text={f.code} label={`Copy ${f.name}`} track={f.name} />
        </span>
      </figcaption>
      <div className="sheet code__sheet">
        {live ?? (
          <pre className="code__pre" key={f.name + active}>
            <code>
              {lines.map((l, i) => (
                <span key={i} className="ln">
                  {tokenize(l).map(([k, t], j) => (
                    <span key={j} className={`t-${k}`}>
                      {t}
                    </span>
                  ))}
                  {"\n"}
                </span>
              ))}
            </code>
          </pre>
        )}
      </div>
    </figure>
  );
}

export function Arrow({ dir = "down" }: { dir?: "down" | "right" | "up-right" }) {
  const d =
    dir === "down" ? "M8 3v9M4 8.5 8 12.5l4-4" : dir === "right" ? "M3 8h9M8.5 4l4 4-4 4" : "M5 11 11 5M6 5h5v5";
  return (
    <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden className="arrow">
      <path d={d} fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/** Light or dark. Starts from the visitor's system setting; a choice is remembered on this device only. */
export function ThemeToggle() {
  const [dark, setDark] = useState<boolean | null>(null);
  useEffect(() => setDark(document.documentElement.classList.contains("dark")), []);
  const flip = () => {
    const next = !document.documentElement.classList.contains("dark");
    document.documentElement.classList.toggle("dark", next);
    document.documentElement.classList.toggle("light", !next);
    try {
      localStorage.setItem("theme", next ? "dark" : "light");
    } catch {}
    setDark(next);
  };
  return (
    <button type="button" className="iconbtn iconbtn--ring" onClick={flip} aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}>
      <svg viewBox="0 0 20 20" width="17" height="17" aria-hidden className="themeicon">
        <circle cx="10" cy="10" r="6.4" fill="none" stroke="currentColor" strokeWidth="1.5" />
        <path d="M10 3.6a6.4 6.4 0 0 1 0 12.8z" fill="currentColor" />
      </svg>
    </button>
  );
}
