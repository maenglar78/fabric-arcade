# 🏰 Quest Data Pipeline

> **Build a medallion architecture data pipeline as a fantasy adventure**

![Difficulty](https://img.shields.io/badge/Difficulty-Advanced-red)
![Duration](https://img.shields.io/badge/Duration-40%20min-blue)
![Workloads](https://img.shields.io/badge/Workloads-DE%20%2B%20DF-green)

## 🎯 Quest Briefing

Welcome, brave Data Knight! The kingdom's treasures are scattered across dangerous dungeons (raw data sources). Your quest: **collect the loot, refine it in the forge, and deliver legendary artifacts to the royal treasury**.

This is the Medallion Architecture... but with swords and dragons! 🐉

| Layer | Fantasy Theme | Technical Reality |
|-------|--------------|-------------------|
| 🥉 **Bronze** | Dungeon Loot | Raw data landing zone |
| 🥈 **Silver** | Refined Treasures | Cleaned, deduplicated data |
| 🥇 **Gold** | Legendary Artifacts | Business-ready aggregates |

## 🛠️ What You'll Learn

| Skill | Fabric Workload | Level |
|-------|-----------------|-------|
| Lakehouse architecture | Data Engineering | ⭐⭐⭐ |
| Data pipelines | Data Factory | ⭐⭐ |
| Spark transformations | Notebook | ⭐⭐⭐ |
| Delta Lake | Lakehouse | ⭐⭐ |

## 📋 Prerequisites

- Microsoft Fabric workspace with F4+ capacity (Spark)
- PySpark knowledge
- Understanding of ETL concepts

## 🏰 Quick Start

```python
import fabric_arcade as arcade

arcade.install("quest-pipeline")
arcade.play("quest-pipeline")
```

## 📖 Quest Chapters

### Chapter 1: Enter the Dungeon 🥉
**Objective**: Set up the Bronze Lakehouse and ingest raw data

The Bronze layer is your **dungeon loot collection** - everything you find goes here, untouched and unfiltered.

1. Create Lakehouse `bronze-dungeon`
2. Ingest raw data from various "dungeons":

```python
# Dungeon 1: Monster Encounters (CSV files)
monsters_df = spark.read.csv(
    "abfss://dungeons@onelake.dfs.fabric.microsoft.com/monsters/*.csv",
    header=True,
    inferSchema=True
)
monsters_df.write.format("delta").mode("append").save(
    "Tables/raw_monster_encounters"
)

# Dungeon 2: Treasure Chests (JSON)
treasure_df = spark.read.json(
    "abfss://dungeons@onelake.dfs.fabric.microsoft.com/treasure/*.json"
)
treasure_df.write.format("delta").mode("append").save(
    "Tables/raw_treasure_chests"
)

# Dungeon 3: Hero Stats (Parquet)
heroes_df = spark.read.parquet(
    "abfss://dungeons@onelake.dfs.fabric.microsoft.com/heroes/"
)
heroes_df.write.format("delta").mode("append").save(
    "Tables/raw_hero_stats"
)
```

**Achievement Unlocked: 🥉 Bronze Collector**

### Chapter 2: The Forge 🥈
**Objective**: Transform raw loot into refined treasures in Silver

The Silver layer is your **blacksmith's forge** - clean the rust, remove duplicates, standardize the quality.

1. Create Lakehouse `silver-treasury`
2. Apply data quality transformations:

```python
from pyspark.sql.functions import *

# Read bronze data
bronze_monsters = spark.read.format("delta").load(
    "abfss://bronze-dungeon@onelake.dfs.fabric.microsoft.com/Tables/raw_monster_encounters"
)

# Clean and transform
silver_monsters = (bronze_monsters
    # Remove duplicates
    .dropDuplicates(["encounter_id"])
    # Clean nulls
    .fillna({"damage_dealt": 0, "gold_dropped": 0})
    # Standardize types
    .withColumn("monster_type", upper(col("monster_type")))
    # Add processing metadata
    .withColumn("processed_at", current_timestamp())
    .withColumn("source_system", lit("dungeon_crawler"))
)

# Write to Silver
silver_monsters.write.format("delta").mode("overwrite").save(
    "abfss://silver-treasury@onelake.dfs.fabric.microsoft.com/Tables/monster_encounters"
)
```

**Data Quality Checks (The Forge's Quality Control):**
```python
# Check for orphaned records
orphan_check = silver_monsters.filter(col("hero_id").isNull()).count()
assert orphan_check == 0, f"Found {orphan_check} encounters without heroes!"

# Check for future dates
future_check = silver_monsters.filter(col("encounter_date") > current_date()).count()
assert future_check == 0, "Time-traveling monsters detected!"
```

**Achievement Unlocked: 🥈 Silver Refiner**

### Chapter 3: The Royal Treasury 🥇
**Objective**: Create legendary artifacts (business aggregations) in Gold

The Gold layer is the **Royal Treasury** - only the finest, most valuable insights worthy of the King's attention.

1. Create Lakehouse `gold-vault`
2. Build business-ready aggregations:

```python
# Hero Performance Leaderboard
hero_performance = (silver_monsters
    .groupBy("hero_id", "hero_name", "hero_class")
    .agg(
        count("*").alias("total_encounters"),
        sum("monsters_slain").alias("total_kills"),
        sum("gold_dropped").alias("total_gold"),
        avg("damage_dealt").alias("avg_damage"),
        max("dungeon_level").alias("highest_level_reached")
    )
    .withColumn("kill_efficiency", col("total_kills") / col("total_encounters"))
    .orderBy(desc("total_gold"))
)

# Write to Gold
hero_performance.write.format("delta").mode("overwrite").save(
    "abfss://gold-vault@onelake.dfs.fabric.microsoft.com/Tables/hero_leaderboard"
)

# Dungeon Analytics
dungeon_stats = (silver_monsters
    .groupBy("dungeon_id", "dungeon_name", "difficulty")
    .agg(
        count("*").alias("total_runs"),
        avg("completion_time_minutes").alias("avg_completion_time"),
        sum("gold_dropped").alias("total_gold_yield"),
        countDistinct("hero_id").alias("unique_heroes")
    )
)

dungeon_stats.write.format("delta").mode("overwrite").save(
    "abfss://gold-vault@onelake.dfs.fabric.microsoft.com/Tables/dungeon_analytics"
)
```

**Achievement Unlocked: 🥇 Gold Master**

### Chapter 4: The Automation Spell 🔄
**Objective**: Create a Data Factory pipeline to automate the quest

Build a pipeline that runs the full Bronze → Silver → Gold flow:

```
Pipeline: Quest_ETL_Pipeline
├── Activity 1: Bronze_Ingestion (Notebook)
├── Activity 2: Silver_Transformation (Notebook)
│   └── Depends on: Bronze_Ingestion
├── Activity 3: Gold_Aggregation (Notebook)
│   └── Depends on: Silver_Transformation
└── Activity 4: Notify_King (Email on completion)
    └── Depends on: Gold_Aggregation
```

Schedule: Daily at midnight (when the dungeons reset!)

## 🏅 Achievements

| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| Bronze Collector | Complete Bronze layer | 🥉 |
| Silver Refiner | Complete Silver layer | 🥈 |
| Gold Master | Complete Gold layer | 🥇 |
| Pipeline Wizard | Automate full flow | 🔄 |
| Legendary Knight | Complete all chapters | 🏆 |

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE KINGDOM'S DATA REALM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │  🏔️ Dungeon │   │  🏔️ Dungeon │   │  🏔️ Dungeon │           │
│  │  (CSV)      │   │  (JSON)     │   │  (Parquet)  │           │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘           │
│         │                 │                 │                   │
│         └────────────┬────┴────────────────┘                   │
│                      ▼                                          │
│              ┌──────────────┐                                   │
│              │ 🥉 BRONZE    │  ← Raw Loot                       │
│              │ Dungeon LH   │                                   │
│              └──────┬───────┘                                   │
│                     │ Forge (Notebook)                          │
│                     ▼                                           │
│              ┌──────────────┐                                   │
│              │ 🥈 SILVER    │  ← Refined Treasures              │
│              │ Treasury LH  │                                   │
│              └──────┬───────┘                                   │
│                     │ Royal Processing                          │
│                     ▼                                           │
│              ┌──────────────┐                                   │
│              │ 🥇 GOLD      │  ← Legendary Artifacts            │
│              │ Vault LH     │                                   │
│              └──────┬───────┘                                   │
│                     │                                           │
│                     ▼                                           │
│              ┌──────────────┐                                   │
│              │ 👑 KING'S    │  ← Power BI Reports               │
│              │ DASHBOARD    │                                   │
│              └──────────────┘                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔗 Resources

- [Lakehouse Tutorial](https://learn.microsoft.com/fabric/data-engineering/tutorial-lakehouse-introduction)
- [Delta Lake Guide](https://learn.microsoft.com/fabric/data-engineering/lakehouse-and-delta-tables)
- [Data Factory Pipelines](https://learn.microsoft.com/fabric/data-factory/create-first-pipeline)

## 🎮 Related Games

- 🏙️ **City Builder** - Apply medallion to urban simulation
- 🌊 **Ocean Explorer** - Combine with ML workflows

---

*"The kingdom's data flows from dungeon to throne!"* 👑
