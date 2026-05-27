# 🏙️ City Builder — Scaffold (Locked Design)

> **Status:** 🚧 Scaffold only. Notebooks contain placeholder cells. Warehouse + Semantic Model are pre-created empty (intentional — the Mayor builds them).
>
> The original `README.md` in this folder contains earlier exploratory notes. This file is the **authoritative design** going forward.

## 🎮 Game design

City Builder is a **learning quest** where the player is the **Mayor of Datapolis**. Each level = one new city district that must be modeled correctly in a Fabric Warehouse + Power BI semantic model. The "game" is a thin notebook layer over real Fabric items.

### Interaction loop per district

1. 📖 Player reads the **briefing** in `CityBuilder_Mayor` notebook.
2. 💼 Player opens **`Datapolis_DW`** Warehouse in Fabric UI and writes T-SQL (`CREATE TABLE`, `INSERT INTO ... SELECT FROM Datapolis_LH...`).
3. 🔗 Player opens **`Datapolis_Model`** semantic model in Fabric UI, adds relationships, writes the DAX measures listed in the briefing.
4. ⚖️ Player runs `mayor.inspect_district("taxi")` in the notebook:
   - Queries `INFORMATION_SCHEMA` to verify tables, columns, keys, FK relationships
   - Connects to semantic model via **XMLA endpoint**, runs each DAX measure with `EVALUATE`, compares to expected oracle
   - Emits `DistrictBuilt` or `DistrictRejected` event to `CityEvents`
5. 📊 `CityBuilder_Dashboard` updates: city map, Mayor reputation, DAX scoreboard.

### Locked design decisions

| Question | Decision |
|---|---|
| Tables created in | **Warehouse** `Datapolis_DW` |
| Warehouse state at install | **Pre-created empty** — player adds tables |
| Where DAX measures are written | **Semantic Model** in Fabric UI |
| Schema validation method | **`INFORMATION_SCHEMA`** queries |
| Boss fight | **Galaxy schema** (3 facts sharing conformed dimensions) |

## 📦 What `arcade.install("city-builder")` deploys

- **Lakehouse `Datapolis_LH`** — 8 raw + 8 expected oracle datasets
- **Warehouse `Datapolis_DW`** — empty
- **Semantic Model `Datapolis_Model`** — empty (bound to warehouse)
- **Eventhouse `Datapolis_EH`** + KQL DB `CityData` + table `CityEvents`
- **3 Notebooks**: `CityBuilder_Seed`, `CityBuilder_Mayor`, `CityBuilder_Dashboard`

## 🗺️ 8 districts → star schema concepts

| Lvl | District | Concept |
|---|---|---|
| 1 | 🏛️ Town Hall | Fact vs dimension identification |
| 2 | 🏘️ Residential | Surrogate keys + SCD Type 1 |
| 3 | 🚕 Taxi | Additive fact + conformed dimensions |
| 4 | ⚡ Energy Grid | Semi-additive fact (snapshot) |
| 5 | 🛒 Retail Plaza | Role-playing dimensions |
| 6 | 🏥 Hospital | Junk + degenerate dimensions |
| 7 | 🏭 Industrial Park | SCD Type 2 |
| 8 | 🌃 City-wide BI (BOSS) | Galaxy schema + perf tuning |

## 🤖 What the Mayor (judge) checks

- ✅ **Grain** correct (fact row count vs raw event count)
- ✅ **Keys**: surrogate `INT IDENTITY`, no NULL FKs
- ✅ **Relationships**: many-to-one single direction
- ✅ **Star vs Snowflake** penalty if snowflake without reason
- ✅ **DAX measure values** match expected (XMLA EVALUATE)
- ✅ **Performance**: query time under threshold

## 🔨 TODO (development phase)

- [ ] Implement `city_builder_seed.ipynb` — PySpark generation of 8 raw + 8 expected datasets in `Datapolis_LH`
- [ ] Implement `Mayor` class: `briefing()`, `inspect_district()`, XMLA executor, INFORMATION_SCHEMA validators, telemetry emitter
- [ ] Implement `city_builder_dashboard.ipynb` — KQL queries + Plotly city map
- [ ] Write 8 district briefing markdowns inside mayor notebook
- [ ] Wire `arcade.install("city-builder")` in `FabricArcade/fabric_arcade/fabric_api.py` — must create LH + empty DW + empty Semantic Model + EH + 3 notebooks (the empty DW/Semantic Model creation is the trickiest part — see Fabric REST APIs `dataWarehouses` and `semanticModels`)
