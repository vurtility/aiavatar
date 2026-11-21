"""Thumbnail toolkit: 3 A/B variants per episode, 1280x720 JPEG/PNG under YouTube's 2 MB limit.

Usage: EPISODE=episodes/<name>.py python3 thumbnails.py OUTDIR
The episode module defines thumbnails() -> [(slug, PIL.Image 1920x1080), ...] built with the helpers here.

Thumbnail rules (house style):
  - 3 variants that test different hooks (a face reacting, the stakes/number, the conflict/power angle)
  - at most 3-5 words of text, huge, thick black outline, readable at phone size
  - one or two big characters (heads take up ~1/3 of the height), high-contrast background
  - nothing misleading: the claim on the thumbnail must be true in the video
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
import art
from art import W, H


def canvas(bgk=None, col=None, rays=None):
    if bgk:
        im = art.bg(bgk).convert("RGBA")
    else:
        im = Image.new("RGBA", (W, H), col or (230, 60, 50, 255))
    if rays:
        d = ImageDraw.Draw(im)
        import math
        cx, cy = rays[0], rays[1]
        for i in range(24):
            if i % 2:
                continue
            a0, a1 = i * math.pi / 12, (i + 1) * math.pi / 12
            d.polygon([(cx, cy), (cx + 3000 * math.cos(a0), cy + 3000 * math.sin(a0)),
                       (cx + 3000 * math.cos(a1), cy + 3000 * math.sin(a1))], fill=rays[2])
        im = art.paperize(im, 0.12)
    return im


def big_text(im, lines, x, y, size=170, fill=(255, 255, 255), stroke=14, rot=-3, anchor="mm", hilite=None):
    """Huge outlined headline. lines: list of str or (str, colour)."""
    lines = [(l, fill) if isinstance(l, str) else l for l in lines]
    f = art.font("title", size)
    lh = int(size * 1.02)
    w = max(f.getbbox(t)[2] for t, _ in lines) + stroke * 4
    h = lh * len(lines) + stroke * 4
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, (t, c) in enumerate(lines):
        ty = 20 + stroke * 2 + i * lh + size // 2
        d.text((w / 2 + 28, ty + 10), t, font=f, fill=(0, 0, 0, 150), anchor="mm",
               stroke_width=stroke, stroke_fill=(0, 0, 0, 150))  # drop shadow
        d.text((w / 2 + 20, ty), t, font=f, fill=c, anchor="mm", stroke_width=stroke, stroke_fill=art.INK)
    layer = layer.rotate(rot, expand=True, resample=Image.BICUBIC)
    px = int(x - layer.width / 2) if anchor == "mm" else int(x)
    im.alpha_composite(layer, (px, int(y - layer.height / 2)))
    return im


def put(im, sprite, x, y, scale=1.0, anchor="bc", rot=0):
    s = sprite
    if scale != 1:
        s = s.resize((int(s.width * scale), int(s.height * scale)), Image.LANCZOS)
    if rot:
        s = s.rotate(rot, expand=True, resample=Image.BICUBIC)
    px = int(x - s.width / 2)
    py = int(y - s.height) if anchor == "bc" else int(y - s.height / 2)
    im.alpha_composite(s, (px, py))
    return im


def save(im, path):
    out = im.convert("RGB").resize((1280, 720), Image.LANCZOS)
    out = out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    out.save(path, "JPEG", quality=92, optimize=True)
    return path


if __name__ == "__main__":
    from kit import load_episode
    ep = load_episode()
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    for slug, im in ep.thumbnails():
        p = save(im, os.path.join(outdir, f"thumbnail_{slug}.jpg"))
        print(p, os.path.getsize(p) // 1024, "KB")
