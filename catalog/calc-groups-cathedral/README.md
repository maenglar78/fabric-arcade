# 🏛️ Calc Groups Cathedral

> **Status:** ✅ Ready · **Version:** 1.0.0 · **Workload:** Power BI / Semantic Model · **Difficulty:** ⭐⭐⭐ · **Duration:** ~60 min

Build a cathedral of **Calculation Groups** on a real Direct Lake semantic model. Replace 12 redundant time-intelligence measures with **one elegant calc group** and earn the rank of *Cathedral Builder*.

## What you'll learn

- Calculation Groups in Direct Lake semantic models
- `SELECTEDMEASURE()` and the `CALCULATE` pattern
- Authoring measures programmatically with **sempy-labs** (TOM)
- Streaming gameplay telemetry to **Eventhouse / KQL**
- Building a player-facing Plotly dashboard over KQL data

## The Quest

You build **12 KPI pillars** on the `Sales` table:

| # | Pillar | Concept |
|---|--------|---------|
| 1 | Current | base measure (SUM) |
| 2 | LastYear | `SAMEPERIODLASTYEAR` |
| 3 | YoY | `Current − LY` |
| 4 | YoY % | `(Current − LY) / LY` |
| 5 | YTD | `DATESYTD` |
| 6 | MTD | `DATESMTD` |
| 7 | QTD | `DATESQTD` |
| 8 | Rolling 12 | `DATESINPERIOD -12 months` |
| 9 | Best Month | `MAXX` over months |
| 10 | % of Year | `ALL` ratio |
| 11 | Avg Daily Sales | `AVERAGEX` over dates |
| 12 | Distinct Customers | `DISTINCTCOUNT` (standalone) |

**Final Challenge:** collapse pillars 1–11 into a single calc group with 11 items (pillar 12 stays standalone — it changes the aggregation, not the time context).

## Items installed

| Type | Name | Purpose |
|------|------|---------|
| Lakehouse | `Cathedral_LH` | Sales / Date / Customer / Budget Delta tables (3 years, synthetic) |
| Eventhouse | `Cathedral_EH` | Hosts `CathedralEvents` (KQL telemetry table) |
| Notebook | `01_Setup` | Generates data, loads tables, builds `Cathedral_Model` (Direct Lake) |
| Notebook | `02_Quest` | Reads the quest brief |
| Notebook | `03_Check` | Grades, scores, ships telemetry |
| Notebook | `04_Dashboard` | Live Plotly dashboard over KQL |

The semantic model **`Cathedral_Model`** is created at runtime by `01_Setup` (via sempy-labs), so it does not appear in the install list.

## Install

```python
%pip install -q fabric-arcade
from fabric_arcade import arcade
arcade.install("calc-groups-cathedral", workspace="My Workspace")
```

Then open `01_Setup` and run it once to populate the lakehouse and build the model.
Open `02_Quest` to read the brief, then start authoring measures and run `03_Check` to submit.

## Scoring

```
elegance = max(0, 100
                  - max(0, len(dax) - 60) * 0.4
                  - max(0, count(CALCULATE) - 1) * 8
                  - count(FILTER) * 6
                  - count(SUMX)   * 4)
score    = 50 + elegance * 0.5     # only if all 3 contexts pass
```

### Ranks

| Min score | Rank |
|-----------|------|
| 0 | Stonemason |
| 300 | Apprentice |
| 700 | Journeyman |
| 1100 | Architect |
| 1500 | Master Architect |
| 1800 | Cathedral Builder 🏆 |
