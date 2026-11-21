#!/usr/bin/env bash
# One-time setup: Python deps + a Whisper model.
# Hugging Face may be blocked in cloud sessions, so the model comes from npm
# (Whisper small, CTranslate2 int8, split into 4 packages) and is checksum-verified.
set -euo pipefail
pip install -q faster-whisper numpy pillow wordfreq
M="${WHISPER_MODEL:-$HOME/.cache/cutout-video/whisper-small}"
if [ -f "$M/model.bin" ]; then echo "model ready: $M"; exit 0; fi
mkdir -p "$M"; T=$(mktemp -d)
( cd "$T" && for p in 0 1 2 3; do npm pack --silent "@skillninja/shortmovie-telop-model-p$p" >/dev/null; done
  for f in *.tgz; do d="${f%.tgz}"; mkdir "$d"; tar xzf "$f" -C "$d"; done )
P0=$(ls -d "$T"/*-p0-*/package)
cp "$P0"/{config.json,preprocessor_config.json,tokenizer.json,vocabulary.json} "$M/"
cat "$T"/*-p0-*/package/model.bin.part0 "$T"/*-p1-*/package/model.bin.part1 \
    "$T"/*-p2-*/package/model.bin.part2 "$T"/*-p3-*/package/model.bin.part3 > "$M/model.bin"
want=$(cut -d' ' -f1 "$P0/model.sha256"); got=$(sha256sum "$M/model.bin" | cut -d' ' -f1)
rm -rf "$T"
[ "$want" = "$got" ] || { echo "checksum mismatch"; rm -f "$M/model.bin"; exit 1; }
echo "model ready: $M"
