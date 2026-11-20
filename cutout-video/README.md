# Cutout-style explainer video generator

Builds the "Dom Talks Politics – Paraguay's Bank Crisis" cartoon from a narration MP3.

- `art.py` – paper-cutout characters, props and backgrounds (PIL)
- `scenes.py` – timeline keyed to the narration's word timings, plus SFX cue list
- `render.py` – renders frames at 12fps (stepped cutout look), encodes to 24fps chunks
- `sfx.py` – synthesises gavel, whoosh, stamp, cash, glass, crowd and mixes under the voice

Fonts: Luckiest Guy and Patrick Hand (SIL Open Font License, via Fontsource).

```bash
ffmpeg -i narration.mp3 -ac 1 -ar 16000 -f f32le audio16k.raw   # for mouth-flap levels
python3 render.py chunk 0 7956 video.mp4
python3 sfx.py narration.mp3 mix.wav
ffmpeg -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac out.mp4
```

Rendered videos go in `output/` (git-ignored; they exceed GitHub's 100 MB file limit).
