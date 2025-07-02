# Reprise Assistant IA – CardGame2

## État du projet (dernière session)
- **Tests UI/robustesse** : stress_test_ui.py, stress_test_charge.py, stress_profile_ui.py, stress_migration_test.py, stress_fuzzing.py tous présents et fonctionnels.
- **CI/CD** : workflow GitHub Actions prêt (test-ui.yml), README_TESTS.md et CONTRIBUTING.md à jour.
- **Profiling** : psutil installé, script de profiling OK.
- **Fuzzing/migration** : scripts pour tester la robustesse face à des données corrompues ou anciennes sauvegardes.
- **Onboarding** : README, CONTRIBUTING, structure pro du repo.
- **Git** : tentative de liaison GitHub, blocage sur device code (authentification Cursor/GitHub non finalisée).

## Blocages / Points à reprendre
- Liaison GitHub non finalisée (device code à générer depuis Cursor ou outil git, voir instructions dans ce fichier).
- PATH git à vérifier si besoin.
- Authentification à finaliser pour push/pull.

## Prochaines étapes prévues
- Surveillance continue (watchdog) mémoire/widgets.
- Ajout d'assertions métier dans les modèles (robustesse business).
- Extension possible : tests multi, API, migration serveur.

## Contexte technique
- Python 3.8+, PyQt5, psutil, scripts de test/fuzzing/profiling.
- Projet prêt pour extension, contribution, et CI/CD.

## TODO / Notes
- [ ] Finaliser la connexion GitHub (voir instructions device code dans ce fichier).
- [ ] Relancer l'IA/assistant ici pour reprendre la session sans perte de contexte.
- [ ] Continuer la surveillance, assertions, ou toute extension demandée.

---

**Pour reprendre :**
- Lire ce fichier, vérifier l'état du projet, et relancer l'IA/assistant avec ce contexte.
- Reprendre la TODO ou demander la suite. 