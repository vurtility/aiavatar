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

## 6. Visual check loop (repeat until clean)
1. `EPISODE=episodes/<slug>.py WORKDIR=WORKDIR python3 check.py --sheets`
2. Fix every **ERROR** in `WORKDIR/visual_report.md`: text overlapping anything, text off-frame, or text
   spilling out of a bubble. Fix **WARN**s unless they're deliberate (e.g. a desk running off the edge).
   Deliberate layering gets `ok=True`, and a group allowed to overlap each other gets `ok="<group>"`.
3. Look at **every** `WORKDIR/sheets/sheet_NN.png`. Each tile shows a scene's final frame with its
   narration underneath. Check that:
   - every element relates to what's being said and moves the story on, with nothing decorative or off-topic
   - captions are correct: names, numbers and spellings (brand casing such as "ueno")
   - characters are consistent: the same person keeps the same look, and nobody stands in for someone else
   - the layout is balanced and evenly spaced, with nothing crammed into a corner and no big empty half
   - allegations are labelled as allegations
4. Re-run until there are 0 errors and every warning remaining is deliberate.

## 7. Render and deliver
- `./make_video.sh episodes/<slug>.py narration.mp3 output/<slug>.mp4 WORKDIR` (about 10 min for 11 min of video
  on 4 cores). Then pull 4–6 frames at hero moments (gavel hits, quotes) with ffmpeg and look at them.
- Send the MP4 with SendUserFile. Commit the episode, the script and lexicon changes, but not the MP4.

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
