from CardGame2.models.player import Player
from typing import Optional
from CardGame2.models.hero import HeroPassive
import random
import os

def log_debug(msg):
    try:
        with open(os.path.join(os.path.dirname(__file__), '../../debug_cardgame2.log'), 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass

class Battle:
    def __init__(self, player1: Player, player2: Player):
        self.player1: Player = player1
        self.player2: Player = player2
        self.turn: int = 0
        self.active_player: Player = player1
        self.opponent: Player = player2
        self.winner: Player = None
        self.forfeit: Optional[str] = None  # None, 'player1', 'player2'
        # Hooks UI (à connecter par le contrôleur/CombatScreen)
        self.on_effect_expire = None  # callback(unit, effect)
        self.on_effect_secondary = None  # callback(unit, effect, action)
        self.on_error = None  # callback(msg)

    def next_turn(self) -> None:
        self.turn += 1
        self.active_player, self.opponent = self.opponent, self.active_player
        # Passif de héros : soin de 1 PV à toutes les unités alliées si CHARISMATIQUE
        if hasattr(self.active_player, 'hero') and self.active_player.hero and hasattr(self.active_player.hero, 'has_passive'):
            if self.active_player.hero.has_passive(HeroPassive.CHARISMATIQUE):
                for unit in self.active_player.board:
                    if hasattr(unit, 'health') and hasattr(unit, 'max_health'):
                        unit.health = min(unit.health + 1, unit.max_health)
        # Passif de héros : ENFLAMME applique brûlure à une unité adverse aléatoire
        if hasattr(self.active_player, 'hero') and self.active_player.hero and hasattr(self.active_player.hero, 'has_passive'):
            if self.active_player.hero.has_passive(HeroPassive.ENFLAMME):
                candidates = [u for u in self.opponent.board if hasattr(u, 'status_effects')]
                if candidates:
                    target = random.choice(candidates)
                    if hasattr(target, 'apply_status_effect'):
                        target.apply_status_effect('burn', 2)
        # Passif de héros : POISON applique poison à une unité adverse aléatoire
        if hasattr(self.active_player, 'hero') and self.active_player.hero and hasattr(self.active_player.hero, 'has_passive'):
            if self.active_player.hero.has_passive(HeroPassive.POISON):
                candidates = [u for u in self.opponent.board if hasattr(u, 'status_effects')]
                if candidates:
                    target = random.choice(candidates)
                    if hasattr(target, 'apply_status_effect'):
                        target.apply_status_effect('poison', 2)
        # Application des effets de statut (dont brûlure) sur toutes les unités du board
        for unit in self.active_player.board:
            expired_effects = []
            for eff in unit.status_effects:
                if isinstance(eff, dict) and 'duration' in eff:
                    eff['duration'] -= 1
                    if eff['duration'] <= 0:
                        expired_effects.append(eff)
                    else:
                        # Tick d'effet (ex: burn, poison)
                        if eff.get('type') == 'burn':
                            unit.take_damage(1)
                            log_debug(f"[EFFECT] {unit.name} subit 1 dégât de brûlure (burn).")
                        elif eff.get('type') == 'poison':
                            unit.take_damage(1)
                            log_debug(f"[EFFECT] {unit.name} subit 1 dégât de poison.")
                        # Ajoute d'autres effets à tick ici si besoin
            for eff in expired_effects:
                unit.status_effects.remove(eff)
                # Feedback exhaustif à l'expiration
                msg = f"L'effet {eff.get('type')} sur {unit.name} a expiré."
                log_debug(f"[EFFECT-EXPIRE] {msg}")
                if self.on_effect_expire:
                    try:
                        self.on_effect_expire(unit, eff)
                    except Exception as e:
                        log_debug(f"[ERROR] Exception in on_effect_expire: {e}")
                # Effets secondaires à l'expiration
                if eff.get('type') == 'poison':
                    unit.take_damage(1)
                    log_debug(f"[EFFECT-EXPIRE] {unit.name} subit 1 dégât de poison à l'expiration.")
                    if self.on_effect_secondary:
                        try:
                            self.on_effect_secondary(unit, eff, 'poison_expire')
                        except Exception as e:
                            log_debug(f"[ERROR] Exception in on_effect_secondary: {e}")
                elif eff.get('type') == 'shield':
                    if hasattr(unit, 'health') and hasattr(unit, 'max_health'):
                        unit.health = min(unit.health + 1, getattr(unit, 'max_health', unit.health))
                        log_debug(f"[EFFECT-EXPIRE] {unit.name} récupère 1 PV grâce au bouclier dissipé.")
                        if self.on_effect_secondary:
                            try:
                                self.on_effect_secondary(unit, eff, 'shield_expire')
                            except Exception as e:
                                log_debug(f"[ERROR] Exception in on_effect_secondary: {e}")
                elif eff.get('type') == 'boost':
                    # Ex: bonus permanent à l'expiration
                    log_debug(f"[EFFECT-EXPIRE] {unit.name} perd le bonus de boost.")
                    if self.on_effect_secondary:
                        try:
                            self.on_effect_secondary(unit, eff, 'boost_expire')
                        except Exception as e:
                            log_debug(f"[ERROR] Exception in on_effect_secondary: {e}")
                # Ajoute d'autres effets secondaires ici si besoin
        # Sécurité sur la pioche et le mana
        try:
            self.active_player.draw(1)
        except Exception as e:
            log_debug(f"[ERROR] Pioche impossible : {e}")
            if self.on_error:
                try:
                    self.on_error(f"Erreur lors de la pioche : {e}")
                except Exception as e2:
                    log_debug(f"[ERROR] Exception in on_error: {e2}")
        try:
            self.active_player.gain_mana()
        except Exception as e:
            log_debug(f"[ERROR] Gain de mana impossible : {e}")
            if self.on_error:
                try:
                    self.on_error(f"Erreur lors du gain de mana : {e}")
                except Exception as e2:
                    log_debug(f"[ERROR] Exception in on_error: {e2}")

    def attack(self, attacker, defender) -> None:
        defender.take_damage(getattr(attacker, 'attack', 0))
        attacker.take_damage(getattr(defender, 'attack', 0))
        if not defender.is_alive:
            if defender in self.opponent.board:
                self.opponent.board.remove(defender)
        if not attacker.is_alive:
            if attacker in self.active_player.board:
                self.active_player.board.remove(attacker)

    def check_victory(self) -> Player:
        # 1. Terrain vide : si un joueur n'a plus d'unités, il perd. Égalité si les deux terrains sont vides.
        if not self.player1.board and not self.player2.board:
            self.winner = None  # Égalité
            return self.winner
        if not self.player1.board:
            self.winner = self.player2
            return self.winner
        if not self.player2.board:
            self.winner = self.player1
            return self.winner
        # 2. Héros tué
        if not self.player1.is_alive or (hasattr(self.player1, 'hero') and self.player1.hero and getattr(self.player1.hero, 'current_hp', 1) <= 0):
            self.winner = self.player2
            return self.winner
        if not self.player2.is_alive or (hasattr(self.player2, 'hero') and self.player2.hero and getattr(self.player2.hero, 'current_hp', 1) <= 0):
            self.winner = self.player1
            return self.winner
        # 3. Abandon
        if self.forfeit == 'player1':
            self.winner = self.player2
            return self.winner
        if self.forfeit == 'player2':
            self.winner = self.player1
            return self.winner
        # 4. 50ème tour
        if self.turn >= 50:
            self.winner = None  # Égalité
            return self.winner
        return self.winner

    def forfeit_player(self, player: Player) -> None:
        if player == self.player1:
            self.forfeit = 'player1'
        elif player == self.player2:
            self.forfeit = 'player2'

    def play_round(self) -> None:
        self.next_turn()
        self.check_victory() 