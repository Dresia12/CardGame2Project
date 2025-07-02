import os
import json

CONFIG_PATH = os.path.expanduser('~/.cardgame2_config.json')

def save_user_config(config: dict):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la config utilisateur : {e}")

def load_user_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de la config utilisateur : {e}")
        return {} 