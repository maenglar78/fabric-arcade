"""
🎮 Fabric Arcade - Learn Microsoft Fabric by Playing

A gamified catalog of projects to learn Real-Time Intelligence,
Data Engineering, Power BI and Data Science through fun experiences.
"""

__version__ = "0.1.0"
__author__ = "Fabric Gaming Community"

from .core import list_games, install, play, achievements
from .catalog import get_catalog, search_games
from .deploy import deploy_game, remove_game

__all__ = [
    "list_games",
    "install", 
    "play",
    "achievements",
    "get_catalog",
    "search_games",
    "deploy_game",
    "remove_game",
]

# Alias for backward compatibility with jumpstart-like interface
list = list_games
