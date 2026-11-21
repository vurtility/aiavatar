"""Visual QA for an episode timeline.

Usage: EPISODE=episodes/<name>.py WORKDIR=work python3 check.py [--sheets]

Automated checks (every scene, sampled whenever a new element has fully appeared):
  OFF-FRAME   element cut off by the frame edge; text closer than MARGIN px to an edge
  OVERLAP     elements touching each other (pixel masks, not boxes). Text on anything is an ERROR.
              Exempt: scenery (buildings, desks, podiums) and overlays (ice, bars) against non-text,
              stamps (they slam on top on purpose), actors with ok=True, members of the same
              ok-group (e.g. a crowd), and anything mid-move/fall.
  BUBBLE      speech-bubble text not fully inside its ellipse
  SPACING     two text elements closer than GAP px
  CLUTTER     more than MAX_TEXT text elements on screen at once
  BALANCE     the scene's visual weight sits far off-centre
  READING     a caption is on screen too briefly for its word count
  GROUND      on street backgrounds, standing things must stand on the near pavement (y >= 890)
  DEPTH       a foreground building on a full street background (use the "<bg>_far" variant)
  TARGET      a stamp with no target or not landing on it; a bubble with no speaker, speaker not on
              screen, or tail pointing away from the speaker
Writes WORKDIR/visual_report.md. With --sheets also writes WORKDIR/sheets/sheet_NN.png: the final
frame of every scene captioned with its time and the narration, for the relevance/story review.
"""
import json, os, sys, textwrap
import numpy as np
from PIL import Image, ImageDraw
import art
from art import W, H
from kit import load_episode
import render

MARGIN, GAP, MAX_TEXT, DS = 24, 16, 4, 4  # DS: mask downsample factor
TEXT = ("label", "bubble")
ep = load_episode()
WORK = os.environ.get("WORKDIR", "work")


def mask_of(img):
    a = np.asarray(img.getchannel("A"))
    return a > 110  # ignore the soft drop shadow


def placed(a, T, s0):
    st = render.actor_state(a, T, s0, 0)
    if st is None:
        return None
    x, y, sc, rot, v = st
    img = a.v[v]
    if a.anchor == "bc":
        px, py = int(x - img.width / 2), int(y - img.height)
    else:
        px, py = int(x - img.width / 2), int(y - img.height / 2)
    m = mask_of(img)
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return None
    box = (px + xs.min(), py + ys.min(), px + xs.max(), py + ys.max())
    if box[2] < 0 or box[0] > W or box[3] < 0 or box[1] > H:
        return None  # wholly off screen (walked off, not yet arrived): not visible
    t_in = a.t if a.t is not None else s0
    moving = T < t_in + a.dur or (a.move and a.move[0] <= T <= a.move[1] + 0.1) or (a.fall is not None and T > a.fall) \
        or a.swing is not None
    return dict(img=img, px=px, py=py, box=box, mask=m, moving=moving)


