---
name: cutout-video
description: Make a "Dom Talks Politics" paper-cutout cartoon explainer video. Covers scripting in the channel's explain-it-to-a-friend style, a pronunciation pass before and after the voiceover, scene planning, drawing and animating, a visual QA loop, sound effects and rendering. Use when the user asks for a new episode, a script, a cutout/cartoon video from a narration MP3, or to fix or re-render an existing episode.
---

# Cutout explainer video workflow

Everything lives in `cutout-video/` (see its README). Work in a scratch WORKDIR for big files (audio,
chunks, sheets). Rendered MP4s are git-ignored because they're over GitHub's 100 MB limit. Send them with
SendUserFile.

Stop at the **[CHECKPOINT]** steps and get the user's OK before moving on.

## 0. Setup (once per session)
`cd cutout-video && ./setup.sh`. This installs deps and fetches Whisper from npm, because Hugging Face is
blocked in cloud sessions.

## 1. Script
- Read `cutout-video/SCRIPT_STYLE.md` first and follow it: explain it like talking to a friend, use the
  why-it-matters / pause-and-break-it-down / misconception / story-link devices, and end on the footnote close.
- Research the topic properly and cite sources for every claim. Present allegations as allegations.
- Save as `cutout-video/scripts/<slug>.txt`, with one paragraph per beat and `PART N – Title` lines for part cards.
- **[CHECKPOINT]** The user reviews the script.

## 2. Pronunciation (before recording)
- `python3 pronounce.py prep scripts/<slug>.txt WORKDIR`
- For every term the sheet marks as needing a respelling, add an entry to `lexicon.json`, which is shared
  across episodes: `say` is a plain-English respelling for the TTS, `guide` shows the stress for humans. If
  a term is fine as written, set `say` to the word itself. Re-run until nothing is missing.
- Give the user `WORKDIR/dictionary.pls` (to upload to ElevenLabs as a pronunciation dictionary) or
  `WORKDIR/tts_script.txt` (respellings already substituted, ready to paste in), plus the pronunciation sheet.
- **[CHECKPOINT]** The user records the voiceover and sends the MP3.

## 3. Transcribe and verify pronunciation
- `python3 transcribe.py narration.mp3 WORKDIR` produces word timings and `audio16k.raw`.
- `python3 pronounce.py verify scripts/<slug>.txt WORKDIR` lists every hard term Whisper heard
  differently, with a timestamp. Report these to the user as "listen at m:ss". If one is genuinely wrong,
  fix its lexicon entry and have them regenerate that line before you animate.

## 4. Scene plan
- Use `WORKDIR/transcript.txt`, which has timings, to plan one scene per sentence or idea (about every
  4–10s, a part card for each part), and the sound-effect cues.
