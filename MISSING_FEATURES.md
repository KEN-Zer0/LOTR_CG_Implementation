# Analiza brakujących mechanik — LOTR LCG

Dokument porównuje aktualną implementację z pełnymi zasadami gry
*The Lord of the Rings: The Card Game* (Fantasy Flight Games).

---

## Co jest zaimplementowane (poprawnie)

| Mechanika | Plik |
|---|---|
| 7-fazowa pętla rundy | `src/game/game.py` |
| Faza zasobów: +1 zasób/bohater, dobierz kartę | `resources_phase.py` |
| Faza planowania: zagraj sojuszników (najtańszego pierwszego) | `planning_phase.py` |
| Faza questa: willpower vs staging threat, progress, awans questa | `quest_phase.py` |
| Faza podróży: podróż do lokacji, koszt podróży, delegacja wyboru do agenta | `travel_phase.py` |
| Faza spotkań: reveal karty, optional engagement (agent), auto-engage wrogów | `encounter_phase.py` |
| Faza walki: atak wroga (obrona/chump/undefended), atak gracza (minimalni atakujący) | `combat_phase.py` |
| Faza odnowienia: odśwież postacie, +1 threat | `refresh_phase.py` |
| Hierarchia kart: BaseCard, Creature, Enemy, PlayerCreature, Hero, Ally | `src/cards/` |
| Quest, Location, ProgressObjective | `src/cards/progress_objective/` |
| Warunek przegranej: threat ≥ 50 lub wszyscy bohaterowie martwi | `src/table/table.py` |
| Warunek wygranej: quest_deck pusty (wszystkie questy ukończone) | `src/table/table.py`, `main.py` |
| Wzorzec `_choose_*()` do nadpisania przez AI agentów | wszystkie fazy |
| ExpertAgent: heurystyczny agent (quest all, chump block, minimalni atakujący) | `agents/expert_agent.py` |
| RandomAgent | `agents/random_agent.py` |
| Argparse wybór agenta z linii poleceń | `main.py` |

---

## Znalezione błędy (bugs)

### Naprawione

| Bug | Status |
|---|---|
| `staging_threat()` permanentnie podnosił `table_threat` | ✅ naprawiony — metoda usunięta |
| `encounter_deck.pop()` zamiast `pop(0)` | ✅ naprawiony — `table.reveal_encounter_card()` używa `pop(0)` |
| `_choose_location()` — `max(loc.progress)` zawsze 0 | ✅ naprawiony — delegacja do agenta; ExpertAgent wybiera `max(loc.threat)` |
| Warunek wygranej nie istniał | ✅ naprawiony — `check_win_condition()` + pętla w `main.py` |

---

### Nowo zidentyfikowane

#### KRYTYCZNY — `Table.__init__()` — płytkie kopie list (shared state)

`Table.__init__` robi `hero_pool.copy()`, `player_deck.copy()`, `encounter_deck.copy()`, `quest_deck.copy()` — to są **płytkie kopie list**, nie kopie obiektów wewnątrz. Wszystkie instancje `Table` dzielą te same obiekty kart:

```python
# Table.__init__ — BUG
self.player_heroes  = hero_pool.copy()       # nowa lista, ale te same obiekty Hero
self.encounter_deck = encounter_deck.copy()  # nowa lista, ale te same obiekty Enemy/Location
self.quest_deck     = quest_deck.copy()      # nowa lista, ale te same obiekty Quest
```

Jeśli gra zmodyfikuje HP wroga lub postęp questa, kolejna instancja `Table` zobaczy zmodyfikowane obiekty. `conftest.py` ma częściowy workaround (tworzy nowych bohaterów ręcznie), ale `quest_deck`, `player_deck`, `encounter_deck` nadal są podatne.

```python
# Poprawna implementacja:
self.player_heroes  = [hero.copy() for hero in hero_pool]
self.player_deck    = [card.copy() for card in player_deck]
self.encounter_deck = [card.copy() for card in encounter_deck]
self.quest_deck     = [card.copy() for card in quest_deck]
```

#### ŚREDNI — `EncounterPhase._optional_engagement()` — niezgodność z zasadami (limit 1 wroga)

Zasady: w kroku optional engagement każdy gracz może zaangażować **jednego** wroga.
Implementacja: `_choose_optional_engagement()` zwraca `list[Enemy]` — agent może zaangażować dowolną liczbę.

```python
# base_agent.py — niezgodna sygnatura
def choose_optional_engagement(...) -> list[Enemy]:  # powinno być Enemy | None
```

