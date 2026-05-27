"""
Fabric Arcade - Native Fabric API
Works inside Fabric notebooks using notebookutils
"""

import json
import time
import base64
import re
from typing import Dict, List, Optional
from pathlib import Path

# Try to import notebookutils (only available in Fabric)
try:
    from notebookutils import mssparkutils
    IN_FABRIC = True
except ImportError:
    IN_FABRIC = False

# Fabric REST API base
FABRIC_API = "https://api.fabric.microsoft.com/v1"


def _get_token() -> str:
    """Get access token for Fabric API"""
    if IN_FABRIC:
        return mssparkutils.credentials.getToken("https://api.fabric.microsoft.com")
    else:
        # Fallback for local testing
        from azure.identity import AzureCliCredential
        credential = AzureCliCredential()
        return credential.get_token("https://api.fabric.microsoft.com/.default").token


def _get_kusto_token() -> str:
    """Get access token for Kusto API"""
    if IN_FABRIC:
        return mssparkutils.credentials.getToken("https://kusto.kusto.windows.net")
    else:
        from azure.identity import AzureCliCredential
        credential = AzureCliCredential()
        return credential.get_token("https://kusto.kusto.windows.net/.default").token


def _api_call(method: str, url: str, json_data: dict = None) -> dict:
    """Make API call to Fabric"""
    import requests
    
    headers = {
        "Authorization": f"Bearer {_get_token()}",
        "Content-Type": "application/json"
    }
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=json_data)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Handle long-running operations
    if response.status_code == 202:
        return _wait_for_operation(response, headers)
    
    response.raise_for_status()
    return response.json() if response.text else {}


def _wait_for_operation(response, headers: dict, timeout: int = 300) -> dict:
    """Wait for long-running operation"""
    import requests
    
    operation_url = response.headers.get("Location")
    if not operation_url:
        return response.json() if response.text else {}
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        op_response = requests.get(operation_url, headers=headers)
        
        if op_response.status_code == 200:
            result = op_response.json()
            status = result.get("status", "").lower()
            
            if status == "succeeded":
                # Get result from Location header
                result_location = op_response.headers.get("Location")
                if result_location and "/result" in result_location:
                    result_response = requests.get(result_location, headers=headers)
                    if result_response.status_code == 200:
                        return result_response.json()
                return result
                
            elif status == "failed":
                raise Exception(f"Operation failed: {result}")
        
        time.sleep(2)
    
    raise TimeoutError("Operation timed out")


def _get_current_workspace() -> str:
    """Get current workspace ID (only works in Fabric)"""
    if IN_FABRIC:
        return mssparkutils.runtime.context.get("currentWorkspaceId")
    else:
        raise RuntimeError("Not running in Fabric. Please specify workspace_id.")


def _get_catalog() -> List[dict]:
    """Get game catalog from GitHub"""
    import requests
    
    catalog_url = "https://raw.githubusercontent.com/maenglar78/fabric-arcade/main/catalog_index.json"
    response = requests.get(catalog_url)
    
    if response.status_code == 200:
        return response.json().get("games", [])
    
    # Fallback to embedded catalog
    return [
        {
            "id": "fabric-racing-game",
            "name": "Fabric Racing Game",
            "description": "🏎️ HTML5 multiplayer racing game for 4 drivers with real-time telemetry",
            "workloads": ["RTI"],
            "difficulty": 2,
            "duration_minutes": 30,
            "icon": "🏎️"
        },
        {
            "id": "mission-artemis-2",
            "name": "Mission Artemis 2",
            "description": "🚀 Lunar mission with 4 astronauts and real-time telemetry",
            "workloads": ["RTI", "DE"],
            "difficulty": 3,
            "duration_minutes": 45,
            "icon": "🚀"
        }
    ]


