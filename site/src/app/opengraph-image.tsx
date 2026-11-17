import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { ImageResponse } from "next/og";
import { G, WORD, build, data } from "@/lib/glyph";

export const dynamic = "force-static";
export const alt = "Inrond: Inter, with a roundness axis. The letters a and s drawn at full roundness, with the ink the rounding removed in grey.";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const INK = "#121212";
const SIG = "#c4c4c4";
const LINE = "rgba(18,18,18,0.12)";

// Rendered at build time from the static Inrond Soft files and the font's own outlines.
export default async function OpengraphImage() {
  const dir = join(process.cwd(), "..", "fonts", "static");
  const [bold, regular] = await Promise.all([
    readFile(join(dir, "InrondSoft-Bold.ttf")),
    readFile(join(dir, "InrondSoft-Regular.ttf")),
  ]);
  const adv = WORD.map((c) => G[c].adv);
  const x0 = [0, adv[0]];
  const sharp = WORD.map((c, i) => build(G[c], G[c].paths[0], x0[i]).d).join("");
  const round = WORD.map((c, i) => build(G[c], G[c].paths[20], x0[i]).d).join("");
  const W = adv[0] + adv[1];
  const top = 1560;
  const bottom = 700;
  const vb = `-60 ${-top} ${W + 120} ${top + bottom}`;
  const lines = [data.capHeight, data.xHeight, 0, data.descender];
  const dimY = -data.descender + 170;

  return new ImageResponse(
    (
      <div style={{ width: "100%", height: "100%", display: "flex", background: "#ffffff", fontFamily: "Inrond Soft" }}>
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            padding: "56px 0 52px 64px",
            color: INK,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 30, fontWeight: 700 }}>
            <div style={{ width: 22, height: 22, background: INK, borderRadius: "11px 11px 11px 0" }} />
            Inrond
          </div>
          <div style={{ display: "flex", flexDirection: "column", fontSize: 80, fontWeight: 700, letterSpacing: -3, lineHeight: 0.98 }}>
            <span>Inter, with a</span>
            <span>roundness axis.</span>
          </div>
          <div style={{ display: "flex", gap: 22, fontSize: 20, color: "#767676" }}>
            <span>ROND 0 to 100</span>
            <span>2,937 glyphs</span>
            <span>0 widths changed</span>
            <span>Free, OFL</span>
          </div>
        </div>
        <div style={{ width: 500, display: "flex", alignItems: "center", justifyContent: "center", background: "#f5f5f5", borderLeft: `1px solid ${LINE}` }}>
          <svg width={440} height={Math.round((440 * (top + bottom)) / (W + 120))} viewBox={vb}>
            {lines.map((y) => (
              <line key={y} x1={-60} x2={W + 60} y1={-y} y2={-y} stroke={LINE} strokeWidth={5} />
            ))}
            {[0, adv[0], W].map((x) => (
              <line key={x} x1={x} x2={x} y1={-top} y2={dimY + 30} stroke={LINE} strokeWidth={5} strokeDasharray="14 18" />
            ))}
            <path d={sharp} fill={SIG} />
            <path d={round} fill={INK} />
            <line x1={6} x2={W - 6} y1={dimY} y2={dimY} stroke={INK} strokeWidth={5} />
            <path d={`M6 ${dimY - 30}v60M${adv[0]} ${dimY - 30}v60M${W - 6} ${dimY - 30}v60`} stroke={INK} strokeWidth={5} />
          </svg>
        </div>
      </div>
    ),
    {
      ...size,
      fonts: [
        { name: "Inrond Soft", data: bold, weight: 700, style: "normal" },
        { name: "Inrond Soft", data: regular, weight: 400, style: "normal" },
      ],
    }
  );
}
