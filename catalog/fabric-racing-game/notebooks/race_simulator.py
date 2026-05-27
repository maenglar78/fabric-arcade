# Databricks notebook source
# MAGIC %md
# MAGIC # 🏎️ Fabric Racing Game - Deploy Notebook
# MAGIC 
# MAGIC This notebook automatically creates the entire FabricRacingGame workspace:
# MAGIC - Workspace with assigned capacity
# MAGIC - Eventhouse + KQL Database
# MAGIC - GameEvents table + JSON mapping
# MAGIC - Eventstream (Custom Endpoint → Eventhouse)
# MAGIC - 4 Player notebooks with HTML5 game

# COMMAND ----------

# MAGIC %md
# MAGIC ## ⚙️ Configuration

# COMMAND ----------

# PARAMETERS TO FILL IN
CAPACITY_ID = "<YOUR_CAPACITY_ID>"  # e.g.: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
WORKSPACE_NAME = "FabricRacingGame"

# Driver configuration
PLAYERS = [
    {"id": "P1", "name": "Red Racer", "color": "#FF0000", "emoji": "🔴"},
    {"id": "P2", "name": "Blue Bolt", "color": "#0000FF", "emoji": "🔵"},
    {"id": "P3", "name": "Green Machine", "color": "#00FF00", "emoji": "🟢"},
    {"id": "P4", "name": "Yellow Flash", "color": "#FFFF00", "emoji": "🟡"},
]

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📦 Step 1: Create Workspace

# COMMAND ----------

import requests
import json
import time
from notebookutils import mssparkutils

# Get access token
access_token = mssparkutils.credentials.getToken("https://api.fabric.microsoft.com")
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Create workspace
ws_payload = {
    "displayName": WORKSPACE_NAME,
    "capacityId": CAPACITY_ID
}

response = requests.post(
    "https://api.fabric.microsoft.com/v1/workspaces",
    headers=headers,
    json=ws_payload
)

if response.status_code in [200, 201]:
    workspace = response.json()
    WORKSPACE_ID = workspace["id"]
    print(f"✅ Workspace created: {WORKSPACE_NAME}")
    print(f"   ID: {WORKSPACE_ID}")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 Step 2: Create Eventhouse + KQL Database

# COMMAND ----------

# Create Eventhouse
eh_payload = {
    "displayName": "racing-events",
    "type": "Eventhouse"
}

response = requests.post(
    f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}/items",
    headers=headers,
    json=eh_payload
)

if response.status_code in [200, 201, 202]:
    # Polling for completion
    if response.status_code == 202:
        location = response.headers.get("Location")
        while True:
            poll = requests.get(location, headers=headers)
            if poll.status_code == 200:
                eventhouse = poll.json()
                break
            time.sleep(2)
    else:
        eventhouse = response.json()
    
    EVENTHOUSE_ID = eventhouse["id"]
    print(f"✅ Eventhouse created: racing-events")
    print(f"   ID: {EVENTHOUSE_ID}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📋 Step 3: Create GameEvents Table + Mapping

# COMMAND ----------

# Schema tabella GameEvents
CREATE_TABLE_KQL = """
.create table GameEvents (
    Timestamp: datetime,
    SessionId: string,
    PlayerId: string,
    PlayerName: string,
    EventType: string,
    PositionX: real,
    PositionY: real,
    Speed: real,
    LapNumber: int,
    LapTime: real,
    GameData: dynamic
)

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
"""

print("📋 Execute these KQL commands in the database:")
print(CREATE_TABLE_KQL)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🌊 Step 4: Create Eventstream

# COMMAND ----------

# Create Eventstream
es_payload = {
    "displayName": "racing-stream",
    "type": "Eventstream"
}

response = requests.post(
    f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}/items",
    headers=headers,
    json=es_payload
)

if response.status_code in [200, 201, 202]:
    if response.status_code == 202:
        location = response.headers.get("Location")
        while True:
            poll = requests.get(location, headers=headers)
            if poll.status_code == 200:
                eventstream = poll.json()
                break
            time.sleep(2)
    else:
        eventstream = response.json()
    
    EVENTSTREAM_ID = eventstream["id"]
    print(f"✅ Eventstream created: racing-stream")
    print(f"   ID: {EVENTSTREAM_ID}")
    print("")
    print("⚠️ MANUAL ACTION REQUIRED:")
    print("   1. Open the Eventstream in Fabric portal")
    print("   2. Add 'Custom Endpoint' as source")
    print("   3. Add 'Eventhouse' (racing-events) as destination")
    print("   4. Publish the Eventstream")
    print("   5. Copy the Custom Endpoint SAS URL")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🎮 Step 5: Create Player Notebooks

