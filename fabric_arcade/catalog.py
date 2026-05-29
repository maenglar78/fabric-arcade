"""
Game catalog management for Fabric Arcade
"""

import json
from pathlib import Path
from typing import List, Optional
from .core import Game, GameType, Workload, Difficulty

# Catalog data - in production this would be loaded from a remote source
CATALOG_DATA = [
    {
        "id": "mission-artemis-2",
        "name": "Mission Artemis 2",
        "description": "Lunar mission with 4 astronauts. 4-minute video synchronized with real-time telemetry: acceleration, pressure, heart rate, flight phases.",
        "type": "mission",
        "workloads": ["RTI", "DE"],
        "difficulty": 3,
        "duration_minutes": 45,
        "icon": "🚀",
        "tags": ["space", "telemetry", "streaming", "video-sync"],
        "achievements": ["first-launch", "lunar-orbit", "splashdown"]
    },
    {
        "id": "fabric-racing-game",
        "name": "Fabric Racing Game",
        "description": "HTML5 multiplayer racing game for 4 drivers with real-time telemetry. Custom Endpoint, JSON mapping, live dashboard.",
        "type": "mission",
        "workloads": ["RTI"],
        "difficulty": 2,
        "duration_minutes": 30,
        "icon": "🏎️",
        "tags": ["racing", "html5", "multiplayer", "gaming"],
        "achievements": ["first-start", "full-grid", "champion"]
    },
    {
        "id": "calc-groups-cathedral",
        "name": "Calc Groups Cathedral",
        "description": "Replace 12 redundant time-intelligence measures with one elegant Calculation Group on a real Direct Lake semantic model. Earn the rank of Cathedral Builder.",
        "type": "puzzle",
        "workloads": ["PBI"],
        "difficulty": 3,
        "duration_minutes": 60,
        "icon": "🏛️",
        "tags": ["dax", "calc-groups", "semantic-model", "direct-lake", "puzzle"],
        "achievements": ["stonemason", "architect", "cathedral-builder"]
    },
    {
        "id": "sports-tracker",
        "name": "Sports Tracker",
        "description": "Track live sports statistics from matches. Analyze player performance, team stats, and predict outcomes using ML models on streaming data.",
        "type": "challenge",
        "workloads": ["RTI", "DS"],
        "difficulty": 2,
        "duration_minutes": 25,
        "icon": "⚽",
        "tags": ["sports", "analytics", "ml", "predictions"],
        "achievements": ["stat-master", "prediction-ace"]
    },
    {
        "id": "quest-pipeline",
        "name": "Quest Data Pipeline",
        "description": "Build a medallion architecture data pipeline as a fantasy quest. Bronze = Raw dungeon loot, Silver = Cleaned treasures, Gold = Legendary items ready for analysis.",
        "type": "mission",
        "workloads": ["DE", "DF"],
        "difficulty": 3,
        "duration_minutes": 40,
        "icon": "🏰",
        "tags": ["fantasy", "medallion", "pipeline", "etl"],
        "achievements": ["bronze-collector", "silver-refiner", "gold-master"]
    },
    {
        "id": "retro-arcade",
        "name": "Retro Arcade",
        "description": "Build a Power BI report on a pre-made arcade-themed Direct Lake semantic model (Pac-Man, Galaga, Donkey Kong & friends). 5 levels graded by sempy: Foundation, Visuals, Interactivity, Storytelling, Polish. Earn a signed badge from Newbie to Kill Screen Survivor.",
        "type": "arcade",
        "workloads": ["PBI"],
        "difficulty": 2,
        "duration_minutes": 45,
        "icon": "🕹️",
        "tags": ["retro", "powerbi", "pbir", "sempy", "report-building"],
        "achievements": ["newbie", "quarter-muncher", "high-roller", "arcade-legend", "kill-screen-survivor"]
    },
    {
        "id": "ocean-explorer",
        "name": "Ocean Explorer",
        "description": "Explore ocean data with ML models. Detect marine life patterns, track vessel movements, and predict weather using satellite and sensor data.",
        "type": "mission",
        "workloads": ["DS", "RTI"],
        "difficulty": 3,
        "duration_minutes": 50,
        "icon": "🌊",
        "tags": ["ocean", "ml", "exploration", "satellite"],
        "achievements": ["deep-diver", "whale-spotter", "storm-predictor"]
    },
    {
        "id": "target-practice",
        "name": "Target Practice",
        "description": "Quick-fire Real-Time Intelligence basics. Hit targets by correctly routing events through Eventstream to Eventhouse. Perfect for RTI beginners.",
        "type": "challenge",
        "workloads": ["RTI"],
        "difficulty": 1,
        "duration_minutes": 15,
        "icon": "🎯",
        "tags": ["beginner", "rti", "eventstream", "quick"],
        "achievements": ["bullseye", "quick-draw"]
    },
    {
        "id": "city-builder",
        "name": "City Builder Analytics",
        "description": "Design and analyze a virtual city. Track population, resources, traffic, and happiness metrics. Build data warehouses for urban planning insights.",
        "type": "mission",
        "workloads": ["DE", "DW"],
        "difficulty": 3,
        "duration_minutes": 60,
        "icon": "🏙️",
        "tags": ["simulation", "city", "warehouse", "analytics"],
        "achievements": ["city-founder", "metropolis-mayor", "data-urbanist"]
    },
    {
        "id": "wizard-workshop",
        "name": "Wizard's Workshop",
        "description": "Learn Data Science through magical experiments. Train 'spell' models, mix 'potion' features, and predict 'enchantment' outcomes.",
        "type": "challenge",
        "workloads": ["DS"],
        "difficulty": 2,
        "duration_minutes": 20,
        "icon": "🧙",
        "tags": ["fantasy", "ml", "data-science", "fun"],
        "achievements": ["apprentice", "spell-caster", "grand-wizard"]
    },
    {
        "id": "train-dispatch",
        "name": "Train Dispatch",
        "description": "Manage a railway network in real-time. Route trains, avoid collisions, and optimize schedules using streaming data and live dashboards.",
        "type": "arcade",
        "workloads": ["RTI"],
        "difficulty": 2,
        "duration_minutes": 15,
        "icon": "🚂",
        "tags": ["trains", "simulation", "streaming", "optimization"],
        "achievements": ["on-time", "traffic-controller", "rail-master"]
    }
]

