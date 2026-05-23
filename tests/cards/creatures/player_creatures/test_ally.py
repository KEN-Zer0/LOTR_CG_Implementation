import pytest
from src.cards import Ally


class TestAlly:
    @pytest.fixture
    def gandalf(self):
        """Create a standard Ally instance for testing."""
        return Ally(
            name="Gandalf",
            attack=4,
            defense=4,
            max_hit_points=5,
            willpower=4,
            sphere_of_influence="Neutral",
            cost=5
        )

    def test_init(self, gandalf):
        """Check if all attributes are set correctly on creation."""
        assert gandalf.name == "Gandalf"
        assert gandalf.attack == 4
        assert gandalf.defense == 4
        assert gandalf.max_hit_points == 5
        assert gandalf.hit_points == 5  # Starts at max HP
        assert gandalf.willpower == 4
        assert gandalf.sphere_of_influence == "Neutral"
        assert gandalf.cost == 5

    def test_cost_is_read_only(self, gandalf):
        """Verify that cost cannot be modified directly."""
        assert gandalf.cost == 5
        with pytest.raises(AttributeError):
            gandalf.cost = 3

    def test_copy_creates_new_object(self, gandalf):
        """Verify copy is a different object with same stats."""
        gandalf_copy = gandalf.copy()

        assert gandalf_copy is not gandalf
        assert gandalf_copy.name == gandalf.name
        assert gandalf_copy.cost == gandalf.cost

    def test_copy_preserves_damage(self, gandalf):
        """Verify copy keeps the current hit points (damage)."""
        # Simulate taking 2 damage (5 max - 2 damage = 3 HP left)
        gandalf._hit_points = 3

        gandalf_copy = gandalf.copy()

        assert gandalf_copy.hit_points == 3
        assert gandalf_copy.max_hit_points == 5

    def test_copy_independence(self, gandalf):
        """Check that changing the copy does not affect the original."""
        gandalf_copy = gandalf.copy()
        gandalf_copy._hit_points = 1  # Heavily damaged

        # Original should still be healthy
        assert gandalf.hit_points == 5
        assert gandalf_copy.hit_points == 1