# COMMAND ----------

# Template HTML5 Game
HTML5_GAME_TEMPLATE = '''
# Fabric Racing Game - Player {player_id}

from IPython.display import HTML

# ⚠️ CONFIGURE THESE PARAMETERS
SAS_URL = "<EVENTSTREAM_CUSTOM_ENDPOINT_SAS>"
CLUSTER_URI = "<EVENTHOUSE_CLUSTER_URI>"

PLAYER_ID = "{player_id}"
PLAYER_NAME = "{player_name}"
PLAYER_COLOR = "{player_color}"

game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        canvas {{ border: 2px solid #333; background: #1a1a2e; }}
        .controls {{ font-family: Arial; margin: 10px 0; color: #fff; }}
    </style>
</head>
<body>
    <div class="controls">
        🎮 Controls: ⬆️ Accelerate | ⬇️ Brake | ⬅️➡️ Steer
    </div>
    <canvas id="raceCanvas" width="800" height="600"></canvas>
    <div id="telemetry" style="color:#0f0; font-family:monospace;"></div>
    
    <script>
        const canvas = document.getElementById('raceCanvas');
        const ctx = canvas.getContext('2d');
        const sessionId = 'race_' + Date.now();
        
        // Car state
        const car = {{
            x: 400, y: 500, angle: -90,
            speed: 0, maxSpeed: 8,
            lap: 0, lapTime: 0, lastLapTime: 0
        }};
        
        const keys = {{}};
        document.addEventListener('keydown', e => keys[e.key] = true);
        document.addEventListener('keyup', e => keys[e.key] = false);
        
        // Send telemetry
        function sendTelemetry(eventType) {{
            const event = {{
                timestamp: new Date().toISOString(),
                sessionId: sessionId,
                playerId: "{player_id}",
                playerName: "{player_name}",
                eventType: eventType,
                positionX: car.x,
                positionY: car.y,
                speed: car.speed * 25,
                lapNumber: car.lap,
                lapTime: car.lapTime / 1000,
                gameData: {{ angle: car.angle }}
            }};
            
            fetch("{SAS_URL}", {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(event)
            }}).catch(() => {{}});
        }}
        
        // Game loop
        let lastTime = Date.now();
        function gameLoop() {{
            const now = Date.now();
            const dt = now - lastTime;
            lastTime = now;
            car.lapTime += dt;
            
            // Controls
            if (keys['ArrowUp'] || keys['w']) car.speed = Math.min(car.speed + 0.1, car.maxSpeed);
            if (keys['ArrowDown'] || keys['s']) car.speed = Math.max(car.speed - 0.2, 0);
            if (keys['ArrowLeft'] || keys['a']) car.angle -= 3;
            if (keys['ArrowRight'] || keys['d']) car.angle += 3;
            
            // Physics
            car.speed *= 0.99;
            const rad = car.angle * Math.PI / 180;
            car.x += Math.cos(rad) * car.speed;
            car.y += Math.sin(rad) * car.speed;
            
            // Bounds
            car.x = Math.max(20, Math.min(780, car.x));
            car.y = Math.max(20, Math.min(580, car.y));
            
            // Draw
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, 800, 600);
            
            // Track
            ctx.strokeStyle = '#444';
            ctx.lineWidth = 60;
            ctx.beginPath();
            ctx.ellipse(400, 300, 300, 200, 0, 0, Math.PI * 2);
            ctx.stroke();
            
            // Car
            ctx.save();
            ctx.translate(car.x, car.y);
            ctx.rotate(rad);
            ctx.fillStyle = '{player_color}';
            ctx.fillRect(-15, -10, 30, 20);
            ctx.restore();
            
            // HUD
            ctx.fillStyle = '#fff';
            ctx.font = '20px Arial';
            ctx.fillText('🏎️ ' + '{player_name}', 10, 30);
            ctx.fillText('Lap: ' + car.lap, 10, 55);
            ctx.fillText('Speed: ' + Math.round(car.speed * 25) + ' km/h', 10, 80);
            
            // Telemetry display
            document.getElementById('telemetry').innerHTML = 
                '📡 Telemetry: X=' + Math.round(car.x) + ' Y=' + Math.round(car.y) + 
                ' Speed=' + Math.round(car.speed * 25);
            
            requestAnimationFrame(gameLoop);
        }}
        
        // Start
        sendTelemetry('start');
        setInterval(() => sendTelemetry('position'), 100);
        gameLoop();
    </script>
</body>
</html>
"""

HTML(game_html)
'''

