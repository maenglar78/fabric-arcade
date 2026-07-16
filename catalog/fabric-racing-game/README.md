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

- `RacingStream` - receives game telemetry

- `RacingEventhouse` with `RaceData` database

- `Racing_Championship` notebook - the game!

---

## 📖 How to Play

### Step 1: Configure Eventstream

1. Open **RacingStream**

2. Click **Edit**

3. Add **Custom Endpoint** source → Name: `TelemetryInput`

4. Add **Eventhouse** destination:
   - Data ingestion mode: `Event processing before ingestion`
   - Eventhouse: `RacingEventhouse`
   - Database: `RaceData`
   - KQL Destination table: **Create new** → `GameEvents`
   - Format: `Json`
   - 💡 The **Inspect** step reads a live sample to map the schema — if it shows *no data*, run the game first (Steps 2–3), then come back and finish this destination.

5. Connect Source → Destination

6. Click **Publish**

---

### Step 2: Get the 4 SAS Credentials

1. In Eventstream canvas, click on **TelemetryInput** (Custom Endpoint)

2. In the side panel, open the **Keys** tab (SAS Key Authentication)

3. Click 👁️ on **Connection string-primary key** to reveal it. You'll see something like:

```
Endpoint=sb://esXXXX.servicebus.windows.net/;SharedAccessKeyName=key_abc123;SharedAccessKey=AbCdEf...XyZ=;EntityPath=esXXXX_eh
```

4. **Map the connection string to 4 variables:**

| Notebook Variable | Where to find it | Example |
|-------------------|------------------|---------|
| `EH_NS` | Part after `sb://` and before `/` | `esXXXX.servicebus.windows.net` |
| `EH_NAME` | Value of `EntityPath=` | `esXXXX_eh` |
| `EH_KEY_NAME` | Value of `SharedAccessKeyName=` | `key_abc123` |
| `EH_KEY` | Value of `SharedAccessKey=` (long base64 string) | `AbCdEf...XyZ=` |

> 💡 **Tip:** `EH_NS` does **NOT** include `sb://` or the trailing `/`. Just the host name ending in `.servicebus.windows.net`.

---

### Step 3: Configure Game

1. Open **Racing_Championship** notebook

2. In Cell 1, paste your 4 values:

```python
EH_NS       = "esXXXX.servicebus.windows.net"   # from sb://...
EH_NAME     = "esXXXX_eh"                       # from EntityPath=
EH_KEY_NAME = "key_abc123"                      # from SharedAccessKeyName=
EH_KEY      = "AbCdEf...XyZ="                   # from SharedAccessKey=

PLAYER_NAME = "YourName"
```

3. Run all cells (the SAS token is auto-generated and valid for 4 hours)

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
| `racing_game_v3.ipynb` | Main game notebook with telemetry |
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
