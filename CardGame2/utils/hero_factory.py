"""
Module utilitaire pour la création de héros selon le barème CardGame2.
"""
from ..models.hero import Hero
from ..models.types import Rarity

def get_rarity_multiplier(rarity: Rarity) -> float:
    if rarity == Rarity.COMMON:
        return 1.00
    elif rarity == Rarity.UNCOMMON:
        return 1.05
    elif rarity == Rarity.RARE:
        return 1.10
    elif rarity in (Rarity.MYTHIC, Rarity.SPECIAL):
        return 1.15
    return 1.00

def create_default_hero(name: str, rarity: Rarity = Rarity.COMMON) -> Hero:
    """
    Crée un héros avec les stats de base et applique le bonus de rareté.
    PV de base : 1000
    ATK de base : 50
    DEF de base : 0
    """
    mult = get_rarity_multiplier(rarity)
    base_hp = int(1000 * mult)
    base_attack = int(50 * mult)
    base_defense = 0
    return Hero(name, base_hp, base_attack, base_defense) 