#### NISKI — `EncounterPhase._optional_engagement()` — brak ochrony przed duplikatem w liście

Jeśli agent zwróci tego samego wroga dwa razy, drugie `_engage()` wyrzuci `ValueError` przy `encounter_staging.remove(enemy)`. Poprawka: sprawdzić `if enemy in self.table.encounter_staging` przed wywołaniem `_engage()`.

#### NISKI — `RefreshPhase.ready_player_characters()` — martwy kod

Iteruje po `questing + attacking + defending`, ale te listy są zawsze puste w momencie wykonania RefreshPhase:
- `questing` jest czyszczone przez `QuestPhase.execute()` przed TravelPhase
- `attacking` i `defending` są czyszczone przez `CombatPhase.execute()` przed RefreshPhase

Efektywnie `ready_player_characters()` readies tylko `player_heroes + player_board`.

#### NISKI — `ExpertAgent.choose_defender()` — `hasattr` zamiast `isinstance`

```python
allies = [c for c in available if hasattr(c, "cost")]  # kruche duck typing
# powinno być:
allies = [c for c in available if isinstance(c, Ally)]
```

---

## Brakujące typy kart

### Karty gracza
| Typ | Opis | Status |
|---|---|---|
| **Ally** | sojusznik | ✅ zaimplementowany |
| **Attachment** | attachment do bohatera/sojusznika (tarcza, broń, umiejętność) | ❌ brak |
| **Event** | jednorazowy efekt grany z ręki, odrzucany po zagraniu | ❌ brak |

### Karty spotkań (encounter deck)
| Typ | Opis | Status |
|---|---|---|
| **Enemy** | wróg | ✅ zaimplementowany |
| **Location** | lokacja | ✅ zaimplementowana |
| **Treachery** | efekt "When Revealed" bez statystyk, natychmiastowy | ❌ brak |
| **Objective** | neutralna karta, którą gracz może zdobyć | ❌ brak |

### Karty questa
| Typ | Opis | Status |
|---|---|---|
| **Quest** | quest card z wymaganym postępem | ✅ zaimplementowany |
| **Side Quest** | opcjonalne boczne questa (z późniejszych zestawów) | ❌ brak |

---

## Brakujące słowa kluczowe (keywords)

### Keywords kart spotkań
| Keyword | Zasada | Status |
|---|---|---|
| **Surge** | Po reveal tej karty, odkryj dodatkowo 1 kartę z encounter deck | ❌ brak |
| **Doomed X** | Po reveal — każdy gracz podnosi zagrożenie o X | ❌ brak |
| **Guarded** | Obiektywna karta przyczepia się do następnej odkrytej karty encounter; nie można jej zdobyć dopóki karta jest przyczepiona | ❌ brak |
| **Archery X** | Na początku fazy walki, zadaj X obrażeń postaciom gracza (dowolny podział) | ❌ brak |
| **Toughness X** | Wróg redukuje otrzymywane obrażenia o X przy każdym trafieniu | ❌ brak |
| **Indestructible** | Wróg nie może zostać zabity przez obrażenia | ❌ brak |
| **Regenerate X** | Wróg odzyskuje X HP na początku fazy odnowienia | ❌ brak |

### Keywords kart gracza
| Keyword | Zasada | Status |
|---|---|---|
| **Sentinel** | Postać może bronić ataków skierowanych przeciwko innym graczom | ❌ brak (dotyczy trybu wieloosobowego) |
| **Ranged** | Postać może atakować wrogów zaangażowanych z innymi graczami | ❌ brak (dotyczy trybu wieloosobowego) |
| **Secrecy X** | Obniż koszt karty o X, jeśli zagrożenie gracza ≤ 20 | ❌ brak |
| **Restricted** | Postać może mieć maksymalnie 2 attachmenty z tym keyword | ❌ brak (wymaga attachmentów) |

### Specjalne typy questo-fazowe
| Keyword | Zasada | Status |
|---|---|---|
| **Battle** | W fazie questa postacie wkładają do questa wartość Attack zamiast Willpower | ❌ brak |
| **Siege** | W fazie questa postacie wkładają wartość Defense zamiast Willpower | ❌ brak |

---

## Brakujące mechaniki fazowe

