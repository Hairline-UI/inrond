// Copies the shipped webfonts into public/fonts/<stamp>/ so the page is set in the real files.
// The repository's fonts/ folder is the single source; nothing is duplicated in git.
// Browsers keep /fonts/* for 30 days (public/_headers), so the folder is named after the files' contents: when the
// fonts change, the address changes, and returning visitors fetch the new files instead of their cached copies.
// The address is written to src/data/fonts.json for the layout to use.
import { createHash } from "node:crypto";
import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const site = join(dirname(fileURLToPath(import.meta.url)), "..");
const from = join(site, "..", "fonts", "webfonts");
const root = join(site, "public", "fonts");

if (!existsSync(from)) {
  console.error(`No webfonts at ${from}. Run python scripts/release.py in the repository root first.`);
  process.exit(1);
}

const files = readdirSync(from)
  .filter((f) => /\.(woff2|css)$/.test(f))
  .sort();
const hash = createHash("sha256");
for (const f of files) hash.update(f).update(readFileSync(join(from, f)));
const stamp = hash.digest("hex").slice(0, 10);
const to = join(root, stamp);

rmSync(root, { recursive: true, force: true });
mkdirSync(to, { recursive: true });
for (const f of files) cpSync(join(from, f), join(to, f));
writeFileSync(join(site, "src", "data", "fonts.json"), JSON.stringify({ base: `/fonts/${stamp}` }) + "\n");
console.log(`Copied ${files.length} webfont files to public/fonts/${stamp}`);
