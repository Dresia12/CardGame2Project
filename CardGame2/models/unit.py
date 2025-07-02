"""
Module unit.py
Modèle d'unité pour CardGame2.
Extensible pour nouveaux effets, statuts, hooks UI.
"""
from .card import Card
from .types import CardType, Rarity, Element
from typing import Optional

class Unit(Card):
    """
    Représente une unité (créature) sur le board.
    Gère attaque, PV, statuts temporaires/permanents.
    Extensible pour nouveaux effets ou hooks de feedback.
    """
    def __init__(self, name: str, rarity: Rarity, cost: int, attack: int, health: int, effect=None, set_name=None, description="", element: Element = Element.NEUTRE, card_type=None):
        # Conversion automatique str -> Enum pour rarity
        if isinstance(rarity, str):
            try:
                rarity = Rarity[rarity]
            except Exception:
                rarity = Rarity.COMMON
        # Conversion automatique str -> Enum pour element
        if isinstance(element, str):
            try:
                element = Element[element]
            except Exception:
                element = Element.NEUTRE
        # Conversion automatique str -> Enum pour card_type
        if card_type is None:
            card_type = CardType.UNIT
        elif isinstance(card_type, str):
            try:
                card_type = CardType[card_type]
            except Exception:
                card_type = CardType.UNIT
        super().__init__(name, card_type, rarity, cost, effect, set_name, description)
        self.attack = attack
        self.health = health
        self.max_health = health
        self.status_effects = []  # ex: [{'type': 'boost', 'duration': 2}, ...]
        self.element = element

    def take_damage(self, amount: int):
        """Inflige des dégâts à l'unité. Peut déclencher un hook de feedback UI/sonore."""
        self.health -= amount
        if self.health < 0:
            self.health = 0
        # TODO: Hook feedback (animation, son, log)

    def is_alive(self):
        """Retourne True si l'unité est vivante."""
        return self.health > 0

    def apply_status_effect(self, effect_type: str, duration: Optional[int] = None):
        """Ajoute un effet temporaire ou permanent à l'unité."""
        if duration is not None:
            self.status_effects.append({'type': effect_type, 'duration': duration})
        else:
            self.status_effects.append({'type': effect_type})
        # TODO: Hook feedback (animation, log, son)

    # TODO: Ajouter méthode pour gérer l'expiration d'un effet (avec feedback)
    # TODO: Prévoir extension pour effets complexes (ex: effet avec callback)

    def __repr__(self):
        return f"<Unit {self.name} ATK:{self.attack} HP:{self.health}/{self.max_health} ({self.rarity.name}) [{self.element.name}]>" 