- **[CHECKPOINT]** Show the user a short scene table (time, what's on screen, captions) before you build it.

## 5. Build the episode
- Copy the shape of `episodes/paraguay_bank_crisis.py`. Use `kit.py` helpers: `C` for a character, `L`
  for a caption label, `P` for a prop or bubble, plus `crowd`, `gavel_actor` and `part_card`. Time every
  element to the word it illustrates. Put `SFX`, `WHOOSH`, `SHAKE` and `END` at the bottom.
- Add new characters to `art.CAST` and new props to `art.py`. Stay in the house style (below).
- **Real people must be recognisable.** Before you add a real person, look up their public appearance
  and give them their distinguishing traits through `person()` options: `build` (0.85 thin to 1.42 heavy,
  where 1.25 and up adds a belly), `height`, `head_w`, `hair` (short/side/slick/swoop/bald/curly/bun/long),
  hair colour, `brows`, `mustache`, `beard`, `glasses`, `jowls`, `old`, skin tone, suit and tie colours,
  `tie_w` and `outfit="longtie"` (a long tie), `pin` (a flag pin), `sash`, `cross`, and `rest` (their
  signature resting expression, e.g. Trump's `"pout"`). Exaggerate what viewers know them for, like a
  gentle caricature, and never mock. Write a one-line comment above each entry saying which traits it
  shows. Generic characters and crowds get a varied mix of builds and heights.
- **Every face should look different, as in classic cutout cartoons.** Use `head` (round, oval, square,
  egg, pear or bean), `head_h`/`head_w`, `eye_s`, `nose`, `ears` and the wider hairstyle set (spiky,
  afro, mohawk, buzz, ponytail, receding, beanie, slick, etc.). Real people get the shape that matches
  them. Generic characters (players, senators, extras, reporters) always use `C(..., vary=<unique int>)`;
  crowds vary automatically. Never put two identical generic faces side by side.
- **Depth and ground (street backgrounds):** buildings stand on the horizon (y=800). The road runs
  800–900, and people and props stand on the near pavement (y≈960; feet at y≥890). A scene whose subject
  is its own building uses the `<bg>_far` background (a hazy distant skyline), with that building
  placed at y=1000 on the pavement. Never put a foreground building in front of full-size street buildings.
- **Pointing things need targets:** give the thing an `id=` and give every stamp and speech bubble
  `target=<id>`. A stamp must land on its target, never on empty background. A bubble's `tail` must
  face its speaker. If a "stamp" is really a comment about something (e.g. "ALLEGATION – NOT
  PROVEN"), make it a caption placed next to the thing, not over its text.

## 6. Visual check loop (repeat until clean)
1. `EPISODE=episodes/<slug>.py WORKDIR=WORKDIR python3 check.py --sheets`
2. Fix every **ERROR** in `WORKDIR/visual_report.md`: text overlapping anything, text off-frame, or text
   spilling out of a bubble. Fix **WARN**s unless they're deliberate (e.g. a desk running off the edge).
   Deliberate layering gets `ok=True`, and a group allowed to overlap each other gets `ok="<group>"`.
3. Look at **every** `WORKDIR/sheets/sheet_NN.png` and fill in `WORKDIR/review_log.md`, changing each
   `[ ]` to `[x]` with a note on what you checked and fixed. `make_video.sh` refuses to render while
   any sheet is unticked or the report has errors. Re-running `check.py --sheets` resets the log,
   because new sheets need a new review. Each tile shows a scene's final frame with its
   narration underneath. Check that:
   - every element relates to what's being said and moves the story on, with nothing decorative or off-topic
   - captions are correct: names, numbers and spellings (brand casing such as "ueno")
   - characters are consistent: the same person keeps the same look, and nobody stands in for someone else
   - the layout is balanced and evenly spaced, with nothing crammed into a corner and no big empty half
   - allegations are labelled as allegations
   - it makes physical sense: things stand on the ground, near things are bigger than far things,
     nothing floats, sinks into the road or is cut off by the frame (falls and exits included)
   - every stamp, arrow and bubble clearly points at what it's about
4. Re-run until there are 0 errors and every warning remaining is deliberate.

## 7. Thumbnails (3 per video, for A/B testing)
- Define `thumbnails()` in the episode file using the helpers in `thumbnails.py`, then run
  `EPISODE=episodes/<slug>.py python3 thumbnails.py WORKDIR/thumbs`. This writes 1280x720 JPEGs.
- Each of the three tests a different hook: **A** a face reacting, **B** the stakes or a number, **C** the
  conflict or power angle. Use 3–5 huge words with a thick outline and one or two big recognisable
  characters. Text must be solid, never the rough stamp texture, which can't be read on a phone.
  Every claim shown must be true in the video.
- Look at all three at 640px wide (roughly phone size) before you keep them.

## 8. Render and deliver
- `./make_video.sh episodes/<slug>.py narration.mp3 output/<slug>.mp4 WORKDIR` (about 10 min for 11 min of video
  on 4 cores). Then pull 4–6 frames at hero moments (gavel hits, quotes) with ffmpeg and look at them.
- Send the MP4 with SendUserFile. Commit the episode, the script and lexicon changes, but not the MP4.

## 9. Google Drive archive
- Drive folder **Dom Talks Politics** (id `1MxKOp5yLcuQvgBJgQmNYlGIofpFuE41R`) holds one subfolder per
  episode, named `YYYY-MM <Title>`. Create it with the Drive connector (`create_file` with the
  folder mime type and that parentId).
- Upload with `create_file`, using `base64Content` set to a file reference
  (`sha256:<hash>:<absolute path>`) and `disableConversionToGoogleType: true`. Upload: script.txt, the 3
  thumbnails, pronunciation_sheet.md, pronunciation_check.md and visual_report.md.
- **The connector rejects files over 10 MB**, which rules out the MP4 and usually the narration MP3.
  Until there's a large-file route, deliver those with SendUserFile and note in the folder that
  they're held elsewhere.

## 10. YouTube upload
_Not set up yet. It needs YouTube Data API access to the channel (OAuth)._

## House visual style
- Construction-paper cutout look: flat colours, thin dark outlines, paper grain, soft drop shadows.
  Characters have wide round heads, big touching oval eyes with dot pupils, mitten hands and short legs.
  All characters are original; never copy characters from existing shows.
- Real public figures are simple caricatures, each with a name caption the first time they appear.
- Captions are torn-paper strips in Luckiest Guy. Speech bubbles use Patrick Hand. Cream is the default
  caption colour, yellow is for key numbers, red is for bad news, and green is for good news or approvals.
- Motion is stepped at 12fps: pop-ins, slides, bobbing, blinking, and mouth flaps on the speaker only.
  The camera pushes in slowly and shakes on impacts.
- Sound effects stay sparse: a gavel after the title and on big votes or verdicts, whooshes on part
  cards, stamps for official actions, and one-off effects (cash, glass, crowd) only where the script earns them.
