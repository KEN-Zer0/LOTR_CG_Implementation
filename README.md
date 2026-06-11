# LOTR LCG Implementation

A Python simulation of the cooperative **Lord of the Rings Living Card Game** (Fantasy Flight Games). The game runs in a console loop with a pluggable AI agent executing all decisions — no UI required.

## Overview

The simulator implements the full 7-phase round structure of the LOTR LCG, configured for the **Passage through Mirkwood** scenario from the Core Set. Agents follow the **Strategy Pattern**: swap decision-making logic without touching any phase or game code.

## Scenario

**Passage through Mirkwood**

- **Heroes:** Éowyn (Spirit), Eleanor (Spirit), Thalin (Tactics)
- **Quest cards:** Flies and Spiders → A Fork in the Road → Beorn's Path
- **Encounter deck:** Dol Guldur Orcs, Chieftain Ufthak, Dol Guldur Beastmaster, Forest Spider, East Bight Patrol, Black Forest Bats, King Spider, Hummerhorns, Ungoliant's Spawn + 6 Mirkwood locations

**Win condition:** complete all three quest stages  
**Lose conditions:** table threat ≥ 50, or all heroes dead

## Project Structure

```
LOTR_CG_Implementation/
├── main.py                      # Entry point (argparse: expert / random)
├── config/
│   ├── constants.py             # GameConstants, PlayerEngagementType
│   └── limited/
│       ├── cards_list.py        # Enums: Heroes, Allies, Enemies, Locations, Quests, Sphere
│       ├── cards_registry.py    # CARDS dict — single source of truth for all card prototypes
│       └── decks.py             # hero_pool, player_deck, encounter_deck, quest_deck
├── agents/
│   ├── base_agent.py            # BaseAgent ABC — 7 abstract decision methods
│   ├── expert_agent.py          # ExpertAgent — heuristic greedy strategy
│   └── random_agent.py          # RandomAgent — fully random decisions
└── src/
    ├── cards/
    │   ├── base_card.py
    │   ├── creatures/
    │   │   ├── base_creature.py          # attack, defense, hit_points
    │   │   ├── enemy.py                  # threat, engagement_cost
    │   │   └── player_creatures/
    │   │       ├── base_player_creature.py  # willpower, sphere, exhausted, resource_pool
    │   │       ├── hero.py
    │   │       └── ally.py               # cost
    │   └── progress_objective/
    │       ├── progress_objective.py     # progress, required_progress
    │       ├── quest.py
    │       └── location.py               # threat contribution, travel_cost
    ├── game/
    │   ├── game.py                       # Phase orchestration, Game(agent=...) entry point
    │   └── phases/
    │       ├── phase.py
    │       ├── resources_phase.py
    │       ├── planning_phase.py
    │       ├── quest_phase.py
    │       ├── travel_phase.py
    │       ├── encounter_phase.py
    │       ├── combat_phase.py
    │       └── refresh_phase.py
    └── table/
        └── table.py                      # Full mutable game state
```

## Card Hierarchy

```
BaseCard (name: Enum)
├── Creature (attack, defense, hit_points)
│   ├── Enemy (threat, engagement_cost)
│   └── PlayerCreature (willpower, sphere, exhausted, resource_pool)
│       ├── Hero (starting_threat)
│       └── Ally (cost)
└── ProgressObjective (progress, required_progress)
    ├── Quest (scenario)
    └── Location (threat, travel_cost)
```

## Round Structure

| # | Phase | Description |
|---|-------|-------------|
| 1 | Resources | Each hero gains 1 resource; draw 1 card |
| 2 | Planning | Play allies from hand (agent chooses which card) |
| 3 | Quest | Characters commit; willpower vs staging threat → progress or threat gain |
| 4 | Travel | Agent chooses one location from staging to make active |
| 5 | Encounter | Reveal top encounter card; forced + optional enemy engagement |
| 6 | Combat | Enemies attack (agent declares defenders), then player attacks (agent picks attackers) |
| 7 | Refresh | Ready all characters; table threat +1 |

## Running

```bash
python main.py           # ExpertAgent (default)
python main.py expert    # ExpertAgent
python main.py random    # RandomAgent
```

## Agent System

All decision points are defined in `BaseAgent` as abstract methods:

| Method | Called from | Returns |
|--------|-------------|---------|
| `choose_questing_characters(state, available)` | Quest phase | `list[Hero \| Ally]` |
| `choose_card_to_play(state, playable)` | Planning phase | `Ally \| None` |
| `choose_location(state, eligible)` | Travel phase | `Location \| None` |
| `choose_optional_engagement(state, available)` | Encounter phase | `list[Enemy]` |
| `choose_defender(state, enemy, available)` | Combat phase | `Hero \| Ally \| None` |
| `choose_undefended_target(state, enemy)` | Combat phase | `Hero` |
| `choose_attackers(state, enemy, available)` | Combat phase | `list[Hero \| Ally]` |

### Plugging in an agent

```python
from src.game.game import Game
from agents import ExpertAgent, RandomAgent

game = Game(agent=ExpertAgent())   # or RandomAgent()
```

### Implementing a custom agent

```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def choose_questing_characters(self, state, available):
        return available  # commit everyone

    def choose_card_to_play(self, state, playable):
        return playable[0] if playable else None

    # ... implement remaining 5 methods
```

### Benchmark (1 000 games each, ~6 s per 100)

| Agent | Wins | Win rate |
|-------|------|----------|
| ExpertAgent | 416 / 1000 | **41.6 %** |
| RandomAgent | 36 / 1000 | **3.6 %** |

## Card Registry

All card prototypes live in `config/limited/cards_registry.py` as a single `CARDS` dict with keyword-argument stats. Deck lists in `decks.py` are built from `CARDS[...].copy()`:

```python
from config.limited.cards_registry import CARDS
from config.limited.cards_list import Allies

card = CARDS[Allies.Wandering_Took].copy()  # independent instance, safe to mutate
```

## Tests

167 tests covering card classes, all 7 phases, agents, and game/table integration:

```bash
python -m pytest -vq
```

Tests are organised by topic:

```
tests/
├── agents/        # ExpertAgent decisions (questing, planning, combat) + RandomAgent contracts
├── cards/         # Card class behaviour and hierarchy
├── game/phases/   # Phase mechanics (no agent substitution)
├── game/          # Full-round Game integration
└── table/         # Table state and win/lose conditions
```

## Requirements

- Python 3.10+
- `pytest` (dev dependency, install via `.venv`)
