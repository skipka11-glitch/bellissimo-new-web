# YouTube video s AI avatarom

Vertikálne video (9:16, ~2 min), ktoré celé odrozpráva AI avatar s klonovaným hlasom: hook → odhalenie, že ide o AI → 1. tri príklady → 2. postup → 3. skutočné náklady a čas → záver. Vizuál a strih sa riadia `STYL.md`.

| súbor | obsah |
|---|---|
| `scenar.md` | čitateľný scenár (generovaný zo `scenes.json`) |
| `scenes.json` | zdroj pravdy: texty, titulky, dosky kapitol |
| `produkcia.md` | kroky v Higgsfield MCP, prompty, rozpočet z preflight cien, čo blokuje |
| `boards/boards.html` + `tools/render_boards.mjs` | grafické dosky kapitol v štýle (Playwright → PNG) |
| `tools/build.py` | zostrih: doska hore, titulok, avatar dole, SFX, loudnorm −14 LUFS |
| `tools/qc.sh` | kontrola finálneho exportu pred odovzdaním |
| `tools/avatar_sadtalker.sh` | pohyb pier zo SadTalkera (obnoviteľný render) |

**Stav:** hotové. `out/final.mp4` (1080×1920, 30 fps, 167,7 s, −14,3 LUFS) prešiel `tools/qc.sh` bez výhrad. Video nie je v gite (53 MB); vznikne znova cez `python3 tools/build.py` z `assets/`. Názov a popis pre YouTube sú v `youtube-popis.md`.
