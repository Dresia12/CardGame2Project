from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox, QListWidgetItem, QLineEdit, QHBoxLayout, QComboBox, QDialog
from CardGame2.data_manager import DataManager
from CardGame2.sets.base_set import get_base_set
from CardGame2.sets.elemental_set import get_elemental_set
from PyQt5.QtGui import QColor, QBrush, QKeyEvent, QKeySequence
from typing import Optional
from CardGame2.ui.components import StyledButton, StatsPanel, CardWidget, LoadingPopup, HelpDialog, NotificationPopup
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtCore import Qt
from CardGame2.ui.resources import UI_TEXTS
import os
from CardGame2.models.types import Element
from CardGame2.models.hero import Hero
from CardGame2.ui.utils import safe_add_widget, safe_clear_layout, is_layout_valid, is_widget_valid  # type: ignore

data_manager = DataManager()

def log_debug(msg):
    with open(os.path.join(os.path.dirname(__file__), '../../debug_cardgame2.log'), 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

class CollectionMenu(QWidget):
    def __init__(self, player_name: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        self.label = QLabel("Collection de cartes :")
        self.label.setToolTip(UI_TEXTS['collection_label'])
        # Barre de recherche, tri et filtre élémentaire
        search_sort_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher une carte...")
        self.search_bar.textChanged.connect(self.refresh_collection)
        self.search_bar.setToolTip(UI_TEXTS['search_bar'])
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Nom", "Rareté", "Coût"])
        self.sort_combo.currentIndexChanged.connect(self.refresh_collection)
        self.sort_combo.setToolTip(UI_TEXTS['sort_combo'])
        self.element_filter = QComboBox()
        self.element_filter.addItem("Tous les éléments")
        for e in Element:
            self.element_filter.addItem(e.name.title())
        self.element_filter.currentIndexChanged.connect(self.refresh_collection)
        self.owned_filter = QComboBox()
        self.owned_filter.addItems(["Toutes les cartes", "Cartes possédées", "Cartes non possédées"])
        self.owned_filter.currentIndexChanged.connect(self.refresh_collection)
        self.owned_filter.setToolTip("Filtrer par possession")
        self.sort_all_button = StyledButton("Tout trier")
        self.sort_all_button.setToolTip(UI_TEXTS['sort_all_button'])
        self.sort_all_button.clicked.connect(self.show_sort_menu)
        search_sort_layout.addWidget(self.search_bar)
        search_sort_layout.addWidget(self.sort_combo)
        search_sort_layout.addWidget(self.element_filter)
        search_sort_layout.addWidget(self.owned_filter)
        search_sort_layout.addWidget(self.sort_all_button)
        self.cards_list = QListWidget()
        self.cards_list.setToolTip(UI_TEXTS['cards_list'])
        self.back_button = StyledButton("Retour")
        self.back_button.setToolTip(UI_TEXTS['collection_back_button'])
        self.stats_panel = StatsPanel("Détails de la carte", {"-": "-"})
        self.stats_panel.setToolTip(UI_TEXTS['collection_stats_panel'])
        self.card_widget = CardWidget("-", "-", "-", 0)
        self.card_widget.setToolTip(UI_TEXTS['collection_card_widget'])
        self.heroes_label = QLabel("Héros possédés :")
        self.heroes_list = QListWidget()
        self.heroes_list.setToolTip("Liste des héros possédés.")
        layout.addWidget(self.label)
        layout.addLayout(search_sort_layout)
        layout.addWidget(self.cards_list)
        layout.addWidget(self.heroes_label)
        layout.addWidget(self.heroes_list)
        layout.addWidget(self.stats_panel)
        layout.addWidget(self.card_widget)
        layout.addWidget(self.back_button)
        self.setLayout(layout)
        self.back_button.clicked.connect(self.return_to_main)
        self.cards_list.currentRowChanged.connect(self.update_stats_panel)
        self.base_cards = get_base_set() + get_elemental_set()
        self.heroes = [c for c in self.base_cards if isinstance(c, Hero)]
        self.refresh_collection()
        self.setTabOrder(self.search_bar, self.sort_combo)
        self.setTabOrder(self.sort_combo, self.element_filter)
        self.setTabOrder(self.element_filter, self.owned_filter)
        self.setTabOrder(self.owned_filter, self.sort_all_button)
        self.setTabOrder(self.sort_all_button, self.cards_list)
        self.setTabOrder(self.cards_list, self.heroes_label)
        self.setTabOrder(self.heroes_label, self.heroes_list)
        self.setTabOrder(self.heroes_list, self.back_button)
        self.search_bar.setFocus()
    def refresh_collection(self) -> None:
        log_debug("[DEBUG] refresh_collection appelée")
        self.loading_popup = LoadingPopup("Chargement de la collection...", self)
        self.loading_popup.show()
        try:
            self.cards_list.clear()
            self.heroes_list.clear()
            collection = data_manager.get_collection()
            hero_collection = data_manager.get_hero_collection()
            query = self.search_bar.text().lower() if hasattr(self, 'search_bar') else ''
            cards = [c for c in self.base_cards if not isinstance(c, Hero)]
            selected_element = self.element_filter.currentText() if hasattr(self, 'element_filter') else "Tous les éléments"
            # Filtre de possession
            owned_mode = self.owned_filter.currentText() if hasattr(self, 'owned_filter') else "Toutes les cartes"
            if owned_mode == "Cartes possédées":
                cards = [c for c in cards if collection.get(c.name, 0) > 0]
            elif owned_mode == "Cartes non possédées":
                cards = [c for c in cards if collection.get(c.name, 0) == 0]
            if query:
                cards = [c for c in cards if query in c.name.lower()]
            if selected_element != "Tous les éléments":
                cards = [c for c in cards if hasattr(c, 'element') and c.element and c.element.name.title() == selected_element]
            if hasattr(self, 'sort_combo'):
                sort_mode = self.sort_combo.currentText()
                if sort_mode == "Nom":
                    cards = sorted(cards, key=lambda c: c.name)
                elif sort_mode == "Rareté":
                    cards = sorted(cards, key=lambda c: c.rarity.value)
                elif sort_mode == "Coût":
                    cards = sorted(cards, key=lambda c: getattr(c, 'cost', 0))
            for c in cards:
                count = collection.get(c.name, 0)
                item = QListWidgetItem(f"{c.name} ({c.rarity.name})  x{count}")
                if count == 0:
                    item.setForeground(QBrush(QColor('gray')))
                self.cards_list.addItem(item)
            # Affichage des héros possédés
            for h in self.heroes:
                owned = h.name in hero_collection
                item = QListWidgetItem(f"{h.name} (HÉROS){' ✔' if owned else ''}")
                if not owned:
                    item.setForeground(QBrush(QColor('gray')))
                self.heroes_list.addItem(item)
            self.update_stats_panel()
            NotificationPopup("Collection mise à jour !", 1200, self).show()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans refresh_collection : {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la mise à jour de la collection : {e}")
            NotificationPopup(f"Erreur maj collection : {e}", 2500, self).show()
        finally:
            self.loading_popup.close()
    def update_stats_panel(self) -> None:
        idx = self.cards_list.currentRow()
        if 0 <= idx < len(self.base_cards):
            card = self.base_cards[idx]
            stats = self.card_stats(card)
            self.stats_panel.set_stats(stats)
            # CardWidget
            self.card_widget.setParent(None)
            self.card_widget = CardWidget(card.name, card.card_type.name, card.rarity.name, getattr(card, 'cost', 0), getattr(card, 'attack', None), getattr(card, 'health', None), getattr(card, 'description', ''))
            self.layout().insertWidget(3, self.card_widget)
            # Animation d'apparition
            self.card_widget.setWindowOpacity(0.0)
            anim = QPropertyAnimation(self.card_widget, b"windowOpacity")
            anim.setDuration(300)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start()
            self._last_anim = anim
        else:
            self.stats_panel.set_stats({"-": "-"})
            self.card_widget.setParent(None)
            self.card_widget = CardWidget("-", "-", "-", 0)
            self.layout().insertWidget(3, self.card_widget)
    def card_stats(self, card) -> dict:
        d = {"Nom": card.name, "Type": card.card_type.name, "Rareté": card.rarity.name, "Coût": getattr(card, 'cost', '-')}
        if hasattr(card, 'attack') and hasattr(card, 'health'):
            d["ATK"] = getattr(card, 'attack', '-')
            d["PV"] = getattr(card, 'health', '-')
        if hasattr(card, 'description') and card.description:
            d["Description"] = card.description
        return d
    def return_to_main(self) -> None:
        log_debug("[DEBUG] Retour au menu principal depuis CollectionMenu")
        try:
            self.parent().parent().go_to_menu(self.parent().parent().player_name)
            NotificationPopup("Retour au menu principal", 1500, self).show()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans return_to_main : {e}")
            QMessageBox.critical(self, "Erreur navigation", f"Exception lors du retour au menu : {e}")
            NotificationPopup(f"Erreur navigation : {e}", 2500, self).show()
    def set_daltonian_mode(self, daltonian: bool):
        if hasattr(self, 'card_widget') and self.card_widget:
            self.card_widget.set_aura(True, daltonian_mode=daltonian)
    def show_sort_menu(self):
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        menu.addAction("Nom", lambda: self.sort_collection("Nom"))
        menu.addAction("Rareté", lambda: self.sort_collection("Rareté"))
        menu.addAction("Coût", lambda: self.sort_collection("Coût"))
        menu.addAction("Nombre possédé", lambda: self.sort_collection("Possédé"))
        menu.exec_(self.sort_all_button.mapToGlobal(self.sort_all_button.rect().bottomLeft()))
    def sort_collection(self, mode):
        log_debug(f"[DEBUG] sort_collection appelé avec mode={mode}")
        self.loading_popup = LoadingPopup("Tri de la collection...", self)
        self.loading_popup.show()
        try:
            self.sort_combo.setCurrentIndex({"Nom": 0, "Rareté": 1, "Coût": 2}.get(mode, 0))
            if mode == "Possédé":
                collection = data_manager.get_collection()
                cards = self.base_cards
                cards = sorted(cards, key=lambda c: -collection.get(c.name, 0))
                self.cards_list.clear()
                for c in cards:
                    count = collection.get(c.name, 0)
                    item = QListWidgetItem(f"{c.name} ({c.rarity.name})  x{count}")
                    if count == 0:
                        item.setForeground(QBrush(QColor('gray')))
                    self.cards_list.addItem(item)
                self.update_stats_panel()
            NotificationPopup("Tri effectué !", 1200, self).show()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans sort_collection : {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du tri de la collection : {e}")
            NotificationPopup(f"Erreur tri collection : {e}", 2500, self).show()
        finally:
            self.loading_popup.close()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            # Ouvre le menu d'options
            if hasattr(self.window(), 'show_options_menu'):
                self.window().show_options_menu()
            event.accept()
            return
        elif event.key() == Qt.Key_Delete:
            self.return_to_main()
            event.accept()
            return
        elif event.key() == Qt.Key_F1:
            html_content = """
            <b>Raccourcis clavier :</b><br>
            <ul>
            <li><b>Suppr</b> : Retour au menu principal</li>
            <li><b>Échap</b> : Menu d'options</li>
            <li><b>F1</b> : Afficher cette aide</li>
            <li><b>Tab</b> : Naviguer entre les éléments</li>
            </ul>
            <b>Conseils :</b><br>
            - Utilisez la barre de recherche pour filtrer les cartes.<br>
            - Utilisez les tris pour organiser votre collection.<br>
            - Cliquez sur une carte pour voir ses détails.<br>
            """
            dlg = HelpDialog('Aide - Collection', html_content, self)
            dlg.exec_()
            event.accept()
            return
        super().keyPressEvent(event) 