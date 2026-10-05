# Môj štýl – vizuálny štýl a štýl strihu

Tento dokument popisuje môj vizuálny jazyk: typografiu, farby, prvky rozhrania, zvuk a pohyb. Slúži ako referencia pre web, sociálne siete, videá (Reels/TikTok) aj pre zadanie práce AI nástrojom alebo strihačovi.

> **V jednej vete:** elegantný, ženský a editoriálny minimalizmus. Pudrovo ružové pozadie, hlboká bordová, klasický pätkový font kombinovaný s ručne pôsobiacou kurzívou a jemné, „mäkké“ karty so zaoblenými rohmi.

---

## 1. Celkový dojem a nálada

- **Elegancia a pokoj:** veľa voľného priestoru, nič nekričí, žiadne neónové ani syté „tech“ farby.
- **Editoriálny / magazínový dojem:** typografia pripomína módny časopis. Klasický serif doplnený výraznou kurzívou.
- **Teplo a ženskosť:** teplé tóny bordovej, terakoty a pudrovej ružovej.
- **Prémiovosť bez okázalosti:** jemné tiene, zaoblené tvary, konzistentná paleta.
- **Kľúčové slová:** *clean, soft, editorial, burgundy, blush, feminine, premium, calm.*

---

## 2. Typografia

| Úloha | Font | Použitie |
|---|---|---|
| Hlavný serif | **Times New Roman** (alternatíva: *Times*, *Libre Caslon*, *EB Garamond*) | Bežný text titulkov, vety v strede obrazovky, kratšie odseky |
| Akcentová kurzíva | **PP Migra Italic** (alternatíva zdarma: *Playfair Display Italic*, *Instrument Serif Italic*, *Cormorant Italic*) | Nadpisy („tvůj styl“), zvýraznené slová vo vete, čísla v odznakoch |
| Bezpätkový font | **PP Frama** (alternatíva zdarma: *Inter*, *Manrope*, *DM Sans*) | Popisky v UI, tlačidlá („play“), drobné informácie |

### Pravidlá typografie

- **Kombinovanie v jednej vete:** bežný text v serife, kľúčové slovo/slovné spojenie v kurzíve a v **bordovej farbe**.
  - Príklad: „je najít svůj *styl střihu*“ – „styl střihu“ je kurzíva PP Migra Italic, bordová.
- **Nadpisy sekcií:** malé písmená, kurzíva, tmavá farba, mierne zúžené medzery medzi písmenami (tracking −1 až −2 %).
- **Číslovanie:** číslo v kurzíve so bodkou („1.“) vo vnútri bordovej pilulky, biely text.
- **Veľkosti:** nadpis výrazne väčší ako text vety; titulky stredne veľké, nikdy nie obrovské.
- **Zarovnanie:** na stred.
- **Vždy malé písmená** v nadpisoch a titulkoch (okrem názvov fontov a vlastných mien).
- Nepoužívať: hrubé (bold) bezpätkové nadpisy, VERZÁLKY, obrysy (outline) a tiene na texte.

---

## 3. Farebná paleta

Zo štyroch bodiek na „paletovej“ karte (zľava doprava) + farby pozadia:

| Názov | HEX (približne) | Použitie |
|---|---|---|
| **Bordová (primárna)** | `#6B0F12` | Odznaky s číslom, tlačidlá, zvýraznené slová, ikony, waveform |
| **Tmavá čokoládovo-bordová** | `#3B0A0C` | Hlavný text, nadpisy, kontrastné prvky |
| **Terakota / staroružová** | `#C9705F` | Doplnkový akcent, sekundárne prvky, dekor |
| **Svetlá pudrová sivá** | `#E6DCDA` | Neaktívne stavy (vypnutý prepínač), oddeľovače |
| **Pozadie – pudrová ružová** | `#F7ECEA` | Hlavné pozadie scény / stránky |
| **Karty – teplá biela** | `#FFFBFA` | Pozadie kariet a panelov |
| **Text** | `#1F1414` | Takmer čierna s teplým podtónom pre dlhší text |

### Pravidlá farieb

