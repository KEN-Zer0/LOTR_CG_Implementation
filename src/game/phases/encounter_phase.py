from .phase import Phase


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
        for enemy in list(self.table.encounter_staging):

            # znajdź najniższy threat gracza
            player_threat = self.table.table_threat

            if enemy.engagement <= player_threat:
                self.table.encounter_engagement.append(enemy)
                self.table.encounter_staging.remove(enemy)

    def staging_threat(self):
        # dodaje threat z kart w staging area
        threat = sum(
            enemy.threat for enemy in self.table.encounter_staging
        )

        self.table.table_threat += threat