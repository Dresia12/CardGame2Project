import os

def log_debug(msg):
    with open(os.path.join(os.path.dirname(__file__), '../../debug_cardgame2.log'), 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from CardGame2.data_manager import DataManager
from CardGame2.sets.base_set import get_base_set
from CardGame2.sets.elemental_set import get_elemental_set
from CardGame2.boosters.booster import generate_booster
from typing import Optional
from CardGame2.ui.components import StyledButton, StatsPanel, CardWidget, NotificationPopup, LoadingPopup, HelpDialog, make_styled_button, BoosterOpenDialog
from PyQt5.QtCore import QPropertyAnimation, QPoint, QTimer, Qt
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QKeyEvent, QKeySequence
from CardGame2.ui.style_constants import BUY_BTN_STYLE, BACK_BTN_STYLE, RARITY_COLOR_MAP
from CardGame2.ui.resources import UI_TEXTS
from CardGame2.ui.utils import safe_add_widget, safe_clear_layout, is_layout_valid, is_widget_valid  # type: ignore
try:
    from CardGame2.models.types import CardType
    from CardGame2.models.hero import Hero
except ImportError:
    from ..models.types import CardType
    from ..models.hero import Hero

data_manager = DataManager()

class ShopMenu(QWidget):
    BOOSTER_COST = 100
    def __init__(self, player_name: str, parent: Optional[QWidget] = None) -> None:
        log_debug(f"[DEBUG] ShopMenu.__init__ début pour {player_name}, parent={parent}")
        super().__init__(parent)
        if player_name == 'Dresia':
            self.BOOSTER_COST = 0
        else:
            self.BOOSTER_COST = ShopMenu.BOOSTER_COST
        layout = QVBoxLayout()
        self.label = QLabel("Boutique : Achetez des boosters")
        self.unit_button = StyledButton(f"Acheter 1 booster (Gratuit)")
        self.pack_button = StyledButton(f"Acheter un pack de 5 boosters (Gratuit)")
        self.currency_label = QLabel(f"Monnaie : {data_manager.get_currency()} 🪙")
        self.stats_panel = StatsPanel("Dernière carte obtenue", {"-": "-"})
        self.card_widget = CardWidget("-", "-", "-", 0)
        self.buy_button = make_styled_button(
            "Acheter un booster (100)", BUY_BTN_STYLE, "Acheter un booster pour 100 pièces", lambda: self.buy_boosters(1)
        )
        self.back_button = make_styled_button(
            "Retour", BACK_BTN_STYLE, "Retour au menu principal", self.return_to_main
        )
        self.history_button = StyledButton("Historique des boosters")
        self.label.setToolTip(UI_TEXTS['shop_label'])
        self.unit_button.setToolTip(UI_TEXTS['unit_button'])
        self.pack_button.setToolTip(UI_TEXTS['pack_button'])
        self.currency_label.setToolTip(UI_TEXTS['currency_label'])
        self.stats_panel.setToolTip(UI_TEXTS['shop_stats_panel'])
        self.card_widget.setToolTip(UI_TEXTS['shop_card_widget'])
        self.buy_button.setToolTip(UI_TEXTS['buy_button'])
        self.back_button.setToolTip(UI_TEXTS['shop_back_button'])
        self.history_button.setToolTip(UI_TEXTS['history_button'])
        layout.addWidget(self.label)
        layout.addWidget(self.currency_label)
        layout.addWidget(self.unit_button)
        layout.addWidget(self.pack_button)
        layout.addWidget(self.stats_panel)
        layout.addWidget(self.card_widget)
        layout.addWidget(self.buy_button)
        layout.addWidget(self.back_button)
        layout.addWidget(self.history_button)
        self.setLayout(layout)
        self.unit_button.clicked.connect(self.buy_one)
        self.pack_button.clicked.connect(self.buy_pack)
        self.buy_button.clicked.connect(lambda: self.buy_boosters(1))
        self.back_button.clicked.connect(self.return_to_main)
        self.history_button.clicked.connect(self.show_booster_history)
        self.setTabOrder(self.unit_button, self.pack_button)
        self.setTabOrder(self.pack_button, self.buy_button)
        self.setTabOrder(self.buy_button, self.back_button)
        self.setTabOrder(self.back_button, self.history_button)
        self.unit_button.setFocus()
        log_debug(f"[DEBUG] ShopMenu.__init__ fin pour {player_name}, self={self}, parent={self.parent()}")
    def buy_one(self) -> None:
        self.buy_boosters(1)
    def buy_pack(self) -> None:
        self.buy_boosters(5)
    def buy_boosters(self, count: int) -> None:
        log_debug(f"[DEBUG] buy_boosters appelé avec count={count}")
        loading = LoadingPopup("Ouverture du booster...", self)
        loading.show()
        def ensure_card_object(card, card_pool):
            if isinstance(card, str):
                card_obj = next((c for c in card_pool if getattr(c, 'name', None) == card), None)
                if card_obj is not None:
                    log_debug(f"[WARN] Carte '{card}' convertie en objet depuis card_pool (utilitaire global)")
                    return card_obj
                else:
                    log_debug(f"[ERROR] Impossible de retrouver l'objet pour le nom {card} (utilitaire global)")
                    return None
            return card
        try:
            QApplication.processEvents()
            total_cost = self.BOOSTER_COST * count
            if data_manager.get_currency() < total_cost:
                log_debug("[DEBUG] Pas assez de monnaie pour acheter le booster")
                loading.close()
                QMessageBox.warning(self, "Boutique", "Pas assez de monnaie !")
                NotificationPopup("Pas assez de monnaie !", 2000, self).show()
                return
            data_manager.spend_currency(total_cost)
            card_pool = get_base_set() + get_elemental_set()
            collection = data_manager.get_collection()
            hero_collection = data_manager.get_hero_collection()
            gain = 0
            last_card = None
            doublon = False
            all_boosters = []
            for _ in range(count):
                booster = generate_booster(card_pool)
                log_debug(f"[TRACE] Booster brut généré : {booster} (types: {[type(c) for c in booster]})")
                # Patch radical : conversion str -> objet AVANT tout accès à .name
                booster_fixed = []
                for card in booster:
                    if isinstance(card, str):
                        card_obj = next((c for c in card_pool if getattr(c, 'name', None) == card), None)
                        if card_obj is not None:
                            booster_fixed.append(card_obj)
                            log_debug(f"[WARN] Carte '{card}' convertie en objet depuis card_pool (patch radical)")
                        else:
                            log_debug(f"[ERROR] Impossible de retrouver l'objet pour le nom {card} (patch radical)")
                    else:
                        booster_fixed.append(card)
                booster = booster_fixed
                if any(isinstance(c, str) for c in booster):
                    log_debug(f"[ALERT] Booster contient encore des str après conversion : {booster}")
                all_boosters.append(booster)
                log_debug(f"[DEBUG] Booster généré : {[card.name for card in booster]}")
                for card in booster:
                    log_debug(f"[TRACE] Avant accès à .name dans boucle booster : card={card} (type={type(card)})")
                    if isinstance(card, str):
                        log_debug(f"[ERROR] card est un str dans la boucle booster, valeur={card}, on ignore.")
                        continue
                    name = card.name
                    # Gestion héros
                    if (hasattr(card, 'card_type') and getattr(card, 'card_type', None) == CardType.HERO) or isinstance(card, Hero):
                        if name not in hero_collection:
                            data_manager.add_hero_to_collection(name)
                            log_debug(f"[DEBUG] Nouveau héros obtenu : {name}")
                        else:
                            gain += int(self.BOOSTER_COST * 0.1)
                            doublon = True
                            log_debug(f"[DEBUG] Doublon héros pour {name}, gain +{int(self.BOOSTER_COST * 0.1)}")
                    else:
                        if collection.get(name, 0) < 2:
                            collection[name] = collection.get(name, 0) + 1
                            log_debug(f"[DEBUG] Nouvelle carte obtenue : {name}")
                        else:
                            gain += int(self.BOOSTER_COST * 0.1)
                            doublon = True
                            log_debug(f"[DEBUG] Doublon pour {name}, gain +{int(self.BOOSTER_COST * 0.1)}")
                    last_card = card
            data_manager.set_collection(collection)
            if gain > 0:
                data_manager.add_currency(gain)
                log_debug(f"[DEBUG] Gain total sur doublons : {gain}")
                NotificationPopup(f"+{gain} 🪙 pour les doublons !", 2000, self).show()
            self.currency_label.setText(f"Monnaie : {data_manager.get_currency()} 🪙")
            log_debug(f"[DEBUG] Monnaie après achat : {data_manager.get_currency()}")
            # OUVERTURE ANIMEE
            for booster in all_boosters:
                log_debug(f"[TRACE] Avant BoosterOpenDialog : booster={booster} (types: {[type(c) for c in booster]})")
                dlg = BoosterOpenDialog(booster, RARITY_COLOR_MAP, self)
                dlg.exec_()
                log_debug(f"[TRACE] Avant add_booster_history : booster={booster} (types: {[type(c) for c in booster]})")
                data_manager.add_booster_history(booster)
            if last_card:
                log_debug(f"[TRACE] Avant accès à .name sur last_card : last_card={last_card} (type={type(last_card)})")
                if isinstance(last_card, str):
                    log_debug(f"[ERROR] last_card est un str, valeur={last_card}, on ignore l'affichage.")
                else:
                    self.stats_panel.set_stats(self.card_stats(last_card))
                    self.card_widget.setParent(None)
                    self.card_widget = CardWidget(last_card.name, last_card.card_type.name, last_card.rarity.name, getattr(last_card, 'cost', 0), getattr(last_card, 'attack', None), getattr(last_card, 'health', None), getattr(last_card, 'description', ''))
                    layout_obj = self.layout()
                    if layout_obj is not None:
                        try:
                            safe_add_widget(layout_obj, self.card_widget)
                        except AttributeError:
                            safe_add_widget(layout_obj, self.card_widget)
                    self.card_widget.setWindowOpacity(0.0)
                    anim = QPropertyAnimation(self.card_widget, b"windowOpacity")
                    anim.setDuration(300)
                    anim.setStartValue(0.0)
                    anim.setEndValue(1.0)
                    anim.start()
                    self._last_anim = anim
                    shake = QPropertyAnimation(self.card_widget, b"pos")
                    shake.setDuration(180)
                    shake.setKeyValueAt(0, self.card_widget.pos())
                    shake.setKeyValueAt(0.2, self.card_widget.pos() + self.card_widget.mapToParent(QPoint(-10, 0)))
                    shake.setKeyValueAt(0.5, self.card_widget.pos() + self.card_widget.mapToParent(QPoint(10, 0)))
                    shake.setKeyValueAt(0.8, self.card_widget.pos() + self.card_widget.mapToParent(QPoint(-10, 0)))
                    shake.setKeyValueAt(1, self.card_widget.pos())
                    shake.start()
                    self.card_widget.play_sound('victory' if not doublon else 'effect_expire')
            else:
                self.stats_panel.set_stats({"-": "-"})
                self.card_widget.setParent(None)
                self.card_widget = CardWidget("-", "-", "-", 0)
                layout_obj = self.layout()
                if layout_obj is not None:
                    try:
                        safe_add_widget(layout_obj, self.card_widget)
                    except AttributeError:
                        safe_add_widget(layout_obj, self.card_widget)
            NotificationPopup(f"Vous avez ouvert {count} booster(s) !", 2000, self).show()
            QTimer.singleShot(1000, loading.close)
            log_debug("[DEBUG] Fin de buy_boosters")
        except Exception as e:
            log_debug(f"[ERROR] Exception dans buy_boosters : {e}")
            loading.close()
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'achat du booster : {e}")
            NotificationPopup(f"Erreur achat booster : {e}", 2500, self).show()
    def card_stats(self, card) -> dict:
        d = {"Nom": card.name, "Type": card.card_type.name, "Rareté": card.rarity.name, "Coût": getattr(card, 'cost', '-')}
        if hasattr(card, 'attack') and hasattr(card, 'health'):
            d["ATK"] = getattr(card, 'attack', '-')
            d["PV"] = getattr(card, 'health', '-')
        if hasattr(card, 'description') and card.description:
            d["Description"] = card.description
        return d
    def return_to_main(self) -> None:
        log_debug("[DEBUG] Retour au menu principal depuis ShopMenu")
        try:
            self.parent().parent().go_to_menu(self.parent().parent().player_name)
            NotificationPopup("Retour au menu principal", 1500, self).show()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans return_to_main : {e}")
            QMessageBox.critical(self, "Erreur navigation", f"Exception lors du retour au menu : {e}")
            NotificationPopup(f"Erreur navigation : {e}", 2500, self).show()
    def set_daltonian_mode(self, daltonian: bool):
        log_debug(f"[DEBUG] set_daltonian_mode appelé avec daltonian={daltonian}")
        if hasattr(self, 'card_widget') and self.card_widget:
            self.card_widget.set_aura(True, daltonian_mode=daltonian)
    def keyPressEvent(self, event):
        log_debug(f"[DEBUG] keyPressEvent ShopMenu : key={event.key()}")
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
            - Achetez des boosters pour agrandir votre collection.<br>
            - Les cartes en double sont converties en monnaie bonus.<br>
            - Cliquez sur une carte pour voir ses détails.<br>
            """
            dlg = HelpDialog('Aide - Boutique', html_content, self)
            dlg.exec_()
            event.accept()
            return
        super().keyPressEvent(event)
    def showEvent(self, event):
        log_debug(f"[DEBUG] ShopMenu.showEvent pour {self.player_name}, self={self}, visible={self.isVisible()}")
        super().showEvent(event)
    def setVisible(self, visible):
        log_debug(f"[DEBUG] ShopMenu.setVisible({visible}) pour {self.player_name}, self={self}")
        super().setVisible(visible)
    def focusInEvent(self, event):
        log_debug(f"[DEBUG] ShopMenu.focusInEvent pour {self.player_name}, self={self}")
        super().focusInEvent(event)
    def show_booster_history(self):
        history = data_manager.get_booster_history()
        dlg = QDialog(self)
        dlg.setWindowTitle("Historique des boosters")
        vbox = QVBoxLayout()
        if not history:
            vbox.addWidget(QLabel("Aucun booster ouvert récemment."))
        else:
            for entry in reversed(history):
                date = entry.get('date', '')
                cards = entry.get('cards', [])
                label = QLabel(f"<b>{date[:19]}</b> : " + ', '.join([f"<span style='color:{RARITY_COLOR_MAP.get(c['rarity'], '#fff')}'>{c['name']} ({c['rarity']})</span>" for c in cards]))
                label.setWordWrap(True)
                vbox.addWidget(label)
        close_btn = StyledButton("Fermer")
        close_btn.clicked.connect(dlg.accept)
        vbox.addWidget(close_btn)
        dlg.setLayout(vbox)
        dlg.exec_() 