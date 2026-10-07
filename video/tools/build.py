#!/usr/bin/env python3
"""Assemble the final 1080x1920 video from Higgsfield outputs.

Layout (STYL.md, section 5): board on top (768 px), subtitle line just below it,
AI avatar in the bottom 60 %, soft blush gradient between them.

Expected inputs (see produkcia.md for how each one is generated):
  assets/avatar/<scene>.mp4   lip-synced avatar clip (Higgsfield wan2_7)
  assets/vo/<scene>.wav|mp3   cloned-voice line (seed_audio); used as master audio if present
  assets/media/<name>.mp4     example footage referenced by board.media / tail[].media
  build/boards/<scene>.png    from tools/render_boards.mjs
Optional:
  assets/music.mp3            quiet background bed (--music-db sets its level)
  assets/align/<scene>.json   word timings [{"w": "...", "start": s, "end": s}] for exact subtitles

Usage: python3 tools/build.py [--crop-y 260] [--music-db -26] [--only s01,s02]
Writes build/segments/*.mp4 and out/final.mp4.
"""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
BOARD_H = 768
AV_H = H - BOARD_H
MEDIA = (170, 290, 740, 416)  # x, y, w, h — must match .media in boards.html
GRAD_H = 240
SUB_Y = 788
PAD_END = 0.35

BURGUNDY = "&H00120F6B"   # #6B0F12 in ASS BGR
TEXT_DARK = "&H000C0A3B"  # #3B0A0C


def run(cmd):
    subprocess.run(cmd, check=True)


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True).stdout.strip()
    return float(out)


def has_audio(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True).stdout.strip()
    return bool(out)


def find(folder, stem, exts):
    for ext in exts:
        p = ROOT / "assets" / folder / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def ass_text(s):
    """'*kľúčové slovo*' -> italic burgundy Playfair, everything else Caslon."""
    s = s.replace("{", "(").replace("}", ")")
    return re.sub(r"\*([^*]+)\*",
                  lambda m: r"{\fnPlayfair Display\i1\c" + BURGUNDY + "&}" + m.group(1) + r"{\r}", s)


def ts(t):
    t = max(0.0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def chunk_times(chunks, start, end, align):
    """Timings per subtitle chunk: from word alignment if present, else by character share."""
    if align:
        words = [a for a in align if a.get("w", "").strip()]
        times, i = [], 0
        for c in chunks:
            n = len(re.sub(r"\*", "", c).split())
            seg = words[i:i + n] or words[-1:]
            times.append((seg[0]["start"], seg[-1]["end"]))
            i += n
        return [(a + start, b + start) for a, b in times]
    weights = [len(re.sub(r"\*", "", c)) + 4 for c in chunks]
    total, t, out = sum(weights), start, []
    for w in weights:
        d = (end - start) * w / total
        out.append((t, t + d))
        t += d
    return out


def write_ass(path, events):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Libre Caslon Text,58,{TEXT_DARK},{TEXT_DARK},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,8,80,80,{SUB_Y},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [f"Dialogue: 0,{ts(a)},{ts(b)},Sub,,0,0,0,,{{\\fad(160,120)}}{ass_text(t)}" for a, b, t in events]
    path.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")


def make_static_assets(build):
    grad = build / "gradient.png"
    if not grad.exists():
        # blush (#F7ECEA) fading from opaque to transparent over GRAD_H px
        run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=c=0xF7ECEA:s={W}x{GRAD_H},format=rgba",
             "-vf", f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='255*pow(1-Y/{GRAD_H},1.6)'", "-frames:v", "1", str(grad)])
    mask = build / "media_mask.png"
    if not mask.exists():
        x, y, w, h = MEDIA
        r = 16
        expr = (f"if(lte(hypot(max(0,abs(X-{w}/2)-({w}/2-{r})),max(0,abs(Y-{h}/2)-({h}/2-{r}))),{r}),255,0)")
        run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=c=white:s={w}x{h},format=gray",
             "-vf", f"geq=lum='{expr}'", "-frames:v", "1", str(mask)])
    pop = build / "sfx_pop.wav"
    if not pop.exists():
        run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
             "aevalsrc='0.5*sin(2*PI*(520+900*exp(-40*t))*t)*exp(-28*t)':s=48000:d=0.18",
             "-af", "lowpass=f=3500,afade=t=in:d=0.004", "-ac", "2", str(pop)])
    swoosh = build / "sfx_swoosh.wav"
    if not swoosh.exists():
        run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anoisesrc=d=0.45:c=pink:a=0.35:r=48000",
             "-af", "bandpass=f=1800:w=1400,afade=t=in:d=0.2,afade=t=out:st=0.2:d=0.25", "-ac", "2", str(swoosh)])
    return grad, mask, pop, swoosh