# Create the 4 player notebooks
for player in PLAYERS:
    notebook_content = HTML5_GAME_TEMPLATE.format(
        player_id=player["id"],
        player_name=player["name"],
        player_color=player["color"]
    )
    
    nb_payload = {
        "displayName": f"Race_{player['id']}",
        "type": "Notebook"
    }
    
    response = requests.post(
        f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}/items",
        headers=headers,
        json=nb_payload
    )
    
    if response.status_code in [200, 201, 202]:
        print(f"✅ Notebook created: Race_{player['id']} {player['emoji']}")
    else:
        print(f"⚠️ Notebook Race_{player['id']}: create manually")

print("")
print(f"🎮 Copy the HTML5 code into each notebook")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Deploy Complete!
# MAGIC 
# MAGIC ### Remaining manual steps:
# MAGIC 
# MAGIC 1. **Eventstream**: Open, configure Custom Endpoint → Eventhouse, Publish
# MAGIC 2. **KQL Database**: Run the commands to create GameEvents + mapping
# MAGIC 3. **Notebooks**: Update SAS_URL and CLUSTER_URI in all 4
# MAGIC 4. **Test**: Start a race and verify data in KQL
# MAGIC 
# MAGIC ```kql
# MAGIC // Test query
# MAGIC GameEvents
# MAGIC | where Timestamp > ago(5m)
# MAGIC | summarize count() by PlayerId, EventType
# MAGIC ```

# COMMAND ----------

