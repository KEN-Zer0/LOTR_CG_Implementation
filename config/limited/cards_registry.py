"""Master card prototypes for the Passage through Mirkwood scenario.

CARDS maps every card enum to its canonical instance.
Use .copy() when creating deck lists — never mutate entries here.
"""

from config.limited.cards_list import *
from src.cards import Hero, Ally, Enemy, Location, Quest

CARDS = {
    # Heroes
    Heroes.Eowyn:   Hero(Heroes.Eowyn,   attack=1, defense=1, max_hit_points=3, willpower=4, sphere_of_influence=Sphere.Spirit,  threat=9),
    Heroes.Eleanor: Hero(Heroes.Eleanor, attack=1, defense=2, max_hit_points=3, willpower=1, sphere_of_influence=Sphere.Spirit,  threat=7),
    Heroes.Thalin:  Hero(Heroes.Thalin,  attack=2, defense=2, max_hit_points=4, willpower=1, sphere_of_influence=Sphere.Tactics, threat=9),

    # Allies
    Allies.Wandering_Took:     Ally(Allies.Wandering_Took,     attack=1, defense=1, max_hit_points=2, willpower=1, sphere_of_influence=Sphere.Spirit,  cost=2),
    Allies.Lorien_Guide:       Ally(Allies.Lorien_Guide,       attack=1, defense=1, max_hit_points=2, willpower=0, sphere_of_influence=Sphere.Spirit,  cost=3),
    Allies.Northern_Tracker:   Ally(Allies.Northern_Tracker,   attack=2, defense=2, max_hit_points=3, willpower=1, sphere_of_influence=Sphere.Spirit,  cost=4),
    Allies.Veteran_Axehand:    Ally(Allies.Veteran_Axehand,    attack=2, defense=1, max_hit_points=2, willpower=0, sphere_of_influence=Sphere.Tactics, cost=2),
    Allies.Gondorian_Spearman: Ally(Allies.Gondorian_Spearman, attack=1, defense=1, max_hit_points=1, willpower=0, sphere_of_influence=Sphere.Tactics, cost=2),
    Allies.Horseback_Archer:   Ally(Allies.Horseback_Archer,   attack=2, defense=1, max_hit_points=2, willpower=0, sphere_of_influence=Sphere.Tactics, cost=3),
    Allies.Beorn:              Ally(Allies.Beorn,              attack=3, defense=3, max_hit_points=6, willpower=1, sphere_of_influence=Sphere.Tactics, cost=6),
    Allies.Gandalf:            Ally(Allies.Gandalf,            attack=4, defense=4, max_hit_points=4, willpower=4, sphere_of_influence=Sphere.Neutral, cost=5),

    # Enemies
    Enemies.Dol_Guldur_Orcs:        Enemy(Enemies.Dol_Guldur_Orcs,        attack=2, defense=0, max_hit_points=3, engagement=10, threat=2),
    Enemies.Chieftan_Ufthak:        Enemy(Enemies.Chieftan_Ufthak,        attack=3, defense=3, max_hit_points=6, engagement=35, threat=2),
    Enemies.Dol_Guldur_Beastmaster: Enemy(Enemies.Dol_Guldur_Beastmaster, attack=3, defense=1, max_hit_points=5, engagement=35, threat=2),
    Enemies.Forest_Spider:          Enemy(Enemies.Forest_Spider,          attack=2, defense=1, max_hit_points=4, engagement=25, threat=2),
    Enemies.East_Bight_Patrol:      Enemy(Enemies.East_Bight_Patrol,      attack=3, defense=1, max_hit_points=2, engagement= 5, threat=3),
    Enemies.Black_Forest_Bats:      Enemy(Enemies.Black_Forest_Bats,      attack=1, defense=0, max_hit_points=2, engagement=15, threat=1),
    Enemies.King_Spider:            Enemy(Enemies.King_Spider,            attack=3, defense=1, max_hit_points=3, engagement=20, threat=2),
    Enemies.Hummerhorns:            Enemy(Enemies.Hummerhorns,            attack=2, defense=0, max_hit_points=3, engagement=40, threat=1),
    Enemies.Ungoliants_Spawn:       Enemy(Enemies.Ungoliants_Spawn,       attack=5, defense=2, max_hit_points=9, engagement=32, threat=3),

    # Locations
    Locations.Necromancers_Pass:     Location(Locations.Necromancers_Pass,     threat=3, required_progress=2),
    Locations.Enchanted_Stream:      Location(Locations.Enchanted_Stream,      threat=2, required_progress=2),
    Locations.Old_Forest_Road:       Location(Locations.Old_Forest_Road,       threat=1, required_progress=3),
    Locations.Forest_Gate:           Location(Locations.Forest_Gate,           threat=2, required_progress=4),
    Locations.Great_Forest_Web:      Location(Locations.Great_Forest_Web,      threat=2, required_progress=2),
    Locations.Mountains_of_Mirkwood: Location(Locations.Mountains_of_Mirkwood, threat=2, required_progress=3),

    # Quests
    Quests.Flies_and_Spiders:  Quest(Quests.Flies_and_Spiders,  scenario=Scenario.Passage_through_Mirkwood, required_progress= 8),
    Quests.A_fork_in_the_road: Quest(Quests.A_fork_in_the_road, scenario=Scenario.Passage_through_Mirkwood, required_progress= 2),
    Quests.Beorns_Path:        Quest(Quests.Beorns_Path,        scenario=Scenario.Passage_through_Mirkwood, required_progress=10),
}
