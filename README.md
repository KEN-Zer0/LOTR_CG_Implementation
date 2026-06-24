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
├── main.py                      # Entry point (argparse: expert / random / alphabeta)
├── config/
│   ├── constants.py             # GameConstants, PlayerEngagementType
│   └── limited/
│       ├── cards_list.py        # Enums: Heroes, Allies, Enemies, Locations, Quests, Sphere
│       ├── cards_registry.py    # CARDS dict — single source of truth for all card prototypes
│       └── decks.py             # hero_pool, player_deck, encounter_deck, quest_deck
├── agents/
│   ├── base_agent.py            # BaseAgent ABC — 7 abstract decision methods
│   ├── expert_agent.py          # ExpertAgent — heuristic greedy strategy
│   ├── alpha_beta_agent.py      # AlphaBetaAgent — 2-ply minimax with alpha-beta pruning
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
python main.py              # ExpertAgent (default)
python main.py expert       # ExpertAgent
python main.py random       # RandomAgent
python main.py alphabeta    # AlphaBetaAgent
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

### AlphaBetaAgent — 2-ply minimax z alpha-beta pruningiem

#### Architektura algorytmu

Faza questa jest jedyną fazą z prawdziwym przeszukiwaniem drzewa gry. Pozostałe decyzje (planowanie, podróż, walka) używają tych samych heurystyk co ExpertAgent.

```
MAX node — wybór podzbioru questujących postaci (2^N podzbiorów)
  └── MIN node — worst-case odsłonięcie karty z encounter_deck
        └── alpha cut gdy beta ≤ alpha
```

Dla każdego podzbioru questujących agent sprawdza każdą kartę w encounter_deck i szuka najgorszego możliwego odsłonięcia. `alpha` propagowane z poziomu MAX pozwala ciąć MIN-loop wcześnie.

#### Funkcja oceny — `_evaluate`

```
+ quest.progress × 8        + ally stats (atk+def+wp) × 2    + resources × 0.5
- threat × 2.5              - enemy.threat (staging) × 2
- hero.hp × 5               - enemy (engaged): atk×2.5 + hp×1.5
- kara kwadratowa gdy table_threat ≥ 44
```

#### Faza questa — pełne 2-ply alpha-beta

**Węzeł MAX:** iteracja po wszystkich 2^N podzbiorach dostępnych postaci.

**Węzeł MIN (`_min_encounter_after_quest`):** dla każdego podzbioru przeszukuje całą encounter_deck szukając karty, która da najgorszy wynik po odsłonięciu. Alpha cut przerwie MIN-loop gdy znaleziony wynik jest już gorszy niż najlepsza opcja z wyższego poziomu.

**Optymalizacje przycinania:**
- `_evaluate(state)` obliczany raz dla wszystkich podzbiorów (stan się nie zmienia w trakcie przeszukiwania)
- Podzbiory sortowane malejąco po willpower — wysokie alpha ustawiane wcześnie, więcej MIN-pętli uciętych
- Encounter deck sortowany od najgroźniejszej karty (`_card_danger`) — MIN node szybciej obniża betę i triggeruje alpha cut

**`_reveal_delta`** — szacunek wpływu odsłoniętej karty:
- Wróg z `engagement > table_threat` → idzie do staging, kara `-threat × 2.0`
- Wróg z `engagement ≤ table_threat` → **auto-angażuje się natychmiast** → oblicz `_combat_estimate` z dostępnymi obrońcami (postacie, które NIE questują)
- Lokacja → kara `-threat × 2.0`

Kluczowa różnica względem ExpertAgent: gdy encounter_deck zawiera wroga który auto-angażuje (engagement ≤ table_threat), agent uwzględnia, że questujące postacie będą exhausted i nie będą mogły bronić. Utrzymanie obrońców może być ważniejsze niż wysłanie wszystkich na questa.

**Przykład:** staging_threat = 6, table_threat = 25, encounter_deck = [East Bight Patrol (engagement=5)]:
- Wysłanie wszystkich (wp=6, net=0): zero questujących obrońców → EBP zadaje pełne obrażenia bez obrony
- Wysłanie tylko Éowyn (wp=4, net=−2, threat+2): Eleanor+Thalin wolni → razem zabijają EBP
- Minimax wybiera Éowyn, bo worst-case przy EBP jest mniej kosztowny z dwoma obrońcami

---

### ExpertAgent — szczegółowa taktyka

#### 1. Faza questa — `choose_questing_characters`

```
Czy są dostępne postacie (ready heroes + allies)?
├── NIE → wyślij pustą listę (quest bez postaci)
└── TAK → wyślij WSZYSTKICH gotowych
```

Wszystkie niezexhausted postacie idą na questa. Priorytet: willpower > gotowość bojowa. Każdy punkt willpower niżej od staging threat to +1 do table threat gracza — strata nieodwracalna. Postacie zostaną exhausted, co oznacza że nie mogą bronić ani atakować tego samego wroga w tej samej turze, ale agent akceptuje ten trade-off.

---

#### 2. Faza planowania — `choose_card_to_play`

```
Czy są karty które gracz może sobie pozwolić?
├── NIE → pass (zwróć None, zakończ fazę)
└── TAK → zagraj kartę z NAJMNIEJSZYM kosztem
          └── powtarzaj dopóki brak affordowalnych kart lub agent zwróci None
```

Greedy: najszybciej wejść na planszę = najdłużej generować willpower, atak i obronę. Tania karta zaprzysiężona w turze 2 wygeneruje więcej wartości przez całą grę niż droga karta zaprzysiężona w turze 5.

