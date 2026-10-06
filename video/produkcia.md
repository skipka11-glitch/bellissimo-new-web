# produkcia (bez Higgsfieldu)

| krok | nástroj | stav |
|---|---|---|
| hlas | vidIQ MCP `vidiq_voiceover_generate`, hlas **Bella – Professional, Bright, Warm** (ElevenLabs, `hpp4J3VqNfWAUOO0d1Us`), ten istý hlas ako v dodanej vzorke | hotové |
| tvár | dodaná fotka (9:16) | hotové |
| pohyb pier | [SadTalker](https://github.com/OpenTalker/SadTalker) (open source, Apache-2.0), lokálne na CPU, `--still --preprocess full --enhancer gfpgan` | `tools/avatar_sadtalker.sh` |
| grafika | `boards/boards.html` → `tools/render_boards.mjs` (Playwright) | hotové |
| strih | `tools/build.py` (ffmpeg) | |
| kontrola exportu | `tools/qc.sh` | |

> Hlas **nie je klon** dodanej nahrávky. Je to ten istý syntetický hlas z knižnice ElevenLabs, z ktorého vzorka pochádza (podľa názvu súboru). Scenár to tak aj hovorí („hlas, ktorý počuješ, je syntetický“).

## 1. hlas

Celý scenár sa generuje jedným volaním (zachová sa rovnaká intonácia, platí sa za znaky). Na scény sa delí podľa páuz medzi odsekmi: hranice sa hľadajú tak, aby tempo reči (znaky/s) bolo v každej scéne rovnaké. Výsledok sa zhodoval s dlhými pauzami (0,8 – 1,1 s), tempo vyšlo 15 – 17 znakov/s.

| volanie | obsah | znakov | kredity vidIQ |
|---|---|---|---|
| 1 | prvá verzia celého scenára (bez s09) | 1 327 | 28 |
| 2 | opravené repliky s02, s04, s05, s07 + texty ukážok 1 a 2 | 953 | 14 |
| 3 | ukážka 3: úvod po anglicky a taliansky | 232 | 14 |
| 4 | s09 (náklady), až keď sú známe čísla | | 14 |

Prvá verzia mala vety o klonovaní z 20 s nahrávky, ktoré po prechode na hotový hlas Bella neboli pravdivé. Preto volanie 2.

## 2. avatar

```bash
SADTALKER=/cesta/SadTalker PY=/cesta/venv/bin/python tools/avatar_sadtalker.sh tvar.jpg
```

Váhy modelov sa sťahujú z GitHub releases (`scripts/download_models.sh` v repozitári SadTalker). Na Pythone 3.13 / NumPy 2 treba drobné úpravy (`np.float` → `float` v `src/face3d/util/my_awing_arch.py`, `np.VisibleDeprecationWarning` v `src/face3d/util/preprocess.py`).

## 3. tri príklady (všetky vyrobené tým istým postupom)

1. **reklama pre reštauráciu Bellissimo**: text z ich webu (tagliatelle al tartufo 18,90 €, OC MAX Nitra).
2. **odpoveď zákazníkovi**: „Dá sa u vás rezervovať stôl?“, odpoveď podľa `rezervacia.html` a `kontakt.html`.
3. **iný jazyk**: úvod videa po anglicky a taliansky (preklad, hlas Bella, nový pohyb pier zo SadTalkera).

## 4. strih a export

```bash
cd video
npm install && npm run boards
python3 tools/build.py --crop-y 260
tools/qc.sh out/final.mp4
```

## 5. pri nahrávaní na YouTube

- V YouTube Studio zaškrtnúť **„Altered or synthetic content“**.
- Do popisu: hlas Bella (ElevenLabs cez vidIQ), animácia SadTalker (open source), grafika a strih ffmpeg + Playwright. Overiť, či licencia ElevenLabs/vidIQ pokrýva komerčné použitie hlasu.
- Štítok „ai avatar · syntetický hlas“ je vo videu viditeľný celý čas.
