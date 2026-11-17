"""Render launch media from the built fonts: a looping GIF of the roundness axis
and still images for the README.

    python tools/make_media.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ROMAN = str(ROOT / "fonts" / "variable" / "Inrond[ROND,opsz,wght].ttf")
ITALIC = str(ROOT / "fonts" / "variable" / "Inrond-Italic[ROND,opsz,wght].ttf")
OUT = ROOT / "documentation"
OUT.mkdir(exist_ok=True)
BG, FG, MUTED, ACCENT = (251, 251, 250), (17, 17, 16), (125, 124, 118), (255, 77, 46)
SS = 2      # supersampling


def font(path, size, wght, rond, opsz=None):
    f = ImageFont.truetype(path, size * SS)
    vals = []
    for ax in f.get_variation_axes():
        name = ax["name"].decode() if isinstance(ax["name"], bytes) else ax["name"]
        key = name.lower().replace(" ", "")
        if "weight" in key:
            vals.append(wght)
        elif "round" in key:
            vals.append(rond)
        elif "optical" in key:
            vals.append(opsz if opsz is not None else min(max(size * 0.75, ax["minimum"]), ax["maximum"]))
        else:
            vals.append(ax["default"])
    f.set_variation_by_axes(vals)
    return f


def canvas(w, h):
    return Image.new("RGB", (w * SS, h * SS), BG)


def finish(img):
    return img.resize((img.width // SS, img.height // SS), Image.LANCZOS)


def text(d, xy, s, f, fill=FG):
    d.text((xy[0] * SS, xy[1] * SS), s, font=f, fill=fill)


def hero_frame(rond, wght=660):
    W, H = 1200, 675
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    big = font(ROMAN, 330, wght, rond)
    text(d, (64, 96), "Inrond", big)
    wd = d.textlength("Inrond", font=big) / SS
    text(d, (64 + wd + 4, 96), ".", big, ACCENT)
    text(d, (70, 78), "A typeface with a roundness axis", font(ROMAN, 26, 520, 40), MUTED)
    lab = font(ROMAN, 30, 600, rond)
    text(d, (70, 520), "ROND", font(ROMAN, 22, 560, 40), MUTED)
    text(d, (70, 548), "%3d" % round(rond), lab)
    # slider
    x0, x1, y = 190, 1130, 566
    d.rounded_rectangle([x0 * SS, (y - 3) * SS, x1 * SS, (y + 3) * SS], radius=3 * SS, fill=(226, 225, 220))
    xk = x0 + (x1 - x0) * rond / 100
    d.rounded_rectangle([x0 * SS, (y - 3) * SS, xk * SS, (y + 3) * SS], radius=3 * SS, fill=ACCENT)
    d.ellipse([(xk - 13) * SS, (y - 13) * SS, (xk + 13) * SS, (y + 13) * SS], fill=ACCENT)
    text(d, (190, 596), "Sharp", font(ROMAN, 20, 520, 0), MUTED)
    r = font(ROMAN, 20, 520, 100)
    text(d, (1130 - d.textlength("Round", font=r) / SS, 596), "Round", r, MUTED)
    return finish(img)


def gif():
    frames = []
    n = 48
    for i in range(n):
        frames.append(hero_frame(50 - 50 * math.cos(2 * math.pi * i / n)))
    frames = [f.quantize(colors=64, method=Image.MEDIANCUT) for f in frames]
    frames[0].save(OUT / "inrond-roundness.gif", save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True)
    hero_frame(100).save(OUT / "inrond-hero.png")
    print("saved", OUT / "inrond-roundness.gif", (OUT / "inrond-roundness.gif").stat().st_size // 1024, "KB")


def ramp():
    W, H = 1200, 760
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    y = 44
    for rond in (0, 25, 50, 75, 100):
        text(d, (60, y + 34), "ROND %d" % rond, font(ROMAN, 20, 560, 40), MUTED)
        text(d, (200, y), "Rounded type, 2026", font(ROMAN, 92, 640, rond))
        y += 134
    finish(img).save(OUT / "inrond-ramp.png")


def weights():
    W, H = 1200, 700
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    y = 40
    for wght, label in ((100, "Thin"), (300, "Light"), (400, "Regular"), (600, "SemiBold"), (800, "ExtraBold"), (900, "Black")):
        text(d, (60, y + 22), label, font(ROMAN, 18, 560, 40), MUTED)
        text(d, (200, y + 8), "Sphinx of black quartz", font(ROMAN, 52, wght, 100))
        f = font(ITALIC, 52, wght, 100)
        text(d, (W - 60 - d.textlength("judge my vow", font=f) / SS, y + 8), "judge my vow", f)   # right-aligned
        y += 106
    finish(img).save(OUT / "inrond-weights.png")


if __name__ == "__main__":
    gif()
    ramp()
    weights()
    print("done")