- Pomer zhruba **70 % pozadie (pudrová/biela) – 20 % tmavý text – 10 % bordová akcent**.
- Bordová je „podpis“ – používaj ju striedmo, na to, čo má upútať pozornosť.
- Žiadne studené farby (modrá, zelená, fialová) ani čistá čierna `#000` či čistá biela `#FFF` na veľkých plochách.
- Prechod medzi grafickou časťou a videom: jemný gradient z pudrovej ružovej do záberu (fade, nie ostrá hrana).

### CSS premenné

```css
:root {
  --burgundy:      #6B0F12;
  --burgundy-dark: #3B0A0C;
  --terracotta:    #C9705F;
  --blush-grey:    #E6DCDA;
  --bg-blush:      #F7ECEA;
  --card:          #FFFBFA;
  --text:          #1F1414;

  --font-serif:  "Times New Roman", Times, "Libre Caslon Text", serif;
  --font-italic: "PP Migra", "Playfair Display", "Instrument Serif", serif; /* italic */
  --font-sans:   "PP Frama", "Inter", "DM Sans", system-ui, sans-serif;

  --radius-card: 16px;
  --radius-pill: 999px;
  --shadow-soft: 0 6px 18px rgba(59, 10, 12, 0.08);
}
```

---

## 4. Prvky rozhrania (UI komponenty)

Na obrazovke „tvůj styl“ je šesť kariet, ktoré definujú stavebné kamene štýlu:

1. **Typografia – „Aa *Aa*“:** ukážka kombinácie serifu a kurzívy.
2. **Paleta – 4 bodky:** bordová, tmavá bordová, terakota, svetlá pudrová.
3. **Textový box / karta:** obdĺžnik s tenkým bordovým obrysom a zaoblenými rohmi, vnútri sivé linky ako placeholder textu.
4. **Prepínač (toggle):** dve pilulky – svetlá sivá (vypnuté) a bordová (zapnuté).
5. **Zvuková vlna (waveform):** vertikálne bordové čiarky rôznej výšky – symbol zvukových efektov.
6. **Tlačidlo „play“:** bordová pilulka, biely text malými písmenami, bezpätkový font.

### Karty

- Pozadie teplá biela, **zaoblenie ~16 px**, **veľmi jemný mäkký tieň** (nie tvrdý okraj).
- Rozmiestnenie v **mriežke 3 × 2**, rovnaké medzery medzi kartami.
- Obsah karty vycentrovaný, veľa vnútorného priestoru (padding).

### Odznak s číslom

- Bordová pilulka/ovál, vnútri biele číslo v kurzíve („1.“).
- Umiestnený **nad nadpisom** kapitoly, centrovaný.

### Checklist

- Ikona: **plný bordový kruh s bielou fajkou**.
- Vedľa text – každá položka vo „svojom“ fonte (napr. *Times New Roman* v serife, *PP Migra Italic* v kurzíve, *PP Frama* v bezpätkovom fonte), aby položka zároveň slúžila ako ukážka.

### Tlačidlá

- Tvar pilulky, plná bordová, biely text, malé písmená.
- Sekundárne tlačidlo: svetlá pudrová sivá výplň alebo tenký bordový obrys.

### Ikony

- Tenké linky (outline), bordová farba, zaoblené konce čiar (napr. ikona reproduktora).

---

## 5. Štýl strihu videa (Reels / TikTok)

### Kompozícia obrazovky

- **Horná polovica (~40 %):** grafická „doska“ na pudrovom pozadí – odznak s číslom, nadpis v kurzíve, karty.
- **Stred:** titulok (jedna krátka veta) na pudrovom pozadí, tesne nad videom.
- **Spodná polovica (~60 %):** záber hovoriacej osoby (talking head) v teplom, domácom interiéri.
- Prechod medzi grafikou a videom je **mäkký gradient**, nie ostrá čiara.

### Štruktúra obsahu

