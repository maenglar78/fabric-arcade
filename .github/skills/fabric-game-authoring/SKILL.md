---
name: fabric-game-authoring
description: Playbook per creare, correggere, testare e pubblicare i giochi di Fabric Arcade (notebook HTML5 + RTI/KQL su Microsoft Fabric). Usare quando si lavora a un gioco del catalogo (catalog/<game>/), si correggono notebook che girano in Fabric, si fa il deploy in "Fabric Arcade Test", o si pubblica il gioco. Trigger: "sistema il gioco", "nuovo gioco arcade", "pubblica il gioco", "deploy in Fabric Arcade Test", "il gioco non funziona in Fabric".
---

# Skill: Fabric Arcade — Game Authoring & Publishing

Playbook consolidato dal lavoro su `fabric-racing-game` (2026-07). Applicare ai prossimi giochi.

## 1. Architettura di distribuzione (MEMORIZZARE)
- Pacchetto PyPI `fabric-arcade`. Repo: github.com/maenglar78/fabric-arcade (branch `main`).
- `%pip install fabric-arcade` → installa la **logica** (`fabric_arcade/fabric_api.py`, classe `Arcade`).
- `arcade.install("<game>")` a **runtime scarica gli asset da GitHub RAW `main`**:
  `raw.githubusercontent.com/maenglar78/fabric-arcade/main/catalog/<game>/{manifest.json, notebooks/*, schemas/*}`.
- **Regola d'oro:**
  - Modifiche a notebook / manifest / schemi → **basta `git push` su `main`** (nessun PyPI).
  - Modifiche a `fabric_api.py` (logica install) → serve **rilascio PyPI**.

## 2. Rilascio PyPI
- `.github/workflows/release.yml` pubblica su PyPI (trusted publishing OIDC) su **GitHub Release published**
  oppure `workflow_dispatch` con `publish_pypi=true`.
- Passi: bump versione in `pyproject.toml` → `git push` → creare GitHub Release con tag `vX.Y.Z` (UI: Releases →
  Draft new release → Choose a tag → Create new tag on publish → Publish). `gh` NON è installato in locale.
- NOTA: il job `deploy-website` di `release.yml` fallisce (ridondante coi workflow Pages dedicati); è benigno,
  il sito è online lo stesso e "Publish to PyPI" resta verde.

## 3. Regole d'oro per notebook che girano in Fabric (verificate live)
1. **localStorage = SecurityError** in Fabric (iframe sandbox senza `allow-same-origin`). Avvolgere OGNI accesso a
   `localStorage` in `try/catch`. NON mettere codice che può throware **prima** di registrare listener critici
   (es. tasti di gioco): un'eccezione lì blocca tutto il resto dello script. Usare fallback in-memory (`window.__x`).
2. **Timestamp inferito come STRING** quando la tabella la crea l'Eventstream (event-processing). Nelle query KQL
   usare sempre `todatetime(Timestamp)` (per `> ago()`, `bin()`, `datetime_diff`, ordinamenti).
3. **azure-kusto-data NON è installato** in Fabric → usare le **REST API** `/v2/rest/query`
   (`requests` + token `notebookutils.credentials.getToken("https://kusto.kusto.windows.net")`), NON il SDK.
4. **Auto-detect del Query URI** invece di config manuale: `notebookutils.runtime.context.get("currentWorkspaceId")`
   → `GET /v1/workspaces/{ws}/items?type=KQLDatabase` → trova il DB → `GET .../kqlDatabases/{id}` →
   `properties.queryServiceUri`. Fallback placeholder se fuori Fabric.
5. **Re-run pulito**: dopo un aggiornamento del notebook, la cella già eseguita NON si ri-renderizza. Istruire
   sempre l'utente: Reload + Clear all outputs + ri-eseguire le celle.

## 4. Ingestion RTI (Eventstream → Eventhouse)
- Flusso scelto: **event-processing** (l'Eventstream crea la tabella con "Create new table"). Consente auto-mapping
  senza mapper e senza connessione esterna.
- **NON pre-creare la tabella** (niente `"tables"` nel manifest, altrimenti l'install applica lo schema e il
  destination event-processing chiede "add mapper"). Config manuale in `post_deploy_steps`.
- **DirectIngestion via API definition NON funziona**: la connection Eventhouse non viene provisionata
  → destination "Warning", 0 righe. Non usarla.
- Il wizard event-processing pretende **dati live** nell'Inspect: giocare/inviare PRIMA, poi completare il destination.
- SAS del CustomEndpoint recuperabile via API:
  `GET /v1/workspaces/{ws}/eventstreams/{id}/sources/{sourceId}/connection` → `primaryConnectionString`.

## 5. Deploy in "Fabric Arcade Test" (per testare come utente finale)
- Workspace id: `a5235927-0289-4a06-83d1-456be383b496`. Helper riusabili in `dev/cathedral/upload_notebook.py`
  (`upload_or_update_notebook`, `_az_token`, `_wait_lro`, `find_item`, `FABRIC_API`, `WORKSPACE_ID`).
- Pattern per gioco: `dev/<game>/deploy_to_test_ws.py` (crea Eventhouse/KQLDB, notebook, cartella) +
  `setup_eventprocessing.py` se serve (droppa tabella + Eventstream source-only).
- Ogni `updateDefinition` **sovrascrive** il notebook (Cell1 SAS torna placeholder): per il test pre-compilare le
  SAS **in-memory** (mai scriverle nei file del catalogo).

## 6. Testare la UI del gioco SENZA Fabric (Playwright + iframe sandbox)
- Renderizzare l'HTML del gioco (le celle f-string) su file, aprirlo con `open_browser_page`, e testare i tasti con
  `run_playwright_code` (`page.keyboard`, leggere `car.x` via `frame.evaluate`).
- **Per riprodurre il comportamento di Fabric** avvolgere in un iframe `sandbox="allow-scripts"` (SENZA
  `allow-same-origin`): questo fa fallire `localStorage` esattamente come in Fabric → test fedele.

## 7. Checklist SICUREZZA prima di ogni `git push`
- Grep dei file del catalogo per SAS/segreti reali (namespace `*.servicebus.windows.net`, `SharedAccessKey=...`,
  cluster `trd-*`). Devono esserci solo PLACEHOLDER (`YOUR_NAMESPACE`, `key_XXXXX`, `trd-XXXXX`).
- Genericizzare `PLAYER_NAME`/valori utente nei notebook del catalogo.
- `git add` con path espliciti (non `-A`) per evitare residui dev.

## 8. Procedura tipo "sistema + pubblica un gioco"
1. Revisiona manifest/notebook/schemi vs ciò che il gioco realmente emette (fonte di verità = codice di gioco).
2. Applica i fix (regole §3–§4). Testa la UI in sandbox (§6) e le query KQL live via REST.
3. Deploy in "Fabric Arcade Test" (§5), l'utente testa con re-run pulito.
4. Sicurezza (§7) → `git add` espliciti → `commit` (conventional) → `push main` (asset pubblicati).
5. Se cambiata la logica `fabric_api.py`: bump versione + GitHub Release → PyPI (§2).
6. Consolida: handoff + decision log + action register (skill CSA).
