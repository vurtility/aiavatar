"""Pronunciation pass for the voiceover.

1) Before recording:  python3 pronounce.py prep script.txt WORKDIR
   - finds names/foreign words/acronyms the voice is likely to get wrong
   - writes WORKDIR/pronunciation_sheet.md   (terms, how to say them, which still need a respelling)
   - writes WORKDIR/dictionary.pls           (upload to ElevenLabs as a pronunciation dictionary)
   - writes WORKDIR/tts_script.txt           (fallback: script with respellings swapped in, paste into TTS)
   Respellings live in lexicon.json (shared across episodes); add new ones there and re-run.

2) After recording + transcribe.py:  python3 pronounce.py verify script.txt WORKDIR
   - aligns the script with what Whisper heard and lists every hard term that came out differently,
     with timestamps, in WORKDIR/pronunciation_check.md. Listen to each; re-generate those lines if wrong.
   Whisper mishearing a foreign name is not proof the voice got it wrong, but it is the place to listen.
"""
import difflib, json, os, re, sys, unicodedata
try:
    from wordfreq import zipf_frequency
except ImportError:  # optional: without it more everyday words get flagged
    def zipf_frequency(w, lang):
        return 0.0
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "lexicon.json")
COMMON_CAPS = set("""I A The This That These Those It Its In On At For From By With And But Or So If When While
Then There Here Today Tonight Yesterday Tomorrow We You He She They His Her Their Our My Your What Why How Who
Where Which Part Monday Tuesday Wednesday Thursday Friday Saturday Sunday January February March April May June
July August September October November December Congress Senate President Secretary State Treasury Party
Social Security Institute Court Human Rights Board Peace Shield Americas Central Bank House Wall Street Let
Let's Just Even Meanwhile Instead Under Before After Over About One Two Three Four Five Six Seven Eight Nine Ten
Twelve Critics Players Prosecutors Investigators Reuters Guardian Photos Hours Thousands Millions Pensioners
Every Its Here's That's Because South America American US UK""".split())


def load_lex():
    return json.load(open(LEX)) if os.path.exists(LEX) else {}


def norm(w):
    w = unicodedata.normalize("NFKD", w)
    return "".join(c for c in w if not unicodedata.combining(c)).lower().strip(".,!?;:'\"()-")


def phon(s):
    """Crude sound-alike key so spelling-only differences (ueno/Weno, Vázquez/Vasquez) are not flagged."""
    s = norm(s).replace("-", "").replace(" ", "")
    for a, b in (("ll", "y"), ("w", "u"), ("z", "s"), ("v", "b"), ("qu", "k"), ("c", "k"), ("h", "")):
        s = s.replace(a, b)
    return re.sub(r"(.)\1+", r"\1", s)


def hard_terms(text, lex):
    found = {}
    for term in lex:
        if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text):
            found[term] = "lexicon"
    for sent in re.split(r"(?<=[.!?])\s+", text):
        words = re.findall(r"[\w'’\-]+", sent)
        for i, w in enumerate(words):
            base = w.strip("'’").removesuffix("'s").removesuffix("’s")
            if not base or base in found:
                continue
            nonascii = any(ord(c) > 127 for c in base)
            acronym = len(base) >= 2 and base.isupper() and base.isalpha() and base not in ("US", "UK", "TV")
            common = zipf_frequency(base.lower(), "en") >= 3.0  # everyday English the voice knows
            proper = base[0].isupper() and i > 0 and base not in COMMON_CAPS and not base.isupper() \
                and not common
            lowerbrand = base[0].islower() and base in lex
            if nonascii or acronym or proper or lowerbrand:
                found.setdefault(base, "accent" if nonascii else "acronym" if acronym else "name")
    return found


def prep(script, work):
    text = open(script).read()
    lex = load_lex()
    terms = hard_terms(text, lex)
    os.makedirs(work, exist_ok=True)
    rows, missing = [], []
    for t, why in sorted(terms.items(), key=lambda kv: (kv[0] not in lex, kv[0].lower())):
        e = lex.get(t)
        if e:
            rows.append(f"| {t} | {e['say']} | {e.get('guide', '')} | ok |")
        else:
            missing.append(t)
            rows.append(f"| {t} | ? | ({why}) | **needs respelling or confirm fine** |")
    sheet = ["# Pronunciation sheet", "", f"Script: `{script}`", "",
             "| Term | Say (sent to TTS) | Guide | Status |", "|---|---|---|---|", *rows, "",
             f"{len(missing)} term(s) without an entry: {', '.join(missing) or 'none'}.",
             "Add an entry to lexicon.json for each one the voice could get wrong "
             "(`say` = plain-English respelling the TTS reads, `guide` = stressed syllables for humans), "
             "or `\"say\": \"<same word>\"` to mark it as fine."]
    open(os.path.join(work, "pronunciation_sheet.md"), "w").write("\n".join(sheet) + "\n")
    used = {t: lex[t] for t in terms if t in lex and lex[t]["say"] != t}
    pls = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<lexicon version="1.0" xmlns="http://www.w3.org/2005/01/pronunciation-lexicon" alphabet="ipa" '
           'xml:lang="en-US">']
    for t, e in sorted(used.items()):
        pls.append(f"  <lexeme><grapheme>{escape(t)}</grapheme><alias>{escape(e['say'])}</alias></lexeme>")
    pls.append("</lexicon>")
    open(os.path.join(work, "dictionary.pls"), "w").write("\n".join(pls) + "\n")
    tts = text
    for t, e in sorted(used.items(), key=lambda kv: -len(kv[0])):
        tts = re.sub(r"(?<!\w)" + re.escape(t) + r"(?!\w)", e["say"], tts)
    open(os.path.join(work, "tts_script.txt"), "w").write(tts)
    print("\n".join(sheet[4:]))


def verify(script, work):
    text = open(script).read()
    lex = load_lex()
    terms = hard_terms(text, lex)
    key = {norm(w) for t in terms for w in t.split()}
    sw = [w for w in re.findall(r"[\w'’\-]+", text)]
    segs = json.load(open(os.path.join(work, "transcript.json")))
    hw = [(s, e, w.strip()) for seg in segs for s, e, w in seg["words"]]
    sm = difflib.SequenceMatcher(a=[norm(w) for w in sw], b=[norm(w) for _, _, w in hw], autojunk=False)
    out = []
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == "equal":
            continue
        said = sw[a0:a1]
        if not any(norm(w) in key for w in said):
            continue
        heard = " ".join(w for _, _, w in hw[b0:b1]) or "(nothing)"
        if phon(" ".join(said)) == phon(heard):
            continue
        t = hw[b0][0] if b0 < len(hw) else (hw[-1][1] if hw else 0)
        out.append(f"| {int(t // 60)}:{t % 60:04.1f} | {' '.join(said)} | {heard} |")
    rep = ["# Pronunciation check", "", "Script terms that the transcript heard differently. "
           "Listen at each timestamp; if the voice got it wrong, add/adjust its lexicon.json entry and "
           "regenerate that line.", "", "| Time | Script | Heard |", "|---|---|---|", *out, "",
           f"{len(out)} place(s) to listen to."]
    open(os.path.join(work, "pronunciation_check.md"), "w").write("\n".join(rep) + "\n")
    print("\n".join(rep[4:]))


if __name__ == "__main__":
    cmd, script, work = sys.argv[1], sys.argv[2], sys.argv[3]
    {"prep": prep, "verify": verify}[cmd](script, work)
