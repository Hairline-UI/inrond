// Every number on the page was measured from the font files; the README and qa/ hold the details.

export const REPO = "https://github.com/Hairline-UI/inrond";
export const DOWNLOAD = `${REPO}/releases/latest`;
export const INTER = "https://rsms.me/inter/";
export const HAIRLINE = "https://hairlineui.com";
export const REPO_API = "https://api.github.com/repos/Hairline-UI/inrond";
export const VERSION = "1.0";
export const CDN = "https://cdn.jsdelivr.net/gh/Hairline-UI/inrond@5e6b991/fonts/webfonts";

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
  head: ["Inrond", "Inter", "Google Sans Flex", "Open Runde", "Intern"],
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
    ["File size, roman", "899 KB", "344 KB", "1,418 KB", "151 KB a weight", "170 KB"],
  ],
};

export const SIZES = [
  { build: "Inter", note: "for reference", latin: 103, full: 344, kind: "base" },
  { build: "Inrond Round", note: "fixed at 100", latin: 159, full: 540, kind: "frozen" },
  { build: "Inrond Soft", note: "fixed at 50", latin: 163, full: 563, kind: "frozen" },
  { build: "Inrond", note: "adjustable", latin: 257, full: 899, kind: "live" },
  { build: "Inrond Italic", note: "adjustable", latin: 282, full: 995, kind: "live" },
] as const;

export const CHECKS = [
  { name: "Inter at zero", rule: "At roundness 0, every letter is drawn exactly like Inter", roman: "0 px off", italic: "0 px off" },
  { name: "No bulges", rule: "Rounding never adds ink beyond the slight overshoot an o already has", roman: "0 letters", italic: "0 letters" },
  { name: "Only trims", rule: "Turning roundness up only ever takes ink away, never puts it back", roman: "0 letters", italic: "0 letters" },
  { name: "Clean curves", rule: "Hardly any new kinks where a round end meets a curve (allowed: 2%)", roman: "13 letters", italic: "18 letters" },
  { name: "Same widths", rule: "Every letter is exactly as wide as in Inter", roman: "0 differ", italic: "0 differ" },
  { name: "Same layout", rule: "Text is shaped, kerned and spaced exactly as with Inter", roman: "0 of 504", italic: "0 of 504" },
] as const;
