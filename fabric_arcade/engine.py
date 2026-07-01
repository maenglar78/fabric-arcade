"""
Fabric Arcade Deployment Engine

This module provides the core functionality to deploy game environments
to Microsoft Fabric workspaces using the Fabric REST API.
"""

import json
import base64
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

import requests

# Optional azure-identity (for CLI/local use)
try:
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    HAS_AZURE_IDENTITY = True
except ImportError:
    HAS_AZURE_IDENTITY = False

# Optional notebookutils (for Fabric notebooks)
try:
    import notebookutils
    HAS_NOTEBOOKUTILS = True
except ImportError:
    HAS_NOTEBOOKUTILS = False


# Fabric API endpoints
FABRIC_API_BASE = "https://api.fabric.microsoft.com/v1"
KUSTO_API_BASE = "https://{cluster}.kusto.fabric.microsoft.com"


@dataclass
class DeploymentContext:
    """Context for a game deployment"""
    workspace_id: str
    workspace_name: str
    game_id: str
    game_path: Path
    token: str
    created_items: Dict[str, str] = field(default_factory=dict)  # name -> id mapping
    

class FabricClient:
    """Client for interacting with Fabric REST API"""
    
    def __init__(self, token: Optional[str] = None):
        if token:
            self.token = token
        elif HAS_NOTEBOOKUTILS:
            # In Fabric notebook - use notebookutils
            self.token = notebookutils.credentials.getToken("https://api.fabric.microsoft.com")
        elif HAS_AZURE_IDENTITY:
            # Local/CLI - use Azure Identity
            try:
                credential = AzureCliCredential()
                self.token = credential.get_token("https://api.fabric.microsoft.com/.default").token
            except Exception:
                credential = DefaultAzureCredential()
                self.token = credential.get_token("https://api.fabric.microsoft.com/.default").token
        else:
            raise RuntimeError("No authentication method available. Install azure-identity or run in Fabric notebook.")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_workspaces(self) -> List[Dict]:
        """List all accessible workspaces"""
        response = requests.get(
            f"{FABRIC_API_BASE}/workspaces",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get("value", [])
    
    def get_workspace_by_name(self, name: str) -> Optional[Dict]:
        """Find workspace by name"""
        workspaces = self.get_workspaces()
        for ws in workspaces:
            if ws["displayName"].lower() == name.lower():
                return ws
        return None
    
    def create_item(self, workspace_id: str, item_type: str, display_name: str, 
                    definition: Optional[Dict] = None, description: str = "") -> Dict:
        """Create a Fabric item"""
        payload = {
            "displayName": display_name,
            "type": item_type,
            "description": description
        }
        
        if definition:
            payload["definition"] = definition
        
        response = requests.post(
            f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items",
            headers=self.headers,
            json=payload
        )
        
        # Handle long-running operation
        if response.status_code == 202:
            return self._wait_for_operation(response)
        
        response.raise_for_status()
        return response.json()
    
    def create_eventhouse(self, workspace_id: str, name: str) -> Dict:
        """Create an Eventhouse"""
        return self.create_item(
            workspace_id=workspace_id,
            item_type="Eventhouse",
            display_name=name,
            description=f"Fabric Arcade - {name}"
        )

    def create_lakehouse(self, workspace_id: str, name: str) -> Dict:
        """Create a Lakehouse (no schemas)."""
        return self.create_item(
            workspace_id=workspace_id,
            item_type="Lakehouse",
            display_name=name,
            description=f"Fabric Arcade - {name}"
        )
    
    def create_kql_database(self, workspace_id: str, eventhouse_id: str, 
                            name: str) -> Dict:
        """Create a KQL Database within an Eventhouse"""
        # KQL Database creation payload
        payload = {
            "displayName": name,
            "type": "KQLDatabase",
            "description": f"Fabric Arcade Database - {name}",
            "creationPayload": {
                "databaseType": "ReadWrite",
                "parentEventhouseItemId": eventhouse_id
            }
        }
        
        response = requests.post(
            f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 202:
            return self._wait_for_operation(response)
        
        response.raise_for_status()
        return response.json()
    
    def execute_kql_command(self, workspace_id: str, database_id: str, 
                            command: str, eventhouse_id: str = None) -> Dict:
        """Execute a KQL management command"""
        # Get the query URI - try database first, then eventhouse
        db_info = self.get_item(workspace_id, database_id)
        query_uri = db_info.get("properties", {}).get("queryUri")
        
        # If no queryUri in database, try to get from eventhouse
        if not query_uri and eventhouse_id:
            eh_info = self.get_item(workspace_id, eventhouse_id)
            query_uri = eh_info.get("properties", {}).get("queryServiceUri")
        
        # If still no queryUri, try the KQL Database API
        if not query_uri:
            db_props_url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/kqlDatabases/{database_id}"
            props_response = requests.get(db_props_url, headers=self.headers)
            if props_response.status_code == 200:
                props_data = props_response.json()
                query_uri = props_data.get("properties", {}).get("queryServiceUri")
        
        if not query_uri:
            raise ValueError(f"Could not get query URI for database {database_id}")
        
        # Execute the command
        kusto_headers = {
            "Authorization": f"Bearer {self._get_kusto_token()}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{query_uri}/v1/rest/mgmt",
            headers=kusto_headers,
            json={"csl": command, "db": db_info["displayName"]}
        )
        response.raise_for_status()
        return response.json()
    
    def create_eventstream(self, workspace_id: str, name: str, 
                          definition: Optional[Dict] = None) -> Dict:
        """Create an Eventstream"""
        return self.create_item(
            workspace_id=workspace_id,
            item_type="Eventstream",
            display_name=name,
            definition=definition,
            description=f"Fabric Arcade Eventstream - {name}"
        )
    
    def create_notebook(self, workspace_id: str, name: str, 
                       content: str) -> Dict:
        """Create a Notebook with content"""
        # Encode notebook content as base64
        encoded_content = base64.b64encode(content.encode()).decode()
        
        definition = {
            "format": "ipynb",
            "parts": [
                {
                    "path": "notebook-content.ipynb",
                    "payload": encoded_content,
                    "payloadType": "InlineBase64"
                }
            ]
        }
        
        return self.create_item(
            workspace_id=workspace_id,
            item_type="Notebook",
            display_name=name,
            definition=definition,
            description=f"Fabric Arcade Notebook - {name}"
        )

    def create_data_pipeline(self, workspace_id: str, name: str,
                             description: str = "") -> Dict:
        """Create an empty Data Pipeline the player will build in the UI.

        The pipeline-content.json carries no activities; the player assembles
        them in the Fabric UI as part of the gameplay.
        """
        content = {"properties": {"activities": []}}
        if description:
            content["properties"]["description"] = description
        encoded = base64.b64encode(
            json.dumps(content).encode("utf-8")
        ).decode("ascii")
        definition = {
            "parts": [
                {
                    "path": "pipeline-content.json",
                    "payload": encoded,
                    "payloadType": "InlineBase64",
                }
            ]
        }
        return self.create_item(
            workspace_id=workspace_id,
            item_type="DataPipeline",
            display_name=name,
            definition=definition,
            description=description or f"Fabric Arcade Pipeline - {name}",
        )

    def get_item(self, workspace_id: str, item_id: str) -> Dict:
        """Get item details"""
        response = requests.get(
            f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{item_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def list_items(self, workspace_id: str, item_type: Optional[str] = None) -> List[Dict]:
        """List items in a workspace"""
        url = f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items"
        if item_type:
            url += f"?type={item_type}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("value", [])
    
    def delete_item(self, workspace_id: str, item_id: str) -> None:
        """Delete an item"""
        response = requests.delete(
            f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{item_id}",
            headers=self.headers
        )
        response.raise_for_status()
    
    def _wait_for_operation(self, response: requests.Response, 
                           timeout: int = 300) -> Dict:
        """Wait for a long-running operation to complete"""
        import re
        
        operation_url = response.headers.get("Location")
        if not operation_url:
            return response.json() if response.text else {}
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            op_response = requests.get(operation_url, headers=self.headers)
            
            if op_response.status_code == 200:
                result = op_response.json()
                status = result.get("status", "").lower()
                
                if status == "succeeded":
                    # Check for Location header pointing to /result
                    result_location = op_response.headers.get("Location")
                    if result_location and "/result" in result_location:
                        result_response = requests.get(
                            result_location, headers=self.headers
                        )
                        if result_response.status_code == 200:
                            result_data = result_response.json()
                            if "id" in result_data:
                                return result_data
                    
                    # From resourceLocation headers
                    for header_name in ["resourceLocation", "Resource-Location", "x-ms-resource-location"]:
                        resource_location = op_response.headers.get(header_name)
                        if resource_location:
                            item_response = requests.get(
                                resource_location, headers=self.headers
                            )
                            if item_response.status_code == 200:
                                return item_response.json()
                    
                    # If result contains the item ID directly
                    if "id" in result:
                        return result
                    
                    # Parse item ID from the operation URL
                    match = re.search(r'/items/([a-f0-9-]+)', operation_url)
                    if match:
                        item_id = match.group(1)
                        ws_match = re.search(r'/workspaces/([a-f0-9-]+)/', operation_url)
                        if ws_match:
                            workspace_id = ws_match.group(1)
                            item_response = requests.get(
                                f"{FABRIC_API_BASE}/workspaces/{workspace_id}/items/{item_id}",
                                headers=self.headers
                            )
                            if item_response.status_code == 200:
                                return item_response.json()
                    
                    # Check for nested resourceId
                    for key in ["resourceId", "itemId", "objectId"]:
                        if key in result:
                            return {"id": result[key], **result}
                    
                    return result
                    
                elif status == "failed":
                    error_info = result.get("error", result)
                    raise Exception(f"Operation failed: {error_info}")
            
            time.sleep(2)
        
        raise TimeoutError("Operation timed out")
    
    def _get_kusto_token(self) -> str:
        """Get token for Kusto operations"""
        # Use AzureCliCredential for consistency with main auth
        try:
            credential = AzureCliCredential()
            return credential.get_token("https://kusto.kusto.windows.net/.default").token
        except Exception:
            # Fallback to DefaultAzureCredential
            credential = DefaultAzureCredential()
            return credential.get_token("https://kusto.kusto.windows.net/.default").token


class GameDeployer:
    """Deploys a game to a Fabric workspace"""
    
    def __init__(self, client: Optional[FabricClient] = None):
        self.client = client or FabricClient()
        # Packaged location (wheel): fabric_arcade/_catalog/. Dev source: repo/catalog/.
        _pkg_catalog = Path(__file__).parent / "_catalog"
        self.catalog_path = _pkg_catalog if _pkg_catalog.exists() else Path(__file__).parent.parent / "catalog"
    
    def deploy(self, game_id: str, workspace_name: str, 
               prefix: str = "") -> DeploymentContext:
        """
        Deploy a game to a workspace
        
        Args:
            game_id: ID of the game to deploy (e.g., "fabric-racing-game")
            workspace_name: Name of the target workspace
            prefix: Optional prefix for created items
        
        Returns:
            DeploymentContext with details of created items
        """
        # Find workspace
        workspace = self.client.get_workspace_by_name(workspace_name)
        if not workspace:
            raise ValueError(f"Workspace '{workspace_name}' not found")
        
        workspace_id = workspace["id"]
        
        # Load game manifest
        game_path = self.catalog_path / game_id.replace("-", "_")
        if not game_path.exists():
            # Try with hyphens
            game_path = self.catalog_path / game_id
        
        if not game_path.exists():
            raise ValueError(f"Game '{game_id}' not found in catalog")
        
        manifest_path = game_path / "manifest.json"
        if not manifest_path.exists():
            raise ValueError(f"No manifest.json found for game '{game_id}'")
        
        with open(manifest_path, encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Create deployment context
        ctx = DeploymentContext(
            workspace_id=workspace_id,
            workspace_name=workspace_name,
            game_id=game_id,
            game_path=game_path,
            token=self.client.token
        )
        
        # Deploy items in order
        self._deploy_items(ctx, manifest, prefix)
        
        return ctx
    
    def _deploy_items(self, ctx: DeploymentContext, manifest: Dict, 
                      prefix: str) -> None:
        """Deploy all items defined in manifest"""

        # 0. Create Lakehouse(s) first — notebooks may bind to them at runtime.
        for item in manifest.get("items", []):
            if item["type"] == "Lakehouse":
                name = f"{prefix}{item['name']}" if prefix else item["name"]
                print(f"  Creating Lakehouse: {name}...")
                result = self.client.create_lakehouse(ctx.workspace_id, name)
                ctx.created_items[item["name"]] = result["id"]
                print(f"    ✓ Created: {result['id']}")

        # 1. Create Eventhouse(s)
        for item in manifest.get("items", []):
            if item["type"] == "Eventhouse":
                name = f"{prefix}{item['name']}" if prefix else item["name"]
                print(f"  Creating Eventhouse: {name}...")
                result = self.client.create_eventhouse(ctx.workspace_id, name)
                ctx.created_items[item["name"]] = result["id"]
                print(f"    ✓ Created: {result['id']}")

                # Auto-register the default KQL DB (same displayName as the EH)
                # under key "<eh_name>/db" so tables can reference it without
                # an explicit KQLDatabase manifest entry.
                default_db = None
                for _ in range(20):
                    for db in self.client.list_items(ctx.workspace_id, "KQLDatabase"):
                        if db.get("displayName") == name:
                            default_db = db
                            break
                    if default_db:
                        break
                    time.sleep(2)
                if default_db:
                    ctx.created_items[f"{item['name']}/db"] = default_db["id"]
                    ctx.created_items[f"{item['name']}/db_eventhouse"] = result["id"]
                    print(f"    ✓ Default KQL DB bound: {default_db['id']}")
        
        # 2. Create KQL Database(s)
        for item in manifest.get("items", []):
            if item["type"] == "KQLDatabase":
                name = f"{prefix}{item['name']}" if prefix else item["name"]
                parent_name = item.get("parent")
                parent_id = ctx.created_items.get(parent_name)
                
                if not parent_id:
                    raise ValueError(f"Parent Eventhouse '{parent_name}' not found")

                # If parent and child share the display name, bind to the
                # auto-provisioned default DB instead of creating a duplicate.
                if name == parent_name:
                    print(f"  Binding to default KQL DB inside {parent_name}...")
                    default_db = None
                    for _ in range(20):
                        for db in self.client.list_items(ctx.workspace_id, "KQLDatabase"):
                            if db.get("displayName") == name:
                                default_db = db
                                break
                        if default_db:
                            break
                        time.sleep(2)
                    if not default_db:
                        raise RuntimeError(f"Default KQL DB '{name}' not found after Eventhouse creation")
                    ctx.created_items[item["name"]] = default_db["id"]
                    ctx.created_items[f"{item['name']}_eventhouse"] = parent_id
                    print(f"    ✓ Bound: {default_db['id']}")
                    continue

                print(f"  Creating KQL Database: {name}...")
                result = self.client.create_kql_database(
                    ctx.workspace_id, parent_id, name
                )
                ctx.created_items[item["name"]] = result["id"]
                # Also track parent eventhouse for this database
                ctx.created_items[f"{item['name']}_eventhouse"] = parent_id
                print(f"    ✓ Created: {result['id']}")
        
        # 3. Create tables (wait for database to be ready)
        if manifest.get("tables"):
            print(f"  Waiting for database to be ready...")
            time.sleep(5)  # Give database time to become operational
            
        for table in manifest.get("tables", []):
            db_name = table.get("database")
            db_id = ctx.created_items.get(f"{db_name}/db") or ctx.created_items.get(db_name)
            eventhouse_id = (
                ctx.created_items.get(f"{db_name}_eventhouse")
                or ctx.created_items.get(f"{db_name}/db_eventhouse")
                or ctx.created_items.get(db_name)
            )

            if not db_id:
                raise ValueError(f"Database '{db_name}' not found")
            
            schema_file = ctx.game_path / table["schema"]
            if schema_file.exists():
                print(f"  Creating table: {table['name']}...")
                with open(schema_file, encoding='utf-8') as f:
                    kql_content = f.read()
                
                # Parse KQL commands and execute each separately
                # Remove comments and split by command
                kql_commands = self._parse_kql_commands(kql_content)
                
                for cmd in kql_commands:
                    self.client.execute_kql_command(
                        ctx.workspace_id, db_id, cmd, eventhouse_id
                    )
                print(f"    ✓ Table created")
        
        # 4. Create Eventstream(s)
        for item in manifest.get("items", []):
            if item["type"] == "Eventstream":
                name = f"{prefix}{item['name']}" if prefix else item["name"]
                print(f"  Creating Eventstream: {name}...")
                
                # Create Eventstream without definition for now
                # Definition format for Eventstream is complex and requires 
                # proper Fabric definition structure with base64-encoded parts
                # TODO: Support eventstream definitions once format is confirmed
                result = self.client.create_eventstream(
                    ctx.workspace_id, name, None
                )
                ctx.created_items[item["name"]] = result["id"]
                print(f"    ✓ Created: {result['id']}")
                
                # If there was a definition file, show instructions
                if "definition" in item:
                    print(f"    ⚠️ Note: Configure Eventstream manually using definition in {item['definition']}")
        
        # 5. Create Notebook(s)
        for item in manifest.get("items", []):
            if item["type"] == "Notebook":
                name = f"{prefix}{item['name']}" if prefix else item["name"]
                print(f"  Creating Notebook: {name}...")
                
                notebook_path = ctx.game_path / item["file"]
                if notebook_path.exists():
                    with open(notebook_path, encoding='utf-8') as f:
                        content = f.read()
                    
                    result = self.client.create_notebook(
                        ctx.workspace_id, name, content
                    )
                    ctx.created_items[item["name"]] = result["id"]
                    print(f"    ✓ Created: {result['id']}")

        # 6. Create Data Pipeline(s) — empty shells the player fills in the UI
        for item in manifest.get("items", []):
            if item["type"] == "DataPipeline":
                name = f"{prefix}{item['name']}" if prefix else item["name"]
                print(f"  Creating Data Pipeline: {name}...")
                result = self.client.create_data_pipeline(
                    ctx.workspace_id, name, item.get("description", "")
                )
                ctx.created_items[item["name"]] = result["id"]
                print(f"    ✓ Created: {result['id']}")
    
    def _parse_kql_commands(self, kql_content: str) -> list:
        """
        Parse KQL content into individual commands.
        Removes comments and splits by command.
        """
        import re
        
        # Remove single-line comments (// ...)
        lines = []
        for line in kql_content.split('\n'):
            # Strip leading/trailing whitespace
            stripped = line.strip()
            # Skip comment-only lines
            if stripped.startswith('//'):
                continue
            # Remove inline comments
            if '//' in line:
                line = line.split('//')[0]
            lines.append(line)
        
        # Join and split by KQL command markers
        content = '\n'.join(lines)
        
        # Split by commands that start with a dot (management commands)
        # Each command starts with a dot at the beginning of a line
        commands = []
        current_cmd = []
        
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('.') and current_cmd:
                # New command starts, save previous
                cmd = '\n'.join(current_cmd).strip()
                if cmd:
                    commands.append(cmd)
                current_cmd = [line]
            elif stripped:
                current_cmd.append(line)
        
        # Don't forget the last command
        if current_cmd:
            cmd = '\n'.join(current_cmd).strip()
            if cmd:
                commands.append(cmd)
        
        return commands
    
    def uninstall(self, game_id: str, workspace_name: str, 
                  prefix: str = "") -> None:
        """Remove a game from a workspace"""
        workspace = self.client.get_workspace_by_name(workspace_name)
        if not workspace:
            raise ValueError(f"Workspace '{workspace_name}' not found")
        
        workspace_id = workspace["id"]
        
        # Load manifest to know what to delete
        game_path = self.catalog_path / game_id.replace("-", "_")
        if not game_path.exists():
            game_path = self.catalog_path / game_id
        
        manifest_path = game_path / "manifest.json"
        if not manifest_path.exists():
            raise ValueError(f"No manifest.json found for game '{game_id}'")
        
        with open(manifest_path, encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Get all items in workspace
        items = self.client.list_items(workspace_id)
        
        # Delete items in reverse order (pipelines, notebooks, eventstreams, databases, eventhouses, lakehouses)
        item_types_order = ["DataPipeline", "Notebook", "Eventstream", "KQLDatabase", "Eventhouse", "Lakehouse"]
        
        for item_type in item_types_order:
            for manifest_item in manifest.get("items", []):
                if manifest_item["type"] == item_type:
                    name = f"{prefix}{manifest_item['name']}" if prefix else manifest_item["name"]
                    
                    # Find item by name
                    for ws_item in items:
                        if ws_item["displayName"] == name:
                            print(f"  Deleting {item_type}: {name}...")
                            self.client.delete_item(workspace_id, ws_item["id"])
                            print(f"    ✓ Deleted")
                            break


def install(game_id: str, workspace: str, prefix: str = "") -> DeploymentContext:
    """
    Install a game to a Fabric workspace
    
    Usage:
        >>> import fabric_arcade as arcade
        >>> arcade.install("fabric-racing-game", workspace="MyWorkspace")
    """
    deployer = GameDeployer()
    print(f"🎮 Installing '{game_id}' to workspace '{workspace}'...")
    ctx = deployer.deploy(game_id, workspace, prefix)
    print(f"✅ Game installed successfully!")
    print(f"   Created {len(ctx.created_items)} items")
    return ctx


def uninstall(game_id: str, workspace: str, prefix: str = "") -> None:
    """
    Uninstall a game from a Fabric workspace
    
    Usage:
        >>> import fabric_arcade as arcade
        >>> arcade.uninstall("fabric-racing-game", workspace="MyWorkspace")
    """
    deployer = GameDeployer()
    print(f"🗑️ Uninstalling '{game_id}' from workspace '{workspace}'...")
    deployer.uninstall(game_id, workspace, prefix)
    print(f"✅ Game uninstalled successfully!")
