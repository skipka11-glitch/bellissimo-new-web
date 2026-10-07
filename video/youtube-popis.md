# YouTube – názov a popis

**Názov:** toto video nemá kameru (a rozpráva ho AI)

**Popis:**

Celé toto video odrozprávala AI. Tvár je jedna fotka, pohyb pier vytvoril open-source model SadTalker a hlas je syntetický.

V kapitole 1 sú tri príklady: reklama pre taliansku reštauráciu Bellissimo v Nitre, odpoveď na otázku zákazníka a ten istý úvod po anglicky a taliansky. V kapitole 2 je postup v piatich krokoch a v kapitole 3 skutočné náklady a čas.

Nástroje:
- hlas: Bella – Professional, Bright, Warm (ElevenLabs) cez vidIQ, 84 kreditov
- pohyb pier: SadTalker (open source, Apache-2.0), render na CPU
- grafika: HTML + Playwright, fonty Playfair Display, Libre Caslon Text, Inter
- strih a kontrola exportu: ffmpeg

Pri nahrávaní v YouTube Studio zaškrtni „Altered or synthetic content“.
