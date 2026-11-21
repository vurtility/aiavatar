# Cutout-style explainer video generator

Builds the "Dom Talks Politics – Paraguay's Bank Crisis" cartoon from a narration MP3.

- `art.py` – paper-cutout characters, props and backgrounds (PIL)
- `kit.py` – timeline building blocks (characters, labels, props, crowds, gavel, part cards)
- `episodes/*.py` – one timeline per video, keyed to the narration's word timings, plus SFX cues
- `render.py` – renders frames at 12fps (stepped cutout look), encodes to 24fps chunks
- `sfx.py` – synthesises gavel, whoosh, stamp, cash, glass, crowd and mixes under the voice
- `transcribe.py` – Whisper word-timed transcript + `audio16k.raw` for mouth flaps
- `pronounce.py` + `lexicon.json` – pronunciation sheet / ElevenLabs dictionary before recording, mismatch check after
- `check.py` – visual QA: overlaps, off-frame, bubble overflow, spacing, balance, reading time + review sheets
- `SCRIPT_STYLE.md` – how Dom Talks Politics scripts are written
- `scripts/` – episode scripts (paraguay one is reconstructed from the transcript)

The full step-by-step workflow is the `cutout-video` skill in `.claude/skills/`.

Fonts: Luckiest Guy and Patrick Hand (SIL Open Font License, via Fontsource).

```bash
./setup.sh                                              # once per machine
python3 transcribe.py narration.mp3 work                # transcript + timings
# write episodes/<name>.py from work/transcript.txt
./make_video.sh episodes/<name>.py narration.mp3 output/<name>.mp4 work
```

Rendered videos go in `output/` (git-ignored; they exceed GitHub's 100 MB file limit).
