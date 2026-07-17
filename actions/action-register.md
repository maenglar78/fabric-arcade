# Action Register — FabricArcade

Registro delle azioni aperte. Aggiornare a ogni "wrap up".

| # | Azione | Stato | Aperto il | Note |
|---|--------|-------|-----------|------|
| 2 | Portare Oracle's Forge da "scaffolded" a gioco disponibile | Aperto | 2026-07-03 | Script di deploy verso "Fabric Arcade Test" già presente (`dev/oracle/deploy_to_test_ws.py`). |
| 3 | Valutare pubblicazione dei coming-soon (Vault Keeper, The Sphinx) | Aperto | 2026-07-03 | Attualmente card "coming-soon" sul sito. |
| 4 | Configurare Giscus (repo-id + category-id) in `website/js/feedback.js` | Aperto | 2026-07-10 | Abilitare Discussions + app giscus, poi incollare gli ID. Fino ad allora fallback su GitHub Issues. |
| 6 | Eseguire il piano editoriale LinkedIn (`marketing/linkedin-launch-plan.md`) | Aperto | 2026-07-10 | Lancio 2026-07-20 + 1 gioco ogni 2-3 giorni. |
| 7 | Fix opzionale CI: job `deploy-website` in `release.yml` fallisce (ridondante coi workflow Pages) | Aperto | 2026-07-16 | Rimuovere il job o aggiungere `concurrency: {group: pages}`. Benigno: sito online, PyPI verde. |
| 8 | Debito tecnico: 4 test falliti preesistenti (`Game.type`, `search_games(max_difficulty=...)`) | Aperto | 2026-07-16 | Disallineamento test vs `catalog.py`/`core.py`. Non legato al racing. |
| 9 | Applicare il trattamento racing (auto-detect URI, robustezza Fabric, REST) agli altri giochi RTI | Aperto | 2026-07-16 | Vedi `.github/skills/fabric-game-authoring/SKILL.md`. Candidati: ontology-detective, monster-breach. |
| 10 | Prima del lancio: "riscaldare" le anteprime social (LinkedIn Post Inspector / X Card Validator) per gli URL già condivisi | Aperto | 2026-07-17 | Cache LinkedIn ~7gg. Serve solo per URL condivisi PRIMA degli OG tag; i nuovi mostrano la card subito. |

## Completate
- **Sito: analytics + share + anteprime social** (2026-07-17): Cloudflare Web Analytics su 15 pagine; pulsanti share con post pre-compilati (#FabricArcade + #Gioco + link); Open Graph/Twitter Card + 6 social card giochi + card hub (home/feature). Generatore `dev/gen_social_cards.py`. Dettagli: `handoffs/2026-07-17-website-marketing-handoff.md`.
- **#5 GIF/MP4 intro arcade** (2026-07-17): `marketing/gif/arcade-intro.mp4` (1.76MB, 720p) + `.gif` fallback; descrizioni post riscritte in `marketing/posts/00-launch.md`.
- **Fabric Racing Game overhaul + pubblicazione v0.6.1** (2026-07-16): fix frecce (localStorage guard),
  bilanciamento, dashboard/check in REST + auto-detect URI, flusso event-processing. Push su `main` + Release PyPI.
  Dettagli: `handoffs/2026-07-16-racing-published-handoff.md`, `decisions/decision-log.md`.
- **#1 Builder Monster Breach eliminato** (2026-07-10): i 3 notebook erano già generati; file rimosso come da suo docstring.
- Rilascio v0.6.0: rimozione giochi legacy (2026-07-02).
- Pubblicazione Monster Breach v1.0.0.
