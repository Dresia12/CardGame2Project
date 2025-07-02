"""
Module card.py
Modèle de carte générique pour CardGame2.
Extensible pour nouveaux types d'effets, hooks UI, etc.
"""
from .types import Rarity, CardType
from typing import Optional, Callable

class Card:
    """
    Représente une carte générique (unité, sort, équipement, etc.).
    Extensible pour nouveaux effets, hooks, ou types de cartes.
    """
    def __init__(self, name: str, card_type: CardType, rarity: Rarity, cost: int = 0, effect: Optional[Callable] = None, set_name: Optional[str] = None, description: str = ""):
        self.name = name
        # Conversion automatique str -> Enum pour card_type
        if isinstance(card_type, str):
            try:
                self.card_type = CardType[card_type]
            except Exception:
                self.card_type = CardType.UNIT
        else:
            self.card_type = card_type
        # Conversion automatique str -> Enum pour rarity
        if isinstance(rarity, str):
            try:
                self.rarity = Rarity[rarity]
            except Exception:
                self.rarity = Rarity.COMMON
        else:
            self.rarity = rarity
        self.cost = cost
        self.effect = effect
        self.set_name = set_name
        self.description = description

    def play(self, game, player, target=None):
        """Joue la carte (déclenche l'effet si présent)."""
        if self.effect:
            return self.effect(game, player, target)
        return None
        # TODO: Hook feedback jeu de carte (log, anim, son)

    def __repr__(self):
        return f"<Card {self.name} [{self.card_type.name}] ({self.rarity.name})>"
    # TODO: Ajouter extension pour effets complexes ou hooks UI 