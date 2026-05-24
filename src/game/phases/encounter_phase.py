from .phase import Phase
from src.cards import Enemy


class EncounterPhase(Phase):
    def execute(self):
        self.reveal_encounter_cards()
        self.engagement_check()
        self.staging_threat()

    def reveal_encounter_cards(self):
        # 1 gracz = 1 karta encounter
        if not self.table.encounter_deck:
            return

        card = self.table.encounter_deck.pop()
        self.table.encounter_staging.append(card)

    def engagement_check(self):
        player_threat = self.table.table_threat

        for card in list(self.table.encounter_staging):
            if not isinstance(card, Enemy):
                continue

            if card.engagement <= player_threat:
                self.table.encounter_engagement.append(card)
                self.table.encounter_staging.remove(card)

    def staging_threat(self):
        # dodaje threat z kart w staging area
        threat = sum(
            card.threat for card in self.table.encounter_staging
        )

        self.table.table_threat += threat