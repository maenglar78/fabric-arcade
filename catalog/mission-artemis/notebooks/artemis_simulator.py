# Databricks notebook source
# MAGIC %md
# MAGIC # 🚀 Mission Artemis - Telemetry Simulator
# MAGIC 
# MAGIC This notebook simulates spacecraft telemetry data for the Artemis mission.
# MAGIC It generates realistic sensor readings and sends them to your Eventstream.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📦 Setup

# COMMAND ----------

!pip install azure-eventhub faker -q

# COMMAND ----------

import json
import time
import random
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Generator
from concurrent.futures import ThreadPoolExecutor

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🛰️ Sensor Configuration

# COMMAND ----------

@dataclass
class Sensor:
    """Spacecraft sensor definition"""
    id: str
    name: str
    sensor_type: str
    unit: str
    min_value: float
    max_value: float
    normal_range: tuple
    critical_low: float
    critical_high: float

# Define spacecraft sensors
SENSORS = [
    Sensor("VEL-001", "Main Velocity", "velocity", "km/s", 0, 15, (5, 12), 2, 14),
    Sensor("FUEL-001", "Main Fuel Tank", "fuel_level", "%", 0, 100, (20, 100), 10, 105),
    Sensor("TEMP-001", "Hull Temperature", "temperature", "C", -200, 200, (-50, 80), -150, 150),
    Sensor("TEMP-002", "Engine Temperature", "temperature", "C", 0, 3000, (500, 2500), 100, 2800),
    Sensor("PRES-001", "Cabin Pressure", "pressure", "kPa", 0, 200, (90, 110), 80, 120),
    Sensor("RAD-001", "Radiation Level", "radiation", "mSv", 0, 100, (0, 20), -1, 50),
    Sensor("O2-001", "Oxygen Level", "oxygen", "%", 0, 100, (19, 23), 18, 25),
    Sensor("PWR-001", "Power Output", "power", "kW", 0, 500, (200, 450), 100, 480),
]

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🎲 Telemetry Generator

# COMMAND ----------

class TelemetryGenerator:
    """Generates realistic spacecraft telemetry"""
    
    def __init__(self, sensors: List[Sensor]):
        self.sensors = sensors
        self.mission_phase = "pre-launch"
        self.mission_start = None
        self.anomaly_probability = 0.001  # 0.1% chance of anomaly
        
        # Track sensor state for realistic progression
        self.sensor_states = {s.id: random.uniform(s.normal_range[0], s.normal_range[1]) 
                            for s in sensors}
    
    def set_mission_phase(self, phase: str):
        """Update mission phase (pre-launch, launch, cruise, orbit, landing)"""
        self.mission_phase = phase
        if phase == "launch" and not self.mission_start:
            self.mission_start = datetime.utcnow()
    
    def generate_reading(self, sensor: Sensor) -> dict:
        """Generate a single sensor reading with realistic variation"""
        
        # Get base value from state
        base_value = self.sensor_states[sensor.id]
        
        # Add phase-specific behavior
        if self.mission_phase == "launch":
            if sensor.sensor_type == "velocity":
                base_value = min(base_value + random.uniform(0.1, 0.5), sensor.max_value)
            elif sensor.sensor_type == "fuel_level":
                base_value = max(base_value - random.uniform(0.05, 0.2), sensor.min_value)
            elif sensor.sensor_type == "temperature" and "Engine" in sensor.name:
                base_value = min(base_value + random.uniform(10, 50), sensor.max_value)
        
        # Add random noise
        noise = random.gauss(0, (sensor.normal_range[1] - sensor.normal_range[0]) * 0.02)
        value = base_value + noise
        
        # Occasional anomaly
        if random.random() < self.anomaly_probability:
            value = random.choice([
                sensor.critical_low - random.uniform(1, 10),
                sensor.critical_high + random.uniform(1, 10)
            ])
            status = "CRITICAL"
        elif value < sensor.normal_range[0] or value > sensor.normal_range[1]:
            status = "WARNING"
        else:
            status = "NOMINAL"
        
        # Clamp to valid range
        value = max(sensor.min_value, min(sensor.max_value, value))
        
        # Update state
        self.sensor_states[sensor.id] = value
        
        return {
            "Timestamp": datetime.utcnow().isoformat() + "Z",
            "SensorId": sensor.id,
            "SensorName": sensor.name,
            "SensorType": sensor.sensor_type,
            "Value": round(value, 3),
            "Unit": sensor.unit,
            "Status": status,
            "MissionPhase": self.mission_phase
        }
    
    def generate_batch(self, batch_size: int = 100) -> List[dict]:
        """Generate a batch of readings from all sensors"""
        readings = []
        for _ in range(batch_size):
            for sensor in self.sensors:
                readings.append(self.generate_reading(sensor))
        return readings

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📡 Eventstream Configuration
# MAGIC 
# MAGIC Configure your Eventstream connection below.

