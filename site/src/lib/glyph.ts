// Outline geometry from the font's own outlines (data/glyphs.json, made by scripts/glyph-data.py).
import data from "@/data/glyphs.json";

export { data };
export type Glyph = { paths: number[][]; area: number[]; adv: number; cmds: [string, number][] };
export const G = data.glyphs as unknown as Record<string, Glyph>;
export const WORD = ["a", "s"] as const;

/** The outline at any roundness: the font's own outlines at every 5 units, interpolated between neighbours. */
export function numsAt(g: Glyph, v: number) {
  const s = Math.min(19.9999, v / 5);
  const i = Math.floor(s);
  const t = s - i;
  const a = g.paths[i];
  const b = g.paths[i + 1];
  const out = new Array<number>(a.length);
  for (let k = 0; k < a.length; k++) out[k] = a[k] + (b[k] - a[k]) * t;
  return out;
}

export function areaAt(g: Glyph, v: number) {
  const s = Math.min(19.9999, v / 5);
  const i = Math.floor(s);
  return g.area[i] + (g.area[i + 1] - g.area[i]) * (s - i);
}

export const f = (n: number) => n.toFixed(1);

/** TrueType quadratic contours to an SVG path (y flipped), plus handle polylines and point lists. */
export function build(g: Glyph, nums: number[], dx: number) {
  let p = 0;
  const pt = () => {
    const x = nums[p] + dx;
    const y = -nums[p + 1];
    p += 2;
    return [x, y] as const;
  };
  let d = "";
  let handles = "";
  const on: number[] = [];
  const off: number[] = [];
  let last: readonly [number, number] = [0, 0];
  for (const [op, n] of g.cmds) {
    if (op === "moveTo") {
      last = pt();
      d += `M${f(last[0])} ${f(last[1])}`;
      on.push(last[0], last[1]);
    } else if (op === "lineTo") {
      last = pt();
      d += `L${f(last[0])} ${f(last[1])}`;
      on.push(last[0], last[1]);
    } else if (op === "qCurveTo") {
      const ps = Array.from({ length: n }, pt);
      const end = ps[n - 1];
      const offs = ps.slice(0, -1);
      handles += `M${f(last[0])} ${f(last[1])}`;
      for (let j = 0; j < offs.length; j++) {
        const o = offs[j];
        const next = j === offs.length - 1 ? end : ([(o[0] + offs[j + 1][0]) / 2, (o[1] + offs[j + 1][1]) / 2] as const);
        d += `Q${f(o[0])} ${f(o[1])} ${f(next[0])} ${f(next[1])}`;
        handles += `L${f(o[0])} ${f(o[1])}`;
        off.push(o[0], o[1]);
      }
      if (offs.length === 0) d += `L${f(end[0])} ${f(end[1])}`;
      handles += `L${f(end[0])} ${f(end[1])}`;
      on.push(end[0], end[1]);
      last = end;
    } else {
      d += "Z";
    }
  }
  return { d, handles, on, off };
}

