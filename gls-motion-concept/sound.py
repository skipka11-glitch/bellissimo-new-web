#!/usr/bin/env python3
"""Original sound design for the 15 s GLS concept, synthesised from scratch (numpy only).

    python3 sound.py  ->  audio/soundtrack.wav  (48 kHz, stereo, 16-bit, exactly 15.0 s)

Cue times mirror the beats in index.html (T = {...} and the per-scene timings).
Structure: soft opening pulse -> tight transition hits -> rising momentum -> resolve on the logo.
"""
import os
import wave
import numpy as np

SR = 48000
DUR = 15.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def place(sig, at, gain=1.0, pan=0.0):
    """Add a mono signal at time `at` (s) with constant-power pan (-1..1)."""
    i = int(at * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    a = (pan + 1) * np.pi / 4
    L[i:i + len(sig)] += sig * np.cos(a)
    R[i:i + len(sig)] += sig * np.sin(a)


def onepole_lp(x, fc):
    """One-pole low-pass; fc may be a scalar or an array (time-varying)."""
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def svf_bp(x, fc, q=1.2):
    """Chamberlin state-variable band-pass with time-varying centre."""
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape)
    f = 2 * np.sin(np.pi * np.minimum(fc, SR / 6) / SR)
    lo = bp = 0.0
    y = np.empty_like(x)
    for i in range(len(x)):
        hp = x[i] - lo - bp / q
        bp += f[i] * hp
        lo += f[i] * bp
        y[i] = bp
    return y


def env(d, a=0.005, r=None, curve=6.0):
    t = t_axis(d)
    e = np.minimum(1, t / max(a, 1e-4))
    return e * np.exp(-curve * t / (r or d))


# ── instruments ──────────────────────────────────────────────────────────
def pulse(amp=1.0, d=0.45):            # soft sub kick: pitch-dropping sine, no click
    t = t_axis(d)
    f = 48 + 70 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(d, 0.004, d, 7) * amp


def tick(freq=2600, d=0.05):           # UI tick
    t = t_axis(d)
    return np.sin(2 * np.pi * freq * t) * env(d, 0.001, d, 9)


def hat(d=0.06):
    n = rng.standard_normal(int(d * SR))
    n = n - onepole_lp(n, 6000)
    return n * env(d, 0.001, d, 10)


def whoosh(d, f0, f1, q=0.9):
    t = t_axis(d)
    n = rng.standard_normal(len(t))
    fc = f0 * (f1 / f0) ** (t / d)
    shape = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.6
    return svf_bp(n, fc, q) * shape


def hit(d=0.5):                        # transition hit: thump + short bright noise
    out = pulse(1.0, d) * 0.9
    n = whoosh(0.09, 3000, 1200, 1.4) * np.exp(-t_axis(0.09) * 20)
    out[:len(n)] += 0.5 * n
    return out


def beep(freqs=(1880, 2350), d=0.16):  # scanner confirmation, two short tones
    out = np.zeros(int(d * SR))
    seg = int(d * SR / len(freqs))
    for k, f in enumerate(freqs):
        t = t_axis(seg / SR)
        out[k * seg:(k + 1) * seg] = np.sin(2 * np.pi * f * t) * env(seg / SR, 0.002, seg / SR, 3)
    return out


def pop(f0=900, f1=520, d=0.09):
    t = t_axis(d)
    f = f1 + (f0 - f1) * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.001, d, 7)


def bell(freq, d=1.4, bright=1.0):
    t = t_axis(d)
    partials = [(1, 1.0), (2.0, 0.35 * bright), (2.76, 0.22 * bright), (5.4, 0.08 * bright)]
    s = sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-t * (2.2 + m * 1.3)) for m, a in partials)
    return s * np.minimum(1, t / 0.003)


def pad(freqs, d, cutoff, detune=0.004):
    """Soft saw pad from additive partials; `cutoff` is (start, end) brightness in Hz."""
    t = t_axis(d)
    fc = np.linspace(cutoff[0], cutoff[1], len(t))
    out = np.zeros(len(t))
    for f in freqs:
        for dt in (-detune, detune):
            f0 = f * (1 + dt)
            for k in range(1, 14):
                fk = f0 * k
                if fk > 9000:
                    break
                g = (1 / k) / np.sqrt(1 + (fk / fc) ** 4)   # 2-pole-ish roll-off that opens over time
                out += g * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28))
    a = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.25)
    return out * a / (len(freqs) * 2)


