# Handoff — 2026-07-10 (Piano di comunicazione LinkedIn)

**Workspace:** FabricArcade · **Branch:** `main`
**Obiettivo:** preparare il lancio del sito (2026-07-20) con piano di comunicazione LinkedIn IT+EN, GIF arcade, e sezione feedback/share su ogni gioco.

## Lavoro svolto oggi
### A) Contenuti marketing (`marketing/`)
- `linkedin-launch-plan.md` — piano editoriale, calendario (lancio + 1 gioco ogni 2-3 giorni), hashtag, regole di stile.
- `posts/00-launch.md` — post di lancio IT+EN (visione + curiosità, CTA "prova e costruisci il tuo piano di learning").
- `posts/01..06` — un post IT+EN per ciascuno dei 6 giochi disponibili (Racing, Calc Groups Cathedral, Monster Breach, City Builder, Ontology Detective, Retro Arcade).
- `gif/arcade-intro.html` — animazione stile CRT anni '80 (loop 12s, 800×800) con parole chiave scorrevoli, marquee e CTA.
- `gif/README.md` — come esportare la GIF/MP4 (ScreenToGif / ffmpeg).

### B) Sito (`website/`) — feedback + share per gioco
- `css/game-detail.css` — stili `.game-feedback`, `.share-row`, `.share-btn`.
- `js/feedback.js` — pulsanti share (LinkedIn/X/Reddit) funzionanti + commenti **Giscus** (con fallback a GitHub Issues finché non si inseriscono repo-id/category-id).
- Sezione feedback inserita in tutte e 6 le pagine gioco prima di `</main>`.

## Fatti chiave verificati
- Il sito live è servito da GitHub Pages **e** Netlify dalla cartella `website/` (non dalla root). Fonte: `.github/workflows/deploy-pages.yml`, `netlify.toml`.
- 6 giochi disponibili + 6 coming-soon (da sito live e `catalog_index.json`).
- LinkedIn non riproduce SVG animati: la GIF va prodotta registrando `arcade-intro.html`.

## Open loops (vedi action-register #4-#6)
- Configurare Giscus (repo-id/category-id) in `website/js/feedback.js`.
- Produrre la GIF dal file HTML.
- Nessun handle X / hashtag di campagna specificato: i share usano solo URL+titolo.

## Prossima azione consigliata
1. Rivedere i testi dei post (tono/claim) prima del 2026-07-20.
2. Abilitare Discussions + app giscus e incollare gli ID.
3. Esportare la GIF e allegarla al post di lancio.
