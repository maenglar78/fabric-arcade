# Decision Log — FabricArcade

Decisioni tecniche durature. Ogni voce: contesto → decisione → motivo.

## 2026-07-16 · Fabric Racing Game — overhaul e pubblicazione (v0.6.1)

### D1 — Ingestion via "event-processing" (l'Eventstream crea la tabella)
- **Contesto:** pre-creando la tabella `GameEvents` + JSON mapping, il destination Eventhouse in event-processing
  chiedeva "add mapper"; DirectIngestion via API non provisiona la connection (destination "Warning", 0 righe).
- **Decisione:** NON pre-creare la tabella (rimosso `"tables"` dal manifest). L'Eventstream la crea in modalità
  "Event processing before ingestion" (Create new table). Config manuale nei `post_deploy_steps`.
- **Motivo:** è il flusso che "funziona come prima", senza mapper e senza connessione esterna fragile.

### D2 — Fix tasti freccia = guard su localStorage
- **Contesto:** in Fabric le frecce non muovevano l'auto e i "Best Scores" sparivano. Riprodotto in iframe
  `sandbox="allow-scripts"`: `localStorage` lancia SecurityError; `loadLeaderboard()` (chiamato PRIMA della
  registrazione dei listener tasti) interrompeva lo script.
- **Decisione:** `try/catch` attorno a ogni accesso `localStorage` + fallback leaderboard in-memory.
- **Motivo:** verificato che ripristina le frecce anche in sandbox stile-Fabric. Root cause reale (non il focus).

### D3 — Query KQL: `todatetime(Timestamp)` ovunque
- **Motivo:** l'event-processing inferisce `Timestamp` come STRING → confronti temporali/bin/datetime_diff falliscono
  (HTTP 400). `todatetime()` è robusto sia per string che datetime.

### D4 — Dashboard e Check via REST, non SDK; auto-detect Query URI
- **Contesto:** `azure-kusto-data` non è installato in Fabric → errore import. Config manuale del cluster URI fragile.
- **Decisione:** REST `/v2/rest/query` + token `notebookutils`; auto-detect del Query URI via Fabric API.
- **Motivo:** nessun pacchetto da installare, zero config manuale, coerente tra i 3 notebook.

### D5 — Badge senza `DASHBOARD_URL`
- **Decisione:** rimosso il requisito URL dashboard (auto-dichiarazione). Badge su 2 gate basati sui dati.
- **Motivo:** il gioco fornisce un dashboard-notebook, non un KQL Dashboard item → l'URL creava confusione.

### D6 — Pubblicazione: push su `main` per gli asset, PyPI solo per la logica
- **Decisione:** asset (notebook/manifest) via `git push main`; `fabric_api.py` via GitHub Release → PyPI.
- **Motivo:** `arcade.install` scarica gli asset da GitHub raw main a runtime.