def get_catalog() -> List[Game]:
    """
    Get the full game catalog.
    
    Returns
    -------
    List[Game]
        All games in the catalog
    """
    games = []
    for data in CATALOG_DATA:
        game = Game(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            game_type=GameType(data["type"]),
            workloads=[Workload[w] for w in data["workloads"]],
            difficulty=Difficulty(data["difficulty"]),
            duration_minutes=data["duration_minutes"],
            icon=data.get("icon", "🎮"),
            tags=data.get("tags", []),
            achievements=data.get("achievements", [])
        )
        games.append(game)
    return games

def search_games(
    query: str,
    game_type: Optional[GameType] = None,
    workloads: Optional[List[Workload]] = None,
    max_duration: Optional[int] = None
) -> List[Game]:
    """
    Search games by keyword and filters.
    
    Parameters
    ----------
    query : str
        Search term to match in name, description, or tags
    game_type : GameType, optional
        Filter by game type
    workloads : List[Workload], optional
        Filter by workloads (games must include ALL specified)
    max_duration : int, optional
        Maximum duration in minutes
        
    Returns
    -------
    List[Game]
        Matching games
        
    Example
    -------
    >>> search_games("space", workloads=[Workload.RTI])
    [Game(id='mission-artemis-2', ...)]
    """
    games = get_catalog()
    query_lower = query.lower()
    
    results = []
    for game in games:
        # Search in name, description, and tags
        searchable = f"{game.name} {game.description} {' '.join(game.tags)}".lower()
        if query_lower not in searchable:
            continue
            
        # Apply filters
        if game_type and game.game_type != game_type:
            continue
        if workloads and not all(w in game.workloads for w in workloads):
            continue
        if max_duration and game.duration_minutes > max_duration:
            continue
            
        results.append(game)
    
    return results

def get_game(game_id: str) -> Optional[Game]:
    """
    Get a specific game by ID.
    
    Parameters
    ----------
    game_id : str
        The game identifier
        
    Returns
    -------
    Game or None
        The game if found, None otherwise
    """
    for game in get_catalog():
        if game.id == game_id:
            return game
    return None
