"""Synthesise sound effects and mix them under the narration."""
import numpy as np, subprocess, sys
import scenes

SR = 44100
rng = np.random.default_rng(7)


def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    na = int(a * SR)
    if na:
        e[:na] *= np.linspace(0, 1, na)
    return e


def lowpass(x, cut):
    a = np.exp(-2 * np.pi * cut / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def bandnoise(n, lo, hi):
    x = rng.normal(0, 1, n)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(X, n)
    return y / (np.abs(y).max() + 1e-9)


def gavel():
    n = int(SR * 0.9)
    t = np.arange(n) / SR
    knock = bandnoise(n, 300, 3500) * env(n, 0.0005, 0.018)
    body = (np.sin(2 * np.pi * 180 * t) * 0.9 + np.sin(2 * np.pi * 410 * t) * 0.5 +
            np.sin(2 * np.pi * 760 * t) * 0.3) * env(n, 0.0005, 0.09)
    thump = np.sin(2 * np.pi * 75 * t) * env(n, 0.001, 0.12)
    room = bandnoise(n, 200, 2000) * env(n, 0.01, 0.25) * 0.08
    return (knock * 0.8 + body + thump * 0.8 + room) * 0.9


def thud():
    n = int(SR * 0.6)
    t = np.arange(n) / SR
    f = 110 * np.exp(-t * 6) + 45
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * env(n, 0.001, 0.15) + bandnoise(n, 100, 1200) * env(n, 0.001, 0.04) * 0.5) * 0.9


def stamp():
    n = int(SR * 0.4)
    t = np.arange(n) / SR
    return (bandnoise(n, 150, 2500) * env(n, 0.0005, 0.03) +
            np.sin(2 * np.pi * 120 * t) * env(n, 0.001, 0.07) * 0.8) * 0.8


def whoosh():
    n = int(SR * 0.7)
    t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    out = np.zeros(n)
    # sweeping band via short-time filtering
    seg = 2048
    for s in range(0, n, seg):
        c = 400 + 3000 * np.sin(np.pi * min(1, s / n))
        chunk = x[s:s + seg]
        X = np.fft.rfft(chunk)
        f = np.fft.rfftfreq(len(chunk), 1 / SR)
        X *= np.exp(-((f - c) / (c * 0.6)) ** 2)
        out[s:s + seg] = np.fft.irfft(X, len(chunk))
    out /= np.abs(out).max() + 1e-9
    shape = np.sin(np.pi * t / t[-1]) ** 2
    return out * shape * 0.35


def cash():
    n = int(SR * 0.9)
    t = np.arange(n) / SR
    out = np.zeros(n)
    # drawer clunk
    out += bandnoise(n, 200, 3000) * env(n, 0.0005, 0.03) * 0.6
    # bell "ching"
    for k, (f, d) in enumerate([(2093, 0.5), (2637, 0.45), (3136, 0.35), (4186, 0.25)]):
        st = int(SR * 0.08)
        bell = np.zeros(n)
        bell[st:] = np.sin(2 * np.pi * f * t[: n - st]) * env(n - st, 0.001, d)
        out += bell * (0.35 / (k + 1) ** 0.5)
    return out * 0.7


def gulp():
    n = int(SR * 0.35)
    t = np.arange(n) / SR
    f = 200 + 500 * (t / t[-1])
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.sin(np.pi * t / t[-1]) * 0.5


def pop():
    n = int(SR * 0.15)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 20) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.04) * 0.5


def crash():
    s = np.concatenate([np.zeros(int(SR * 0.05)), stamp()]); s = np.pad(s, (0, int(SR * 0.6) - len(s)))
    return thud() * 0.8 + s * 0.5


def glass():
    n = int(SR * 1.4)
    t = np.arange(n) / SR
    out = bandnoise(n, 2000, 9000) * env(n, 0.0005, 0.12) * 0.6
    for i in range(28):
        st = int(rng.uniform(0, 0.7) * SR)
        f = rng.uniform(2500, 7000)
        m = n - st
        out[st:] += np.sin(2 * np.pi * f * t[:m]) * env(m, 0.0005, rng.uniform(0.02, 0.08)) * rng.uniform(.1, .3)
    out += thud()[: n] if len(thud()) >= n else np.pad(thud(), (0, n - len(thud()))) * 0.4
    return out * 0.6


def crack():
    n = int(SR * 0.5)
    return bandnoise(n, 800, 6000) * env(n, 0.0003, 0.05) * 0.7


def crowd(sec=7.5):
    n = int(SR * sec)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for v in range(14):
        b = bandnoise(n, 250 + v * 30, 1200 + v * 40)
        mod = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(1.5, 4) * t + rng.uniform(0, 6))
        out += b * mod
    out /= np.abs(out).max()
    fade = np.minimum(1, np.minimum(t / 1.0, (t[-1] - t) / 1.5))
    return out * fade * 0.18


FX = {"gavel": gavel, "thud": thud, "stamp": stamp, "cash": cash, "gulp": gulp, "pop": pop,
      "crash": crash, "glass": glass, "crack": crack, "crowd": crowd, "crowd_short": lambda: crowd(6.0)}
GAIN = {"gavel": 1.0, "thud": 0.55, "stamp": 0.55, "cash": 0.45, "gulp": 0.4, "pop": 0.35, "crash": 0.5,
        "glass": 0.5, "crack": 0.45, "crowd": 0.55, "crowd_short": 0.45}


def main(voice_path, out_path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", voice_path, "-ac", "1", "-ar", str(SR), "-f",
                          "f32le", "-"], capture_output=True, check=True).stdout
    v = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    total = int(SR * scenes.END)
    mix = np.zeros(total)
    mix[: len(v)] += v
    fx = np.zeros(total)

    def add(t, sig, g):
        s = int(t * SR)
        e = min(total, s + len(sig))
        fx[s:e] += sig[: e - s] * g

    for t, k in scenes.SFX:
        add(t, FX[k](), GAIN[k])
    for t in scenes.WHOOSH:
        add(t, whoosh(), 0.5)
    # duck the effects a little under speech, except the hero gavels
    mix += fx * 0.8
    peak = np.abs(mix).max()
    a = np.abs(mix)
    soft = np.where(a > 0.85, 0.85 + 0.13 * np.tanh((a - 0.85) / 0.13), a)
    mix = np.sign(mix) * soft
    pcm = (mix * 32767).astype(np.int16)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "pcm_s16le", out_path], input=pcm.tobytes(), check=True)
    print("peak", peak)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
