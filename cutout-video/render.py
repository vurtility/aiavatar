"""Render the cutout animation to video chunks in parallel."""
import math, sys, subprocess, os, random
import numpy as np
from PIL import Image
import art, scenes
from art import W, H

FPS = 12  # cutout-style stepped animation, output upsampled to 24fps
WORK = os.path.dirname(os.path.abspath(__file__))

_rms = None


def rms():
    global _rms
    if _rms is None:
        a = np.fromfile(f"{WORK}/audio16k.raw", dtype=np.float32)
        hop = 16000 // FPS
        n = len(a) // hop
        r = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1))
        _rms = r / (np.percentile(r, 95) + 1e-9)
    return _rms


def ease_out_back(x):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def actor_state(a, T, s0, fidx):
    t_in = a.t if a.t is not None else s0
    if T < t_in or (a.out is not None and T >= a.out):
        return None
    x, y, sc, rot, dx, dy = a.x, a.y, 1.0, 0.0, 0.0, 0.0
    e = (T - t_in) / a.dur
    if e < 1:
        if a.enter == "pop":
            sc = max(0.05, ease_out_back(e))
        elif a.enter == "slam":
            sc = 1 + 1.6 * (1 - ease(e * 1.6)) if e < 0.62 else 1.0
        elif a.enter == "slideL":
            dx = -(1 - ease(e)) * 1500
        elif a.enter == "slideR":
            dx = (1 - ease(e)) * 1500
        elif a.enter == "drop":
            dy = -(1 - ease(e)) * 1100
    if a.move:
        t0, t1, x1, y1 = a.move
        k = ease((T - t0) / (t1 - t0))
        x, y = a.x + (x1 - a.x) * k, a.y + (y1 - a.y) * k
        if 0 < k < 1:
            dy += -abs(math.sin(T * 14)) * 14  # little hop while walking
    ph = a.phase
    if a.idle == "bob":
        dy += round(math.sin(2 * math.pi * (T * 0.9 + ph)) * 2) * 3
    elif a.idle == "sway":
        rot += math.sin(2 * math.pi * (T * 0.6 + ph)) * 4
    elif a.idle == "shake":
        r = random.Random(fidx * 31 + int(a.x))
        dx += r.uniform(-4, 4)
        dy += r.uniform(-3, 3)
    elif a.idle == "pulse":
        sc *= 1 + 0.025 * math.sin(2 * math.pi * T * 1.2)
    if a.fall is not None and T > a.fall:
        k = ease((T - a.fall) / 0.6)
        rot += -88 * k
        dy += 60 * k
    if a.spin:
        t0, t1, r0, r1 = a.spin
        rot += r0 + (r1 - r0) * ease((T - t0) / (t1 - t0))
    if a.swing is not None:
        ti = a.swing
        if T < ti - 0.45:
            rot += -38
        elif T < ti:
            rot += -38 + 38 * ((T - (ti - 0.45)) / 0.45) ** 2
        else:
            rot += -6 * math.exp(-(T - ti) * 6) * abs(math.sin((T - ti) * 18))
    # variant
    v = "closed"
    if any(t0 <= T < t1 for t0, t1 in a.talk) and "open" in a.v:
        i = int(T * FPS)
        if i < len(rms()) and rms()[i] > 0.28 and fidx % 2 == 0:
            v = "open"
    if v == "closed" and "blink" in a.v and a.blink:
        if ((T + ph * 3.1) % 3.7) < 1.0 / FPS:
            v = "blink"
    return x + dx, y + dy, sc, rot, v


def place(frame, img, x, y, anchor):
    if anchor == "bc":
        px, py = int(x - img.width / 2), int(y - img.height)
    else:
        px, py = int(x - img.width / 2), int(y - img.height / 2)
    frame.paste(img, (px, py), img)


def render_frame(scene, nxt_start, T, fidx, bgs):
    if scene.bgk not in bgs:
        bgs[scene.bgk] = art.bg(scene.bgk)
    frame = bgs[scene.bgk].copy()
    for a in scene.actors:
        st = actor_state(a, T, scene.start, fidx)
        if st is None:
            continue
        x, y, sc, rot, v = st
        img = a.v[v]
        if abs(sc - 1) > 1e-3:
            nw, nh = max(1, int(img.width * sc)), max(1, int(img.height * sc))
            img = img.resize((nw, nh), Image.BILINEAR)
            if a.anchor == "bc":
                pass
        if abs(rot) > 0.05:
            if a.anchor == "bc" and a.fall is not None:
                # rotate around feet
                big = Image.new("RGBA", (img.width * 2, img.height * 2), (0, 0, 0, 0))
                big.paste(img, (img.width // 2, 0), img)
                img = big.rotate(rot, center=(img.width, img.height), resample=Image.BICUBIC)
                place(frame, img, x, y + img.height / 2, "bc")
                continue
            img = img.rotate(rot, expand=a.swing is None, resample=Image.BICUBIC)
        place(frame, img, x, y, a.anchor)
    # camera: slow push-in + impact shake
    dur = max(0.5, nxt_start - scene.start)
    z = 1 + scene.zoom * min(1.0, (T - scene.start) / dur)
    sx = sy = 0
    for ti, mag in scenes.SHAKE.items():
        if 0 <= T - ti < 0.35:
            r = random.Random(fidx)
            m = mag * (1 - (T - ti) / 0.35)
            sx, sy = r.uniform(-m, m), r.uniform(-m, m)
    if sx or sy:
        z = max(z, 1.03)
    if z > 1.001:
        cw, ch = W / z, H / z
        x0 = (W - cw) / 2 + sx
        y0 = (H - ch) / 2 + sy
        x0 = min(max(x0, 0), W - cw)
        y0 = min(max(y0, 0), H - ch)
        frame = frame.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    return frame


def scene_at(S, T):
    idx = 0
    for i, s in enumerate(S):
        if s.start <= T:
            idx = i
    nxt = S[idx + 1].start if idx + 1 < len(S) else scenes.END
    return S[idx], nxt


def render_chunk(i0, i1, out):
    S = scenes.build()
    bgs = {}
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-vf", "fps=24", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(i0, i1):
        T = f / FPS
        sc, nxt = scene_at(S, T)
        fr = render_frame(sc, nxt, T, f, bgs)
        p.stdin.write(fr.tobytes())
        if f % 600 == 0:
            print(f"chunk {out}: frame {f}/{i1}", flush=True)
    p.stdin.close()
    p.wait()


def still(T, path):
    S = scenes.build()
    sc, nxt = scene_at(S, T)
    render_frame(sc, nxt, T, int(T * FPS), {}).save(path)


if __name__ == "__main__":
    if sys.argv[1] == "still":
        for t in sys.argv[2:]:
            still(float(t), f"{WORK}/still_{t}.png")
    else:
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        render_chunk(i0, i1, out)
