# 🚀 Mission Artemis 2

> **Simula la missione Artemis 2 della NASA con telemetria real-time e video pixel art**

![Difficulty](https://img.shields.io/badge/Difficulty-Advanced-red)
![Duration](https://img.shields.io/badge/Duration-45%20min-blue)
![Workloads](https://img.shields.io/badge/Workloads-RTI%20%2B%20DE-green)

## 🎯 Mission Briefing

È il 2024. La NASA sta per lanciare **Artemis 2**, la prima missione con equipaggio verso la Luna dopo oltre 50 anni! 4 astronauti a bordo della capsula Orion partiranno da Cape Canaveral, orbiteranno attorno alla Luna nel suo cono d'ombra, e torneranno con uno splashdown nell'Oceano Pacifico.

**Il tuo compito**: costruire il sistema di telemetria real-time che monitorerà ogni istante della missione!

### 🎬 Il Concept
Un **video pixel art di ~4 minuti** accompagna la demo, mostrando:
- 4 astronauti stilizzati (uno biondo, uno alto e magro, uno robusto, uno basso)
- Il decollo da Cape Canaveral
- Il viaggio verso la Luna e l'orbita nel cono d'ombra
- Lo splashdown finale in mare

### 📡 Dati di Telemetria
La simulazione genera e trasmette in real-time:
- **Accelerazione** (G-force durante le varie fasi)
- **Pressione atmosferica** (interna cabina ed esterna)
- **Fasi del volo** (Pre-launch, Launch, Max-Q, MECO, TLI, Lunar Orbit, TEI, Re-entry, Splashdown)
- **Distanza dalla Terra e dalla Luna** (km)
- **Battito cardiaco** di ciascun astronauta (BPM)
- **Venti e condizioni ambientali** (velocità, direzione, temperatura)

## 🛠️ What You'll Learn

| Skill | Fabric Workload | Level |
|-------|-----------------|-------|
| Real-time data ingestion | Eventstream | ⭐⭐ |
| Time-series storage | Eventhouse | ⭐⭐ |
| KQL query language | KQL Database | ⭐⭐⭐ |
| Live dashboards | Real-Time Dashboard | ⭐⭐ |
| Data simulation | Spark Notebook | ⭐⭐ |
| Video sync with data | Custom App | ⭐⭐⭐ |

## 👨‍🚀 L'Equipaggio

| Astronauta | Caratteristica | Ruolo |
|------------|----------------|-------|
| 👱 Commander Reid | Biondo | Comandante missione |
| 🧍 Pilot Hansen | Alto e magro | Pilota |
| 💪 Specialist Torres | Robusto | Specialista di missione |
| 🧑 Engineer Kim | Basso | Ingegnere di bordo |

Ogni astronauta ha un sensore di battito cardiaco che trasmette in real-time!

## 📋 Prerequisites

- Microsoft Fabric workspace with F2+ capacity
- Basic Python knowledge
- Understanding of streaming data concepts

## 🚀 Quick Start

```python
import fabric_arcade as arcade

# Deploy the mission
arcade.install("mission-artemis-2")

# Start playing!
arcade.play("mission-artemis-2")
```

## 📖 Mission Chapters

### Chapter 1: Mission Prep 🔧
**Objective**: Set up the telemetry infrastructure

1. Create the Eventhouse `artemis2-telemetry`
2. Configure the KQL Database `mission-data`
3. Define tables for all sensor data:

**Schema Telemetria Veicolo**:
```kql
.create table VehicleTelemetry (
    Timestamp: datetime,
    MissionPhase: string,
    Acceleration_G: real,
    Velocity_KmH: real,
    Altitude_Km: real,
    DistanceFromEarth_Km: real,
    DistanceFromMoon_Km: real,
    PressureInternal_kPa: real,
    PressureExternal_kPa: real,
    Temperature_C: real
)

.create table CrewVitals (
    Timestamp: datetime,
    AstronautId: string,
    AstronautName: string,
    HeartRate_BPM: int,
    OxygenSaturation: real,
    StressLevel: string
)

.create table EnvironmentalConditions (
    Timestamp: datetime,
    WindSpeed_Knots: real,
    WindDirection_Deg: int,
    Temperature_C: real,
    Humidity_Pct: real,
    WeatherCondition: string
)

.create table MissionEvents (
    Timestamp: datetime,
    EventType: string,
    Phase: string,
    Description: string,
    VideoTimestamp_Sec: int
)
```

**Fasi della Missione**:
| Fase | Durata Video | Eventi |
|------|--------------|--------|
| Pre-Launch | 0:00-0:30 | Countdown, ignition |
| Launch | 0:30-1:00 | Liftoff, Max-Q, MECO |
| TLI | 1:00-1:30 | Trans-Lunar Injection |
| Cruise | 1:30-2:00 | Coast to Moon |
| Lunar Orbit | 2:00-3:00 | Orbit in shadow |
| TEI | 3:00-3:30 | Trans-Earth Injection |
| Re-entry | 3:30-3:50 | Atmosphere entry |
| Splashdown | 3:50-4:00 | Ocean landing |

### Chapter 2: Launch 🚀
**Objective**: Start streaming telemetry data synchronized with the video

1. Create Eventstream `artemis2-stream`
2. Configure custom endpoint for data ingestion
3. Run the simulator notebook that generates telemetry **sincronizzata con il video**:

```python
# Configurazione astronauti
CREW = [
    {"id": "CMD", "name": "Commander Reid", "emoji": "👱", "base_hr": 72},
    {"id": "PLT", "name": "Pilot Hansen", "emoji": "🧍", "base_hr": 68},
    {"id": "MS1", "name": "Specialist Torres", "emoji": "💪", "base_hr": 75},
    {"id": "MS2", "name": "Engineer Kim", "emoji": "🧑", "base_hr": 70},
]

# Fasi missione con timing video
MISSION_PHASES = [
    {"name": "Pre-Launch", "start": 0, "end": 30, "g_force": 1.0},
    {"name": "Launch", "start": 30, "end": 60, "g_force": 3.5},
    {"name": "Max-Q", "start": 45, "end": 50, "g_force": 4.0},
    {"name": "MECO", "start": 55, "end": 60, "g_force": 0.1},
    {"name": "TLI", "start": 60, "end": 90, "g_force": 1.5},
    {"name": "Cruise", "start": 90, "end": 120, "g_force": 0.0},
    {"name": "Lunar Orbit", "start": 120, "end": 180, "g_force": 0.0},
    {"name": "TEI", "start": 180, "end": 210, "g_force": 1.2},
    {"name": "Re-entry", "start": 210, "end": 230, "g_force": 6.0},
    {"name": "Splashdown", "start": 230, "end": 240, "g_force": 3.0},
]

# Distanze reali (scala per 4 minuti)
EARTH_MOON_DISTANCE = 384400  # km
```

### Chapter 3: In-Flight 📡
**Objective**: Monitor spacecraft health in real-time

Write KQL queries to answer critical questions:

**Query 1: Current Status**
```kql
SensorReadings
| where Timestamp > ago(1m)
| summarize LatestValue = arg_max(Timestamp, Value) by SensorId, SensorType
| project SensorType, Value = LatestValue, Timestamp
```

**Query 2: Anomaly Detection**
```kql
SensorReadings
| where Timestamp > ago(5m)
| summarize AvgValue = avg(Value), StdDev = stdev(Value) by SensorType
| join kind=inner (
    SensorReadings | where Timestamp > ago(1m)
) on SensorType
| where abs(Value - AvgValue) > 3 * StdDev
| project Timestamp, SensorType, Value, AvgValue, Deviation = abs(Value - AvgValue)
```

**Query 3: Mission Timeline**
```kql
MissionEvents
| order by Timestamp asc
| project Timestamp, Phase, EventType, Description
```

### Chapter 4: Landing 🏆
**Objective**: Complete the mission and analyze results

1. Build the Mission Control Dashboard with:
   - Live telemetry gauges for each sensor
   - Anomaly alert panel
   - Mission timeline visualization
   - Trajectory plot (if position data available)

2. Trigger a "landing" event and verify all systems
3. Run the final analysis notebook

## 🏅 Achievements

| Achievement | Requirement | Badge |
|-------------|-------------|-------|
| First Launch | Deploy and start streaming | 🚀 |
| Lunar Orbit | Process 100,000 events | 🌙 |
| Safe Landing | Complete all chapters | 🏆 |
| Anomaly Hunter | Detect 10 anomalies | 🔍 |
| Speed Demon | Complete in under 30 min | ⚡ |

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MISSION CONTROL CENTER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Notebook   │    │  Eventstream │    │  Eventhouse  │      │
│  │  Simulator   │───▶│   artemis-   │───▶│   artemis-   │      │
│  │              │    │   sensors    │    │  telemetry   │      │
│  └──────────────┘    └──────────────┘    └──────┬───────┘      │
│                                                  │               │
│                                                  ▼               │
│                                          ┌──────────────┐       │
│                                          │ KQL Database │       │
│                                          │  mission-    │       │
│                                          │    data      │       │
│                                          └──────┬───────┘       │
│                                                  │               │
│                                                  ▼               │
│                                          ┌──────────────┐       │
│                                          │ RT Dashboard │       │
│                                          │   mission-   │       │
│                                          │   control    │       │
│                                          └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔗 Resources

- [Fabric Real-Time Intelligence Docs](https://learn.microsoft.com/fabric/real-time-intelligence/)
- [KQL Quick Reference](https://learn.microsoft.com/azure/data-explorer/kql-quick-reference)
- [Eventstream Overview](https://learn.microsoft.com/fabric/real-time-intelligence/event-streams/overview)

## 🎮 Next Mission

Enjoyed Mission Artemis? Try these related games:
- 🏎️ **Race Analytics** - Apply your RTI skills to racing telemetry
- 🌊 **Ocean Explorer** - Combine RTI with ML for marine data
- 🚂 **Train Dispatch** - Quick RTI arcade challenge

---

*"Houston, we have a data pipeline!"* 🚀
