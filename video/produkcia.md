# produkcia cez Higgsfield MCP

Postup krok za krokom. Každý platený krok má cenu overenú cez `get_cost` (preflight bez míňania kreditov) k 6. 10. 2026.

## 0. predpoklady (stav: blokujú)

| čo | stav | ako vyriešiť |
|---|---|---|
| kredity | **1,95 kr.**, plán `free`, dobitie kreditov pre tento workspace nie je dostupné | PLUS (1 000 kr./mes., 49 USD) stačí s rezervou |
| klon hlasu | nová vzorka: ElevenLabs „Bella – Professional Bright Warm“ (48 s, mono, súvislá reč) – vhodná; **hlas zatiaľ nevytvorený** | widget *Create Voice* → Upload, alebo povoliť `upload.higgsfield.ai` v sieti prostredia. Záloha bez klonovania: prednastavený hlas „Bella“ v Higgsfielde (`eba85120-4ed5-5202-a6f6-696e2c6fe2b6`) |
| fotka avatara | dodaná (9:16, pláž) | rovnaký problém s uploadom: nahrať cez `media_upload_widget` |
| zhoda hlasu a tváre | vyriešené: výška hlasu ≈ 213 Hz (ženský), sedí k avatarovi | – |

## 1. hlas

1. `create_voice` (Upload, súbor ElevenLabs „Bella“) → názov „Bella – AI rozprávačka“ → `voice_id`, `voice_type: "element"`.
2. Počkať, kým `list_voices` ukáže `status=completed`, `is_audio_eligible=true`.
3. **Test slovenčiny** (1 replika, s01): `generate_audio` s `seed_audio` a s `text2speech_v2` + `variant: "elevenlabs"`. Vybrať ten, ktorý vyslovuje slovenčinu prirodzenejšie. 0,6 kr. za repliku.
4. `generate_audio_batch` pre s01 až s10 (text = pole `vo` v `scenes.json`). Uložiť ako `assets/vo/sXX.wav`.

Kapitola 3 (s09) sa generuje **ako posledná**, až keď sú známe skutočné náklady a čas.

## 2. tvár avatara v štýle (teplý interiér)

Referenčná fotka je z pláže, `STYL.md` chce teplý domáci interiér. `generate_image`, model `gpt_image_2_5`, referencia = nahratá fotka, `aspect_ratio: "9:16"`, `count: 4`:

> Same woman as in the reference photo: identical face, freckles, green eyes, eyebrows and gold hoop earrings. She sits in a bright, cozy living room in cream and beige tones, warm soft window daylight, shallow depth of field with a softly blurred background. Cream knit top, burgundy nail polish. She looks straight into the camera with a calm, friendly expression, lips relaxed and closed. Chest-up framing, head in the upper third of the frame, natural unretouched skin texture. No text, no logos.

Vybrať 1 snímku. Hlavu treba mať vyššie, pretože build orezáva spodných 60 % (`--crop-y`).

## 3. avatar s pohybom pier

Model `wan2_7` (obrázok + zvuk → video so synchronizovaným zvukom), 720p, 9:16. Pre každú scénu: `start_image` = vybraná snímka, `audio_references` = hlas sXX, `duration` = dĺžka repliky zaokrúhlená nahor (max. 15 s).

> The woman speaks calmly and warmly to the camera, lips precisely synced to the audio, natural blinking and subtle head movement, relaxed shoulders, static camera, warm interior light.

Výstupy uložiť ako `assets/avatar/sXX.mp4`. Ak by sa model odklonil od tváre, fallback je `seedance_2_5` s režimom `omni_reference` (drahší).

## 4. tri príklady

| # | čo | model | prompt / postup | výstup |
|---|---|---|---|---|
| 1 | reklama pre reštauráciu Bellissimo | `kling3_0`, 5 s, 16:9, 2 zábery | *Slow push-in on a plate of fresh tagliatelle with basil being set on a rustic wooden table in a warm Italian trattoria, golden evening light, gentle steam, shallow depth of field, cinematic, no text.* + druhý záber: *Close-up of olive oil drizzled over burrata and tomatoes, warm light, slow motion.* | `assets/media/ex1.mp4` (2 zábery zlepené) |
| 2 | jedna tvár, všade | `gpt_image_2_5` s referenciou, 2 snímky (kaviareň, kancelária) + pôvodná fotka z pláže | prompt z kroku 2, iba vymeniť prostredie | `assets/media/ex2.mp4`: 3 snímky × 2 s, jemné prelínanie (ffmpeg, zadarmo) |
| 3 | jedno video, tri jazyky | `dubbing` z hotového klipu s01 | `target_language: "eng"` a `"ita"` | `assets/media/ex3_en.mp4`, `ex3_it.mp4` |

