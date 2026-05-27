# 🏎️ Fabric Racing Game

> **A multiplayer HTML5 racing game with real-time telemetry on Microsoft Fabric**

![Difficulty](https://img.shields.io/badge/Difficulty-Intermediate-orange)
![Duration](https://img.shields.io/badge/Duration-30%20min-blue)
![Workloads](https://img.shields.io/badge/Workloads-Real--Time%20Intelligence-green)

## 🏁 Race Briefing

Welcome to the **Fabric Racing Championship**! A real HTML5 racing game for **4 players**, where every race generates real-time telemetry flowing through Fabric Real-Time Intelligence architecture.

Each player has their own notebook with the embedded game. While playing, race events (position, speed, collisions, laps) are sent in real-time to the Eventhouse for live analytics!

### 🎮 The Concept
- **4 HTML5 Notebooks** - One for each driver (Race_P1, Race_P2, Race_P3, Race_P4)
- **Arcade game** - Simple controls, retro graphics, maximum fun
- **Real-time telemetry** - Every action generates events to the Eventstream
- **Live dashboard** - Watch the race in real-time with KQL

## 🛠️ What You'll Learn

| Skill | Fabric Workload | Level |
|-------|-----------------|-------|
| Custom Endpoint ingestion | Eventstream | ⭐⭐ |
| JSON data mapping | KQL Database | ⭐⭐ |
| Real-time queries | Eventhouse | ⭐⭐ |
| HTML5 in notebooks | Notebook | ⭐⭐ |
| Live dashboards | Real-Time Dashboard | ⭐⭐ |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FABRIC RACING GAME                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │ Race_P1  │ │ Race_P2  │ │ Race_P3  │ │ Race_P4  │  ← 4 HTML5 Notebooks  │
│  │ 🏎️ Red   │ │ 🏎️ Blue  │ │ 🏎️ Green │ │ 🏎️ Yellow│                       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘                       │
│       │            │            │            │                              │
│       └────────────┴─────┬──────┴────────────┘                              │
│                          ▼                                                   │
│                 ┌─────────────────┐                                         │
│                 │   Eventstream   │  ← Custom Endpoint                      │
│                 │  (racing-stream)│                                         │
│                 └────────┬────────┘                                         │
│                          │                                                   │
│                          ▼                                                   │
│                 ┌─────────────────┐                                         │
│                 │   Eventhouse    │                                         │
│                 │ (racing-events) │                                         │
│                 └────────┬────────┘                                         │
│                          │                                                   │
│                          ▼                                                   │
│                 ┌─────────────────┐                                         │
│                 │  KQL Database   │  ← GameEvents Table                     │
│                 │  (race-data)    │     + JSON Mapping                      │
│                 └────────┬────────┘                                         │
│                          │                                                   │
│                          ▼                                                   │
│                 ┌─────────────────┐                                         │
│                 │  RT Dashboard   │  ← Leaderboard + Analytics              │
│                 │ (race-monitor)  │                                         │
│                 └─────────────────┘                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- Microsoft Fabric workspace with F2+ capacity
- 4 people to play (or test solo with multiple browsers!)

## 🏎️ Quick Start

```python
import fabric_arcade as arcade

# Automatic deployment of the complete workspace
arcade.install("fabric-racing-game")

# The deploy notebook creates everything:
# 1. Workspace with capacity
# 2. Eventhouse + KQL Database
# 3. GameEvents table + JSON mapping
# 4. Eventstream (Custom Endpoint)
# 5. The 4 player notebooks with HTML5 game
```

## 📖 Race Chapters

### 🔧 Qualifying: Setup KQL Database

Create the **GameEvents** table in the KQL Database with 11 columns for all event types:

```kql
.create table GameEvents (
    Timestamp: datetime,
    SessionId: string,
    PlayerId: string,
    PlayerName: string,
    EventType: string,      // position, lap, collision, finish, speed, start
    PositionX: real,
    PositionY: real,
    Speed: real,
    LapNumber: int,
    LapTime: real,
    GameData: dynamic       // Extra data in JSON
)

// JSON mapping per ingestion
.create table GameEvents ingestion json mapping 'GameEventsMapping' 
'['
'{"column":"Timestamp","path":"$.timestamp","datatype":"datetime"},'
'{"column":"SessionId","path":"$.sessionId","datatype":"string"},'
'{"column":"PlayerId","path":"$.playerId","datatype":"string"},'
'{"column":"PlayerName","path":"$.playerName","datatype":"string"},'
'{"column":"EventType","path":"$.eventType","datatype":"string"},'
'{"column":"PositionX","path":"$.positionX","datatype":"real"},'
'{"column":"PositionY","path":"$.positionY","datatype":"real"},'
'{"column":"Speed","path":"$.speed","datatype":"real"},'
'{"column":"LapNumber","path":"$.lapNumber","datatype":"int"},'
'{"column":"LapTime","path":"$.lapTime","datatype":"real"},'
'{"column":"GameData","path":"$.gameData","datatype":"dynamic"}'
']'
```

### 🚦 Race Start: Eventstream Setup

1. Create the Eventstream `racing-stream`
2. Configure **Custom Endpoint** as source
3. Add **Eventhouse** as destination
4. **Publish** the Eventstream in the Fabric portal

```
Custom Endpoint (SAS URL)
        │
        ▼
   Eventstream
        │
        ▼
   Eventhouse
   (GameEvents)
```

### 🎮 Mid-Race: Notebook HTML5 Game

Each notebook contains a complete HTML5 game with:
- **2D Track** with curves and straightaways
- **4 colored cars** (🔴 Red, 🔵 Blue, 🟢 Green, 🟡 Yellow)
- **Controls** via keyboard (arrows or WASD)
- **Telemetry** sent every 100ms to the Custom Endpoint

```python
# Race_P1.ipynb - Player 1 (Red Car)
from IPython.display import HTML
import json

# Configurazione giocatore
PLAYER_ID = "P1"
PLAYER_NAME = "Red Racer"
PLAYER_COLOR = "#FF0000"
SAS_URL = "<eventstream-custom-endpoint-sas>"

# Il gioco HTML5 embedded
game_html = f"""
<canvas id="raceCanvas" width="800" height="600"></canvas>
<script>
const playerId = "{PLAYER_ID}";
const playerName = "{PLAYER_NAME}";
const sasUrl = "{SAS_URL}";

// Game loop - sends telemetry every 100ms
function sendTelemetry() {{
    const event = {{
        timestamp: new Date().toISOString(),
        sessionId: sessionId,
        playerId: playerId,
        playerName: playerName,
        eventType: "position",
        positionX: car.x,
        positionY: car.y,
        speed: car.speed,
        lapNumber: car.lap,
        lapTime: car.lapTime,
        gameData: {{ steering: car.steering, throttle: car.throttle }}
    }};
    
    fetch(sasUrl, {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(event)
    }});
}}

setInterval(sendTelemetry, 100);
</script>
"""

HTML(game_html)
```

### 📊 Dashboard: Live Race Analytics

**Query 1: Live Leaderboard**
```kql
GameEvents
| where EventType == "position"
| where Timestamp > ago(5m)
| summarize arg_max(Timestamp, *) by PlayerId
| extend CurrentLap = LapNumber, CurrentSpeed = Speed
| order by CurrentLap desc, LapTime asc
| project 
    Position = row_number(),
    PlayerName,
    PlayerId,
    CurrentLap,
    CurrentSpeed = round(CurrentSpeed, 1),
    LastUpdate = Timestamp
```

**Query 2: Lap Times Comparison**
```kql
GameEvents
| where EventType == "lap"
| project Timestamp, PlayerName, LapNumber, LapTime
| order by LapNumber asc, LapTime asc
| render columnchart with (
    title="Lap Times by Player",
    xcolumn=LapNumber,
    ycolumns=LapTime,
    series=PlayerName
)
```

**Query 3: Speed Heatmap**
```kql
GameEvents
| where EventType == "position"
| summarize AvgSpeed = avg(Speed) by 
    bin(PositionX, 50),
    bin(PositionY, 50)
| render heatmap with (title="Speed Heatmap - Track Analysis")
```

**Query 4: Race Events Timeline**
```kql
GameEvents
| where EventType in ("start", "lap", "collision", "finish")
| project Timestamp, PlayerName, EventType, LapNumber, GameData
| order by Timestamp asc
| take 100
```

### 🏆 Checkered Flag: Post-Race Report

Create a **Real-Time Dashboard** with:

1. **Leaderboard Panel** - Real-time positions
2. **Speed Chart** - Speed of each player
3. **Lap Times Grid** - Lap times comparison
4. **Track Map** - Car positions on track

## 🛠️ Post-Deploy Configuration

| Step | Action | Where |
|------|--------|-------|
| 1 | Fill in CAPACITY_ID in deploy notebook | Deploy_FabricRacingGame |
| 2 | Publish the Eventstream | Fabric Portal |
| 3 | Copy SAS URL to the 4 notebooks | Race_P1 - Race_P4 |
| 4 | Update CLUSTER_URI | All notebooks |
| 5 | Test with KQL query | KQL Database |

## 🏅 Achievements

| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| First Start | Launch the first race | 🏁 |
| Full Grid | 4 players connected simultaneously | 👥 |
| Photo Finish | Finish within 0.5s of each other | 📸 |
| Speed Demon | Reach max speed > 200 | ⚡ |
| Clean Race | Complete 5 laps without collisions | 🧹 |
| Champion | Win 3 races in a row | 🏆 |

## 🎮 The 4 Drivers

| Notebook | Player | Color | Emoji |
|----------|--------|-------|-------|
| Race_P1 | Red Racer | 🔴 #FF0000 | 🏎️ |
| Race_P2 | Blue Bolt | 🔵 #0000FF | 🚙 |
| Race_P3 | Green Machine | 🟢 #00FF00 | 🚗 |
| Race_P4 | Yellow Flash | 🟡 #FFFF00 | 🚕 |

## 📁 Deploy Contents

The **Deploy_FabricRacingGame** notebook (10 cells) automatically creates:

```
FabricRacingGame/
├── 📊 racing-events (Eventhouse)
│   └── 📂 race-data (KQL Database)
│       └── 📋 GameEvents (Table)
├── 🌊 racing-stream (Eventstream)
│   ├── Source: Custom Endpoint
│   └── Destination: Eventhouse
├── 📓 Race_P1 (Notebook - Player 1)
├── 📓 Race_P2 (Notebook - Player 2)
├── 📓 Race_P3 (Notebook - Player 3)
├── 📓 Race_P4 (Notebook - Player 4)
└── 📓 Deploy_FabricRacingGame (Notebook)
```

## 🔗 Resources

- [Eventstream Custom Endpoints](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/add-source-custom-endpoint)
- [KQL Ingestion Mapping](https://learn.microsoft.com/azure/data-explorer/kusto/management/mappings)
- [Real-Time Dashboard](https://learn.microsoft.com/fabric/real-time-intelligence/dashboard-real-time-create)
- [HTML5 Canvas Games](https://developer.mozilla.org/en-US/docs/Games/Tutorials/2D_Breakout_game_pure_JavaScript)

## 🎮 Related Games

- 🚀 **Mission Artemis 2** - Advanced RTI with synchronized video
- ⚽ **Sports Tracker** - Analytics for team sports
- 🎯 **Target Practice** - RTI fundamentals in 5 minutes

---

*"Ready... Set... Stream!"* 🏁🏎️💨
