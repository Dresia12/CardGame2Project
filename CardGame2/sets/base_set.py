from ..models.card import Card
from ..models.unit import Unit
from ..models.types import CardType, Rarity
from typing import List

def get_base_set() -> List[Card]:
    cards = [
        Unit("Soldat Vaillant", Rarity.COMMON, 0, 50, 1000, description="Unité de base. 1000 PV, 50 ATK, CD 1 tour."),
        Unit("Archer Agile", Rarity.UNCOMMON, 0, 63, 1000, description="Peu commune. 1000 PV, 63 ATK, CD 1 tour. Peut attaquer à distance."),
        Unit("Chevalier Légendaire", Rarity.RARE, 0, 110, 1320, description="Rare. 1320 PV, 110 ATK, CD 1 tour. Unité puissante."),
        Unit("Garde d'Élite", Rarity.UNCOMMON, 0, 79, 1208, description="Peu commune. 1208 PV, 79 ATK, CD 1 tour. Unité défensive solide."),
        Card("Boule de Feu", CardType.SPELL, Rarity.COMMON, 2, description="Inflige 100 dégâts à une cible (2 mana)."),
        Card("Potion de Soin", CardType.SPELL, Rarity.COMMON, 1, description="Soigne 50 PV (1 mana)."),
        Card("Invocation du Dragon", CardType.SPELL, Rarity.MYTHIC, 6, description="Invoque un dragon (1610 PV, 173 ATK) (6 mana)."),
        Card("Aura Mystique", CardType.SPELL, Rarity.SPECIAL, 5, description="Effet spécial à équilibrer (5 mana)."),
        Card("Bouclier Magique", CardType.EQUIPMENT, Rarity.UNCOMMON, 2, description="Donne +105 PV à une unité (2 mana)."),
        Card("Épée Runique", CardType.EQUIPMENT, Rarity.RARE, 3, description="Donne +110 ATK à une unité (3 mana)."),
    ]
    # Purge automatique : ne garder que les objets valides
    cards = [c for c in cards if hasattr(c, "name") and hasattr(c, "card_type")]
    return cards 