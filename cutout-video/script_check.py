"""Lint a Dom Talks Politics script against SCRIPT_STYLE.md. Exit code 1 if any ERROR.

Usage: python3 script_check.py scripts/<slug>.txt [--partial]
--partial: skip whole-script checks (length, required sections) - for drafts of a single section.
"""
import re, sys

WPM = 150  # Dom's narration pace
BEATS = {  # beat: (patterns, minimum count)
    "why it matters": ([r"this matters because", r"why (this|that|it) matters", r"why you should care",
                        r"here'?s why", r"what (this|that) means for you", r"matters to you"], 3),
    "pause and break it down": ([r"let'?s (stop|pause)", r"break (it|this|that) down", r"you need to (get|understand)",
                                 r"slow down", r"bear with me"], 2),
    "misconception": ([r"people (often )?(say|think|assume)", r"you'?ll hear", r"(most|a lot of) (people|coverage)",
                       r"that'?s not (quite )?right", r"common (myth|mistake|misconception)", r"gets? (this|that) wrong",
                       r"actually,"], 1),
    "recap": ([r"so that'?s (the )?(first|second|third|reason|piece|part)", r"so,? to recap", r"so far"], 2),
    "caveat": ([r"i don'?t want to overstate", r"to be fair", r"we don'?t (yet )?know", r"of course,"], 1),
    "footnote close": ([r"here'?s the footnote"], 1),
}
SECTIONS = ["COLD OPEN", "INTRO", "PART", "FOOTNOTE", "HANDOFF"]
UNSAFE = [r"\bf+u+c+k", r"\bshit", r"\bbitch", r"\bbastard", r"\bretard", r"\bkill (yourself|them all)",
          r"you should (buy|sell|invest)", r"\bguaranteed returns?\b"]


def main(path, partial=False):
    raw = open(path).read()
    errs, warns = [], []
    head, _, body = raw.partition("\n\n")
    meta = dict(re.findall(r"^([A-Z]+):\s*(.*)$", raw, re.M))
    lines = body.splitlines()
    spoken = []
    quotes = []
    for l in lines:
        s = l.strip()
        if not s or s.startswith("[") or s.startswith("#") or s.startswith("- http"):
            continue
        m = re.match(r'QUOTE \(([^)]+)\):\s*"?(.+?)"?$', s)
        if m:
            quotes.append((m.group(1), m.group(2)))
            spoken.append(m.group(2))
        else:
            spoken.append(s)
    text = " ".join(spoken)
    words = re.findall(r"[\w'’%$.-]+", text)
    n = len(words)
    mins = n / WPM
    if not partial:
        for k in ("TITLE", "TYPE", "TOPIC"):
            if k not in meta:
                errs.append(f"missing header {k}:")
        if "SOURCES" not in raw or len(re.findall(r"^- https?://", raw, re.M)) < 3:
            errs.append("needs a SOURCES list with at least 3 links")
        if mins < 8:
            errs.append(f"too short: {n} words ≈ {mins:.1f} min (need ≥ 8 min for mid-rolls, ~1,200+ words)")
        elif mins > 14:
            warns.append(f"long: {n} words ≈ {mins:.1f} min (target 8–12)")
        heads = re.findall(r"^\[([^\]]+)\]", body, re.M)
        for sec in SECTIONS:
            if not any(h.upper().startswith(sec) for h in heads):
                errs.append(f"missing section [{sec}…]")
        parts = [h for h in heads if h.upper().startswith("PART")]
        if not 4 <= len(parts) <= 10:
            warns.append(f"{len(parts)} parts (target 4–7)")
        low = text.lower()
        for beat, (pats, need) in BEATS.items():
            c = sum(len(re.findall(p, low)) for p in pats)
            if c < need:
                errs.append(f"beat '{beat}': found {c}, need ≥ {need}")
        hook = " ".join(spoken[:6])  # first ~15 seconds
        if "?" not in hook and not re.search(r"\b(but|yet|and yet|somehow|shouldn'?t|wasn'?t supposed)\b", hook.lower()):
            warns.append("cold open has no paradox/question in its first lines")
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    lens = [len(s.split()) for s in sents]
    if lens:
        avg = sum(lens) / len(lens)
        if avg > 17:
            warns.append(f"average sentence {avg:.1f} words (target 12–16)")
        for s, ln in zip(sents, lens):
            if ln > 30:
                errs.append(f"sentence too long ({ln} words): {s[:80]}…")
    for who, q in quotes:
        if len(q.split()) > 25:
            errs.append(f"quote from {who} is {len(q.split())} words (max 25): {q[:60]}…")
    for p in UNSAFE:
        for m in re.finditer(p, text.lower()):
            errs.append(f"advertiser-unsafe wording: '{m.group(0)}'")
    if re.search(r"\b(stole|fraudster|criminal|corrupt)\b", text.lower()) and not re.search(
            r"\b(alleg|accus|deni|presumed innocent|not been proven|hasn'?t been proven)", text.lower()):
        warns.append("strong accusations without any 'alleged/denies' framing - check fairness")
    print(f"{path}: {n} words ≈ {mins:.1f} min, {len(sents)} sentences, {len(quotes)} quotes")
    for e in errs:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
    print("PASS" if not errs else f"FAIL ({len(errs)} errors)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], "--partial" in sys.argv))