def hz(note):                          # 'D4' -> Hz
    names = {'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'G#': -1, 'A': 0, 'A#': 1, 'B': 2}
    n, o = note[:-1], int(note[-1])
    return 440 * 2 ** ((names[n] + 12 * (o - 4)) / 12)


# ── arrangement ──────────────────────────────────────────────────────────
# Pad: B minor colour under the story, opening up; resolves to D major on the logo.
place(pad([hz('B2'), hz('F#3'), hz('A3'), hz('D4')], 6.6, (250, 900)), 0.0, 0.16)
place(pad([hz('G2'), hz('D3'), hz('F#3'), hz('B3')], 5.1, (900, 2400)), 6.4, 0.17)
place(pad([hz('D2'), hz('A2'), hz('F#3'), hz('C#4'), hz('E4')], 3.2, (2600, 1200)), 12.38, 0.22)

# Pulse: sparse at the open, then every half-beat (120 bpm) with rising energy.
beats = [0.0, 1.0] + list(np.arange(2.0, 11.5, 0.5))
for b in beats:
    place(pulse(0.35 + 0.45 * min(1, b / 11.0)), b, 0.8)
for b in np.arange(4.25, 11.5, 0.5):                   # off-beat hats from the tracking scene on
    place(hat(), b, 0.05 + 0.05 * (b - 4) / 7.5, pan=0.3)
for b in np.arange(9.0, 11.4, 0.25):                   # 16th shimmer as time tightens
    place(hat(0.035), b, 0.035, pan=-0.3)

# Hook
place(whoosh(0.75, 300, 5000, 1.1), 0.5, 0.22, pan=0.4)    # line shoots across the country
place(tick(1760, 0.12), 1.3, 0.12, pan=0.6)                # ping at Košice
# Pickup
place(whoosh(0.4, 4000, 400), 1.95, 0.25)                  # push back into Bratislava
place(hit(), 2.0, 0.55)
place(whoosh(0.3, 1500, 3500, 2.5), 2.08, 0.10, pan=-0.2)  # tape zip
place(beep(), 2.64, 0.13)                                  # scan OK
place(whoosh(0.3, 600, 200), 2.76, 0.18, pan=0.5)          # van reverses in
place(pulse(0.5, 0.25), 3.05, 0.5)                         # van stops
place(pop(500, 260, 0.12), 3.35, 0.35)                     # parcel loaded, door shut
place(whoosh(0.6, 250, 2200), 3.45, 0.2, pan=0.4)          # drive off
# Tracking
place(hit(), 4.0, 0.55)
place(tick(), 4.3, 0.18)                                   # step 1 ticked
place(tick(), 4.915, 0.18)                                 # step 2 ticked (Na ceste)
for i, f in enumerate([4.305, 4.84, 5.415, 6.405]):        # route reaches Nitra, B. Bystrica, Poprad, Košice
    place(tick(1400 + 120 * i, 0.04), f, 0.06, pan=-0.2 + 0.15 * i)
# Flexibility
place(whoosh(0.45, 3500, 500), 6.4, 0.2)
place(hit(0.4), 6.5, 0.45)
for i, f in enumerate([7.12, 7.21, 7.30]):                 # three options pop in
    place(pop(880 + 140 * i, 520 + 80 * i), f, 0.3, pan=(i - 1) * 0.5)
place(pop(1300, 700, 0.06), 7.86, 0.4, pan=0.4)            # tap
place(tick(2100, 0.08), 7.88, 0.12, pan=0.4)
place(whoosh(0.5, 500, 1800, 1.5), 7.98, 0.12, pan=0.3)    # parcel rides to the locker
place(pop(700, 400, 0.08), 8.55, 0.3, pan=0.4)             # into the cell
# Reliability
place(whoosh(0.5, 300, 3000), 8.8, 0.2)
place(hit(0.35), 9.0, 0.4)
place(pop(1600, 900, 0.05), 9.42, 0.45)                # window snaps into place
place(pulse(0.7, 0.2), 9.42, 0.4)
place(whoosh(1.0, 400, 1600, 1.3), 9.55, 0.1)              # parcel travels the timeline
place(bell(hz('A5'), 1.2), 10.55, 0.22)                    # lands right on the mark
place(bell(hz('D6'), 1.0, 0.6), 10.6, 0.12, pan=0.3)
# Reveal: riser into the resolve
riser_d = 1.0
rt = t_axis(riser_d)
riser = whoosh(riser_d, 200, 7000, 1.6) * (rt / riser_d) ** 2
riser += 0.15 * np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2 * rt / riser_d)) / SR) * (rt / riser_d) ** 2
place(riser, 11.32, 0.4)
place(whoosh(0.5, 6000, 300), 11.6, 0.25)                  # blue fills the frame
place(pulse(1.0, 1.4), 12.38, 1.0)                         # resolve
for i, n in enumerate(['D5', 'F#5', 'A5', 'E6']):
    place(bell(hz(n), 2.4, 0.7), 12.38 + i * 0.03, 0.12, pan=(i - 1.5) * 0.35)
place(tick(3200, 0.05), 12.95, 0.05)                       # credit appears

# ── space + master ──────────────────────────────────────────────────────
def reverb(x, seconds=1.8, seed=3):
    r = np.random.default_rng(seed)
    ir_t = t_axis(seconds)
    ir = r.standard_normal(len(ir_t)) * np.exp(-ir_t * 4.0)
    ir = onepole_lp(ir, 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(x) + len(ir)
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]
    return y

wetL, wetR = reverb(L, seed=3), reverb(R, seed=4)
L = L + 0.22 * wetL
R = R + 0.22 * wetR
# gentle high-pass to keep the low end clean
L = L - onepole_lp(L, 28)
R = R - onepole_lp(R, 28)
mix = np.stack([L, R], axis=1)
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.3) / np.tanh(1.3)              # soft glue
fade = np.ones(N)
fade[-int(0.35 * SR):] = np.linspace(1, 0, int(0.35 * SR)) ** 1.5
mix *= fade[:, None] * 10 ** (-1.0 / 20)             # peak at -1 dBFS

os.makedirs(os.path.join(os.path.dirname(__file__) or '.', 'audio'), exist_ok=True)
out_path = os.path.join(os.path.dirname(__file__) or '.', 'audio', 'soundtrack.wav')
with wave.open(out_path, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out_path)
