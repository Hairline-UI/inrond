"""Freeze Inrond at any roundness and keep weight and optical size variable.

    python scripts/pin.py 60            ->  fonts/custom/Inrond60[opsz,wght].woff2 (+ italic, ttf, subsets, css)

A site that uses one roundness everywhere does not need the roundness axis on
the wire. A frozen build is about a third smaller than the full font.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import release  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("roundness", type=float, help="0 to 100")
ap.add_argument("--out", default=str(release.ROOT / "fonts" / "custom"))
a = ap.parse_args()
if not 0 <= a.roundness <= 100:
    raise SystemExit("roundness must be between 0 and 100")
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)
label = "%g" % a.roundness
css = ["/* %s %s: roundness fixed at %s. font-weight: 100..900; opsz follows font-size. */\n" % (release.F, label, label)]
for italic in (False, True):
    ttf = release.FONTS / "variable" / (release.F + ("-Italic" if italic else "") + release.AXES + ".ttf")
    release.make_pinned(ttf, italic, label, a.roundness, css, out_dir=out)
(out / ("%s-%s.css" % (release.F.lower(), label))).write_text("\n".join(css), encoding="utf-8")
