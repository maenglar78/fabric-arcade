# 🔮 Oracle's Forge — Scaffold

> **Status:** 🚧 Coming soon. Notebooks contain a working scaffold with `# TODO` markers. Tune the AutoML time budgets and encoding to reach the Grand Oracle threshold.

## 🎮 Game design

Oracle's Forge is a **Data Science learning quest**: the player forges *Prophecy Crystals* (ML models) on real Fabric. The "game" is a thin notebook layer over real **AutoML + MLflow + Model Registry + PREDICT** workflows.

### Interaction loop per level

1. Player reads the **briefing** in `oracle_judge.ipynb` (`judge.brief(N)`).
2. Player works in `oracle_forge.ipynb` (Levels 1–4) or `oracle_prophecy.ipynb` (Level 5).
3. Player runs `judge.check_level(N)` → the Judge inspects the Lakehouse tables / MLflow experiment / Model Registry, emits `LevelComplete` / `LevelFailed` telemetry.
4. `oracle_dashboard.ipynb` tracks best `roc_auc` over attempts and the final rank.

### Design decisions (locked in)

| Question | Decision |
|---|---|
| Validation mechanism | **Notebook** (`judge.check_level(N)`) |
| Data | **Synthetic** churn-style dataset via `oracle_seed.ipynb` |
| AutoML engine | **FLAML** (Fabric AutoML) |
| Tracking | **MLflow** experiment `oracles-forge` + registry model `oracle_champion` |
| Win condition | Holdout **roc_auc ≥ 0.80** |

## 📦 What `arcade.install("oracles-forge")` deploys

- **1 Lakehouse** `OraclesForge_LH` — holds `omens_train`, `omens_holdout`, player output `prophecy_scores`
- **1 Eventhouse** `OraclesForge_EH` + **KQL Database** `ForgeData` + **Table** `ProphecyEvents`
- **5 Notebooks**: seed, forge (workbench), prophecy (scoring), judge, dashboard

## 🗺️ Level → Skill mapping

| Lvl | Trial | Skill |
|---|---|---|
| 1 | 🌫️ Gather the Auspices | Load + clean + encode features |
| 2 | 🔥 Light the Forge | First AutoML run + MLflow tracking |
| 3 | ⚔️ Arena of Models | Compare ≥3 algorithms on roc_auc |
| 4 | 👑 Crown the Crystal | Register champion in Model Registry |
| 5 | 🔮 The Prophecy | Batch scoring above the threshold |

## 🔨 TODO (development phase)

- [ ] Finalize `oracle_seed.ipynb` signal strength so the threshold is achievable but not trivial
- [ ] Harden `judge.check_level(N)` against partial/aborted runs
- [ ] Add real Eventhouse telemetry ingestion (currently print-based in preview)
- [ ] Wire `arcade.install("oracles-forge")` in `fabric_arcade/fabric_api.py` + `deploy.py`
- [ ] Build the website detail page `website/games/oracles-forge.html`