# Resources summary
print("=" * 50)
print("🏁 FABRIC RACING GAME - DEPLOY SUMMARY")
print("=" * 50)
print(f"Workspace:   {WORKSPACE_NAME}")
print(f"Eventhouse:  racing-events")
print(f"Eventstream: racing-stream")
print(f"Database:    race-data")
print(f"Table:       GameEvents (11 columns)")
print(f"Notebooks:   Race_P1, Race_P2, Race_P3, Race_P4")
print("=" * 50)
print("🎮 Ready to race!")

    
    def __init__(self, drivers: List[Driver], total_laps: int = 50):
        self.total_laps = total_laps
        self.current_lap = 0
        self.base_lap_time = timedelta(seconds=85)  # ~1:25 base lap
        
        # Initialize cars on grid (reverse skill order for realism)
        sorted_drivers = sorted(drivers, key=lambda d: d.skill_level, reverse=True)
        self.cars = [Car(driver=d, position=i+1, tire_compound="Medium") 
                     for i, d in enumerate(sorted_drivers)]
        
        self.events = []  # Race events (pit stops, retirements, etc.)
        
    def simulate_lap(self) -> List[Dict]:
        """Simulate one lap for all cars"""
        self.current_lap += 1
        lap_data = []
        
        for car in self.cars:
            if car.is_retired:
                continue
                
            # Check for pit stop decision
            if self._should_pit(car):
                pit_event = self._do_pit_stop(car)
                self.events.append(pit_event)
            
            # Calculate lap time
            lap_time = self._calculate_lap_time(car)
            sectors = self._split_into_sectors(lap_time)
            
            # Update car state
            car.lap = self.current_lap
            car.total_time += lap_time
            car.tire_age += 1
            car.tire_wear = self._calculate_tire_wear(car)
            car.fuel_level = max(0, car.fuel_level - (100 / self.total_laps))
            
            # Random retirement chance
            if random.random() < 0.001:  # 0.1% per lap
                car.is_retired = True
                self.events.append({
                    "type": "retirement",
                    "driver_id": car.driver.id,
                    "lap": self.current_lap,
                    "reason": random.choice(["Engine failure", "Gearbox issue", "Hydraulics"])
                })
                continue
            
            lap_data.append({
                "Timestamp": datetime.utcnow().isoformat() + "Z",
                "DriverId": car.driver.id,
                "DriverName": car.driver.name,
                "Team": car.driver.team,
                "TeamColor": car.driver.team_color,
                "LapNumber": self.current_lap,
                "LapTime": lap_time.total_seconds(),
                "LapTimeFormatted": self._format_time(lap_time),
                "Sector1": sectors[0].total_seconds(),
                "Sector2": sectors[1].total_seconds(),
                "Sector3": sectors[2].total_seconds(),
                "Position": car.position,
                "TireCompound": car.tire_compound,
                "TireAge": car.tire_age,
                "TireWear": round(car.tire_wear, 1),
                "FuelLevel": round(car.fuel_level, 1),
                "PitStops": car.pit_stops
            })
        
        # Update positions based on total time
        self._update_positions()
        
        # Add gap to leader
        leader_time = min(c.total_time for c in self.cars if not c.is_retired)
        for data in lap_data:
            car = next(c for c in self.cars if c.driver.id == data["DriverId"])
            gap = (car.total_time - leader_time).total_seconds()
            data["GapToLeader"] = gap
            data["GapFormatted"] = f"+{gap:.3f}s" if gap > 0 else "LEADER"
            data["Position"] = car.position
        
        return lap_data
    
    def _calculate_lap_time(self, car: Car) -> timedelta:
        """Calculate lap time based on driver skill and car state"""
        base = self.base_lap_time.total_seconds()
        
        # Driver skill factor
        skill_factor = 1 - (car.driver.skill_level * 0.03)  # Up to 3% faster
        
        # Consistency variation
        consistency_var = random.gauss(0, (1 - car.driver.consistency) * 0.5)
        
        # Tire compound effect
        tire_info = TIRE_COMPOUNDS[car.tire_compound]
        tire_pace = 1 - tire_info["pace_bonus"]
        
        # Tire wear effect (quadratic degradation)
        wear_factor = 1 + (car.tire_wear / 100) ** 2 * 0.05
        
        # Fuel load effect (lighter = faster)
        fuel_factor = 1 - (1 - car.fuel_level / 100) * 0.015
        
        # Calculate final lap time
        lap_seconds = base * skill_factor * tire_pace * wear_factor * fuel_factor
        lap_seconds += consistency_var
        
        return timedelta(seconds=max(80, lap_seconds))  # Minimum 1:20
    
    def _split_into_sectors(self, lap_time: timedelta) -> List[timedelta]:
        """Split lap time into 3 sectors with variation"""
        total = lap_time.total_seconds()
        s1_pct = random.uniform(0.30, 0.35)
        s2_pct = random.uniform(0.32, 0.37)
        s3_pct = 1 - s1_pct - s2_pct
        
        return [
            timedelta(seconds=total * s1_pct),
            timedelta(seconds=total * s2_pct),
            timedelta(seconds=total * s3_pct)
        ]
    
    def _calculate_tire_wear(self, car: Car) -> float:
        """Calculate cumulative tire wear"""
        degradation = TIRE_COMPOUNDS[car.tire_compound]["degradation"]
        management = car.driver.tire_management
        
        # Wear increases with each lap, affected by driver skill
        lap_wear = degradation * (2 - management) * 100
        return min(100, car.tire_wear + lap_wear)
    
    def _should_pit(self, car: Car) -> bool:
        """Decide if car should pit"""
        # Pit if tires are heavily worn
        if car.tire_wear > 80:
            return True
        
        # Strategy-based pit windows
        if car.pit_stops == 0 and self.current_lap in range(15, 25):
            return random.random() < 0.15
        if car.pit_stops == 1 and self.current_lap in range(35, 45):
            return random.random() < 0.10
            
        return False
    
    def _do_pit_stop(self, car: Car) -> Dict:
        """Execute pit stop"""
        pit_time = timedelta(seconds=random.uniform(22, 28))  # 22-28 second pit
        car.total_time += pit_time
        car.pit_stops += 1
        
        # Choose new compound
        old_compound = car.tire_compound
        if car.pit_stops == 1:
            car.tire_compound = random.choice(["Hard", "Medium"])
        else:
            car.tire_compound = random.choice(["Soft", "Medium"])
        
        car.tire_age = 0
        car.tire_wear = 0
        
        return {
            "type": "pit_stop",
            "Timestamp": datetime.utcnow().isoformat() + "Z",
            "DriverId": car.driver.id,
            "DriverName": car.driver.name,
            "LapNumber": self.current_lap,
            "Duration": pit_time.total_seconds(),
            "TireCompoundIn": old_compound,
            "TireCompoundOut": car.tire_compound
        }
    
    def _update_positions(self):
        """Update race positions based on total time"""
        active_cars = sorted(
            [c for c in self.cars if not c.is_retired],
            key=lambda c: c.total_time
        )
        for i, car in enumerate(active_cars):
            car.position = i + 1
        
        # Retired cars get position after active
        for car in self.cars:
            if car.is_retired:
                car.position = len(active_cars) + 1
    
    def _format_time(self, td: timedelta) -> str:
        """Format timedelta as m:ss.fff"""
        total_seconds = td.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:06.3f}"
    
    def get_standings(self) -> List[Dict]:
        """Get current race standings"""
        standings = []
        for car in sorted(self.cars, key=lambda c: c.position):
            standings.append({
                "Position": car.position,
                "Driver": car.driver.name,
                "Team": car.driver.team,
                "Laps": car.lap,
                "TotalTime": self._format_time(car.total_time),
                "Tire": f"{TIRE_COMPOUNDS[car.tire_compound]['color']} {car.tire_compound}",
                "Status": "Retired" if car.is_retired else "Running"
            })
        return standings

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🚦 Race Control

