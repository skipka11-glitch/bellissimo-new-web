#!/usr/bin/env node
// Renders index.html frame by frame in headless Chromium and encodes the MP4.
//   node render.cjs                      → out/gls-koncept-15s.mp4 (needs audio/soundtrack.wav, run sound.py first)
//   node render.cjs --stills 0.5,2.6,7.9 → out/stills/*.png at those seconds (add --safe for the 9:16 guide)
//   node render.cjs --sheet              → out/stills/sheet-*.png, every 6th frame, for frame-by-frame review
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const OUT = path.join(ROOT, 'out');
const FPS = 30, FRAMES = 450;
const args = process.argv.slice(2);
const flag = n => args.includes(n);
const val = n => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };

(async () => {
  fs.mkdirSync(path.join(OUT, 'stills'), { recursive: true });
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => { console.error('page error:', e.message); process.exitCode = 1; });
  await page.goto('file://' + path.join(ROOT, 'index.html') + '?render=1');
  await page.waitForFunction('window.__ready === true');
  const frame = (f, o = {}) => page.evaluate(([f, o]) => window.renderFrame(f, o), [f, o]);

  if (val('--stills') || flag('--sheet')) {
    const list = flag('--sheet')
      ? Array.from({ length: FRAMES / 6 }, (_, i) => i * 6)
      : val('--stills').split(',').map(s => Math.round(parseFloat(s) * FPS));
    for (const f of list) {
      const png = await frame(Math.min(FRAMES - 1, f), { safe: flag('--safe') });
      const name = (flag('--sheet') ? 'sheet-' : 'still-') + String(f).padStart(3, '0') + '.png';
      fs.writeFileSync(path.join(OUT, 'stills', name), Buffer.from(png, 'base64'));
    }
    console.log(`wrote ${list.length} stills to out/stills`);
    await browser.close();
    return;
  }

  const audio = path.join(ROOT, 'audio', 'soundtrack.wav');
  const mp4 = path.join(OUT, 'gls-koncept-15s.mp4');
  const ff = spawn('ffmpeg', [
    '-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-i', audio,
    '-map', '0:v', '-map', '1:a',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
    '-r', String(FPS), '-c:a', 'aac', '-b:a', '256k', '-t', '15', '-movflags', '+faststart', mp4,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = 0; f < FRAMES; f++) {
    const png = Buffer.from(await frame(f), 'base64');
    if (!ff.stdin.write(png)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 30 === 0) process.stdout.write(`\rframe ${f}/${FRAMES}  ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))));
  console.log(`\nwrote ${path.relative(ROOT, mp4)}`);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
