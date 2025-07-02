from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QListWidget, QMessageBox, QTableWidget, QTableWidgetItem
from CardGame2.data_manager import DataManager
from CardGame2.models.hero import Hero
from CardGame2.sets.base_set import get_base_set
from CardGame2.models.player import Player, AIPlayer
from CardGame2.combat.battle import Battle
import random
from typing import Optional
from CardGame2.ui.components import (
    StyledButton, StatsPanel, DeckPreviewPanel, LoadingPopup, HelpDialog, make_styled_button, NotificationPopup
)
from CardGame2.screens.combat_screen import CombatScreen
import os
from PyQt5.QtGui import QKeyEvent, QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from CardGame2.ui.style_constants import PLAY_BTN_STYLE, BACK_BTN_STYLE
from CardGame2.ui.resources import UI_TEXTS
from CardGame2.ui.utils import safe_add_widget, safe_clear_layout, is_layout_valid, is_widget_valid  # type: ignore

data_manager = DataManager()

def log_debug(msg):
    with open(os.path.join(os.path.dirname(__file__), '../../debug_cardgame2.log'), 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

class PlayMenu(QWidget):
    def __init__(self, player_name: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        self.label = QLabel("Mode de jeu :")
        self.label.setToolTip(UI_TEXTS['play_label'])
        self.solo_button = StyledButton("Solo")
        self.solo_button.setToolTip(UI_TEXTS['solo_button'])
        self.multi_button = StyledButton("Multi (à venir)")
        self.multi_button.setEnabled(False)
        self.multi_button.setToolTip(UI_TEXTS['multi_button'])
        self.deck_label = QLabel("Choisissez un deck :")
        self.deck_label.setToolTip(UI_TEXTS['deck_label'])
        self.deck_combo = QComboBox()
        self.deck_combo.addItems([f"Deck {i+1}" for i in range(5)])
        self.deck_combo.setToolTip(UI_TEXTS['deck_combo'])
        self.deck_cards_list = QListWidget()
        self.deck_cards_list.setToolTip(UI_TEXTS['deck_cards_list'])
        self.deck_summary_panel = StatsPanel("Résumé du deck", {"-": "-"})
        self.deck_summary_panel.setToolTip(UI_TEXTS['deck_summary_panel'])
        self.deck_preview_panel = DeckPreviewPanel({}, get_base_set())
        self.deck_preview_panel.setToolTip(UI_TEXTS['deck_preview_panel'])
        self.play_button = make_styled_button(
            "Jouer !", PLAY_BTN_STYLE, "Lancer une partie contre l'IA", self.start_game
        )
        self.play_button.setToolTip(UI_TEXTS['play_play_button'])
        self.back_button = make_styled_button(
            "Retour", BACK_BTN_STYLE, "Retour au menu principal", self.return_to_main
        )
        self.back_button.setToolTip(UI_TEXTS['play_back_button'])
        self.reset_history_button = StyledButton("Réinitialiser l'historique")
        self.reset_history_button.setStyleSheet("background: #e74c3c; color: #fff; font-weight: bold; font-size: 15px; margin-top: 10px;")
        self.reset_history_button.setToolTip(UI_TEXTS['reset_history_button'])
        self.reset_history_button.clicked.connect(self.reset_history)
        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(["Date", "Deck", "Résultat", "Tours", "Récompense"])
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionMode(QTableWidget.NoSelection)
        self.history_table.setToolTip(UI_TEXTS['history_table'])
        layout.addWidget(self.label)
        layout.addWidget(self.solo_button)
        layout.addWidget(self.multi_button)
        layout.addWidget(self.deck_label)
        layout.addWidget(self.deck_combo)
        layout.addWidget(self.deck_summary_panel)
        layout.addWidget(self.deck_preview_panel)
        layout.addWidget(QLabel("Cartes du deck :"))
        layout.addWidget(self.deck_cards_list)
        layout.addWidget(self.history_table)
        layout.addWidget(self.reset_history_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.back_button)
        self.setLayout(layout)
        self.solo_button.clicked.connect(self.start_game)
        self.deck_combo.currentIndexChanged.connect(self.refresh_deck_cards)
        self.back_button.clicked.connect(self.return_to_main)
        self.refresh_deck_cards()
        self.refresh_history()
        self.setTabOrder(self.solo_button, self.deck_combo)
        self.setTabOrder(self.deck_combo, self.back_button)
        self.solo_button.setFocus()
    def select_solo(self) -> None:
        QMessageBox.information(self, "Solo", "Mode solo sélectionné. (À implémenter)")
    def refresh_deck_cards(self) -> None:
        self.loading_popup = LoadingPopup("Chargement du deck...", self)
        self.loading_popup.show()
        try:
            idx = self.deck_combo.currentIndex()
            decks = data_manager.get_decks()
            self.deck_cards_list.clear()
            if 0 <= idx < len(decks):
                deck = decks[idx]
                # Affichage des cartes (héros, unités, autres)
                if deck.get("hero"):
                    self.deck_cards_list.addItem(f"Héros : {deck['hero']['name']}")
                if deck.get("units"):
                    for u in deck["units"]:
                        self.deck_cards_list.addItem(f"Unité : {u}")
                if deck.get("cards"):
                    for c in deck["cards"]:
                        self.deck_cards_list.addItem(f"Carte : {c}")
                self.deck_summary_panel.set_stats(self.deck_summary(deck))
                self.deck_preview_panel.setParent(None)
                self.deck_preview_panel = DeckPreviewPanel(deck, get_base_set())
                layout_obj = self.layout()
                if layout_obj is not None and hasattr(layout_obj, 'insertWidget'):
                    layout_obj.insertWidget(6, self.deck_preview_panel)
            else:
                self.deck_summary_panel.set_stats({"-": "-"})
                self.deck_preview_panel.setParent(None)
                self.deck_preview_panel = DeckPreviewPanel({}, get_base_set())
                layout_obj = self.layout()
                if layout_obj is not None and hasattr(layout_obj, 'insertWidget'):
                    layout_obj.insertWidget(6, self.deck_preview_panel)
        finally:
            self.loading_popup.close()
    def deck_summary(self, deck) -> dict:
        hero = deck.get("hero")
        units = deck.get("units", [])
        cards = deck.get("cards", [])
        d = {}
        if hero:
            d["Héros"] = hero["name"]
        d["Unités"] = f"{len(units)} / 4"
        d["Autres cartes"] = f"{len(cards)}"
        return d
    def return_to_main(self) -> None:
        log_debug("[DEBUG] Retour au menu principal depuis PlayMenu")
        try:
            self.parent().parent().go_to_menu(self.parent().parent().player_name)
            NotificationPopup("Retour au menu principal", 1500, self).show()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans return_to_main : {e}")
            QMessageBox.critical(self, "Erreur navigation", f"Exception lors du retour au menu : {e}")
            NotificationPopup(f"Erreur navigation : {e}", 2500, self).show()
    def start_game(self) -> None:
        log_debug("[DEBUG] start_game appelé")
        self.loading_popup = LoadingPopup("Préparation du combat...", self)
        self.loading_popup.show()
        try:
            idx = self.deck_combo.currentIndex()
            decks = data_manager.get_decks()
            base_cards = get_base_set()
            def card_from_name(name):
                return next((c for c in base_cards if c.name == name), None)
            if 0 <= idx < len(decks):
                deck = decks[idx]
                # Création du joueur humain
                hero = Hero.from_dict(deck["hero"]) if deck.get("hero") else None
                player_deck = [card_from_name(n) for n in deck["cards"] if card_from_name(n)]
                player = Player(self.parent().parent().player_name, deck=player_deck, hero=hero)
                player.board = [card_from_name(n) for n in deck.get("units", []) if card_from_name(n)]
                ai_decks = [d for d in decks if d.get("hero")]
                if not ai_decks:
                    log_debug("[ERROR] Aucun deck IA valide n'est disponible.")
                    QMessageBox.warning(self, "Erreur", "Aucun deck IA valide n'est disponible. Créez au moins un deck avec un héros.")
                    NotificationPopup("Erreur : aucun deck IA valide.", 2500, self).show()
                    return
                ai_deck_data = random.choice(ai_decks)
                ai_hero = Hero.from_dict(ai_deck_data["hero"])
                ai_deck = [card_from_name(n) for n in ai_deck_data["cards"] if card_from_name(n)]
                ai = AIPlayer("IA", deck=ai_deck, hero=ai_hero)
                ai.board = [card_from_name(n) for n in ai_deck_data.get("units", []) if card_from_name(n)]
                battle = Battle(player, ai)
                combat_screen = CombatScreen(player, ai, battle, parent=self.parent().parent())
                self.loading_popup.close()
                self.parent().parent().stack.addWidget(combat_screen)
                self.parent().parent().stack.setCurrentWidget(combat_screen)
                self.refresh_history()
                NotificationPopup("Combat lancé !", 2000, self).show()
            else:
                log_debug("[ERROR] Aucun deck sélectionné.")
                QMessageBox.warning(self, "Erreur", "Aucun deck sélectionné.")
                NotificationPopup("Erreur : aucun deck sélectionné.", 2500, self).show()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans start_game : {e}")
            QMessageBox.critical(self, "Erreur critique", f"Exception lors du lancement de la partie : {e}")
            NotificationPopup(f"Erreur critique : {e}", 3000, self).show()
        finally:
            self.loading_popup.close()
    def refresh_history(self):
        self.loading_popup = LoadingPopup("Chargement de l'historique...", self)
        self.loading_popup.show()
        try:
            history = data_manager.get_game_history()
            self.history_table.setRowCount(len(history))
            for i, entry in enumerate(reversed(history)):
                self.history_table.setItem(i, 0, QTableWidgetItem(entry.get('date', '')))
                deck_str = ', '.join([c.name if hasattr(c, 'name') else str(c) for c in entry.get('deck', [])])
                self.history_table.setItem(i, 1, QTableWidgetItem(deck_str))
                self.history_table.setItem(i, 2, QTableWidgetItem(entry.get('resultat', '')))
                self.history_table.setItem(i, 3, QTableWidgetItem(str(entry.get('tours', ''))))
                self.history_table.setItem(i, 4, QTableWidgetItem(str(entry.get('recompense', ''))))
        finally:
            self.loading_popup.close()
    def reset_history(self):
        reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment effacer l'historique des parties ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                path = os.path.join(os.path.dirname(__file__), '../../game_history.json')
                if os.path.exists(path):
                    os.remove(path)
                self.refresh_history()
                log_debug("[DEBUG] Historique effacé.")
                NotificationPopup("Historique effacé !", 2000, self).show()
            except Exception as e:
                log_debug(f"[ERROR] Exception dans reset_history : {e}")
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la suppression de l'historique : {e}")
                NotificationPopup(f"Erreur suppression historique : {e}", 2500, self).show()
    def set_daltonian_mode(self, daltonian: bool):
        # À compléter : appliquer le mode daltonien aux widgets si besoin
        pass
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.return_to_main()
            event.accept()
            return
        elif event.key() == Qt.Key_F1:
            html_content = """
            <b>Raccourcis clavier :</b><br>
            <ul>
            <li><b>Échap</b> : Retour au menu principal</li>
            <li><b>F1</b> : Afficher cette aide</li>
            <li><b>Tab</b> : Naviguer entre les éléments</li>
            </ul>
            <b>Conseils :</b><br>
            - Sélectionnez un deck pour jouer.<br>
            - Consultez l'historique de vos parties.<br>
            - Utilisez les boutons pour lancer une partie solo.<br>
            """
            dlg = HelpDialog('Aide - Menu Jouer', html_content, self)
            dlg.exec_()
            event.accept()
            return
        super().keyPressEvent(event) 