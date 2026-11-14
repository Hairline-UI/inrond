"use client";

import { useEffect, useState } from "react";
import { REPO, REPO_API } from "@/data/site";

const KEY = "inrond-stars";
const FRESH = 10 * 60 * 1000;

const fmt = (n: number) => (n >= 1000 ? `${(n / 1000).toFixed(n >= 10000 ? 0 : 1).replace(/\.0$/, "")}k` : n.toLocaleString("en-US"));

/**
 * The GitHub button with the repository's star count. The count is read from GitHub when the site is built, then
 * refreshed in the visitor's browser (at most every ten minutes per visitor, so GitHub's limit of 60 requests an hour
 * per address is never a problem). If GitHub cannot be reached, the build-time count stays.
 */
export function StarButton({ initial }: { initial: number | null }) {
  const [stars, setStars] = useState(initial);
  useEffect(() => {
    try {
      const saved = JSON.parse(sessionStorage.getItem(KEY) || "null");
      if (saved && Date.now() - saved.t < FRESH && typeof saved.n === "number") {
        setStars(saved.n);
        return;
      }
    } catch {}
    const ctl = new AbortController();
    fetch(REPO_API, { headers: { Accept: "application/vnd.github+json" }, signal: ctl.signal })
      .then((r) => (r.ok ? r.json() : null))
      .then((j) => {
        if (j && typeof j.stargazers_count === "number") {
          setStars(j.stargazers_count);
          try {
            sessionStorage.setItem(KEY, JSON.stringify({ n: j.stargazers_count, t: Date.now() }));
          } catch {}
        }
      })
      .catch(() => {});
    return () => ctl.abort();
  }, []);

  const label = stars === null ? "Star Inrond on GitHub" : `Star Inrond on GitHub, ${stars} stars`;
  return (
    <a className="btn btn--soft gh" href={REPO} aria-label={label} data-oa-event="github_star" data-oa-prop-location="hero">
      <svg viewBox="0 0 16 16" width="17" height="17" aria-hidden className="gh__mark">
        <path
          fill="currentColor"
          d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
        />
      </svg>
      Star
      <span className="gh__count">
        <svg viewBox="0 0 16 16" width="13" height="13" aria-hidden>
          <path
            fill="currentColor"
            d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.751.751 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z"
          />
        </svg>
        <span className="gh__n">{stars === null ? "–" : fmt(stars)}</span>
      </span>
    </a>
  );
}
