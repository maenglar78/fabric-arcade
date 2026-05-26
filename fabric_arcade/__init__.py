"""
🎮 Fabric Arcade - Learn Microsoft Fabric by Playing

A gamified catalog of projects to learn Real-Time Intelligence,
Data Engineering, Power BI and Data Science through fun experiences.

Usage:
    >>> import fabric_arcade as arcade
    >>> arcade.list()           # List available games
    >>> arcade.install("fabric-racing-game", workspace="MyWorkspace")
    >>> arcade.uninstall("fabric-racing-game", workspace="MyWorkspace")
"""

__version__ = "0.1.0"
__author__ = "Fabric Gaming Community"

from .catalog import get_catalog, get_game, search_games
from .engine import install, uninstall, FabricClient, GameDeployer

__all__ = [
    # Catalog functions
    "get_catalog",
    "get_game",
    "search_games",
    # Deployment functions
    "install",
    "uninstall",
    "FabricClient",
    "GameDeployer",
]


def list():
    """List all available games"""
    games = get_catalog()
    print("🎮 Fabric Arcade - Available Games\n")
    for game in games:
        print(f"  {game.icon} {game.name} ({game.id})")
    print(f"\nTotal: {len(games)} games")
    return games