# COMMAND ----------

def run_race(total_laps: int = 50, speed_multiplier: float = 1.0):
    """Run a complete race simulation"""
    
    sim = RaceSimulator(DRIVERS, total_laps)
    all_lap_data = []
    all_pit_stops = []
    
    print("=" * 70)
    print("🏁 GRAND PRIX - RACE START")
    print("=" * 70)
    print(f"Total Laps: {total_laps}")
    print(f"Drivers: {len(DRIVERS)}")
    print("=" * 70)
    print()
    
    try:
        for lap in range(1, total_laps + 1):
            lap_data = sim.simulate_lap()
            all_lap_data.extend(lap_data)
            
            # Collect pit stops
            for event in sim.events:
                if event.get("type") == "pit_stop" and event.get("LapNumber") == lap:
                    all_pit_stops.append(event)
                    print(f"  🔧 PIT: {event['DriverName']} - "
                          f"{event['TireCompoundIn']} → {event['TireCompoundOut']} "
                          f"({event['Duration']:.1f}s)")
            
            # Print standings every 5 laps
            if lap % 5 == 0 or lap == 1:
                print(f"\n📊 Lap {lap}/{total_laps}")
                print("-" * 50)
                standings = sim.get_standings()[:5]
                for s in standings:
                    print(f"  P{s['Position']}: {s['Driver']:<20} {s['Tire']} "
                          f"({s['Status']})")
            
            time.sleep(0.5 / speed_multiplier)
    
    except KeyboardInterrupt:
        print("\n\n🚩 RED FLAG - Race stopped")
    
    print("\n" + "=" * 70)
    print("🏆 FINAL STANDINGS")
    print("=" * 70)
    for s in sim.get_standings():
        status = "🏁" if s["Status"] == "Running" else "❌"
        print(f"  {status} P{s['Position']:>2}: {s['Driver']:<20} {s['Team']:<15} "
              f"Laps: {s['Laps']}")
    
    print("\n" + "=" * 70)
    print("📈 RACE STATISTICS")
    print("=" * 70)
    print(f"Total lap records: {len(all_lap_data):,}")
    print(f"Total pit stops: {len(all_pit_stops)}")
    
    return all_lap_data, all_pit_stops

# COMMAND ----------

# MAGIC %md
# MAGIC ## ▶️ Start the Race!

# COMMAND ----------

# Run a 20-lap sprint race (for testing)
lap_data, pit_stops = run_race(total_laps=20, speed_multiplier=2.0)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 Data Preview

# COMMAND ----------

import pandas as pd

# Lap times
df_laps = pd.DataFrame(lap_data)
print(f"Lap data shape: {df_laps.shape}")
display(df_laps.head(20))

# COMMAND ----------

# Pit stops
df_pits = pd.DataFrame(pit_stops)
if not df_pits.empty:
    print(f"Pit stops: {len(df_pits)}")
    display(df_pits)
else:
    print("No pit stops recorded")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC 
# MAGIC ## 🎮 Next Steps
# MAGIC 
# MAGIC 1. ✅ Race simulator working
# MAGIC 2. ⬜ Connect to Eventstream
# MAGIC 3. ⬜ Write KQL queries for live leaderboard
# MAGIC 4. ⬜ Build Power BI race report
# MAGIC 
# MAGIC *"And it's lights out and away we go!"* 🏁