### Shadow Cards (Karty cienia) — brak w całości
W fazie walki, **zanim** każdy zaangażowany wróg zaatakuje, odkrywa się dla niego 1 kartę cienia
(face-down z encounter deck). Karta ta może zawierać efekt "Shadow:", który modyfikuje atak
(np. zadaje dodatkowe obrażenia, angażuje dodatkowego wroga). Implementacja wymaga:
- `Enemy._shadow_card` — przechowywanie karty cienia
- `CombatPhase._deal_shadow_cards()` — rozdanie kart cienia na początku fazy walki
- `CombatPhase._resolve_shadow_effect()` — rozpatrzenie efektu cienia podczas ataku wroga

### Action Windows — brak w całości
Pomiędzy każdym sub-krokiem fazy gracze mogą grać karty Event i uruchamiać zdolności.
Aktualnie gra jest w pełni deterministyczna bez okien interakcji. Główne okna:
- **1.3**: po fazie zasobów (przed planowaniem)
- **2.2**: podczas planowania — graj sojuszników i attachmenty
- **3.1** / **3.2** / **3.3** / **3.4**: w fazie questa — przed/po zobowiązaniu, przed/po resolvie
- **4.2**: po podróży
- **5.2** / **5.3**: w fazie spotkań
- **6.2** / **6.4.x** / **6.8.x**: wielokrotne okna w fazie walki
- **7.4**: po wzroście zagrożenia

### Sphere Resource Matching (dopasowanie sfer) — brak
W zasadach zasoby z bohatera danej sfery mogą opłacać tylko karty tej samej sfery
(lub Neutral). Aktualnie `PlanningPhase` używa sumy zasobów ze wszystkich bohaterów bez weryfikacji sfery.

```python
# aktualna implementacja (uproszczona):
def _total_resources(self) -> int:
    return sum(hero.resource_pool for hero in self.table.player_heroes)

# zgodna z zasadami — np. przy płaceniu za kartę Spirit:
# można użyć tylko zasobów bohaterów Spirit + Neutral
```

### Efekty kart — "When Revealed" / "Travel" / "Response" — brak
- **When Revealed**: efekt uruchamiany przy odkryciu karty encounter (treachery, niektóre lokacje i wrogowie)
- **Travel**: efekt uruchamiany przy podróży do lokacji
- **Forced**: efekt wymuszony w konkretnym momencie rundy
- **Response**: efekt uruchamiany w odpowiedzi na zdarzenie

---

## Brakujące dane w config

| Brak | Uwaga |
|---|---|
| Karty Treachery w `encounter_deck` | Scenariusz "Passage through Mirkwood" zawiera: *Caught in a Web*, *Driven by Shadow*, *Misty Mountain Orcs*, *The Necromancer's Reach*, *Wargs* |
| Attachment karty w `player_deck` | W scenariuszu brak, ale klasa `Attachment` jest potrzebna |
| Event karty w `player_deck` | *Gandalf* i inne karty mają wersje Event |
| Sfery `Leadership` i `Lore` | Zdefiniowane są tylko Spirit, Tactics, Neutral |
| Duplikaty kart w talii | Scenariusz wymaga wielu kopii tych samych kart; `decks.py` ma po 1 kopii każdej |

---

## Brak trybu wieloosobowego

Gra LOTR LCG obsługuje 1–4 graczy. Aktualnie:
- `Table` przechowuje dane tylko 1 gracza
- Faza planowania iteruje po 1 graczu
- Sentinel/Ranged nie mają sensu bez innych graczy
- Kolejność graczy (first player token) nie istnieje

---

## Priorytetyzacja

Dla uzyskania grywalnej symulacji (singleplayer, 1 scenariusz):

| Priorytet | Zadanie |
|---|---|
| 🟠 WYSOKI | Zaimplementuj karty Treachery + rozpatrzenie "When Revealed" |
| 🟠 WYSOKI | Zaimplementuj Shadow Cards w fazie walki |
| 🟠 WYSOKI | Dodaj keyword **Surge** (bardzo częsty w kartach encounter) |
| 🟠 WYSOKI | Dodaj duplikaty kart do `decks.py` (1 kopia każdej to za mało) |
| 🟡 ŚREDNI | Sphere resource matching |
| 🟡 ŚREDNI | Keyword **Doomed X** i **Archery X** |
| 🟡 ŚREDNI | Klasa Attachment + Event + ich wsparcie w Planning Phase |
| 🟢 NISKI | Keyword Toughness, Indestructible, Regenerate, Battle, Siege |
| 🟢 NISKI | Action windows |
| ⚪ OPCJONALNY | Tryb wieloosobowy (Sentinel, Ranged, kolejność graczy) |
| ⚪ OPCJONALNY | Side Quests, Objective cards |
