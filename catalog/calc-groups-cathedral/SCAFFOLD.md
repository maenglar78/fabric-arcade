# Calc Groups Cathedral — SCAFFOLD

> **Status:** in-development (target: first truly implementable game after Racing).
> All building blocks below are verified to work with current Fabric REST APIs + configured MCP servers.

## Concept

Player = Chief Architect of the Vertipaq Cathedral. 12 KPI variations need exposure on a real Semantic Model. Lazy way = 36 measures. Architect way = 3 base measures + 1 Calculation Group with 12 calc items. Judge runs DAX over XMLA and scores **elegance = `1 - (measure_count / 36)`**.

## Locked decisions

| # | Topic | Decision |
|---|---|---|
| 1 | Semantic Model creation | TMDL inline via Fabric REST `items` POST (Racing pattern). |
| 2 | Data | Synthetic Sales (3y) + Budget. Generated in `CalcGroups_Seed` notebook. |
| 3 | Judge execution | DAX via XMLA through MCP `powerbi-model.dax_query_operations`. |
| 4 | Measure counting | MCP `powerbi-model.measure_operations` (live count from TOM). |
| 5 | Telemetry | Eventhouse REST ingestion → `CathedralEvents` (same as Racing). |
| 6 | Seed measure | Pre-existing `Sales Amount Seed` excluded from score. |
| 7 | Calc item counting | Calc items count as 0; only the calc group counts as 1. |
| 8 | Rank | Mason → Sculptor → Architect → Grandmaster (based on elegance + pillars passed). |

## What gets installed

- **Lakehouse** `Cathedral_LH` — tables `Sales`, `Date`, `Customer`, `Budget` (3 years synthetic).
- **Semantic Model** `Cathedral_Model` — tables + relationships + ONE seed measure. Zero calc groups.
- **Eventhouse** `Cathedral_EH` + KQL DB `CathedralData` + table `CathedralEvents`.
- **3 Notebooks:** `CalcGroups_Seed`, `CalcGroups_Cathedral`, `CalcGroups_Dashboard`.

## 12 KPI Pillars

| # | Key | Concept | Expected on test date |
|---|---|---|---|
| 1 | Current | base | fixed by seed |
| 2 | LY | `SAMEPERIODLASTYEAR` | fixed |
| 3 | YoY | Current − LY | derived |
| 4 | YoYPct | (Current − LY) / LY | derived |
| 5 | YTD | `DATESYTD` | fixed |
| 6 | MTD | `DATESMTD` | fixed |
| 7 | QTD | `DATESQTD` | fixed |
| 8 | Rolling12 | `DATESINPERIOD` | fixed |
| 9 | VsBudget | Sales − Budget | derived |
| 10 | VsBudgetPct | Sales / Budget − 1 | derived |
| 11 | BestMonth | `TOPN` | fixed |
| 12 | **PctOfTotal (KEYSTONE)** | `ALLSELECTED` ratio | fixed |

## Judge validation

1. For each of the 12 pillars: build a DAX `EVALUATE` query that calls the calc item (or measure) on the locked test date.
2. Execute via XMLA → compare numeric result to expected (tolerance `0.01`).
3. Count player measures via TOM (exclude `Sales Amount Seed`).
4. Score: `pillars_passed / 12` × `(1 - measure_count / 36)`.
5. Emit telemetry per pillar.

## TODO (implementation order)

1. **`fabric_api.py` extension** — helpers: `create_semantic_model_from_tmdl(name, tmdl_str)`, `execute_dax(model_id, query)`, `count_measures(model_id, exclude=[...])`. Reuse Racing's REST patterns.
2. **TMDL seed** — `tmdl/cathedral_model.tmdl` with tables, relationships, one seed measure.
3. **Seed notebook** — generate synthetic Sales+Budget, write to Lakehouse Delta, deploy semantic model with TMDL above.
4. **Cathedral notebook** — 12 cells, one per pillar, with `Pillar` class and `judge.submit_all()`.
5. **Dashboard notebook** — KQL tiles + Plotly: pillars passed, measures count, elegance %, rank board.
6. **Install entry** — register `calc-groups-cathedral` in `arcade.install()` dispatch.
7. **Tests** — `tests/test_calc_groups_cathedral.py`: dry-run install in test workspace, simulate one pillar pass, verify telemetry.

## Constraints

- Do NOT touch racing game (frozen at tag `racing-v3-stable`).
- Reuse existing Eventhouse ingestion helper.
- Zero new deps — everything possible with already-installed libs + MCP.
