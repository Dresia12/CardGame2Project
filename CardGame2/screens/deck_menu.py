import os

def log_debug(msg):
    with open(os.path.join(os.path.dirname(__file__), '../../debug_cardgame2.log'), 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QComboBox, QSpinBox, QDialog,
    QFormLayout, QCheckBox, QDialogButtonBox, QMessageBox, QHBoxLayout, QTabWidget
)
from PyQt5.QtCore import QPropertyAnimation, Qt, QEvent
from PyQt5.QtGui import QKeyEvent, QKeySequence
from typing import Optional
from CardGame2.data_manager import DataManager
from CardGame2.sets.base_set import get_base_set
from CardGame2.sets.elemental_set import get_elemental_set
from CardGame2.models.hero import Hero, HeroCustomization, HeroPassive
from CardGame2.models.types import CardType, Rarity, Element
from CardGame2.ui.components import (
    StatsPanel, StyledButton, CardWidget, DeckPreviewPanel, LoadingPopup, HelpDialog, make_styled_button, NotificationPopup
)
from CardGame2.ui.style_constants import (
    PLAY_BTN_STYLE, BACK_BTN_STYLE, DUPLICATE_BTN_STYLE, SAVE_BTN_STYLE, SUMMARY_LABEL_STYLE, TAB_STYLESHEET, LIST_STYLESHEET, PREVIEW_STYLESHEET
)
from CardGame2.utils.hero_factory import create_default_hero
from CardGame2.ui.utils import safe_add_widget, safe_clear_layout, is_layout_valid, is_widget_valid  # type: ignore

data_manager = DataManager()

