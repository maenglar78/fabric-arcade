"""
Deployment functionality for Fabric Arcade games
"""

import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass 
class DeployedItem:
    """Represents a deployed Fabric item"""
    item_type: str
    name: str
    item_id: Optional[str] = None
    
def deploy_game(game_id: str, workspace: Optional[str] = None) -> Dict[str, Any]:
    """
    Deploy a game to a Fabric workspace.
    
    Parameters
    ----------
    game_id : str
        The game identifier to deploy
    workspace : str, optional
        Target workspace. Uses default if not specified.
        
    Returns
    -------
    dict
        Deployment result with created items
    """
    from .catalog import get_game
    
    game = get_game(game_id)
    if not game:
        raise ValueError(f"Game not found: {game_id}")
    
    print(f"\n{game.icon} Deploying: {game.name}")
    print(f"Description: {game.description}")
    print(f"Estimated time: {game.duration_minutes} minutes")
    print()
    
    # Get deployment manifest for this game
    items = _get_game_items(game_id)
    
    deployed = []
    for item in items:
        print(f"  📦 Creating {item['type']}: {item['name']}...")
        # In production, this would call Fabric APIs
        deployed.append(DeployedItem(
            item_type=item['type'],
            name=item['name']
        ))
    
    return {
        "game_id": game_id,
        "workspace": workspace or "default",
        "items_created": len(deployed),
        "items": [{"type": d.item_type, "name": d.name} for d in deployed]
    }

def _get_game_items(game_id: str) -> List[Dict[str, str]]:
    """Get the Fabric items required for a game"""
    
    # Game-specific item definitions
    GAME_ITEMS = {
        "mission-artemis-2": [
            {"type": "Eventhouse", "name": "artemis2-telemetry"},
            {"type": "Eventstream", "name": "artemis2-stream"},
            {"type": "KQLDatabase", "name": "mission-data"},
            {"type": "RTDashboard", "name": "mission-control"},
            {"type": "Notebook", "name": "artemis2-simulator"},
        ],
        "fabric-racing-game": [
            {"type": "Eventhouse", "name": "racing-events"},
            {"type": "Eventstream", "name": "racing-stream"},
            {"type": "KQLDatabase", "name": "race-data"},
            {"type": "Notebook", "name": "Deploy_FabricRacingGame"},
            {"type": "Notebook", "name": "Race_P1"},
            {"type": "Notebook", "name": "Race_P2"},
            {"type": "Notebook", "name": "Race_P3"},
            {"type": "Notebook", "name": "Race_P4"},
        ],
        "sports-tracker": [
            {"type": "Eventhouse", "name": "sports-events"},
            {"type": "Eventstream", "name": "match-stream"},
            {"type": "Notebook", "name": "sports-ml-model"},
            {"type": "MLModel", "name": "outcome-predictor"},
        ],
        "quest-pipeline": [
            {"type": "Lakehouse", "name": "bronze-dungeon"},
            {"type": "Lakehouse", "name": "silver-treasury"},
            {"type": "Lakehouse", "name": "gold-vault"},
            {"type": "Pipeline", "name": "quest-etl"},
            {"type": "Notebook", "name": "loot-processor"},
        ],
        "retro-arcade": [
            {"type": "SemanticModel", "name": "arcade-scores"},
            {"type": "Report", "name": "retro-dashboard"},
        ],
        "ocean-explorer": [
            {"type": "Eventhouse", "name": "ocean-sensors"},
            {"type": "Eventstream", "name": "satellite-feed"},
            {"type": "Notebook", "name": "marine-detection"},
            {"type": "MLModel", "name": "species-classifier"},
            {"type": "RTDashboard", "name": "ocean-monitor"},
        ],
        "target-practice": [
            {"type": "Eventhouse", "name": "target-events"},
            {"type": "Eventstream", "name": "target-stream"},
            {"type": "Notebook", "name": "target-tutorial"},
        ],
        "city-builder": [
            {"type": "Lakehouse", "name": "city-bronze"},
            {"type": "Lakehouse", "name": "city-silver"},
            {"type": "Warehouse", "name": "city-analytics"},
            {"type": "Pipeline", "name": "city-ingestion"},
            {"type": "Notebook", "name": "city-simulator"},
            {"type": "Report", "name": "city-dashboard"},
        ],
        "wizard-workshop": [
            {"type": "Lakehouse", "name": "spell-data"},
            {"type": "Notebook", "name": "potion-features"},
            {"type": "Notebook", "name": "spell-training"},
            {"type": "MLModel", "name": "enchantment-model"},
        ],
        "train-dispatch": [
            {"type": "Eventhouse", "name": "train-telemetry"},
            {"type": "Eventstream", "name": "train-positions"},
            {"type": "RTDashboard", "name": "dispatch-center"},
            {"type": "Notebook", "name": "train-simulator"},
        ],
    }
    
    return GAME_ITEMS.get(game_id, [])

def remove_game(game_id: str, workspace: Optional[str] = None) -> Dict[str, Any]:
    """
    Remove a deployed game from a workspace.
    
    Parameters
    ----------
    game_id : str
        The game identifier to remove
    workspace : str, optional
        Target workspace
        
    Returns
    -------
    dict
        Removal result
    """
    items = _get_game_items(game_id)
    
    print(f"\n🗑️ Removing game: {game_id}")
    for item in items:
        print(f"  ❌ Removing {item['type']}: {item['name']}...")
    
    return {
        "game_id": game_id,
        "items_removed": len(items)
    }
