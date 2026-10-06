// Renders one 1080x768 PNG "board" per scene from boards/boards.html.
// Usage: node tools/render_boards.mjs [values.json]
//   values.json fills {{PLACEHOLDERS}} (costs/time) once production numbers are known.
import { chromium } from "playwright";
import { readFileSync, mkdirSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const cfg = JSON.parse(readFileSync(resolve(root, "scenes.json"), "utf8"));
const valuesPath = process.argv[2];
const values = valuesPath && existsSync(valuesPath) ? JSON.parse(readFileSync(valuesPath, "utf8")) : {};
const outDir = resolve(root, "build/boards");
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1080, height: cfg.format.board_height } });
await page.goto(pathToFileURL(resolve(root, "boards/boards.html")).href);
await page.evaluate(() => document.fonts.ready);

for (const scene of cfg.scenes) {
  await page.evaluate(([s, d, v]) => window.renderBoard(s, d, v), [scene, cfg.disclosure, values]);
  await page.evaluate(() => document.fonts.ready);
  const file = resolve(outDir, `${scene.id}.png`);
  await page.screenshot({ path: file });
  console.log("board", file);
}
await browser.close();
