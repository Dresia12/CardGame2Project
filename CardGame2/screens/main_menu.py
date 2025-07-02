from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from CardGame2.data_manager import DataManager
from PyQt5.QtWidgets import QMessageBox
from typing import Optional
from CardGame2.ui.components import StyledButton, LoadingPopup, NotificationPopup
from CardGame2.ui.theme_manager import ThemeManager
from CardGame2.ui.resources import UI_TEXTS
from CardGame2.ui.utils import print_memory_diagnostics  # type: ignore
import os

def log_debug(msg):
    with open(os.path.join(os.path.dirname(__file__), '../../debug_cardgame2.log'), 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

data_manager = DataManager()

class MainMenu(QWidget):
    def __init__(self, player_name: str, parent: Optional[QWidget] = None) -> None:
        log_debug(f"[DEBUG] MainMenu.__init__ appelé avec player_name={player_name}, parent={parent}")
        try:
            super().__init__(parent)
            self._layout = QVBoxLayout()
            # Theme selector
            self.theme_combo = StyledButton("Thème : Sombre")
            self.theme_combo.setToolTip(UI_TEXTS['theme_combo'])
            self.theme_combo.clicked.connect(self.toggle_theme)
            self.current_theme = 'DARK'
            self._layout.addWidget(self.theme_combo)
            self.label = QLabel(f"Bienvenue, {player_name} !")
            self.currency_label = QLabel(f"Monnaie : {data_manager.get_currency()} 🦙")
            self.play_button = StyledButton("Jouer")
            self.play_button.setToolTip(UI_TEXTS['play_button'])
            self.deck_button = StyledButton("Création de Deck")
            self.deck_button.setToolTip(UI_TEXTS['deck_button'])
            self.shop_button = StyledButton("Boutique")
            self.shop_button.setToolTip(UI_TEXTS['shop_button'])
            self.collection_button = StyledButton("Collection")
            self.collection_button.setToolTip(UI_TEXTS['collection_button'])
            self.profile_button = StyledButton("Changer de profil")
            self.profile_button.setToolTip(UI_TEXTS['profile_button'])
            self.logout_button = StyledButton("Retour (Déconnexion)")
            self.logout_button.setToolTip(UI_TEXTS['logout_button'])
            self._layout.addWidget(self.label)
            self._layout.addWidget(self.currency_label)
            self._layout.addWidget(self.play_button)
            self._layout.addWidget(self.deck_button)
            self._layout.addWidget(self.shop_button)
            self._layout.addWidget(self.collection_button)
            self._layout.addWidget(self.profile_button)
            self._layout.addWidget(self.logout_button)
            self.setLayout(self._layout)
            self.play_button.clicked.connect(lambda: (log_debug(f"[DEBUG] play_button cliqué pour {player_name}"), self.window().go_to_play_menu(player_name)))
            self.deck_button.clicked.connect(lambda: (log_debug(f"[DEBUG] deck_button cliqué pour {player_name}"), self.window().go_to_deck_menu(player_name)))
            self.shop_button.clicked.connect(lambda: (log_debug(f"[DEBUG] shop_button cliqué pour {player_name}"), self.window().go_to_shop_menu(player_name)))
            self.collection_button.clicked.connect(lambda: (log_debug(f"[DEBUG] collection_button cliqué pour {player_name}"), self.window().go_to_collection_menu(player_name)))
            self.profile_button.clicked.connect(lambda: (log_debug(f"[DEBUG] profile_button cliqué"), self.change_profile(), NotificationPopup("Profil changé !", 2000, self).show()))
            self.logout_button.clicked.connect(lambda: (log_debug(f"[DEBUG] logout_button cliqué"), self.return_to_login(), NotificationPopup("Déconnexion effectuée", 2000, self).show()))
            self.setFocusPolicy(1)
            ThemeManager.apply(ThemeManager.DARK)
            self.setTabOrder(self.theme_combo, self.play_button)
            self.setTabOrder(self.play_button, self.deck_button)
            self.setTabOrder(self.deck_button, self.shop_button)
            self.setTabOrder(self.shop_button, self.collection_button)
            self.setTabOrder(self.collection_button, self.profile_button)
            self.setTabOrder(self.profile_button, self.logout_button)
            self.theme_combo.setFocus()
            log_debug("[DEBUG] MainMenu.__init__ terminé sans erreur")
            # Ajout du bouton debug si mode dev
            if os.environ.get('CARDGAME2_DEBUG', '0') == '1':
                debug_btn = QPushButton('DEBUG: Mémoire')
                debug_btn.setToolTip('Afficher le nombre de widgets/layouts vivants')
                debug_btn.clicked.connect(print_memory_diagnostics)
                debug_btn.setStyleSheet('background: #222; color: #fff; border: 2px solid #0f0;')
                # Ajoute en bas à droite
                self._layout.addWidget(debug_btn)
        except Exception as e:
            log_debug(f"[ERROR] Exception dans MainMenu.__init__ : {e}")
            raise
    def return_to_login(self) -> None:
        self.window().stack.setCurrentWidget(self.window().login_screen)
    def change_profile(self):
        self.window().stack.setCurrentWidget(self.window().login_screen)
    def keyPressEvent(self, event):
        key = event.key()
        if key == 78:  # N
            self.play_button.click()
        elif key == 68:  # D
            self.deck_button.click()
        elif key == 66:  # B
            self.shop_button.click()
        elif key == 67:  # C
            self.collection_button.click()
        elif key == 82:  # R
            self.logout_button.click()
        elif key == 16777216:  # Qt.Key_Escape
            self.logout_button.click()
        elif key == 16777264:  # Qt.Key_F1
            if self.parent() and hasattr(self.parent(), 'show_help_popup'):
                self.parent().show_help_popup()
        else:
            super().keyPressEvent(event)
    def set_daltonian_mode(self, daltonian: bool):
        # À compléter : appliquer le mode daltonien aux widgets si besoin
        pass
    def get_current_theme(self):
        return self.current_theme
    def set_current_theme(self, theme):
        self.current_theme = theme
        if theme == 'DARK':
            ThemeManager.apply(ThemeManager.DARK)
            self.theme_combo.setText("Thème : Sombre")
        elif theme == 'LIGHT':
            ThemeManager.apply(ThemeManager.LIGHT)
            self.theme_combo.setText("Thème : Clair")
        else:
            ThemeManager.apply(ThemeManager.CONTRAST)
            self.theme_combo.setText("Thème : Contraste élevé")
    def toggle_theme(self):
        if self.current_theme == 'DARK':
            self.set_current_theme('LIGHT')
        elif self.current_theme == 'LIGHT':
            self.set_current_theme('CONTRAST')
        else:
            self.set_current_theme('DARK')
        # Propagate to parent/main window if possible
        if self.parent() and hasattr(self.parent(), 'set_global_theme'):
            self.parent().set_global_theme(self.current_theme) 