---

#### 3. Faza podróży — `choose_location`

```
Czy jest aktywna lokacja?
├── TAK → pomiń całą fazę (tylko jedna aktywna lokacja naraz)
└── NIE → czy są lokacje w staging area które gracz może opłacić?
          ├── NIE → pomiń
          └── TAK → jedź do lokacji z NAJWYŻSZYM threat
```

Lokacja w staging area dodaje swój threat co turę do staging threat questa. Wyjęcie jej ze staging natychmiast zmniejsza staging threat — efekt widoczny już w tej samej fazie questa. Agent wybiera lokację z max threatsem, bo jej usunięcie daje największy zysk.

---

#### 4. Faza spotkań — optional engagement — `choose_optional_engagement`

```
Czy są wrogowie w staging area?
├── NIE → nic
└── TAK → NIE angażuj żadnego (zwróć pustą listę)
```

Agent nigdy nie angażuje wroga dobrowolnie. Zaangażowany wróg musi być obsłużony w fazie walki — wymaga exhausted obrońcy i atakujących, nawet jeśli gracz nie jest gotowy. Strategia: czekać aż forced engagement wciągnie wroga naturalnie (gdy table_threat ≥ enemy.engagement), dając czas na zgromadzenie zasobów i sojuszników.

---

#### 5. Faza walki — obrona — `choose_defender`

```
Czy są gotowe (niezexhausted) postacie?
├── NIE → atak undefended → przejdź do choose_undefended_target
└── TAK → czy wśród gotowych sojuszników (Ally) jest chump blocker?
          │   [chump blocker = ally.hp ≤ enemy.attack − ally.defense]
          │   (ally i tak zginie nawet jeśli zablokuje)
          ├── TAK → wybierz chump blockera z NAJMNIEJSZĄ liczbą HP
          │         (najtańsza strata spośród skazanych)
          └── NIE → wybierz postać z NAJWYŻSZĄ obroną (spośród heroes + allies)
                    (minimalizuj obrażenia przebijające obronę)
```

Priorytet chump blockera: sojusznik który i tak zginie można "poświęcić" zamiast tracić bohatera lub lepszego sojusznika. Wybór min HP spośród chump blockerów to wybór najtańszej straty — ally z 1 HP jest bardziej zbędny niż ally z 3 HP który mógłby jeszcze pomóc.

---

#### 6. Faza walki — cel niezablokowanego ataku — `choose_undefended_target`

```
(wywoływane gdy choose_defender zwróciło None)

Wybierz bohatera z NAJWIĘKSZĄ liczbą HP
```

Kieruje obrażenia na najwytrzymalszego bohatera, chroniąc tych z małą liczbą HP przed natychmiastową śmiercią. Bohater z 1 HP zabity przez atak to stała strata (utrata willpower, ataku, obrony na całą grę).

---

#### 7. Faza walki — atak gracza — `choose_attackers`

```
Czy są gotowe (niezexhausted) postacie?
├── NIE → nie atakuj tego wroga
└── TAK → posortuj malejąco po attack
          zacznij dobierać kolejno:
          │
          czy Σ attack − enemy.defense ≥ enemy.hp?  (czy ten zestaw zabije wroga?)
          ├── TAK → zwróć ten minimalny zestaw atakujących
          │         (pozostałe postacie zostają gotowe na kolejnych wrogów)
          └── NIE → dodaj następną postać i sprawdź ponownie
                    │
                    czy przejrzano wszystkich?
                    └── TAK → wróg nieubijany w tej turze
                              → zwróć WSZYSTKICH dostępnych
                              (maksymalizuj obrażenia, zbliż się do zabicia w następnej rundzie)
```

Kluczowa optymalizacja: sortowanie po ataku malejąco + early return przy pierwszym zestawie lethal. Dzięki temu reszta postaci jest exhausted tylko gdy konieczne — mogą wtedy bronić lub atakować kolejnych wrogów w tej samej fazie walki.

---

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

### Benchmark (3 000 games each)

| Agent | Wins | Win rate | Threat defeats | Hero defeats | Time / 1000 games |
|-------|------|----------|---------------|-------------|-------------------|
| AlphaBetaAgent | 2270 / 3000 | **75.7 %** | 0 | 730 | ~2.9 s |
| ExpertAgent | 1202 / 3000 | **40.1 %** | 0 | 1798 | ~0.3 s |
| RandomAgent | 2 / 3000 | **0.1 %** | 12 | 2986 | ~0.3 s |

AlphaBetaAgent wygrywa niemal 2× częściej niż ExpertAgent (75.7 % vs 40.1 %) kosztem ~10× wolniejszego czasu na grę. Wszystkie porażki to śmierć bohaterów — threat nigdy nie osiąga 50 przy rozsądnych agentach.

## Card Registry

All card prototypes live in `config/limited/cards_registry.py` as a single `CARDS` dict with keyword-argument stats. Deck lists in `decks.py` are built from `CARDS[...].copy()`:

```python
from config.limited.cards_registry import CARDS
from config.limited.cards_list import Allies

card = CARDS[Allies.Wandering_Took].copy()  # independent instance, safe to mutate
```

## Tests

```bash
conda activate lotr-cg-implementation
python -m pytest -vq
```

280 testów pokrywa klasy kart, wszystkie 7 faz, agentów i integrację Table/Game.

## Requirements

- Python 3.11 (`environment.yml` — środowisko conda `lotr-cg-implementation`)
- `pytest` (doinstaluj: `pip install pytest`)
