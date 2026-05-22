from enum import Enum


class GameConstants:
    LOSING_THREAT = 50


class PlayerEngagementType(Enum):
    QUESTING = "questing"
    ATTACKING = "attacking"
    DEFENDING = "defending"