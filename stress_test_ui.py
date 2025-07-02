import sys
import time
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Import dynamique de l'app principale
try:
    from CardGame2.ui_app import launch_ui_for_test
    from CardGame2.ui.utils import print_memory_diagnostics  # type: ignore
    import CardGame2.debug_api as debug_api
except ImportError:
    print("[ERROR] Impossible d'importer CardGame2.ui_app.launch_ui_for_test, print_memory_diagnostics ou debug_api.")
    sys.exit(1)

# Helper pour trouver un bouton par son texte
def find_button(widget, text):
    for btn in widget.findChildren(QPushButton):
        if btn.text() == text:
            return btn
    return None

def click_button(btn, app, label=None):
    if btn:
        QTest.mouseClick(btn, Qt.LeftButton)
        app.processEvents()
        time.sleep(0.15)
        print(f"[STRESS] Clicked: {label or btn.text()}")
    else:
        print(f"[WARNING] Bouton '{label}' introuvable")

def stress_navigation(app, window):
    print("[STRESS] Navigation extrême entre écrans...")
    for i in range(10):
        for btn_text in ["Decks", "Collection", "Boutique", "Jouer", "Retour"]:
            btn = find_button(window, btn_text)
            click_button(btn, app, btn_text)
        print_memory_diagnostics()
        time.sleep(0.1)

def stress_play_game(app, window):
    print("[STRESS] Lancement et abandon de parties...")
    play_btn = find_button(window, "Jouer")
    click_button(play_btn, app, "Jouer")
    time.sleep(0.5)
    start_btn = find_button(window, "Démarrer") or find_button(window, "Start")
    click_button(start_btn, app, "Démarrer")
    time.sleep(1)
    # Simule 3 clics sur "Fin de tour" ou "Abandon"
    for _ in range(3):
        end_btn = find_button(window, "Fin de tour")
        click_button(end_btn, app, "Fin de tour")
        time.sleep(0.3)
    abandon_btn = find_button(window, "Abandon")
    click_button(abandon_btn, app, "Abandon")
    print_memory_diagnostics()
    time.sleep(0.5)
    retour_btn = find_button(window, "Retour")
    click_button(retour_btn, app, "Retour")
    time.sleep(0.2)

def assert_collection_increased(before, after):
    if sum(after.values()) <= sum(before.values()):
        print(f"[ASSERTION FAILED] La collection n'a pas augmenté après ouverture de booster !")
    else:
        print(f"[ASSERTION OK] Collection augmentée.")

def assert_money_decreased(before, after):
    if after >= before:
        print(f"[ASSERTION FAILED] La monnaie n'a pas diminué après achat !")
    else:
        print(f"[ASSERTION OK] Monnaie diminuée.")

def assert_deck_changed(before, after):
    if before == after:
        print(f"[ASSERTION FAILED] Le deck n'a pas changé après édition !")
    else:
        print(f"[ASSERTION OK] Deck modifié.")

def stress_shop_boosters(app, window):
    print("[STRESS] Achat et ouverture de boosters...")
    shop_btn = find_button(window, "Boutique")
    click_button(shop_btn, app, "Boutique")
    before_money = debug_api.get_money()
    before_collection = debug_api.get_collection().copy()
    buy_btn = find_button(window, "Acheter") or find_button(window, "Buy")
    click_button(buy_btn, app, "Acheter")
    after_money = debug_api.get_money()
    open_btn = find_button(window, "Ouvrir") or find_button(window, "Open")
    click_button(open_btn, app, "Ouvrir")
    after_collection = debug_api.get_collection().copy()
    assert_money_decreased(before_money, after_money)
    assert_collection_increased(before_collection, after_collection)
    print_memory_diagnostics()
    retour_btn = find_button(window, "Retour")
    click_button(retour_btn, app, "Retour")
    time.sleep(0.2)

def stress_deck_edit(app, window):
    print("[STRESS] Création/édition de deck...")
    deck_btn = find_button(window, "Decks")
    click_button(deck_btn, app, "Decks")
    before_decks = debug_api.get_decks().copy()
    add_btn = find_button(window, "Ajouter") or find_button(window, "Add")
    click_button(add_btn, app, "Ajouter")
    save_btn = find_button(window, "Sauvegarder") or find_button(window, "Save")
    click_button(save_btn, app, "Sauvegarder")
    after_decks = debug_api.get_decks().copy()
    assert_deck_changed(before_decks, after_decks)
    print_memory_diagnostics()
    retour_btn = find_button(window, "Retour")
    click_button(retour_btn, app, "Retour")
    time.sleep(0.2)

def stress_combat(app, window):
    print("[STRESS] Combat automatisé...")
    play_btn = find_button(window, "Jouer")
    click_button(play_btn, app, "Jouer")
    time.sleep(0.5)
    start_btn = find_button(window, "Démarrer") or find_button(window, "Start")
    click_button(start_btn, app, "Démarrer")
    time.sleep(1)
    for i in range(10):
        end_btn = find_button(window, "Fin de tour")
        if not end_btn:
            print(f"[STRESS] Bouton 'Fin de tour' introuvable au tour {i+1}, fin du combat ou bug.")
            break
        click_button(end_btn, app, f"Fin de tour (tour {i+1})")
        time.sleep(0.3)
    abandon_btn = find_button(window, "Abandon")
    if abandon_btn:
        click_button(abandon_btn, app, "Abandon")
        print("[STRESS] Combat abandonné proprement.")
    else:
        print("[STRESS] Impossible d'abandonner, combat déjà terminé ou bug.")
    print_memory_diagnostics()
    retour_btn = find_button(window, "Retour")
    click_button(retour_btn, app, "Retour")
    time.sleep(0.2)

def stress_test():
    app, window = launch_ui_for_test()
    app.processEvents()
    time.sleep(1)
    print_memory_diagnostics()
    # Navigation extrême
    stress_navigation(app, window)
    # Lancement/abandon de parties
    stress_play_game(app, window)
    # Combat automatisé
    stress_combat(app, window)
    # Achat/ouverture boosters
    stress_shop_boosters(app, window)
    # Création/édition de deck
    stress_deck_edit(app, window)
    print("[STRESS] Test avancé terminé. Vérifie la console pour toute anomalie ou crash.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    stress_test() 