def _get_game_assets(game_id: str) -> dict:
    """Download game assets from GitHub"""
    import requests
    
    base_url = f"https://raw.githubusercontent.com/maenglar78/fabric-arcade/main/catalog/{game_id}"
    
    # Get manifest
    manifest_response = requests.get(f"{base_url}/manifest.json")
    manifest_response.raise_for_status()
    manifest = manifest_response.json()
    
    # Get schemas
    schemas = {}
    for table in manifest.get("tables", []):
        schema_path = table.get("schema", "")
        if schema_path:
            schema_response = requests.get(f"{base_url}/{schema_path}")
            if schema_response.status_code == 200:
                schemas[table["name"]] = schema_response.text
    
    # Get notebooks
    notebooks = {}
    for item in manifest.get("items", []):
        if item.get("type") == "Notebook" and "file" in item:
            nb_response = requests.get(f"{base_url}/{item['file']}")
            if nb_response.status_code == 200:
                notebooks[item["name"]] = nb_response.text
    
    return {
        "manifest": manifest,
        "schemas": schemas,
        "notebooks": notebooks
    }


class Arcade:
    """Fabric Arcade - Browse and install games"""
    
    def __init__(self):
        self._catalog = None
    
    def list(self) -> None:
        """List all available games"""
        catalog = _get_catalog()
        
        print("🎮 Fabric Arcade - Available Games\n")
        print("-" * 60)
        
        for game in catalog:
            difficulty = "⭐" * game.get("difficulty", 1)
            duration = game.get("duration_minutes", 30)
            workloads = ", ".join(game.get("workloads", []))
            
            print(f"\n{game.get('icon', '🎮')} {game['name']}")
            print(f"   ID: {game['id']}")
            print(f"   {game.get('description', '')}")
            print(f"   Difficulty: {difficulty}  |  Duration: {duration} min")
            print(f"   Workloads: {workloads}")
        
        print("\n" + "-" * 60)
        print(f"\nTotal: {len(catalog)} games")
        print("\nUse arcade.install('game-id') to install a game")
    
    def info(self, game_id: str) -> None:
        """Show detailed info about a game"""
        catalog = _get_catalog()
        game = next((g for g in catalog if g["id"] == game_id), None)
        
        if not game:
            print(f"❌ Game '{game_id}' not found")
            return
        
        print(f"\n{game.get('icon', '🎮')} {game['name']}")
        print("=" * 50)
        print(f"\nID: {game['id']}")
        print(f"Description: {game.get('description', '')}")
        print(f"Difficulty: {'⭐' * game.get('difficulty', 1)}")
        print(f"Duration: {game.get('duration_minutes', 30)} minutes")
        print(f"Workloads: {', '.join(game.get('workloads', []))}")
        print("\n" + "=" * 50)
        print(f"\nTo install: arcade.install('{game_id}')")
    
    def install(self, game_id: str, workspace_id: str = None) -> None:
        """Install a game in the current workspace"""
        
        # Get workspace ID
        if workspace_id is None:
            try:
                workspace_id = _get_current_workspace()
                print(f"📍 Current workspace: {workspace_id[:8]}...")
            except RuntimeError:
                print("❌ Error: Specify workspace_id or run from a Fabric notebook")
                return
        
        print(f"\n🎮 Installing '{game_id}'...\n")
        
        # Download game assets
        try:
            print("📥 Downloading assets...")
            assets = _get_game_assets(game_id)
            manifest = assets["manifest"]
        except Exception as e:
            print(f"❌ Download error: {e}")
            return
        
        created_items = {}
        
        try:
            # 1. Create Eventhouse
            for item in manifest.get("items", []):
                if item["type"] == "Eventhouse":
                    print(f"  ⏳ Creating Eventhouse: {item['name']}...")
                    result = _api_call("POST", f"{FABRIC_API}/workspaces/{workspace_id}/items", {
                        "displayName": item["name"],
                        "type": "Eventhouse",
                        "description": f"Fabric Arcade - {item['name']}"
                    })
                    created_items[item["name"]] = result["id"]
                    print(f"    ✅ Created: {result['id'][:8]}...")
            
            # 2. Create KQL Database
            for item in manifest.get("items", []):
                if item["type"] == "KQLDatabase":
                    parent_id = created_items.get(item.get("parent"))
                    if not parent_id:
                        continue
                    
                    print(f"  ⏳ Creating KQL Database: {item['name']}...")
                    result = _api_call("POST", f"{FABRIC_API}/workspaces/{workspace_id}/items", {
                        "displayName": item["name"],
                        "type": "KQLDatabase",
                        "description": f"Fabric Arcade - {item['name']}",
                        "creationPayload": {
                            "databaseType": "ReadWrite",
                            "parentEventhouseItemId": parent_id
                        }
                    })
                    created_items[item["name"]] = result["id"]
                    created_items[f"{item['name']}_eventhouse"] = parent_id
                    print(f"    ✅ Created: {result['id'][:8]}...")
            
            # 3. Create tables
            print("  ⏳ Waiting for database to be ready...")
            time.sleep(5)
            
            for table in manifest.get("tables", []):
                db_name = table.get("database")
                db_id = created_items.get(db_name)
                schema = assets["schemas"].get(table["name"])
                
                if db_id and schema:
                    print(f"  ⏳ Creating table: {table['name']}...")
                    
                    # Get query URI
                    db_info = _api_call("GET", f"{FABRIC_API}/workspaces/{workspace_id}/kqlDatabases/{db_id}")
                    query_uri = db_info.get("properties", {}).get("queryServiceUri")
                    
                    if query_uri:
                        # Parse and execute KQL commands
                        commands = _parse_kql(schema)
                        for cmd in commands:
                            _execute_kql(query_uri, db_info["displayName"], cmd)
                        print(f"    ✅ Table created")
            
            # 4. Create Eventstream
            for item in manifest.get("items", []):
                if item["type"] == "Eventstream":
                    print(f"  ⏳ Creating Eventstream: {item['name']}...")
                    result = _api_call("POST", f"{FABRIC_API}/workspaces/{workspace_id}/items", {
                        "displayName": item["name"],
                        "type": "Eventstream",
                        "description": f"Fabric Arcade - {item['name']}"
                    })
                    created_items[item["name"]] = result["id"]
                    print(f"    ✅ Created: {result['id'][:8]}...")
                    print(f"    ⚠️ Configure manually: Custom Endpoint → KQL Database")
            
            # 5. Create Notebooks
            for item in manifest.get("items", []):
                if item["type"] == "Notebook":
                    nb_content = assets["notebooks"].get(item["name"])
                    if nb_content:
                        print(f"  ⏳ Creating Notebook: {item['name']}...")
                        
                        encoded = base64.b64encode(nb_content.encode()).decode()
                        result = _api_call("POST", f"{FABRIC_API}/workspaces/{workspace_id}/items", {
                            "displayName": item["name"],
                            "type": "Notebook",
                            "description": f"Fabric Arcade - {item['name']}",
                            "definition": {
                                "format": "ipynb",
                                "parts": [{
                                    "path": "notebook-content.ipynb",
                                    "payload": encoded,
                                    "payloadType": "InlineBase64"
                                }]
                            }
                        })
                        created_items[item["name"]] = result["id"]
                        print(f"    ✅ Created: {result['id'][:8]}...")
            
            # 6. Create README notebook with instructions
            print(f"  ⏳ Creating README notebook...")
            
            # Get game info for the notebook
            catalog = _get_catalog()
            game_info = next((g for g in catalog if g["id"] == game_id), {"name": game_id})
            
            readme_content = _create_readme_notebook(
                game_id, 
                game_info.get("name", game_id),
                manifest, 
                created_items
            )
            
            encoded_readme = base64.b64encode(readme_content.encode()).decode()
            readme_result = _api_call("POST", f"{FABRIC_API}/workspaces/{workspace_id}/items", {
                "displayName": f"{game_id}_README",
                "type": "Notebook",
                "description": f"Post-deploy guide for {game_info.get('name', game_id)}",
                "definition": {
                    "format": "ipynb",
                    "parts": [{
                        "path": "notebook-content.ipynb",
                        "payload": encoded_readme,
                        "payloadType": "InlineBase64"
                    }]
                }
            })
            created_items[f"{game_id}_README"] = readme_result["id"]
            print(f"    ✅ README created: {readme_result['id'][:8]}...")
            
            # Success!
            print(f"\n🎉 Installation complete!")
            print(f"   Created {len([k for k in created_items if not k.endswith('_eventhouse')])} items")
            print(f"\n📖 Next steps:")
            print(f"   1. Open the '{game_id}_README' notebook for complete instructions")
            print(f"   2. Configure the Eventstream (Custom Endpoint → KQL Database)")
            print(f"   3. Start the game from the main notebook!")
            
        except Exception as e:
            print(f"\n❌ Error during installation: {e}")
            raise


