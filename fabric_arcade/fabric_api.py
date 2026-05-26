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
            "description": "🏎️ Un gioco HTML5 multiplayer per 4 piloti con telemetria real-time",
            "workloads": ["RTI"],
            "difficulty": 2,
            "duration_minutes": 30,
            "icon": "🏎️"
        },
        {
            "id": "mission-artemis-2",
            "name": "Mission Artemis 2",
            "description": "🚀 Missione lunare con 4 astronauti e telemetria real-time",
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
        
        print("🎮 Fabric Arcade - Giochi Disponibili\n")
        print("-" * 60)
        
        for game in catalog:
            difficulty = "⭐" * game.get("difficulty", 1)
            duration = game.get("duration_minutes", 30)
            workloads = ", ".join(game.get("workloads", []))
            
            print(f"\n{game.get('icon', '🎮')} {game['name']}")
            print(f"   ID: {game['id']}")
            print(f"   {game.get('description', '')}")
            print(f"   Difficoltà: {difficulty}  |  Durata: {duration} min")
            print(f"   Workloads: {workloads}")
        
        print("\n" + "-" * 60)
        print(f"\nTotale: {len(catalog)} giochi")
        print("\nUsa arcade.install('game-id') per installare un gioco")
    
    def info(self, game_id: str) -> None:
        """Show detailed info about a game"""
        catalog = _get_catalog()
        game = next((g for g in catalog if g["id"] == game_id), None)
        
        if not game:
            print(f"❌ Gioco '{game_id}' non trovato")
            return
        
        print(f"\n{game.get('icon', '🎮')} {game['name']}")
        print("=" * 50)
        print(f"\nID: {game['id']}")
        print(f"Descrizione: {game.get('description', '')}")
        print(f"Difficoltà: {'⭐' * game.get('difficulty', 1)}")
        print(f"Durata: {game.get('duration_minutes', 30)} minuti")
        print(f"Workloads: {', '.join(game.get('workloads', []))}")
        print("\n" + "=" * 50)
        print(f"\nPer installare: arcade.install('{game_id}')")
    
    def install(self, game_id: str, workspace_id: str = None) -> None:
        """Install a game in the current workspace"""
        
        # Get workspace ID
        if workspace_id is None:
            try:
                workspace_id = _get_current_workspace()
                print(f"📍 Workspace corrente: {workspace_id[:8]}...")
            except RuntimeError:
                print("❌ Errore: Specifica workspace_id o esegui da un notebook Fabric")
                return
        
        print(f"\n🎮 Installazione '{game_id}'...\n")
        
        # Download game assets
        try:
            print("📥 Download assets...")
            assets = _get_game_assets(game_id)
            manifest = assets["manifest"]
        except Exception as e:
            print(f"❌ Errore download: {e}")
            return
        
        created_items = {}
        
        try:
            # 1. Create Eventhouse
            for item in manifest.get("items", []):
                if item["type"] == "Eventhouse":
                    print(f"  ⏳ Creazione Eventhouse: {item['name']}...")
                    result = _api_call("POST", f"{FABRIC_API}/workspaces/{workspace_id}/items", {
                        "displayName": item["name"],
                        "type": "Eventhouse",
                        "description": f"Fabric Arcade - {item['name']}"
                    })
                    created_items[item["name"]] = result["id"]
                    print(f"    ✅ Creato: {result['id'][:8]}...")
            
            # 2. Create KQL Database
            for item in manifest.get("items", []):
                if item["type"] == "KQLDatabase":
                    parent_id = created_items.get(item.get("parent"))
                    if not parent_id:
                        continue
                    
                    print(f"  ⏳ Creazione KQL Database: {item['name']}...")
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
                    print(f"    ✅ Creato: {result['id'][:8]}...")
            
            # 3. Create tables
            print("  ⏳ Attesa database ready...")
            time.sleep(5)
            
            for table in manifest.get("tables", []):
                db_name = table.get("database")
                db_id = created_items.get(db_name)
                schema = assets["schemas"].get(table["name"])
                
                if db_id and schema:
                    print(f"  ⏳ Creazione tabella: {table['name']}...")
                    
                    # Get query URI
                    db_info = _api_call("GET", f"{FABRIC_API}/workspaces/{workspace_id}/kqlDatabases/{db_id}")
                    query_uri = db_info.get("properties", {}).get("queryServiceUri")
                    
                    if query_uri:
                        # Parse and execute KQL commands
                        commands = _parse_kql(schema)
                        for cmd in commands:
                            _execute_kql(query_uri, db_info["displayName"], cmd)
                        print(f"    ✅ Tabella creata")
            
            # 4. Create Eventstream
            for item in manifest.get("items", []):
                if item["type"] == "Eventstream":
                    print(f"  ⏳ Creazione Eventstream: {item['name']}...")
                    result = _api_call("POST", f"{FABRIC_API}/workspaces/{workspace_id}/items", {
                        "displayName": item["name"],
                        "type": "Eventstream",
                        "description": f"Fabric Arcade - {item['name']}"
                    })
                    created_items[item["name"]] = result["id"]
                    print(f"    ✅ Creato: {result['id'][:8]}...")
                    print(f"    ⚠️ Configura manualmente: Custom Endpoint → KQL Database")
            
            # 5. Create Notebooks
            for item in manifest.get("items", []):
                if item["type"] == "Notebook":
                    nb_content = assets["notebooks"].get(item["name"])
                    if nb_content:
                        print(f"  ⏳ Creazione Notebook: {item['name']}...")
                        
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
                        print(f"    ✅ Creato: {result['id'][:8]}...")
            
            # Success!
            print(f"\n🎉 Installazione completata!")
            print(f"   Creati {len([k for k in created_items if not k.endswith('_eventhouse')])} items")
            print(f"\n📖 Prossimi passi:")
            print(f"   1. Configura l'Eventstream (Custom Endpoint → KQL Database)")
            print(f"   2. Apri il notebook del gioco e divertiti!")
            
        except Exception as e:
            print(f"\n❌ Errore durante l'installazione: {e}")
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


# Create global instance for easy access
arcade = Arcade()