def frame_mask(p):
    out = np.zeros((H // DS + 1, W // DS + 1), bool)
    m = p["mask"][::DS, ::DS]
    x0, y0 = p["px"] // DS, p["py"] // DS
    h, w = m.shape
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(out.shape[1], x0 + w), min(out.shape[0], y0 + h)
    if dx1 > dx0 and dy1 > dy0:
        out[dy0:dy1, dx0:dx1] = m[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
    return out


def exempt(a, b):
    kinds = {a.kind, b.kind}
    if kinds & {"scenery", "overlay"} and not kinds & set(TEXT):
        return True
    if a.kind == "stamp" or b.kind == "stamp" or a.ok is True or b.ok is True:
        return True
    return isinstance(a.ok, str) and a.ok == b.ok


def desc(a):
    n = a.name.replace("\n", " ") if a.name else ""
    return f"{a.kind} '{n[:40]}'" if n else a.kind


def narration(transcript, t0, t1):
    return " ".join(s["text"] for s in transcript if s["start"] < t1 - 0.2 and s["end"] > t0 + 0.2)


def main():
    S = ep.build()
    tpath = os.path.join(WORK, "transcript.json")
    transcript = json.load(open(tpath)) if os.path.exists(tpath) else []
    issues = []  # (severity, scene_idx, time, msg)
    seen = set()

    def add(sev, i, T, msg):
        key = (i, msg)
        if key not in seen:
            seen.add(key)
            issues.append((sev, i, T, msg))

    for i, sc in enumerate(S):
        end = S[i + 1].start if i + 1 < len(S) else ep.END
        # bubble geometry (once per actor)
        for a in sc.actors:
            img = next(iter(a.v.values()))
            if a.kind == "bubble" and "ellipse" in img.info:
                cx, cy, rx, ry = img.info["ellipse"]
                x0, y0, x1, y1 = img.info["textbox"]
                for qx, qy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                    if ((qx - cx) / rx) ** 2 + ((qy - cy) / ry) ** 2 > 1.0:
                        add("ERROR", i, sc.start, f"BUBBLE text spills outside the bubble: {desc(a)}")
                        break
            # reading time
            if a.kind in TEXT:
                t_in = a.t if a.t is not None else sc.start
                t_out = min(a.out if a.out is not None else end, end)
                secs = t_out - t_in
                words = len((a.name or "").split())
                if secs < 1.2 or (words and words / max(secs, 0.01) > 3.5):
                    add("WARN", i, t_in, f"READING {desc(a)} only on screen {secs:.1f}s for {words} words")
        # sample when each element has fully entered, and just before the cut
        samples = {end - 0.06}
        for a in sc.actors:
            t_in = a.t if a.t is not None else sc.start
            ts = t_in + a.dur + 0.05
            if sc.start <= ts < end:
                samples.add(ts)
        for T in sorted(samples):
            vis = []
            for a in sc.actors:
                p = placed(a, T, sc.start)
                if p:
                    vis.append((a, p))
            text = [(a, p) for a, p in vis if a.kind in TEXT]
            if len(text) > MAX_TEXT:
                add("WARN", i, T, f"CLUTTER {len(text)} captions/bubbles on screen at once")
            for a, p in vis:
                if p["moving"]:
                    continue
                x0, y0, x1, y1 = p["box"]
                m = MARGIN if a.kind in TEXT else -4
                if x0 < m or y0 < m or x1 > W - m or (y1 > H - m and a.kind in TEXT):
                    add("ERROR" if a.kind in TEXT else "WARN", i, T,
                        f"OFF-FRAME {desc(a)} box=({x0},{y0},{x1},{y1})")
            masks = [frame_mask(p) for _, p in vis]
            for j in range(len(vis)):
                for k in range(j + 1, len(vis)):
                    a, pa = vis[j]
                    b, pb = vis[k]
                    if pa["moving"] or pb["moving"] or exempt(a, b):
                        continue
                    inter = int((masks[j] & masks[k]).sum()) * DS * DS
                    if inter > 300:
                        sev = "ERROR" if (a.kind in TEXT or b.kind in TEXT) else "WARN"
                        add(sev, i, T, f"OVERLAP {desc(a)} x {desc(b)} ({inter}px)")
                    elif a.kind in TEXT and b.kind in TEXT:
                        ax0, ay0, ax1, ay1 = pa["box"]
                        bx0, by0, bx1, by1 = pb["box"]
                        gx = max(bx0 - ax1, ax0 - bx1)
                        gy = max(by0 - ay1, ay0 - by1)
                        if max(gx, gy) < GAP:
                            add("WARN", i, T, f"SPACING {desc(a)} and {desc(b)} only {max(gx, gy)}px apart")
        # depth: a foreground building in front of same-size street buildings reads as pasted on
        if sc.bgk in art.STREETS and sc.bgk not in ("washington",):
            for a in sc.actors:
                if a.name == "building":
                    add("ERROR", i, sc.start, f"DEPTH foreground building on '{sc.bgk}': use '{sc.bgk}_far'")
                    break
        street = sc.bgk.removesuffix("_far") in art.STREETS
        ids = {a.id: a for a in sc.actors if a.id}
        for a in sc.actors:
            if a.kind not in ("stamp", "bubble"):
                continue
            t_in = a.t if a.t is not None else sc.start
            T = min(t_in + a.dur + 0.05, end - 0.06)
            if not a.target:
                add("ERROR", i, T, f"TARGET {desc(a)} has no target= (what is it about?)")
                continue
            tg = ids.get(a.target)
            pa, pt = placed(a, T, sc.start), (placed(tg, T, sc.start) if tg else None)
            if pt is None:
                add("ERROR", i, T, f"TARGET {desc(a)} -> '{a.target}' is not on screen")
                continue
            if pa is None:
                continue
            if a.kind == "stamp":
                ma, mt = frame_mask(pa), frame_mask(pt)
                frac = (ma & mt).sum() / max(1, ma.sum())
                if frac < 0.2:
                    add("ERROR", i, T, f"TARGET {desc(a)} lands on the background, not on '{a.target}' "
                                       f"({frac:.0%} on target)")
            else:
                tail = next(iter(a.v.values())).info.get("tail", "left")
                bx = (pa["box"][0] + pa["box"][2]) / 2
                sx = (pt["box"][0] + pt["box"][2]) / 2
                if (sx < bx and tail != "left") or (sx > bx and tail != "right"):
                    add("ERROR", i, T, f"TARGET {desc(a)}: tail points {tail} but '{a.target}' is on the "
                                       f"{'left' if sx < bx else 'right'}")
                if abs(sx - bx) > 950:
                    add("WARN", i, T, f"TARGET {desc(a)} is far from its speaker '{a.target}'")
        # ground: on streets, standing things stand on the near pavement
        if street:
            T = end - 0.06
            for a in sc.actors:
                if a.anchor != "bc" or a.kind not in ("char", "scenery", "prop") or a.name in ("gavel",):
                    continue
                p = placed(a, T, sc.start)
                if p is None or p["moving"]:
                    continue
                if sc.bgk.startswith("washington") and a.name == "building":
                    continue  # the Capitol sits on the far lawn by design
                bottom = p["box"][3]
                if bottom < 890:
                    add("ERROR", i, T, f"GROUND {desc(a)} stands at y={bottom}, in the road/sky; "
                                       f"stand it on the pavement (y>=890)")
        # balance at the final frame
        allm = None
        for a in sc.actors:
            p = placed(a, end - 0.06, sc.start)
            if p:
                fm = frame_mask(p)
                allm = fm if allm is None else (allm | fm)
        if allm is not None and allm.sum():
            ys, xs = np.nonzero(allm)
            off = (xs.mean() * DS - W / 2) / W
            if abs(off) > 0.2:
                add("WARN", i, end - 0.06, f"BALANCE visual weight sits {'right' if off > 0 else 'left'} "
                                           f"of centre ({off:+.0%} of width)")

    lines = ["# Visual check report", "",
             f"Episode: `{os.environ.get('EPISODE')}` - {len(S)} scenes", "",
             f"**{sum(1 for s in issues if s[0] == 'ERROR')} errors, "
             f"{sum(1 for s in issues if s[0] == 'WARN')} warnings**", ""]
    for i, sc in enumerate(S):
        si = [x for x in issues if x[1] == i]
        if not si:
            continue
        end = S[i + 1].start if i + 1 < len(S) else ep.END
        lines.append(f"## Scene {i} ({sc.start:.1f}s-{end:.1f}s, bg={sc.bgk})")
        if transcript:
            lines.append(f"> {narration(transcript, sc.start, end)}")
        for sev, _, T, msg in sorted(si, key=lambda x: x[2]):
            lines.append(f"- **{sev}** @{T:.1f}s {msg}")
        lines.append("")
    os.makedirs(WORK, exist_ok=True)
    open(os.path.join(WORK, "visual_report.md"), "w").write("\n".join(lines))
    print("\n".join(lines[:6]))

    if "--sheets" in sys.argv:
        out = os.path.join(WORK, "sheets")
        os.makedirs(out, exist_ok=True)
        bgs, tiles = {}, []
        for i, sc in enumerate(S):
            end = S[i + 1].start if i + 1 < len(S) else ep.END
            T = end - 0.06
            fr = render.render_frame(sc, end, T, int(T * render.FPS), bgs).resize((640, 360))
            tile = Image.new("RGB", (640, 470), "white")
            tile.paste(fr, (0, 0))
            d = ImageDraw.Draw(tile)
            n = sum(1 for x in issues if x[1] == i and x[0] == "ERROR")
            d.text((8, 366), f"#{i}  {sc.start:.1f}-{end:.1f}s" + (f"   {n} ERRORS" if n else ""),
                   fill=(200, 0, 0) if n else (0, 0, 0), font=art.font("title", 20))
            nar = narration(transcript, sc.start, end) if transcript else ""
            for li, l in enumerate(textwrap.wrap(nar, 70)[:4]):
                d.text((8, 392 + li * 19), l, fill=(40, 40, 40), font=art.font("hand", 18))
            tiles.append(tile)
        for s in range(0, len(tiles), 6):
            sheet = Image.new("RGB", (1280, 1410), "white")
            for j, t in enumerate(tiles[s:s + 6]):
                sheet.paste(t, ((j % 2) * 640, (j // 2) * 470))
            sheet.save(os.path.join(out, f"sheet_{s // 6:02d}.png"))
        print(f"sheets: {out}")
        log = os.path.join(WORK, "review_log.md")
        rows = ["# Sheet review log", "",
                "Look at EVERY sheet. For each, check: elements match the narration and move the story on;",
                "captions correct; characters consistent and recognisable; physically sensible (things stand",
                "on the ground, near things bigger than far things, nothing floating or sunk); every stamp,",
                "arrow and bubble clearly points at what it is about; balanced spacing.",
                "Replace [ ] with [x] and a short note. make_video.sh refuses to render while any [ ] remains.", ""]
        for s in range(0, len(tiles), 6):
            rows.append(f"- [ ] sheet_{s // 6:02d}.png (scenes {s}-{min(s + 5, len(tiles) - 1)}): ")
        open(log, "w").write("\n".join(rows) + "\n")
        print(f"review log: {log}")


if __name__ == "__main__":
    main()