# COMMAND ----------

# TODO: Replace with your Eventstream custom endpoint
EVENTSTREAM_ENDPOINT = "https://your-workspace.fabric.microsoft.com/eventstream/..."
EVENTSTREAM_KEY = "your-key-here"

# For local testing without Eventstream:
USE_LOCAL_MODE = True  # Set to False when connected to Fabric

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🚀 Launch Sequence

# COMMAND ----------

def run_mission(duration_minutes: int = 5, events_per_second: int = 100):
    """Run the mission simulation"""
    
    generator = TelemetryGenerator(SENSORS)
    total_events = 0
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    print("=" * 60)
    print("🚀 MISSION ARTEMIS - TELEMETRY SIMULATOR")
    print("=" * 60)
    print(f"Mission Duration: {duration_minutes} minutes")
    print(f"Events/second: {events_per_second}")
    print(f"Sensors: {len(SENSORS)}")
    print("=" * 60)
    
    # Mission phases timeline
    phase_schedule = [
        (0, "pre-launch"),
        (10, "launch"),
        (60, "cruise"),
        (180, "orbit"),
        (270, "landing"),
    ]
    
    phase_idx = 0
    
    try:
        while datetime.utcnow() < end_time:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Check for phase transition
            if phase_idx < len(phase_schedule) - 1:
                if elapsed >= phase_schedule[phase_idx + 1][0]:
                    phase_idx += 1
                    new_phase = phase_schedule[phase_idx][1]
                    generator.set_mission_phase(new_phase)
                    print(f"\n🎯 Phase Transition: {new_phase.upper()}")
            
            # Generate batch
            batch = generator.generate_batch(events_per_second // len(SENSORS))
            total_events += len(batch)
            
            # Send to Eventstream or print locally
            if USE_LOCAL_MODE:
                # Print summary every 5 seconds
                if int(elapsed) % 5 == 0:
                    anomalies = sum(1 for r in batch if r["Status"] == "CRITICAL")
                    warnings = sum(1 for r in batch if r["Status"] == "WARNING")
                    print(f"[{elapsed:.0f}s] Events: {total_events:,} | "
                          f"Phase: {generator.mission_phase} | "
                          f"⚠️ Warnings: {warnings} | 🚨 Critical: {anomalies}")
            else:
                # TODO: Send to Eventstream
                pass
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Mission aborted by user")
    
    print("\n" + "=" * 60)
    print("📊 MISSION SUMMARY")
    print("=" * 60)
    print(f"Total Events Generated: {total_events:,}")
    print(f"Duration: {(datetime.utcnow() - start_time).total_seconds():.1f} seconds")
    print(f"Final Phase: {generator.mission_phase}")
    print("=" * 60)
    
    return total_events

# COMMAND ----------

# MAGIC %md
# MAGIC ## ▶️ Start the Mission!
# MAGIC 
# MAGIC Run the cell below to begin generating telemetry.

# COMMAND ----------

# Start a 5-minute mission simulation
events = run_mission(duration_minutes=5, events_per_second=100)

print(f"\n🏆 Achievement Progress: {events:,} / 100,000 events for 'Lunar Orbit' badge")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📈 Sample Data Preview

# COMMAND ----------

# Generate sample data for preview
generator = TelemetryGenerator(SENSORS)
sample_batch = generator.generate_batch(10)

import pandas as pd
df = pd.DataFrame(sample_batch)
display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC 
# MAGIC ## 🎮 Next Steps
# MAGIC 
# MAGIC 1. ✅ Telemetry simulator running
# MAGIC 2. ⬜ Check your Eventstream for incoming data
# MAGIC 3. ⬜ Write KQL queries in the analytics notebook
# MAGIC 4. ⬜ Build the Mission Control dashboard
# MAGIC 
# MAGIC *"Houston, the data is flowing!"* 🚀
