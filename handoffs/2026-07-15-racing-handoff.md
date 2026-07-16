# Handoff — 2026-07-15 · Fabric Racing Game (revisione + ripubblicazione)

**Workspace:** FabricArcade · **Tenant test:** MngEnvMCAP609624 (capacity mefabric)
**Deploy test:** "Fabric Arcade Test" (`a5235927-0289-4a06-83d1-456be383b496`) → cartella **"Fabric Racing Game (test)"**

## Obiettivo
Rivedere, sistemare e ripubblicare `fabric-racing-game` (primo gioco, con dubbi). Deploy di prova in
"Fabric Arcade Test", test manuale dell'utente, e **solo dopo autorizzazione** ripubblicare su GitHub
(`maenglar78/fabric-arcade` main) così `arcade.install` prende l'ultima versione.

## Stato: FUNZIONA in test ✅ (in attesa conferma finale utente su dashboard + badge)
- Ingestion end-to-end confermata: 57+ righe reali in `RaceData/GameEvents` (Marcolino, MaxScore 1450).
- Flusso scelto = **event-processing, l'Eventstream crea la tabella** (come "prima"). NON si pre-crea la tabella.

## Fix applicati (locali, NON ancora su GitHub)
- `schemas/GameEvents.kql`, `manifest.json` (eventTypes/columns), `catalog_index.json` (descrizione),
  `README.md`, `deploy.py`, `fabric_api.py` (README notebook + istruzioni Direct→poi tornati a event-processing).
- `race_check` Q2C (Telemetry/Speed → StarCollected); `race_dashboard` (lap→level times, speed→multiplier,
  heatmap→EventType×Level); Cell 3 `DB_NAME=RaceData` + chiarito Query URI.
- **todatetime(Timestamp)** in TUTTE le query (Timestamp è inferito come STRING dall'Eventstream). Verificato live.
- I 3 notebook (Racing_Championship, Race_Dashboard, Race_Check) ri-caricati in test.

## Scoperte chiave
- DirectIngestion via API definition NON provisiona la connection Eventhouse → destination "Warning", 0 righe. Abbandonato.
- Event-processing con tabella PRE-creata → prompt "add mapper" + wizard bloccato senza dati live. Causa del "casino".
- Soluzione: far creare la tabella all'Eventstream (tipi inferiti, Timestamp=string → serve todatetime()).
- Wizard event-processing pretende dati LIVE nell'Inspect: giocare PRIMA, poi configurare il destination.
- SAS del CustomEndpoint recuperabile via API: `GET /workspaces/{ws}/eventstreams/{id}/sources/{sourceId}/connection`.

## Script utili (dev/racing/)
- `deploy_to_test_ws.py` — deploy completo (⚠️ da aggiornare: NON pre-creare tabella; Eventstream source-only).
- `setup_eventprocessing.py` — droppa tabella + ricrea RacingStream con sola source CustomEndpoint.

## Prossime azioni (DOMANI)
1. Attendere conferma utente: Race_Dashboard (grafici) + Race_Check (badge) OK.
2. Allineare al flusso event-processing: `deploy_to_test_ws.py` e `fabric_api.py` install → NIENTE tabella
   pre-creata; spedire Eventstream con **source-only** (come setup_eventprocessing.py); aggiornare README/manifest.
3. Valutare `GameEvents.kql`: reference-only o rimuovere da manifest.tables.
4. **Solo con via libera esplicita dell'utente** → commit + push su GitHub (republish) così install serve l'ultima versione.

## Note
- Nulla è stato pushato su GitHub. Nessun commit fatto. Working tree con le modifiche locali sopra.
- Dettagli completi in memoria di sessione: `/memories/session/racing-review.md`.