def _parse_kql(content: str) -> List[str]:
    """Parse KQL content into individual commands"""
    lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('//'):
            continue
        if '//' in line:
            line = line.split('//')[0]
        lines.append(line)
    
    content = '\n'.join(lines)
    commands = []
    current_cmd = []
    
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('.') and current_cmd:
            cmd = '\n'.join(current_cmd).strip()
            if cmd:
                commands.append(cmd)
            current_cmd = [line]
        elif stripped:
            current_cmd.append(line)
    
    if current_cmd:
        cmd = '\n'.join(current_cmd).strip()
        if cmd:
            commands.append(cmd)
    
    return commands


def _execute_kql(query_uri: str, database: str, command: str) -> dict:
    """Execute KQL management command"""
    import requests
    
    headers = {
        "Authorization": f"Bearer {_get_kusto_token()}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{query_uri}/v1/rest/mgmt",
        headers=headers,
        json={"csl": command, "db": database}
    )
    response.raise_for_status()
    return response.json()


def _create_readme_notebook(game_id: str, game_name: str, manifest: dict, created_items: dict) -> str:
    """Generate README notebook content with post-deploy instructions"""
    
    # Get game-specific instructions based on game_id
    if game_id == "fabric-racing-game":
        game_instructions = '''## 🏎️ How to Play

### Step 1: Configure the Eventstream
1. Open **RacingEventstream** in your workspace
2. Click **Edit** to enter edit mode
3. Add a **Custom Endpoint** source:
   - Name: `TelemetryInput`
   - This will create an HTTP endpoint to receive data
4. Add an **Eventhouse** destination:
   - Data ingestion mode: **Event processing before ingestion**
   - Workspace: **Your workspace**
   - Eventhouse: **RacingEventhouse**
   - KQL Database: **RaceData**
   - KQL Destination table: **GameEvents**
   - Input data format: **Json**
5. Connect Source → Destination and click **Publish**

### Step 2: Copy the Eventstream URL
1. After publishing, click on the Custom Endpoint Source
2. Copy the **Ingestion URL** (you'll need it in the game)

### Step 3: Start the Game
1. Open the **Racing_Championship** notebook
2. Paste the Eventstream URL in the configuration cell
3. Run all cells
4. The HTML5 game will open in your browser!

### Step 4: Play! 🎮
- **Arrow Keys**: Steer left/right
- **Collect ⭐** data points for bonus score
- **Avoid 🐛** bugs or lose points
- Reach the FINISH line with enough points to advance!'''

    elif game_id == "mission-artemis-2":
        game_instructions = '''## 🚀 How to Start the Mission

### Step 1: Configure the Eventstream
1. Open **ArtemisEventstream** in your workspace
2. Click **Edit** to enter edit mode
3. Add **4 Custom Endpoint Sources**:
   - `VehicleTelemetryInput`
   - `CrewVitalsInput`
   - `EnvironmentalInput`
   - `MissionEventsInput`
4. Add a **KQL Database Destination**:
   - Select **ArtemisEventhouse** → **MissionData**
5. Map each Source to its corresponding table
6. Click **Publish**

### Step 2: Start the Simulation
1. Open the **Artemis_Simulator** notebook
2. Configure the Eventstream Custom Endpoint URLs
3. Run the configuration cell
4. Start the simulation with `start_mission()`

### Step 3: Monitor from Mission Control
1. Open the **Mission_Control** notebook
2. Run the cells to visualize:
   - 📊 Real-time vehicle telemetry
   - 👨‍🚀 Crew vital signs
   - 🌡️ Environmental conditions
   - 📜 Mission event log
3. The mission video is synchronized with the data!

### Step 4: Analyze with KQL
Explore the data with KQL queries in the "KQL Queries" section below.'''

    else:
        game_instructions = '''## 🎮 How to Get Started

### Step 1: Configure the Eventstream
1. Open the Eventstream created in your workspace
2. Configure the appropriate data sources
3. Connect to the KQL Database
4. Click **Publish**

### Step 2: Start the Game
1. Open the main game notebook
2. Configure the required parameters
3. Run the cells in order

### Step 3: Have Fun!
Follow the instructions in the game notebook.'''

    # Build items list
    items_list = ""
    for name, item_id in created_items.items():
        if not name.endswith('_eventhouse'):
            items_list += f"- **{name}**: `{item_id[:8]}...`\n"

    # Build notebook JSON
    notebook_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    f"# 📖 {game_name} - Guida Post-Deploy\n",
                    "\n",
                    f"Benvenuto in **{game_name}**! Questa guida ti aiuterà a configurare e avviare il gioco.\n",
                    "\n",
                    "---"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## ✅ Items Creati\n",
                    "\n",
                    "I seguenti items sono stati creati nel tuo workspace:\n",
                    "\n",
                    items_list
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": game_instructions.split('\n')
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 🔍 Query KQL di Esempio\n",
                    "\n",
                    "Ecco alcune query KQL utili per esplorare i dati:"
                ]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Query KQL - Eseguile nel KQL Queryset o dal notebook\n",
                    "\n",
                    "# Ultimi 10 record\n",
                    "# Telemetry | take 10\n",
                    "\n",
                    "# Aggregazione per driver/astronauta\n",
                    "# Telemetry | summarize count() by DriverId\n",
                    "\n",
                    "# Serie temporale\n",
                    "# Telemetry | summarize avg(Speed) by bin(Timestamp, 1s) | render timechart"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 🆘 Troubleshooting\n",
                    "\n",
                    "### L'Eventstream non riceve dati\n",
                    "- Verifica che l'Eventstream sia in stato **Running**\n",
                    "- Controlla che l'URL del Custom Endpoint sia corretto\n",
                    "- Assicurati che il mapping Source → Destination sia configurato\n",
                    "\n",
                    "### Le tabelle KQL sono vuote\n",
                    "- Attendi qualche secondo dopo l'invio dei primi dati\n",
                    "- Verifica la connessione Eventstream → KQL Database\n",
                    "- Controlla i log dell'Eventstream per errori\n",
                    "\n",
                    "### Il notebook non si connette\n",
                    "- Verifica che il Lakehouse sia collegato al notebook\n",
                    "- Riavvia il kernel se necessario\n",
                    "\n",
                    "---\n",
                    "\n",
                    "## 🎮 Buon Divertimento!\n",
                    "\n",
                    "Per supporto: [GitHub Issues](https://github.com/maenglar78/fabric-arcade/issues)\n",
                    "\n",
                    "Per altri giochi: `from fabric_arcade import arcade; arcade.list()`"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    
    return json.dumps(notebook_content, indent=2, ensure_ascii=False)


# Create global instance for easy access
arcade = Arcade()
