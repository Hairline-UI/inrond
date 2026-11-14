"""Render side-by-side comparison sheets with Pillow/FreeType.

usage: render.py out.png SIZE "text" label=path[@axis=val,axis=val] ...
"""
import sys
from PIL import Image, ImageDraw, ImageFont

out, size, text = sys.argv[1], int(sys.argv[2]), sys.argv[3]
specs = sys.argv[4:]

LABEL = ImageFont.load_default(size=16)
rows = []
for spec in specs:
    label, rest = spec.split("=", 1)
    path, _, axes = rest.partition("@")
    font = ImageFont.truetype(path, size)
    if axes:
        want = dict(kv.split("=") for kv in axes.split(","))
        vals = []
        for ax in font.get_variation_axes():
            # Pillow exposes axis names, not tags; match on either.
            nm = ax["name"]
            nm = nm.decode() if isinstance(nm, bytes) else nm
            key = next((k for k in want if k.lower() in nm.lower().replace(" ", "")), None)
            vals.append(float(want[key]) if key else ax["default"])
        font.set_variation_by_axes(vals)
    rows.append((label, font))

pad = 28
lines = text.split("\\n")
line_h = int(size * 1.25)
row_h = line_h * len(lines) + 34
width = max(int(max(f.getlength(l) for l in lines)) for _, f in rows) + pad * 2
img = Image.new("RGB", (width, row_h * len(rows) + pad), "white")
d = ImageDraw.Draw(img)
y = pad // 2
for label, font in rows:
    d.text((pad, y), label, font=LABEL, fill=(150, 150, 150))
    for i, l in enumerate(lines):
        d.text((pad, y + 22 + i * line_h), l, font=font, fill="black")
    y += row_h
img.save(out)
print("saved", out, img.size)
