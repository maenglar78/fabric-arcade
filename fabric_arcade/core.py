"""
Core functionality for Fabric Arcade
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

class GameType(Enum):
    MISSION = "mission"      # Full end-to-end projects (30-60 min)
    CHALLENGE = "challenge"  # Single workload focus (15-30 min)
    ARCADE = "arcade"        # Quick demos (5-15 min)
    PUZZLE = "puzzle"        # Constraint-based authoring challenges

class Difficulty(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3

class Workload(Enum):
    RTI = "Real-Time Intelligence"
    DE = "Data Engineering"
    PBI = "Power BI"
    DS = "Data Science"
    DF = "Data Factory"
    DW = "Data Warehouse"

@dataclass
class Game:
    """Represents a Fabric Arcade game"""
    id: str
    name: str
    description: str
    game_type: GameType
    workloads: List[Workload]
    difficulty: Difficulty
    duration_minutes: int
    icon: str
    tags: List[str]
    achievements: List[str]
    
    @classmethod
    def from_manifest(cls, manifest_path: Path) -> "Game":
        """Load game from manifest.json"""
        with open(manifest_path) as f:
            data = json.load(f)
        return cls(
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

def list_games(
    game_type: Optional[GameType] = None,
    workload: Optional[Workload] = None,
    difficulty: Optional[Difficulty] = None,
    verbose: bool = True
) -> List[Game]:
    """
    List all available games in the Fabric Arcade catalog.
    
    Parameters
    ----------
    game_type : GameType, optional
        Filter by game type (MISSION, CHALLENGE, ARCADE)
    workload : Workload, optional  
        Filter by Fabric workload (RTI, DE, PBI, DS, DF, DW)
    difficulty : Difficulty, optional
        Filter by difficulty level (BEGINNER, INTERMEDIATE, ADVANCED)
    verbose : bool
        If True, prints formatted table
        
    Returns
    -------
    List[Game]
        List of matching games
        
    Example
    -------
    >>> import fabric_arcade as arcade
    >>> arcade.list()  # Show all games
    >>> arcade.list(workload=Workload.RTI)  # Only Real-Time Intelligence
    """
    from .catalog import get_catalog
    
    games = get_catalog()
    
    # Apply filters
    if game_type:
        games = [g for g in games if g.game_type == game_type]
    if workload:
        games = [g for g in games if workload in g.workloads]
    if difficulty:
        games = [g for g in games if g.difficulty == difficulty]
    
    if verbose:
        _print_games_table(games)
    
    return games

def _print_games_table(games: List[Game]) -> None:
    """Print games in a nice formatted table"""
    print("\n🎮 FABRIC ARCADE - Game Catalog")
    print("=" * 80)
    print(f"{'Icon':<4} {'Game':<30} {'Type':<12} {'Workloads':<15} {'Diff':<6} {'Time':<8}")
    print("-" * 80)
    
    for g in games:
        workloads = "+".join([w.name for w in g.workloads])
        stars = "⭐" * g.difficulty.value
        print(f"{g.icon:<4} {g.name:<30} {g.game_type.value:<12} {workloads:<15} {stars:<6} {g.duration_minutes} min")
    
    print("-" * 80)
    print(f"Total: {len(games)} games available")
    print("\nUse arcade.install('game-id') to deploy a game to your workspace")
    print()

def install(game_id: str, workspace: Optional[str] = None) -> Dict[str, Any]:
    """
    Install a game to your Fabric workspace.
    
    Parameters
    ----------
    game_id : str
        The unique identifier of the game to install
    workspace : str, optional
        Target workspace name. If not provided, uses default workspace.
        
    Returns
    -------
    dict
        Installation result with created items
        
    Example
    -------
    >>> import fabric_arcade as arcade
    >>> arcade.install("mission-artemis-2")
    🚀 Installing Mission Artemis 2...
    ✅ Created Eventhouse: artemis2-telemetry
    ✅ Created Eventstream: artemis2-stream  
    ✅ Created Dashboard: mission-control
    ✅ Created Notebook: artemis2-simulator
    
    Installation complete! Run arcade.play("mission-artemis-2") to start.
    """
    from .deploy import deploy_game
    
    print(f"\n🎮 Installing game: {game_id}")
    print("-" * 40)
    
    result = deploy_game(game_id, workspace)
    
    print("\n✅ Installation complete!")
    print(f"Run arcade.play('{game_id}') to start playing!\n")
    
    return result

def play(game_id: str) -> None:
    """
    Start playing an installed game.
    
    Opens the game's main notebook or dashboard with instructions.
    
    Parameters
    ----------
    game_id : str
        The unique identifier of the installed game
        
    Example
    -------
    >>> import fabric_arcade as arcade
    >>> arcade.play("mission-artemis-2")
    🚀 Starting Mission Artemis 2...
    
    Opening Mission Control Dashboard...
    """
    print(f"\n🎮 Starting game: {game_id}")
    print("-" * 40)
    print("Opening game entry point...")
    # TODO: Implement actual game launch logic
    print("\n🎯 Game started! Follow the instructions in the notebook.\n")

def achievements(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    View your achievements and progress.
    
    Parameters
    ----------
    user_id : str, optional
        User ID to check. If not provided, uses current user.
        
    Returns
    -------
    dict
        Achievement data including badges, stats, and progress
        
    Example
    -------
    >>> import fabric_arcade as arcade
    >>> arcade.achievements()
    
    🏆 Your Achievements
    ==================
    🚀 First Launch - Completed your first project
    ⚡ Speed Demon - Completed a challenge in under 10 min
    
    Progress: 5/20 games completed
    Total play time: 3h 45m
    """
    print("\n🏆 Your Achievements")
    print("=" * 40)
    print("🚀 First Launch - Completed your first project")
    print("⏱️ Real-Time Rookie - Processed 10,000 events")
    print()
    print("Progress: 2/10 games completed")
    print("Total play time: 1h 15m")
    print()
    
    return {
        "badges": ["first-launch", "realtime-rookie"],
        "games_completed": 2,
        "total_games": 10,
        "play_time_minutes": 75
    }
