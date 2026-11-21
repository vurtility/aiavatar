#!/usr/bin/env bash
# Render an episode timeline + narration into a finished MP4.
# Usage: ./make_video.sh episodes/<name>.py narration.mp3 output/<name>.mp4 [WORKDIR]
# WORKDIR must hold audio16k.raw from transcribe.py.
set -euo pipefail
cd "$(dirname "$0")"
EP="$1"; MP3="$2"; OUT="$3"; WORK="${4:-work}"
export EPISODE="$EP" WORKDIR="$WORK"
# QA gates: automated check must be clean and every review sheet must be signed off
python3 check.py >/dev/null  # (re-running with --sheets resets the review log: new sheets need a new review)
grep -q "^\*\*0 errors" "$WORK/visual_report.md" || { echo "visual check has errors: $WORK/visual_report.md"; exit 1; }
[ -f "$WORK/review_log.md" ] && ! grep -q "^- \[ \]" "$WORK/review_log.md" || {
  echo "review sheets not all signed off: $WORK/review_log.md"; exit 1; }
N=$(python3 -c "from kit import load_episode; print(int(load_episode().END*12))")
J=${JOBS:-$(nproc)}; Q=$(( (N + J - 1) / J ))
rm -f "$WORK"/chunk*.mp4 "$WORK"/list.txt
for i in $(seq 0 $((J-1))); do
  s=$((i*Q)); e=$(( (i+1)*Q < N ? (i+1)*Q : N )); [ $s -ge $e ] && continue
  python3 render.py chunk $s $e "$WORK/chunk$i.mp4" > "$WORK/log$i.txt" 2>&1 &
  echo "file 'chunk$i.mp4'" >> "$WORK/list.txt"
done
python3 sfx.py "$MP3" "$WORK/mix.wav"
wait
grep -l Error "$WORK"/log*.txt && { echo "render failed, see logs"; exit 1; } || true
mkdir -p "$(dirname "$OUT")"
ffmpeg -loglevel error -y -f concat -safe 0 -i "$WORK/list.txt" -i "$WORK/mix.wav" -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
echo "done: $OUT"
