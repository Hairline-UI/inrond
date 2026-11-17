// Every number on the page was measured from the font files; the README and qa/ hold the details.

export const REPO = "https://github.com/Hairline-UI/inrond";
export const DOWNLOAD = `${REPO}/releases/latest`;
export const INTER = "https://rsms.me/inter/";
export const HAIRLINE = "https://hairlineui.com";
export const REPO_API = "https://api.github.com/repos/Hairline-UI/inrond";
export const VERSION = "1.0";
export const CDN = "https://cdn.jsdelivr.net/gh/Hairline-UI/inrond@v1.0/fonts/webfonts";

export const TICKER = [
  ["2,937", "glyphs"],
  ["2,852", "characters"],
  ["249", "Cyrillic"],
  ["105", "Greek"],
  ["39", "OpenType features"],
  ["100–900", "weight"],
  ["14–32", "optical size"],
  ["Drawn", "italic"],
] as const;

export type Row = [string, string, string, string, string, string];
export const COMPARE: { head: string[]; rows: Row[] } = {
  head: ["Inrond 1.0", "Inter 4.1", "Google Sans Flex", "Open Runde", "Intern"],
  rows: [
    ["Roundness", "Axis, 0 to 100", "None", "Axis, 0 to 100", "Fixed", "Fixed"],
    ["Design", "Inter", "Inter", "Google Sans", "Inter", "Inter"],
    ["Glyphs", "2,937", "2,937", "686", "2,549", "1,087"],
    ["Unicode characters", "2,852", "2,852", "541", "2,512", "541"],
    ["Cyrillic / Greek", "249 / 105", "249 / 105", "0 / 1", "256 / 121", "0 / 0"],
    ["Italic", "Drawn", "Drawn", "Slant axis", "None", "None"],
    ["Weight", "100 to 900", "100 to 900", "1 to 1000", "4 static", "100 to 900"],
    ["Optical size", "14 to 32", "14 to 32", "1 to 144", "No", "14 to 32"],
    ["OpenType features", "39", "39", "20", "6", "33"],
    ["Full roman, woff2", "899 KB", "344 KB", "1,418 KB", "151 KB a weight", "170 KB"],
  ],
};

export const SIZES = [
  { build: "Inter 4.1", note: "the baseline", latin: 103, full: 344, kind: "base" },
  { build: "Inrond Round", note: "frozen at 100", latin: 159, full: 540, kind: "frozen" },
  { build: "Inrond Soft", note: "frozen at 50", latin: 163, full: 563, kind: "frozen" },
  { build: "Inrond", note: "axis live", latin: 257, full: 899, kind: "live" },
  { build: "Inrond Italic", note: "axis live", latin: 282, full: 995, kind: "live" },
] as const;

export const CHECKS = [
  { name: "Sharp", rule: "ROND 0 renders the same as Inter", limit: "any 4-unit difference", roman: "0 px", italic: "0 px" },
  { name: "Inside", rule: "Round ends pass their cut no further than Inter’s o passes the baseline", limit: "8+ units beyond that", roman: "0 glyphs", italic: "0 glyphs" },
  { name: "Monotone", rule: "More roundness never brings ink back", limit: "10+ units return", roman: "0 glyphs", italic: "0 glyphs" },
  { name: "Kinks", rule: "New 8° direction breaks at ROND 100", limit: "over 2% of glyphs", roman: "13 of 58", italic: "18 of 57" },
  { name: "Metrics", rule: "Advance widths that differ from Inter", limit: "any mismatch", roman: "0", italic: "0" },
  { name: "Shaping", rule: "HarfBuzz runs that differ from Inter", limit: "any differing run", roman: "0 of 504", italic: "0 of 504" },
] as const;
