# Tests UI & Robustesse – CardGame2

## Lancer les tests localement

### 1. Stress test UI (fonctionnel + robustesse)
```bash
python stress_test_ui.py
```
- Simule navigation extrême, achats, boosters, édition de deck, combats, assertions métier.
- Loggue tout warning, assertion échouée, ou crash.
- Affiche le monitoring mémoire à chaque étape.

### 2. Test de charge (plusieurs instances en parallèle)
```bash
python stress_test_charge.py
```
- Lance 3 à 5 instances du stress test UI en parallèle.
- Affiche un résumé des résultats et extraits de logs.

## Interpréter les résultats
- **OK** : Tous les tests passent, pas de crash, assertions métier validées.
- **ECHEC** : Un ou plusieurs tests plantent, assertion échouée, ou crash natif détecté.
- **Logs** : Les logs affichent les étapes, warnings, assertions, et monitoring mémoire.

## Ajouter de nouveaux tests/assertions
- Modifier `stress_test_ui.py` :
  - Ajouter des scénarios (ex : test d'un nouvel écran, d'une nouvelle action).
  - Ajouter des assertions métier via le module `debug_api`.
- Pour tester une nouvelle fonctionnalité, ajouter un helper ou une séquence de clics.

## CI/CD (GitHub Actions)
- Le workflow `.github/workflows/test-ui.yml` lance automatiquement le stress test UI à chaque push/pull request.
- Le merge est bloqué en cas de crash, d'erreur critique, ou d'assertion échouée.

## Conseils pour l'extension future
- Ajouter des hooks/tests pour le mode multi, l'API serveur, etc.
- Ajouter des assertions sur l'état du jeu après chaque nouvelle fonctionnalité.
- Intégrer des tests de performance (temps de réponse, charge mémoire).
- Documenter chaque nouveau test/scénario dans ce README.

---

**CardGame2 est maintenant équipé d'une suite de tests UI robuste, automatisée, et évolutive.** 