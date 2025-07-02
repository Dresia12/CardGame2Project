import random
import json
from CardGame2.data_manager import DataManager

errors = []

# Génère des collections corrompues
for i in range(10):
    # Cas 1 : types erronés
    collection = {random.choice([None, '', 123, [], {}, 'card'+str(i)]): random.choice(['a', -1, 0, 1, 999999, None, [], {}]) for i in range(10)}
    try:
        dm = DataManager()
        dm.set_collection(collection)
    except Exception as e:
        errors.append((f"collection_type_{i}", str(e)))

# Génère des decks corrompus
for i in range(10):
    deck = [random.choice([None, '', 123, [], {}, 'card'+str(i)]) for _ in range(20)]
    try:
        dm = DataManager()
        decks = [deck]
        if hasattr(dm, 'set_decks'):
            dm.set_decks(decks)
        else:
            dm.decks = decks
    except Exception as e:
        errors.append((f"deck_type_{i}", str(e)))

# Génère des JSON invalides
for i in range(5):
    data = random.choice([None, '', 123, [], {}, {'foo': 'bar'}])
    try:
        s = json.dumps(data)
        dm = DataManager()
        dm.set_collection(json.loads(s))
    except Exception as e:
        errors.append((f"json_invalid_{i}", str(e)))

print("\n=== Résumé fuzzing ===")
if not errors:
    print("Aucune exception inattendue sur données corrompues.")
else:
    for label, err in errors:
        print(f"{label} : {err}") 