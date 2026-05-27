# 🧙‍♂️ Monster Breach — Scaffold

> **Status:** 🚧 Scaffold only. Notebooks contain placeholder cells. Pipelines are empty (intentional — player builds them).

## 🎮 Game design

Monster Breach is a **learning quest**: the player builds **real Fabric Data Pipelines** to defeat monsters. The "game" is a thin notebook-based layer over real Fabric items.

### Interaction loop per level

1. Player reads the **briefing** in `monster_breach_judge.ipynb` (e.g. *"Defeat the Null Bug: build a Copy Activity that filters non-null `CrystalId`"*).
2. Player opens the corresponding **empty pipeline** (e.g. `Lvl01_CopyQuest`) in the Fabric UI and assembles it.
3. Player **runs the pipeline** in the Fabric UI.
4. Player runs `judge.check_level(N)` in the notebook → reads pipeline output, compares to `clean_crystals_expected/lvlNN`, emits `LevelComplete` / `LevelFailed` event to Eventhouse.
5. `monster_breach_dashboard.ipynb` shows boss HP, crystals saved, leaderboard.

### Design decisions (locked in)

| Question | Decision |
|---|---|
| Validation mechanism | **Notebook** (`judge.check_level(N)`) — not auto-trigger |
| Dirty data | **Synthetic** via `seed_dirty_data.ipynb` |
| Difficulty variants | **1 variant per level** |
| Pipeline state at install | **Pre-created but empty** — player fills them |
| Boss fight | **Single mega-pipeline** with 10 activities |

## 📦 What `arcade.install("monster-breach")` deploys

- **1 Lakehouse** `MonsterBreach_LH` — holds `dirty_crystals`, `clean_crystals_expected`, player output tables
- **1 Eventhouse** `MonsterBreach_EH` + **KQL Database** `BattleData` + **Table** `BattleEvents`
- **3 Notebooks**: seed, judge, dashboard
- **8 empty level pipelines** `Lvl01_CopyQuest` → `Lvl08_RetryReef`
- **1 empty boss pipeline** `BossBattle_CorruptionKing`

## 🗺️ Level → Skill mapping

| Lvl | Monster | Skill |
|---|---|---|
| 1 | 🐛 Null Bug | Copy Activity |
| 2 | 👻 Duplicate Ghost | Dataflow Gen2 + Distinct |
| 3 | 🔥 Schema Dragon | Schema mapping / data type cast |
| 4 | ⏰ Latency Demon | Trigger / scheduling |
| 5 | 🌀 Loop Wraith | ForEach + parameters |
| 6 | 🎭 If Mimic | If Condition + expressions |
| 7 | ⚡ Switch Hydra | Switch Activity multi-branch |
| 8 | 💀 Failure Phantom | Retry policy + error handling |
| 9 | 👑 Corruption King | Mega-pipeline: all 10 activities |

## 🔨 TODO (development phase)

- [ ] Implement `seed_dirty_data.ipynb` — generate 8 dirty datasets + expected outputs (PySpark on Lakehouse)
- [ ] Implement `judge.check_level(N)` — output diff + telemetry emission
- [ ] Implement `monster_breach_dashboard.ipynb` — KQL queries for boss HP / leaderboard
- [ ] Write 9 pipeline JSON definitions (empty shells with correct sink/source bindings) for the installer
- [ ] Wire `arcade.install("monster-breach")` in `fabric_arcade/fabric_api.py`
- [ ] Write per-level briefing markdown (currently TODO inside judge notebook)
