# 🏎️ Fabric Racing Game

> **An HTML5 racing game with real-time telemetry on Microsoft Fabric**

![Difficulty](https://img.shields.io/badge/Difficulty-Intermediate-orange)
![Duration](https://img.shields.io/badge/Duration-30%20min-blue)
![Workloads](https://img.shields.io/badge/Workloads-Real--Time%20Intelligence-green)

---

## 🎮 What is it?

A retro-style racing game running in a Fabric Notebook.

Every game action sends telemetry to Eventhouse via Eventstream!

**Features:**

- 10 Fabric-themed tracks (Lakehouse Lane, Pipeline Pass, etc.)

- Lives system (3 lives, Game Over when depleted)

- Score multipliers (up to x10)

- Real-time event streaming to KQL Database

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Game Notebook  │  ← HTML5 game in Fabric Notebook
│  (JavaScript)   │
└────────┬────────┘
         │ HTTP POST (SAS Token)
         ▼
┌─────────────────┐
│  Eventstream    │  ← Custom Endpoint receives JSON events
│ (TelemetryInput)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Eventhouse    │  ← Stores game events in KQL Database
│  (GameEvents)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  KQL Queries    │  ← Analyze player performance
└─────────────────┘
```

---

## 🚀 Quick Start

### Install

```python
pip install fabric-arcade
```

### Deploy

```python
from fabric_arcade import arcade

arcade.install("fabric-racing-game")
```

This creates in your Fabric workspace:

- `RacingEventstream` - receives game telemetry

- `RacingEventhouse` with `RaceData` database

- `Racing_Championship` notebook - the game!

---

## 📖 How to Play

### Step 1: Configure Eventstream

1. Open **RacingEventstream**

2. Click **Edit**

3. Add **Custom Endpoint** source → Name: `TelemetryInput`

4. Add **Eventhouse** destination:
   - Eventhouse: `RacingEventhouse`
   - Database: `RaceData`
   - Table: `GameEvents`
   - Format: `Json`

5. Connect Source → Destination

6. Click **Publish**

---

### Step 2: Get Connection String

1. Click on **TelemetryInput** node

2. In Details panel → **SAS Key Authentication**

3. Click 👁️ on **Connection string-primary key**

4. Copy the full string

---

### Step 3: Configure Game

1. Open **Racing_Championship** notebook

2. In Cell 1, paste:

```python
CONNECTION_STRING = "Endpoint=sb://your...;SharedAccessKeyName=...;SharedAccessKey=...;EntityPath=..."
PLAYER_NAME = "YourName"
```

3. Run all cells

---

### Step 4: Play!

| Control | Action |
|---------|--------|
| ← / A | Steer Left |
| → / D | Steer Right |

| Item | Points |
|------|--------|
| ⭐ Star | +50 × multiplier |
| 🐛 Bug | -30 |

**Lives:** Start with 3 ❤️, lose 1 per failed level

**Goal:** Reach target score before finish line!

---

## 📊 Sample KQL Queries

### Events by Type

```kql
GameEvents
| summarize count() by EventType
| render piechart
```

### Player Scores

```kql
GameEvents
| where EventType == "GameComplete" or EventType == "GameOver"
| project Timestamp, PlayerId, TotalScore, Level=Level
| order by TotalScore desc
```

### Events Timeline

```kql
GameEvents
| where Timestamp > ago(1h)
| summarize Events=count() by bin(Timestamp, 1m)
| render timechart
```

---

## 🔧 Troubleshooting

### Telemetry not working (📡 stays at 0)

- Verify connection string is correct

- Check Eventstream is **Published** and **Running**

- Open browser console (F12) for errors

### No data in Eventhouse

- Wait 30-60 seconds after sending first events

- Verify Eventstream Source → Destination is connected

- Check Custom Endpoint shows **Active** status

---

## 📁 Files Included

| File | Description |
|------|-------------|
| `racing_game_v2.ipynb` | Main game notebook with telemetry |
| `race_dashboard.ipynb` | KQL analytics dashboard |

---

## 🎓 What You'll Learn

- Eventstream Custom Endpoints

- Event Hub REST API with SAS tokens

- Real-time data ingestion

- KQL queries and visualizations

- HTML5 games in Fabric Notebooks

---

## 📜 License

MIT License - Free to use, modify, and share!
