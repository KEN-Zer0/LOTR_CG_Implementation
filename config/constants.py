from enum import Enum


class GameConstants:
    """Numeric thresholds that govern win/lose conditions and per-round increments."""

    LOSING_THREAT = 50
    THREAT_PER_ROUND = 1
    RESOURCES_PER_HERO_PER_ROUND = 1


class PlayerEngagementType(Enum):
    """Identifies which engagement list a character has been assigned to this round."""

    QUESTING = "questing"
    ATTACKING = "attacking"
    DEFENDING = "defending"