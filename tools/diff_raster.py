"""diff_raster.py SRC OUT glyph wght opsz rond out.png — where does the built glyph add or lose ink?"""
import ctypes
import sys
import freetype
import numpy as np
from PIL import Image

srcp, outp, name = sys.argv[1:4]
wght, opsz, rond = (float(x) for x in sys.argv[4:7])
PPEM = 1024
FLAGS = freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO | freetype.FT_LOAD_NO_BITMAP


def raster(path, coords):
    f = freetype.Face(path)
    f.set_pixel_sizes(0, PPEM)
    tags = [a.tag for a in f.get_variation_info().axes]
    f.set_var_design_coords([coords[t] for t in tags])
    f.load_glyph(f.get_name_index(name.encode()), FLAGS)
    b = f.glyph.bitmap
    raw = ctypes.string_at(b._FT_Bitmap.buffer, b.rows * b.pitch)
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8).reshape(b.rows, b.pitch), axis=1)[:, :b.width].astype(bool)
    return f.glyph.bitmap_left, f.glyph.bitmap_top, bits


a = raster(srcp, {"wght": wght, "opsz": opsz})
b = raster(outp, {"wght": wght, "opsz": opsz, "ROND": rond})
x0, y1 = min(a[0], b[0]), max(a[1], b[1])
x1 = max(a[0] + a[2].shape[1], b[0] + b[2].shape[1])
y0 = min(a[1] - a[2].shape[0], b[1] - b[2].shape[0])


def place(i):
    c = np.zeros((y1 - y0, x1 - x0), dtype=bool)
    c[y1 - i[1]:y1 - i[1] + i[2].shape[0], i[0] - x0:i[0] - x0 + i[2].shape[1]] = i[2]
    return c


A, B = place(a), place(b)
img = np.full(A.shape + (3,), 255, dtype=np.uint8)
img[A & B] = (60, 60, 60)
img[A & ~B] = (120, 170, 255)       # removed by rounding
img[B & ~A] = (255, 40, 40)         # added
Image.fromarray(img).save(sys.argv[7])
added = B & ~A
ys, xs = np.nonzero(added)
print("added px:", int(added.sum()), "bbox", (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None, "canvas", A.shape)
