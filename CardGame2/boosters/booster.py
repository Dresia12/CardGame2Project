import random
from CardGame2.models.card import Card
from CardGame2.models.types import CardType, Rarity
from typing import List

def generate_booster(card_pool: List[Card]) -> List[Card]:
    units = [c for c in card_pool if c.card_type == CardType.UNIT]
    spells_equip = [c for c in card_pool if c.card_type in (CardType.SPELL, CardType.EQUIPMENT)]
    bonus = [c for c in card_pool if c.rarity in (Rarity.RARE, Rarity.MYTHIC, Rarity.SPECIAL, Rarity.BONUS)]
    commons = [c for c in card_pool if c.rarity == Rarity.COMMON]
    uncommons = [c for c in card_pool if c.rarity == Rarity.UNCOMMON]

    booster = []
    booster += random.sample(units, min(2, len(units)))
    booster += random.sample(spells_equip, min(5, len(spells_equip)))
    # Carte bonus : rareté supérieure si possible
    if bonus:
        booster.append(random.choice(bonus))
    else:
        # fallback : uncommon ou common
        if uncommons:
            booster.append(random.choice(uncommons))
        else:
            booster.append(random.choice(commons))
    random.shuffle(booster)
    return booster 