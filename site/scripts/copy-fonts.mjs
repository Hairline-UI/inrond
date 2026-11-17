// Copies the shipped webfonts into public/fonts so the page is set in the real files.
// The repository's fonts/ folder is the single source; nothing is duplicated in git.
import { cpSync, existsSync, mkdirSync, readdirSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const site = join(dirname(fileURLToPath(import.meta.url)), "..");
const from = join(site, "..", "fonts", "webfonts");
const to = join(site, "public", "fonts");

if (!existsSync(from)) {
  console.error(`No webfonts at ${from}. Run python scripts/release.py in the repository root first.`);
  process.exit(1);
}

rmSync(to, { recursive: true, force: true });
mkdirSync(to, { recursive: true });
let n = 0;
for (const file of readdirSync(from)) {
  if (!/\.(woff2|css)$/.test(file)) continue;
  cpSync(join(from, file), join(to, file));
  n++;
}
console.log(`Copied ${n} webfont files to public/fonts`);
