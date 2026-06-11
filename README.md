# LOTR LCG Implementation

A Python simulation of the cooperative **Lord of the Rings Living Card Game** (Fantasy Flight Games). The game runs in a console loop with an auto-player executing all decisions using default greedy strategies — no UI required.

## Overview

The simulator implements the full round structure of the LOTR LCG, currently configured for the **Passage through Mirkwood** scenario from the Core Set. The codebase is designed so that every decision point (`_choose_*` methods in each phase) can be overridden by AI agent subclasses.

## Scenario

**Passage through Mirkwood**

- **Heroes:** Éowyn (Spirit), Eleanor (Spirit), Thalin (Tactics)
- **Quest cards:** Flies and Spiders → A Fork in the Road → Beorn's Path
- **Encounter deck:** Dol Guldur Orcs, Chieftain Ufthak, Dol Guldur Beastmaster, Forest Spider, East Bight Patrol, Black Forest Bats, King Spider, Hummerhorns, Ungoliant's Spawn, and 6 Mirkwood locations

**Win condition:** complete all three quest stages  
**Lose conditions:** table threat reaches 50, or all heroes are dead

## Project Structure

```
LOTR_CG_Implementation/
├── main.py                  # Entry point
├── config/
│   ├── constants.py         # LOSING_THREAT, PlayerEngagementType enum
│   ├── cards_list.py        # Card name enums (Heroes, Allies, Enemies, Locations, Quests)
│   ├── cards_dict.py        # Card lookup dictionary
│   └── all_cards_deck.py    # Deck definitions (hero_pool, player_deck, encounter_deck, quest_deck)
├── src/
│   ├── cards/
│   │   ├── base_card.py
│   │   ├── creatures/
│   │   │   ├── base_creature.py   # attack, defense, hit_points
│   │   │   ├── enemy.py           # threat, engagement_cost
│   │   │   └── player_creatures/
│   │   │       ├── base_player_creature.py  # willpower, sphere, exhausted, resource_pool
│   │   │       ├── hero.py                  # starting_threat, is_alive
│   │   │       └── ally.py                  # cost
│   │   └── progress_objective/
│   │       ├── progress_objective.py  # progress, required_progress
│   │       ├── quest.py
│   │       └── location.py            # threat contribution
│   ├── game/
│   │   ├── game.py            # Game loop, phase orchestration
│   │   └── phases/
│   │       ├── phase.py           # Base Phase class
│   │       ├── resources_phase.py # Heroes gain resources, draw cards
│   │       ├── planning_phase.py  # Play allies from hand
│   │       ├── quest_phase.py     # Willpower vs staging threat
│   │       ├── travel_phase.py    # Travel to a staging location
│   │       ├── encounter_phase.py # Reveal encounter card, enemy engagement
│   │       ├── combat_phase.py    # Enemy attacks, then player attacks
│   │       └── refresh_phase.py   # Ready characters, +1 threat
│   └── table/
│       └── table.py           # Full game state
└── tests/                     # Unit tests for all card classes
```

## Card Hierarchy

```
BaseCard (name: Heroes | Allies | Enemies | Locations | Quests)
├── Creature (attack, defense, hit_points)
│   ├── Enemy (threat, engagement_cost)
│   └── PlayerCreature (willpower, sphere, exhausted, resource_pool)
│       ├── Hero (starting_threat)
│       └── Ally (cost)
└── ProgressObjective (progress, required_progress)
    ├── Quest
    └── Location (threat)
```

## Round Structure

Each round executes 7 phases in order:

| # | Phase | Description |
|---|-------|-------------|
| 1 | Resources | Each hero gains 1 resource; draw 1 card |
| 2 | Planning | Play allies from hand (cheapest first) |
| 3 | Quest | Characters commit to the quest; willpower vs staging threat determines progress or threat gain |
| 4 | Travel | Travel to one location from the staging area |
| 5 | Encounter | Reveal top encounter card; enemies with `engagement_cost ≤ table_threat` engage |
| 6 | Combat | Enemies attack (player declares defenders), then player attacks enemies |
| 7 | Refresh | Ready all exhausted characters; table threat +1 |

## Running

```bash
python main.py
```

The game runs automatically until victory or defeat and prints the outcome.

## Extending with AI Agents

Every phase exposes `_choose_*` methods that encode each decision point. Subclass any phase and override these methods to implement custom strategies or AI agents:

```python
class MyQuestPhase(QuestPhase):
    def _choose_questers(self, available):
        # custom logic
        ...

class MyGame(Game):
    def __init__(self):
        super().__init__()
        self.phases[2] = MyQuestPhase(self.table)
```

Key override points:

- `CombatPhase._choose_defender(enemy, available)` — pick a defender or leave undefended
- `CombatPhase._choose_attackers(enemy, available)` — pick attackers
- `CombatPhase._choose_undefended_target(enemy)` — pick which hero absorbs unblocked damage
- `QuestPhase._choose_questers(available)` — commit characters to the quest
- `PlanningPhase._choose_card(hand)` — pick which ally to play

## Tests

Unit tests cover all card classes:

```bash
python -m pytest tests/
```

## Requirements

- Python 3.10+
- No external dependencies
