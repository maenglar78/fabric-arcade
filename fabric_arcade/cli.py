"""
Fabric Arcade CLI

Command-line interface for managing Fabric Arcade games.

Usage:
    arcade list                     # List available games
    arcade info <game-id>           # Show game details
    arcade install <game-id> -w <workspace>  # Install game
    arcade uninstall <game-id> -w <workspace>  # Remove game
"""

import argparse
import sys
from typing import Optional

from .catalog import get_catalog, get_game, search_games
from .engine import install, uninstall


def cmd_list(args) -> int:
    """List all available games"""
    print("🎮 Fabric Arcade - Available Games\n")
    print("-" * 60)
    
    games = get_catalog()
    for game in games:
        workloads = ", ".join(w.value for w in game.workloads)
        difficulty = "⭐" * game.difficulty
        print(f"\n{game.icon} {game.name}")
        print(f"   ID: {game.id}")
        print(f"   Workloads: {workloads}")
        print(f"   Difficulty: {difficulty}")
        print(f"   Duration: {game.duration_minutes} min")
    
    print(f"\n{'-' * 60}")
    print(f"Total: {len(games)} games available")
    print("\nUse 'arcade info <game-id>' for details")
    return 0


def cmd_info(args) -> int:
    """Show detailed info about a game"""
    game = get_game(args.game_id)
    
    if not game:
        print(f"❌ Game '{args.game_id}' not found")
        return 1
    
    workloads = ", ".join(w.value for w in game.workloads)
    difficulty = "⭐" * game.difficulty
    
    print(f"\n{game.icon} {game.name}")
    print("=" * 50)
    print(f"\nID: {game.id}")
    print(f"Type: {game.type.value}")
    print(f"Version: {game.version}")
    print(f"\nDescription:\n{game.description}")
    print(f"\nWorkloads: {workloads}")
    print(f"Difficulty: {difficulty}")
    print(f"Duration: {game.duration_minutes} minutes")
    
    print(f"\nTags: {', '.join(game.tags)}")
    
    print("\n" + "=" * 50)
    print("To install, run:")
    print(f"  arcade install {game.id} -w <your-workspace>")
    
    return 0


def cmd_search(args) -> int:
    """Search for games"""
    results = search_games(args.query)
    
    if not results:
        print(f"No games found matching '{args.query}'")
        return 0
    
    print(f"🔍 Found {len(results)} game(s) matching '{args.query}':\n")
    
    for game in results:
        print(f"  {game.icon} {game.name} ({game.id})")
    
    return 0


def cmd_install(args) -> int:
    """Install a game to a workspace"""
    game = get_game(args.game_id)
    
    if not game:
        print(f"❌ Game '{args.game_id}' not found")
        return 1
    
    if not args.workspace:
        print("❌ Workspace name required. Use -w <workspace-name>")
        return 1
    
    try:
        ctx = install(
            game_id=args.game_id,
            workspace=args.workspace,
            prefix=args.prefix or ""
        )
        
        print(f"\n🎮 Game ready! Created items:")
        for name, item_id in ctx.created_items.items():
            print(f"  - {name}: {item_id[:8]}...")
        
        return 0
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return 1


def cmd_uninstall(args) -> int:
    """Remove a game from a workspace"""
    if not args.workspace:
        print("❌ Workspace name required. Use -w <workspace-name>")
        return 1
    
    try:
        uninstall(
            game_id=args.game_id,
            workspace=args.workspace,
            prefix=args.prefix or ""
        )
        return 0
    except Exception as e:
        print(f"❌ Uninstall failed: {e}")
        return 1


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="arcade",
        description="Fabric Arcade - Gamified Learning for Microsoft Fabric"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List all available games")
    list_parser.set_defaults(func=cmd_list)
    
    # info command
    info_parser = subparsers.add_parser("info", help="Show game details")
    info_parser.add_argument("game_id", help="Game ID")
    info_parser.set_defaults(func=cmd_info)
    
    # search command
    search_parser = subparsers.add_parser("search", help="Search for games")
    search_parser.add_argument("query", help="Search query")
    search_parser.set_defaults(func=cmd_search)
    
    # install command
    install_parser = subparsers.add_parser("install", help="Install a game")
    install_parser.add_argument("game_id", help="Game ID")
    install_parser.add_argument("-w", "--workspace", required=True,
                                help="Target workspace name")
    install_parser.add_argument("-p", "--prefix", default="",
                                help="Prefix for created items")
    install_parser.set_defaults(func=cmd_install)
    
    # uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Remove a game")
    uninstall_parser.add_argument("game_id", help="Game ID")
    uninstall_parser.add_argument("-w", "--workspace", required=True,
                                  help="Workspace name")
    uninstall_parser.add_argument("-p", "--prefix", default="",
                                  help="Prefix used during install")
    uninstall_parser.set_defaults(func=cmd_uninstall)
    
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
