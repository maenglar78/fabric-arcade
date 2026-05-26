# 🚀 Mission Artemis 2

[← Back to catalog](index.md)

---

## Overview

| | |
|---|---|
| **Type** | Accelerator |
| **Difficulty** | Advanced |
| **Deploy Time** | ~5 min |
| **Complete Time** | ~45 min |

Experience a lunar mission with 4 astronauts! Stream real-time telemetry synchronized with a 4-minute mission video. Learn multi-table streaming architecture, IoT data patterns, and real-time correlation analysis.

---

## Workloads

- **Real-Time Intelligence** - Multi-stream telemetry processing
- **Data Engineering** - Complex data transformations

---

## Fabric Items Deployed

| Icon | Item Type | Name | Description |
|------|-----------|------|-------------|
| 🏠 | Eventhouse | ArtemisEventhouse | Container for mission data |
| 📊 | KQL Database | MissionData | Stores all telemetry streams |
| 📋 | KQL Table | VehicleTelemetry | Rocket acceleration, altitude, velocity |
| 📋 | KQL Table | CrewVitals | Astronaut heart rate, blood pressure |
| 📋 | KQL Table | EnvironmentalConditions | Cabin pressure, temperature, O2 levels |
| 📋 | KQL Table | MissionEvents | Flight phase transitions, alerts |
| 🌊 | Eventstream | ArtemisStream | Multi-input streaming pipeline |
| 📓 | Notebook | Artemis_Simulator | Generates mission telemetry |
| 📓 | Notebook | Mission_Control | Dashboard with embedded video |

---

## Scenarios

- **Streaming** - Multi-source real-time data ingestion
- **IoT Telemetry** - Sensor data patterns and time-series analysis
- **Video Synchronization** - Correlate video timeline with data events
- **Monitoring** - Real-time alerting on threshold conditions

---

## Quick Start

### Step 1: Install in your Fabric Notebook

```python
# Cell 1 - Install the package
%pip install -q fabric-arcade
```

```python
# Cell 2 - Import and install the mission
from fabric_arcade import arcade

# Install Mission Artemis 2 in your current workspace
arcade.install("mission-artemis-2")
```

### Step 2: Start the Mission Simulation

1. Navigate to your workspace
2. Open the **Artemis_Simulator** notebook
3. Run all cells to begin telemetry generation

### Step 3: Open Mission Control

1. Open the **Mission_Control** notebook
2. Run all cells to display the mission dashboard
3. Watch telemetry update in sync with the mission video!

---

## ✨ Key Features

- 🚀 **Realistic Lunar Mission** - Based on actual Apollo/Artemis mission profiles
- 👨‍🚀 **4 Crew Members** - Individual vital signs for each astronaut
- 📡 **Multi-Table Architecture** - Learn how to design streaming data models
- 🎬 **Video Sync** - Correlate data events with mission video timeline
- ⚠️ **Real-Time Alerts** - Threshold monitoring with visual indicators
- 📊 **Time-Series Analysis** - KQL patterns for temporal data

---

## 🏛️ Solution Architecture

```
                    ┌──────────────────────────────────────┐
                    │         Artemis Simulator            │
                    │  (Notebook generating telemetry)     │
                    └──────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
    ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
    │   Vehicle     │      │    Crew       │      │ Environmental │
    │  Telemetry    │      │   Vitals      │      │  Conditions   │
    └───────────────┘      └───────────────┘      └───────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    ▼
                    ┌──────────────────────────────────────┐
                    │           Eventstream                │
                    │    (Multi-input Custom Endpoints)    │
                    └──────────────────────────────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────────────┐
                    │           Eventhouse                 │
                    │  ┌────────────────────────────────┐  │
                    │  │       KQL Database             │  │
                    │  │  • VehicleTelemetry            │  │
                    │  │  • CrewVitals                  │  │
                    │  │  • EnvironmentalConditions     │  │
                    │  │  • MissionEvents               │  │
                    │  └────────────────────────────────┘  │
                    └──────────────────────────────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────────────┐
                    │         Mission Control              │
                    │   (Dashboard + Embedded Video)       │
                    └──────────────────────────────────────┘
```

### Data Tables

| Table | Frequency | Fields |
|-------|-----------|--------|
| VehicleTelemetry | 10 Hz | Timestamp, Altitude, Velocity, Acceleration, Fuel, Phase |
| CrewVitals | 1 Hz | Timestamp, AstronautId, HeartRate, BloodPressure, O2Saturation |
| EnvironmentalConditions | 1 Hz | Timestamp, CabinPressure, Temperature, O2Level, CO2Level |
| MissionEvents | Event-driven | Timestamp, EventType, Description, Severity |

---

## 📦 Prerequisites

### Required
- **Microsoft Fabric Capacity** - F4 or higher recommended
- **Fabric Workspace** - A workspace with Contributor permissions

### Recommended Knowledge
- Basic understanding of Fabric Eventstream and Eventhouse
- Familiarity with KQL (Kusto Query Language)
- Understanding of time-series data concepts

---

## 📖 Usage Instructions

### Mission Phases

The simulation covers 5 mission phases over ~4 minutes:

1. **Launch** (0:00 - 0:45) - Liftoff and initial ascent
2. **Max-Q** (0:45 - 1:15) - Maximum dynamic pressure
3. **Orbit Insertion** (1:15 - 2:00) - Reaching stable orbit
4. **Trans-Lunar Injection** (2:00 - 3:00) - Burn to lunar trajectory
5. **Coast Phase** (3:00 - 4:00) - Cruising toward the Moon

### Monitoring Astronaut Health

Query crew vitals in KQL:

```kql
CrewVitals
| where Timestamp > ago(1m)
| summarize 
    AvgHeartRate = avg(HeartRate),
    MaxHeartRate = max(HeartRate)
    by AstronautId
| order by AvgHeartRate desc
```

### Detecting Anomalies

Set up threshold alerts:

```kql
VehicleTelemetry
| where Acceleration > 4.0  // > 4G warning
| project Timestamp, Acceleration, Phase
```

---

## 🔧 Troubleshooting

### Telemetry not flowing
- Ensure the Artemis_Simulator notebook is running
- Check that the Eventstream shows active connections
- Verify Custom Endpoint URLs in the simulator

### Video out of sync
- Reset both notebooks and start fresh
- Ensure your machine clock is accurate
- The video uses relative timestamps from simulation start

### High latency in dashboard
- Check Eventhouse ingestion latency
- Reduce query time ranges for faster response
- Consider creating materialized views for common queries

---

## 📄 License

MIT License - This project is provided for demonstration and educational purposes.

---

[← Back to catalog](index.md)
