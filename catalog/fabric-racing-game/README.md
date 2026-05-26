# 🏎️ Fabric Racing Game

> **Un gioco di corse HTML5 multiplayer con telemetria real-time su Microsoft Fabric**

![Difficulty](https://img.shields.io/badge/Difficulty-Intermediate-orange)
![Duration](https://img.shields.io/badge/Duration-30%20min-blue)
![Workloads](https://img.shields.io/badge/Workloads-RTI-green)

## 🏁 Race Briefing

Benvenuto al **Fabric Racing Championship**! Un vero gioco di corse HTML5 per **4 giocatori**, dove ogni partita genera telemetria real-time che fluisce attraverso l'architettura Fabric Real-Time Intelligence.

Ogni giocatore ha il proprio notebook con il gioco integrato. Mentre giocano, gli eventi di gara (posizione, velocità, collisioni, giri) vengono inviati in real-time all'Eventhouse per analytics live!

### 🎮 Il Concept
- **4 Notebook HTML5** - Uno per ogni pilota (Race_P1, Race_P2, Race_P3, Race_P4)
- **Gioco arcade** - Controlli semplici, grafica retrò, massimo divertimento
- **Telemetria real-time** - Ogni azione genera eventi verso l'Eventstream
- **Dashboard live** - Visualizza la gara in tempo reale con KQL

## 🛠️ What You'll Learn

| Skill | Fabric Workload | Level |
|-------|-----------------|-------|
| Custom Endpoint ingestion | Eventstream | ⭐⭐ |
| JSON data mapping | KQL Database | ⭐⭐ |
| Real-time queries | Eventhouse | ⭐⭐ |
| HTML5 in notebooks | Notebook | ⭐⭐ |
| Live dashboards | Real-Time Dashboard | ⭐⭐ |

## 🏗️ Architettura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FABRIC RACING GAME                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                       │
│  │ Race_P1  │ │ Race_P2  │ │ Race_P3  │ │ Race_P4  │  ← 4 Notebook HTML5   │
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
│                 │  KQL Database   │  ← Tabella GameEvents                   │
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

- Microsoft Fabric workspace con F2+ capacity
- 4 persone per giocare (o testa da solo con più browser!)

## 🏎️ Quick Start

```python
import fabric_arcade as arcade

# Deploy automatico del workspace completo
arcade.install("fabric-racing-game")

# Il notebook di deploy crea tutto:
# 1. Workspace con capacity
# 2. Eventhouse + KQL Database
# 3. Tabella GameEvents + JSON mapping
# 4. Eventstream (Custom Endpoint)
# 5. I 4 notebook giocatore con gioco HTML5
```

## 📖 Race Chapters

### 🔧 Qualifying: Setup KQL Database

Crea la tabella **GameEvents** nel KQL Database con 11 colonne per tutti i tipi di eventi:

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
    GameData: dynamic       // Dati extra in JSON
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

1. Crea l'Eventstream `racing-stream`
2. Configura **Custom Endpoint** come source
3. Aggiungi **Eventhouse** come destination
4. **Pubblica** l'Eventstream nel portale Fabric

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

Ogni notebook contiene un gioco HTML5 completo con:
- **Pista 2D** con curve e rettilineo
- **4 auto colorate** (🔴 Red, 🔵 Blue, 🟢 Green, 🟡 Yellow)
- **Controlli** con tastiera (frecce o WASD)
- **Telemetria** inviata ogni 100ms al Custom Endpoint

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

// Game loop - invia telemetria ogni 100ms
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

Crea una **Real-Time Dashboard** con:

1. **Leaderboard Panel** - Posizioni in tempo reale
2. **Speed Chart** - Velocità di ogni giocatore
3. **Lap Times Grid** - Confronto tempi sul giro
4. **Track Map** - Posizione auto sulla pista

## 🛠️ Configurazione Post-Deploy

| Step | Azione | Dove |
|------|--------|------|
| 1 | Compila CAPACITY_ID nel notebook deploy | Deploy_FabricRacingGame |
| 2 | Pubblica l'Eventstream | Portale Fabric |
| 3 | Copia SAS URL nei 4 notebook | Race_P1 - Race_P4 |
| 4 | Aggiorna CLUSTER_URI | Tutti i notebook |
| 5 | Test con query KQL | KQL Database |

## 🏅 Achievements

| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| First Start | Lancia la prima gara | 🏁 |
| Full Grid | 4 giocatori connessi contemporaneamente | 👥 |
| Photo Finish | Arrivo entro 0.5s di distacco | 📸 |
| Speed Demon | Raggiungi velocità max > 200 | ⚡ |
| Clean Race | Completa 5 giri senza collisioni | 🧹 |
| Champion | Vinci 3 gare di fila | 🏆 |

## 🎮 I 4 Piloti

| Notebook | Giocatore | Colore | Emoji |
|----------|-----------|--------|-------|
| Race_P1 | Red Racer | 🔴 #FF0000 | 🏎️ |
| Race_P2 | Blue Bolt | 🔵 #0000FF | 🚙 |
| Race_P3 | Green Machine | 🟢 #00FF00 | 🚗 |
| Race_P4 | Yellow Flash | 🟡 #FFFF00 | 🚕 |

## 📁 Contenuto del Deploy

Il notebook **Deploy_FabricRacingGame** (10 celle) crea automaticamente:

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

- 🚀 **Mission Artemis 2** - RTI avanzato con video sincronizzato
- ⚽ **Sports Tracker** - Analytics per sport di squadra
- 🎯 **Target Practice** - Fondamentali RTI in 5 minuti

---

*"Ready... Set... Stream!"* 🏁🏎️💨
