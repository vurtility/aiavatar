"""Transcribe a narration with word timings.

Usage: python3 transcribe.py narration.mp3 WORKDIR
Writes WORKDIR/audio16k.raw (used for mouth-flap levels), transcript.json and transcript.txt.
"""
import json, os, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

MODEL = os.environ.get("WHISPER_MODEL", os.path.expanduser("~/.cache/cutout-video/whisper-small"))

src, work = sys.argv[1], sys.argv[2]
os.makedirs(work, exist_ok=True)
raw = os.path.join(work, "audio16k.raw")
# decode with ffmpeg directly (faster-whisper's PyAV decoder can be version-incompatible)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ac", "1", "-ar", "16000", "-f", "f32le", raw],
               check=True)
audio = np.fromfile(raw, dtype=np.float32)
model = WhisperModel(MODEL, device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
segs, _ = model.transcribe(audio, language="en", word_timestamps=True, beam_size=1)
out = []
with open(os.path.join(work, "transcript.txt"), "w") as f:
    for s in segs:
        out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                    "words": [(w.start, w.end, w.word) for w in s.words]})
        line = f"{s.start:7.2f} {s.end:7.2f} {s.text.strip()}"
        print(line)
        f.write(line + "\n")
json.dump(out, open(os.path.join(work, "transcript.json"), "w"))
print(f"duration {len(audio) / 16000:.2f}s")
