# Handoff — 2026-07-16 · Fabric Racing Game pubblicato (v0.6.1)

**Workspace:** FabricArcade · **Branch:** `main` (commit `5368b2f`) · **Release:** PyPI **v0.6.1** ✅

## Cosa è stato fatto
Overhaul completo di `fabric-racing-game` (primo gioco, aveva vari problemi) e ripubblicazione.
`%pip install fabric-arcade` → `arcade.install("fabric-racing-game")` ora installa il gioco corretto.

- **Racing_Championship** (congelato): fix frecce (guard localStorage), leaderboard in-memory, bilanciamento
  10 livelli difficile (speed 3.5→10.8, target 350→5200, hitbox stelle 26), Cell 3 auto-detect Query URI.
- **Race_Dashboard** (congelato): riscritto in REST (no azure-kusto SDK), auto-detect Query URI, setup in 1 cella.
- **Race_Check** (congelato): auto-detect Query URI, rimosso `DASHBOARD_URL`, 2 gate sui dati.
- **manifest/README/deploy.py/fabric_api.py**: allineati a event-processing; `pyproject` 0.6.0→0.6.1.

## Verifiche
- UI testata in browser + iframe sandbox stile-Fabric (frecce OK, no freeze).
- Query KQL testate live (LevelComplete 16, StarCollected 315, best score Marcolino 4950).
- Test suite: 9 pass, **4 fail PREESISTENTI** (Game.type / search_games `max_difficulty`, NON legati a questo lavoro).

## Artefatti di consolidamento (skill CSA)
- `.github/skills/fabric-game-authoring/SKILL.md` — playbook riusabile per i prossimi giochi.
- `decisions/decision-log.md` — decisioni D1–D6.
- Memoria repo: `/memories/repo/fabric-arcade-publish.md` (meccanismo pubblicazione + gotchas Fabric).

## Open loops (vedi actions/action-register.md)
- CI: job `deploy-website` di `release.yml` fallisce (ridondante coi workflow Pages) — fix opzionale.
- 4 test preesistenti falliti (Game.type / search_games) — debito tecnico non legato al racing.
- Applicare lo stesso trattamento (auto-detect, robustezza Fabric, REST) agli altri giochi RTI.

## Prossima azione
Tornare al **piano marketing** (`marketing/linkedin-launch-plan.md`, post di lancio 2026-07-20).
