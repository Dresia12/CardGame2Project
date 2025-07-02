from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QFrame, QScrollArea, QDialog
)
from PyQt5.QtCore import QPropertyAnimation, QRect, QTimer, Qt
from PyQt5.QtGui import QKeyEvent, QKeySequence
from typing import Optional, Callable
from CardGame2.ui.components import (
    StyledButton, StatsPanel, CardWidget, NotificationPopup, HealthBarWidget, LoadingPopup, HelpDialog
)
import datetime
from CardGame2.data_manager import DataManager
from CardGame2.models.hero import HeroPassive
from CardGame2.ui.theme_manager import ThemeManager
from CardGame2.ui.resources import UI_TEXTS
import os
try:
    import sip
except ImportError:
    sip = None

# Stylesheets factorisés
PLAYER_BOARD_STYLE = "border: 2px solid #3a7afe; padding: 8px; background: transparent;"
PLAYER_BOARD_HIGHLIGHT_STYLE = "border: 2px solid #27ae60; background: #23272e; padding: 8px;"
IA_HERO_STYLE = "background-color: #ffe066; border: 2px solid #ffae00; color: #222;"
IA_UNIT_STYLE = "background-color: #ffebee; border: 2px solid #c62828; color: #222;"

def log_debug(msg):
    with open(os.path.join(os.path.dirname(__file__), '../../debug_cardgame2.log'), 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Utilitaires robustes pour layouts/widgets

def safe_add_widget(layout, widget):
    if sip is not None and layout is not None and not sip.isdeleted(layout):
        layout.addWidget(widget)
    else:
        log_debug("[CRITICAL] Tentative d'ajout à un layout détruit !")

def safe_clear_layout(layout):
    if sip is None or layout is None or sip.isdeleted(layout):
        return
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if sip is not None and widget is not None and not sip.isdeleted(widget):
            widget.setParent(None)
            widget.deleteLater()

class PlayerBoardWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet(PLAYER_BOARD_STYLE)
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)
        self.setLayout(self._layout)
        self.setMinimumHeight(280)  # Pour que les CardWidget (260px) tiennent bien
        self.setSizePolicy(self.sizePolicy().Expanding, self.sizePolicy().Fixed)
    def add_card_widget(self, widget):
        if not hasattr(self, '_layout') or self._layout is None or (sip is not None and sip.isdeleted(self._layout)):
            log_debug("[ERROR] PlayerBoardWidget._layout is None or destroyed, board will be recreated if needed.")
            raise RuntimeError("PlayerBoardWidget._layout is None or destroyed")
        try:
            safe_add_widget(self._layout, widget)
        except RuntimeError as e:
            log_debug(f"[ERROR] add_card_widget: {e}")
            raise
    def clear_board(self):
        safe_clear_layout(self._layout)
    def set_highlight(self, highlight: bool):
        if highlight:
            self.setStyleSheet(PLAYER_BOARD_HIGHLIGHT_STYLE)
        else:
            self.setStyleSheet(PLAYER_BOARD_STYLE)

