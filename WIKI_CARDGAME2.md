# CardGame2 – Wiki

## Sommaire
- [1. Jeu : Règles et fonctionnement](#1-jeu--règles-et-fonctionnement)
  - [But du jeu](#but-du-jeu)
  - [Déroulement d'une partie](#déroulement-dune-partie)
  - [Effets et mécaniques](#effets-et-mécaniques)
  - [Statuts et interactions élémentaires](#statuts-et-interactions-élémentaires)
  - [FAQ](#faq)
- [2. Cartes : Types et affichage](#2-cartes--types-et-affichage)
  - [Exemple d'affichage d'une carte](#exemple-daffichage-dune-carte)
  - [Unités](#unités)
  - [Héros](#héros)
  - [Sorts & Équipements](#sorts--équipements)
- [3. Decks et Collection](#3-decks-et-collection)
- [4. Interface et accessibilité](#4-interface-et-accessibilité)
- [5. Avancées, extensions et communauté](#5-avancées-extensions-et-communauté)
- [6. Glossaire et conseils](#6-glossaire-et-conseils)

---

## 1. Jeu : Règles et fonctionnement

### But du jeu
Construire un deck, affronter l'IA ou d'autres joueurs, collectionner toutes les cartes et optimiser ses stratégies.

### Déroulement d'une partie
- Chaque joueur commence avec un héros et 4 unités sur le terrain.
- Pioche initiale de 5 cartes, puis 1 carte piochée par tour.
- Mana pour jouer des cartes, activation de capacités spéciales, gestion des statuts.
- Victoire par réduction des PV du héros adverse à 0.

### Effets et mécaniques
- **Effets temporaires** : poison, boost, shield, freeze, etc.
- **Effets permanents** : bonus/malus, auras, passifs.
- **Interactions élémentaires** : Feu > Glace, Eau > Feu, etc.

#### Exemples d'effets
- **Poison** : inflige des dégâts chaque tour.
- **Boost** : augmente temporairement l'attaque.
- **Shield** : absorbe les dégâts, soigne à l'expiration.

### Statuts et interactions élémentaires
- Liste complète des statuts (poison, gel, silence, etc.).
- Tableau des faiblesses élémentaires.

### FAQ
- Questions fréquentes sur les règles, la collection, les boosters, etc.

---

## 2. Cartes : Types et affichage

### Exemple d'affichage d'une carte
```
┌─────────────────────────────┐
│  [Image]                    │
│  Nom : Pyrodrake            │
│  Type : Unité               │
│  Rareté : Mythic            │
│  Coût : 5                   │
│  ATK : 72   DEF : 22   PV : 1200
│  Description : Explosion : inflige des dégâts élément feu...
└─────────────────────────────┘
```
- **Icônes d'effets** affichées en overlay.
- **Tooltip** détaillé au survol.

### Unités
| Image | Nom | Rareté | ATK | DEF | PV | Élément | Description |
|-------|-----|--------|-----|-----|----|---------|-------------|
// ... (générer la table à partir du set) ...

### Héros
| Image | Nom | PV | ATK | DEF | Élément | Pouvoir spécial | Passif |
|-------|-----|----|-----|-----|---------|-----------------|--------|
// ... (générer la table à partir du set) ...

### Sorts & Équipements
| Nom | Rareté | Coût | Élément | Description |
|-----|--------|------|---------|-------------|
// ... (générer la table à partir du set) ...

---

## 3. Decks et Collection
- Un deck = 1 héros + 20 cartes max (unités, sorts, équipements).
- 5 decks maximum par joueur.
- 2 exemplaires max par carte dans un deck.
- Toutes les cartes possédées sont visibles dans la collection.
- Les doublons (plus de 2 exemplaires) sont automatiquement convertis en pièces.
- Un booster = 8 cartes (3 unités, 4 sorts/équipements, 1 bonus).
- Les probabilités de rareté sont affichées.
- Les doublons sont transformés en pièces lors de l'ouverture.

---

## 4. Interface et accessibilité
- Navigation clavier complète (tab, flèches, Entrée/Espace).
- Feedback visuel et sonore (animations, sons, popups).
- Mode daltonien et accessibilité (aura adaptée, tooltips explicites).

---

## 5. Avancées, extensions et communauté
- Mode multi-joueur (hotseat, réseau).
- Nouvelles familles de cartes, nouveaux effets.
- API serveur, migration cloud.
- Lien vers le guide de contribution, Discord, issues GitHub, email de contact.

---

## 6. Glossaire et conseils
- Explication de tous les termes du jeu.
- Tableau des faiblesses élémentaires.
- Exemples de combos et stratégies.
- Section "Trucs & Astuces" pour les nouveaux joueurs.
- Changelog : historique des mises à jour.

---

# (Les sections Unités, Héros, Sorts & Équipements seront générées automatiquement à partir des sets du jeu) 