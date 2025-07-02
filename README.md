# CardGame2

Jeu de cartes cross-over inspiré de "CardGame" (mécaniques de combat) et "mage-master" (collection, rareté, boosters).

## Fonctionnalités principales
- Système de cartes avec rareté (Common, Uncommon, Rare, Mythic, Special, Bonus)
- Génération de boosters (8 cartes : 2 unités, 5 sorts/équipements, 1 carte bonus)
- Mécaniques de combat automatisées entre deux joueurs
- Architecture modulaire pour ajouter des sets, cartes, effets, etc.

## Structure du projet
- `models/` : Modèles de cartes, unités, joueurs, types, etc.
- `sets/` : Définition des sets de cartes
- `boosters/` : Génération de boosters
- `combat/` : Logique de combat
- `players/` : Gestion des joueurs
- `utils/` : Utilitaires divers

## Lancer l'UI complète

Depuis la racine du projet :
```bash
python -m CardGame2.ui_app
```

## Tester PyQt5

```bash
python test_pyqt.py
```

## Astuce : configuration VSCode/Pyright

Pour éviter les faux positifs d'import (PyQt5, CardGame2), ajoutez ceci à votre settings.json :
```json
"python.analysis.extraPaths": [
    "./CardGame2"
],
"python.analysis.diagnosticMode": "openFilesOnly"
```
Cela permet à Pyright/pylance de reconnaître les modules du projet et PyQt5 même si l'environnement virtuel n'est pas activé.

## Extension
Ajoutez vos propres cartes, sets, effets et mécaniques dans les dossiers appropriés. 