"""
Tests for Fabric Arcade catalog module
"""

import pytest
from fabric_arcade.catalog import get_catalog, get_game, search_games
from fabric_arcade.core import Game, GameType, Workload, Difficulty


class TestCatalog:
    """Test catalog functionality"""

    def test_get_catalog_returns_games(self):
        """Catalog should return a list of games"""
        catalog = get_catalog()
        assert isinstance(catalog, list)
        assert len(catalog) > 0
        assert all(isinstance(game, Game) for game in catalog)

    def test_all_games_have_required_fields(self):
        """All games should have required fields"""
        catalog = get_catalog()
        for game in catalog:
            assert game.id is not None
            assert game.name is not None
            assert game.description is not None
            assert game.type is not None
            assert len(game.workloads) > 0
            assert game.difficulty is not None
            assert game.duration_minutes > 0

    def test_get_game_by_id(self):
        """Should retrieve a specific game by ID"""
        game = get_game("mission-artemis-2")
        assert game is not None
        assert game.id == "mission-artemis-2"
        assert game.name == "Mission Artemis 2"

    def test_get_game_returns_none_for_invalid_id(self):
        """Should return None for non-existent game"""
        game = get_game("non-existent-game")
        assert game is None

    def test_search_games_by_query(self):
        """Should find games by search query"""
        results = search_games("space")
        assert len(results) >= 1
        # Artemis should be in results
        assert any("artemis" in g.id.lower() for g in results)

    def test_search_games_by_workload(self):
        """Should filter games by workload"""
        results = search_games("", workloads=[Workload.RTI])
        assert len(results) > 0
        assert all(Workload.RTI in g.workloads for g in results)

    def test_search_games_by_difficulty(self):
        """Should filter games by difficulty"""
        results = search_games("", max_difficulty=Difficulty.BEGINNER)
        for game in results:
            assert game.difficulty <= Difficulty.BEGINNER

    def test_search_games_by_type(self):
        """Should filter games by type"""
        results = search_games("", game_type=GameType.MISSION)
        assert len(results) > 0
        assert all(g.type == GameType.MISSION for g in results)


class TestGame:
    """Test Game model"""

    def test_game_creation(self):
        """Should create a valid Game instance"""
        game = Game(
            id="test-game",
            name="Test Game",
            description="A test game",
            type=GameType.ARCADE,
            workloads=[Workload.PBI],
            difficulty=Difficulty.BEGINNER,
            duration_minutes=10,
            icon="🎮",
            tags=["test"],
            achievements=[]
        )
        assert game.id == "test-game"
        assert game.type == GameType.ARCADE

    def test_game_difficulty_levels(self):
        """Difficulty enum should have correct values"""
        assert Difficulty.BEGINNER.value == 1
        assert Difficulty.INTERMEDIATE.value == 2
        assert Difficulty.ADVANCED.value == 3

    def test_workload_enum(self):
        """Workload enum should have all expected values"""
        assert Workload.RTI is not None
        assert Workload.DE is not None
        assert Workload.PBI is not None
        assert Workload.DW is not None
        assert Workload.DS is not None


class TestSpecificGames:
    """Test specific game entries"""

    def test_mission_artemis_2_exists(self):
        """Mission Artemis 2 should be in catalog"""
        game = get_game("mission-artemis-2")
        assert game is not None
        assert Workload.RTI in game.workloads
        assert game.difficulty == Difficulty.ADVANCED

    def test_fabric_racing_game_exists(self):
        """Fabric Racing Game should be in catalog"""
        game = get_game("fabric-racing-game")
        assert game is not None
        assert Workload.RTI in game.workloads
        assert "html5" in game.tags or "multiplayer" in game.tags

    def test_all_games_have_unique_ids(self):
        """All game IDs should be unique"""
        catalog = get_catalog()
        ids = [game.id for game in catalog]
        assert len(ids) == len(set(ids)), "Duplicate game IDs found"
