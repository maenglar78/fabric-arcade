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
from azure.identity import DefaultAzureCredential, AzureCliCredential


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
        else:
            # Try Azure CLI first, then fall back to DefaultAzureCredential
            try:
                credential = AzureCliCredential()
                self.token = credential.get_token("https://api.fabric.microsoft.com/.default").token
            except Exception:
                credential = DefaultAzureCredential()
                self.token = credential.get_token("https://api.fabric.microsoft.com/.default").token
        
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
                            command: str) -> Dict:
        """Execute a KQL management command"""
        # Get the query URI for the database
        db_info = self.get_item(workspace_id, database_id)
        query_uri = db_info.get("properties", {}).get("queryUri")
        
        if not query_uri:
            raise ValueError("Could not get query URI for database")
        
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
        operation_url = response.headers.get("Location")
        if not operation_url:
            # Try to get result from response
            return response.json() if response.text else {}
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            op_response = requests.get(operation_url, headers=self.headers)
            
            if op_response.status_code == 200:
                result = op_response.json()
                status = result.get("status", "").lower()
                
                if status == "succeeded":
                    # Get the created item
                    if "resourceLocation" in op_response.headers:
                        item_response = requests.get(
                            op_response.headers["resourceLocation"],
                            headers=self.headers
                        )
                        return item_response.json()
                    return result
                elif status == "failed":
                    raise Exception(f"Operation failed: {result}")
            
            time.sleep(2)
        
        raise TimeoutError("Operation timed out")
    
    def _get_kusto_token(self) -> str:
        """Get token for Kusto operations"""
        credential = DefaultAzureCredential()
        return credential.get_token("https://kusto.kusto.windows.net/.default").token


class GameDeployer:
    """Deploys a game to a Fabric workspace"""
    
    def __init__(self, client: Optional[FabricClient] = None):
        self.client = client or FabricClient()
        self.catalog_path = Path(__file__).parent.parent / "catalog"
    
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
        
        # 1. Create Eventhouse(s)
        for item in manifest.get("items", []):
            if item["type"] == "Eventhouse":
                name = f"{prefix}{item['name']}" if prefix else item["name"]
                print(f"  Creating Eventhouse: {name}...")
                result = self.client.create_eventhouse(ctx.workspace_id, name)
                ctx.created_items[item["name"]] = result["id"]
                print(f"    ✓ Created: {result['id']}")
        
        # 2. Create KQL Database(s)
        for item in manifest.get("items", []):
            if item["type"] == "KQLDatabase":
                name = f"{prefix}{item['name']}" if prefix else item["name"]
                parent_name = item.get("parent")
                parent_id = ctx.created_items.get(parent_name)
                
                if not parent_id:
                    raise ValueError(f"Parent Eventhouse '{parent_name}' not found")
                
                print(f"  Creating KQL Database: {name}...")
                result = self.client.create_kql_database(
                    ctx.workspace_id, parent_id, name
                )
                ctx.created_items[item["name"]] = result["id"]
                print(f"    ✓ Created: {result['id']}")
        
        # 3. Create tables
        for table in manifest.get("tables", []):
            db_name = table.get("database")
            db_id = ctx.created_items.get(db_name)
            
            if not db_id:
                raise ValueError(f"Database '{db_name}' not found")
            
            schema_file = ctx.game_path / table["schema"]
            if schema_file.exists():
                print(f"  Creating table: {table['name']}...")
                with open(schema_file, encoding='utf-8') as f:
                    kql_command = f.read()
                
                self.client.execute_kql_command(ctx.workspace_id, db_id, kql_command)
                print(f"    ✓ Table created")
        
        # 4. Create Eventstream(s)
        for item in manifest.get("items", []):
            if item["type"] == "Eventstream":
                name = f"{prefix}{item['name']}" if prefix else item["name"]
                print(f"  Creating Eventstream: {name}...")
                
                # Load definition if specified
                definition = None
                if "definition" in item:
                    def_path = ctx.game_path / item["definition"]
                    if def_path.exists():
                        with open(def_path, encoding='utf-8') as f:
                            definition = json.load(f)
                
                result = self.client.create_eventstream(
                    ctx.workspace_id, name, definition
                )
                ctx.created_items[item["name"]] = result["id"]
                print(f"    ✓ Created: {result['id']}")
        
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
        
        # Delete items in reverse order (notebooks, eventstreams, databases, eventhouses)
        item_types_order = ["Notebook", "Eventstream", "KQLDatabase", "Eventhouse"]
        
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
