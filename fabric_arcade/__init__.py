"""
🎮 Fabric Arcade - Learn Microsoft Fabric by Playing

A gamified catalog of projects to learn Real-Time Intelligence,
Data Engineering, Power BI and Data Science through fun experiences.

Usage (in Fabric Notebook):
    >>> %pip install -q fabric-arcade
    >>> from fabric_arcade import arcade
    >>> arcade.list()              # List available games
    >>> arcade.install("fabric-racing-game")  # Install in current workspace!

Usage (Local CLI):
    >>> arcade list
    >>> arcade install fabric-racing-game -w MyWorkspace
"""

__version__ = "0.1.3"
__author__ = "Fabric Gaming Community"

from .catalog import get_catalog, get_game, search_games
from .engine import install, uninstall, FabricClient, GameDeployer

# Fabric-native API (for use inside Fabric notebooks)
from .fabric_api import arcade, Arcade

__all__ = [
    # Fabric-native API (recommended for Fabric notebooks)
    "arcade",
    "Arcade",
    # Catalog functions
    "get_catalog",
    "get_game",
    "search_games",
    # Deployment functions (CLI)
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
