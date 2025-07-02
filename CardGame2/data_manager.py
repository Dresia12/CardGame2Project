import os
import json
import logging
import datetime

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'player_data.json')

DEFAULT_DECK = {
    "hero": None,    # dict représentant le héros et sa personnalisation
    "units": [],     # liste de 4 noms ou dicts d'unités
    "cards": []      # liste des autres cartes
}

DEFAULT_DATA = {
    "player_name": None,
    "currency": 0,
    "collection": {},  # {card_name: count}
    "heroes": [],      # liste des noms de héros possédés
    "decks": [
        DEFAULT_DECK.copy(),
        DEFAULT_DECK.copy(),
        DEFAULT_DECK.copy(),
        DEFAULT_DECK.copy(),
        DEFAULT_DECK.copy()
    ],
}

def merge_with_default(data):
    merged = DEFAULT_DATA.copy()
    merged.update(data)
    # Pour les decks, s'assurer qu'il y a bien 5 decks
    if 'decks' in data:
        merged['decks'] = data['decks'] + [DEFAULT_DECK.copy()] * (5 - len(data['decks']))
        merged['decks'] = merged['decks'][:5]
    return merged

class DataManager:
    def __init__(self):
        self.data = DEFAULT_DATA.copy()
        self.load()

    def load(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                try:
                    loaded = json.load(f)
                    self.data = merge_with_default(loaded)
                    logger.info(f"Loaded player data from {DATA_FILE}")
                except Exception as e:
                    logger.error(f"Failed to load player data: {e}")
                    self.data = DEFAULT_DATA.copy()
        else:
            logger.warning(f"Data file {DATA_FILE} not found, creating new one.")
            self.save()

    def save(self):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved player data to {DATA_FILE}")
        except Exception as e:
            logger.error(f"Failed to save player data: {e}")

    def set_player_name(self, name):
        self.data["player_name"] = name
        self.save()

    def get_player_name(self):
        return self.data.get("player_name", None)

    def get_currency(self):
        return self.data.get("currency", 0)

    def add_currency(self, amount):
        self.data["currency"] = self.data.get("currency", 0) + amount
        self.save()

    def spend_currency(self, amount):
        if self.data.get("currency", 0) >= amount:
            self.data["currency"] -= amount
            self.save()
            return True
        return False

    def get_collection(self):
        return self.data.get("collection", {})

    def add_to_collection(self, card_name, count=1):
        col = self.data.setdefault("collection", {})
        if card_name in col:
            col[card_name] += count
        else:
            col[card_name] = count
        self.save()

    def set_collection(self, collection):
        self.data["collection"] = collection
        self.save()

    def get_decks(self):
        return self.data.get("decks", [DEFAULT_DECK.copy() for _ in range(5)])

    def set_deck(self, idx, deck):
        decks = self.data.setdefault("decks", [DEFAULT_DECK.copy() for _ in range(5)])
        while len(decks) < 5:
            decks.append(DEFAULT_DECK.copy())
        decks[idx] = deck
        self.save()

    def reset(self):
        self.data = DEFAULT_DATA.copy()
        self.save()

    def add_game_history(self, entry: dict):
        path = os.path.join(os.path.dirname(__file__), 'history.json')
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
        except Exception as e:
            logger.error(f"Failed to load game history: {e}")
            data = []
        data.append(entry)
        data = data[-10:]
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Game history updated in {path}")
        except Exception as e:
            logger.error(f"Failed to save game history: {e}")

    def get_game_history(self):
        path = os.path.join(os.path.dirname(__file__), 'history.json')
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read game history: {e}")
        return []

    def get_all_player_names(self):
        # Cherche tous les fichiers player_data_<name>.json dans le dossier
        base = os.path.dirname(__file__)
        names = []
        for f in os.listdir(base):
            if f.startswith('player_data_') and f.endswith('.json'):
                names.append(f[len('player_data_'):-len('.json')])
        return names

    def reset_player_data(self, name):
        # Crée ou écrase le fichier player_data_<name>.json avec un profil vierge
        base = os.path.dirname(__file__)
        path = os.path.join(base, f'player_data_{name}.json')
        data = DEFAULT_DATA.copy()
        data['player_name'] = name
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Reset player data for {name} in {path}")
        except Exception as e:
            logger.error(f"Failed to reset player data for {name}: {e}")
        # Réinitialise aussi le profil courant
        self.data = data.copy()
        self.save()

    def add_booster_history(self, cards: list):
        path = os.path.join(os.path.dirname(__file__), 'booster_history.json')
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
        except Exception as e:
            logger.error(f"Failed to load booster history: {e}")
            data = []
        # Patch robustesse : conversion str -> objet si besoin
        from .sets.base_set import get_base_set
        from .sets.elemental_set import get_elemental_set
        card_pool = get_base_set() + get_elemental_set()
        def ensure_card_object(card, card_pool):
            if isinstance(card, str):
                card_obj = next((c for c in card_pool if getattr(c, 'name', None) == card), None)
                if card_obj is not None:
                    logger.warning(f"[WARN] Carte '{card}' convertie en objet depuis card_pool (add_booster_history)")
                    return card_obj
                else:
                    logger.error(f"[ERROR] Impossible de retrouver l'objet pour le nom {card} (add_booster_history)")
                    return None
            return card
        cards_fixed = [ensure_card_object(c, card_pool) for c in cards if ensure_card_object(c, card_pool) is not None]
        entry = {
            'date': datetime.datetime.now().isoformat(),
            'cards': [
                {
                    'name': c.name if c is not None and hasattr(c, 'name') else str(c),
                    'rarity': c.rarity.name if c is not None and hasattr(c, 'rarity') and hasattr(c.rarity, 'name') else (c.rarity if c is not None and hasattr(c, 'rarity') else 'SPECIAL'),
                    'type': c.card_type.name if c is not None and hasattr(c, 'card_type') and hasattr(c.card_type, 'name') else (c.card_type if c is not None and hasattr(c, 'card_type') else 'HÉROS')
                } for c in cards_fixed if c is not None
            ]
        }
        data.append(entry)
        data = data[-100:]
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Booster history updated in {path}")
        except Exception as e:
            logger.error(f"Failed to save booster history: {e}")

    def get_booster_history(self):
        path = os.path.join(os.path.dirname(__file__), 'booster_history.json')
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read booster history: {e}")
        return []

    def get_hero_collection(self):
        return self.data.get("heroes", [])

    def add_hero_to_collection(self, hero_name):
        heroes = self.data.setdefault("heroes", [])
        if hero_name not in heroes:
            heroes.append(hero_name)
            self.save()
            return True
        return False

    def clean_collections(self):
        # Nettoie la collection principale (supprime clés vides ou None, garde uniquement les cartes valides)
        collection = self.get_collection()
        cleaned = {k: v for k, v in collection.items() if isinstance(k, str) and k.strip() != '' and isinstance(v, int) and v > 0}
        self.set_collection(cleaned)

        # Nettoie la collection de héros (supprime str vides ou None)
        hero_collection = self.get_hero_collection()
        hero_cleaned = [h for h in hero_collection if isinstance(h, str) and h.strip() != '']
        self.data['heroes'] = hero_cleaned

        # Utilitaire : conversion robuste des champs Enum sur dict/objets
        from .models.types import CardType, Rarity, Element
        def robust_enum_patch(obj):
            # Patche card_type
            if hasattr(obj, 'card_type'):
                ct = getattr(obj, 'card_type')
                if isinstance(ct, str):
                    try:
                        setattr(obj, 'card_type', CardType[ct])
                    except Exception:
                        setattr(obj, 'card_type', CardType.UNIT)
            # Patche rarity
            if hasattr(obj, 'rarity'):
                r = getattr(obj, 'rarity')
                if isinstance(r, str):
                    try:
                        setattr(obj, 'rarity', Rarity[r])
                    except Exception:
                        setattr(obj, 'rarity', Rarity.COMMON)
            # Patche element
            if hasattr(obj, 'element'):
                e = getattr(obj, 'element')
                if isinstance(e, str):
                    try:
                        setattr(obj, 'element', Element[e])
                    except Exception:
                        setattr(obj, 'element', Element.NEUTRE)
            return obj

        # Nettoie les decks sauvegardés (supprime entrées vides ou None dans chaque deck)
        decks = self.get_decks()
        decks_cleaned = []
        for deck in decks:
            deck_cleaned = {}
            # Nettoie le héros du deck
            hero = deck.get('hero')
            if isinstance(hero, dict) or hero is None:
                deck_cleaned['hero'] = hero
            else:
                deck_cleaned['hero'] = None
            # Nettoie les unités
            units = deck.get('units', [])
            deck_cleaned['units'] = [u for u in units if isinstance(u, str) and u.strip() != '']
            # Nettoie les cartes
            cards = deck.get('cards', [])
            deck_cleaned['cards'] = [c for c in cards if isinstance(c, str) and c.strip() != '']
            decks_cleaned.append(deck_cleaned)
        self.data['decks'] = decks_cleaned

        # Patche tous les objets cartes/units/héros en mémoire (si présents)
        # (ex: self.cards, self.units, self.heroes, etc. si utilisés)
        for attr in ['cards', 'units', 'heroes']:
            if hasattr(self, attr):
                items = getattr(self, attr)
                if isinstance(items, list):
                    setattr(self, attr, [robust_enum_patch(obj) for obj in items])
        self.save() 