#!/usr/bin/env bash
# Lip-synced avatar clips with SadTalker (open source, CPU OK), no paid service.
# ENHANCER=gfpgan doubles CPU render time; EXPR sets mouth-movement strength (default 1.3).
#   SADTALKER=/path/to/SadTalker  PY=/path/to/venv/bin/python  tools/avatar_sadtalker.sh face.jpg
# Input audio: assets/vo/*.wav (narration) and assets/vo_ex/*.wav (example clips).
# Output: assets/avatar/<id>.mp4 and assets/media/<id>.mp4 (example clips keep their audio).
set -euo pipefail
face="${1:?cesta k fotke tváre}"
: "${SADTALKER:?nastav SADTALKER}"; : "${PY:?nastav PY}"
root="$(cd "$(dirname "$0")/.." && pwd)"
work="$root/build/sadtalker"; mkdir -p "$work" "$root/assets/avatar" "$root/assets/media"

render() {  # $1 = wav, $2 = output mp4
  local wav="$1" out="$2" id mp4; id="$(basename "$wav" .wav)"
  [ -s "$out" ] && { echo "skip $id"; return; }
  # SadTalker writes the final video as <result_dir>/<timestamp>.mp4 and deletes its temp folder;
  # reuse a finished render after an interruption instead of starting over
  mp4="$( (find "$work/$id" -maxdepth 1 -name '*.mp4' 2>/dev/null || true) | sort | tail -1)"
  if [ -z "$mp4" ]; then
    rm -rf "$work/$id"
    (cd "$SADTALKER" && "$PY" inference.py --driven_audio "$wav" --source_image "$face" \
        --result_dir "$work/$id" --still --preprocess full --size 256 --expression_scale "${EXPR:-1.3}" \
        ${ENHANCER:+--enhancer "$ENHANCER"} --cpu)
    mp4="$(find "$work/$id" -maxdepth 1 -name '*.mp4' | sort | tail -1)"
  fi
  [ -n "$mp4" ] || { echo "SadTalker nevytvoril video pre $id" >&2; return 1; }
  # re-encode to 30 fps h264 + 48 kHz audio from the original wav
  ffmpeg -loglevel error -y -i "$mp4" -i "$wav" -map 0:v -map 1:a -r 30 -c:v libx264 -crf 17 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -shortest "$out"
  echo "ok $id -> ${out#$root/}"
}

for wav in "$root"/assets/vo/*.wav; do render "$wav" "$root/assets/avatar/$(basename "$wav" .wav).mp4"; done
for wav in "$root"/assets/vo_ex/*.wav; do render "$wav" "$root/assets/media/$(basename "$wav" .wav).mp4"; done
