"""Construction-paper cutout art: characters, props and backgrounds drawn with PIL."""
import math, random, functools, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import numpy as np

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
W, H = 1920, 1080
K = 2  # supersample factor
INK = (28, 24, 22)
OUT = 3  # outline width at 1x

SKIN = {"light": (246, 206, 160), "tan": (226, 172, 120), "brown": (176, 118, 78),
        "orange": (247, 176, 108), "pale": (250, 222, 190)}


@functools.lru_cache(None)
def font(kind, size):
    f = {"title": "title.woff", "hand": "hand.woff"}[kind]
    return ImageFont.truetype(f"{ASSETS}/{f}", size)


@functools.lru_cache(None)
def grain(w, h, seed=1):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (h // 4 + 1, w // 4 + 1)).astype(np.float32)
    img = Image.fromarray(((n * 18) + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
    fine = Image.fromarray((rng.normal(128, 9, (h, w))).clip(0, 255).astype(np.uint8))
    return Image.blend(img, fine, 0.5)


def paperize(img, strength=0.10):
    """Multiply a paper grain into an RGBA/RGB image."""
    g = grain(img.width, img.height).convert("RGB")
    rgb = img.convert("RGB")
    arr = np.asarray(rgb).astype(np.float32)
    ga = (np.asarray(g).astype(np.float32) - 128) / 128.0
    arr = (arr * (1 + ga * strength)).clip(0, 255).astype(np.uint8)
    out = Image.fromarray(arr)
    if img.mode == "RGBA":
        out.putalpha(img.getchannel("A"))
    return out


class Pen:
    """Draws at K-times resolution with coordinates given at 1x."""

    def __init__(self, w, h, oy=0):
        """oy: extra headroom added above the drawing (all y coordinates shift down by oy)."""
        self.w, self.h, self.oy = w, h + oy, oy
        self.im = Image.new("RGBA", (w * K, (h + oy) * K), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _p(self, pts):
        return [(x * K, (y + self.oy) * K) for x, y in pts]

    def ell(self, cx, cy, w, h, fill, ol=INK, ow=OUT):
        cy = cy + self.oy
        self.d.ellipse([(cx - w / 2) * K, (cy - h / 2) * K, (cx + w / 2) * K, (cy + h / 2) * K],
                       fill=fill, outline=ol, width=int(ow * K) if ol else 0)

    def rect(self, x0, y0, x1, y1, fill, ol=INK, ow=OUT, r=0):
        y0, y1 = y0 + self.oy, y1 + self.oy
        box = [x0 * K, y0 * K, x1 * K, y1 * K]
        if r:
            self.d.rounded_rectangle(box, r * K, fill=fill, outline=ol, width=int(ow * K) if ol else 0)
        else:
            self.d.rectangle(box, fill=fill, outline=ol, width=int(ow * K) if ol else 0)

    def poly(self, pts, fill, ol=INK, ow=OUT):
        self.d.polygon(self._p(pts), fill=fill, outline=ol, width=int(ow * K) if ol else 0)

    def line(self, pts, fill=INK, w=OUT):
        self.d.line(self._p(pts), fill=fill, width=int(w * K), joint="curve")

    def arc(self, cx, cy, w, h, a0, a1, fill=INK, wd=OUT):
        cy = cy + self.oy
        self.d.arc([(cx - w / 2) * K, (cy - h / 2) * K, (cx + w / 2) * K, (cy + h / 2) * K], a0, a1,
                   fill=fill, width=int(wd * K))

    def chord(self, cx, cy, w, h, a0, a1, fill, ol=INK, ow=OUT):
        cy = cy + self.oy
        self.d.chord([(cx - w / 2) * K, (cy - h / 2) * K, (cx + w / 2) * K, (cy + h / 2) * K], a0, a1,
                     fill=fill, outline=ol, width=int(ow * K) if ol else 0)

    def pie(self, cx, cy, w, h, a0, a1, fill, ol=INK, ow=OUT):
        cy = cy + self.oy
        self.d.pieslice([(cx - w / 2) * K, (cy - h / 2) * K, (cx + w / 2) * K, (cy + h / 2) * K], a0, a1,
                        fill=fill, outline=ol, width=int(ow * K) if ol else 0)

    def text(self, cx, cy, s, size, fill=INK, kind="title", anchor="mm", stroke=0, stroke_fill=None):
        cy = cy + self.oy
        self.d.text((cx * K, cy * K), s, font=font(kind, int(size * K)), fill=fill, anchor=anchor,
                    stroke_width=int(stroke * K), stroke_fill=stroke_fill)

    def done(self, shadow=True, paper=True):
        im = self.im.resize((self.w, self.h), Image.LANCZOS)
        if paper:
            im = paperize(im, 0.07)
        if shadow:
            im = add_shadow(im)
        return im


def add_shadow(im, off=(7, 8), alpha=0.33, pad=12):
    w, h = im.size
    out = Image.new("RGBA", (w + pad, h + pad), (0, 0, 0, 0))
    a = im.getchannel("A").point(lambda v: int(v * alpha))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 255))
    sh.putalpha(a)
    out.paste(sh, off, sh)
    out.alpha_composite(im, (0, 0))
    return out


def text_size(s, size, kind="title"):
    b = font(kind, size).getbbox(s)
    return b[2] - b[0], b[3] - b[1]


# ----------------------------------------------------------------------------- characters

def head_outline(q, kind, cx, hy, sk):
    """Face shape. All fit the same ~226x196 box so hair/hats line up; head_w/head_h stretch it."""
    a, b = 113, 98
    if kind == "round":
        q.ell(cx, hy, 2 * a, 2 * b, sk)
        return
    if kind == "square":
        q.rect(cx - a + 4, hy - b, cx + a - 4, hy + b, sk, r=46)
        return
    pts = []
    for i in range(72):
        t = 2 * math.pi * i / 72
        x, y = math.cos(t), math.sin(t)  # y>0 is the lower half (chin side)
        if kind == "oval":
            px, py = a * 0.86 * x, b * 1.08 * y
        elif kind == "egg":      # broad forehead, narrow chin
            px, py = a * x * (1 - 0.2 * max(0, y)), b * 1.04 * y
        elif kind == "pear":     # narrow crown, heavy jaw
            px, py = a * x * (1 + 0.1 * y) * (0.92 if y < 0 else 1.0), b * y
        elif kind == "bean":     # wide and flat
            px, py = a * 1.04 * x, b * 0.86 * y + 10
        else:
            px, py = a * x, b * y
        pts.append((cx + px, hy + py))
    q.poly(pts, sk)


def person(skin="light", hair="short", hair_col=(70, 45, 30), outfit="suit", col=(45, 60, 110),
           tie=(190, 40, 40), mouth="closed", eyes="normal", sash=False, glasses=False, mustache=False,
           beard=False, hat=None, shirt=(240, 240, 240), pants=(50, 50, 60), arms="down", hold=None,
           scale=1.0, flip=False, old=False, look=0, build=1.0, height=1.0, head_w=1.0, brows=None,
           pin=None, cross=False, jowls=False, tie_w=1.0, head="round", head_h=1.0, eye_s=1.0,
           nose=None, ears=False, hat_col=None, detach_sign=False):
    """Cutout character.
    build: body width (0.8 thin, 1.0 average, 1.2 stocky, 1.4 heavy - heavy also gets a belly)
    height: overall size multiplier; head_w: head width multiplier
    brows: None/'thick'/'grey'; pin: lapel pin ('us'/'py'); cross: pendant; jowls: rounder lower face
    tie_w: tie width multiplier (Trump's tie is wide and extra long via outfit='longtie')
    head: round/oval/square/egg/pear/bean outline; head_h: head height multiplier (chin stays put)
    eye_s: eye size (0.75 small .. 1.2 big); nose: None/'dot'/'button'/'long'/'wide'; ears: draw ears
    hat: police/cap/helmet/bobble/earflap/hood/bucket/headband/beret/clip; hat_col: its colour"""
    w, h = 300, 430
    p = Pen(w, h, oy=TOP)
    sk = SKIN.get(skin, skin) if isinstance(skin, str) else skin
    cx = 150
    b = build
    xl, xr = cx - 52 * b, cx + 52 * b          # shoulders
    bl, br = cx - 62 * b, cx + 62 * b          # hem
    # legs + shoes (heavier builds stand a little wider)
    lg = 18 + 8 * (b - 1)
    p.rect(cx - lg - 14, 352, cx - lg + 14, 392, pants)
    p.rect(cx + lg - 14, 352, cx + lg + 14, 392, pants)
    p.ell(cx - lg - 6, 398, 52, 22, (30, 30, 30))
    p.ell(cx + lg + 6, 398, 52, 22, (30, 30, 30))
    # body
    if outfit == "dress":
        p.poly([(cx - 40 * b, 228), (cx + 40 * b, 228), (cx + 65 * b, 370), (cx - 65 * b, 370)], col)
    else:
        p.poly([(xl, 236), (xr, 236), (br, 362), (bl, 362)], col)
        if b >= 1.25:  # belly
            p.ell(cx, 318, 128 * b, 96 + 30 * (b - 1.25), col)
            p.rect(bl + 3, 340, br - 3, 360, col, ol=None)
    if outfit == "suit":
        p.poly([(132, 236), (168, 236), (150, 300)], shirt)
        tw = 6 * tie_w
        p.poly([(cx - tw, 248), (cx + tw, 248), (cx + tw + 4, 318), (cx, 330), (cx - tw - 4, 318)], tie, ow=2)
        p.line([(150, 300), (150, 360)], w=2)
        p.ell(150, 328, 7, 7, INK, ol=None)
    elif outfit == "longtie":
        p.poly([(130, 236), (170, 236), (150, 300)], shirt)
        tw = 9 * tie_w
        p.poly([(cx - tw, 248), (cx + tw, 248), (cx + tw + 6, 392), (cx, 408), (cx - tw - 6, 392)], tie, ow=2)
        p.poly([(cx - tw - 2, 244), (cx + tw + 2, 244), (cx + tw, 258), (cx - tw, 258)], tie, ow=2)  # knot
    elif outfit == "jersey":
        x = xl + 2
        i = 0
        while x < xr - 4:
            if i % 2 == 0:
                p.poly([(x, 238), (min(x + 11, xr), 238), (min(x + 11 + 10 * b, br), 360), (x + 10 * b - 10, 360)],
                       (255, 255, 255), ol=None)
            x += 22
            i += 1
        p.poly([(xl, 236), (xr, 236), (br, 362), (bl, 362)], None)
        p.text(150, 300, "ueno", 22, fill=(20, 140, 120), kind="title")
    elif outfit == "uniform":
        p.ell(cx - 20 * b, 270, 18, 18, (230, 200, 60))
        p.line([(150, 240), (150, 360)], w=2)
        p.ell(150, 280, 6, 6, (230, 200, 60), ol=None)
        p.ell(150, 320, 6, 6, (230, 200, 60), ol=None)
    elif outfit == "robe":
        p.poly([(132, 236), (168, 236), (150, 280)], shirt)
    elif outfit == "shirt":
        p.poly([(135, 236), (165, 236), (150, 262)], tuple(min(255, c + 40) for c in col))
    if pin == "us":
        p.rect(xl + 16, 262, xl + 34, 274, (200, 40, 50), ow=1)
        p.rect(xl + 16, 262, xl + 24, 268, (40, 60, 140), ol=None)
    elif pin == "py":
        p.ell(xl + 26, 268, 14, 14, (210, 40, 45), ow=1)
    if cross:
        p.line([(140, 238), (150, 280), (160, 238)], fill=(200, 170, 60), w=2)
        p.rect(147, 280, 153, 304, (200, 170, 60), ol=None)
        p.rect(141, 286, 159, 292, (200, 170, 60), ol=None)
    if sash:
        p.poly([(xl, 250), (xl + 20, 236), (br - 6, 340), (br - 22, 356)], (210, 40, 45), ow=2)
        p.poly([(xl + 6, 258), (xl + 16, 250), (br - 13, 347), (br - 19, 352)], (255, 255, 255), ol=None)
        p.ell(br - 16, 352, 20, 20, (235, 200, 60), ow=2)
    # arms + mitten hands
    front = Pen(w, h, oy=TOP)  # limbs that must sit in front of the head
    if hold_is_sign(hold):  # sign stick runs up behind the head from the right hand
        p.rect(xr - 6, 40, xr + 4, 344, (140, 100, 60), ow=2)
    if arms == "up":  # hands out wide beside the head, arms drawn over the head's lower edge
        front.poly([(xl + 4, 240), (xl + 18, 252), (xl - 34, 186), (xl - 48, 196)], col)
        front.poly([(xr - 4, 240), (xr - 18, 252), (xr + 34, 186), (xr + 48, 196)], col)
        front.ell(xl - 44, 180, 30, 30, sk)
        front.ell(xr + 44, 180, 30, 30, sk)
    elif arms == "point":
        p.poly([(xl, 244), (xl + 12, 252), (bl + 12, 340), (bl - 4, 336)], col)
        p.ell(bl + 2, 344, 30, 30, sk)
        p.poly([(xr, 244), (xr - 6, 262), (282, 236), (282, 222)], col)
        p.ell(288, 228, 30, 30, sk)
    elif arms == "hold":
        p.poly([(xl, 244), (xl + 14, 252), (128, 310), (112, 318)], col)
        p.poly([(xr, 244), (xr - 14, 252), (172, 310), (188, 318)], col)
    else:
        p.poly([(xl, 244), (xl + 12, 252), (bl + 12, 340), (bl - 4, 336)], col)
        p.poly([(xr, 244), (xr - 12, 252), (br - 12, 340), (br + 4, 336)], col)
        p.ell(bl + 2, 344, 30, 30, sk)
        p.ell(br - 2, 344, 30, 30, sk)
    # ---- head on its own layer so it can be widened/narrowed per person
    q = Pen(w, h, oy=TOP)
    hy = 138
    if hair == "long":  # hair falls behind the head at the sides, ending level with the cheeks
        q.rect(cx - 122, hy - 40, cx - 60, hy + 66, hair_col, r=26)
        q.rect(cx + 60, hy - 40, cx + 122, hy + 66, hair_col, r=26)
    if ears:
        q.ell(cx - 112, hy + 6, 34, 50, sk)
        q.ell(cx + 112, hy + 6, 34, 50, sk)
    hcol = hat_col or (200, 60, 60)
    dark = tuple(int(v * 0.75) for v in hcol)
    if hat == "hood":
        q.ell(cx, hy - 4, 262, 236, hcol)
    head_outline(q, head, cx, hy, sk)
    if jowls:
        q.chord(cx, hy + 34, 214, 150, 0, 180, sk, ol=None)
        q.arc(cx, hy + 34, 214, 150, 20, 160, wd=OUT)
        q.arc(cx - 64, hy + 62, 40, 30, 300, 40, fill=(170, 110, 80), wd=2)
        q.arc(cx + 64, hy + 62, 40, 30, 140, 240, fill=(170, 110, 80), wd=2)
    if old:
        q.arc(cx - 70, hy + 40, 30, 20, 200, 340, fill=(150, 100, 80), wd=2)
        q.arc(cx + 70, hy + 40, 30, 20, 200, 340, fill=(150, 100, 80), wd=2)
    hc = hair_col
    if hair == "short":
        q.chord(cx, hy - 20, 228, 170, 180, 360, hc)
        q.poly([(cx - 110, hy - 20), (cx - 60, hy - 40), (cx - 100, hy + 10)], hc, ol=None)
    elif hair == "swoop":  # big blond comb-over that sweeps forward and up
        q.chord(cx, hy - 26, 236, 166, 180, 360, hc)
        q.poly([(cx - 122, hy - 26), (cx - 40, hy - 96), (cx + 70, hy - 104), (cx + 132, hy - 60),
                (cx + 120, hy - 24), (cx + 40, hy - 40), (cx - 50, hy - 4)], hc)
        q.line([(cx - 60, hy - 60), (cx + 80, hy - 78)], fill=tuple(max(0, c - 40) for c in hc), w=3)
        q.line([(cx - 40, hy - 40), (cx + 90, hy - 56)], fill=tuple(max(0, c - 40) for c in hc), w=3)
    elif hair == "bald":
        q.chord(cx - 98, hy + 6, 40, 80, 90, 270, hc)
        q.chord(cx + 98, hy + 6, 40, 80, 270, 90, hc)
    elif hair == "side":
        q.chord(cx, hy - 24, 226, 150, 180, 360, hc)
        q.line([(cx - 40, hy - 96), (cx - 30, hy - 40)], fill=sk, w=4)
    elif hair == "slick":  # short, neat, swept back
        q.chord(cx, hy - 30, 222, 140, 180, 360, hc)
        q.line([(cx - 70, hy - 84), (cx + 60, hy - 90)], fill=tuple(min(255, c + 50) for c in hc), w=3)
    elif hair == "bun":
        q.chord(cx, hy - 20, 228, 160, 180, 360, hc)
        q.ell(cx, hy - 110, 70, 56, hc)
    elif hair == "long":
        q.chord(cx, hy - 20, 228, 160, 180, 360, hc)
    elif hair == "spiky":  # spikes growing out of the crown, no flat cap underneath
        for i in range(9):
            t = math.radians(212 + i * 14.5)
            d = 0.11
            bx0, by0 = cx + 112 * math.cos(t - d), hy + 97 * math.sin(t - d)
            bx1, by1 = cx + 112 * math.cos(t + d), hy + 97 * math.sin(t + d)
            ln = 1.42 - 0.08 * abs(i - 4) / 4
            q.poly([(bx0, by0), (cx + 112 * ln * math.cos(t), hy + 97 * ln * math.sin(t)), (bx1, by1)], hc)
    elif hair == "afro":
        for i in range(11):
            a_ = math.pi * (0.9 + i * 1.2 / 10)
            q.ell(cx + 112 * math.cos(a_), hy - 30 + 100 * math.sin(a_), 80, 80, hc)
        q.ell(cx, hy - 90, 200, 90, hc, ol=None)
    elif hair == "mohawk":
        q.poly([(cx - 22, hy - 92), (cx - 10, hy - 140), (cx + 10, hy - 140), (cx + 22, hy - 92)], hc)
        q.chord(cx, hy - 26, 226, 150, 200, 340, tuple(int(v * 0.6 + s * 0.4) for v, s in zip(hc, sk)), ol=None)
    elif hair == "buzz":
        q.chord(cx, hy - 22, 224, 156, 180, 360, tuple(int(v * 0.55 + s * 0.45) for v, s in zip(hc, sk)), ol=None)
        q.arc(cx, hy - 22, 224, 156, 180, 360, wd=OUT)
    elif hair == "ponytail":
        q.ell(cx + 120, hy - 10, 56, 110, hc)
        q.chord(cx, hy - 20, 228, 160, 180, 360, hc)
    elif hair == "receding":
        q.chord(cx - 92, hy - 10, 50, 110, 90, 270, hc)
        q.chord(cx + 92, hy - 10, 50, 110, 270, 90, hc)
        q.ell(cx, hy - 92, 50, 16, hc, ol=None)
    elif hair == "beanie":
        q.chord(cx, hy - 34, 232, 190, 180, 360, col if isinstance(col, tuple) else (200, 60, 60))
        q.rect(cx - 116, hy - 46, cx + 116, hy - 22, tuple(int(v * 0.8) for v in col), r=8)
        q.ell(cx, hy - 132, 36, 36, (240, 240, 240))
    elif hair == "messy":  # mop-top following the head, with a jagged fringe and a few stray tufts
        pts = [(cx + 118 * math.cos(math.radians(t)), hy - 6 + 104 * math.sin(math.radians(t)))
               for t in range(180, 361, 10)]
        fr = []
        for i in range(11):
            x = cx + 114 - i * 22.8
            fr.append((x, hy - 34 + (14 if i % 2 else 0)))
        q.poly(pts + fr, hc)
    elif hair == "bob":  # straight bob framing the face
        q.chord(cx, hy - 16, 236, 176, 180, 360, hc)
        q.rect(cx - 120, hy - 20, cx - 92, hy + 50, hc, r=10)
        q.rect(cx + 92, hy - 20, cx + 120, hy + 50, hc, r=10)
    elif hair == "pigtails":
        q.chord(cx, hy - 20, 228, 160, 180, 360, hc)
        q.ell(cx - 126, hy + 10, 44, 70, hc)
        q.ell(cx + 126, hy + 10, 44, 70, hc)
        q.ell(cx - 112, hy - 18, 16, 16, (90, 200, 120))
        q.ell(cx + 112, hy - 18, 16, 16, (90, 200, 120))
    elif hair == "bangs":  # straight fringe
        q.chord(cx, hy - 18, 230, 168, 180, 360, hc)
        q.rect(cx - 96, hy - 82, cx + 96, hy - 44, hc, ol=None)
        q.line([(cx - 96, hy - 44), (cx + 96, hy - 44)], w=OUT)
    elif hair == "mop":  # long shaggy mop over the ears
        q.chord(cx, hy - 14, 240, 188, 180, 360, hc)
        for i in range(8):
            x = cx - 105 + i * 30
            q.ell(x, hy - 40 + (0 if 1 < i < 6 else 26), 44, 40, hc, ol=None)
        q.arc(cx, hy - 14, 240, 188, 180, 360, wd=OUT)
    elif hair == "curly":
        for i in range(9):
            a = math.pi + i * math.pi / 8
            q.ell(cx + 100 * math.cos(a), hy - 10 + 85 * math.sin(a), 56, 56, hc)
    # eyes
    es = eye_s
    ex, ey = 26 * es, hy - 18 - 6 * (es - 1)
    if eyes == "blink":
        q.line([(cx - ex - 24, ey), (cx - ex + 24, ey)], w=4)
        q.line([(cx + ex - 24, ey), (cx + ex + 24, ey)], w=4)
    elif eyes == "squint":
        q.ell(cx - ex, ey + 6, 54, 34, (255, 255, 255), ow=2)
        q.ell(cx + ex, ey + 6, 54, 34, (255, 255, 255), ow=2)
        q.ell(cx - ex + 6, ey + 8, 9, 9, INK, ol=None)
        q.ell(cx + ex - 6, ey + 8, 9, 9, INK, ol=None)
        q.line([(cx - ex - 26, ey - 8), (cx - ex + 24, ey - 12)], w=5)
        q.line([(cx + ex + 26, ey - 8), (cx + ex - 24, ey - 12)], w=5)
    else:
        q.ell(cx - ex, ey, 54 * es, 62 * es, (255, 255, 255), ow=2)
        q.ell(cx + ex, ey, 54 * es, 62 * es, (255, 255, 255), ow=2)
        q.ell(cx - ex + 6 + look, ey + 4, 9, 9, INK, ol=None)
        q.ell(cx + ex - 6 + look + (6 if look else 0), ey + 4, 9, 9, INK, ol=None)
        if eyes == "angry":
            q.line([(cx - ex - 28, ey - 34), (cx - 4, ey - 18)], w=5)
            q.line([(cx + ex + 28, ey - 34), (cx + 4, ey - 18)], w=5)
        elif eyes == "worried":
            q.line([(cx - ex - 26, ey - 22), (cx - 6, ey - 36)], w=5)
            q.line([(cx + ex + 26, ey - 22), (cx + 6, ey - 36)], w=5)
    if brows and eyes not in ("angry", "worried", "squint"):
        bc = (150, 150, 150) if brows == "grey" else hc
        q.poly([(cx - ex - 26, ey - 36), (cx - 6, ey - 40), (cx - 6, ey - 32), (cx - ex - 26, ey - 28)], bc, ow=1)
        q.poly([(cx + ex + 26, ey - 36), (cx + 6, ey - 40), (cx + 6, ey - 32), (cx + ex + 26, ey - 28)], bc, ow=1)
    if glasses:
        q.arc(cx - ex, ey, 64, 70, 0, 360, wd=3)
        q.arc(cx + ex, ey, 64, 70, 0, 360, wd=3)
    if nose == "dot":
        q.ell(cx, hy + 26, 12, 9, tuple(int(v * 0.8) for v in sk), ol=None)
    elif nose == "button":
        q.ell(cx, hy + 24, 22, 18, tuple(int(v * 0.92) for v in sk), ow=2)
    elif nose == "long":
        q.poly([(cx - 4, hy + 2), (cx + 18, hy + 34), (cx - 6, hy + 36)], tuple(int(v * 0.92) for v in sk), ow=2)
    elif nose == "wide":
        q.ell(cx, hy + 26, 36, 18, tuple(int(v * 0.9) for v in sk), ow=2)
    my = hy + 54
    if beard:
        q.chord(cx, hy + 40, 170, 140, 0, 180, hair_col if hair_col != (0, 0, 0) else (60, 40, 30), ol=None)
    if mustache:
        mc = mustache if isinstance(mustache, tuple) else hair_col
        q.ell(cx - 16, my - 14, 40, 16, mc, ol=None)
        q.ell(cx + 16, my - 14, 40, 16, mc, ol=None)
    if mouth == "open":
        q.chord(cx, my - 6, 44, 40, 0, 180, (110, 20, 30), ow=2)
    elif mouth == "shout":
        q.ell(cx, my, 50, 46, (110, 20, 30), ow=2)
    elif mouth == "smile":
        q.arc(cx, my - 10, 46, 26, 20, 160, wd=3)
    elif mouth == "frown":
        q.arc(cx, my + 6, 40, 22, 200, 340, wd=3)
    elif mouth == "pout":  # pursed "O"
        q.ell(cx, my - 2, 22, 18, (150, 50, 60), ow=2)
    else:
        q.line([(cx - 12, my), (cx + 12, my)], w=3)
    if hat == "police":
        q.chord(cx, hy - 66, 200, 110, 180, 360, (30, 45, 90))
        q.rect(cx - 104, hy - 70, cx + 104, hy - 56, (20, 20, 25))
        q.ell(cx, hy - 92, 22, 22, (230, 200, 60))
    elif hat == "cap":
        q.chord(cx, hy - 44, 230, 150, 180, 360, hcol)
        q.poly([(cx + 30, hy - 50), (cx + 160, hy - 46), (cx + 140, hy - 30), (cx + 30, hy - 34)], dark)
    elif hat == "bobble":  # striped knitted beanie with a pom-pom
        q.chord(cx, hy - 30, 236, 196, 180, 360, hcol)
        for k_ in range(2):
            q.chord(cx, hy - 30, 236 - 40 * k_ - 40, 196 - 40 * k_ - 40, 180, 360, None, ol=dark, ow=6)
        q.rect(cx - 120, hy - 46, cx + 120, hy - 18, dark, r=10)
        q.ell(cx, hy - 132, 44, 44, (245, 245, 245) if sum(hcol) < 600 else (220, 60, 60))
    elif hat == "earflap":  # trapper hat with flaps down
        q.chord(cx, hy - 28, 236, 190, 180, 360, hcol)
        q.rect(cx - 126, hy - 40, cx - 96, hy + 52, hcol, r=14)
        q.rect(cx + 96, hy - 40, cx + 126, hy + 52, hcol, r=14)
        q.rect(cx - 118, hy - 54, cx + 118, hy - 30, dark, r=10)
    elif hat == "hood":  # opening of the hood around the face
        q.arc(cx, hy + 4, 236, 214, 0, 360, fill=dark, wd=8)
        q.line([(cx - 10, hy + 108), (cx - 16, hy + 150)], fill=dark, w=4)
        q.line([(cx + 10, hy + 108), (cx + 16, hy + 150)], fill=dark, w=4)
    elif hat == "bucket":
        q.poly([(cx - 90, hy - 120), (cx + 90, hy - 120), (cx + 104, hy - 56), (cx - 104, hy - 56)], hcol)
        q.ell(cx, hy - 52, 280, 40, hcol)
    elif hat == "headband":
        q.rect(cx - 114, hy - 66, cx + 114, hy - 44, hcol, r=10)
    elif hat == "beret":
        q.ell(cx - 20, hy - 92, 220, 70, hcol)
        q.ell(cx - 10, hy - 126, 16, 22, dark, ol=None)
    elif hat == "clip":  # flower hair clip
        for k_ in range(5):
            ang = k_ * 2 * math.pi / 5
            q.ell(cx + 70 + 14 * math.cos(ang), hy - 70 + 14 * math.sin(ang), 18, 18, hcol)
        q.ell(cx + 70, hy - 70, 12, 12, (250, 220, 80))
    elif hat == "helmet":
        q.chord(cx, hy - 50, 220, 150, 180, 360, (40, 50, 70))
        q.rect(cx - 70, hy - 66, cx + 70, hy - 30, (150, 200, 230), ow=2)
    head = q.im
    if abs(head_h - 1) > 1e-3:  # stretch/squash vertically about the chin (y=236)
        chin = (236 + TOP) * K
        top = head.crop((0, 0, head.width, chin))
        nh = int(chin * head_h)
        top = top.resize((head.width, nh), Image.LANCZOS)
        hh = Image.new("RGBA", head.size, (0, 0, 0, 0))
        hh.alpha_composite(top.crop((0, max(0, nh - chin), head.width, nh)), (0, max(0, chin - nh)))
        hh.alpha_composite(head.crop((0, chin, head.width, head.height)), (0, chin))
        head = hh
    if abs(head_w - 1) > 1e-3:
        nw = int(head.width * head_w)
        head = head.resize((nw, head.height), Image.LANCZOS)
        pad = Image.new("RGBA", q.im.size, (0, 0, 0, 0))
        pad.alpha_composite(head.crop((max(0, (nw - q.im.width) // 2), 0,
                                       max(0, (nw - q.im.width) // 2) + min(nw, q.im.width), head.height)),
                            (max(0, (q.im.width - nw) // 2), 0))
        head = pad
    p.im.alpha_composite(head)
    p.im.alpha_composite(front.im)
    im = p.done()
    if flip:  # flip the body first, then add props so their text never reads backwards
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    sign = None
    if hold:
        hand = (300 - (br - 2) if flip else br - 2, TOP + 344, sk)
        if detach_sign and hold_is_sign(hold):
            # board drawn as its own layer above the crowd so nobody in front can hide it
            sign = sign_layout(hold, TOP, flip, hand)
            im = add_hold(im, None, TOP, mirror=flip, hand=hand)
        else:
            im = add_hold(im, hold, TOP, mirror=flip, hand=hand)
    s = scale * height
    if s != 1.0:
        im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        if sign:
            b, bx, by = sign
            sign = (b.resize((max(1, int(b.width * s)), max(1, int(b.height * s))), Image.LANCZOS), bx * s, by * s)
    if sign:
        im.info["sign_board"] = sign
    return im


TOP = 80  # headroom above every character for tall hair and hats


def hold_is_sign(what):
    return isinstance(what, tuple) and what and what[0] == "sign"


def sign_layout(what, top, mirror, hand):
    """Sign board image and its top-left position inside the holder's sprite."""
    pr = sign_board(what[1], what[2] if len(what) > 2 else (255, 250, 230), size=40)
    rx = 300 - hand[0] if mirror else hand[0]
    x, y = rx - pr.width * 0.6, top + 40 - pr.height + 8
    if mirror:
        x = 300 - x - pr.width
    return pr, x, y


def add_hold(im, what, top=0, mirror=False, hand=None):
    """Put a prop in the character's right hand (hand=(x, y, skin) in image pixels), then redraw the
    hand over it so the fingers visibly grip it. mirror=True for flipped characters: positions are
    mirrored but the prop itself is never mirrored, so its text stays readable."""
    hx, hy_, sk = hand if hand else (210, top + 344, SKIN["light"])

    def put(pr, x, y):  # x, y: prop top-left for an unflipped character
        if mirror:
            x = 300 - x - pr.width
        im.alpha_composite(pr, (int(x), int(y)))

    rx = 300 - hx if mirror else hx  # hand x as if unflipped
    if what == "phone":
        pr = phone(scale=0.32)
        put(pr, rx - pr.width // 2, hy_ - pr.height + 18)
    elif what == "mic":
        p = Pen(80, 140)
        p.rect(34, 50, 46, 130, (60, 60, 60))
        p.ell(40, 40, 46, 56, (90, 90, 90))
        pr = p.done(shadow=False)
        put(pr, rx - 40, hy_ - 120)
    elif what == "briefcase":
        p = Pen(120, 100)
        p.rect(10, 25, 110, 95, (120, 70, 30), r=8)
        p.rect(40, 8, 80, 28, None)
        pr = p.done(shadow=False)
        put(pr, rx - 60, hy_ - 12)
    elif what == "cane":
        p = Pen(60, 200)
        p.line([(30, 30), (30, 195)], fill=(110, 70, 30), w=8)
        p.arc(16, 30, 30, 30, 180, 360, fill=(110, 70, 30), wd=8)
        pr = p.done(shadow=False)
        put(pr, rx - 30, hy_ - 30)
    elif what == "magnifier":  # handle in the hand, glass held up and out to the side
        p = Pen(110, 200)
        p.line([(18, 188), (62, 92)], fill=(110, 70, 30), w=12)
        p.ell(70, 62, 70, 70, (200, 235, 255), ow=6)
        p.arc(62, 54, 40, 40, 200, 260, fill=(255, 255, 255), wd=5)
        pr = p.done(shadow=False)
        put(pr, rx - 18, hy_ - 188)
    elif hold_is_sign(what):  # board above the head on the stick (stick is drawn in person())
        pr, x, y = sign_layout(what, top, mirror, (hx, hy_, sk))
        im.alpha_composite(pr, (int(x), int(y)))
    if hand and what != "phone":
        p = Pen(40, 40)
        p.ell(20, 20, 30, 30, sk)
        hd = p.done(shadow=False, paper=False)
        im.alpha_composite(hd, (int(hx - 20), int(hy_ - 20)))
    return im


def sign_board(txt, col=(255, 250, 230), size=34):
    lines = txt.split("\n")
    tw = max(text_size(l, size)[0] for l in lines) + 40
    th = len(lines) * (size + 8) + 30
    p = Pen(tw + 10, th + 10)
    p.rect(5, 5, tw, th, col, r=6)
    for i, l in enumerate(lines):
        p.text((tw + 5) / 2, 20 + size / 2 + i * (size + 8) + 4, l, size, fill=INK)
    return p.done(shadow=False)


# named characters --------------------------------------------------------------------

# Recognisable traits are drawn from each real person's public appearance (build, hair, signature
# clothing). Keep them as gentle caricature: exaggerate what people recognise, never mock.
CAST = {
    "dom": dict(skin="light", hair="short", hair_col=(95, 60, 35), outfit="shirt", col=(60, 120, 190)),
    # Santiago Pena: 47, solid build, round face, short dark side-parted hair, presidential sash
    "pena": dict(skin="tan", hair="side", hair_col=(35, 28, 25), outfit="suit", col=(35, 45, 80),
                 tie=(40, 70, 160), sash=True, build=1.15, head_w=1.06, pin="py", head="round"),
    "pena_nosash": dict(skin="tan", hair="side", hair_col=(35, 28, 25), outfit="suit", col=(35, 45, 80),
                        tie=(40, 70, 160), build=1.15, head_w=1.06, head="round"),
    # Trump: big frame, blond swept comb-over, orange tan, long wide red tie, flag pin, pursed mouth
    "trump": dict(skin="orange", hair="swoop", hair_col=(242, 206, 110), outfit="longtie", col=(28, 36, 70),
                  tie=(215, 25, 35), tie_w=1.5, build=1.42, height=1.08, head_w=1.12, jowls=True,
                  pin="us", brows="thick", rest="pout", head="round"),
    # Horacio Cartes: older, heavy-set, bald with grey sides, businessman's grey suit
    "cartes": dict(skin="light", hair="bald", hair_col=(190, 190, 190), outfit="suit", col=(80, 80, 85),
                   tie=(200, 40, 40), old=True, build=1.38, head_w=1.08, jowls=True, brows="grey", head="round",
                   head_h=0.96),
    # Marco Rubio: slim, youthful, short dark hair, thick dark eyebrows
    "rubio": dict(skin="tan", hair="short", hair_col=(40, 30, 25), outfit="suit", col=(40, 45, 60),
                  tie=(60, 90, 170), build=0.92, brows="thick", pin="us", head="round", head_h=1.05, head_w=0.95),
    # Scott Bessent: tall and lean, neat silver hair swept back
    "bessent": dict(skin="light", hair="slick", hair_col=(205, 205, 210), outfit="suit", col=(40, 45, 60),
                    tie=(140, 40, 60), build=0.85, height=1.06, head_w=0.95, pin="us", head="round",
                    head_h=1.06),
    "cbchief": dict(skin="light", hair="side", hair_col=(120, 120, 120), outfit="suit", col=(90, 95, 105),
                    tie=(40, 120, 90), glasses=True, build=0.95),
    "newchief": dict(skin="tan", hair="short", hair_col=(50, 40, 30), outfit="suit", col=(70, 60, 90),
                     tie=(200, 160, 40), build=1.1),
    "regulator": dict(skin="brown", hair="short", hair_col=(30, 25, 20), outfit="suit", col=(80, 80, 90),
                      tie=(90, 60, 160), glasses=True, build=0.9),
    "finchief": dict(skin="tan", hair="bun", hair_col=(60, 35, 25), outfit="dress", col=(150, 50, 90),
                     glasses=True, build=0.95),
    "senator": dict(skin="brown", hair="curly", hair_col=(30, 25, 20), outfit="suit", col=(110, 40, 40),
                    tie=(240, 200, 60), mustache=True, build=1.2),
    "exec": dict(skin="light", hair="slick", hair_col=(40, 30, 25), outfit="suit", col=(25, 25, 30),
                 tie=(20, 140, 120), build=1.05),
    "lawyer": dict(skin="brown", hair="short", hair_col=(25, 20, 15), outfit="suit", col=(60, 50, 40),
                   tie=(120, 30, 30), glasses=True, build=0.9),
    # Pedro Alliana: heavier build, dark hair, thick moustache
    "alliana": dict(skin="tan", hair="short", hair_col=(30, 25, 20), outfit="suit", col=(50, 70, 50),
                    tie=(200, 40, 40), mustache=True, build=1.3, head_w=1.05, brows="thick", head="round"),
    # Fernando Lugo: former Catholic bishop - lean, white beard, bald crown, open shirt, small cross
    "lugo": dict(skin="tan", hair="bald", hair_col=(225, 225, 225), outfit="shirt", col=(150, 130, 100),
                 beard=True, cross=True, build=0.88, head="round", head_h=1.04),
    "cop": dict(skin="tan", hair="short", outfit="uniform", col=(40, 60, 110), hat="police",
                pants=(30, 40, 80), build=1.1),
    "riot": dict(skin="tan", hair="short", outfit="uniform", col=(35, 40, 55), hat="helmet",
                 pants=(30, 30, 40), build=1.2),
    "player": dict(skin="tan", hair="short", outfit="jersey", col=(210, 35, 45), pants=(40, 60, 160),
                   build=0.95, height=1.04),
    "reporter": dict(skin="light", hair="long", hair_col=(170, 110, 50), outfit="shirt", col=(80, 150, 90),
                     hold="mic", build=0.9),
    "pensioner": dict(skin="light", hair="bald", hair_col=(225, 225, 225), outfit="shirt", col=(150, 120, 90),
                      old=True, glasses=True, hold="cane", build=0.9, height=0.95),
    "granny": dict(skin="tan", hair="bun", hair_col=(220, 220, 220), outfit="dress", col=(120, 90, 160),
                   old=True, glasses=True, build=1.05, height=0.92),
}

HEADS = ["round"]  # house style: every head is a circle; variety comes from hair, hats, size and colour
HATS = [None, None, None, "bobble", "earflap", "hood", "cap", "bucket", "headband", "beret", "clip"]
HAIRS = ["short", "side", "slick", "spiky", "messy", "curly", "afro", "bob", "pigtails", "bangs", "mop",
         "ponytail", "bun", "long", "receding", "bald", "buzz", "mohawk"]
HAT_COLS = [(220, 60, 60), (60, 120, 200), (70, 170, 90), (240, 190, 60), (150, 80, 170), (240, 130, 40),
            (230, 120, 170), (60, 170, 170), (90, 90, 100)]


def varied(seed, **kw):
    """Look-variety for generic characters (players, senators, extras) - same random pool as crowds."""
    rng = random.Random(seed * 104729)
    d = dict(head="round", head_h=rng.choice([0.96, 1.0, 1.04]), head_w=rng.choice([0.96, 1.0, 1.05]),
             eye_s=rng.choice([0.95, 1.0, 1.05]), hat=rng.choice(HATS[:3] + ["cap", "headband", "beret"]),
             hat_col=rng.choice(HAT_COLS),
             hair=rng.choice(["short", "curly", "side", "spiky", "messy", "buzz", "receding", "afro", "slick",
                              "mop", "bangs"]),
             hair_col=rng.choice([(40, 30, 20), (90, 55, 25), (20, 20, 20), (180, 130, 60), (130, 80, 40)]),
             build=rng.choice([0.85, 0.95, 1.0, 1.1, 1.25]))
    d.update(kw)
    return d


CROWD_COLS = [(220, 90, 60), (70, 150, 200), (240, 190, 60), (110, 180, 90), (170, 90, 170), (230, 120, 160),
              (90, 90, 180), (60, 170, 160), (200, 60, 60)]
CROWD_HAIR = [(40, 30, 20), (90, 55, 25), (20, 20, 20), (180, 130, 60), (130, 80, 40), (210, 210, 210)]
CROWD_SKIN = ["light", "tan", "brown", "pale", "tan"]


@functools.lru_cache(None)
def char(name, mouth="closed", eyes="normal", flip=False, scale=1.0, **kw):
    d = dict(CAST[name])
    rest = d.pop("rest", "closed")  # the person's signature resting expression
    if mouth == "closed":
        mouth = rest
    d.update(kw)
    d.update(mouth=mouth, eyes=eyes, flip=flip, scale=scale)
    return person(**d)


def char_set(name, scale=1.0, flip=False, mouth="closed", eyes="normal", **kw):
    """Variants for talking/blinking."""
    kw = tuple(sorted(kw.items()))
    base = dict(kw)
    open_m = "shout" if mouth == "shout" else "open"
    return {"closed": char(name, mouth=mouth if mouth != "shout" else "open", eyes=eyes, flip=flip,
                           scale=scale, **base),
            "open": char(name, mouth=open_m, eyes=eyes, flip=flip, scale=scale, **base),
            "blink": char(name, mouth=mouth if mouth != "shout" else "open", eyes="blink", flip=flip,
                          scale=scale, **base)}


@functools.lru_cache(None)
def crowd_person(i, scale=0.6, mouth="closed", eyes="normal", hold=None, flip=False, arms="down",
                 detach_sign=False):
    rng = random.Random(i * 7919)
    return person(detach_sign=detach_sign, skin=rng.choice(CROWD_SKIN), hair=rng.choice(HAIRS), hat=rng.choice(HATS),
                  hat_col=rng.choice(HAT_COLS), head="round", head_h=rng.choice([0.96, 1.0, 1.04]),
                  eye_s=rng.choice([0.95, 1.0, 1.0, 1.05]),
                  hair_col=rng.choice(CROWD_HAIR), outfit="shirt", col=rng.choice(CROWD_COLS),
                  mouth=mouth, eyes=eyes, scale=scale, hold=hold, flip=flip, arms=arms,
                  glasses=rng.random() < 0.2, pants=rng.choice([(50, 50, 60), (40, 60, 120), (90, 70, 50)]),
                  build=rng.choice([0.85, 0.95, 1.0, 1.1, 1.25, 1.4]), height=rng.choice([0.92, 1.0, 1.0, 1.06]),
                  head_w=rng.choice([0.96, 1.0, 1.04, 1.08]))


# ----------------------------------------------------------------------------- props

def phone(scale=1.0, screen="app", txt=None):
    p = Pen(220, 400)
    p.rect(10, 10, 210, 390, (35, 35, 40), r=28)
    p.rect(24, 40, 196, 350, (230, 250, 245) if screen != "error" else (250, 230, 230), ow=2, r=8)
    if screen == "app":
        p.rect(24, 40, 196, 110, (20, 150, 125), ol=None)
        p.text(110, 76, "ueno", 40, fill=(255, 255, 255))
        for i, (lab, c) in enumerate([("CASHBACK", (240, 190, 60)), ("SAVINGS", (110, 180, 90)),
                                      ("PAY", (90, 150, 220))]):
            p.rect(40, 130 + i * 70, 180, 185 + i * 70, c, r=10, ow=2)
            p.text(110, 158 + i * 70, lab, 22, fill=INK)
    elif screen == "error":
        p.line([(70, 140), (150, 240)], fill=(200, 30, 30), w=16)
        p.line([(150, 140), (70, 240)], fill=(200, 30, 30), w=16)
        p.text(110, 290, "ERROR", 30, fill=(200, 30, 30))
    elif screen == "locked":
        p.rect(70, 170, 150, 250, (230, 190, 60), r=8)
        p.arc(110, 170, 60, 80, 180, 360, wd=10)
        p.text(110, 300, "LOCKED", 28, fill=(200, 30, 30))
    elif screen == "icons":
        for i, (lab, c) in enumerate([("SALARY", (240, 190, 60)), ("SAVINGS", (110, 180, 90)),
                                      ("PENSION", (220, 120, 160))]):
            p.rect(36, 70 + i * 92, 184, 140 + i * 92, c, r=12, ow=2)
            p.text(110, 106 + i * 92, lab, 28, fill=INK)
    elif screen == "brand":  # another bank's app, shown by name only
        p.rect(24, 40, 196, 110, (90, 90, 110), ol=None)
        p.text(110, 76, txt or "", 30 if len(txt or "") < 7 else 24, fill=(255, 255, 255))
        for i in range(3):
            p.rect(40, 130 + i * 70, 180, 185 + i * 70, (210, 210, 220), r=10, ow=2)
    elif screen == "video":
        p.rect(24, 40, 196, 350, (30, 30, 50), ow=2, r=8)
    p.ell(110, 370, 22, 12, (80, 80, 80), ol=None)
    im = p.done()
    if scale != 1:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    return im


def building(kind="bank", w=560, h=460, label=None, col=None):
    p = Pen(w, h)
    if kind in ("bank", "central", "congress", "court", "ips", "treasury"):
        c = col or {"bank": (230, 245, 240), "central": (235, 225, 200), "congress": (240, 235, 225),
                    "court": (230, 230, 235), "ips": (225, 235, 250), "treasury": (235, 235, 230)}[kind]
        p.rect(30, h - 40, w - 30, h - 5, (190, 185, 175))
        p.rect(50, 150, w - 50, h - 40, c)
        p.poly([(30, 150), (w / 2, 40), (w - 30, 150)], c)
        n = 5
        for i in range(n):
            x = 80 + i * (w - 160) / (n - 1)
            p.rect(x - 16, 175, x + 16, h - 50, (255, 255, 250), ow=2)
        if kind == "bank":
            p.rect(w / 2 - 50, h - 150, w / 2 + 50, h - 40, (90, 60, 40))
        if kind == "congress":
            p.ell(w / 2, 40, 140, 90, (200, 220, 230))
        if label:
            tw = text_size(label, 44)[0]
            p.rect(w / 2 - tw / 2 - 18, 108, w / 2 + tw / 2 + 18, 156, (20, 150, 125) if kind == "bank"
                   else (250, 245, 230), r=8)
            p.text(w / 2, 133, label, 44, fill=(255, 255, 255) if kind == "bank" else INK)
    elif kind == "capitol":
        p.rect(20, h - 150, w - 20, h - 10, (245, 245, 240))
        for i in range(9):
            x = 50 + i * (w - 100) / 8
            p.rect(x - 9, h - 140, x + 9, h - 20, (255, 255, 255), ow=2)
        p.rect(w / 2 - 110, h - 230, w / 2 + 110, h - 150, (245, 245, 240))
        p.chord(w / 2, h - 230, 220, 240, 180, 360, (245, 245, 240))
        p.rect(w / 2 - 10, h - 380, w / 2 + 10, h - 340, (245, 245, 240))
        p.ell(w / 2, h - 384, 26, 26, (245, 245, 240))
    elif kind == "office":
        p.rect(40, 60, w - 40, h - 5, col or (120, 160, 190))
        for r in range(4):
            for c in range(4):
                x = 70 + c * (w - 140) / 4
                y = 90 + r * (h - 120) / 4
                p.rect(x, y, x + (w - 140) / 4 - 25, y + (h - 120) / 4 - 30, (200, 230, 250), ow=2)
        if label:
            p.rect(w / 2 - 120, 20, w / 2 + 120, 74, (20, 150, 125), r=8)
            p.text(w / 2, 47, label, 42, fill=(255, 255, 255))
    return p.done()


def money_bag(label="$", scale=1.0):
    p = Pen(200, 220)
    p.ell(100, 140, 180, 150, (200, 170, 100))
    p.poly([(70, 70), (130, 70), (115, 40), (85, 40)], (200, 170, 100))
    p.line([(72, 72), (128, 72)], w=6)
    p.text(100, 145, label, 60 if len(label) < 3 else 36, fill=(40, 110, 50))
    im = p.done()
    return im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS) if scale != 1 else im


def coin(scale=1.0):
    p = Pen(70, 70)
    p.ell(35, 35, 60, 60, (240, 200, 60))
    p.text(35, 37, "$", 34, fill=(170, 120, 20))
    im = p.done(shadow=False)
    return im.resize((int(70 * scale), int(70 * scale)), Image.LANCZOS) if scale != 1 else im


def cash_stack(scale=1.0):
    p = Pen(220, 120)
    for i in range(4):
        p.rect(10 + i * 4, 70 - i * 18, 200 + i * 4, 105 - i * 18, (130, 200, 120), ow=2)
        p.ell(105 + i * 4, 88 - i * 18, 26, 22, (90, 160, 90), ow=2)
    im = p.done()
    return im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS) if scale != 1 else im


def ice_block(w=520, h=380):
    p = Pen(w, h)
    p.rect(10, 10, w - 10, h - 10, (190, 230, 250, 170), ol=(120, 180, 220), ow=5, r=18)
    p.line([(40, 50), (120, 40)], fill=(255, 255, 255), w=8)
    p.line([(40, 80), (70, 76)], fill=(255, 255, 255), w=8)
    p.line([(w - 80, h - 60), (w - 40, h - 90)], fill=(255, 255, 255), w=6)
    return p.done(shadow=False)


def vault(w=420, h=420):
    p = Pen(w, h)
    p.rect(20, 20, w - 20, h - 20, (150, 155, 165), r=20)
    p.ell(w / 2, h / 2, w * 0.7, h * 0.7, (175, 180, 190), ow=5)
    p.ell(w / 2, h / 2, 60, 60, (120, 120, 130))
    for a in range(0, 360, 60):
        r = math.radians(a)
        p.line([(w / 2, h / 2), (w / 2 + 110 * math.cos(r), h / 2 + 110 * math.sin(r))], w=10)
    p.text(w / 2, 50, "ueno", 36, fill=(20, 150, 125))
    return p.done()


def gavel(scale=1.0):
    p = Pen(420, 200)
    p.rect(150, 86, 410, 112, (140, 85, 40), r=8)
    p.rect(40, 30, 170, 170, (150, 90, 45), r=16)
    p.rect(60, 30, 80, 170, (110, 65, 30), ol=None)
    p.rect(130, 30, 150, 170, (110, 65, 30), ol=None)
    p.rect(40, 30, 170, 170, None, r=16)
    im = p.done()
    return im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS) if scale != 1 else im


def sound_block():
    p = Pen(300, 90)
    p.ell(150, 55, 280, 60, (130, 80, 40))
    p.rect(10, 30, 290, 55, (150, 95, 45), ol=None)
    p.ell(150, 30, 280, 50, (165, 105, 55))
    return p.done()


def stamp(txt, col=(200, 30, 40), size=70, rot=-12):
    tw, th = text_size(txt, size)
    p = Pen(tw + 80, th + 70)
    p.rect(10, 10, tw + 70, th + 60, None, ol=col, ow=8, r=10)
    p.text((tw + 80) / 2, (th + 70) / 2 + 4, txt, size, fill=col)
    im = p.done(shadow=False, paper=False)
    # rough stamp texture
    a = np.asarray(im.getchannel("A")).astype(np.float32)
    rng = np.random.default_rng(len(txt))
    mask = rng.random(a.shape) > 0.12
    im.putalpha(Image.fromarray((a * mask * 0.9).astype(np.uint8)))
    im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    im.info.update(kind="stamp", text=txt)
    return im


def label(txt, size=56, bg=(255, 252, 235), fg=INK, rot=0.0, kind="title", pad=26):
    lines = txt.split("\n")
    lh = int(size * 1.15)
    tw = max(text_size(l, size, kind)[0] for l in lines)
    w, h = tw + pad * 2, lh * len(lines) + pad * 2 - int(size * 0.15)
    p = Pen(w + 10, h + 10)
    # torn paper strip
    rng = random.Random(txt)
    pts = []
    for x in range(0, w + 1, 18):
        pts.append((5 + x, 5 + rng.uniform(-3, 3)))
    for y in range(0, h + 1, 18):
        pts.append((5 + w + rng.uniform(-3, 3), 5 + y))
    for x in range(w, -1, -18):
        pts.append((5 + x, 5 + h + rng.uniform(-3, 3)))
    for y in range(h, -1, -18):
        pts.append((5 + rng.uniform(-3, 3), 5 + y))
    p.poly(pts, bg, ow=2)
    for i, l in enumerate(lines):
        p.text((w + 10) / 2, 5 + pad + lh * i + size * 0.5, l, size, fill=fg, kind=kind)
    im = p.done()
    if rot:
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
    im.info.update(kind="label", text=txt)
    return im


def bubble(txt, size=46, tail="left", w_max=None):
    """Speech bubble sized so the text block sits fully inside the ellipse (x1.42 of the text box)."""
    lines = txt.split("\n")
    lh = int(size * 1.2)
    tw = max(text_size(l, size, "hand")[0] for l in lines)
    th = lh * len(lines)
    w, h = (tw + 30) * 1.42, (th + 16) * 1.42
    p = Pen(int(w + 20), int(h + 80))
    cx, cy = 10 + w / 2, 10 + h / 2
    p.ell(cx, cy, w, h, (255, 255, 255), ow=4)
    s = 1 if tail == "left" else -1
    bx = cx - s * w * 0.22
    p.poly([(bx - 0.08 * w, cy + h * 0.36), (cx - s * w * 0.36, h + 72), (bx + 0.08 * w, cy + h * 0.38)],
           (255, 255, 255), ow=4)
    p.ell(bx, cy + h * 0.33, 0.2 * w, 0.12 * h, (255, 255, 255), ol=None)
    for i, l in enumerate(lines):
        p.text(cx, cy - th / 2 + lh * (i + 0.5), l, size, kind="hand")
    im = p.done()
    im.info.update(kind="bubble", text=txt, tail=tail, tip=(cx - s * w * 0.36, h + 72), ellipse=(cx, cy, w / 2 - 2, h / 2 - 2),
                   textbox=(cx - tw / 2, cy - th / 2, cx + tw / 2, cy + th / 2))
    return im


def document(title="", lines=6, w=300, h=380, col=(255, 255, 250)):
    p = Pen(w, h)
    p.poly([(10, 10), (w - 60, 10), (w - 10, 60), (w - 10, h - 10), (10, h - 10)], col)
    p.poly([(w - 60, 10), (w - 60, 60), (w - 10, 60)], (230, 230, 220))
    if title:
        p.text(w / 2 - 10, 50, title, 30 if len(title) < 14 else 24)
    for i in range(lines):
        y = 100 + i * ((h - 140) / max(lines, 1))
        p.line([(40, y), (w - 40 - (i % 3) * 30, y)], fill=(150, 150, 150), w=4)
    return p.done()


def paper_stack(h_count=8):
    p = Pen(360, 120 + h_count * 18)
    for i in range(h_count):
        y = 100 + h_count * 18 - i * 18
        p.rect(20 + (i % 2) * 6, y - 20, 330 + (i % 2) * 6, y, (255, 255, 248), ow=2)
    p.rect(20, 10, 336, 100 + 0, (255, 255, 248), ow=2)
    p.text(178, 56, "200 PAGES", 40)
    return p.done()


def jail_bars(w=360, h=420):
    p = Pen(w, h)
    p.rect(10, 10, w - 10, h - 10, None, ol=(60, 60, 70), ow=10)
    for i in range(6):
        x = 10 + (i + 1) * (w - 20) / 7
        p.rect(x - 7, 10, x + 7, h - 10, (110, 110, 120), ow=2)
    p.rect(10, h / 2 - 10, w - 10, h / 2 + 10, (110, 110, 120), ow=2)
    return p.done(shadow=False)


def yacht():
    p = Pen(620, 300)
    p.poly([(20, 190), (600, 190), (520, 280), (80, 280)], (250, 250, 255))
    p.line([(60, 235), (560, 235)], fill=(20, 150, 200), w=8)
    p.poly([(160, 190), (180, 120), (440, 120), (480, 190)], (240, 240, 245))
    p.poly([(220, 120), (240, 70), (380, 70), (400, 120)], (235, 235, 240))
    for x in range(200, 440, 50):
        p.rect(x, 140, x + 30, 168, (60, 120, 170), ow=2)
    return p.done()


def plane():
    p = Pen(600, 260)
    p.ell(300, 130, 520, 80, (245, 245, 250))
    p.poly([(230, 130), (350, 130), (300, 250), (260, 250)], (220, 220, 230))
    p.poly([(60, 120), (100, 120), (70, 40), (40, 40)], (220, 220, 230))
    for x in range(330, 500, 40):
        p.ell(x, 118, 22, 18, (80, 140, 200), ow=2)
    p.ell(560, 130, 30, 60, (120, 120, 130))
    return p.done()


def dam(w=600, h=360):
    p = Pen(w, h)
    p.rect(0, 40, w, 140, (90, 160, 220), ol=None)
    p.poly([(60, 60), (w - 60, 60), (w - 20, h - 20), (20, h - 20)], (200, 200, 195))
    for i in range(5):
        x = 110 + i * (w - 220) / 4
        p.rect(x - 22, 140, x + 22, h - 20, (90, 160, 220), ow=2)
    return p.done()


def scales():
    p = Pen(520, 420)
    p.rect(250, 60, 270, 380, (200, 160, 60))
    p.rect(170, 370, 350, 400, (200, 160, 60))
    p.line([(60, 90), (460, 90)], fill=(200, 160, 60), w=12)
    for x in (80, 440):
        p.line([(x, 90), (x - 50, 220)], w=3)
        p.line([(x, 90), (x + 50, 220)], w=3)
        p.chord(x, 210, 140, 70, 0, 180, (220, 180, 70))
    p.ell(260, 55, 34, 34, (220, 180, 70))
    return p.done()


def ballot_box():
    p = Pen(300, 300)
    p.rect(20, 80, 280, 290, (240, 240, 245))
    p.rect(100, 70, 200, 90, INK)
    p.rect(110, 10, 190, 80, (255, 255, 250), ow=2)
    p.text(150, 45, "X", 40, fill=(200, 30, 40))
    p.text(150, 190, "VOTE", 54, fill=(40, 70, 160))
    return p.done()


def rocket_chart(w=760, h=480):
    p = Pen(w, h)
    p.rect(10, 10, w - 10, h - 10, (255, 253, 240), r=10)
    for i in range(1, 5):
        p.line([(60, 10 + i * (h - 20) / 5), (w - 30, 10 + i * (h - 20) / 5)], fill=(210, 210, 200), w=2)
    p.line([(60, h - 40), (w - 30, h - 40)], w=4)
    p.line([(60, 30), (60, h - 40)], w=4)
    pts = [(70, h - 70), (200, h - 100), (330, h - 170), (460, h - 240), (580, h - 340), (690, h - 420)]
    p.line(pts, fill=(20, 150, 125), w=14)
    p.poly([(690, h - 450), (720, h - 395), (660, h - 405)], (20, 150, 125))
    return p.done()


def risk_meter(level=0.8):
    p = Pen(420, 300)
    p.pie(210, 220, 380, 380, 180, 240, (220, 60, 50))
    p.pie(210, 220, 380, 380, 240, 300, (240, 190, 60))
    p.pie(210, 220, 380, 380, 300, 360, (90, 180, 90))
    p.chord(210, 220, 180, 180, 180, 360, (255, 253, 240))
    p.text(210, 268, "RISK SCORE", 26)
    return p.done()


def needle(length=170):
    p = Pen(length * 2 + 20, 40)
    p.poly([(length + 10, 12), (2 * length + 10, 20), (length + 10, 28)], INK, ol=None)
    p.ell(length + 10, 20, 28, 28, INK, ol=None)
    return p.done(shadow=False, paper=False)


def shield(txt="IMMUNITY", cracked=False):
    p = Pen(300, 340)
    p.poly([(30, 30), (270, 30), (270, 170), (150, 320), (30, 170)], (90, 140, 210), ow=5)
    p.poly([(55, 52), (245, 52), (245, 165), (150, 290), (55, 165)], (130, 175, 230), ol=None)
    p.text(150, 140, txt, 36 if len(txt) < 9 else 28, fill=(255, 255, 255), stroke=2, stroke_fill=INK)
    if cracked:
        p.line([(150, 30), (130, 110), (170, 170), (140, 240), (150, 320)], fill=INK, w=8)
    return p.done()


def scroll(txt):
    lines = txt.split("\n")
    p = Pen(560, 120 + 62 * len(lines))
    hh = 120 + 62 * len(lines)
    p.rect(40, 30, 520, hh - 30, (245, 230, 190))
    p.ell(40, hh / 2, 50, hh - 40, (230, 210, 160))
    p.ell(520, hh / 2, 50, hh - 40, (230, 210, 160))
    for i, l in enumerate(lines):
        p.text(280, 80 + i * 62, l, 40)
    return p.done()


def board(lines, w=760, h=440, col=(30, 70, 50), fg=(255, 255, 255), size=64):
    p = Pen(w, h)
    p.rect(10, 10, w - 10, h - 10, (120, 80, 40), r=8)
    p.rect(30, 30, w - 30, h - 30, col, ol=None)
    n = len(lines)
    for i, (t, c) in enumerate(lines):
        p.text(w / 2, 30 + (h - 60) * (i + 0.5) / n, t, size, fill=c or fg)
    return p.done()


def tv(inner, w=720, h=480):
    """Wrap a sprite in a TV/video frame."""
    p = Pen(w, h)
    p.rect(10, 10, w - 10, h - 10, (40, 40, 45), r=24)
    p.rect(40, 40, w - 40, h - 40, (170, 205, 230), ol=None)
    fr = p.done()
    iw = inner.copy()
    sc = min((w - 80) / iw.width, (h - 60) / iw.height) * 1.05
    iw = iw.resize((int(iw.width * sc), int(iw.height * sc)), Image.LANCZOS)
    box = Image.new("RGBA", (w - 80, h - 80), (0, 0, 0, 0))
    box.alpha_composite(iw, ((w - 80 - iw.width) // 2, max(0, (h - 80) - iw.height + 20)))
    fr.alpha_composite(box, (40, 40))
    rec = Pen(140, 60)
    rec.ell(30, 30, 26, 26, (220, 30, 30), ol=None)
    rec.text(85, 32, "LIVE", 30, fill=(255, 255, 255))
    fr.alpha_composite(rec.done(shadow=False), (50, 50))
    return fr


def newspaper(head, sub=""):
    p = Pen(520, 380)
    p.rect(10, 10, 510, 370, (245, 242, 230))
    p.text(260, 50, "THE DAILY NEWS", 30, fill=(90, 90, 90))
    p.line([(30, 75), (490, 75)], w=3)
    for i, l in enumerate(head.split("\n")):
        p.text(260, 120 + i * 50, l, 42)
    if sub:
        p.text(260, 240, sub, 26, fill=(110, 110, 110), kind="hand")
    for i in range(3):
        p.line([(40, 280 + i * 25), (480, 280 + i * 25)], fill=(170, 170, 170), w=4)
    return p.done()


def calendar(top, big):
    p = Pen(300, 320)
    p.rect(10, 30, 290, 310, (255, 255, 250))
    p.rect(10, 30, 290, 110, (200, 40, 45))
    p.text(150, 72, top, 40, fill=(255, 255, 255))
    p.text(150, 210, big, 90 if len(big) < 4 else 60)
    p.ell(80, 30, 20, 40, (90, 90, 90))
    p.ell(220, 30, 20, 40, (90, 90, 90))
    return p.done()


def clock(hour=3):
    p = Pen(260, 260)
    p.ell(130, 130, 240, 240, (255, 253, 240), ow=6)
    for i in range(12):
        a = math.radians(i * 30)
        p.line([(130 + 95 * math.sin(a), 130 - 95 * math.cos(a)), (130 + 108 * math.sin(a), 130 - 108 * math.cos(a))], w=5)
    a = math.radians(hour * 30)
    p.line([(130, 130), (130 + 60 * math.sin(a), 130 - 60 * math.cos(a))], w=10)
    p.line([(130, 130), (130, 50)], w=6)
    return p.done()


def rock():
    p = Pen(90, 80)
    p.poly([(10, 50), (25, 15), (60, 8), (82, 35), (70, 70), (30, 74)], (130, 125, 120))
    return p.done(shadow=False)


def window_pane(broken=False, w=420, h=320, txt="ueno"):
    p = Pen(w, h)
    p.rect(10, 10, w - 10, h - 10, (90, 90, 95))
    p.rect(30, 30, w - 30, h - 30, (170, 215, 240) if not broken else (60, 60, 70), ol=None)
    if not broken:
        p.text(w / 2, h / 2, txt, 70, fill=(20, 150, 125))
        p.line([(50, 50), (110, 110)], fill=(255, 255, 255), w=6)
    else:
        rng = random.Random(4)
        cx, cy = w / 2, h / 2
        for i in range(10):
            a = i * 2 * math.pi / 10 + rng.uniform(-.2, .2)
            r1 = rng.uniform(60, 120)
            p.poly([(cx, cy), (cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
                    (cx + r1 * math.cos(a + .35), cy + r1 * math.sin(a + .35))], (170, 215, 240), ow=2)
        for i in range(8):
            x, y = rng.uniform(40, w - 40), rng.uniform(40, h - 40)
            if abs(x - cx) > 120 or abs(y - cy) > 110:
                p.poly([(x, y), (x + 30, y + 10), (x + 10, y + 35)], (170, 215, 240), ow=2)
    return p.done()


def magnifier(scale=1.0):
    p = Pen(300, 300)
    p.line([(180, 180), (280, 280)], fill=(110, 70, 30), w=26)
    p.ell(120, 120, 200, 200, (215, 240, 255, 140), ow=12)
    p.arc(100, 100, 120, 120, 200, 260, fill=(255, 255, 255), wd=8)
    im = p.done()
    return im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS) if scale != 1 else im


def question(size=150, col=(240, 190, 60)):
    p = Pen(size, size + 20)
    p.text(size / 2, size / 2 + 10, "?", size * 0.9, fill=col, stroke=4, stroke_fill=INK)
    return p.done()


def arrow(w=300, h=120, col=(220, 60, 50)):
    p = Pen(w, h)
    p.poly([(10, h * 0.35), (w - 90, h * 0.35), (w - 90, 10), (w - 10, h / 2), (w - 90, h - 10),
            (w - 90, h * 0.65), (10, h * 0.65)], col)
    return p.done()


def bull():
    p = Pen(460, 320)
    p.ell(220, 170, 300, 160, (120, 70, 40))
    for x in (120, 170, 270, 320):
        p.rect(x - 14, 220, x + 14, 300, (110, 60, 35))
    p.ell(380, 140, 130, 110, (130, 75, 45))
    p.poly([(350, 100), (330, 40), (370, 90)], (240, 230, 210))
    p.poly([(410, 100), (440, 40), (420, 100)], (240, 230, 210))
    p.ell(400, 130, 16, 16, (255, 255, 255), ow=2)
    p.ell(430, 170, 40, 26, (230, 160, 150), ow=2)
    return p.done()


def gas_pump():
    p = Pen(200, 340)
    p.rect(30, 40, 150, 330, (220, 60, 50), r=10)
    p.rect(50, 70, 130, 150, (230, 250, 245))
    p.text(90, 110, "FUEL", 26)
    p.line([(150, 180), (185, 200), (185, 280)], w=8)
    return p.done()


def cart():
    p = Pen(300, 260)
    p.poly([(40, 60), (270, 60), (240, 180), (70, 180)], (200, 200, 210))
    for i in range(4):
        p.line([(80 + i * 50, 62), (95 + i * 40, 178)], w=3)
    p.line([(10, 30), (40, 60)], w=8)
    p.ell(90, 220, 40, 40, (50, 50, 55))
    p.ell(220, 220, 40, 40, (50, 50, 55))
    p.ell(120, 50, 60, 50, (240, 130, 60))
    p.ell(180, 46, 70, 54, (120, 200, 90))
    return p.done()


def radio():
    p = Pen(340, 240)
    p.rect(20, 50, 320, 230, (180, 110, 60), r=20)
    p.line([(250, 50), (300, 5)], w=6)
    p.ell(110, 140, 130, 130, (90, 60, 40))
    for r in range(3):
        p.arc(110, 140, 40 + r * 30, 40 + r * 30, 0, 360, fill=(60, 40, 25), wd=3)
    p.rect(200, 90, 300, 130, (240, 230, 200))
    p.ell(250, 180, 40, 40, (220, 200, 160))
    return p.done()


def football():
    p = Pen(120, 120)
    p.ell(60, 60, 110, 110, (255, 255, 255), ow=4)
    p.poly([(60, 40), (80, 55), (72, 78), (48, 78), (40, 55)], INK, ol=None)
    return p.done()


def podium(txt=""):
    p = Pen(300, 260)
    p.poly([(30, 20), (270, 20), (240, 255), (60, 255)], (130, 85, 50))
    p.ell(150, 120, 80, 80, (235, 200, 80))
    if txt:
        p.text(150, 122, txt, 22)
    return p.done()


def desk(txt="DOM TALKS POLITICS"):
    p = Pen(1100, 320)
    p.rect(20, 40, 1080, 310, (120, 70, 40), r=10)
    p.rect(20, 20, 1080, 60, (150, 95, 55), r=8)
    p.rect(220, 110, 880, 250, (250, 240, 215), r=8)
    p.text(550, 182, txt, 64, fill=(200, 40, 45))
    return p.done()


def desk_mic():
    p = Pen(140, 260)
    p.rect(30, 230, 110, 250, (50, 50, 55))
    p.line([(70, 235), (70, 120), (90, 70)], fill=(60, 60, 65), w=8)
    p.ell(95, 55, 60, 80, (80, 80, 85))
    return p.done()


def chair():
    p = Pen(200, 300)
    p.rect(30, 20, 170, 170, (130, 40, 40), r=16)
    p.rect(20, 160, 180, 200, (150, 50, 50), r=8)
    p.rect(30, 200, 45, 290, (90, 60, 40))
    p.rect(155, 200, 170, 290, (90, 60, 40))
    return p.done()


def badge(txt, col=(235, 195, 70)):
    lines = txt.split("\n")
    p = Pen(300, 340)
    for i in range(16):
        a = i * math.pi / 8
        p.poly([(150, 150), (150 + 130 * math.cos(a - .15), 150 + 130 * math.sin(a - .15)),
                (150 + 145 * math.cos(a), 150 + 145 * math.sin(a)),
                (150 + 130 * math.cos(a + .15), 150 + 130 * math.sin(a + .15))], col, ow=2)
    p.ell(150, 150, 250, 250, col)
    p.ell(150, 150, 210, 210, (250, 240, 200), ow=2)
    for i, l in enumerate(lines):
        p.text(150, 150 + (i - (len(lines) - 1) / 2) * 38, l, 32)
    p.poly([(90, 260), (130, 280), (110, 335), (85, 320)], (200, 50, 50))
    p.poly([(210, 260), (170, 280), (190, 335), (215, 320)], (200, 50, 50))
    return p.done()


def hand_stop(txt="NOT SO FAST!"):
    p = Pen(320, 420)
    sk = SKIN["tan"]
    p.rect(110, 260, 210, 420, (40, 50, 90))
    p.rect(70, 110, 250, 280, sk, r=40)
    for i, x in enumerate((88, 130, 172, 214)):
        p.rect(x - 18, 20 + abs(i - 1.5) * 18, x + 18, 150, sk, r=18)
    p.ell(60, 210, 60, 110, sk)
    im = p.done()
    return im


def flag_py(w=240, h=150):
    p = Pen(w, h)
    p.rect(5, 5, w - 5, h - 5, (255, 255, 255))
    p.rect(5, 5, w - 5, 5 + (h - 10) / 3, (210, 40, 45), ol=None)
    p.rect(5, 5 + 2 * (h - 10) / 3, w - 5, h - 5, (30, 60, 160), ol=None)
    p.ell(w / 2, h / 2, 34, 34, (255, 255, 255), ol=(40, 120, 60), ow=3)
    p.rect(5, 5, w - 5, h - 5, None)
    return p.done()


def flag_us(w=240, h=150):
    p = Pen(w, h)
    for i in range(7):
        y0 = 5 + i * (h - 10) / 7
        p.rect(5, y0, w - 5, y0 + (h - 10) / 14, (200, 40, 50), ol=None)
        p.rect(5, y0 + (h - 10) / 14, w - 5, y0 + (h - 10) / 7, (255, 255, 255), ol=None)
    p.rect(5, 5, w * 0.45, h * 0.55, (40, 60, 140), ol=None)
    for r in range(3):
        for c in range(4):
            p.ell(20 + c * 24, 20 + r * 24, 8, 8, (255, 255, 255), ol=None)
    p.rect(5, 5, w - 5, h - 5, None)
    return p.done()


def bank_logo_sign(txt, col, w=None):
    tw = text_size(txt, 60)[0]
    w = w or tw + 80
    p = Pen(w, 120)
    p.rect(10, 10, w - 10, 110, col, r=14)
    p.text(w / 2, 62, txt, 60, fill=(255, 255, 255))
    return p.done()


def fish(col=(20, 150, 125), txt="ueno", w=520, mouth=False):
    p = Pen(w, int(w * 0.55))
    hh = w * 0.55
    p.poly([(w * 0.02, hh * 0.2), (w * 0.22, hh * 0.5), (w * 0.02, hh * 0.8)], col)
    p.ell(w * 0.56, hh * 0.5, w * 0.78, hh * 0.8, col)
    p.ell(w * 0.8, hh * 0.38, w * 0.09, w * 0.09, (255, 255, 255), ow=2)
    p.ell(w * 0.81, hh * 0.39, w * 0.03, w * 0.03, INK, ol=None)
    if mouth:
        p.pie(w * 0.95, hh * 0.55, w * 0.25, hh * 0.45, 140, 220, (90, 20, 30))
    p.text(w * 0.52, hh * 0.55, txt, int(w * 0.11), fill=(255, 255, 255), stroke=2, stroke_fill=INK)
    return p.done()


# ----------------------------------------------------------------------------- backgrounds

def _bg_base(sky, ground, horizon=780):
    p = Pen(W, H)
    p.rect(-5, -5, W + 5, horizon, sky, ol=None)
    p.rect(-5, horizon, W + 5, H + 5, ground, ol=None)
    p.line([(-5, horizon), (W + 5, horizon)], w=4)
    return p


HORIZON, ROAD_END = 800, 900
# parts of a background that captions must not cover (boxes in frame pixels)
FLAG_BOX = (70, 60, 330, 216)
BG_ZONES = {"chamber": [("flag", FLAG_BOX)], "senate": [("flag", FLAG_BOX)], "court": [("flag", FLAG_BOX)]}  # street geometry: building bases / near kerb
STREETS = {"street", "night", "street_py", "washington", "wallst", "dusk", "sepia"}


def bg(kind):
    rng = random.Random(kind)
    if kind == "studio":
        p = Pen(W, H)
        p.rect(-5, -5, W + 5, H + 5, (60, 70, 120), ol=None)
        for i in range(0, W, 120):
            p.rect(i, -5, i + 60, H, (66, 78, 132), ol=None)
        p.ell(W / 2, 330, 900, 520, (80, 95, 160), ol=None)
        p.rect(-5, 860, W + 5, H + 5, (45, 50, 85), ol=None)
        # skyline cutouts in window
        p.rect(140, 120, 520, 520, (120, 190, 235), ow=6)
        for i in range(6):
            x = 150 + i * 60
            hh = rng.randint(120, 300)
            p.rect(x, 520 - hh, x + 50, 515, (90, 110, 150), ow=2)
        p.rect(1400, 120, 1780, 520, (120, 190, 235), ow=6)
        p.chord(1590, 470, 200, 200, 180, 360, (245, 245, 240))
        p.rect(1480, 470, 1700, 515, (245, 245, 240))
        return paperize(p.done(shadow=False, paper=False).convert("RGB"), 0.12)
    if kind.removesuffix("_far") in STREETS:
        # Depth layout (back to front): sky -> buildings standing on the horizon (y=800) -> road (800-900)
        # -> kerb -> near pavement (912-1080) where characters and foreground props stand (GROUND=960).
        # "<kind>_far" swaps the street buildings for a faint distant skyline, for scenes whose subject is
        # its own foreground building (so it doesn't look pasted in front of same-size neighbours).
        far = kind.endswith("_far")
        base = kind.removesuffix("_far")
        night = base == "night"
        sky = {"night": (30, 35, 80), "dusk": (240, 150, 110), "sepia": (225, 200, 160)}.get(base, (140, 205, 240))
        road = {"night": (45, 45, 52), "sepia": (150, 125, 95)}.get(base, (110, 110, 115))
        pave = {"night": (75, 75, 85), "sepia": (195, 170, 130)}.get(base, (185, 185, 180))
        p = Pen(W, H)
        p.rect(-5, -5, W + 5, HORIZON, sky, ol=None)
        if not night and base != "sepia":
            for cx, cy in ((300, 160), (900, 110), (1500, 180)):
                for dx, dy, s in ((0, 0, 120), (70, -20, 140), (150, 0, 110)):
                    p.ell(cx + dx, cy + dy, s * 1.3, s * 0.8, (255, 255, 255), ow=2)
        if night:
            for i in range(60):
                p.ell(rng.uniform(0, W), rng.uniform(0, 500), 5, 5, (255, 255, 210), ol=None)
            p.ell(1650, 150, 140, 140, (250, 245, 200))
        if base == "washington":
            p.rect(-5, 640, W + 5, HORIZON, (120, 180, 100), ol=None)
            for x in range(0, W, 140):
                p.ell(x + 40, 650, 140, 110, (80, 150, 80), ow=2)
        else:
            cols = [(220, 170, 140), (200, 200, 170), (170, 190, 210), (230, 210, 160), (190, 160, 190)]
            if base == "sepia":
                cols = [(200, 170, 130), (190, 160, 120), (210, 180, 140)]
            x = -40
            while x < W:
                if far:
                    bw, bh = rng.randint(120, 220), rng.randint(90, 230)
                else:
                    bw = rng.randint(180, 300)
                    bh = rng.randint(240, 460) if base != "wallst" else rng.randint(450, 700)
                c = rng.choice(cols)
                if night:
                    c = tuple(int(v * 0.4) for v in c)
                if far:  # hazy: blend towards the sky, thin outline, small window dots
                    c = tuple(int(v * 0.45 + s * 0.55) for v, s in zip(c, sky))
                    p.rect(x, HORIZON - bh, x + bw, HORIZON, c, ol=tuple(int(v * 0.8) for v in c), ow=2)
                    for wy in range(HORIZON - bh + 20, HORIZON - 25, 40):
                        for wx in range(x + 16, x + bw - 22, 34):
                            p.rect(wx, wy, wx + 14, wy + 18, tuple(min(255, v + 25) for v in c), ol=None)
                else:
                    p.rect(x, HORIZON - bh, x + bw, HORIZON, c)
                    # windows stay inside the wall: last row ends at least 20px above the building's base
                    wy = HORIZON - bh + 30
                    while wy + 40 <= HORIZON - 20:
                        for wx in range(x + 25, x + bw - 40, 60):
                            lit = night and rng.random() < 0.4
                            p.rect(wx, wy, wx + 34, wy + 40, (250, 230, 120) if lit else
                                   ((60, 70, 90) if night else (210, 235, 250)), ow=2)
                        wy += 70
                x += bw + rng.randint(5, 40) + (40 if far else 0)
        # road, kerb, pavement
        p.rect(-5, HORIZON, W + 5, ROAD_END, road, ol=None)
        p.line([(-5, HORIZON), (W + 5, HORIZON)], w=4)
        for i in range(0, W, 160):
            p.rect(i, 846, i + 80, 854, (240, 220, 80), ol=None)
        p.rect(-5, ROAD_END, W + 5, ROAD_END + 12, tuple(min(255, v + 30) for v in pave))
        p.rect(-5, ROAD_END + 12, W + 5, H + 5, pave, ol=None)
        for i in range(0, W, 150):
            p.line([(i, ROAD_END + 12), (i - 60, H + 5)], fill=tuple(int(v * 0.85) for v in pave), w=2)
        p.line([(-5, 1000), (W + 5, 1000)], fill=tuple(int(v * 0.85) for v in pave), w=2)
        im = p.done(shadow=False, paper=False).convert("RGB")
        if base == "sepia":
            im = Image.blend(im, Image.new("RGB", im.size, (180, 140, 90)), 0.25)
        return paperize(im, 0.12)
    if kind == "py_land":  # countryside with hills
        p = _bg_base((150, 210, 240), (110, 180, 80), 760)
        for cx, s in ((300, 700), (1100, 900), (1800, 600)):
            p.chord(cx, 780, s, 420, 180, 360, (90, 160, 70))
        return paperize(p.done(shadow=False, paper=False).convert("RGB"), 0.12)
    if kind == "map":
        p = Pen(W, H)
        p.rect(-5, -5, W + 5, H + 5, (110, 175, 220), ol=None)
        for i in range(0, W, 90):
            p.arc(i, 60 + (i % 180), 60, 20, 200, 340, fill=(150, 200, 235), wd=3)
        return paperize(p.done(shadow=False, paper=False).convert("RGB"), 0.12)
    if kind in ("chamber", "senate", "court"):
        p = Pen(W, H)
        wall = {"chamber": (170, 120, 90), "senate": (120, 50, 60), "court": (130, 100, 70)}[kind]
        p.rect(-5, -5, W + 5, H + 5, wall, ol=None)
        for i in range(0, W, 160):
            p.rect(i + 20, 60, i + 120, 640, tuple(min(255, c + 20) for c in wall), ow=2)
        p.rect(-5, 640, W + 5, H + 5, (110, 70, 45), ol=None)
        p.line([(-5, 640), (W + 5, 640)], w=4)
        fx0, fy0, fx1, fy1 = FLAG_BOX  # flag on a pole in the top-left corner, clear of titles
        fh = (fy1 - fy0) / 3
        p.rect(fx0 - 22, fy0 - 10, fx0 - 12, 640, (190, 160, 70))
        p.rect(fx0, fy0, fx1, fy1, (255, 255, 255), ow=4)
        p.rect(fx0, fy0, fx1, fy0 + fh, (210, 40, 45), ol=None)
        p.rect(fx0, fy1 - fh, fx1, fy1, (30, 60, 160), ol=None)
        p.ell((fx0 + fx1) / 2, (fy0 + fy1) / 2, 40, 40, (255, 255, 255), ol=(40, 120, 60), ow=3)
        p.rect(fx0, fy0, fx1, fy1, None, ow=4)
        return paperize(p.done(shadow=False, paper=False).convert("RGB"), 0.12)
    if kind in ("office_in", "locker", "jail"):
        p = Pen(W, H)
        wall = {"office_in": (210, 225, 200), "locker": (90, 120, 160), "jail": (150, 150, 150)}[kind]
        p.rect(-5, -5, W + 5, H + 5, wall, ol=None)
        p.rect(-5, 760, W + 5, H + 5, (140, 110, 80) if kind != "jail" else (110, 110, 110), ol=None)
        p.line([(-5, 760), (W + 5, 760)], w=4)
        if kind == "locker":
            for i in range(0, W, 130):
                p.rect(i + 10, 140, i + 120, 760, (200, 40, 50), ow=3)
                p.rect(i + 40, 180, i + 90, 190, INK, ol=None)
                p.rect(i + 40, 200, i + 90, 210, INK, ol=None)
        elif kind == "jail":
            for y in range(0, 760, 70):
                for x in range((y // 70 % 2) * 60, W, 120):
                    p.rect(x, y, x + 116, y + 66, (160, 160, 158), ow=2)
        else:
            p.rect(1400, 140, 1760, 460, (180, 220, 245), ow=6)
            p.rect(160, 160, 420, 400, (250, 245, 230), ow=4)
            p.line([(180, 360), (240, 300), (300, 330), (400, 200)], fill=(20, 150, 125), w=8)
        return paperize(p.done(shadow=False, paper=False).convert("RGB"), 0.12)
    if kind in ("paper_red", "paper_blue", "paper_green", "paper_yellow", "paper_purple", "cork"):
        c = {"paper_red": (200, 70, 60), "paper_blue": (70, 110, 180), "paper_green": (80, 150, 100),
             "paper_yellow": (240, 200, 90), "paper_purple": (120, 80, 150), "cork": (200, 160, 110)}[kind]
        p = Pen(W, H)
        p.rect(-5, -5, W + 5, H + 5, c, ol=None)
        if kind == "cork":
            for i in range(900):
                x, y = rng.uniform(0, W), rng.uniform(0, H)
                p.ell(x, y, 6, 4, (170, 130, 85), ol=None)
        else:
            dark = tuple(int(v * 0.88) for v in c)
            for i in range(-H, W, 140):
                p.poly([(i, 0), (i + 60, 0), (i + 60 + H, H), (i + H, H)], dark, ol=None)
        return paperize(p.done(shadow=False, paper=False).convert("RGB"), 0.14)
    raise ValueError(kind)


def map_sprite():
    """Simplified cutout map of Paraguay and its neighbours."""
    p = Pen(1200, 1000)
    bol = [(120, 60), (520, 40), (640, 190), (600, 420), (430, 470), (300, 380), (160, 300)]
    bra = [(640, 190), (980, 120), (1180, 380), (1150, 900), (860, 980), (760, 760), (730, 560), (600, 420)]
    arg = [(160, 300), (300, 380), (430, 470), (560, 640), (760, 760), (860, 980), (300, 990), (180, 700)]
    par = [(430, 470), (600, 420), (730, 560), (760, 760), (640, 720), (560, 640)]
    p.poly(bol, (230, 200, 120), ow=4)
    p.poly(bra, (140, 200, 110), ow=4)
    p.poly(arg, (170, 200, 230), ow=4)
    p.text(380, 200, "BOLIVIA", 54)
    p.text(950, 520, "BRAZIL", 60)
    p.text(380, 820, "ARGENTINA", 54)
    return p.done()


def paraguay_sprite():
    par = [(430, 470), (600, 420), (730, 560), (760, 760), (640, 720), (560, 640)]
    p = Pen(1200, 1000)
    p.poly(par, (220, 70, 60), ow=6)
    p.text(615, 590, "PARAGUAY", 40, fill=(255, 255, 255), stroke=3, stroke_fill=INK)
    return p.done()


# scenery: sits behind characters/props by design (buildings, desks, podiums, maps)
SCENERY = {"building", "map_sprite", "desk", "podium", "sound_block", "desk_mic"}
# overlay: deliberately drawn over something else (ice over a vault, bars over a prisoner)
OVERLAY = {"ice_block", "jail_bars", "needle", "paraguay_sprite", "rock", "window_pane", "hand_stop"}

# tag every drawn sprite with the function that made it, so QA reports can name it
def _tagged(fn):
    @functools.wraps(fn)
    def wrap(*args, **kw):
        im = fn(*args, **kw)
        if isinstance(im, Image.Image):
            im.info.setdefault("what", fn.__name__)
            if fn.__name__ in SCENERY:
                im.info.setdefault("kind", "scenery")
            elif fn.__name__ in OVERLAY:
                im.info.setdefault("kind", "overlay")
        return im
    return wrap


for _n in ["phone", "building", "money_bag", "coin", "cash_stack", "ice_block", "vault", "gavel", "sound_block",
           "document", "paper_stack", "jail_bars", "yacht", "plane", "dam", "scales", "ballot_box", "rocket_chart",
           "risk_meter", "needle", "shield", "scroll", "board", "tv", "newspaper", "calendar", "clock", "rock",
           "window_pane", "magnifier", "question", "arrow", "bull", "gas_pump", "cart", "radio", "football",
           "podium", "desk", "desk_mic", "chair", "badge", "hand_stop", "flag_py", "flag_us", "fish",
           "map_sprite", "paraguay_sprite"]:
    globals()[_n] = _tagged(globals()[_n])