def build_scene(scene, idx, prev_part, args, build, statics):
    grad, mask, pop, swoosh = statics
    sid = scene["id"]
    avatar = find("avatar", sid, [".mp4", ".mov"])
    if not avatar:
        raise SystemExit(f"chýba assets/avatar/{sid}.mp4")
    vo = find("vo", sid, [".wav", ".mp3", ".m4a"])
    audio_src = vo or (avatar if has_audio(avatar) else None)
    if not audio_src:
        raise SystemExit(f"{sid}: chýba hlas (assets/vo/{sid}.wav) a avatar klip nemá zvuk")
    vo_len = probe_duration(audio_src)
    main_len = vo_len + PAD_END

    tails = []
    for t in scene.get("tail", []):
        p = find("media", t["media"], [".mp4", ".mov"])
        if not p:
            raise SystemExit(f"{sid}: chýba assets/media/{t['media']}.mp4")
        tails.append((p, probe_duration(p), t.get("sub", "")))
    total = main_len + sum(d for _, d, _ in tails)

    align_p = ROOT / "assets" / "align" / f"{sid}.json"
    align = json.loads(align_p.read_text()) if align_p.exists() else None
    times = chunk_times(scene["subs"], 0.05, vo_len, align)
    events = [(a, b, text) for (a, b), text in zip(times, scene["subs"])]
    t0 = main_len
    for _, d, sub in tails:
        if sub:
            events.append((t0 + 0.1, t0 + d - 0.1, sub))
        t0 += d
    ass = build / "subs" / f"{sid}.ass"
    ass.parent.mkdir(parents=True, exist_ok=True)
    write_ass(ass, events)

    board = build / "boards" / f"{sid}.png"
    if not board.exists():
        raise SystemExit(f"chýba {board} — spusti najprv tools/render_boards.mjs")

    inputs = ["-f", "lavfi", "-t", f"{total:.3f}", "-i", f"color=c=0xF7ECEA:s={W}x{H}:r={FPS}",
              "-loop", "1", "-t", f"{total:.3f}", "-i", str(board),
              "-i", str(avatar),
              "-loop", "1", "-t", f"{total:.3f}", "-i", str(grad),
              "-i", str(audio_src),
              "-i", str(swoosh if scene["part"] != prev_part else pop)]
    n = 6
    cover = lambda w, h: f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
    av_chain = (f"[2:v]fps={FPS},scale={W}:-2,crop={W}:{AV_H}:0:'min(ih-{AV_H},{args.crop_y})',setsar=1,unsharp=5:5:0.5,"
                f"tpad=stop_mode=clone:stop_duration={total:.3f},trim=duration={main_len:.3f},setpts=PTS-STARTPTS[av0]")
    f = [av_chain]
    av_parts = ["[av0]"]
    for i, (p, d, _) in enumerate(tails):
        inputs += ["-i", str(p)]
        f.append(f"[{n}:v]fps={FPS},scale={W}:-2,crop={W}:{AV_H}:0:'min(ih-{AV_H},{args.crop_y})',setsar=1,unsharp=5:5:0.5,trim=duration={d:.3f},setpts=PTS-STARTPTS[tv{i}]")
        av_parts.append(f"[tv{i}]")
        n += 1
    if len(av_parts) > 1:
        f.append(f"{''.join(av_parts)}concat=n={len(av_parts)}:v=1:a=0[av]")
    else:
        f.append("[av0]null[av]")

    f.append(f"[0:v][av]overlay=0:{BOARD_H}:shortest=1[b1]")
    f.append(f"[b1][3:v]overlay=0:{BOARD_H}[b2]")
    f.append(f"[1:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1[brd]")
    f.append(f"[b2][brd]overlay=0:'12*max(0,1-t/0.3)'[b3]")
    last = "[b3]"

    media_name = scene["board"].get("media")
    if media_name:
        mp = find("media", media_name, [".mp4", ".mov", ".png", ".jpg"])
        if not mp:
            raise SystemExit(f"{sid}: chýba assets/media/{media_name}.mp4")
        x, y, w, h = MEDIA
        loop = ["-loop", "1"] if mp.suffix in (".png", ".jpg") else ["-stream_loop", "-1"]
        inputs += loop + ["-t", f"{total:.3f}", "-i", str(mp), "-loop", "1", "-t", f"{total:.3f}", "-i", str(mask)]
        f.append(f"[{n}:v]fps={FPS},{cover(w, h)},setsar=1,format=rgba[m0]")
        f.append(f"[{n+1}:v]format=gray[mk]")
        f.append(f"[m0][mk]alphamerge,fade=t=in:st=0.25:d=0.35:alpha=1[med]")
        f.append(f"{last}[med]overlay={x}:'{y}+10*max(0,1-(t-0.25)/0.35)'[b4]")
        last = "[b4]"
        n += 2

    subs_path = str(ass).replace(":", r"\:")
    fonts = str(ROOT / "fonts").replace(":", r"\:")
    f.append(f"{last}subtitles='{subs_path}':fontsdir='{fonts}',format=yuv420p[v]")

    # audio: voice line, then tail clips' own audio, SFX at scene start, optional music bed
    f.append(f"[4:a]aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={main_len:.3f},atrim=duration={main_len:.3f}[a0]")
    a_parts = ["[a0]"]
    for i, (p, d, _) in enumerate(tails):
        src = 6 + i
        if has_audio(p):
            f.append(f"[{src}:a]aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={d:.3f},atrim=duration={d:.3f}[ta{i}]")
        else:
            f.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={d:.3f}[ta{i}]")
        a_parts.append(f"[ta{i}]")
    f.append(f"{''.join(a_parts)}concat=n={len(a_parts)}:v=0:a=1[voice]")
    f.append("[5:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.35[sfx]")
    f.append("[voice][sfx]amix=inputs=2:duration=first:normalize=0[a]")

    out = build / "segments" / f"{idx:02d}_{sid}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(f),
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(out)])
    print(f"{sid}: {total:.2f} s -> {out.relative_to(ROOT)}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crop-y", type=int, default=260, help="vertical crop offset of the avatar frame")
    ap.add_argument("--music-db", type=float, default=-26.0)
    ap.add_argument("--only", default="")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg nie je nainštalovaný")
    cfg = json.loads((ROOT / "scenes.json").read_text(encoding="utf-8"))
    build = ROOT / "build"
    statics = make_static_assets(build)
    only = set(filter(None, args.only.split(",")))

    segs, prev = [], None
    for i, scene in enumerate(cfg["scenes"], 1):
        if not only or scene["id"] in only:
            segs.append(build_scene(scene, i, prev, args, build, statics))
        prev = scene["part"]
    if only:
        return

    lst = build / "segments.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in segs))
    joined = build / "joined.mp4"
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])

    out_dir = ROOT / "out"
    out_dir.mkdir(exist_ok=True)
    final = out_dir / "final.mp4"
    music = ROOT / "assets" / "music.mp3"
    if music.exists():
        af = (f"[1:a]volume={args.music_db}dB,aformat=sample_rates=48000:channel_layouts=stereo[m];"
              f"[0:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(joined), "-stream_loop", "-1", "-i", str(music),
             "-filter_complex", af, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(final)])
    else:
        run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(joined), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(final)])
    print(f"hotovo: {final.relative_to(ROOT)} ({probe_duration(final):.1f} s)")


if __name__ == "__main__":
    main()
