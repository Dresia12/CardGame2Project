import os
import json
from CardGame2.data_manager import DataManager

SAVE_DIR = '.'

errors = []

for root, dirs, files in os.walk(SAVE_DIR):
    for file in files:
        if file.endswith('.json'):
            path = os.path.join(root, file)
            print(f"[MIGRATION TEST] Test de {path}")
            try:
                with open(path, encoding='utf-8') as f:
                    data = json.load(f)
                # Si c'est booster_history.json ou collection.json, tente de charger via DataManager
                if 'collection' in file or 'deck' in file or 'booster' in file:
                    try:
                        dm = DataManager()
                        # Simule un set/get pour vérifier la compatibilité
                        if 'collection' in file:
                            dm.set_collection(data)
                        elif 'deck' in file:
                            dm.set_decks(data)
                        elif 'booster' in file:
                            pass  # Optionnel : ajouter un test spécifique
                    except Exception as e:
                        errors.append((path, str(e)))
                        print(f"[ERROR] Chargement DataManager échoué : {e}")
            except Exception as e:
                errors.append((path, str(e)))
                print(f"[ERROR] Lecture/JSON échouée : {e}")

print("\n=== Résumé migration ===")
if not errors:
    print("Aucune erreur de compatibilité détectée sur les sauvegardes JSON.")
else:
    for path, err in errors:
        print(f"{path} : {err}") 