# GLS Slovakia – 15 s motion concept

An independent portfolio concept, not an official GLS production. The end card credits it as "Nezávislý portfolio projekt".

- `out/gls-koncept-15s.mp4`: 1920×1080, 30 fps, 15.000 s, H.264 + AAC, about −16.7 LUFS
- `index.html`: the composition as Canvas 2D code. Open it in Chrome to preview (Space plays, S shows the 9:16 safe guide, ←/→ step one frame)
- `sound.py`: original sound design, synthesised with numpy → `audio/soundtrack.wav`
- `render.cjs`: headless Chromium render with motion blur, encoded by ffmpeg

## Rebuild
```
python3 sound.py
NODE_PATH=$(npm root -g) node render.cjs          # needs playwright + ffmpeg
node render.cjs --stills 2.6,7.9 --safe           # review stills with the 9:16 guide
```

## Where to edit
- Text: `COPY` in `index.html`. The claim and the credit name are placeholders for you to confirm.
- Colours: `COL`. The values are #061AB1 and #FFD100, sampled from gls-slovakia.sk. Confirm them against the brand guide.
- Logo: a typographic stand-in (Inter Display Black plus a yellow dot). Replace it with the official GLS SVG before any public use.
- Timing: each scene block in `render()`. Sound cues in `sound.py` mirror those timings.

## Claims used
Only these: parcel pickup, tracking, delivery to home / pickup point / locker, and a delivery time window. There are no numbers, times, awards or partners. Confirm on gls-slovakia.sk what GLS Slovakia offers.

Fonts: Inter Display (SIL Open Font License). Map: Natural Earth (public domain).
