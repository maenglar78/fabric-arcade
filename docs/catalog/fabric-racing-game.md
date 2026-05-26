# 🏎️ Fabric Racing Game

[← Back to catalog](index.md)

---

## Overview

| | |
|---|---|
| **Type** | Accelerator |
| **Difficulty** | Intermediate |
| **Deploy Time** | ~3 min |
| **Complete Time** | ~30 min |

HTML5 multiplayer racing game for 4 drivers with real-time telemetry streaming. Learn how to build Custom Endpoints, JSON mapping, and live dashboards while having fun racing!

---

## Workloads

- **Real-Time Intelligence** - Stream processing and real-time analytics

---

## Fabric Items Deployed

| Icon | Item Type | Name | Description |
|------|-----------|------|-------------|
| 🏠 | Eventhouse | RacingEventhouse | Container for KQL databases |
| 📊 | KQL Database | RaceData | Stores race telemetry events |
| 🌊 | Eventstream | RacingStream | Ingests data from Custom Endpoint |
| 📓 | Notebook | Racing_Game | HTML5 game with embedded telemetry |
| 📓 | Notebook | Race_Simulator | Generates simulated race data |
| 📓 | Notebook | Race_Dashboard | KQL queries and visualizations |

---

## Scenarios

- **Streaming** - Real-time data ingestion from game events
- **Gaming** - Interactive HTML5 racing experience
- **Real-Time Dashboard** - Live visualization of race telemetry

---

## Quick Start

### Step 1: Install in your Fabric Notebook

```python
# Cell 1 - Install the package
%pip install -q fabric-arcade
```

```python
# Cell 2 - Import and install the game
from fabric_arcade import arcade

# Install the racing game in your current workspace
arcade.install("fabric-racing-game")
```

### Step 2: Open the Racing Game Notebook

1. Navigate to your workspace
2. Find and open the **Racing_Game** notebook
3. Run all cells to start the game!

### Step 3: Play and Learn!

1. Use **Arrow Keys** or **WASD** to control your car
2. Watch the telemetry stream in real-time to Eventhouse
3. Open **Race_Dashboard** to see live analytics

---

## ✨ Key Features

- 🎮 **Interactive HTML5 Game** - Play directly in a Fabric notebook
- 📡 **Custom Endpoint Integration** - Learn how to send data to Eventstream
- 🗺️ **JSON Mapping** - Understand data transformation in KQL
- 📊 **Real-Time Dashboard** - See race stats update live
- 👥 **Multiplayer Support** - Race against 3 AI drivers

---

## 🏛️ Solution Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  HTML5 Racing   │────▶│   Eventstream   │────▶│   Eventhouse    │
│     Game        │     │  (Custom EP)    │     │  (KQL Database) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  Race Dashboard │
                                                │   (KQL Queries) │
                                                └─────────────────┘
```

### Data Flow

1. **Game Events** - Player inputs and car positions are captured in the HTML5 game
2. **Eventstream Ingestion** - Events are sent via Custom Endpoint with JSON payload
3. **KQL Processing** - Data is mapped and stored in the GameEvents table
4. **Dashboard Visualization** - Real-time queries display race statistics

---

## 📦 Prerequisites

### Required
- **Microsoft Fabric Capacity** - F2 or higher (Trial capacity works!)
- **Fabric Workspace** - A workspace with Contributor permissions

### Recommended Knowledge
- Basic understanding of Fabric notebooks
- Familiarity with HTML/JavaScript (optional)
- Basic KQL knowledge for customizing dashboards (optional)

---

## 📖 Usage Instructions

### Playing the Game

1. Open the **Racing_Game** notebook
2. Run all cells to render the game
3. Controls:
   - **↑ / W** - Accelerate
   - **↓ / S** - Brake
   - **← / A** - Steer left
   - **→ / D** - Steer right

### Viewing Race Telemetry

1. Open the **Race_Dashboard** notebook
2. Run the KQL queries to see:
   - Live position tracking
   - Speed over time
   - Lap times
   - Event counts by player

### Customizing the Experience

- Edit `GameEvents` table schema to add custom metrics
- Modify the HTML5 game to send additional telemetry
- Create new KQL visualizations in Real-Time Dashboard

---

## 🔧 Troubleshooting

### Game doesn't load
- Ensure all notebook cells have finished executing
- Check that the kernel is connected (PySpark)

### No data in Eventhouse
- Verify the Eventstream is running (check for green status)
- Confirm the Custom Endpoint URL is correctly configured
- Check the JSON mapping in the Eventstream

### Dashboard shows no results
- Wait 30 seconds for data to flow through
- Ensure you've played the game (generated events)
- Check the time range filter in your KQL queries

---

## 📄 License

MIT License - This project is provided for demonstration and educational purposes.

---

[← Back to catalog](index.md)
