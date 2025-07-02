"""
Module hero.py
Modèle de héros personnalisable pour CardGame2.
Extensible pour nouveaux passifs, hooks UI, et mécaniques avancées.
"""
from enum import Enum
from .types import Element, Rarity, CardType

class HeroPassive(Enum):
    POISON = "Poison"
    ENFLAMME = "Enflammé"
    CHARISMATIQUE = "Charismatique"
    # TODO: Ajouter de nouveaux passifs ici

class HeroCustomization:
    """
    Gère la personnalisation d'un héros (niveaux, passifs, coût).
    Extensible pour nouveaux types de bonus ou de passifs.
    """
    def __init__(self):
        self.hp_level = 0
        self.attack_level = 0
        self.defense_level = 0
        self.passives = []
        self.total_cost = 0
    def get_hp_bonus(self):
        return self.hp_level * 5
    def get_attack_bonus(self):
        return self.attack_level * 2
    def get_defense_bonus(self):
        return self.defense_level * 2
    def get_activation_cost(self):
        return 3 + self.total_cost
    def can_add_passive(self, passive: HeroPassive):
        return self.total_cost + 3 <= 15
    def add_passive(self, passive: HeroPassive):
        if self.can_add_passive(passive) and passive not in self.passives:
            self.passives.append(passive)
            self.total_cost += 3
            return True
        return False
    def remove_passive(self, passive: HeroPassive):
        if passive in self.passives:
            self.passives.remove(passive)
            self.total_cost -= 3
            return True
        return False
    def can_upgrade_stat(self, stat_type: str):
        current_level = getattr(self, f"{stat_type}_level", 0)
        if current_level >= 3:
            return False
        upgrade_cost = current_level + 1
        return self.total_cost + upgrade_cost <= 15
    def upgrade_stat(self, stat_type: str):
        if self.can_upgrade_stat(stat_type):
            current_level = getattr(self, f"{stat_type}_level", 0)
            upgrade_cost = current_level + 1
            setattr(self, f"{stat_type}_level", current_level + 1)
            self.total_cost += upgrade_cost
            return True
        return False
    def downgrade_stat(self, stat_type: str):
        current_level = getattr(self, f"{stat_type}_level", 0)
        if current_level > 0:
            downgrade_cost = current_level
            setattr(self, f"{stat_type}_level", current_level - 1)
            self.total_cost -= downgrade_cost
            return True
        return False
    def to_dict(self):
        return {
            'hp_level': self.hp_level,
            'attack_level': self.attack_level,
            'defense_level': self.defense_level,
            'passives': [p.value for p in self.passives],
            'total_cost': self.total_cost
        }
    @classmethod
    def from_dict(cls, data: dict):
        customization = cls()
        customization.hp_level = data.get('hp_level', 0)
        customization.attack_level = data.get('attack_level', 0)
        customization.defense_level = data.get('defense_level', 0)
        customization.passives = [HeroPassive(p) for p in data.get('passives', [])]
        customization.total_cost = data.get('total_cost', 0)
        return customization

class Hero:
    """
    Représente un héros personnalisable.
    Gère les stats de base, la personnalisation, l'activation, et les hooks d'UI.
    Extensible pour nouvelles capacités ou feedbacks.
    """
    def __init__(self, name: str, base_hp: int, base_attack: int, base_defense: int, element: Element = Element.NEUTRE, card_type=None, rarity=Rarity.SPECIAL):
        self.name = name
        self.base_hp = base_hp
        self.base_attack = base_attack
        self.base_defense = base_defense
        # Conversion automatique str -> Enum pour element
        if isinstance(element, str):
            try:
                element = Element[element]
            except Exception:
                pass
        self.element = element
        # Conversion automatique str -> Enum pour card_type
        if card_type is None:
            self.card_type = CardType.HERO
        elif isinstance(card_type, str):
            try:
                self.card_type = CardType[card_type]
            except Exception:
                self.card_type = CardType.HERO
        else:
            self.card_type = card_type
        # Conversion automatique str -> Enum pour rarity
        if isinstance(rarity, str):
            try:
                self.rarity = Rarity[rarity]
            except Exception:
                self.rarity = Rarity.SPECIAL
        else:
            self.rarity = rarity
        self.customization = HeroCustomization()
        self.is_active = False
        self.is_tapped = False
        self.ability_cooldown = 0
        self.hero_ability = ""
        self.ability_description = ""
    def activate(self):
        """Active le héros (hook possible pour feedback UI/sonore)."""
        self.is_active = True
        # TODO: Hook feedback activation
    def deactivate(self):
        """Désactive le héros."""
        self.is_active = False
    def apply_customization(self):
        """Applique la personnalisation au héros (bonus stats)."""
        self.max_hp = self.base_hp + self.customization.get_hp_bonus()
        self.current_hp = self.max_hp
        self.attack = self.base_attack + self.customization.get_attack_bonus()
        self.defense = self.base_defense + self.customization.get_defense_bonus()
    def get_activation_cost(self):
        return self.customization.get_activation_cost()
    def has_passive(self, passive: HeroPassive):
        return passive in self.customization.passives
    def to_dict(self):
        return {
            'name': self.name,
            'base_hp': self.base_hp,
            'base_attack': self.base_attack,
            'base_defense': self.base_defense,
            'element': self.element.name,
            'card_type': self.card_type.name,
            'rarity': self.rarity.name,
            'customization': self.customization.to_dict()
        }
    @classmethod
    def from_dict(cls, data: dict):
        element = data.get('element', 'NEUTRE')
        card_type = data.get('card_type', 'HERO')
        rarity = data.get('rarity', 'SPECIAL')
        hero = cls(
            name=data['name'],
            base_hp=data['base_hp'],
            base_attack=data['base_attack'],
            base_defense=data['base_defense'],
            element=element,
            card_type=card_type,
            rarity=rarity
        )
        if 'customization' in data:
            hero.customization = HeroCustomization.from_dict(data['customization'])
            hero.apply_customization()
        return hero
    # TODO: Ajouter méthode pour hooks d'effets spéciaux ou feedbacks UI 