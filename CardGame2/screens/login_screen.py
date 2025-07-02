from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from CardGame2.data_manager import DataManager
from typing import Optional
from CardGame2.ui.components import StyledButton, LoadingPopup, HelpDialog
from PyQt5.QtGui import QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt

data_manager = DataManager()

class LoginScreen(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        self.label = QLabel("Entrez votre nom de joueur :")
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(data_manager.get_all_player_names() if hasattr(data_manager, 'get_all_player_names') else [])
        self.profile_combo.currentTextChanged.connect(self.fill_input_from_combo)
        self.input = QLineEdit()
        self.button = StyledButton("Se connecter")
        self.button.clicked.connect(self.login)
        self.create_button = StyledButton("Créer un nouveau profil")
        self.create_button.clicked.connect(self.create_profile)
        self.label.setToolTip("Entrez votre nom de joueur ou sélectionnez un profil existant.")
        self.profile_combo.setToolTip("Liste des profils existants. Sélectionnez-en un pour pré-remplir le champ.")
        self.input.setToolTip("Saisissez ici votre nom de joueur.")
        self.button.setToolTip("Se connecter avec le nom indiqué")
        self.create_button.setToolTip("Créer un nouveau profil avec le nom indiqué")
        layout.addWidget(self.label)
        layout.addWidget(self.profile_combo)
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        layout.addWidget(self.create_button)
        self.setLayout(layout)
        self.setTabOrder(self.profile_combo, self.input)
        self.setTabOrder(self.input, self.button)
        self.setTabOrder(self.button, self.create_button)
        self.profile_combo.setFocus()

    def fill_input_from_combo(self, text):
        self.input.setText(text)

    def login(self) -> None:
        self.loading_popup = LoadingPopup("Connexion...", self)
        self.loading_popup.show()
        try:
            name = self.input.text().strip()
            if name:
                data_manager.set_player_name(name)
                main_window = self.parent().parent()
                if hasattr(main_window, 'go_to_menu'):
                    try:
                        main_window.go_to_menu(name)
                    except Exception as nav_exc:
                        QMessageBox.critical(self, "Erreur navigation", f"Exception lors de la navigation : {nav_exc}")
                else:
                    QMessageBox.critical(self, "Erreur technique", "Impossible de naviguer vers le menu principal : MainWindow non trouvé ou méthode manquante.")
            else:
                QMessageBox.warning(self, "Erreur", "Veuillez entrer un nom de joueur.")
        except Exception as e:
            QMessageBox.critical(self, "Exception", f"Erreur inattendue : {e}")
        finally:
            self.loading_popup.close()

    def create_profile(self) -> None:
        self.loading_popup = LoadingPopup("Création du profil...", self)
        self.loading_popup.show()
        try:
            name = self.input.text().strip()
            if not name:
                QMessageBox.warning(self, "Erreur", "Veuillez entrer un nom de joueur.")
                return
            existing = data_manager.get_all_player_names() if hasattr(data_manager, 'get_all_player_names') else []
            if name in existing:
                QMessageBox.warning(self, "Erreur", "Ce nom de joueur existe déjà.")
                return
            data_manager.set_player_name(name)
            data_manager.reset_player_data(name) if hasattr(data_manager, 'reset_player_data') else None
            self.parent().parent().go_to_menu(name)
        finally:
            self.loading_popup.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.parent() and hasattr(self.parent(), 'stack') and hasattr(self.parent().parent(), 'main_menu'):
                self.parent().parent().stack.setCurrentWidget(self.parent().parent().main_menu)
            event.accept()
            return
        elif event.key() == Qt.Key_F1:
            html_content = """
            <b>Raccourcis clavier :</b><br>
            <ul>
            <li><b>Échap</b> : Retour à l'écran précédent</li>
            <li><b>F1</b> : Afficher cette aide</li>
            <li><b>Tab</b> : Naviguer entre les éléments</li>
            </ul>
            <b>Conseils :</b><br>
            - Sélectionnez un profil existant ou saisissez un nouveau nom.<br>
            - Cliquez sur 'Se connecter' ou appuyez sur Entrée pour valider.<br>
            - Utilisez 'Créer un nouveau profil' pour démarrer une nouvelle partie.<br>
            """
            dlg = HelpDialog('Aide - Connexion', html_content, self)
            dlg.exec_()
            event.accept()
            return
        super().keyPressEvent(event) 