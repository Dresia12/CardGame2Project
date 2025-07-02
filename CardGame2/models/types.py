"""
Module types.py
Définit les énumérations de rareté et de type de carte pour CardGame2.
Extensible pour nouveaux types ou raretés.
"""
from enum import Enum, auto

class Rarity(Enum):
    """Enum des raretés de carte."""
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    MYTHIC = auto()
    SPECIAL = auto()
    BONUS = auto()
    # TODO: Ajouter de nouvelles raretés si besoin

class CardType(Enum):
    """Enum des types de carte."""
    UNIT = auto()
    SPELL = auto()
    EQUIPMENT = auto()
    HERO = auto()
    STATUS = auto()
    LAND = auto()
    # TODO: Ajouter de nouveaux types si besoin

class Element(Enum):
    NEUTRE = auto()
    FEU = auto()
    EAU = auto()
    FOUDRE = auto()
    TERRE = auto()
    GLACE = auto()
    AIR = auto()
    METAL = auto()
    LUMIERE = auto()
    TENEBRES = auto()
    NATURE = auto()
    POISON = auto()
    PSYCHIQUE = auto()
    VIBRATION = auto()
    CRISTAL = auto()
    TEMPOREL = auto()
    NEANT = auto()
    ARCANIQUE = auto()
    ORDRE = auto()
    CHAOS = auto()
    MORT = auto()
    VIE = auto()
    TECHNOLOGIQUE = auto()
    OMBRE = auto()

# Table de faiblesses élémentaires
ELEMENT_WEAKNESS = {
    Element.FEU: Element.EAU,
    Element.EAU: Element.FOUDRE,
    Element.TERRE: Element.GLACE,
    Element.AIR: Element.METAL,
    Element.LUMIERE: Element.TENEBRES,
    Element.TENEBRES: Element.LUMIERE,
    Element.FOUDRE: Element.TERRE,
    Element.GLACE: Element.FEU,
    Element.NATURE: Element.POISON,
    Element.METAL: Element.CHAOS,
    Element.PSYCHIQUE: Element.VIBRATION,
    Element.VIBRATION: Element.CRISTAL,
    Element.TEMPOREL: Element.NEANT,
    Element.NEANT: Element.ARCANIQUE,
    Element.ARCANIQUE: Element.ORDRE,
    Element.CRISTAL: Element.MORT,
    Element.CHAOS: Element.ORDRE,
    Element.ORDRE: Element.CHAOS,
    Element.POISON: Element.PSYCHIQUE,
    Element.MORT: Element.VIE,
    Element.VIE: Element.MORT,
    Element.TECHNOLOGIQUE: Element.NATURE,
    Element.OMBRE: Element.LUMIERE,
    # Neutre n'a pas de faiblesse
}

def compute_elemental_damage(attacker_element, defender_element, base_damage):
    """
    Renvoie les dégâts infligés en tenant compte des faiblesses élémentaires (+20% si faiblesse).
    """
    if ELEMENT_WEAKNESS.get(attacker_element) == defender_element:
        return int(base_damage * 1.2)
    return base_damage

# Ajoutez d'autres types ou constantes si besoin 