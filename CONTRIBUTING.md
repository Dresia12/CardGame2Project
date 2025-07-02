# Guide Contributeur – CardGame2

## Installation et lancement

1. Cloner le repo :
```bash
git clone ...
cd CardGame2Project
```
2. Installer les dépendances :
```bash
pip install -r requirements.txt
```
3. Lancer l'UI :
```bash
python -m CardGame2.ui_app
```

## Lancer les tests
- Stress test UI : `python stress_test_ui.py`
- Test de charge : `python stress_test_charge.py`
- Profiling : `python stress_profile_ui.py`

## Bonnes pratiques
- Typage systématique (type hints)
- Docstrings pour chaque fonction/classe
- Utiliser les logs (`log_debug`, etc.) pour tout événement important ou erreur
- Factoriser le code réutilisable (composants UI, utilitaires)
- Respecter la structure du projet (un écran = un fichier, composants réutilisables dans ui/components.py)

## Proposer une Pull Request
- Forker le repo, créer une branche dédiée
- Ajouter/adapter les tests si besoin
- Vérifier que la CI passe (GitHub Actions)
- Décrire clairement la PR (but, changements, impact)

## Ajouter un test ou une assertion métier
- Modifier `stress_test_ui.py` pour ajouter un scénario ou une assertion
- Utiliser le module `debug_api` pour accéder à l'état du jeu
- Documenter le nouveau test dans `README_TESTS.md`

## Pour aller plus loin
- Voir `README_TESTS.md` pour tous les détails sur les tests, la CI, et l'extension future

---

Merci de contribuer à CardGame2 ! 