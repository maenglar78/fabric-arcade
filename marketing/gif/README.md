# GIF arcade anni '80 — istruzioni

`arcade-intro.html` è l'animazione stile CRT/arcade da usare come media del **post di lancio**.
Fa scorrere: titolo **FABRIC ARCADE**, parole chiave (POWER BI, REAL-TIME, WAREHOUSE, PIPELINES, KQL, DATA SCIENCE, DAX, LAKEHOUSE), una marquee di messaggi e la CTA "INSERT COIN".

**Loop completo: 12 secondi** (registra 12s per un loop perfetto).
Stage: 800×800 px (quadrato, ideale per il feed LinkedIn). Per un'anteprima link usa 1200×630.

---

## Anteprima
Apri il file nel browser (doppio click) oppure con Live Server in VS Code.

## Opzione A — ScreenToGif (Windows, la più semplice)
1. Scarica ScreenToGif: https://www.screentogif.com/
2. Apri `arcade-intro.html` nel browser a tutto schermo.
3. In ScreenToGif → *Recorder*, inquadra il riquadro 800×800.
4. Registra **12 secondi**, poi *File → Save as → GIF* (o MP4).
5. Per LinkedIn: un MP4 è spesso più fluido e leggero di una GIF grande.

## Opzione B — ffmpeg + screenshot headless (riproducibile)
Richiede Node + Playwright (già disponibile in questo workspace) e ffmpeg.

```powershell
# 1) cattura 120 frame a 10 fps per 12s (script di esempio da adattare)
#    usa un piccolo script Playwright che fa screenshot ogni 100ms del .stage
# 2) monta in GIF:
ffmpeg -framerate 10 -i frame_%03d.png -vf "scale=800:-1:flags=lanczos" arcade-intro.gif
# 2b) oppure in MP4 (consigliato per LinkedIn):
ffmpeg -framerate 10 -i frame_%03d.png -c:v libx264 -pix_fmt yuv420p arcade-intro.mp4
```

## Opzione C — estensione browser
Estensioni come "GIF Screen Recorder" registrano una porzione della pagina direttamente in GIF.

---

## Personalizzazione rapida
- **Parole chiave:** blocco `.word-wrap` nel file HTML (aggiungi/rimuovi `<div class="word">` e aggiorna i `nth-child` delay se cambi il numero).
- **Messaggio marquee:** testo dentro `.marquee span`.
- **Colori:** variabili `--cyan/--magenta/--green/--amber` in `:root` (già allineate alla palette del sito).
- **Dimensione:** `.stage { width/height }`.
