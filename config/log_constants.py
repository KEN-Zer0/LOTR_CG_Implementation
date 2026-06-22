"""
Constants shared across the logging layer (LoggingGame, LoggingAgent, Logger).

Separators and markers control the visual structure of log output.
Enums provide stable keys for phase names, stat tracking and game snapshots.
File-logging constants drive log file naming and directory layout.
"""

from enum import StrEnum
from pathlib import Path

ROUND_SEPARATOR = "=" * 60
STATS_SEPARATOR = "-" * 60
PHASE_FILL      = ("- " * 5).rstrip()

NEW_MARKER = "  # New!"
INDENT_4   = " " * 4
BULLET     = f"{INDENT_4}-> "
INDENT     = "         "


class CardState(StrEnum):
    EXHAUSTED = "exhausted"
    READY     = "ready"


class PhaseKey(StrEnum):
    RESOURCES = "ResourcesPhase"
    PLANNING  = "PlanningPhase"
    QUEST     = "QuestPhase"
    TRAVEL    = "TravelPhase"
    ENCOUNTER = "EncounterPhase"
    COMBAT    = "CombatPhase"
    REFRESH   = "RefreshPhase"


class StatKey(StrEnum):
    RESOURCES_GENERATED = "resources_generated"
    RESOURCES_SPENT     = "resources_spent"
    ALLIES_PLAYED       = "allies_played"
    ENEMIES_DEFEATED    = "enemies_defeated"
    DAMAGE_TO_ENEMIES   = "damage_to_enemies"
    DAMAGE_TO_HEROES    = "damage_to_heroes"
    LOCATIONS_FINISHED  = "locations_finished"


class SnapshotKey(StrEnum):
    THREAT              = "threat"
    HEROES              = "heroes"
    BOARD               = "board"
    STAGING             = "staging"
    ENGAGED             = "engaged"
    HAND                = "hand"
    QUEST_NAME          = "quest_name"
    QUEST_PROGRESS      = "quest_progress"
    QUEST_REQUIRED      = "quest_required"
    ACTIVE_LOC          = "active_loc"
    ACTIVE_LOC_PROGRESS = "active_loc_progress"
    TOTAL_RESOURCES     = "total_resources"


# ── used by Logger to name and locate log files on disk ───────
LOGS_DIR      = Path("logs")
LOG_PREFIX    = "game-log"
LOG_GLOB      = f"{LOG_PREFIX}-*.txt"
LOG_DT_FORMAT = "%d-%m-%Y-%H-%M"
