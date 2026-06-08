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
| Faza podróży: podróż do lokacji, koszt podróży | `travel_phase.py` |
| Faza spotkań: reveal karty, automatyczne angażowanie wrogów | `encounter_phase.py` |
| Faza walki: atak wroga (najlepszy obrońca), atak gracza (wszyscy) | `combat_phase.py` |
| Faza odnowienia: odśwież postacie, +1 threat | `refresh_phase.py` |
| Hierarchia kart: BaseCard, Creature, Enemy, PlayerCreature, Hero, Ally | `src/cards/` |
| Quest, Location, ProgressObjective | `src/cards/progress_objective/` |
| Warunek przegranej: threat ≥ 50 lub wszyscy bohaterowie martwi | `src/table/table.py` |
| Wzorzec `_choose_*()` do nadpisania przez AI agentów | wszystkie fazy |

---

## Znalezione błędy (bugs)

### KRYTYCZNY — `encounter_phase.staging_threat()`
```python
# encounter_phase.py — to jest BŁĄD
def staging_threat(self):
    threat = sum(card.threat for card in self.table.encounter_staging)
    self.table.table_threat += threat  # dodaje threat permanentnie każdą rundę!
```
Staging threat NIE podnosi `table_threat` gracza. W zasadach gry wpływa tylko na wynik questa:
jeśli `willpower < staging_threat` → gracz traci `(staging_threat - willpower)` punktów zagrożenia.
Ta logika jest już **poprawnie** zaimplementowana w `quest_phase._resolve_quest()`.
Ta metoda powinna zostać **usunięta** — powoduje podwójne naliczanie.

### ŚREDNI — `encounter_phase.reveal_encounter_cards()` — `pop()` zamiast `pop(0)`
```python
card = self.table.encounter_deck.pop()   # pobiera z KOŃCA talii
# powinno być:
card = self.table.encounter_deck.pop(0)  # pobiera z POCZĄTKU (jak w table.draw_player_card)
```

### ŚREDNI — `travel_phase._choose_location()` — zła logika wyboru
```python
return max(eligible, key=lambda loc: loc.progress)  # progress startuje od 0 dla wszystkich
```
Wybiera lokację z największym aktualnym postępem (zawsze 0 na starcie).
Powinno być `loc.required_progress` (wybierz lokację, którą najłatwiej ukończyć)
lub `loc.required_progress - loc.progress` (wybierz najbliższą ukończenia).

### NISKI — Warunek wygranej nie istnieje
`main.py` nigdy nie sprawdza, czy gracz wygrał (ukończył wszystkie questy).
Pętla `while not game.table.check_lose_condition()` kończy się tylko przegraną.

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
# aktualna implementacja (błędna):
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

### Optional Engagement — brak
W fazie spotkań gracz może **opcjonalnie** wybrać wroga z staging area do angażowania,
zanim nastąpi automatyczne angażowanie przez próg zagrożenia. Implementacja ma tylko automatyczne.

---

## Brakujące dane w config

| Brak | Uwaga |
|---|---|
| Karty Treachery w `encounter_deck` | Scenariusz "Passage through Mirkwood" zawiera: *Caught in a Web*, *Driven by Shadow*, *Misty Mountain Orcs*, *The Necromancer's Reach*, *Wargs* |
| Attachment karty w `player_deck` | W scenariuszu brak, ale klasa `Attachment` jest potrzebna |
| Event karty w `player_deck` | *Gandalf* i inne karty mają wersje Event |
| Sfery `Leadership` i `Lore` | Zdefiniowane są tylko Spirit, Tactics, Neutral |
| Mechanizm duplikatów w talii | `all_cards_deck.py` ma `all_cards_dict` ale nie jest używany do budowania talii z duplikatami |

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
| 🔴 KRYTYCZNY | Napraw bug `staging_threat()` w `encounter_phase.py` |
| 🔴 KRYTYCZNY | Dodaj warunek wygranej (ukończenie wszystkich kart questa) |
| 🟠 WYSOKI | Zaimplementuj karty Treachery + rozpatrzenie "When Revealed" |
| 🟠 WYSOKI | Zaimplementuj Shadow Cards w fazie walki |
| 🟠 WYSOKI | Dodaj keyword **Surge** (bardzo częsty w kartach encounter) |
| 🟡 ŚREDNI | Sphere resource matching |
| 🟡 ŚREDNI | Keyword **Doomed X** i **Archery X** |
| 🟡 ŚREDNI | Klasa Attachment + Event + ich wsparcie w Planning Phase |
| 🟢 NISKI | Keyword Toughness, Indestructible, Regenerate, Battle, Siege |
| 🟢 NISKI | Optional engagement |
| 🟢 NISKI | Action windows |
| ⚪ OPCJONALNY | Tryb wieloosobowy (Sentinel, Ranged, kolejność graczy) |
| ⚪ OPCJONALNY | Side Quests, Objective cards |
