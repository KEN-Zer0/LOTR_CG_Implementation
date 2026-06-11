from enum import Enum


class GameConstants:
    """Numeric thresholds that govern win/lose conditions."""

    LOSING_THREAT = 50


class PlayerEngagementType(Enum):
    """Identifies which engagement list a character has been assigned to this round."""

    QUESTING = "questing"
    ATTACKING = "attacking"
    DEFENDING = "defending"