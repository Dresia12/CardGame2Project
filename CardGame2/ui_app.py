import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QMenuBar, QMenu, QAction, QColorDialog, QDesktopWidget, QShortcut, QDialog, QVBoxLayout, QCheckBox, QSlider, QLabel, QComboBox, QPushButton
)
from PyQt5.QtCore import QTranslator, QLocale, QPropertyAnimation
from PyQt5.QtGui import QKeySequence
from CardGame2.screens.login_screen import LoginScreen
from CardGame2.screens.main_menu import MainMenu
from CardGame2.screens.play_menu import PlayMenu
from CardGame2.screens.deck_menu import DeckMenu
from CardGame2.screens.shop_menu import ShopMenu
from CardGame2.screens.collection_menu import CollectionMenu
from CardGame2.screens.combat_screen import CombatScreen
from CardGame2.ui.theme_manager import ThemeManager
from CardGame2.ui.components import NotificationPopup, MusicManager
from CardGame2.utils.user_config import load_user_config, save_user_config
from typing import Optional

# Handler global d'exception Python
import traceback
def global_excepthook(exctype, value, tb):
    msg = f"[CRITICAL] Unhandled exception: {exctype.__name__}: {value}\n" + ''.join(traceback.format_tb(tb))
    try:
        with open(os.path.join(os.path.dirname(__file__), '../debug_cardgame2.log'), 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass
    try:
        # Affiche une popup si possible (si QApplication existe)
        app = QApplication.instance()
        if app is not None:
            NotificationPopup(f"Erreur critique : {value}", 6000).show()
    except Exception:
        pass
    # Affiche aussi sur la console
    print(msg, file=sys.stderr)

sys.excepthook = global_excepthook

def log_debug(msg):
    with open(os.path.join(os.path.dirname(__file__), '../debug_cardgame2.log'), 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

class DebugStackedWidget(QStackedWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currentChanged.connect(self._on_current_changed)
    def _on_current_changed(self, idx):
        widget = self.widget(idx)
        log_debug(f"[DEBUG] DebugStackedWidget.currentChanged: idx={idx}, widget={widget}, type={type(widget)}, id={id(widget)}")

# --- Écrans de l'application ---
class MainWindow(QMainWindow):
    def __init__(self):
        log_debug("[DEBUG] MainWindow.__init__ début")
        super().__init__()
        self.setWindowTitle("CardGame2 - PyQt5 Edition")
        screen = QDesktopWidget().screenGeometry()
        w = int(screen.width() * 0.9)
        h = int(screen.height() * 0.9)
        self.resize(w, h)
        self.setMinimumSize(1000, 700)
        self.stack = DebugStackedWidget()
        self.login_screen = LoginScreen(self.stack)
        self.stack.addWidget(self.login_screen)
        self.setCentralWidget(self.stack)
        # Menu de thème
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        theme_menu = QMenu("Thème", self)
        self.menu_bar.addMenu(theme_menu)
        action_light = QAction("Clair", self)
        action_dark = QAction("Sombre", self)
        action_contrast = QAction("Contraste élevé", self)
        action_color = QAction("Couleur principale...", self)
        theme_menu.addAction(action_light)
        theme_menu.addAction(action_dark)
        theme_menu.addAction(action_contrast)
        theme_menu.addSeparator()
        theme_menu.addAction(action_color)
        action_light.triggered.connect(lambda: ThemeManager.apply(ThemeManager.LIGHT))
        action_dark.triggered.connect(lambda: ThemeManager.apply(ThemeManager.DARK))
        action_contrast.triggered.connect(lambda: ThemeManager.apply(ThemeManager.CONTRAST))
        action_color.triggered.connect(self.choose_accent_color)
        ThemeManager.apply(ThemeManager.DARK)
        # Menu aide
        help_menu = QMenu("Aide", self)
        self.menu_bar.addMenu(help_menu)
        action_help = QAction("Aide contextuelle", self)
        help_menu.addAction(action_help)
        action_help.triggered.connect(self.show_help_popup)
        # Menu langue
        lang_menu = QMenu("Langue", self)
        self.menu_bar.addMenu(lang_menu)
        action_fr = QAction("Français", self)
        action_en = QAction("English", self)
        lang_menu.addAction(action_fr)
        lang_menu.addAction(action_en)
        action_fr.triggered.connect(lambda: self.set_language('fr'))
        action_en.triggered.connect(lambda: self.set_language('en'))
        # Menu daltonien
        daltonian_menu = QMenu("Accessibilité", self)
        self.menu_bar.addMenu(daltonian_menu)
        action_daltonian = QAction("Mode daltonien", self)
        action_daltonian.setCheckable(True)
        action_daltonian.setChecked(False)
        daltonian_menu.addAction(action_daltonian)
        self.daltonian_mode = False
        action_daltonian.triggered.connect(self.toggle_daltonian_mode)
        # Toggle grands caractères
        action_bigfont = QAction("Grands caractères", self)
        action_bigfont.setCheckable(True)
        action_bigfont.setChecked(False)
        daltonian_menu.addAction(action_bigfont)
        self.bigfont_mode = False
        action_bigfont.triggered.connect(self.toggle_bigfont_mode)
        self.translator = QTranslator()
        self.current_lang = 'fr'
        config = load_user_config()
        self.current_theme = config.get('theme', 'DARK')
        ThemeManager.apply(getattr(ThemeManager, self.current_theme, ThemeManager.DARK))
        # Musique de fond globale (Harp)
        self.music_manager = MusicManager()
        self.music_manager.ensure_music('D:/CardGameWorkspace/Music/MusicBoardHarp_V1.wav', loop=True)
        # Raccourci ESC pour menu options
        self.options_shortcut = QShortcut(QKeySequence('Esc'), self)
        self.options_shortcut.activated.connect(self.show_options_menu)
        log_debug(f"[DEBUG] MainWindow.__init__ fin, self={self}")

    def animate_transition(self, new_widget):
        log_debug(f"[DEBUG] animate_transition appelée avec new_widget={new_widget}")
        old_widget = self.stack.currentWidget()
        log_debug(f"[DEBUG] Widget courant avant transition : {old_widget}")
        if old_widget:
            anim = QPropertyAnimation(old_widget, b"windowOpacity")
            anim.setDuration(250)
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            def on_anim_finished():
                log_debug("[DEBUG] Animation de fade-out terminée, appel _show_new_widget_with_fade")
                self._show_new_widget_with_fade(new_widget)
            anim.finished.connect(on_anim_finished)
            anim.start()
            self._current_anim = anim
            log_debug("[DEBUG] Animation de fade-out lancée")
        else:
            log_debug("[DEBUG] Pas d'ancien widget, appel direct _show_new_widget_with_fade")
            self._show_new_widget_with_fade(new_widget)

    def _show_new_widget_with_fade(self, new_widget):
        log_debug(f"[DEBUG] _show_new_widget_with_fade appelée avec new_widget={new_widget}")
        log_debug(f"[DEBUG] Avant setCurrentWidget : stack.currentWidget={self.stack.currentWidget()} (type={type(self.stack.currentWidget())}, id={id(self.stack.currentWidget())})")
        self.stack.setCurrentWidget(new_widget)
        log_debug(f"[DEBUG] Après setCurrentWidget : stack.currentWidget={self.stack.currentWidget()} (type={type(self.stack.currentWidget())}, id={id(self.stack.currentWidget())})")
        new_widget.setWindowOpacity(0.0)
        anim = QPropertyAnimation(new_widget, b"windowOpacity")
        anim.setDuration(250)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start()
        self._current_anim = anim
        log_debug("[DEBUG] Animation de fade-in lancée")

    def go_to_menu(self, player_name):
        # Remet la musique Harp hors combat
        self.music_manager.ensure_music('D:/CardGameWorkspace/Music/MusicBoardHarp_V1.wav', loop=True)
        log_debug(f"[DEBUG] go_to_menu appelé avec player_name={player_name}")
        # Vérifie si un MainMenu existe déjà dans le stack
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if isinstance(widget, MainMenu) and getattr(widget, 'player_name', None) == player_name:
                self.animate_transition(widget)
                self.player_name = player_name
                widget.set_current_theme(self.current_theme)
                log_debug(f"[DEBUG] Widget courant après setCurrentWidget : {self.stack.currentWidget()} (type={type(self.stack.currentWidget())}, id={id(self.stack.currentWidget())})")
                log_debug(f"[DEBUG] MainMenu visible ? {self.menu.isVisible()}")
                return
        # Sinon, on crée un nouveau MainMenu
        self.menu = MainMenu(player_name, self.stack)
        self.menu.player_name = player_name  # Ajoute cet attribut si besoin
        self.stack.addWidget(self.menu)
        self.stack.setCurrentWidget(self.menu)
        self.animate_transition(self.menu)
        self.player_name = player_name
        self.menu.set_current_theme(self.current_theme)
        log_debug(f"[DEBUG] Widget courant après setCurrentWidget : {self.stack.currentWidget()} (type={type(self.stack.currentWidget())}, id={id(self.stack.currentWidget())})")
        log_debug(f"[DEBUG] MainMenu visible ? {self.menu.isVisible()}")

    def go_to_play_menu(self, player_name):
        self.music_manager.ensure_music('D:/CardGameWorkspace/Music/MusicBoardHarp_V1.wav', loop=True)
        log_debug(f"[DEBUG] go_to_play_menu appelé avec player_name={player_name}")
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if isinstance(widget, PlayMenu) and getattr(widget, 'player_name', None) == player_name:
                self.animate_transition(widget)
                if hasattr(widget, 'set_current_theme'):
                    widget.set_current_theme(self.current_theme)
                return
        self.play_menu = PlayMenu(player_name, self.stack)
        self.play_menu.player_name = player_name
        self.stack.addWidget(self.play_menu)
        self.animate_transition(self.play_menu)
        if hasattr(self.play_menu, 'set_current_theme'):
            self.play_menu.set_current_theme(self.current_theme)

    def go_to_deck_menu(self, player_name):
        self.music_manager.ensure_music('D:/CardGameWorkspace/Music/MusicBoardHarp_V1.wav', loop=True)
        log_debug(f"[DEBUG] go_to_deck_menu appelé avec player_name={player_name}")
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if isinstance(widget, DeckMenu) and getattr(widget, 'player_name', None) == player_name:
                self.animate_transition(widget)
                if hasattr(widget, 'set_current_theme'):
                    widget.set_current_theme(self.current_theme)
                return
        self.deck_menu = DeckMenu(player_name, self.stack)
        self.deck_menu.player_name = player_name
        self.stack.addWidget(self.deck_menu)
        self.animate_transition(self.deck_menu)
        if hasattr(self.deck_menu, 'set_current_theme'):
            self.deck_menu.set_current_theme(self.current_theme)

    def go_to_shop_menu(self, player_name):
        self.music_manager.ensure_music('D:/CardGameWorkspace/Music/MusicBoardHarp_V1.wav', loop=True)
        log_debug(f"[DEBUG] go_to_shop_menu appelé avec player_name={player_name}")
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if isinstance(widget, ShopMenu) and getattr(widget, 'player_name', None) == player_name:
                self.animate_transition(widget)
                if hasattr(widget, 'set_current_theme'):
                    widget.set_current_theme(self.current_theme)
                return
        self.shop_menu = ShopMenu(player_name, self.stack)
        self.shop_menu.player_name = player_name
        self.stack.addWidget(self.shop_menu)
        self.animate_transition(self.shop_menu)
        if hasattr(self.shop_menu, 'set_current_theme'):
            self.shop_menu.set_current_theme(self.current_theme)

    def go_to_collection_menu(self, player_name):
        self.music_manager.ensure_music('D:/CardGameWorkspace/Music/MusicBoardHarp_V1.wav', loop=True)
        log_debug(f"[DEBUG] go_to_collection_menu appelé avec player_name={player_name}")
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            if isinstance(widget, CollectionMenu) and getattr(widget, 'player_name', None) == player_name:
                self.animate_transition(widget)
                if hasattr(widget, 'set_current_theme'):
                    widget.set_current_theme(self.current_theme)
                return
        self.collection_menu = CollectionMenu(player_name, self.stack)
        self.collection_menu.player_name = player_name
        self.stack.addWidget(self.collection_menu)
        self.animate_transition(self.collection_menu)
        if hasattr(self.collection_menu, 'set_current_theme'):
            self.collection_menu.set_current_theme(self.current_theme)

    def go_to_combat_screen(self, player1, player2, battle, on_finish=None):
        # Change la musique pour le combat
        self.music_manager.ensure_music('D:/CardGameWorkspace/Music/MusicBoard.wav', loop=True)
        self.combat_screen = CombatScreen(player1, player2, battle, self.stack, on_finish)
        self.stack.addWidget(self.combat_screen)
        self.animate_transition(self.combat_screen)
        if hasattr(self.combat_screen, 'set_current_theme'):
            self.combat_screen.set_current_theme(self.current_theme)

    def choose_accent_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            ThemeManager.set_accent_color(color.name())

    def show_help_popup(self):
        popup = NotificationPopup("Utilisez les menus pour naviguer, personnalisez vos decks, et ouvrez des boosters pour enrichir votre collection !", duration=4000, parent=self)
        popup.move(self.geometry().center() - popup.rect().center())
        popup.show()

    def set_language(self, lang):
        if lang == self.current_lang:
            return
        if lang == 'en':
            self.translator.load('en.qm')  # Fichier de traduction à générer
            QApplication.instance().installTranslator(self.translator)
        else:
            QApplication.instance().removeTranslator(self.translator)
        self.current_lang = lang
        # Optionnel : rafraîchir les textes des écrans si besoin

    def toggle_daltonian_mode(self, checked):
        self.daltonian_mode = checked
        # Propager à tous les écrans déjà instanciés
        for attr in ["menu", "play_menu", "deck_menu", "shop_menu", "collection_menu"]:
            if hasattr(self, attr):
                screen = getattr(self, attr)
                if hasattr(screen, "set_daltonian_mode"):
                    screen.set_daltonian_mode(self.daltonian_mode)
        # Pour l'écran de combat, il faut le gérer à l'instanciation

    def toggle_bigfont_mode(self, checked):
        self.bigfont_mode = checked
        if checked:
            self.setStyleSheet("* { font-size: 22px !important; }")
        else:
            self.setStyleSheet("")

    def set_global_theme(self, theme):
        self.current_theme = theme
        if theme == 'DARK':
            ThemeManager.apply(ThemeManager.DARK)
        elif theme == 'LIGHT':
            ThemeManager.apply(ThemeManager.LIGHT)
        else:
            ThemeManager.apply(ThemeManager.CONTRAST)
        # Save user preference
        config = load_user_config()
        config['theme'] = theme
        save_user_config(config)
        # Propagate to current screen if possible
        current = self.stack.currentWidget()
        if hasattr(current, 'set_current_theme'):
            current.set_current_theme(theme)

    def get_global_theme(self):
        return self.current_theme

    def show_options_menu(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Options")
        layout = QVBoxLayout()
        # Musique/sons
        music_box = QCheckBox("Musique de fond")
        music_box.setChecked(not self.music_manager.is_muted())
        music_box.stateChanged.connect(lambda state: self.music_manager.toggle_mute())
        layout.addWidget(music_box)
        sound_box = QCheckBox("Effets sonores")
        sound_box.setChecked(True)
        layout.addWidget(sound_box)
        # Volume
        layout.addWidget(QLabel("Volume musique"))
        music_slider = QSlider(Qt.Horizontal)
        music_slider.setMinimum(0)
        music_slider.setMaximum(100)
        music_slider.setValue(100)
        music_slider.valueChanged.connect(lambda v: self.music_manager._player.setVolume(v))
        layout.addWidget(music_slider)
        # Vitesse d'animation
        layout.addWidget(QLabel("Vitesse d'animation"))
        anim_slider = QSlider(Qt.Horizontal)
        anim_slider.setMinimum(1)
        anim_slider.setMaximum(5)
        anim_slider.setValue(3)
        layout.addWidget(anim_slider)
        # Affichage description cartes
        desc_box = QCheckBox("Afficher la description des cartes")
        desc_box.setChecked(True)
        layout.addWidget(desc_box)
        # Affichage compact/détaillé
        compact_box = QCheckBox("Affichage compact des cartes")
        compact_box.setChecked(False)
        layout.addWidget(compact_box)
        # Mode nuit/jour
        mode_combo = QComboBox()
        mode_combo.addItems(["Nuit", "Jour", "Contraste élevé"])
        layout.addWidget(QLabel("Mode d'affichage"))
        layout.addWidget(mode_combo)
        # Police/couleurs daltoniens
        font_combo = QComboBox()
        font_combo.addItems(["Standard", "Dyslexie", "Daltonien"])
        layout.addWidget(QLabel("Police spéciale"))
        layout.addWidget(font_combo)
        # Langue
        lang_combo = QComboBox()
        lang_combo.addItems(["Français", "English"])
        layout.addWidget(QLabel("Langue du jeu"))
        layout.addWidget(lang_combo)
        # Aide/règles
        help_btn = QPushButton("Aide / Règles")
        layout.addWidget(help_btn)
        # Historique
        histo_btn = QPushButton("Historique des actions")
        layout.addWidget(histo_btn)
        # Autopass
        autopass_box = QCheckBox("Autopass (passer automatiquement si aucune action possible)")
        autopass_box.setChecked(False)
        layout.addWidget(autopass_box)
        # Réseau (placeholder)
        layout.addWidget(QLabel("--- Réseau (à venir) ---"))
        net_box = QCheckBox("Activer le mode en ligne (non disponible)")
        net_box.setChecked(False)
        net_box.setEnabled(False)
        layout.addWidget(net_box)
        chat_box = QCheckBox("Activer le chat (non disponible)")
        chat_box.setChecked(False)
        chat_box.setEnabled(False)
        layout.addWidget(chat_box)
        # Bouton fermer
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.setLayout(layout)
        dlg.exec_()

def launch_ui_for_test():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app, window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 