class CombatScreen(QWidget):
    def __init__(self, player1, player2, battle, parent: Optional[QWidget] = None, on_finish: Optional[Callable] = None) -> None:
        super().__init__(parent)
        self.player1 = player1
        self.player2 = player2
        self.battle = battle
        self.on_finish = on_finish
        self.round_count = 0
        # --- Connexion des hooks Battle pour feedback UI ---
        self.battle.on_effect_expire = self._on_effect_expire
        self.battle.on_effect_secondary = self._on_effect_secondary
        self.battle.on_error = self._on_battle_error
        # ---
        if not hasattr(self.player1, 'mana'):
            self.player1.mana = 1
        # Pioche initiale de 5 cartes pour chaque joueur
        self.player1.draw(5)
        self.player2.draw(5)
        self.selected_attacker = None
        self.show_hp_bars = True
        self.invert_boards = False
        self.daltonian_mode = False
        self._init_ui()
        self._start_turn_timer()
        self.refresh_hand()
        self.update_ui()

    def _init_ui(self):
        self._layout = QVBoxLayout()
        # Barre horizontale de boutons tout en haut
        self.top_buttons_layout = QHBoxLayout()
        self.top_buttons_layout.setSpacing(0)
        self.top_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.daltonian_button = StyledButton("Mode daltonien")
        self.daltonian_button.setCheckable(True)
        self.daltonian_button.setChecked(False)
        self.daltonian_button.clicked.connect(self.toggle_daltonian_mode)
        self.daltonian_button.setToolTip(UI_TEXTS['daltonian_button'])
        self.top_buttons_layout.addWidget(self.daltonian_button)
        self.invert_boards_button = StyledButton("Inverser les boards (IA/Joueur)")
        self.invert_boards_button.setCheckable(True)
        self.invert_boards_button.setChecked(False)
        self.invert_boards_button.clicked.connect(self.toggle_invert_boards)
        self.invert_boards_button.setToolTip(UI_TEXTS['invert_boards_button'])
        self.top_buttons_layout.addWidget(self.invert_boards_button)
        # Activation héros (créé dans _init_hero_activation)
        self.activate_hero_button = StyledButton(f"Activer Héros (Coût : {self.player1.hero.get_activation_cost()} mana)")
        self.activate_hero_button.clicked.connect(self.activate_hero)
        self.activate_hero_button.setToolTip(UI_TEXTS['activate_hero_button'])
        self.top_buttons_layout.addWidget(self.activate_hero_button)
        # Bouton tour suivant (créé dans _init_action_buttons)
        self.next_button = StyledButton("Tour suivant")
        self.next_button.setToolTip("Passer au tour suivant (raccourci : Entrée)")
        self.next_button.clicked.connect(self.next_round)
        self.top_buttons_layout.addWidget(self.next_button)
        # Bouton abandonner
        self.forfeit_button = StyledButton("Abandonner")
        self.forfeit_button.setToolTip("Abandonner la partie et retourner au menu")
        self.forfeit_button.clicked.connect(self.forfeit)
        self.top_buttons_layout.addWidget(self.forfeit_button)
        # Bouton masquer barres de vie
        self.toggle_hp_button = StyledButton("Masquer les barres de vie")
        self.toggle_hp_button.setCheckable(True)
        self.toggle_hp_button.setChecked(True)
        self.toggle_hp_button.clicked.connect(self.toggle_hp_bars)
        self.toggle_hp_button.setToolTip(UI_TEXTS['toggle_hp_button'])
        self.top_buttons_layout.addWidget(self.toggle_hp_button)
        # Ajoute la barre de boutons tout en haut
        self._layout.insertLayout(0, self.top_buttons_layout)
        # Poursuit l'init UI sans les addWidget individuels pour ces boutons
        self._init_hero_panels()
        self._init_mana_label()
        self._init_pv_panels()
        self._init_units_panels()
        self._init_log()
        self._init_timer()
        self._init_hand_panel()
        self.setLayout(self._layout)
        # Tab order (optionnel)
        self.setTabOrder(self.daltonian_button, self.invert_boards_button)
        self.setTabOrder(self.invert_boards_button, self.activate_hero_button)
        self.setTabOrder(self.activate_hero_button, self.next_button)
        self.setTabOrder(self.next_button, self.forfeit_button)
        self.setTabOrder(self.forfeit_button, self.toggle_hp_button)
        self.daltonian_button.setFocus()

    def _init_hero_panels(self):
        self.hero_layout = QHBoxLayout()
        self.hero1_panel = StatsPanel("Votre Héros", self.hero_stats(self.player1.hero))
        self.hero2_panel = StatsPanel("Héros IA", self.hero_stats(self.player2.hero))
        self.hero_layout.addWidget(self.hero1_panel)
        self.hero_layout.addStretch()
        self.hero_layout.addWidget(self.hero2_panel)
        self._layout.addLayout(self.hero_layout)
        self.hero1_panel.setToolTip(UI_TEXTS['hero1_panel'])
        self.hero2_panel.setToolTip(UI_TEXTS['hero2_panel'])

    def _init_hero_activation(self):
        # Ne crée plus le bouton ici, il est déjà créé dans _init_ui
        pass

    def _init_mana_label(self):
        self.mana_label = QLabel(f"Mana : {self.player1.mana}")
        self._layout.addWidget(self.mana_label)
        self.mana_label.setToolTip(UI_TEXTS['mana_label'])

    def _init_pv_panels(self):
        self.pv_layout = QHBoxLayout()
        self.pv1_label = QLabel(f"PV Joueur : {self.player1.health}")
        self.pv2_label = QLabel(f"PV IA : {self.player2.health}")
        self.pv_layout.addWidget(self.pv1_label)
        self.pv_layout.addStretch()
        self.pv_layout.addWidget(self.pv2_label)
        self._layout.addLayout(self.pv_layout)
        self.pv1_label.setToolTip("Points de vie restants de votre héros")
        self.pv2_label.setToolTip("Points de vie restants du héros IA")

    def _init_units_panels(self):
        aura_colors = {
            'boost': "#ffd600" if not self.daltonian_mode else "#ff9800",
            'poison': "#9c27b0" if not self.daltonian_mode else "#607d8b",
            'shield': "#2979ff" if not self.daltonian_mode else "#009688",
            'freeze': "#00e5ff" if not self.daltonian_mode else "#795548",
            'burn': "#ff5722" if not self.daltonian_mode else "#607d8b",
        }
        self.units_layout = QVBoxLayout()
        # Ligne du joueur (héros + unités) avec scroll si besoin
        self.player_board = PlayerBoardWidget()
        self.player_board_widgets = []
        self.player_board_scroll = QScrollArea()
        self.player_board_scroll.setWidgetResizable(True)
        self.player_board_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.player_board_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.player_board_scroll.setFrameShape(QFrame.NoFrame)
        self.player_board_scroll.setMinimumHeight(300)
        self.player_board_scroll.setMaximumHeight(320)
        self.player_board_scroll.setWidget(self.player_board)
        self.units_layout.addWidget(QLabel("Votre board :"))
        self.units_layout.addWidget(self.player_board_scroll)
        # Ligne IA (héros + unités) avec scroll aussi
        self.ia_board_widget = PlayerBoardWidget()
        self.ia_board_widgets = []
        ia_hero_widget = CardWidget(self.player2.hero.name, "HÉROS", "-", 0, self.player2.hero.base_attack, self.player2.hero.base_hp, f"DEF: {self.player2.hero.base_defense}")
        ia_hero_widget.setStyleSheet(IA_HERO_STYLE)
        try:
            self.ia_board_widget.add_card_widget(ia_hero_widget)
        except RuntimeError:
            log_debug("[DEBUG] ia_board_widget détruit détecté lors de add_card_widget (init, héros IA), recréation immédiate")
            self.ia_board_widget = PlayerBoardWidget()
            self.ia_board_widgets = []
            if hasattr(self, 'units_layout') and self.units_layout is not None:
                self.units_layout.insertWidget(3, self.ia_board_widget)
                log_debug("[DEBUG] Nouveau ia_board_widget inséré dans units_layout (recréation immédiate, init, héros IA)")
            self.ia_board_widget.add_card_widget(ia_hero_widget)
        self.ia_board_widgets.append(ia_hero_widget)
        if self.show_hp_bars:
            hp_bar = HealthBarWidget(getattr(self.player2.hero, 'current_hp', self.player2.hero.base_hp), getattr(self.player2.hero, 'max_hp', self.player2.hero.base_hp))
            try:
                self.ia_board_widget.add_card_widget(hp_bar)
            except RuntimeError:
                log_debug("[DEBUG] ia_board_widget détruit détecté lors de add_card_widget (init, hp_bar héros IA), recréation immédiate")
                self.ia_board_widget = PlayerBoardWidget()
                self.ia_board_widgets = []
                if hasattr(self, 'units_layout') and self.units_layout is not None:
                    self.units_layout.insertWidget(3, self.ia_board_widget)
                    log_debug("[DEBUG] Nouveau ia_board_widget inséré dans units_layout (recréation immédiate, init, hp_bar héros IA)")
                self.ia_board_widget.add_card_widget(hp_bar)
        for unit in self.player2.board:
            w = CardWidget(unit.name, "UNITÉ", getattr(unit, 'rarity', '-'), getattr(unit, 'cost', 0), getattr(unit, 'attack', None), getattr(unit, 'health', None), getattr(unit, 'description', ''))
            w.setStyleSheet(IA_UNIT_STYLE)
            w.clicked.connect(lambda _, widget=w, target_unit=unit: self.handle_attack(widget, target_unit))
            w.keyPressEvent = lambda event, w=w, u=unit: self._card_keypress(event, w, u, is_player=False)
            # Ajout du héros IA sur le board (robuste)
            try:
                self.ia_board_widget.add_card_widget(w)
            except RuntimeError:
                log_debug("[DEBUG] ia_board_widget détruit détecté lors de add_card_widget, recréation immédiate")
                self.ia_board_widget = PlayerBoardWidget()
                self.ia_board_widgets = []
                if hasattr(self, 'units_layout') and self.units_layout is not None:
                    self.units_layout.insertWidget(3, self.ia_board_widget)
                    log_debug("[DEBUG] Nouveau ia_board_widget inséré dans units_layout (recréation immédiate)")
                self.ia_board_widget.add_card_widget(w)
            self.ia_board_widgets.append(w)
            if self.show_hp_bars:
                hp_bar = HealthBarWidget(getattr(unit, 'health', 0), getattr(unit, 'max_health', 0))
                # Ajout du héros IA sur le board (robuste)
                try:
                    self.ia_board_widget.add_card_widget(hp_bar)
                except RuntimeError:
                    log_debug("[DEBUG] ia_board_widget détruit détecté lors de add_card_widget, recréation immédiate")
                    self.ia_board_widget = PlayerBoardWidget()
                    self.ia_board_widgets = []
                    if hasattr(self, 'units_layout') and self.units_layout is not None:
                        self.units_layout.insertWidget(3, self.ia_board_widget)
                        log_debug("[DEBUG] Nouveau ia_board_widget inséré dans units_layout (recréation immédiate)")
                    self.ia_board_widget.add_card_widget(hp_bar)
            if hasattr(unit, 'status_effects'):
                for eff in unit.status_effects:
                    eff_type = eff['type'] if isinstance(eff, dict) else eff
                    if eff_type in aura_colors:
                        w.set_aura(True, color=aura_colors[eff_type], daltonian_mode=self.daltonian_mode)
            if hasattr(self.player2, 'hero') and self.player2.hero and hasattr(self.player2.hero, 'has_passive'):
                if self.player2.hero.has_passive(HeroPassive.CHARISMATIQUE):
                    if hasattr(unit, 'health') and hasattr(unit, 'max_health') and unit.health < unit.max_health:
                        w.heal_glow()
        for w in self.ia_board_widgets:
            w.set_glow(self.selected_attacker is not None, color="#ff1744")
            # Feedback visuel de sélection de cible
            if self.selected_attacker is not None and w.hasFocus():
                w.set_target_highlight(True)
            else:
                w.set_target_highlight(False)
        self.pv1_label.setText(f"PV Joueur : {self.player1.health}")
        self.pv2_label.setText(f"PV IA : {self.player2.health}")
        self.mana_label.setText(f"Mana : {self.player1.mana}")

    def _init_log(self):
        self.log = QListWidget()
        self.toggle_log_button = StyledButton("Masquer le log")
        self.toggle_log_button.setCheckable(True)
        self.toggle_log_button.setChecked(True)
        self.toggle_log_button.clicked.connect(self.toggle_log_visibility)
        self.toggle_log_button.setToolTip("Affiche ou masque le log du combat")
        self.copy_log_button = StyledButton("Copier le log")
        self.copy_log_button.clicked.connect(self.copy_log_to_clipboard)
        self.copy_log_button.setToolTip("Copie l'intégralité du log dans le presse-papiers")
        self.export_log_button = StyledButton("Exporter le log")
        self.export_log_button.clicked.connect(self.export_log_to_file)
        self.export_log_button.setToolTip("Exporte le log du combat dans un fichier texte")
        self._layout.addWidget(QLabel("Log du combat :"))
        self._layout.addWidget(self.toggle_log_button)
        self._layout.addWidget(self.log)
        self._layout.addWidget(self.copy_log_button)
        self._layout.addWidget(self.export_log_button)
        self.log.setToolTip("Historique détaillé des actions du combat")

    def _init_action_buttons(self):
        # Ne crée plus les boutons ici, ils sont déjà créés dans _init_ui
        pass

    def _init_timer(self):
        self.timer_label = QLabel("Temps restant : 45s")
        self._layout.addWidget(self.timer_label)
        self.timer_label.setToolTip("Temps restant pour jouer ce tour")
        self.turn_timer = QTimer(self)
        self.turn_timer.setInterval(1000)
        self.turn_timer.timeout.connect(self.update_timer)
        self.time_left = 45

    def _start_turn_timer(self):
        self.turn_timer.start()

    def _init_hand_panel(self):
        self.hand_list = QListWidget()
        self.hand_list.setStyleSheet("background: #181a20; color: #f8f8f2; font-size: 15px; min-height: 80px;")
        self.hand_list.setDragEnabled(True)
        self._layout.addWidget(QLabel("Votre main :"))
        self._layout.addWidget(self.hand_list)
        # Correction PyQt5 : signature des événements
        def board_drag_enter_a0(a0):
            return self.board_drag_enter(a0)
        def board_drag_leave_a0(a0):
            return self.board_drag_leave(a0)
        def board_drop_event_a0(a0):
            return self.board_drop_event(a0)
        self.player_board.dragEnterEvent = board_drag_enter_a0
        self.player_board.dragLeaveEvent = board_drag_leave_a0
        self.player_board.dropEvent = board_drop_event_a0

    def hero_stats(self, hero) -> dict:
        if not hero:
            return {"-": "-"}
        return {
            "Nom": hero.name,
            "PV": f"{hero.base_hp}+{hero.customization.get_hp_bonus()}",
            "ATK": f"{hero.base_attack}+{hero.customization.get_attack_bonus()}",
            "DEF": f"{hero.base_defense}+{hero.customization.get_defense_bonus()}",
            "Passifs": ', '.join([p.value for p in hero.customization.passives])
        }

    def units_summary(self, units) -> str:
        if not units:
            return "-"
        return ", ".join([f"{u.name} (ATK:{getattr(u, 'attack', '-')}/PV:{getattr(u, 'health', '-')})" for u in units])

    def _add_log(self, message: str, type_: str = "info"):
        # Ajoute une icône/couleur selon le type
        if type_ == "attack":
            html = f'<span style="color:#d32f2f;">🗡️ {message}</span>'
        elif type_ == "activate":
            html = f'<span style="color:#ffb300;">✨ {message}</span>'
        elif type_ == "victory":
            html = f'<span style="color:#43a047;">🏆 {message}</span>'
        elif type_ == "defeat":
            html = f'<span style="color:#b71c1c;">💀 {message}</span>'
        elif type_ == "warning":
            html = f'<span style="color:#fbc02d;">⚠️ {message}</span>'
        else:
            html = message
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.DisplayRole, html)
        self.log.addItem(item)
        self.log.scrollToBottom()
        while self.log.count() > 8:
            self.log.takeItem(0)

    def activate_hero(self):
        try:
            cost = self.player1.hero.get_activation_cost()
            if self.player1.mana < cost:
                self._add_log(f"Pas assez de mana pour activer le héros (coût : {cost}) !", type_="warning")
                return
            self.player1.mana -= cost
            self.mana_label.setText(f"Mana : {self.player1.mana}")
            self.player1.hero.activate()
            self.hero1_panel.setStyleSheet("background-color: #ffe066; border: 2px solid #ffae00; color: #222;")
            self._add_log(f"Votre héros est activé et entre sur le terrain ! (Coût : {cost} mana)", type_="activate")
            self.activate_hero_button.setEnabled(False)
            self.update_ui()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans activate_hero : {e}")
            NotificationPopup(f"Erreur lors de l'activation du héros : {e}", 4000, self).show()

    def update_ui(self) -> None:
        try:
            aura_colors = {
                'boost': "#ffd600" if not self.daltonian_mode else "#ff9800",
                'poison': "#9c27b0" if not self.daltonian_mode else "#607d8b",
                'shield': "#2979ff" if not self.daltonian_mode else "#009688",
                'freeze': "#00e5ff" if not self.daltonian_mode else "#795548",
                'burn': "#ff5722" if not self.daltonian_mode else "#607d8b",
            }
            log_debug("[DEBUG] CombatScreen.update_ui appelée")
            recreate = False
            if (not hasattr(self, 'player_board') or self.player_board is None or
                not hasattr(self.player_board, '_layout') or self.player_board._layout is None or
                self.player_board.parent() is None):
                log_debug("[DEBUG] player_board détruit ou orphelin, recréation forcée")
                recreate = True
            if recreate:
                if hasattr(self, 'units_layout') and self.units_layout is not None:
                    for i in reversed(range(self.units_layout.count())):
                        item = self.units_layout.itemAt(i)
                        widget = item.widget() if item is not None else None
                        if widget is self.player_board:
                            self.units_layout.removeWidget(widget)
                            if widget is not None:
                                widget.deleteLater()
                            log_debug("[DEBUG] Ancien player_board supprimé du layout (recréation forcée)")
                self.player_board = PlayerBoardWidget()
                self.player_board_widgets = []
                if hasattr(self, 'units_layout') and self.units_layout is not None:
                    self.units_layout.insertWidget(1, self.player_board)
                    log_debug("[DEBUG] Nouveau player_board inséré dans units_layout (recréation forcée)")
            try:
                self._refresh_hero_panels()
            except Exception as e:
                log_debug(f"[ERROR] Exception dans _refresh_hero_panels : {e}")
                NotificationPopup(f"Erreur dans l'affichage des héros : {e}", 4000, self).show()
            self.player_board.clear_board()
            self.player_board_widgets.clear()
            for w in self.ia_board_widgets:
                if w is not None:
                    w.hide()
            self.ia_board_widgets.clear()
            if hasattr(self, 'units_widget') and self.units_widget is not None:
                self._layout.removeWidget(self.units_widget)
                self.units_widget.hide()
            self.units_layout = QVBoxLayout()
            if self.invert_boards:
                self.units_layout.addWidget(QLabel("Votre board :"))
                self.units_layout.addWidget(self.player_board_scroll)
                self.units_layout.addWidget(QLabel("Board IA :"))
                if hasattr(self, 'ia_board_scroll') and self.ia_board_scroll is not None:
                    self.units_layout.addWidget(self.ia_board_scroll)
            else:
                self.units_layout.addWidget(QLabel("Board IA :"))
                if hasattr(self, 'ia_board_scroll') and self.ia_board_scroll is not None:
                    self.units_layout.addWidget(self.ia_board_scroll)
                self.units_layout.addWidget(QLabel("Votre board :"))
                self.units_layout.addWidget(self.player_board_scroll)
            self.units_widget = QWidget()
            self.units_widget.setLayout(self.units_layout)
            self._layout.insertWidget(4, self.units_widget)
            hero_widget = CardWidget(self.player1.hero.name, "HÉROS", "-", 0, self.player1.hero.base_attack, self.player1.hero.base_hp, f"DEF: {self.player1.hero.base_defense}")
            hero_widget.setStyleSheet("background-color: #ffe066; border: 2px solid #ffae00; color: #222;")
            hero_widget.clicked.connect(lambda _, widget=hero_widget, unit=self.player1.hero: self.select_attacker(widget, unit))
            hero_widget.keyPressEvent = lambda event, w=hero_widget, u=self.player1.hero: self._card_keypress(event, w, u, is_player=True)
            try:
                if hasattr(self.player_board, '_layout') and self.player_board._layout is not None:
                    self.player_board.add_card_widget(hero_widget)
                else:
                    raise RuntimeError("player_board._layout is None")
            except RuntimeError:
                log_debug("[DEBUG] player_board détruit détecté lors de add_card_widget, recréation immédiate (hero_widget)")
                self.player_board = PlayerBoardWidget()
                self.player_board_widgets = []
                if hasattr(self, 'units_layout') and self.units_layout is not None:
                    self.units_layout.insertWidget(1, self.player_board)
                    log_debug("[DEBUG] Nouveau player_board inséré dans units_layout (recréation immédiate)")
                self.player_board.add_card_widget(hero_widget)
            self.player_board_widgets.append(hero_widget)
            if self.show_hp_bars:
                hp_bar = HealthBarWidget(getattr(self.player1.hero, 'current_hp', self.player1.hero.base_hp), getattr(self.player1.hero, 'max_hp', self.player1.hero.base_hp))
                try:
                    if hasattr(self.player_board, '_layout') and self.player_board._layout is not None:
                        self.player_board.add_card_widget(hp_bar)
                    else:
                        raise RuntimeError("player_board._layout is None")
                except RuntimeError:
                    log_debug("[DEBUG] player_board détruit détecté lors de add_card_widget, recréation immédiate (hp_bar hero)")
                    self.player_board = PlayerBoardWidget()
                    self.player_board_widgets = []
                    if hasattr(self, 'units_layout') and self.units_layout is not None:
                        self.units_layout.insertWidget(1, self.player_board)
                        log_debug("[DEBUG] Nouveau player_board inséré dans units_layout (recréation immédiate)")
                    self.player_board.add_card_widget(hp_bar)
            for unit in self.player1.board:
                w = CardWidget(unit.name, "UNITÉ", getattr(unit, 'rarity', '-'), getattr(unit, 'cost', 0), getattr(unit, 'attack', None), getattr(unit, 'health', None), getattr(unit, 'description', ''))
                w.setStyleSheet("background-color: #e3f2fd; border: 2px solid #1976d2; color: #222;")
                w.clicked.connect(lambda _, widget=w, unit=unit: self.select_attacker(widget, unit))
                w.keyPressEvent = lambda event, w=w, u=unit: self._card_keypress(event, w, u, is_player=True)
                try:
                    if hasattr(self.player_board, '_layout') and self.player_board._layout is not None:
                        self.player_board.add_card_widget(w)
                    else:
                        raise RuntimeError("player_board._layout is None")
                except RuntimeError:
                    log_debug("[DEBUG] player_board détruit détecté lors de add_card_widget, recréation immédiate (unit)")
                    self.player_board = PlayerBoardWidget()
                    self.player_board_widgets = []
                    if hasattr(self, 'units_layout') and self.units_layout is not None:
                        self.units_layout.insertWidget(1, self.player_board)
                        log_debug("[DEBUG] Nouveau player_board inséré dans units_layout (recréation immédiate)")
                    self.player_board.add_card_widget(w)
                self.player_board_widgets.append(w)
                if self.show_hp_bars:
                    hp_bar = HealthBarWidget(getattr(unit, 'health', 0), getattr(unit, 'max_health', 0))
                    try:
                        if hasattr(self.player_board, '_layout') and self.player_board._layout is not None:
                            self.player_board.add_card_widget(hp_bar)
                        else:
                            raise RuntimeError("player_board._layout is None")
                    except RuntimeError:
                        log_debug("[DEBUG] player_board détruit détecté lors de add_card_widget, recréation immédiate (hp_bar unit)")
                        self.player_board = PlayerBoardWidget()
                        self.player_board_widgets = []
                        if hasattr(self, 'units_layout') and self.units_layout is not None:
                            self.units_layout.insertWidget(1, self.player_board)
                            log_debug("[DEBUG] Nouveau player_board inséré dans units_layout (recréation immédiate)")
                        self.player_board.add_card_widget(hp_bar)
                if hasattr(unit, 'status_effects'):
                    for eff in unit.status_effects:
                        eff_type = eff['type'] if isinstance(eff, dict) else eff
                        if eff_type in aura_colors:
                            w.set_aura(True, color=aura_colors[eff_type], daltonian_mode=self.daltonian_mode)
                if hasattr(self.player1, 'hero') and self.player1.hero and hasattr(self.player1.hero, 'has_passive'):
                    if self.player1.hero.has_passive(HeroPassive.CHARISMATIQUE):
                        if hasattr(unit, 'health') and hasattr(unit, 'max_health') and unit.health < unit.max_health:
                            w.heal_glow()
            ia_hero_widget = CardWidget(self.player2.hero.name, "HÉROS", "-", 0, self.player2.hero.base_attack, self.player2.hero.base_hp, f"DEF: {self.player2.hero.base_defense}")
            try:
                if hasattr(self.ia_board_widget, '_layout') and self.ia_board_widget._layout is not None:
                    self.ia_board_widget.add_card_widget(ia_hero_widget)
                else:
                    raise RuntimeError("ia_board_widget._layout is None")
            except RuntimeError:
                log_debug("[DEBUG] ia_board_widget détruit détecté lors de add_card_widget (update_ui, héros IA), recréation immédiate")
                self.ia_board_widget = PlayerBoardWidget()
                self.ia_board_widgets = []
                if hasattr(self, 'units_layout') and self.units_layout is not None:
                    self.units_layout.insertWidget(3, self.ia_board_widget)
                    log_debug("[DEBUG] Nouveau ia_board_widget inséré dans units_layout (recréation immédiate, update_ui, héros IA)")
                self.ia_board_widget.add_card_widget(ia_hero_widget)
            self.ia_board_widgets.append(ia_hero_widget)
            if self.show_hp_bars:
                hp_bar = HealthBarWidget(getattr(self.player2.hero, 'current_hp', self.player2.hero.base_hp), getattr(self.player2.hero, 'max_hp', self.player2.hero.base_hp))
                try:
                    if hasattr(self.ia_board_widget, '_layout') and self.ia_board_widget._layout is not None:
                        self.ia_board_widget.add_card_widget(hp_bar)
                    else:
                        raise RuntimeError("ia_board_widget._layout is None")
                except RuntimeError:
                    log_debug("[DEBUG] ia_board_widget détruit détecté lors de add_card_widget (update_ui, hp_bar héros IA), recréation immédiate")
                    self.ia_board_widget = PlayerBoardWidget()
                    self.ia_board_widgets = []
                    if hasattr(self, 'units_layout') and self.units_layout is not None:
                        self.units_layout.insertWidget(3, self.ia_board_widget)
                        log_debug("[DEBUG] Nouveau ia_board_widget inséré dans units_layout (recréation immédiate, update_ui, hp_bar héros IA)")
                    self.ia_board_widget.add_card_widget(hp_bar)
            for unit in self.player2.board:
                w = CardWidget(unit.name, "UNITÉ", getattr(unit, 'rarity', '-'), getattr(unit, 'cost', 0), getattr(unit, 'attack', None), getattr(unit, 'health', None), getattr(unit, 'description', ''))
                w.setStyleSheet(IA_UNIT_STYLE)
                w.clicked.connect(lambda _, widget=w, target_unit=unit: self.handle_attack(widget, target_unit))
                w.keyPressEvent = lambda event, w=w, u=unit: self._card_keypress(event, w, u, is_player=False)
                try:
                    if hasattr(self.ia_board_widget, '_layout') and self.ia_board_widget._layout is not None:
                        self.ia_board_widget.add_card_widget(w)
                    else:
                        raise RuntimeError("ia_board_widget._layout is None")
                except RuntimeError:
                    log_debug("[DEBUG] ia_board_widget détruit détecté lors de add_card_widget, recréation immédiate (unit)")
                    self.ia_board_widget = PlayerBoardWidget()
                    self.ia_board_widgets = []
                    if hasattr(self, 'units_layout') and self.units_layout is not None:
                        self.units_layout.insertWidget(3, self.ia_board_widget)
                        log_debug("[DEBUG] Nouveau ia_board_widget inséré dans units_layout (recréation immédiate)")
                    self.ia_board_widget.add_card_widget(w)
                self.ia_board_widgets.append(w)
                if self.show_hp_bars:
                    hp_bar = HealthBarWidget(getattr(unit, 'health', 0), getattr(unit, 'max_health', 0))
                    try:
                        if hasattr(self.ia_board_widget, '_layout') and self.ia_board_widget._layout is not None:
                            self.ia_board_widget.add_card_widget(hp_bar)
                        else:
                            raise RuntimeError("ia_board_widget._layout is None")
                    except RuntimeError:
                        log_debug("[DEBUG] ia_board_widget détruit détecté lors de add_card_widget, recréation immédiate (hp_bar unit)")
                        self.ia_board_widget = PlayerBoardWidget()
                        self.ia_board_widgets = []
                        if hasattr(self, 'units_layout') and self.units_layout is not None:
                            self.units_layout.insertWidget(3, self.ia_board_widget)
                            log_debug("[DEBUG] Nouveau ia_board_widget inséré dans units_layout (recréation immédiate)")
                        self.ia_board_widget.add_card_widget(hp_bar)
                if hasattr(unit, 'status_effects'):
                    for eff in unit.status_effects:
                        eff_type = eff['type'] if isinstance(eff, dict) else eff
                        if eff_type in aura_colors:
                            w.set_aura(True, color=aura_colors[eff_type], daltonian_mode=self.daltonian_mode)
                if hasattr(self.player2, 'hero') and self.player2.hero and hasattr(self.player2.hero, 'has_passive'):
                    if self.player2.hero.has_passive(HeroPassive.CHARISMATIQUE):
                        if hasattr(unit, 'health') and hasattr(unit, 'max_health') and unit.health < unit.max_health:
                            w.heal_glow()
            for w in self.ia_board_widgets:
                w.set_glow(self.selected_attacker is not None, color="#ff1744")
                if self.selected_attacker is not None and w.hasFocus():
                    w.set_target_highlight(True)
                else:
                    w.set_target_highlight(False)
            self.pv1_label.setText(f"PV Joueur : {self.player1.health}")
            self.pv2_label.setText(f"PV IA : {self.player2.health}")
            self.mana_label.setText(f"Mana : {self.player1.mana}")
        except Exception as e:
            log_debug(f"[ERROR] Exception dans update_ui : {e}")
            NotificationPopup(f"Erreur d'affichage : {e}", 4000, self).show()

    def _refresh_hero_panels(self):
        # On ne fait plus setParent(None), on remplace les panels dans le layout
        for i in reversed(range(self.hero_layout.count())):
            item = self.hero_layout.itemAt(i)
            widget = item.widget() if item is not None else None
            if widget:
                self.hero_layout.removeWidget(widget)
                widget.hide()
        self.hero1_panel = StatsPanel("Votre Héros", self.hero_stats(self.player1.hero))
        if self.player1.hero.is_active:
            self.hero1_panel.setStyleSheet("background-color: #ffe066; border: 2px solid #ffae00; color: #222;")
        self.hero2_panel = StatsPanel("Héros IA", self.hero_stats(self.player2.hero))
        self.hero_layout.addWidget(self.hero1_panel)
        self.hero_layout.addStretch()
        self.hero_layout.addWidget(self.hero2_panel)

    def forfeit(self):
        try:
            self.battle.forfeit_player(self.player1)
            self._add_log("Vous avez abandonné. Défaite.", type_="defeat")
            self.next_button.setEnabled(False)
            self.forfeit_button.setEnabled(False)
            self.turn_timer.stop()
            if self.on_finish:
                self.on_finish(self.battle, self.round_count)
            else:
                NotificationPopup("Retour au menu principal", 2000, self).show()
                self.hide()
                if self.parent() and hasattr(self.parent(), 'go_to_menu'):
                    self.parent().go_to_menu(getattr(self.player1, 'name', ''))
                else:
                    self.close()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans forfeit : {e}")
            NotificationPopup(f"Erreur lors de l'abandon : {e}", 4000, self).show()

    def update_timer(self):
        self.time_left -= 1
        self.timer_label.setText(f"Temps restant : {self.time_left}s")
        if self.time_left <= 0:
            self._add_log("Temps écoulé ! Fin du tour automatique.", type_="warning")
            self.turn_timer.stop()
            self.next_round()

    def next_round(self) -> None:
        try:
            self.time_left = 45
            self.timer_label.setText(f"Temps restant : {self.time_left}s")
            self.turn_timer.start()
            # Décrément durée effets spéciaux sur toutes les unités
            for unit in self.player1.board + self.player2.board:
                if hasattr(unit, 'status_effects'):
                    new_effects = []
                    for eff in unit.status_effects:
                        if isinstance(eff, dict) and 'duration' in eff:
                            eff['duration'] -= 1
                            if eff['duration'] > 0:
                                new_effects.append(eff)
                            else:
                                self._add_log(f"L'effet {eff['type']} sur {unit.name} s'est dissipé.", type_="info")
                                for w in self.player_board_widgets + self.ia_board_widgets:
                                    if w.name_label.text().replace('<b>','').replace('</b>','') == unit.name:
                                        w.flash()
                                        w.play_sound('effect_expire')
                                        break
                                if eff['type'] == 'poison':
                                    if hasattr(unit, 'take_damage'):
                                        unit.take_damage(1)
                                        self._add_log(f"{unit.name} subit 1 dégât du poison qui s'est dissipé.", type_="attack")
                                        for w in self.player_board_widgets + self.ia_board_widgets:
                                            if w.name_label.text().replace('<b>','').replace('</b>','') == unit.name:
                                                w.shake()
                                                w.play_sound('attack')
                                                break
                                elif eff['type'] == 'shield':
                                    if hasattr(unit, 'health') and hasattr(unit, 'max_health'):
                                        unit.health = min(unit.health + 1, getattr(unit, 'max_health', unit.health))
                                        self._add_log(f"{unit.name} récupère 1 PV grâce au bouclier dissipé.", type_="activate")
                                        for w in self.player_board_widgets + self.ia_board_widgets:
                                            if w.name_label.text().replace('<b>','').replace('</b>','') == unit.name:
                                                w.play_sound('heal')
                                                w.heal_glow()
                                                break
                        else:
                            new_effects.append(eff)
                    unit.status_effects = new_effects
            self.player1.gain_mana()
            if self.battle.check_victory():
                winner = self.battle.winner
                result = 'victoire' if winner == self.player1 else ('défaite' if winner == self.player2 else 'égalité')
                reward = 0
                if result == 'victoire':
                    reward = int(0.2 * 100)
                elif result == 'défaite':
                    reward = int(0.1 * 100)
                if self.round_count >= 15:
                    reward *= 2
                data_manager = DataManager()
                data_manager.add_game_history({
                    'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'deck': getattr(self.player1, 'deck', []),
                    'resultat': result,
                    'tours': self.round_count,
                    'recompense': reward
                })
                if winner == self.player1:
                    self._add_log("Fin du combat : Victoire !", type_="victory")
                    for w in self.player_board_widgets:
                        w.play_sound('victory')
                    NotificationPopup("🏆 Victoire !", 3500, self).show()
                    self._fade_out()
                elif winner == self.player2:
                    self._add_log("Fin du combat : Défaite.", type_="defeat")
                    for w in self.player_board_widgets:
                        w.play_sound('defeat')
                    NotificationPopup("💀 Défaite...", 3500, self).show()
                    self._fade_out()
                else:
                    self._add_log("Fin du combat : Égalité.", type_="warning")
                    NotificationPopup("🤝 Égalité", 3500, self).show()
                    self._fade_out()
                self.next_button.setEnabled(False)
                if self.on_finish:
                    self.on_finish(self.battle, self.round_count)
                return
            self.battle.play_round()
            self.round_count += 1
            self._add_log(f"Tour {self.round_count} joué.", type_="info")
            self.update_ui()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans next_round : {e}")
            NotificationPopup(f"Erreur lors de la fin de tour : {e}", 4000, self).show()

    def _fade_out(self):
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(1200)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.start()
        self._current_anim = anim  # Correction : référence forte pour éviter le GC

    def refresh_hand(self):
        self.hand_list.clear()
        for card in self.player1.hand:
            item = QListWidgetItem(card.name)
            self.hand_list.addItem(item)
        # Feedback sonore pioche
        if hasattr(self, 'player_board_widgets') and self.player_board_widgets:
            self.player_board_widgets[0].play_sound('draw')

    def board_drag_enter(self, event):
        event.accept()
        self.player_board.set_highlight(True)

    def board_drag_leave(self, event):
        self.player_board.set_highlight(False)

    def board_drop_event(self, event):
        card_name = event.mimeData().text().split(' (')[0]
        card = next((c for c in self.player1.hand if c.name == card_name), None)
        if card:
            if getattr(card, 'cost', 0) > self.player1.mana:
                self._add_log(f"Pas assez de mana pour jouer {card.name} !")
            else:
                self.player1.play_card(card, self.battle, None)
                self._add_log(f"Vous jouez {card.name} sur le board.")
                # Feedback sonore pose carte
                if hasattr(self, 'player_board_widgets') and self.player_board_widgets:
                    self.player_board_widgets[0].play_sound('play_card')
                self.refresh_hand()
                self.update_ui()
        self.player_board.set_highlight(False)
        event.accept()

    def handle_attack(self, widget, target_unit):
        if not self.selected_attacker:
            self._add_log("Sélectionnez d'abord une unité à attaquer !", type_="warning")
            return
        # Empêche d'attaquer si l'unité est gelée
        if hasattr(self.selected_attacker, 'status_effects'):
            for eff in self.selected_attacker.status_effects:
                eff_type = eff['type'] if isinstance(eff, dict) else eff
                if eff_type == 'freeze':
                    self._add_log(f"{self.selected_attacker.name} est gelé et ne peut pas attaquer !", type_="warning")
                    return
        # Applique le bonus d'attaque temporaire du boost
        atk_bonus = 0
        if hasattr(self.selected_attacker, 'status_effects'):
            for eff in self.selected_attacker.status_effects:
                eff_type = eff['type'] if isinstance(eff, dict) else eff
                if eff_type == 'boost':
                    atk_bonus += 2  # Exemple : +2 ATK temporaire
        if atk_bonus:
            if hasattr(self.selected_attacker, 'attack'):
                self.selected_attacker.attack += atk_bonus
        self.battle.attack(self.selected_attacker, target_unit)
        widget.shake()
        widget.play_sound('attack')
        self._add_log(f"{self.selected_attacker.name} attaque {target_unit.name} !", type_="attack")
        # Retire le bonus d'attaque temporaire après l'attaque
        if atk_bonus:
            if hasattr(self.selected_attacker, 'attack'):
                self.selected_attacker.attack -= atk_bonus
        self.selected_attacker = None
        self.update_ui()

    def select_attacker(self, widget, unit):
        # Désactive le glow sur tous les widgets du board joueur
        for w in self.player_board_widgets:
            w.set_glow(False)
        widget.set_glow(True)
        self.selected_attacker = unit

    def _card_keypress(self, event, widget, unit, is_player):
        key = event.key()
        widgets = self.player_board_widgets if is_player else self.ia_board_widgets
        idx = widgets.index(widget)
        if key in (Qt.Key_Right, Qt.Key_Down):
            next_idx = (idx + 1) % len(widgets)
            widgets[next_idx].setFocus()
        elif key in (Qt.Key_Left, Qt.Key_Up):
            prev_idx = (idx - 1) % len(widgets)
            widgets[prev_idx].setFocus()
        elif key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            if is_player:
                self.select_attacker(widget, unit)
            else:
                self.handle_attack(widget, unit)

    def toggle_log_visibility(self):
        visible = self.toggle_log_button.isChecked()
        self.log.setVisible(visible)
        self.toggle_log_button.setText("Masquer le log" if visible else "Afficher le log")

    def copy_log_to_clipboard(self):
        from PyQt5.QtWidgets import QApplication
        text = '\n'.join(self.log.item(i).text() for i in range(self.log.count()) if self.log.item(i) is not None and hasattr(self.log.item(i), 'text'))
        text = '\n'.join(self.log.item(i).text() for i in range(self.log.count()))
        QApplication.clipboard().setText(text)

    def export_log_to_file(self):
        self.loading_popup = LoadingPopup("Export du log...", self)
        self.loading_popup.show()
        try:
            from PyQt5.QtWidgets import QFileDialog
            text = '\n'.join(self.log.item(i).text() for i in range(self.log.count()))
            path, _ = QFileDialog.getSaveFileName(self, "Exporter le log", "combat_log.txt", "Fichiers texte (*.txt)")
            if path:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
        finally:
            self.loading_popup.close()

    def toggle_hp_bars(self):
        try:
            self.show_hp_bars = self.toggle_hp_button.isChecked()
            self.toggle_hp_button.setText("Masquer les barres de vie" if self.show_hp_bars else "Afficher les barres de vie")
            self.update_ui()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans toggle_hp_bars : {e}")
            NotificationPopup(f"Erreur lors du switch barres de vie : {e}", 4000, self).show()

    def toggle_invert_boards(self):
        try:
            self.invert_boards = self.invert_boards_button.isChecked()
            self.update_ui()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans toggle_invert_boards : {e}")
            NotificationPopup(f"Erreur lors de l'inversion des boards : {e}", 4000, self).show()

    def toggle_daltonian_mode(self):
        try:
            self.daltonian_mode = self.daltonian_button.isChecked()
            self.update_ui()
        except Exception as e:
            log_debug(f"[ERROR] Exception dans toggle_daltonian_mode : {e}")
            NotificationPopup(f"Erreur lors du switch daltonien : {e}", 4000, self).show()

    def set_current_theme(self, theme):
        if theme == 'DARK':
            ThemeManager.apply(ThemeManager.DARK)
        elif theme == 'LIGHT':
            ThemeManager.apply(ThemeManager.LIGHT)
        else:
            ThemeManager.apply(ThemeManager.CONTRAST)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.forfeit()
            event.accept()
            return
        elif event.key() == Qt.Key_F1:
            html_content = """
            <b>Raccourcis clavier :</b><br>
            <ul>
            <li><b>Échap</b> : Abandonner le combat (ou retour au menu)</li>
            <li><b>F1</b> : Afficher cette aide</li>
            <li><b>Tab</b> : Naviguer entre les éléments</li>
            </ul>
            <b>Conseils :</b><br>
            - Cliquez ou utilisez Tab pour sélectionner vos unités et attaquer.<br>
            - Utilisez les boutons pour activer les pouvoirs ou passer le tour.<br>
            - Les barres de vie et effets sont affichés sur les cartes.<br>
            """
            dlg = HelpDialog('Aide - Combat', html_content, self)
            dlg.exec_()
            event.accept()
            return
        super().keyPressEvent(event)

    def _on_effect_expire(self, unit, effect):
        # Message, son, anim à l'expiration d'un effet
        msg = f"{effect.get('type', 'Effet')} expiré sur {getattr(unit, 'name', str(unit))}."
        self._add_log(msg, type_="info")
        for w in self.player_board_widgets + self.ia_board_widgets:
            if hasattr(w, 'name_label') and w.name_label.text().replace('<b>','').replace('</b>','') == getattr(unit, 'name', str(unit)):
                w.flash()
                w.play_sound('effect_expire')
                break
        NotificationPopup(msg, 2500, self).show()

    def _on_effect_secondary(self, unit, effect, action):
        # Feedback pour les effets secondaires à l'expiration
        if action == 'poison_expire':
            msg = f"{getattr(unit, 'name', str(unit))} subit 1 dégât de poison à l'expiration."
            self._add_log(msg, type_="attack")
            for w in self.player_board_widgets + self.ia_board_widgets:
                if hasattr(w, 'name_label') and w.name_label.text().replace('<b>','').replace('</b>','') == getattr(unit, 'name', str(unit)):
                    w.shake()
                    w.play_sound('attack')
                    break
            NotificationPopup(msg, 2500, self).show()
        elif action == 'shield_expire':
            msg = f"{getattr(unit, 'name', str(unit))} récupère 1 PV grâce au bouclier dissipé."
            self._add_log(msg, type_="activate")
            for w in self.player_board_widgets + self.ia_board_widgets:
                if hasattr(w, 'name_label') and w.name_label.text().replace('<b>','').replace('</b>','') == getattr(unit, 'name', str(unit)):
                    w.play_sound('heal')
                    w.heal_glow()
                    break
            NotificationPopup(msg, 2500, self).show()
        elif action == 'boost_expire':
            msg = f"{getattr(unit, 'name', str(unit))} perd le bonus de boost."
            self._add_log(msg, type_="info")
            for w in self.player_board_widgets + self.ia_board_widgets:
                if hasattr(w, 'name_label') and w.name_label.text().replace('<b>','').replace('</b>','') == getattr(unit, 'name', str(unit)):
                    w.play_sound('effect_expire')
                    break
            NotificationPopup(msg, 2500, self).show()
        # Ajoute d'autres actions secondaires ici si besoin

    def _on_battle_error(self, msg):
        self._add_log(msg, type_="error")
        NotificationPopup(msg, 3500, self).show() 