#!/usr/bin/env bash
# Final export check before delivery. Usage: tools/qc.sh out/final.mp4
# Fails (exit 1) on anything that would get rejected or look broken on YouTube.
set -uo pipefail
f="${1:-out/final.mp4}"
dir="$(dirname "$f")/qc"; mkdir -p "$dir"
fail=0
ok()   { printf '  \033[32mOK\033[0m   %s\n' "$1"; }
bad()  { printf '  \033[31mCHYBA\033[0m %s\n' "$1"; fail=1; }
warn() { printf '  \033[33mPOZOR\033[0m %s\n' "$1"; }

[ -s "$f" ] || { echo "súbor $f neexistuje"; exit 1; }
v() { ffprobe -v error -select_streams v:0 -show_entries "stream=$1" -of csv=p=0 "$f"; }
a() { ffprobe -v error -select_streams a:0 -show_entries "stream=$1" -of csv=p=0 "$f"; }

echo "== $f"
[ "$(v width),$(v height)" = "1080,1920" ] && ok "rozlíšenie 1080x1920 (9:16)" || bad "rozlíšenie $(v width)x$(v height)"
[ "$(v codec_name)" = "h264" ] && ok "video kodek h264" || bad "video kodek $(v codec_name)"
[ "$(v pix_fmt)" = "yuv420p" ] && ok "pix_fmt yuv420p" || bad "pix_fmt $(v pix_fmt)"
[ "$(v r_frame_rate)" = "30/1" ] && ok "30 fps" || bad "fps $(v r_frame_rate)"
[ "$(a codec_name)" = "aac" ] && ok "audio aac" || bad "audio $(a codec_name)"
[ "$(a sample_rate)" = "48000" ] && ok "audio 48 kHz" || bad "audio $(a sample_rate) Hz"

dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
vd=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "$f")
ad=$(ffprobe -v error -select_streams a:0 -show_entries stream=duration -of csv=p=0 "$f")
diff=$(python3 -c "print(abs($vd-$ad))")
python3 -c "import sys; sys.exit(0 if $diff<0.1 else 1)" && ok "dĺžka ${dur}s, rozdiel audio/video ${diff}s" || bad "audio a video sa líšia o ${diff}s"
python3 -c "import sys; sys.exit(0 if $dur<=180 else 1)" && ok "do 3 min (YouTube Shorts)" || warn "dlhšie ako 3 min – nebude Shorts"

loud=$(ffmpeg -hide_banner -nostats -i "$f" -af ebur128=peak=true -f null - 2>&1 | grep -A20 "Summary" )
I=$(echo "$loud" | awk '/I:/{print $2; exit}'); TP=$(echo "$loud" | awk '/Peak:/{print $2; exit}')
python3 -c "import sys; sys.exit(0 if -16<=$I<=-12 else 1)" && ok "hlasitosť ${I} LUFS (cieľ −14)" || bad "hlasitosť ${I} LUFS"
python3 -c "import sys; sys.exit(0 if $TP<=-1.0 else 1)" && ok "true peak ${TP} dBTP" || bad "true peak ${TP} dBTP (clipping)"

sil=$(ffmpeg -hide_banner -nostats -i "$f" -af silencedetect=n=-45dB:d=1.5 -f null - 2>&1 | grep -c silence_start)
[ "$sil" = "0" ] && ok "žiadne ticho > 1,5 s" || warn "$sil úsekov ticha > 1,5 s – skontroluj"
blk=$(ffmpeg -hide_banner -nostats -i "$f" -vf blackdetect=d=0.3:pix_th=0.08 -an -f null - 2>&1 | grep -c black_start)
[ "$blk" = "0" ] && ok "žiadne čierne zábery" || bad "$blk čiernych úsekov"
frz=$(ffmpeg -hide_banner -nostats -i "$f" -vf "crop=1080:1152:0:768,freezedetect=n=0.002:d=2.5" -an -f null - 2>&1 | grep -c freeze_start)
[ "$frz" = "0" ] && ok "avatar sa nezasekol (> 2,5 s)" || warn "$frz zamrznutí v oblasti avatara – skontroluj lip-sync"

# contact sheet: one frame every ~10 s for visual review
ffmpeg -loglevel error -y -i "$f" -vf "fps=1/10,scale=270:480,tile=6x3:padding=6:color=0xF7ECEA" -frames:v 1 "$dir/contact_sheet.png" \
  && ok "náhľady: $dir/contact_sheet.png" || bad "náhľady sa nepodarilo vytvoriť"

[ $fail = 0 ] && echo "VÝSLEDOK: export je pripravený" || echo "VÝSLEDOK: export NEPREŠIEL kontrolou"
exit $fail