# Inclure ici la classe HeroCustomizationDialog si elle n'est pas utilisée ailleurs
class HeroCustomizationDialog(QDialog):
    def __init__(self, hero: Hero, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Personnalisation de {hero.name}")
        self.hero = hero
        self.customization = HeroCustomization()
        if hero.customization:
            self.customization.hp_level = hero.customization.hp_level
            self.customization.attack_level = hero.customization.attack_level
            self.customization.defense_level = hero.customization.defense_level
            self.customization.passives = list(hero.customization.passives)
            self.customization.total_cost = hero.customization.total_cost
        layout = QFormLayout()
        self.hp_spin = QSpinBox()
        self.hp_spin.setRange(0, 3)
        self.hp_spin.setValue(self.customization.hp_level)
        self.hp_spin.valueChanged.connect(self.update_cost)
        layout.addRow("Niveau PV (+5/PV)", self.hp_spin)
        self.atk_spin = QSpinBox()
        self.atk_spin.setRange(0, 3)
        self.atk_spin.setValue(self.customization.attack_level)
        self.atk_spin.valueChanged.connect(self.update_cost)
        layout.addRow("Niveau ATK (+2/ATK)", self.atk_spin)
        self.def_spin = QSpinBox()
        self.def_spin.setRange(0, 3)
        self.def_spin.setValue(self.customization.defense_level)
        self.def_spin.valueChanged.connect(self.update_cost)
        layout.addRow("Niveau DEF (+2/DEF)", self.def_spin)
        self.passive_checks = []
        passive_layout = QHBoxLayout()
        for p in HeroPassive:
            cb = QCheckBox(p.value)
            cb.setChecked(p in self.customization.passives)
            cb.stateChanged.connect(self.update_cost)
            passive_layout.addWidget(cb)
            self.passive_checks.append((p, cb))
        layout.addRow("Passifs (3 pts chacun)", passive_layout)
        self.cost_label = QLabel("")
        layout.addRow("Coût total", self.cost_label)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
        self.setLayout(layout)
        self.update_cost()
    def update_cost(self) -> None:
        self.customization.hp_level = self.hp_spin.value()
        self.customization.attack_level = self.atk_spin.value()
        self.customization.defense_level = self.def_spin.value()
        self.customization.passives = [p for p, cb in self.passive_checks if cb.isChecked()]
        total = 0
        total += sum([self.hp_spin.value(), self.atk_spin.value(), self.def_spin.value()])
        total += 3 * len(self.customization.passives)
        self.customization.total_cost = total
        self.cost_label.setText(f"{total} / 15")
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(total <= 15)
    def get_customization(self) -> HeroCustomization:
        return self.customization

class DeckMenu(QWidget):
    def __init__(self, player_name: str, parent: Optional[QWidget] = None) -> None:
        log_debug(f"[DEBUG] DeckMenu.__init__ tout début pour {player_name}, parent={parent}")
        # Nettoyage automatique des collections/décks/héros
        data_manager.clean_collections()
        super().__init__(parent)
        self.deck_preview_panel = None  # Correction : initialisation explicite
        self.base_cards = get_base_set() + get_elemental_set()
        self.player_name = player_name
        self.decks = data_manager.get_decks()
        self.selected_hero = None
        self.selected_units = []
        self.selected_cards = []
        self.current_deck_idx = None
        self.loading_popup = None
        self._init_ui()
        DeckMenu.ensure_ai_deck_exists()
        log_debug(f"[DEBUG] DeckMenu.__init__ fin pour {player_name}, self={self}, parent={self.parent()}")

    def _init_ui(self):
        log_debug(f"[DEBUG] DeckMenu._init_ui appelée pour {self.player_name}, self={self}")
        main_layout = QHBoxLayout()
        self.deck_selector = QComboBox()
        self.deck_selector.addItems([f"Deck {i+1}" for i in range(5)])
        self.deck_selector.currentIndexChanged.connect(self.change_deck_slot)
        self.deck_selector.setToolTip("Sélectionnez le slot de deck à éditer")
        main_layout.insertWidget(0, self.deck_selector)
        self.current_deck_idx = 0
        self.tabs = QTabWidget()
        self._build_hero_tab()
        self._build_unit_tab()
        self._build_card_tab()
        self.tabs.setStyleSheet(TAB_STYLESHEET)
        self.tabs.setToolTip("Naviguez entre les onglets Héros, Unités et Cartes")
        self.deck_list = QListWidget()
        self.deck_list.setFixedWidth(200)
        self.deck_list.setStyleSheet(LIST_STYLESHEET)
        self.deck_list.itemEntered.connect(self.show_deck_card_preview)
        self.deck_list.setMouseTracking(True)
        self.deck_list.setToolTip("Liste des cartes actuellement dans le deck. Cliquez pour retirer.")
        self.deck_card_preview = CardWidget("-", "-", "-", 0)
        self.deck_card_preview.setStyleSheet(PREVIEW_STYLESHEET)
        self.deck_card_preview.setVisible(False)
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Deck actuel :"))
        right_layout.addWidget(self.deck_list)
        right_layout.addWidget(self.deck_card_preview)
        self.duplicate_button = make_styled_button(
            "Dupliquer ce deck", DUPLICATE_BTN_STYLE, "Duplique le deck actuel dans un autre slot", self.duplicate_deck
        )
        self.save_button = make_styled_button(
            "Valider le deck", SAVE_BTN_STYLE, "Valide et sauvegarde la composition du deck", self.save_deck
        )
        self.deck_summary_label = QLabel()
        self.deck_summary_label.setStyleSheet(SUMMARY_LABEL_STYLE)
        right_layout.addWidget(self.deck_summary_label)
        right_layout.addWidget(self.save_button)
        self.back_button = make_styled_button(
            "Retour", BACK_BTN_STYLE, "Retour au menu principal", self.return_to_main
        )
        right_layout.addWidget(self.back_button)
        main_layout.addWidget(self.tabs)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)
        self.refresh_deck_list()
        self.deck_list.itemClicked.connect(self.remove_card_from_deck)
        self.installEventFilter(self)
        self.load_deck_to_ui()
        self.setTabOrder(self.deck_selector, self.tabs)
        self.setTabOrder(self.tabs, self.deck_list)
        self.setTabOrder(self.deck_list, self.duplicate_button)
        self.setTabOrder(self.duplicate_button, self.save_button)
        self.setTabOrder(self.save_button, self.back_button)
        self.deck_selector.setFocus()

    def _build_hero_tab(self):
        self.hero_tab = QWidget()
        hero_layout = QHBoxLayout()
        hero_label = QLabel("<b>Sélectionnez votre héros :</b>")
        hero_label.setStyleSheet("color: #ffae00; font-size: 16px;")
        self.hero_list = QListWidget()
        self.hero_list.setStyleSheet("background: #181a20; color: #f8f8f2; font-size: 15px;")
        for h in self.get_heroes_base():
            item = QListWidgetItem(h.name)
            self.hero_list.addItem(item)
        self.hero_list.currentRowChanged.connect(self.update_hero_preview)
        self.choose_hero_button = StyledButton("Choisir ce héros")
        self.choose_hero_button.setStyleSheet("background: #3a7afe; color: #fff; font-weight: bold;")
        self.remove_hero_button = StyledButton("Retirer le héros")
        self.remove_hero_button.setStyleSheet("background: #e74c3c; color: #fff; font-weight: bold;")
        self.choose_hero_button.clicked.connect(self.choose_hero)
        self.remove_hero_button.clicked.connect(self.remove_hero)
        self.hero_preview = CardWidget("-", "HÉROS", "-", 0)
        self.hero_preview.setToolTip("Aperçu du héros sélectionné")
        hero_layout.addWidget(hero_label)
        hero_layout.addWidget(self.hero_list)
        hero_layout.addWidget(self.hero_preview)
        hero_layout.addWidget(self.choose_hero_button)
        hero_layout.addWidget(self.remove_hero_button)
        self.hero_tab.setLayout(hero_layout)
        self.hero_list.setToolTip("Liste des héros disponibles. Sélectionnez-en un pour l'ajouter au deck.")
        self.choose_hero_button.setToolTip("Ajoute le héros sélectionné au deck")
        self.remove_hero_button.setToolTip("Retire le héros du deck")
        self.tabs.addTab(self.hero_tab, "Héros")

    def _build_unit_tab(self):
        self.unit_tab = QWidget()
        self.unit_layout = QHBoxLayout()  # Correction : attribut de classe
        unit_label = QLabel("<b>Unités disponibles (4 max, 2x max par unité) :</b>")
        unit_label.setStyleSheet("color: #ffae00; font-size: 16px;")
        self.unit_element_filter = QComboBox()
        self.unit_element_filter.addItem("Tous les éléments")
        for e in Element:
            self.unit_element_filter.addItem(e.name.title())
        self.unit_element_filter.currentIndexChanged.connect(self.refresh_unit_list)
        self.unit_list = QListWidget()
        self.unit_list.setStyleSheet("background: #181a20; color: #f8f8f2; font-size: 15px;")
        self.unit_list.setDragEnabled(True)
        self.unit_list.setSelectionMode(QListWidget.SingleSelection)
        self.unit_list.itemDoubleClicked.connect(self.add_unit)
        self.unit_list.viewport().setAcceptDrops(False)
        self.deck_units_list = QListWidget()
        self.deck_units_list.setStyleSheet("background: #181a20; color: #f8f8f2; font-size: 15px;")
        self.deck_units_list.setAcceptDrops(True)
        self.deck_units_list.setDragDropMode(QListWidget.DropOnly)
        self.deck_units_list.setDefaultDropAction(Qt.MoveAction)
        self.deck_units_list.itemDoubleClicked.connect(self.remove_unit)
        self.deck_units_list.setToolTip("Unités actuellement dans le deck. Double-cliquez pour retirer.")
        self.unit_preview = CardWidget("-", "UNITÉ", "-", 0)
        self.unit_preview.setToolTip("Aperçu de l'unité sélectionnée")
        self.add_unit_button = StyledButton("Ajouter unité")
        self.add_unit_button.setStyleSheet("background: #3a7afe; color: #fff; font-weight: bold;")
        self.add_unit_button.setToolTip("Ajoute l'unité sélectionnée au deck")
        self.remove_unit_button = StyledButton("Retirer unité")
        self.remove_unit_button.setStyleSheet("background: #e74c3c; color: #fff; font-weight: bold;")
        self.remove_unit_button.setToolTip("Retire l'unité sélectionnée du deck")
        self.add_unit_button.clicked.connect(self.add_unit)
        self.remove_unit_button.clicked.connect(self.remove_unit)
        self.add_all_units_button = StyledButton("Tout ajouter (unités)")
        self.add_all_units_button.setToolTip("Ajoute toutes les unités possibles au deck (dans la limite autorisée)")
        self.add_all_units_button.clicked.connect(self.add_all_units)
        self.remove_all_units_button = StyledButton("Tout retirer (unités)")
        self.remove_all_units_button.setToolTip("Retire toutes les unités du deck")
        self.remove_all_units_button.clicked.connect(self.remove_all_units)
        self.unit_layout.addWidget(unit_label)
        self.unit_layout.addWidget(self.unit_element_filter)
        self.unit_layout.addWidget(self.unit_list)
        self.unit_layout.addWidget(self.unit_preview)
        self.unit_layout.addWidget(self.deck_units_list)
        self.unit_layout.addWidget(self.add_unit_button)
        self.unit_layout.addWidget(self.remove_unit_button)
        self.unit_layout.addWidget(self.add_all_units_button)
        self.unit_layout.addWidget(self.remove_all_units_button)
        self.unit_tab.setLayout(self.unit_layout)
        self.unit_list.setToolTip("Liste des unités disponibles. Double-cliquez ou faites glisser pour ajouter.")
        self.unit_preview.setToolTip("Aperçu de l'unité sélectionnée")
        self.tabs.addTab(self.unit_tab, "Unités")
        self.refresh_unit_list()

    def _build_card_tab(self):
        self.card_tab = QWidget()
        card_layout = QHBoxLayout()
        card_label = QLabel("<b>Cartes du deck (sorts, équipements, etc.) :</b>")
        card_label.setStyleSheet("color: #ffae00; font-size: 16px;")
        self.card_element_filter = QComboBox()
        self.card_element_filter.addItem("Tous les éléments")
        for e in Element:
            self.card_element_filter.addItem(e.name.title())
        self.card_element_filter.currentIndexChanged.connect(self.refresh_card_list)
        self.card_list = QListWidget()
        self.card_list.setStyleSheet("background: #181a20; color: #f8f8f2; font-size: 15px;")
        self.card_list.setSelectionMode(QListWidget.SingleSelection)
        self.card_list.currentRowChanged.connect(self.update_card_preview)
        self.add_card_button = StyledButton("Ajouter carte")
        self.add_card_button.setStyleSheet("background: #3a7afe; color: #fff; font-weight: bold;")
        self.remove_card_button = StyledButton("Retirer carte")
        self.remove_card_button.setStyleSheet("background: #e74c3c; color: #fff; font-weight: bold;")
        self.add_card_button.clicked.connect(self.add_card)
        self.remove_card_button.clicked.connect(self.remove_card)
        self.add_all_cards_button = StyledButton("Tout ajouter (cartes)")
        self.add_all_cards_button.setToolTip("Ajoute jusqu'à 20 cartes (2x max par carte)")
        self.add_all_cards_button.clicked.connect(self.add_all_cards)
        self.remove_all_cards_button = StyledButton("Tout retirer (cartes)")
        self.remove_all_cards_button.setToolTip("Retire toutes les cartes du deck")
        self.remove_all_cards_button.clicked.connect(self.remove_all_cards)
        self.card_preview = CardWidget("-", "-", "-", 0)
        card_layout.addWidget(card_label)
        card_layout.addWidget(self.card_element_filter)
        card_layout.addWidget(self.card_list)
        card_layout.addWidget(self.card_preview)
        card_layout.addWidget(self.add_card_button)
        card_layout.addWidget(self.remove_card_button)
        card_layout.addWidget(self.add_all_cards_button)
        card_layout.addWidget(self.remove_all_cards_button)
        self.card_tab.setLayout(card_layout)
        self.card_list.setToolTip("Liste des cartes actuellement dans le deck. Cliquez pour retirer.")
        self.tabs.addTab(self.card_tab, "Cartes")
        self.refresh_card_list()

    def get_heroes_base(self):
        # Retourne uniquement les héros possédés par le joueur
        base_heroes = [c for c in get_base_set() + get_elemental_set() if hasattr(c, 'card_type') and getattr(c, 'card_type', None) == CardType.HERO]
        hero_collection = data_manager.get_hero_collection()
        return [h for h in base_heroes if h.name in hero_collection]
    def update_hero_preview(self, idx):
        heroes = self.get_heroes_base()
        if 0 <= idx < len(heroes):
            h = heroes[idx]
            if self.hero_preview is not None and self.hero_preview.parent() is not None:
                self.hero_preview.setParent(None)
            self.hero_preview = CardWidget(h.name, "HÉROS", "-", 0, h.base_attack, h.base_hp, f"DEF: {h.base_defense}")
            layout = self.hero_tab.layout()
            if hasattr(layout, 'insertWidget'):
                layout.insertWidget(2, self.hero_preview)
    def choose_hero(self):
        log_debug(f"[DEBUG] DeckMenu.choose_hero appelée pour {self.player_name}")
        idx = self.hero_list.currentRow()
        heroes = self.get_heroes_base()
        if 0 <= idx < len(heroes):
            hero = heroes[idx]
            # Ouvre la personnalisation
            dlg = HeroCustomizationDialog(hero, self)
            if dlg.exec_() == QDialog.Accepted:
                hero.customization = dlg.get_customization()
                hero.apply_customization()
                self.selected_hero = hero
                log_debug(f"choose_hero : {self.selected_hero} (customisé)")
                self.refresh_deck_list()
            else:
                log_debug("Personnalisation du héros annulée")
    def remove_hero(self):
        log_debug(f"[DEBUG] DeckMenu.remove_hero appelée pour {self.player_name}")
        log_debug("remove_hero appelée")
        self.selected_hero = None
        self.refresh_deck_list()
    def update_unit_preview(self):
        idx = self.unit_list.currentRow()
        units = [c for c in self.base_cards if hasattr(c, "card_type") and c.card_type == CardType.UNIT and hasattr(c, "name") and hasattr(c, "rarity") and hasattr(c, "cost") and hasattr(c, "attack") and hasattr(c, "health")]
        if 0 <= idx < len(units):
            u = units[idx]
            if self.unit_preview is not None and self.unit_preview.parent() is not None:
                self.unit_preview.setParent(None)
            self.unit_preview = CardWidget(u.name, "UNITÉ", u.rarity.name, u.cost, u.attack, u.health, getattr(u, 'description', ''))
            layout = self.unit_tab.layout()
            if hasattr(layout, 'insertWidget'):
                layout.insertWidget(2, self.unit_preview)
    def _can_add_unit(self, name: str) -> bool:
        if len(self.selected_units) >= 4:
            return False
        if self.selected_units.count(name) >= 2:
            return False
        return True

    def _add_unit(self, name: str) -> bool:
        if self._can_add_unit(name):
            self.selected_units.append(name)
            return True
        return False

    def _remove_unit(self, name: str) -> bool:
        if name in self.selected_units:
            self.selected_units.remove(name)
            return True
        return False

    def add_unit(self, item=None):
        log_debug(f"[DEBUG] DeckMenu.add_unit appelée pour {self.player_name}")
        name = item.text() if item else self.unit_list.currentItem().text()
        log_debug(f"add_unit appelée pour {name}")
        count = sum(1 for i in range(self.deck_units_list.count()) if self.deck_units_list.item(i).text() == name)
        if self.deck_units_list.count() >= 4:
            self.deck_units_list.setStyleSheet(self.deck_units_list.styleSheet() + '\nborder: 2px solid #e74c3c;')
            anim = QPropertyAnimation(self.deck_units_list, b"pos")
            anim.setDuration(180)
            anim.setKeyValueAt(0, self.deck_units_list.pos())
            anim.setKeyValueAt(0.2, self.deck_units_list.pos() + Qt.QPoint(-10, 0))
            anim.setKeyValueAt(0.5, self.deck_units_list.pos() + Qt.QPoint(10, 0))
            anim.setKeyValueAt(0.8, self.deck_units_list.pos() + Qt.QPoint(-10, 0))
            anim.setKeyValueAt(1, self.deck_units_list.pos())
            anim.start()
            QMessageBox.warning(self, "Limite atteinte", "Vous ne pouvez avoir que 4 unités dans le deck.")
            return
        if count >= 2:
            anim = QPropertyAnimation(self.deck_units_list, b"pos")
            anim.setDuration(180)
            anim.setKeyValueAt(0, self.deck_units_list.pos())
            anim.setKeyValueAt(0.2, self.deck_units_list.pos() + Qt.QPoint(-10, 0))
            anim.setKeyValueAt(0.5, self.deck_units_list.pos() + Qt.QPoint(10, 0))
            anim.setKeyValueAt(0.8, self.deck_units_list.pos() + Qt.QPoint(-10, 0))
            anim.setKeyValueAt(1, self.deck_units_list.pos())
            anim.start()
            QMessageBox.warning(self, "Limite d'exemplaires", "Vous ne pouvez avoir que 2 exemplaires d'une même unité.")
            return
        self.deck_units_list.addItem(name)
        self.deck_units_list.setStyleSheet(self.deck_units_list.styleSheet().replace('border: 2px solid #e74c3c;', ''))
        self.update_deck_preview()
        # Tooltip sur chaque carte du deck indiquant le nombre d'exemplaires
        for i in range(self.deck_units_list.count()):
            item = self.deck_units_list.item(i)
            n = sum(1 for j in range(self.deck_units_list.count()) if self.deck_units_list.item(j).text() == item.text())
            item.setToolTip(f"{item.text()} : {n} exemplaire(s) dans le deck")
    def remove_unit(self, item=None):
        log_debug(f"[DEBUG] DeckMenu.remove_unit appelée pour {self.player_name}")
        log_debug("remove_unit appelée")
        if isinstance(item, QListWidgetItem):
            name = item.text().rsplit(' x', 1)[0]
        else:
            idx = self.deck_units_list.currentRow()
            if idx < 0:
                return
            name = self.deck_units_list.item(idx).text().rsplit(' x', 1)[0]
        if self._remove_unit(name):
            self.refresh_deck_units_list()
            self.refresh_deck_list()
    def update_card_preview(self, idx):
        cards = [c for c in self.base_cards if c.card_type not in (CardType.UNIT, CardType.HERO)]
        if 0 <= idx < len(cards):
            c = cards[idx]
            if self.card_preview is not None and self.card_preview.parent() is not None:
                self.card_preview.setParent(None)
            self.card_preview = CardWidget(c.name, c.card_type.name, c.rarity.name, c.cost, getattr(c, 'attack', None), getattr(c, 'health', None), getattr(c, 'description', ''))
            layout = self.card_tab.layout()
            if hasattr(layout, 'insertWidget'):
                layout.insertWidget(2, self.card_preview)
    def _can_add_card(self, name: str) -> bool:
        return self.selected_cards.count(name) < 3

    def _add_card(self, name: str) -> bool:
        if self._can_add_card(name):
            self.selected_cards.append(name)
            return True
        return False

    def add_card(self):
        log_debug(f"[DEBUG] DeckMenu.add_card appelée pour {self.player_name}")
        name = self.card_list.currentItem().text()
        log_debug(f"add_card appelée pour {name}")
        count = sum(1 for i in range(self.deck_list.count()) if self.deck_list.item(i).text().startswith(name))
        if self.deck_list.count() >= 20:
            self.deck_list.setStyleSheet(self.deck_list.styleSheet() + '\nborder: 2px solid #e74c3c;')
            anim = QPropertyAnimation(self.deck_list, b"pos")
            anim.setDuration(180)
            anim.setKeyValueAt(0, self.deck_list.pos())
            anim.setKeyValueAt(0.2, self.deck_list.pos() + Qt.QPoint(-10, 0))
            anim.setKeyValueAt(0.5, self.deck_list.pos() + Qt.QPoint(10, 0))
            anim.setKeyValueAt(0.8, self.deck_list.pos() + Qt.QPoint(-10, 0))
            anim.setKeyValueAt(1, self.deck_list.pos())
            anim.start()
            QMessageBox.warning(self, "Limite atteinte", "Vous ne pouvez avoir que 20 cartes dans le deck.")
            return
        if count >= 2:
            anim = QPropertyAnimation(self.deck_list, b"pos")
            anim.setDuration(180)
            anim.setKeyValueAt(0, self.deck_list.pos())
            anim.setKeyValueAt(0.2, self.deck_list.pos() + Qt.QPoint(-10, 0))
            anim.setKeyValueAt(0.5, self.deck_list.pos() + Qt.QPoint(10, 0))
            anim.setKeyValueAt(0.8, self.deck_list.pos() + Qt.QPoint(-10, 0))
            anim.setKeyValueAt(1, self.deck_list.pos())
            anim.start()
            QMessageBox.warning(self, "Limite d'exemplaires", "Vous ne pouvez avoir que 2 exemplaires d'une même carte.")
            return
        self.deck_list.addItem(name)
        self.deck_list.setStyleSheet(self.deck_list.styleSheet().replace('border: 2px solid #e74c3c;', ''))
        self.update_deck_preview()
        # Tooltip sur chaque carte du deck indiquant le nombre d'exemplaires
        for i in range(self.deck_list.count()):
            item = self.deck_list.item(i)
            n = sum(1 for j in range(self.deck_list.count()) if self.deck_list.item(j).text() == item.text())
            item.setToolTip(f"{item.text()} : {n} exemplaire(s) dans le deck")
    def _remove_card(self, name: str) -> bool:
        if name in self.selected_cards:
            self.selected_cards.remove(name)
            return True
        return False

    def remove_card(self):
        log_debug(f"[DEBUG] DeckMenu.remove_card appelée pour {self.player_name}")
        log_debug("remove_card appelée")
        idx = self.card_list.currentRow()
        cards = [c for c in self.base_cards if c.card_type not in (CardType.UNIT, CardType.HERO)]
        if 0 <= idx < len(cards):
            name = cards[idx].name
            if self._remove_card(name):
                self.refresh_deck_list()
    def refresh_deck_list(self):
        self.deck_list.clear()
        if self.selected_hero:
            self.deck_list.addItem(f"Héros : {self.selected_hero.name}")
        for u in self.selected_units:
            self.deck_list.addItem(f"Unité : {u}")
        for c in self.selected_cards:
            self.deck_list.addItem(f"Carte : {c}")
        # Affiche le résumé
        hero = self.selected_hero.name if self.selected_hero else "-"
        units = ', '.join(self.selected_units) if self.selected_units else "-"
        cards = ', '.join(self.selected_cards) if self.selected_cards else "-"
        self.deck_summary_label.setText(f"<b>Résumé du deck :</b><br>Héros : {hero}<br>Unités : {units}<br>Cartes : {cards}")
    def show_deck_card_preview(self, item):
        name = item.text().split(': ', 1)[-1]
        card = next((c for c in self.base_cards if c.name == name), None)
        if card:
            if self.deck_card_preview is not None and self.deck_card_preview.parent() is not None:
                self.deck_card_preview.setParent(None)
            self.deck_card_preview = CardWidget(card.name, getattr(card, 'card_type', '-'), getattr(card, 'rarity', '-'), getattr(card, 'cost', 0), getattr(card, 'attack', None), getattr(card, 'health', None), getattr(card, 'description', ''))
            right_layout = self.layout().itemAt(1)
            if right_layout is not None and hasattr(right_layout, 'addWidget'):
                right_layout.addWidget(self.deck_card_preview)
            self.deck_card_preview.setVisible(True)
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if self.deck_card_preview.isVisible():
                self.deck_card_preview.setVisible(False)
        return super().eventFilter(obj, event)
    def save_deck(self):
        log_debug(f"[DEBUG] save_deck appelé pour {self.player_name}")
        try:
            if not self.selected_hero:
                log_debug("save_deck : pas de héros sélectionné")
                QMessageBox.warning(self, "Erreur", "Vous devez choisir un héros.")
                return
            if len(self.selected_units) != 4:
                log_debug("save_deck : mauvais nombre d'unités")
                QMessageBox.warning(self, "Erreur", "Vous devez choisir 4 unités.")
                return
            if not self.selected_cards:
                log_debug("save_deck : aucune carte sélectionnée")
                QMessageBox.warning(self, "Erreur", "Vous devez ajouter au moins une carte.")
                return
            deck = {
                "hero": self.selected_hero.to_dict(),
                "units": self.selected_units,
                "cards": self.selected_cards.copy()
            }
            self.decks[self.current_deck_idx] = deck
            data_manager.set_deck(self.current_deck_idx, deck)
            log_debug(f"save_deck : deck sauvegardé {deck}")
            NotificationPopup("Deck sauvegardé !", 2000, self).show()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans save_deck : {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde du deck : {e}")
            NotificationPopup(f"Erreur sauvegarde deck : {e}", 2500, self).show()
    def update_deck_preview(self):
        # Met à jour l'aperçu du deck dans le conteneur dédié
        hero = self.selected_hero.to_dict() if self.selected_hero else None
        selected_units = self.selected_units.copy()
        deck = {
            "hero": hero,
            "units": selected_units,
            "cards": self.selected_cards.copy()
        }
        # Supprime l'ancien aperçu s'il existe
        if self.deck_preview_panel is not None:
            self.deck_preview_layout.removeWidget(self.deck_preview_panel)
            self.deck_preview_panel.deleteLater()
        self.deck_preview_panel = DeckPreviewPanel(deck, self.base_cards)
        self.deck_preview_layout.addWidget(self.deck_preview_panel)
    def return_to_main(self) -> None:
        log_debug(f"[DEBUG] Retour au menu principal depuis DeckMenu pour {self.player_name}")
        try:
            self.parent().parent().go_to_menu(self.player_name)
            NotificationPopup("Retour au menu principal", 1500, self).show()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans return_to_main : {e}")
            QMessageBox.critical(self, "Erreur navigation", f"Exception lors du retour au menu : {e}")
            NotificationPopup(f"Erreur navigation : {e}", 2500, self).show()
    def update_unit_stats_panel(self):
        idx = self.unit_list.currentRow()
        units = [c for c in self.base_cards if hasattr(c, "card_type") and c.card_type == CardType.UNIT and hasattr(c, "name") and hasattr(c, "rarity") and hasattr(c, "cost") and hasattr(c, "attack") and hasattr(c, "health")]
        if 0 <= idx < len(units):
            unit = units[idx]
            stats = {"Nom": unit.name, "ATK": unit.attack, "PV": unit.health, "Description": getattr(unit, 'description', '-')}
            self.unit_stats_panel.set_stats(stats)
        else:
            self.unit_stats_panel.set_stats({"-": "-"})
    def update_card_stats_panel(self):
        idx = self.card_list.currentRow()
        others = [c for c in self.base_cards if c.card_type not in (CardType.UNIT, CardType.HERO)]
        if 0 <= idx < len(others):
            card = others[idx]
            stats = {"Nom": card.name, "Type": card.card_type.name, "Rareté": card.rarity.name, "Coût": getattr(card, 'cost', '-')}
            if hasattr(card, 'description') and card.description:
                stats["Description"] = card.description
            self.card_stats_panel.set_stats(stats)
        else:
            self.card_stats_panel.set_stats({"-": "-"})
    def refresh_deck_units_list(self):
        self.deck_units_list.clear()
        # Affiche chaque unité avec son compteur
        for name in sorted(set(self.selected_units)):
            count = self.selected_units.count(name)
            self.deck_units_list.addItem(f"{name} x{count}")
    # Drag & drop support
    def dragEnterEvent(self, event):
        if event.source() == self.unit_list:
            event.acceptProposedAction()
    def dropEvent(self, event):
        if event.source() == self.unit_list:
            idx = self.unit_list.indexAt(event.pos()).row()
            if idx >= 0:
                name = self.unit_list.item(idx).text()
                self.add_unit(self.unit_list.item(idx))
            event.acceptProposedAction()
    def remove_card_from_deck(self, item):
        log_debug(f"[DEBUG] remove_card_from_deck appelé pour {self.player_name}")
        try:
            text = item.text()
            if text.startswith("Héros :"):
                self.selected_hero = None
            elif text.startswith("Unité :"):
                name = text.split(': ', 1)[-1]
                if name in self.selected_units:
                    self.selected_units.remove(name)
            elif text.startswith("Carte :"):
                name = text.split(': ', 1)[-1]
                if name in self.selected_cards:
                    self.selected_cards.remove(name)
            self.refresh_deck_list()
            NotificationPopup("Carte retirée du deck", 1200, self).show()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans remove_card_from_deck : {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du retrait de la carte : {e}")
            NotificationPopup(f"Erreur suppression carte : {e}", 2500, self).show()
    def change_deck_slot(self, idx):
        self.current_deck_idx = idx
        self.load_deck_to_ui()
    def load_deck_to_ui(self):
        self.loading_popup = LoadingPopup("Chargement du deck...", self)
        self.loading_popup.show()
        try:
            deck = self.decks[self.current_deck_idx]
            # Héros
            if deck.get("hero"):
                hero_name = deck["hero"]["name"]
                heroes = self.get_heroes_base()
                idx = [h.name for h in heroes].index(hero_name) if hero_name in [h.name for h in heroes] else 0
                self.hero_list.setCurrentRow(idx)
                self.selected_hero = heroes[idx]
            else:
                self.selected_hero = None
            # Unités
            self.selected_units = deck.get("units", []).copy()
            # Cartes
            self.selected_cards = deck.get("cards", []).copy()
            self.refresh_deck_list()
        finally:
            self.loading_popup.close()
    # Création d'un deck IA par défaut si aucun deck IA n'existe
    @staticmethod
    def ensure_ai_deck_exists():
        decks = data_manager.get_decks()
        has_ai = any(d.get("hero") for d in decks)
        if not has_ai:
            from CardGame2.models.hero import Hero
            from CardGame2.sets.base_set import get_base_set
            base_cards = get_base_set()
            hero = Hero("Arthos", 30, 5, 3)
            units = [c.name for c in base_cards if hasattr(c, 'card_type') and c.card_type.name == 'UNIT'][:4]
            cards = [c.name for c in base_cards if hasattr(c, 'card_type') and c.card_type.name not in ('UNIT', 'HERO')][:5]
            ai_deck = {"hero": hero.to_dict(), "units": units, "cards": cards}
            data_manager.set_deck(0, ai_deck)

    def duplicate_deck(self):
        log_debug(f"[DEBUG] duplicate_deck appelé pour {self.player_name}")
        try:
            idx = self.deck_selector.currentIndex()
            decks = data_manager.get_decks()
            if 0 <= idx < len(decks):
                # Cherche un slot libre
                for i, d in enumerate(decks):
                    if not d.get('hero') and not d.get('units') and not d.get('cards'):
                        decks[i] = {k: v for k, v in decks[idx].items()}
                        data_manager.save_decks(decks)
                        log_debug(f"duplicate_deck : deck copié dans le slot {i+1}")
                        QMessageBox.information(self, "Duplication", f"Deck copié dans le slot {i+1} !")
                        self.deck_selector.setCurrentIndex(i)
                        self.refresh_deck_list()
                        return
                log_debug("duplicate_deck : aucun slot libre")
                QMessageBox.warning(self, "Duplication", "Aucun slot libre pour dupliquer ce deck.")
            else:
                log_debug("duplicate_deck : aucun deck sélectionné")
                QMessageBox.warning(self, "Duplication", "Aucun deck sélectionné.")
            NotificationPopup("Deck dupliqué !", 2000, self).show()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans duplicate_deck : {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la duplication du deck : {e}")
            NotificationPopup(f"Erreur duplication deck : {e}", 2500, self).show()

    def set_daltonian_mode(self, daltonian: bool):
        if hasattr(self, 'hero_preview') and self.hero_preview:
            self.hero_preview.set_aura(True, daltonian_mode=daltonian)
        if hasattr(self, 'unit_preview') and self.unit_preview:
            self.unit_preview.set_aura(True, daltonian_mode=daltonian)
        if hasattr(self, 'card_preview') and self.card_preview:
            self.card_preview.set_aura(True, daltonian_mode=daltonian)

    def add_all_units(self):
        log_debug(f"[DEBUG] DeckMenu.add_all_units appelée pour {self.player_name}")
        log_debug("add_all_units appelée")
        units = [c for c in self.base_cards if hasattr(c, "card_type") and c.card_type == CardType.UNIT and hasattr(c, "name")]
        self.selected_units = []
        for u in units:
            if len(self.selected_units) < 4:
                self.selected_units.extend([u.name] * min(2, 4 - len(self.selected_units)))
        log_debug(f"add_all_units : {self.selected_units}")
        self.refresh_deck_list()
        self.refresh_deck_units_list()

    def remove_all_units(self):
        log_debug(f"[DEBUG] DeckMenu.remove_all_units appelée pour {self.player_name}")
        log_debug("remove_all_units appelée")
        self.selected_units = []
        self.refresh_deck_list()
        self.refresh_deck_units_list()

    def add_all_cards(self):
        log_debug(f"[DEBUG] DeckMenu.add_all_cards appelée pour {self.player_name}")
        log_debug("add_all_cards appelée")
        # Ajoute jusqu'à 20 cartes (2x max par carte différente)
        cards = [c for c in self.base_cards if hasattr(c, "card_type") and c.card_type not in (CardType.UNIT, CardType.HERO) and hasattr(c, "name")]
        self.selected_cards = []
        count = 0
        for c in cards:
            for _ in range(2):
                if count < 20:
                    self.selected_cards.append(c.name)
                    count += 1
        log_debug(f"add_all_cards : {self.selected_cards}")
        self.refresh_deck_list()

    def remove_all_cards(self):
        log_debug(f"[DEBUG] DeckMenu.remove_all_cards appelée pour {self.player_name}")
        log_debug("remove_all_cards appelée")
        self.selected_cards = []
        self.refresh_deck_list()

    def keyPressEvent(self, event):
        log_debug(f"[DEBUG] DeckMenu.keyPressEvent : key={event.key()} pour {self.player_name}")
        log_debug(f"keyPressEvent DeckMenu : key={event.key()}")
        if event.key() == Qt.Key_Escape:
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
            - Double-cliquez ou utilisez les boutons pour ajouter/retirer des cartes et unités.<br>
            - Utilisez les boutons 'Tout ajouter'/'Tout retirer' pour gérer rapidement votre deck.<br>
            - Les limites de deck sont indiquées dans les info-bulles.<br>
            """
            dlg = HelpDialog('Aide - Éditeur de deck', html_content, self)
            dlg.exec_()
            event.accept()
            return
        super().keyPressEvent(event)

    def showEvent(self, event):
        log_debug(f"[DEBUG] DeckMenu.showEvent pour {self.player_name}, self={self}, visible={self.isVisible()}")
        super().showEvent(event)

    def setVisible(self, visible):
        log_debug(f"[DEBUG] DeckMenu.setVisible({visible}) pour {self.player_name}, self={self}")
        super().setVisible(visible)

    def focusInEvent(self, event):
        log_debug(f"[DEBUG] DeckMenu.focusInEvent pour {self.player_name}, self={self}")
        super().focusInEvent(event)

    def refresh_unit_list(self):
        self.unit_list.clear()
        selected_element = self.unit_element_filter.currentText()
        for c in self.base_cards:
            if not hasattr(c, "name") or not hasattr(c, "card_type"):
                log_warn(f"[WARN] DeckMenu.refresh_unit_list: entrée non-carte détectée : {c} (type={type(c)})")
                continue
            if c.card_type == CardType.UNIT:
                if selected_element == "Tous les éléments" or (hasattr(c, 'element') and c.element and c.element.name.title() == selected_element):
                    item = QListWidgetItem(f"{c.name}")
                    self.unit_list.addItem(item)
        self.unit_list.setDragEnabled(True)
        self.unit_list.setSelectionMode(QListWidget.SingleSelection)
        self.unit_list.itemDoubleClicked.connect(self.add_unit)
        self.unit_list.viewport().setAcceptDrops(False)
        self.deck_units_list = QListWidget()
        self.deck_units_list.setStyleSheet("background: #181a20; color: #f8f8f2; font-size: 15px;")
        self.deck_units_list.setAcceptDrops(True)
        self.deck_units_list.setDragDropMode(QListWidget.DropOnly)
        self.deck_units_list.setDefaultDropAction(Qt.MoveAction)
        self.deck_units_list.itemDoubleClicked.connect(self.remove_unit)
        self.deck_units_list.setToolTip("Unités actuellement dans le deck. Double-cliquez pour retirer.")
        self.unit_preview = CardWidget("-", "UNITÉ", "-", 0)
        self.unit_preview.setToolTip("Aperçu de l'unité sélectionnée")
        self.add_unit_button = StyledButton("Ajouter unité")
        self.add_unit_button.setStyleSheet("background: #3a7afe; color: #fff; font-weight: bold;")
        self.add_unit_button.setToolTip("Ajoute l'unité sélectionnée au deck")
        self.remove_unit_button = StyledButton("Retirer unité")
        self.remove_unit_button.setStyleSheet("background: #e74c3c; color: #fff; font-weight: bold;")
        self.remove_unit_button.setToolTip("Retire l'unité sélectionnée du deck")
        self.add_unit_button.clicked.connect(self.add_unit)
        self.remove_unit_button.clicked.connect(self.remove_unit)
        self.add_all_units_button = StyledButton("Tout ajouter (unités)")
        self.add_all_units_button.setToolTip("Ajoute toutes les unités possibles au deck (dans la limite autorisée)")
        self.add_all_units_button.clicked.connect(self.add_all_units)
        self.remove_all_units_button = StyledButton("Tout retirer (unités)")
        self.remove_all_units_button.setToolTip("Retire toutes les unités du deck")
        self.remove_all_units_button.clicked.connect(self.remove_all_units)
        self.unit_layout.addWidget(self.deck_units_list)
        self.unit_layout.addWidget(self.add_unit_button)
        self.unit_layout.addWidget(self.remove_unit_button)
        self.unit_layout.addWidget(self.add_all_units_button)
        self.unit_layout.addWidget(self.remove_all_units_button)
        self.unit_tab.setLayout(self.unit_layout)
        self.unit_list.setToolTip("Liste des unités disponibles. Double-cliquez ou faites glisser pour ajouter.")
        self.unit_preview.setToolTip("Aperçu de l'unité sélectionnée")
        self.tabs.addTab(self.unit_tab, "Unités")
        self.refresh_deck_units_list()

    def refresh_card_list(self):
        log_debug("[CRITICAL] refresh_card_list: version PATCHEE EXECUTEE")
        self.card_list.clear()
        selected_element = self.card_element_filter.currentText()
        for c in self.base_cards:
            if not hasattr(c, "name") or not hasattr(c, "card_type"):
                log_debug(f"[CRITICAL] refresh_card_list: entrée non-carte détectée : {c} (type={type(c)})")
                continue
            # Log pour traquer les card_type pollués
            log_debug(f"[INFO] carte: {c} type(c.card_type): {type(c.card_type)} valeur: {c.card_type}")
            card_type_name = getattr(c.card_type, 'name', c.card_type)
            if card_type_name in ("UNIT", "HERO"):
                continue
            if selected_element == "Tous les éléments" or (hasattr(c, 'element') and c.element and hasattr(c.element, 'name') and c.element.name.title() == selected_element):
                log_debug(f"[CRITICAL] refresh_card_list: ajout carte {c.name} ({card_type_name})")
                item = QListWidgetItem(f"{c.name} ({card_type_name})")
                self.card_list.addItem(item) 