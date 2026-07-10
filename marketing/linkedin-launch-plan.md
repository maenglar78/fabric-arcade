# Fabric Arcade — Piano di Comunicazione LinkedIn

**Obiettivo:** lanciare Fabric Arcade e portare le persone a *provare* i giochi e a costruirsi un **piano di learning giocando** con Microsoft Fabric.
**Voce:** prima persona ("io ho creato…").
**Lingue:** ogni post in **Italiano** e **Inglese** (due versioni pronte in ogni file).
**Data di lancio:** 2026-07-20.
**Cadenza:** post di lancio + 1 gioco ogni 2–3 giorni.

---

## Fonti / razionale (source-backed)

- Il sito è servito da GitHub Pages e Netlify dalla cartella `website/` — verificato in `.github/workflows/deploy-pages.yml` e `netlify.toml`.
- I 6 giochi **disponibili** e i 6 **coming-soon** provengono dal sito live `https://maenglar78.github.io/fabric-arcade/` e da `catalog_index.json`.
- LinkedIn accetta come media **GIF/MP4**, non SVG animati → la GIF va prodotta registrando la pagina in `marketing/gif/arcade-intro.html`.
  Source: official — https://www.linkedin.com/help/linkedin/answer/a564109 — supports: formati media accettati da LinkedIn.
- Best practice orario/giorni (Tue–Thu, mattina) → linea guida di community, non garanzia. Source: community — https://blog.hootsuite.com/best-time-to-post-on-linkedin/ — supports: finestra di pubblicazione consigliata.

---

## Calendario editoriale

| # | Data | Giorno | Contenuto | File |
|---|------|--------|-----------|------|
| 0 | 2026-07-20 | Lun | **Post di lancio** dell'iniziativa + GIF arcade | `posts/00-launch.md` |
| 1 | 2026-07-23 | Gio | 🏎️ Fabric Racing Game | `posts/01-fabric-racing-game.md` |
| 2 | 2026-07-28 | Mar | 🏛️ Calc Groups Cathedral | `posts/02-calc-groups-cathedral.md` |
| 3 | 2026-07-31 | Ven | 🧙‍♂️ Monster Breach | `posts/03-monster-breach.md` |
| 4 | 2026-08-04 | Mar | 🏙️ City Builder | `posts/04-city-builder.md` |
| 5 | 2026-08-07 | Ven | 🕵️ Ontology Detective | `posts/05-ontology-detective.md` |
| 6 | 2026-08-11 | Mar | 🕹️ Retro Arcade | `posts/06-retro-arcade.md` |
| 7 | 2026-08-14 | Ven | **Recap** + teaser dei 6 giochi coming-soon | (opzionale, vedi sotto) |

> Le date cadono tutte tra Mar e Ven, la finestra migliore su LinkedIn. Adatta l'orario alle 08:30–10:00 CET.

---

## Hashtag consigliati

Base (sempre): `#MicrosoftFabric #FabricArcade #LearnByPlaying`
Per workload: `#PowerBI` `#DAX` `#DataEngineering` `#DataWarehouse` `#RealTimeIntelligence` `#KQL` `#DataFactory`

> Nessun handle X specificato: i pulsanti di share sul sito useranno solo l'URL e il titolo. Se vuoi aggiungere un handle/campagna, dimmelo e lo inserisco.

---

## Regole di stile per i post

1. **Hook** nella prima riga (curiosità o visione) — LinkedIn taglia dopo ~2 righe.
2. **1 idea per post**, niente muri di testo. Emoji come segnaposto visivi, con parsimonia.
3. **CTA chiara**: provare il gioco → link al sito.
4. Invito al **feedback/commento** (ora il sito ha commenti Giscus + segnalazione bug per ogni gioco).
5. Chiudi con 3–5 hashtag mirati.

---

## Asset GIF (stile arcade anni '80)

- Sorgente: `marketing/gif/arcade-intro.html` (loop di parole chiave/messaggi in stile CRT anni '80).
- Come esportarla in GIF/MP4: vedi `marketing/gif/README.md`.
- Da usare come media del **post di lancio** (#0).

---

## Post di recap #7 (opzionale) — traccia

- IT: "6 giochi live, altri 6 in forgia. Quale vuoi vedere per primo? 👇"
- EN: "6 games live, 6 more in the forge. Which one should I ship next? 👇"
- Elenca i coming-soon: Oracle's Forge (Data Science), Sentinel Grid (Activator), Purity Protocol (Dataflow), Portal Nexus (Mirroring), Vault Keeper (SQL DB), The Sphinx (AI/Copilot).
