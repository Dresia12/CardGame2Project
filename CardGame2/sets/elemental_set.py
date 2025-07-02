from ..models.unit import Unit
from ..models.hero import Hero
from ..models.types import Rarity, Element
from typing import List

def burn_effect(target, amount, turns):
    # TODO: Appliquer un statut 'brûlure' qui inflige 'amount' dégâts sur 'turns' tours
    pass

def explosion_effect(targets, amount):
    # TODO: Inflige 'amount' dégâts bruts à tous les targets
    pass

def resurrection_effect(unit):
    # TODO: Ramène l'unité à 100% PV, invulnérable 1 tour
    pass

def get_elemental_set() -> List:
    cards = []
    # === FEU ===
    cards += [
        Hero("Pyron, le Flambeur des Cendres", 1150, 58, 0, element=Element.FEU),
        Unit("Salamandre Agile", Rarity.COMMON, 0, 50, 1000, description="25% Brûlure légère (30 dégâts/2 tours) à l'attaque.", element=Element.FEU),
        Unit("Impe du Brasier", Rarity.COMMON, 0, 50, 1000, description="À la mort, explose : 90 dégâts bruts aux ennemis adjacents.", element=Element.FEU),
        Unit("Fourmilion Incandescent", Rarity.COMMON, 0, 50, 1000, description="Résiste 50% aux dégâts Glace.", element=Element.FEU),
        Unit("Renarde Flamboyante", Rarity.COMMON, 0, 50, 1000, description="+10 ATK si une autre unité Feu alliée active.", element=Element.FEU),
        Unit("Dragonnet de Soufre", Rarity.UNCOMMON, 0, 53, 1050, description="40% Brûlure à l'attaque : 60 dégâts/3 tours.", element=Element.FEU),
        Unit("Élémental de Magma", Rarity.RARE, 0, 55, 1100, description="À l'entrée, Brûlure (90 dégâts/2 tours) aux ennemis adjacents.", element=Element.FEU),
        Unit("Phénix Rubicon", Rarity.MYTHIC, 0, 58, 1150, description="Ressuscite 1 fois (100% PV, 1 tour invulnérable). À la mort, explosion de feu : 120 dégâts + Brûlure zone.", element=Element.FEU),
    ]
    # === EAU ===
    cards += [
        Hero("Ondine la Guérisseuse", 1150, 58, 0, element=Element.EAU),
        Unit("Triton Passant", Rarity.COMMON, 0, 50, 1000, description="Soigne 30 PV à un allié adjacent chaque tour.", element=Element.EAU),
        Unit("Poisson-Glacier", Rarity.COMMON, 0, 50, 1000, description="Les ennemis frappés voient leur ATK réduite de 10 (1 tour).", element=Element.EAU),
        Unit("Néréide Jouvence", Rarity.COMMON, 0, 50, 1000, description="En entrant en jeu, supprime Brûlure sur elle-même et 1 allié au choix.", element=Element.EAU),
        Unit("Tortue Pèlerine", Rarity.COMMON, 0, 50, 1000, description="Subit -20% dégâts du Feu en tout temps.", element=Element.EAU),
        Unit("Méduse Bleue", Rarity.UNCOMMON, 0, 53, 1050, description="Toute attaque applique Affaiblissement : -12 ATK à la cible (1 tour).", element=Element.EAU),
        Unit("Krakenoni", Rarity.RARE, 0, 55, 1100, description="À l'arrivée, soigne 300 PV à tous alliés EAU, retire tous débuffs.", element=Element.EAU),
        Unit("Léviathan Émeraude", Rarity.MYTHIC, 0, 58, 1150, description="Régénère 100 PV à toutes unités alliées Eau chaque tour. Immunisé à toutes altérations d'état.", element=Element.EAU),
    ]
    # === TERRE ===
    cards += [
        Hero("Grom le Roc", 1300, 50, 0, element=Element.TERRE),
        Unit("Golem Moussu", Rarity.COMMON, 0, 45, 1100, description="Immunisé au Poison et à la Brûlure.", element=Element.TERRE),
        Unit("Taupe Géante", Rarity.COMMON, 0, 40, 1200, description="La première attaque reçue est annulée (camouflage).", element=Element.TERRE),
        Unit("Scarabée Obsidienne", Rarity.COMMON, 0, 48, 1050, description="Résiste 30% aux Ténèbres et Feu.", element=Element.TERRE),
        Unit("Hermine Boréale", Rarity.COMMON, 0, 42, 1100, description="Bloque une unité Air 1 tour (à son entrée).", element=Element.TERRE),
        Unit("Armadillo Stalactite", Rarity.UNCOMMON, 0, 49, 1250, description="À chaque coup reçu, gagne 15 ATK et 70 PV (1 fois par tour).", element=Element.TERRE),
        Unit("Géant de Basalte", Rarity.RARE, 0, 55, 1350, description="Transfère 30% dégâts reçus à un allié (absorption protectrice).", element=Element.TERRE),
        Unit("Colosse Tellurique", Rarity.MYTHIC, 0, 60, 1500, description="Ne peut être contrôlé + résistance 50% tout sauf Eau.", element=Element.TERRE),
    ]
    # === AIR ===
    cards += [
        Hero("Syrane la Fugitive", 1000, 50, 0, element=Element.AIR),
        Unit("Faucon Virevoltant", Rarity.COMMON, 0, 55, 900, description="35% de chance d'esquive à chaque attaque subie.", element=Element.AIR),
        Unit("Sylphelette", Rarity.COMMON, 0, 52, 950, description="Se déplace après chaque attaque, ne peut pas être touchée deux fois par la même unité ennemie (1 tour max).", element=Element.AIR),
        Unit("Moustique Cyclonique", Rarity.COMMON, 0, 48, 800, description="Attaque deux fois si la cible subit ralentissement.", element=Element.AIR),
        Unit("Elfe Brisesonge", Rarity.COMMON, 0, 49, 950, description="+8% d'esquive globale à tous alliés AIR.", element=Element.AIR),
        Unit("Huppe Rafale", Rarity.UNCOMMON, 0, 56, 1000, description="Peut repousser la cible d'une case, ou annuler un buff ennemi.", element=Element.AIR),
        Unit("Griffon des Nues", Rarity.RARE, 0, 60, 1100, description="Si un autre AIR allié actif, attaque deux cibles par tour.", element=Element.AIR),
        Unit("Grand Alizé", Rarity.MYTHIC, 0, 65, 1200, description="Immunise toute l'équipe AIR contre ralentissement, 20% d'esquive en bonus.", element=Element.AIR),
    ]
    # === LUMIÈRE ===
    cards += [
        Hero("Elira la Bienveillante", 1150, 58, 0, element=Element.LUMIERE),
        Unit("Hirondelle Lustrée", Rarity.COMMON, 0, 48, 1000, description="Soigne 40 PV à un allié Lumière (adjacent à l'attaque).", element=Element.LUMIERE),
        Unit("Cerf Alba", Rarity.COMMON, 0, 45, 1050, description="Immunisé à Malédiction, ignore brûlure et poison.", element=Element.LUMIERE),
        Unit("Héraut du Zénith", Rarity.COMMON, 0, 50, 1000, description="À chaque attaque, retire un effet négatif à la cible alliée la plus proche.", element=Element.LUMIERE),
        Unit("Souris Rayonnante", Rarity.COMMON, 0, 52, 950, description="Boost tous alliés Lumière dans la partie de +10 ATK tant qu'en vie.", element=Element.LUMIERE),
        Unit("Chérubin du Point du Jour", Rarity.UNCOMMON, 0, 55, 1050, description="Soigne toutes unités alliées à l'entrée (80 PV), retire leur dernier débuff.", element=Element.LUMIERE),
        Unit("Lion Choral", Rarity.RARE, 0, 56, 1100, description="Immunise toutes unités Lumière, dans la même zone/demi-tableau, contre Ténèbres et Ombre.", element=Element.LUMIERE),
        Unit("Séraphin du Solstice", Rarity.MYTHIC, 0, 60, 1150, description="Quand un allié Lumière est détruit, peut le ressusciter immédiatement sur un emplacement adjacent.", element=Element.LUMIERE),
    ]
    # === TÉNÈBRES ===
    cards += [
        Hero("Sorin l'Obscurci", 1100, 53, 0, element=Element.TENEBRES),
        Unit("Raton Nocturne", Rarity.COMMON, 0, 52, 950, description="Vole 20 PV en frappant, cumul possible.", element=Element.TENEBRES),
        Unit("Croquéombre", Rarity.COMMON, 0, 48, 1000, description="À chaque attaque réussie, inflige Malédiction (perd 30 PV/2 tours).", element=Element.TENEBRES),
        Unit("Impe Obscur", Rarity.COMMON, 0, 53, 1000, description="Prend +10 ATK à l'ennemi s'il l'achève.", element=Element.TENEBRES),
        Unit("Chauve-Souris d'Ébène", Rarity.COMMON, 0, 55, 900, description="À la mort d'une unité adjacente (ami ou ennemi), regagne 100 PV.", element=Element.TENEBRES),
        Unit("Harpie des Ténèbres", Rarity.UNCOMMON, 0, 58, 1050, description="Inflige Malédiction zone à l'attaque (tous ennemis zone, -15% PV max, stackable).", element=Element.TENEBRES),
        Unit("Spectre du Néant", Rarity.RARE, 0, 60, 1100, description='Immune à toute attaque "basique" 1 tour sur 2.', element=Element.TENEBRES),
        Unit("Hydre Infernale", Rarity.MYTHIC, 0, 62, 1150, description="À la mort d'une autre Ténèbres alliée, se ressuscite sur sa place (max : 3 fois).", element=Element.TENEBRES),
    ]
    # === FOUDRE ===
    cards += [
        Hero("Baltis l'Éclair", 1000, 58, 0, element=Element.FOUDRE),
        Unit("Vipère Voltique", Rarity.COMMON, 0, 55, 900, description="30% de paralyser la cible.", element=Element.FOUDRE),
        Unit("Étourneau Orageux", Rarity.COMMON, 0, 52, 950, description="Peut attaquer deux ennemis différents, mais pas deux fois le même.", element=Element.FOUDRE),
        Unit("Mulot de Fulgure", Rarity.COMMON, 0, 50, 1000, description="Gagne +8 ATK sur cible déjà paralysée.", element=Element.FOUDRE),
        Unit("Luciole Lumiflash", Rarity.COMMON, 0, 48, 1000, description="Toute attaque baisse la défense des ennemis touchés (-15% dégâts reçus).", element=Element.FOUDRE),
        Unit("Mangouste Statique", Rarity.UNCOMMON, 0, 55, 1050, description="Immunise contre la paralysie tous alliés FOUDRE.", element=Element.FOUDRE),
        Unit("Cavalier Fulgurant", Rarity.RARE, 0, 60, 1100, description='Attaque inflige "chaîne d\'éclairs" sur 2 ennemis en plus (demi-dégâts chacun).', element=Element.FOUDRE),
        Unit("Grand Griffon de Foudre", Rarity.MYTHIC, 0, 63, 1150, description="Toute attaque touche toutes cibles adjacentes (30% dégâts chacun, cumulable si plusieurs).", element=Element.FOUDRE),
    ]
    # === GLACE ===
    cards += [
        Hero("Nevis, Reine Hivernale", 1100, 53, 0, element=Element.GLACE),
        Unit("Lutin Pailleté", Rarity.COMMON, 0, 45, 1000, description="Tout ennemi attaqué subit ralentissement (–20% vitesse pour 1 tour)", element=Element.GLACE),
        Unit("Chouette Boréale", Rarity.COMMON, 0, 50, 1050, description="Esquive 25% des attaques Feu/Nature.", element=Element.GLACE),
        Unit("Morse Polaire", Rarity.COMMON, 0, 40, 1200, description="Tank, reçoit 10% de dégâts en moins de toutes sources.", element=Element.GLACE),
        Unit("Aiglon de Givre", Rarity.COMMON, 0, 52, 1000, description="+12 ATK contre unités Feu.", element=Element.GLACE),
        Unit("Esprit du Glaçon", Rarity.UNCOMMON, 0, 53, 1100, description="Première attaque gèle 100% (1 tour).", element=Element.GLACE),
        Unit("Naga Céruléenne", Rarity.RARE, 0, 57, 1200, description='Peut choisir une cible gelée ennemie et la "briser" (double dégâts, consomme le gel).', element=Element.GLACE),
        Unit("Valkyrie du Blizzard", Rarity.MYTHIC, 0, 62, 1250, description='Immunise tous alliés Glace au Feu (dégâts réduits -50%), applique "tempête de givre" (-4 PV par tour à tous ennemis)', element=Element.GLACE),
    ]
    # === NATURE ===
    cards += [
        Hero("Lysandre des Ronces", 1150, 58, 0, element=Element.NATURE),
        Unit("Vipère de Lierre", Rarity.COMMON, 0, 50, 1000, description="Attaque inflige Poison (60 dégâts/2 tours, cumulable).", element=Element.NATURE),
        Unit("Germain Rampant", Rarity.COMMON, 0, 45, 1100, description="Régénère 20 PV à chaque tour.", element=Element.NATURE),
        Unit("Chauve-souris Mousseuse", Rarity.COMMON, 0, 53, 950, description="Soigne 60 PV à un allié Nature au hasard lorsqu'elle attaque.", element=Element.NATURE),
        Unit("Enfant du Bosquet", Rarity.COMMON, 0, 48, 1050, description="Immunisé Poison, annule un débuff par combat (auto).", element=Element.NATURE),
        Unit("Dryade Vénéneuse", Rarity.UNCOMMON, 0, 53, 1050, description="Chaque Poison transféré à un nouvel ennemi adjacent à la cible (contamination).", element=Element.NATURE),
        Unit("Sylve-Alpha", Rarity.RARE, 0, 55, 1100, description="Régénère 10% PV max à tous Nature présents à son entrée.", element=Element.NATURE),
        Unit("Treant Majestueux", Rarity.MYTHIC, 0, 58, 1150, description="Quand il tombe sous 50% PV, double sa régénération et applique poison à tous ennemis au contact.", element=Element.NATURE),
    ]
    # === MÉTAL ===
    cards += [
        Hero("Maelia la Forge-Vie", 1300, 53, 0, element=Element.METAL),
        Unit("Méca-coccinelle", Rarity.COMMON, 0, 45, 1100, description="Armure : Diminue tous dégâts reçus de 10% (sauf anti-métal).", element=Element.METAL),
        Unit("Taupe-taupin", Rarity.COMMON, 0, 40, 1200, description="Ignore la première attaque subie (blindage profond).", element=Element.METAL),
        Unit("Chaton Ferreux", Rarity.COMMON, 0, 50, 1000, description="Renvoie 10% des dégâts reçus à l'attaquant.", element=Element.METAL),
        Unit("Fourmi Monteuse", Rarity.COMMON, 0, 48, 1150, description="Immunisée Stun et contrôle.", element=Element.METAL),
        Unit("Ourson Acier", Rarity.UNCOMMON, 0, 52, 1250, description="Chaque fois qu'il bloque, gagne +5 ATK cumulatif.", element=Element.METAL),
        Unit("Chevalier Lustré", Rarity.RARE, 0, 60, 1300, description="Octroie armure 20% à tous alliés Métal en jeu.", element=Element.METAL),
        Unit("Mastodon d'Argent", Rarity.MYTHIC, 0, 66, 1380, description="Imblocable, ne peut être déplacé ou repoussé. Renvoie 25% dégâts de zone.", element=Element.METAL),
    ]
    # === PSYCHIQUE ===
    cards += [
        Hero("Méandra la Sinuée", 1000, 50, 0, element=Element.PSYCHIQUE),
        Unit("Chat Hypnotique", Rarity.COMMON, 0, 55, 900, description="Sur attaque, 15% chance de confusion.", element=Element.PSYCHIQUE),
        Unit("Lutin Hallucinant", Rarity.COMMON, 0, 52, 950, description="L'ennemi attaqué perd 10 ATK pour 1 tour.", element=Element.PSYCHIQUE),
        Unit("Jacinthe Télépathe", Rarity.COMMON, 0, 48, 1000, description="Retire 1 buff à chaque attaque.", element=Element.PSYCHIQUE),
        Unit("Lézard Oculé", Rarity.COMMON, 0, 54, 950, description="À la mort, inflige 40 dégâts mentaux à tous voisins.", element=Element.PSYCHIQUE),
        Unit("Sphinx Petit", Rarity.UNCOMMON, 0, 57, 1050, description="Immunisé confusion/contrôle, booste tous alliés Psychique (+10 ATK tant qu'il vit).", element=Element.PSYCHIQUE),
        Unit("Lamproie Mentale", Rarity.RARE, 0, 60, 1100, description="Peut forcer une unité ennemie à rater son tour (CD 3).", element=Element.PSYCHIQUE),
        Unit("Kraken Illusoire", Rarity.MYTHIC, 0, 63, 1150, description="Toute zone autour subit confusion aléatoire 20% (alliés, ennemis, chaque tour).", element=Element.PSYCHIQUE),
    ]
    # === VIBRATION ===
    cards += [
        Hero("Ondiris la Sonore", 1000, 58, 0, element=Element.VIBRATION),
        Unit("Chauve-souris Bourdonnante", Rarity.COMMON, 0, 53, 950, description="À l'attaque, +5 ATK à un allié random.", element=Element.VIBRATION),
        Unit("Sylphide Harmonisante", Rarity.COMMON, 0, 50, 1000, description="Peut attaquer deux fois, mais différentes cibles.", element=Element.VIBRATION),
        Unit("Grillon Sonique", Rarity.COMMON, 0, 57, 900, description="Inflige aux ennemis : -10 ATK pour 1 tour.", element=Element.VIBRATION),
        Unit("Loutre Vibra-Aqueuse", Rarity.COMMON, 0, 54, 950, description="Ajoute +20 PV à tous alliés lors de son attaque (zone).", element=Element.VIBRATION),
        Unit("Araignée Accordée", Rarity.UNCOMMON, 0, 58, 1050, description="Quand elle attaque, tous alliés Vibra attaquent immédiatement (CD 2).", element=Element.VIBRATION),
        Unit("Baryton Astral", Rarity.RARE, 0, 60, 1100, description="Toute son équipe regagne 50 PV chaque début de tour.", element=Element.VIBRATION),
        Unit("Lamantin de Résonance", Rarity.MYTHIC, 0, 66, 1150, description="Les attaques alliées Vibra frappent de zone (touchent aussi 1 case autour, dégâts réduits -20%).", element=Element.VIBRATION),
    ]
    # === TEMPOREL ===
    cards += [
        Hero("Tiksal Chronomancien", 1000, 53, 0, element=Element.TEMPOREL),
        Unit("Souris de Sablier", Rarity.COMMON, 0, 51, 950, description="20% chance d'esquive totale chaque tour.", element=Element.TEMPOREL),
        Unit("Coccinelle Horo", Rarity.COMMON, 0, 50, 1000, description="Son attaque baisse le CD de toutes attaques alliées de 1 tour (ne stacke pas).", element=Element.TEMPOREL),
        Unit("Patient Papillon", Rarity.COMMON, 0, 55, 900, description="Peut retarder le mouvement d'une cible ennemie choisie (+1 tour, CD 2).", element=Element.TEMPOREL),
        Unit("Ecureuil des Âges", Rarity.COMMON, 0, 48, 1050, description="Restaure 50 PV à lui-même à chaque tour qui passe sans attaquer.", element=Element.TEMPOREL),
        Unit("Aigle de l'Instant", Rarity.UNCOMMON, 0, 56, 1050, description="Peut attaquer 2 fois tous les 3 tours.", element=Element.TEMPOREL),
        Unit("Sphynx du Retour", Rarity.RARE, 0, 59, 1100, description="Quand une unité alliée meurt, annule sa mort (elle rejoue le même tour mais une seule fois par combat).", element=Element.TEMPOREL),
        Unit("Basilic du Temps Brisé", Rarity.MYTHIC, 0, 63, 1150, description="Peut inverser la position de deux unités alliées ou ennemies et restaurer leur PV à ce qu'ils avaient deux tours plus tôt (CD 5).", element=Element.TEMPOREL),
    ]
    # === NÉANT ===
    cards += [
        Hero("Nihil, Main du Vide", 1150, 58, 0, element=Element.NEANT),
        Unit("Fureteur du Vide", Rarity.COMMON, 0, 50, 1000, description="À la mort, réduit PV max de l'ennemi tueur de 10% (cumulatif jusqu'à 2 fois).", element=Element.NEANT),
        Unit("Ombrelangue", Rarity.COMMON, 0, 52, 950, description="Sur attaque, retire 1 buff à la cible.", element=Element.NEANT),
        Unit("Taupe Abysse", Rarity.COMMON, 0, 45, 1100, description="Immunisée à tout effet de soin ou résurrection.", element=Element.NEANT),
        Unit("Mégère Persécutée", Rarity.COMMON, 0, 49, 1000, description="Ignore tout effet positif d'alliés proches (n'en reçoit pas, ni ne les donne).", element=Element.NEANT),
        Unit("Spectre Famine", Rarity.UNCOMMON, 0, 53, 1050, description='À la mort, inflige "Dessèchement" : bloque tout soin reçu pour l\'ennemi tueur 2 tours.', element=Element.NEANT),
        Unit("Apostat du Rien", Rarity.RARE, 0, 56, 1100, description="Peut choisir un effet ennemi et le désactiver pour 2 tours (effets passifs inclus).", element=Element.NEANT),
        Unit("Crépuscule Exilique", Rarity.MYTHIC, 0, 58, 1150, description="1 fois par combat, bannit une unité adverse (retirée définitivement) si PV < 20%.", element=Element.NEANT),
    ]
    # === ARCANIQUE ===
    cards += [
        Hero("Opalys la Paradoxe", 1050, 55, 0, element=Element.ARCANIQUE),
        Unit("Pixie Copieuse", Rarity.COMMON, 0, 47, 1000, description="À la mort, octroie un bouclier de son dernier type de buff à un allié proche (copié).", element=Element.ARCANIQUE),
        Unit("Rat de Magie", Rarity.COMMON, 0, 55, 900, description="20% chance de répliquer la prochaine attaque reçue en contre-attaque.", element=Element.ARCANIQUE),
        Unit("Minéral Lectomancien", Rarity.COMMON, 0, 50, 1000, description="Immunisé à tout effet anti-magie.", element=Element.ARCANIQUE),
        Unit("Faon Runique", Rarity.COMMON, 0, 49, 1050, description="À l'entrée, octroie +10% ATK à un allié avec buff magique.", element=Element.ARCANIQUE),
        Unit("Chouette de Dispersion", Rarity.UNCOMMON, 0, 49, 1100, description="À l'attaque, retire 1 buff à 2 ennemis différents ciblés.", element=Element.ARCANIQUE),
        Unit("Sphinx d'Entropie", Rarity.RARE, 0, 60, 1100, description="Peut absorber un effet négatif d'un allié et le renvoyer sur un ennemi (CD 2).", element=Element.ARCANIQUE),
        Unit("Chimère du Paradoxe", Rarity.MYTHIC, 0, 64, 1150, description="1/5 tours – Peut copier un ennemi présent (sauf héros/mythique, copie PV, ATK, effets de base, mais pas le passif).", element=Element.ARCANIQUE),
    ]
    # === CRISTAL ===
    cards += [
        Hero("Arieste d'Opale", 1200, 53, 0, element=Element.CRISTAL),
        Unit("Gerbille Prisme", Rarity.COMMON, 0, 49, 1000, description="Toute attaque reçue renvoie 10% dégâts à un ennemi aléatoire.", element=Element.CRISTAL),
        Unit("Ascalaphe à Facettes", Rarity.COMMON, 0, 45, 1050, description="Absorbe 10% dégâts magiques subis pour eux-mêmes (bouclier temporaire).", element=Element.CRISTAL),
        Unit("Lapin Polyèdre", Rarity.COMMON, 0, 50, 1000, description="Gagne 5% PV max à chaque fois qu'un allié Cristal active un bouclier.", element=Element.CRISTAL),
        Unit("Salamandre Opalescente", Rarity.COMMON, 0, 54, 950, description="Si tuée, applique +20% dégâts à la prochaine attaque alliée.", element=Element.CRISTAL),
        Unit("Scinie Symphonique", Rarity.UNCOMMON, 0, 53, 1100, description="Immune à la première destruction de barrière (toutes les 2 tours, CD 2).", element=Element.CRISTAL),
        Unit("Hibou Réfléteur", Rarity.RARE, 0, 60, 1100, description="Peut renvoyer la totalité d'un dégât de sort par combat (CD 3).", element=Element.CRISTAL),
        Unit("Griffon Crysalide", Rarity.MYTHIC, 0, 63, 1150, description="Tant qu'il est en jeu, tous alliés Cristal bénéficient d'un double rebond (2 x 10% dégâts renvoyés à deux cibles à chaque attaque encaissée).", element=Element.CRISTAL),
    ]
    # === CHAOS ===
    cards += [
        Hero("Zygon le Dément", 1050, 60, 0, element=Element.CHAOS),
        Unit("Gobelin Sangpourpre", Rarity.COMMON, 0, 58, 950, description="30% chance de s'auto-infliger l'attaque lancée (dégâts sur lui-même).", element=Element.CHAOS),
        Unit("Micro-Capricorne", Rarity.COMMON, 0, 46, 1050, description="Peut échanger sa place avec une unité alliée (aléatoire).", element=Element.CHAOS),
        Unit("Crapaud Folie", Rarity.COMMON, 0, 56, 900, description="À chaque attaque, effet aléatoire sur la cible (buff, débuff, dommage, soin).", element=Element.CHAOS),
        Unit("Rat d'Entropie", Rarity.COMMON, 0, 52, 1000, description="10% chance d'exploser, inflige 120 dégâts à toutes unités voisines (y compris alliés).", element=Element.CHAOS),
        Unit("Hyène Décousue", Rarity.UNCOMMON, 0, 59, 1050, description='Peut "mordre" un allié chaque attaque (inflige 50 dégâts, mais booste +5 ATK permanent).', element=Element.CHAOS),
        Unit("Manticore du Désordre", Rarity.RARE, 0, 66, 1100, description='Peut déclencher (une fois tous les 2 tours) "Chaos total" : éparpille les positions de toutes créatures sur le plateau.', element=Element.CHAOS),
        Unit("Chimère du Pandémonium", Rarity.MYTHIC, 0, 70, 1150, description="À l'attaque, tire 2 effets aléatoires sur la même cible (Dmg+Buff, ou Heal+Curse, etc.)", element=Element.CHAOS),
    ]
    # === ORDRE ===
    cards += [
        Hero("Sir Galvian, Régent Doré", 1200, 55, 0, element=Element.ORDRE),
        Unit("Soldat Pair", Rarity.COMMON, 0, 50, 1050, description="S'il attaque en même temps qu'un autre Ordre, gagne +10 ATK ce tour.", element=Element.ORDRE),
        Unit("Chouette Perceuse", Rarity.COMMON, 0, 48, 1000, description="Augmente de +5 ATK tous alliés Ordre présents (passif cumulable).", element=Element.ORDRE),
        Unit("Juge Braillard", Rarity.COMMON, 0, 45, 1100, description="Empêche les unités ennemies de gagner buffs pendant 1 tour après chaque attaque.", element=Element.ORDRE),
        Unit("Héraut Rigide", Rarity.COMMON, 0, 55, 1000, description="Immunisé contrôle mental et confusion.", element=Element.ORDRE),
        Unit("Garde de la Balance", Rarity.UNCOMMON, 0, 53, 1050, description="Quand une attaque alliée raterait, il peut la refaire immédiatement (1 fois par tour).", element=Element.ORDRE),
        Unit("Croisé de l'Équité", Rarity.RARE, 0, 58, 1100, description="Peut imposer l'ordre : annule tous bonus/malus temporaires de la cible (CD 2).", element=Element.ORDRE),
        Unit("Ange de la Résolution", Rarity.MYTHIC, 0, 63, 1150, description="Immunise toute l'équipe Ordre aux effets de chaos tant qu'il est en jeu ; +10% dégâts à tous alliés Ordre.", element=Element.ORDRE),
    ]
    # === POISON ===
    cards += [
        Hero("Malmor, Seigneur Venin", 1050, 58, 0, element=Element.POISON),
        Unit("Aspic Fangeux", Rarity.COMMON, 0, 56, 900, description="Empêche la cible d'être soignée pendant 2 tours.", element=Element.POISON),
        Unit("Scarabée Vireux", Rarity.COMMON, 0, 48, 1050, description="Inflige aussi 25 dégâts à l'allié adjacent à la cible (propagation).", element=Element.POISON),
        Unit("Salamandre Akaëlle", Rarity.COMMON, 0, 51, 1000, description="Double tous poisons infligés si la cible est déjà empoisonnée.", element=Element.POISON),
        Unit("Chauve-Souris Fielleuse", Rarity.COMMON, 0, 54, 950, description="Au début chaque tour, inflige 30 dégâts à un ennemi au hasard.", element=Element.POISON),
        Unit("Veuve d'Acide", Rarity.UNCOMMON, 0, 53, 1050, description="Propage tous nouveaux poisons aux ennemis voisins lors de son attaque.", element=Element.POISON),
        Unit("Lamia délétère", Rarity.RARE, 0, 60, 1100, description="Ignore toute immunité anti-poison.", element=Element.POISON),
        Unit("Basilic Épidémique", Rarity.MYTHIC, 0, 68, 1150, description="Chaque décès d'un ennemi propage tous poisons restants à 2 ennemis aléatoires.", element=Element.POISON),
    ]
    # === MORT ===
    cards += [
        Hero("Morticia l'Errante", 1150, 60, 0, element=Element.MORT),
        Unit("Spectre Hurleur", Rarity.COMMON, 0, 51, 1000, description="10% de chance de ressusciter à chaque mort (max 2).", element=Element.MORT),
        Unit("Goule Pestilentielle", Rarity.COMMON, 0, 55, 900, description="Attaque regagne 30% des dégâts infligés en PV.", element=Element.MORT),
        Unit("Moissonneur Squelettique", Rarity.COMMON, 0, 48, 1050, description="Soin reçu divisé par deux (même en autosoins ou alliés).", element=Element.MORT),
        Unit("Hibou de Nécropole", Rarity.COMMON, 0, 50, 1000, description="Chaque allié Mort ressuscité gagne +10 ATK jusqu'à la fin du combat (cumulatif).", element=Element.MORT),
        Unit("Crépusculien", Rarity.UNCOMMON, 0, 53, 1050, description="Peut ressusciter un Mort tombé lors de sa mort (à 50% PV, 1 par partie).", element=Element.MORT),
        Unit("Dullahan Funeste", Rarity.RARE, 0, 60, 1100, description="Ignore toute réduction de dégâts ennemie et bloque tous les soins de la cible.", element=Element.MORT),
        Unit("Liche de l'Infini", Rarity.MYTHIC, 0, 69, 1150, description="À sa mort, ressuscite immédiatement (1 fois), détruit tous soins en jeu à ce moment. Chaque résurrection donne +20 ATK.", element=Element.MORT),
    ]
    # === VIE ===
    cards += [
        Hero("Héliara la Rayonnante", 1200, 53, 0, element=Element.VIE),
        Unit("Cureuil", Rarity.COMMON, 0, 50, 1000, description="À chaque attaque, soigne l'allié Vie le plus blessé de 40 PV.", element=Element.VIE),
        Unit("Moineau Serein", Rarity.COMMON, 0, 47, 1050, description="Retire 1 effet négatif sur un allié à chaque entrée en jeu.", element=Element.VIE),
        Unit("Faon Bénit", Rarity.COMMON, 0, 46, 1100, description="Première fois qu'il subirait la mort, il survit à 1 PV.", element=Element.VIE),
        Unit("Tortue Miraculeuse", Rarity.COMMON, 0, 40, 1200, description="Réduit de 20% tous dégâts reçus.", element=Element.VIE),
        Unit("Chérubin Zéphyr", Rarity.UNCOMMON, 0, 53, 1050, description="Peut transférer un effet positif à un allié de ton choix par attaque.", element=Element.VIE),
        Unit("Seraphin du Matin", Rarity.RARE, 0, 60, 1100, description="Immunise un allié Vie aux dégâts pour 1 attaque (CD 2).", element=Element.VIE),
        Unit("Licorne Renaissance", Rarity.MYTHIC, 0, 63, 1150, description="Peut ressusciter une fois chaque unité Vie (à 40% PV). Tous soins sont augmentés de +40%.", element=Element.VIE),
    ]
    # === TECHNOLOGIQUE ===
    cards += [
        Hero("Léandre le Réinventeur", 1100, 60, 0, element=Element.TECHNOLOGIQUE),
        Unit("Souris à Fumée", Rarity.COMMON, 0, 53, 1000, description="Quand elle subit une attaque, esquive 1 fois/2.", element=Element.TECHNOLOGIQUE),
        Unit("Grenouille Pile", Rarity.COMMON, 0, 47, 1100, description="Peut transférer 30 PV de soi à un allié techno à chaque attaque.", element=Element.TECHNOLOGIQUE),
        Unit("Drone Tapageur", Rarity.COMMON, 0, 57, 950, description="Peut désactiver temporairement un bouclier ennemi (CD 2).", element=Element.TECHNOLOGIQUE),
        Unit("Gecko Nomade", Rarity.COMMON, 0, 48, 1000, description="Immune contrôle un tour sur deux.", element=Element.TECHNOLOGIQUE),
        Unit("Rat Modulaire", Rarity.UNCOMMON, 0, 56, 1050, description="À chaque attaque, donne +7 ATK à un allié techno (cumulable).", element=Element.TECHNOLOGIQUE),
        Unit("Faucon Fixeur", Rarity.RARE, 0, 61, 1100, description="À chaque attaque, répare tous boucliers techno de 100 PV.", element=Element.TECHNOLOGIQUE),
        Unit("Tigre du Futur", Rarity.MYTHIC, 0, 66, 1150, description='Tous alliés techno gagnent "surcharge" (attaque x2 pour leur prochaine action, 1 fois chacun par combat).', element=Element.TECHNOLOGIQUE),
    ]
    # === OMBRE ===
    cards += [
        Hero("Nira l'Ensorceleuse d'Ombre", 1000, 58, 0, element=Element.OMBRE),
        Unit("Vipère Insondable", Rarity.COMMON, 0, 54, 950, description="20% de chance d'esquiver toute attaque.", element=Element.OMBRE),
        Unit("Lémurien Masqué", Rarity.COMMON, 0, 51, 1050, description="Vole un buff à la cible lors de l'attaque.", element=Element.OMBRE),
        Unit("Fouine de Nuit", Rarity.COMMON, 0, 48, 1000, description="Commence chaque combat en furtivité (ne peut pas être ciblé sauf par AoE).", element=Element.OMBRE),
        Unit("Hibou du Voile", Rarity.COMMON, 0, 58, 900, description="Peut retirer 1 buff d'un ennemi à chaque attaque réussie.", element=Element.OMBRE),
        Unit("Corbeau Maudit", Rarity.UNCOMMON, 0, 56, 1050, description='Si tué, applique "Aveuglement" (tous ennemis loupent la prochaine attaque).', element=Element.OMBRE),
        Unit("Panthère Fantôme", Rarity.RARE, 0, 62, 1100, description="Est indétectable chaque fois qu'elle tue un ennemi (jusqu'à la fin du prochain tour).", element=Element.OMBRE),
        Unit("Ombre Prime", Rarity.MYTHIC, 0, 68, 1150, description="Tant qu'elle est en jeu, tous alliés Ombre esquivent la première attaque reçue chaque tour (immunité la 1ère fois).", element=Element.OMBRE),
    ]
    # === NEUTRE ===
    cards += [
        Hero("Argo le Voyageur", 1150, 55, 0, element=Element.NEUTRE),
        Unit("Souriceau Caméléon", Rarity.COMMON, 0, 50, 1000, description="À chaque attaque, prend une spécialité aléatoire d'une unité adverse (+5 ATK de ce type pendant 1 tour).", element=Element.NEUTRE),
        Unit("Pinson Universel", Rarity.COMMON, 0, 45, 1050, description="Octroie +30 PV à un allié de n'importe quel élément au hasard à l'entrée.", element=Element.NEUTRE),
        Unit("Pangolin Polyvalent", Rarity.COMMON, 0, 46, 1100, description="Peut annuler la faiblesse d'un allié contre un élément ennemi (1 fois par combat).", element=Element.NEUTRE),
        Unit("Mulot Opportuniste", Rarity.COMMON, 0, 54, 950, description="Copie le passif d'une unité alliée de ton équipe au hasard (1 fois à l'entrée).", element=Element.NEUTRE),
        Unit("Blaireau Tactique", Rarity.UNCOMMON, 0, 53, 1050, description="Peut accorder à un allié/soi le droit de rejouer immédiatement le même tour (CD 3).", element=Element.NEUTRE),
        Unit("Échidné Arbitraire", Rarity.RARE, 0, 60, 1100, description="À chaque attaque, copie un buff actif d'un ennemi et l'applique à lui-même pour 2 tours.", element=Element.NEUTRE),
        Unit("Phoenix Gris", Rarity.MYTHIC, 0, 69, 1150, description="À sa mort, se réinvoque sous un élément de ton choix, stats et passif deviennent ceux du nouvel élément (sauf légendaire).", element=Element.NEUTRE),
    ]
    # Purge automatique : ne garder que les objets valides
    cards = [c for c in cards if hasattr(c, "name") and hasattr(c, "card_type")]
    return cards 