Zlepenie príkladov 1 a 2 (zadarmo, ffmpeg):

```bash
# príklad 1: dva 5 s zábery s prelínaním
ffmpeg -i shot1.mp4 -i shot2.mp4 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.5:offset=4.5,format=yuv420p" -an assets/media/ex1.mp4
# príklad 2: tri snímky po 2 s s prelínaním
ffmpeg -loop 1 -t 2.5 -i plaz.jpg -loop 1 -t 2.5 -i kaviaren.png -loop 1 -t 2.5 -i kancelaria.png -filter_complex \
 "[0:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1[a];[1:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1[b];[2:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1[c];[a][b]xfade=duration=0.5:offset=2[ab];[ab][c]xfade=duration=0.5:offset=4,format=yuv420p" -r 30 assets/media/ex2.mp4
```

## 5. strih a export

```bash
cd video
npm install                          # playwright (na vykreslenie dosiek)
npm run boards                       # dosky kapitol → build/boards/*.png
python3 tools/build.py --crop-y 260  # zostrih → out/final.mp4
tools/qc.sh out/final.mp4            # kontrola exportu
```

Pri prázdnych `{{…}}` sa dosky vykreslia s viditeľnými zástupnými znakmi. Pred finálnym exportom vytvoriť `values.json` (vzor nižšie) a spustiť `node tools/render_boards.mjs values.json`.

```json
{ "EUR": "…", "CAS": "…", "KR_HLAS": "…", "KR_AVATAR": "…", "KR_PRIKLADY": "…", "KR_OPRAVY": "…" }
```

`qc.sh` kontroluje: 1080×1920, h264/yuv420p, 30 fps, AAC 48 kHz, zhodu dĺžky audia a videa, −14 LUFS ±2, true peak ≤ −1 dBTP, ticho > 1,5 s, čierne zábery, zamrznutie avatara (> 2,5 s) a vytvorí kontaktný hárok na vizuálnu kontrolu. Odovzdáva sa až vtedy, keď skončí s „export je pripravený“ a kontaktný hárok je skontrolovaný očami.

## 6. rozpočet (preflight ceny, nie skutočné náklady)

| položka | jednotková cena | množstvo | kredity |
|---|---|---|---|
| hlas – repliky (`seed_audio`) | 0,6 kr./replika | 10 + 2 testy | 7,2 |
| klon hlasu | neoverené (účtuje sa po vytvorení) | 1 | ? |
| snímky avatara (`gpt_image_2_5`) | 0,25 kr. | 4 + 2 | 1,5 |
| avatar (`wan2_7`, 720p) | 22,5 kr./15 s ≈ 1,5 kr./s | ≈ 115 s | ≈ 173 |
| príklad 1 (`kling3_0`, 5 s) | 8,75 kr. | 2 | 17,5 |
| príklad 3 (`dubbing`) | neoverené | 2 | ? |
| rezerva na opakovania (25 %) | | | ≈ 50 |
| **spolu** | | | **≈ 250 kr. + klon + dubbing** |

Pri pláne PLUS (49 USD / 1 000 kr.) to vychádza na **≈ 12–15 USD**. Pri 1080p (`wan2_7` 37,5 kr./15 s) narastie avatar na ≈ 290 kr. a celok na ≈ 20 USD. Odhad času: 2,5–4 h, z toho väčšina je čakanie na generovanie.

Do videa idú **iba skutočné čísla** z `transactions` a nameraný čas, nie tento odhad.

## 7. pri nahrávaní na YouTube

- V YouTube Studio zaškrtnúť **„Altered or synthetic content“ (upravený alebo syntetický obsah)**, pretože video má realistickú AI osobu a klonovaný hlas.
- Do popisu dať zoznam nástrojov: Higgsfield (wan2_7, seed_audio, gpt_image_2_5, kling3_0, dubbing) + ffmpeg.
- Štítok „ai avatar · ai hlas“ je vo videu viditeľný počas celej dĺžky.
