"""Building blocks for episode timelines: Actor/Scene plus C (character), L (label), P (prop), crowd, gavel, part cards."""
import math, os, importlib.util
from PIL import Image
import art
from art import W, H

GROUND = 960


class Actor:
    def __init__(self, img, x, y, t=None, anchor="bc", enter="pop", idle="bob", talk=(), out=None,
                 move=None, fall=None, swing=None, phase=0.0, spin=0.0, dur=0.32, blink=True):
        self.v = img if isinstance(img, dict) else {"closed": img}
        self.x, self.y, self.t, self.anchor = x, y, t, anchor
        self.enter, self.idle, self.talk, self.out = enter, idle, talk, out
        self.move, self.fall, self.swing, self.phase, self.spin = move, fall, swing, phase, spin
        self.dur, self.blink = dur, blink
        self._cache = {}


class Scene:
    def __init__(self, start, bgk, actors, zoom=0.035, part=None):
        self.start, self.bgk, self.actors, self.zoom, self.part = start, bgk, actors, zoom, part


def C(name, x, y=GROUND, t=None, talk=(), scale=1.15, flip=False, mouth="closed", eyes="normal", **kw):
    a = kw.pop("a", {})
    v = art.char_set(name, scale=scale, flip=flip, mouth=mouth, eyes=eyes, **kw)
    return Actor(v, x, y, t=t, talk=talk, phase=(x % 97) / 97.0, **a)


def L(text, x, y, t=None, size=58, rot=-2.0, bgc=(255, 252, 235), fg=art.INK, **a):
    return Actor(art.label(text, size, bg=bgc, fg=fg, rot=rot), x, y, t=t, anchor="c",
                 idle=a.pop("idle", "none"), **a)


def P(img, x, y, t=None, anchor="bc", enter="pop", idle="none", **a):
    return Actor(img, x, y, t=t, anchor=anchor, enter=enter, idle=idle, **a)


def crowd(x0, x1, y, n, scale=0.62, seed=0, t=None, hold=None, mouth="closed", eyes="normal", rows=1,
          flipmix=True, arms="down", enter="pop"):
    out = []
    for r in range(rows):
        for i in range(n):
            x = x0 + (x1 - x0) * (i + 0.5 * (r % 2)) / max(n - 1, 1)
            k = seed + r * 100 + i
            hd = hold[k % len(hold)] if isinstance(hold, list) else hold
            img = art.crowd_person(k, scale=scale * (1 - 0.12 * r), mouth=mouth, eyes=eyes, hold=hd,
                                   flip=flipmix and (k % 3 == 0), arms=arms)
            out.append(Actor(img, x, y - r * 60, t=None if t is None else t + 0.05 * i, phase=k * 0.37,
                             enter=enter))
    out.sort(key=lambda a: -a.y)
    return out[::-1]


def gavel_actor(x, y, impact):
    """Gavel that swings down at `impact` onto a sound block."""
    g = art.gavel(1.0)
    pad = Image.new("RGBA", (900, 900), (0, 0, 0, 0))
    # handle end (right) at pad centre
    pad.alpha_composite(g, (450 - g.width + 20, 450 - g.height // 2))
    return Actor(pad, x + 307, y - 65, t=impact - 1.2, anchor="c", enter="drop", idle="none", swing=impact)


def part_card(start, num, title, col):
    return Scene(start, col, [
        L(f"PART {num}", W / 2, 400, t=start + 0.05, size=110, rot=-3, bgc=(255, 255, 255), enter="slideL"),
        L(title, W / 2, 610, t=start + 0.25, size=96, rot=2, bgc=(255, 230, 120), enter="slideR"),
    ], zoom=0.02, part=num)




def load_episode(path=None):
    """Import the episode timeline named by $EPISODE (a .py file in episodes/)."""
    path = path or os.environ.get("EPISODE")
    if not path:
        raise SystemExit("Set EPISODE=episodes/<name>.py")
    spec = importlib.util.spec_from_file_location("episode", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
