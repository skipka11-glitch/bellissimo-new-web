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

Pipeline je overený naprázdno (statická fotka + zástupný zvuk). Výstup 1080×1920 mal 113,8 s a prešiel `qc.sh`. Skutočná produkcia čaká na kredity a vytvorenie klonu hlasu, pozri `produkcia.md`, sekcia 0.