- Video je rozdelené do **očíslovaných kapitol** („1. tvůj styl“, „2. …“, „3. …“).
- Každá kapitola má vlastný nadpis v kurzíve a vizuálnu „dosku“ s kartami.
- Karty sa počas hovoreného textu **menia/dopĺňajú** podľa toho, o čom sa práve hovorí (napr. zo 6 ikon sa prejde na checklist fontov a kartu „efekty“).

### Titulky

- Krátke, 3–6 slov na obrazovke naraz.
- Serif + kurzívou a bordovou zvýraznené kľúčové slovo.
- Umiestnené na stred, nad tvárou – nikdy nezakrývajú tvár.
- Bez pozadia (boxu) a bez obrysov, iba čistý text na pudrovom pozadí.

### Animácie a pohyb

- **Jemné a krátke:** fade-in, mierny posun zdola (slide up 8–16 px), jemné „pop“ zväčšenie z 95 % na 100 %.
- Karty sa objavujú **postupne** (stagger ~80–120 ms).
- Žiadne trhané zoomy, glitch efekty, rotácie či rýchle blikanie.
- Ľahké easingy (ease-out / ease-in-out), trvanie 200–400 ms.

### Zvuk

- **Zvukové efekty (SFX):** jemné „pop“, „click“, „swoosh“ pri objavení kariet a prepnutí kapitoly.
- Waveform ako vizuálny symbol zvuku v bordovej farbe.
- Hlas je hlavný – hudba v pozadí tichá a pokojná.
- Čistý zvuk z klopového/bezdrôtového mikrofónu.

### Obraz (kamera, svetlo, farby)

- Teplé, mäkké denné svetlo, rozmazané pozadie (malá hĺbka ostrosti).
- Svetlý, útulný interiér v béžových a krémových tónoch.
- Color grading: teplé, mierne zjemnené farby, jemný kontrast, pleťové tóny prirodzené.
- Oblečenie a doplnky ladia s paletou (krémová/biela, bordová – napr. bordové nechty).

---

## 6. Recept – ako „nájsť svoj štýl strihu“

Podľa kapitoly *1. tvůj styl* – nazbieraj si vlastnú knižnicu:

1. **Fonty** – 1 serif, 1 kurzíva na akcenty, 1 bezpätkový na UI.
2. **Farby** – 1 hlavná akcentová, 1 tmavá na text, 1 doplnková, 1–2 neutrálne svetlé.
3. **Grafické prvky** – karty, tlačidlá, prepínače, odznaky, ikony v jednotnom štýle.
4. **Zvukové efekty** – malá sada (pop, click, swoosh), vždy tie isté.
5. **Animácie** – 2–3 typy prechodov, používať konzistentne.

Potom všetko používaj **opakovane a konzistentne**, aby bol štýl rozpoznateľný na prvý pohľad.

---

## 7. Čo do štýlu nepatrí (Don'ts)

- Neónové, studené alebo príliš syté farby.
- Veľa rôznych fontov naraz (max. 3).
- VERZÁLKY, hrubé bezpätkové nadpisy, outline a drop-shadow na texte.
- Ostré rohy, tvrdé čierne okraje, výrazné tiene.
- Rýchly, agresívny strih, glitch a „memečkové“ efekty.
- Preplnená obrazovka – vždy ponechať voľný priestor.

---

## 8. Krátky prompt pre AI / strihača

> Strihaj v elegantnom editoriálnom štýle: pudrovo ružové pozadie `#F7ECEA`, akcentová bordová `#6B0F12`, tmavý text `#3B0A0C`, doplnková terakota `#C9705F`. Fonty: Times New Roman pre text, PP Migra Italic pre nadpisy a zvýraznené slová (v bordovej), PP Frama pre UI. Horná časť obrazovky = grafická doska s očíslovanou kapitolou (bordová pilulka s číslom v kurzíve), nadpisom malými písmenami a bielymi kartami so zaoblenými rohmi a jemným tieňom. Spodná časť = talking head v teplom interiéri, prechod mäkkým gradientom. Titulky krátke, na stred, bez boxu, kľúčové slovo v kurzíve. Animácie jemné (fade, slide-up, malý pop), zvukové efekty pop/click/swoosh. Žiadne glitch efekty, verzálky ani syté farby.
