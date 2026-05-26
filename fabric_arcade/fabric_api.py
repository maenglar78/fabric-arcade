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
            
            # 6. Create README notebook with instructions
            print(f"  ⏳ Creazione notebook README...")
            
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
                "description": f"Guida post-deploy per {game_info.get('name', game_id)}",
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
            print(f"    ✅ README creato: {readme_result['id'][:8]}...")
            
            # Success!
            print(f"\n🎉 Installazione completata!")
            print(f"   Creati {len([k for k in created_items if not k.endswith('_eventhouse')])} items")
            print(f"\n📖 Prossimi passi:")
            print(f"   1. Apri il notebook '{game_id}_README' per le istruzioni complete")
            print(f"   2. Configura l'Eventstream (Custom Endpoint → KQL Database)")
            print(f"   3. Avvia il gioco dal notebook principale!")
            
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


def _create_readme_notebook(game_id: str, game_name: str, manifest: dict, created_items: dict) -> str:
    """Generate README notebook content with post-deploy instructions"""
    
    # Get game-specific instructions based on game_id
    if game_id == "fabric-racing-game":
        game_instructions = '''## 🏎️ Come Giocare

### Passo 1: Configura l'Eventstream
1. Apri **RacingEventstream** nel tuo workspace
2. Clicca su **Edit** per entrare in modalità modifica
3. Aggiungi una **Custom Endpoint Source**:
   - Nome: `TelemetryInput`
   - Questo creerà un endpoint HTTP per ricevere i dati
4. Aggiungi una **KQL Database Destination**:
   - Seleziona **RacingEventhouse** → **RacingDB**
   - Tabella: **Telemetry**
5. Collega Source → Destination e clicca **Publish**

### Passo 2: Copia l'URL dell'Eventstream
1. Dopo il publish, clicca sulla Custom Endpoint Source
2. Copia l'**Ingestion URL** (ti servirà nel gioco)

### Passo 3: Avvia il Gioco
1. Apri il notebook **RacingGame_Play**
2. Incolla l'URL dell'Eventstream nella cella di configurazione
3. Esegui tutte le celle
4. Si aprirà il gioco HTML5 nel browser!

### Passo 4: Gioca! 🎮
- **WASD** o **Frecce**: Sterza e accelera
- **Spazio**: Freno
- Invita fino a 4 giocatori per gare multiplayer!'''

    elif game_id == "mission-artemis-2":
        game_instructions = '''## 🚀 Come Iniziare la Missione

### Passo 1: Configura l'Eventstream
1. Apri **ArtemisEventstream** nel tuo workspace
2. Clicca su **Edit** per entrare in modalità modifica
3. Aggiungi **4 Custom Endpoint Sources**:
   - `VehicleTelemetryInput`
   - `CrewVitalsInput`
   - `EnvironmentalInput`
   - `MissionEventsInput`
4. Aggiungi una **KQL Database Destination**:
   - Seleziona **ArtemisEventhouse** → **MissionData**
5. Mappa ogni Source alla tabella corrispondente
6. Clicca **Publish**

### Passo 2: Avvia la Simulazione
1. Apri il notebook **Artemis_Simulator**
2. Configura gli URL degli Eventstream Custom Endpoints
3. Esegui la cella di configurazione
4. Avvia la simulazione con `start_mission()`

### Passo 3: Monitora dal Mission Control
1. Apri il notebook **Mission_Control**
2. Esegui le celle per visualizzare:
   - 📊 Telemetria veicolo in tempo reale
   - 👨‍🚀 Segni vitali equipaggio
   - 🌡️ Condizioni ambientali
   - 📜 Log eventi missione
3. Il video della missione è sincronizzato con i dati!

### Passo 4: Analizza con KQL
Esplora i dati con query KQL nella sezione "Query KQL" sotto.'''

    else:
        game_instructions = '''## 🎮 Come Iniziare

### Passo 1: Configura l'Eventstream
1. Apri l'Eventstream creato nel tuo workspace
2. Configura le sorgenti dati appropriate
3. Collega al KQL Database
4. Clicca **Publish**

### Passo 2: Avvia il Gioco
1. Apri il notebook principale del gioco
2. Configura i parametri necessari
3. Esegui le celle in ordine

### Passo 3: Divertiti!
Segui le istruzioni nel notebook del gioco.'''

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
