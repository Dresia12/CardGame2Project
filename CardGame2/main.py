from CardGame2.sets.base_set import get_base_set
from CardGame2.boosters.booster import generate_booster
from CardGame2.models.player import Player
from CardGame2.combat.battle import Battle
import random

def main():
    # Générer la collection de base
    card_pool = get_base_set()
    print("--- OUVERTURE D'UN BOOSTER ---")
    booster = generate_booster(card_pool)
    for card in booster:
        print(card)

    # Créer deux joueurs avec un deck de 5 cartes chacun (tirées du booster)
    deck1 = random.sample(booster, min(5, len(booster)))
    deck2 = random.sample(booster, min(5, len(booster)))
    player1 = Player("Alice", deck=deck1)
    player2 = Player("Bob", deck=deck2)

    # Simuler un combat
    battle = Battle(player1, player2)
    print(f"\n--- DEBUT DU COMBAT : {player1.name} vs {player2.name} ---")
    round_count = 0
    while not battle.check_victory() and round_count < 10:
        battle.play_round()
        print(f"Tour {battle.turn}: {battle.active_player} VS {battle.opponent}")
        round_count += 1
    if battle.winner:
        print(f"\nVictoire de {battle.winner.name}!")
    else:
        print("\nMatch nul ou fin de la démo.")

if __name__ == "__main__":
    main() 