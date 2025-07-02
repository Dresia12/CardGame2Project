"""
Module player.py
Modèle de joueur (humain ou IA) pour CardGame2.
Extensible pour nouveaux hooks IA, feedback, et mécaniques avancées.
"""
from typing import List, Optional
from .card import Card
from .hero import Hero

class Player:
    """
    Représente un joueur (profil, deck, main, board, mana, etc.).
    Extensible pour hooks de feedback ou mécaniques avancées.
    """
    def __init__(self, name: str, deck: Optional[List[Card]] = None, collection: Optional[List[Card]] = None, health: int = 20, hero: Optional[Hero] = None):
        self.name = name
        self.deck = deck or []
        self.hand = []
        self.collection = collection or []
        self.health = health
        self.max_health = health
        self.discard_pile = []
        self.board = []  # cartes en jeu
        self.hero = hero
        self.mana = 1  # Ajout du mana par défaut

    @property
    def is_alive(self) -> bool:
        """Retourne True si le joueur est vivant."""
        return self.health > 0

    @property
    def board_count(self) -> int:
        return len(self.board)

    @property
    def hand_count(self) -> int:
        return len(self.hand)

    def draw(self, n: int = 1) -> None:
        """Pioche n cartes du deck vers la main."""
        for _ in range(n):
            if self.deck:
                self.hand.append(self.deck.pop(0))
        # TODO: Hook feedback pioche (log, son, anim)

    def play_card(self, card: Card, game, target=None) -> Optional[object]:
        """Joue une carte de la main si le coût est payé."""
        if card in self.hand and getattr(card, 'cost', 0) <= self.mana:
            self.hand.remove(card)
            self.mana -= getattr(card, 'cost', 0)
            result = card.play(game, self, target)
            self.board.append(card)
            # TODO: Hook feedback jeu de carte (log, son, anim)
            return result
        return None

    def take_damage(self, amount: int) -> None:
        """Inflige des dégâts au joueur."""
        self.health -= amount
        if self.health < 0:
            self.health = 0
        # TODO: Hook feedback dégâts (log, son, anim)

    def gain_mana(self, amount: int = 1, max_mana: int = 15) -> None:
        self.mana = min(self.mana + amount, max_mana)
        # TODO: Hook feedback gain mana

    def reset_mana(self, value: int = 1) -> None:
        self.mana = value
        # TODO: Hook feedback reset mana

    def __repr__(self):
        return f"<Player {self.name} HP:{self.health}/{self.max_health} Hand:{self.hand_count} Deck:{len(self.deck)} Board:{self.board_count}>"

class AIPlayer(Player):
    """
    Joueur IA, avec logique de tour automatisée.
    Extensible pour hooks IA, feedback, ou stratégies avancées.
    """
    def __init__(self, name: str, deck: Optional[List[Card]] = None, collection: Optional[List[Card]] = None, health: int = 20, hero: Optional[Hero] = None):
        super().__init__(name, deck, collection, health, hero)

    def play_turn(self, game, battle):
        self._play_spells(game, battle)
        self._attack_with_units(battle)
        self._finish_if_possible(battle)
        # TODO: Hook feedback tour IA (log, anim, son)

    def _play_spells(self, game, battle):
        for card in list(self.hand):
            if hasattr(card, 'card_type') and str(card.card_type) == 'CardType.SPELL' and getattr(card, 'cost', 0) <= self.mana:
                target = None
                if battle.opponent.board:
                    target = min(battle.opponent.board, key=lambda u: getattr(u, 'health', 99))
                self.play_card(card, game, target)
        # TODO: Hook feedback sort IA

    def _attack_with_units(self, battle):
        for unit in list(self.board):
            # Vérifie que l'unité est encore vivante et sur le board
            if unit is None or not getattr(unit, 'is_alive', lambda: True)():
                continue
            if unit not in self.board:
                continue
            if battle.opponent.board:
                # Filtre les cibles valides
                valid_targets = [u for u in battle.opponent.board if u is not None and getattr(u, 'is_alive', lambda: True)()]
                if not valid_targets:
                    continue
                target = min(valid_targets, key=lambda u: getattr(u, 'health', 99))
                # Vérifie que la cible est encore sur le board
                if target not in battle.opponent.board:
                    continue
                try:
                    battle.attack(unit, target)
                except Exception as e:
                    import traceback
                    print(f"[CRITICAL][AI] Exception lors de l'attaque IA: {e}\n{traceback.format_exc()}")
            else:
                try:
                    battle.opponent.take_damage(getattr(unit, 'attack', 0))
                except Exception as e:
                    import traceback
                    print(f"[CRITICAL][AI] Exception lors de l'attaque IA (directe): {e}\n{traceback.format_exc()}")
        # TODO: Hook feedback attaque IA

    def _finish_if_possible(self, battle):
        if battle.opponent.health <= 0:
            battle.winner = self
        # TODO: Hook feedback victoire IA 