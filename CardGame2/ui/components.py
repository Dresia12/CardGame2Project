from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel, QFrame, QDialog, QHBoxLayout, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect, QProgressBar
from PyQt5.QtCore import QSize, QPropertyAnimation, Qt, QTimer, QEasingCurve, QPoint
from PyQt5.QtGui import QPixmap, QColor, QPalette
from typing import Optional
from PyQt5 import QtCore
from PyQt5.QtMultimedia import QSoundEffect, QMediaPlayer, QMediaContent
import os
from CardGame2.models.hero import Hero

class StyledButton(QPushButton):
    def __init__(self, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 16px;
                padding: 8px 16px;
                border-radius: 8px;
                background: #1976d2;
                color: #fff;
                border: 2px solid #1976d2;
                transition: box-shadow 0.2s, background 0.2s;
            }
            QPushButton:hover {
                background: #2196f3;
                box-shadow: 0 0 16px 4px #1976d2;
                border: 2px solid #00e676;
            }
            QPushButton:focus {
                background: #e3f2fd;
                color: #1976d2;
                border: 3px solid #ffae00;
                box-shadow: 0 0 0 4px #ffea00, 0 0 24px 6px #00e676;
                outline: none;
            }
        """)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def enterEvent(self, event):
        self.setStyleSheet(self.styleSheet() + "\nbackground-color: #2196f3; box-shadow: 0 0 16px 4px #1976d2; border: 2px solid #00e676;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        base_style = self.styleSheet().split('\n')[0]
        self.setStyleSheet(base_style)
        super().leaveEvent(event)

    def focusInEvent(self, event):
        self.setStyleSheet(self.styleSheet() + "\nbackground-color: #e3f2fd; color: #1976d2; border: 2px solid #00e676; box-shadow: 0 0 24px 6px #00e676;")
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        base_style = self.styleSheet().split('\n')[0]
        self.setStyleSheet(base_style)
        super().focusOutEvent(event)

def make_styled_button(
    text: str,
    style: str = "",
    tooltip: str = "",
    on_click=None,
    checkable: bool = False,
    checked: bool = False,
    parent=None
) -> StyledButton:
    btn = StyledButton(text, parent=parent)
    if style:
        btn.setStyleSheet(style)
    if tooltip:
        btn.setToolTip(tooltip)
    if on_click:
        btn.clicked.connect(on_click)
    btn.setCheckable(checkable)
    if checkable:
        btn.setChecked(checked)
    return btn

class StatsPanel(QWidget):
    def __init__(self, title: str, stats: dict, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.title = title
        self._layout = QVBoxLayout()
        self.title_label = QLabel(f"<b>{title}</b>")
        self._layout.addWidget(self.title_label)
        self.stat_labels = []
        for key, value in stats.items():
            lbl = QLabel(f"{key} : {value}")
            self._layout.addWidget(lbl)
            self.stat_labels.append(lbl)
        self.setLayout(self._layout)
        self.setToolTip(self._make_tooltip(stats))

    def set_stats(self, stats: dict):
        # Supprime les anciens labels de stats
        for lbl in self.stat_labels:
            self._layout.removeWidget(lbl)
            lbl.deleteLater()
        self.stat_labels = []
        # Ajoute les nouveaux labels
        for key, value in stats.items():
            lbl = QLabel(f"{key} : {value}")
            self._layout.addWidget(lbl)
            self.stat_labels.append(lbl)
        self.setToolTip(self._make_tooltip(stats))

    def _make_tooltip(self, stats: dict) -> str:
        if not stats or list(stats.keys()) == ['-']:
            return "Aucune statistique disponible."
        return "\n".join(f"{k} : {v}" for k, v in stats.items())

class CardWidget(QFrame):
    clicked = QtCore.pyqtSignal()

    def __init__(self, name: str, card_type: str, rarity: str, cost: int, attack: Optional[int] = None, health: Optional[int] = None, description: str = "", illustration: Optional[QPixmap] = None, parent: Optional[QWidget] = None) -> None:
        # Patch : si name est un objet Hero, on adapte l'affichage
        if isinstance(name, Hero):
            hero = name
            name = hero.name
            card_type = getattr(hero, 'card_type', 'HÉROS')
            if isinstance(card_type, str):
                card_type = card_type
            else:
                card_type = getattr(card_type, 'name', 'HÉROS')
            rarity = getattr(hero, 'rarity', 'SPECIAL')
            if isinstance(rarity, str):
                rarity = rarity
            else:
                rarity = getattr(rarity, 'name', 'SPECIAL')
            cost = getattr(hero, 'base_defense', 0)
            attack = getattr(hero, 'base_attack', None)
            health = getattr(hero, 'base_hp', None)
            description = getattr(hero, 'ability_description', '')
        super().__init__(parent)
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(2)
        self.setFixedSize(180, 260)
        self.setStyleSheet("background-color: #f8f8f2; border-radius: 12px;")
        layout = QVBoxLayout()
        # Illustration fictive
        self.illu_label = QLabel()
        self.illu_label.setFixedSize(160, 80)
        if illustration:
            self.illu_label.setPixmap(illustration.scaled(160, 80, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
        else:
            pix = QPixmap(160, 80)
            pix.fill(QColor('#bdbdbd'))
            self.illu_label.setPixmap(pix)
        layout.addWidget(self.illu_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        # Nom
        self.name_label = QLabel(f"<b>{name}</b>")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)
        # Type, rareté, coût
        self.info_label = QLabel(f"{card_type} | {rarity} | Coût: {cost}")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        # ATK/PV si unité
        if attack is not None and health is not None:
            self.stats_label = QLabel(f"ATK: {attack}  PV: {health}")
            self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.stats_label)
        # Description
        if description:
            self.desc_label = QLabel(f"<i>{description}</i>")
            self.desc_label.setWordWrap(True)
            layout.addWidget(self.desc_label)
        self.setLayout(layout)
        # Animation d'apparition (zoom)
        self._appear_anim = QPropertyAnimation(self, b"geometry")
        self._appear_anim.setDuration(320)
        self._appear_anim.setEasingCurve(QEasingCurve.OutBack)
        self._appear_anim.setStartValue(self.geometry().adjusted(self.width()//2, self.height()//2, -self.width()//2, -self.height()//2))
        self._appear_anim.setEndValue(self.geometry())
        def start_anim():
            self._appear_anim.start()
        QTimer.singleShot(10, lambda: start_anim())
        # Animation de survol
        self._hover_anim = QPropertyAnimation(self, b"windowOpacity")
        self.setMouseTracking(True)
        # Glow effect
        self._glow_effect = None
        self._glow_enabled = False
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self._focus_anim = QPropertyAnimation(self, b"styleSheet")
        self._update_tooltip(name, card_type, rarity, cost, attack, health, description)

    def set_glow(self, enabled: bool, color: str = '#00e676'):
        if enabled and not self._glow_enabled:
            effect = QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(32)
            effect.setColor(QColor(color))
            effect.setOffset(0, 0)
            self.setGraphicsEffect(effect)
            self._glow_effect = effect
            self._glow_enabled = True
        elif not enabled and self._glow_enabled:
            self.setGraphicsEffect(None)
            self._glow_effect = None
            self._glow_enabled = False

    def enterEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setDuration(150)
        self._hover_anim.setStartValue(1.0)
        self._hover_anim.setEndValue(0.85)
        self._hover_anim.start()
        self.set_glow(True, color="#1976d2")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover_anim.stop()
        self._hover_anim.setDuration(150)
        self._hover_anim.setStartValue(self.windowOpacity())
        self._hover_anim.setEndValue(1.0)
        self._hover_anim.start()
        self.set_glow(False)
        super().leaveEvent(event)

    def shake(self):
        """Anime une secousse horizontale rapide (attaque)."""
        anim = QPropertyAnimation(self, b"pos")
        anim.setDuration(180)
        anim.setKeyValueAt(0, self.pos())
        anim.setKeyValueAt(0.2, self.pos() + QPoint(-10, 0))
        anim.setKeyValueAt(0.5, self.pos() + QPoint(10, 0))
        anim.setKeyValueAt(0.8, self.pos() + QPoint(-10, 0))
        anim.setKeyValueAt(1, self.pos())
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.start()

    def set_aura(self, enabled: bool, color: str = '#ffd600', daltonian_mode: bool = False):
        """Affiche une aura colorée autour de la carte (effet spécial/statut)."""
        if enabled:
            effect = QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(64)
            # Si mode daltonien, on modifie la couleur pour plus de contraste
            if daltonian_mode:
                # On force la couleur à un contraste élevé (ex: orange ou turquoise)
                effect.setColor(QColor('#ff9800'))
            else:
                effect.setColor(QColor(color))
            effect.setOffset(0, 0)
            self.setGraphicsEffect(effect)
        else:
            self.setGraphicsEffect(None)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def set_effect_icons(self, effects: list):
        """Affiche des icônes d'effets spéciaux en overlay en haut à droite, avec la durée si présente."""
        # Supprime les anciens overlays
        if hasattr(self, '_effect_icons'):
            for icon in self._effect_icons:
                icon.setParent(None)
        self._effect_icons = []
        icon_map = {
            'boost': ('⚡', 'Boost : +ATK temporaire'),
            'poison': ('☠️', 'Poison : perd des PV chaque tour'),
            'shield': ('🛡️', 'Bouclier : réduit les dégâts'),
            'freeze': ('❄️', 'Gel : ne peut pas attaquer'),
            'burn': ('🔥', 'Brûlure : perd 1 PV par tour'),
        }
        x_offset = self.width() - 32
        y_offset = 4
        for i, eff in enumerate(effects):
            eff_type = eff['type'] if isinstance(eff, dict) else eff
            duration = eff.get('duration', None) if isinstance(eff, dict) else None
            if eff_type in icon_map:
                icon, tooltip = icon_map[eff_type]
                text = f"{icon}{duration}" if duration and duration > 1 else icon
                lbl = QLabel(text, self)
                lbl.setStyleSheet("font-size: 22px; background: transparent;")
                lbl.setToolTip(tooltip + (f" (reste {duration} tours)" if duration else ""))
                lbl.move(x_offset, y_offset + i*24)
                lbl.show()
                self._effect_icons.append(lbl)
        # Aura spéciale pour brûlure
        if any((isinstance(eff, dict) and eff.get('type') == 'burn') or eff == 'burn' for eff in effects):
            self.set_aura(True, color='#ff5722')  # orange/rouge
        else:
            self.set_aura(False)

    def flash(self):
        """Anime un flash blanc rapide sur la carte (ex: expiration d'effet)."""
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(220)
        anim.setStartValue(1.0)
        anim.setKeyValueAt(0.2, 0.2)
        anim.setKeyValueAt(0.8, 0.2)
        anim.setEndValue(1.0)
        anim.start()

    def play_sound(self, sound_name: str):
        """Joue un son court selon l'événement (attaque, effet, etc.)."""
        sound_map = {
            'attack': 'attack.wav',
            'heal': 'heal.wav',
            'effect_expire': 'effect_expire.wav',
            'victory': 'victory.wav',
            'defeat': 'defeat.wav',
        }
        if sound_name in sound_map:
            effect = QSoundEffect(self)
            effect.setSource(QtCore.QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), 'sounds', sound_map[sound_name])))
            effect.setVolume(0.7)
            effect.play()

    def heal_glow(self):
        """Anime une lueur verte rapide sur la carte (soin)."""
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(48)
        effect.setColor(QColor('#00e676'))
        effect.setOffset(0, 0)
        self.setGraphicsEffect(effect)
        QTimer.singleShot(350, lambda: self.setGraphicsEffect(None))

    def set_effects_tooltip(self, effects: list):
        """Affiche un tooltip global listant tous les effets actifs sur la carte."""
        if not effects:
            self.setToolTip("")
            return
        lines = []
        for eff in effects:
            if isinstance(eff, dict):
                t = eff.get('type', str(eff))
                d = eff.get('duration', None)
                if d:
                    lines.append(f"{t} ({d} tours)")
                else:
                    lines.append(str(t))
            else:
                lines.append(str(eff))
        self.setToolTip("Effets actifs :\n" + "\n".join(lines))

    def focusInEvent(self, event):
        self.set_glow(True, color="#00e676")
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.set_glow(False)
        super().focusOutEvent(event)

    def set_target_highlight(self, enabled: bool):
        """Affiche une bordure animée rouge si la carte est la cible d'une attaque."""
        if enabled:
            self.setStyleSheet(self.styleSheet() + "\nborder: 3px solid #ff1744; box-shadow: 0 0 8px #ff1744;")
        else:
            base_style = self.styleSheet().split('\n')[0]
            self.setStyleSheet(base_style)

    def _update_tooltip(self, name, card_type, rarity, cost, attack, health, description):
        tip = f"Nom : {name}\nType : {card_type}\nRareté : {rarity}\nCoût : {cost}"
        if attack is not None and health is not None:
            tip += f"\nATK : {attack}  PV : {health}"
        if description:
            tip += f"\nDescription : {description}"
        self.setToolTip(tip)

class DeckPreviewPanel(QWidget):
    def __init__(self, deck: dict, base_cards: list, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        # Héros
        hero = deck.get("hero")
        if hero:
            layout.addWidget(QLabel("<b>Héros</b>"))
            # Récupère les stats personnalisées si présentes
            base_hp = hero.get("base_hp", 0)
            base_attack = hero.get("base_attack", 0)
            base_defense = hero.get("base_defense", 0)
            hp_bonus = 0
            atk_bonus = 0
            def_bonus = 0
            passives = []
            if "customization" in hero:
                custom = hero["customization"]
                hp_bonus = custom.get("hp_level", 0) * 5
                atk_bonus = custom.get("attack_level", 0) * 2
                def_bonus = custom.get("defense_level", 0) * 2
                passives = custom.get("passives", [])
            total_hp = base_hp + hp_bonus
            total_atk = base_attack + atk_bonus
            total_def = base_defense + def_bonus
            desc = f"PV: {total_hp}  ATK: {total_atk}  DEF: {total_def}"
            if passives:
                desc += "\nPassifs: " + ", ".join(passives)
            layout.addWidget(CardWidget(hero["name"], "HÉROS", "-", 0, total_atk, total_hp, desc))
        # Unités
        units = deck.get("units", [])
        if units:
            layout.addWidget(QLabel("<b>Unités</b>"))
            for u_name in units:
                card = next((c for c in base_cards if c.name == u_name), None)
                if card:
                    layout.addWidget(CardWidget(card.name, "UNITÉ", getattr(card, 'rarity', '-'), getattr(card, 'cost', 0), getattr(card, 'attack', None), getattr(card, 'health', None), getattr(card, 'description', '')))
        # Autres cartes
        cards = deck.get("cards", [])
        if cards:
            layout.addWidget(QLabel(f"<b>Autres cartes</b> ({len(cards)})"))
        self.setLayout(layout)

class NotificationPopup(QDialog):
    def __init__(self, message: str, duration: int = 2000, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(False)
        layout = QHBoxLayout()
        label = QLabel(message)
        label.setStyleSheet("background: #23272e; color: #f8f8f2; border-radius: 8px; padding: 12px 24px; font-size: 16px;")
        layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(label)
        layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.setLayout(layout)
        self.adjustSize()
        QTimer.singleShot(duration, self.close)
    def mousePressEvent(self, event):
        self.close()
        super().mousePressEvent(event)

class HealthBarWidget(QWidget):
    def __init__(self, current: int, maximum: int, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.bar = QProgressBar(self)
        self.bar.setMinimum(0)
        self.bar.setMaximum(maximum)
        self.bar.setValue(current)
        self.bar.setTextVisible(True)
        self.bar.setFormat(f"PV : {current}/{maximum}")
        self.bar.setStyleSheet("QProgressBar { border: 1px solid #222; border-radius: 6px; background: #eee; height: 16px; } QProgressBar::chunk { background: #43a047; border-radius: 6px; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.bar)

    def set_health(self, current: int, maximum: int):
        self.bar.setMaximum(maximum)
        self.bar.setValue(current)
        self.bar.setFormat(f"PV : {current}/{maximum}")

class LoadingPopup(QDialog):
    def __init__(self, message: str = "Chargement...", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        layout = QHBoxLayout()
        label = QLabel(message)
        label.setStyleSheet("background: #23272e; color: #f8f8f2; border-radius: 8px; padding: 16px 32px; font-size: 18px;")
        spinner = QLabel("⏳")
        spinner.setStyleSheet("font-size: 28px; margin-right: 16px;")
        layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addWidget(spinner)
        layout.addWidget(label)
        layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.setLayout(layout)
        self.adjustSize()
    def mousePressEvent(self, event):
        self.close()
        super().mousePressEvent(event)

class HelpDialog(QDialog):
    def __init__(self, title: str, html_content: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        layout = QVBoxLayout()
        label = QLabel(html_content)
        label.setWordWrap(True)
        layout.addWidget(label)
        close_btn = StyledButton("Fermer")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)
    def mousePressEvent(self, event):
        self.accept()
        super().mousePressEvent(event)

class BoosterOpenDialog(QDialog):
    """Fenêtre d'ouverture animée de booster façon Hearthstone."""
    def __init__(self, cards, rarity_color_map, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ouverture du booster")
        # Patch robustesse : filtrer/convertir les str
        self.cards = []
        for c in cards:
            if isinstance(c, str):
                print(f"[ERROR] BoosterOpenDialog: carte str détectée : {c}")
                # Placeholder : carte inconnue
                self.cards.append(Hero(c, 1000, 50, 0))
            else:
                self.cards.append(c)
        self.revealed = [False] * len(self.cards)
        self.rarity_color_map = rarity_color_map
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        title = QLabel("<b>Ouverture du booster !</b>")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        self.card_widgets = []
        cards_layout = QHBoxLayout()
        for idx, card in enumerate(self.cards):
            card_widget = CardBackWidget(card, idx, self.rarity_color_map)
            card_widget.flipped.connect(self._on_card_flipped)
            self.card_widgets.append(card_widget)
            cards_layout.addWidget(card_widget)
        layout.addLayout(cards_layout)
        self.flip_all_btn = StyledButton("Tout retourner")
        self.flip_all_btn.clicked.connect(self.flip_all)
        layout.addWidget(self.flip_all_btn)
        self.setLayout(layout)
        self.setMinimumWidth(100 * len(self.cards) + 60)

    def _on_card_flipped(self, idx):
        self.revealed[idx] = True
        if all(self.revealed):
            self.flip_all_btn.setDisabled(True)

    def flip_all(self):
        for idx, widget in enumerate(self.card_widgets):
            if not self.revealed[idx]:
                widget.flip()
        self.flip_all_btn.setDisabled(True)

class CardBackWidget(QWidget):
    """Widget carte à retourner (face cachée puis visible)."""
    flipped = QtCore.pyqtSignal(int)
    def __init__(self, card, idx, rarity_color_map, parent=None):
        super().__init__(parent)
        self.card = card
        self.idx = idx
        self.rarity_color_map = rarity_color_map
        self.is_flipped = False
        self._setup_ui()
        # Patch robustesse : couleur par défaut si str
        if hasattr(self.card, 'rarity') and hasattr(self.card.rarity, 'name'):
            self._aura_color = self.rarity_color_map.get(self.card.rarity.name, '#ffd600')
        else:
            self._aura_color = '#ffd600'
        self._aura_strong = self._accentuate_color(self._aura_color)

    def _setup_ui(self):
        stack = QVBoxLayout(self)
        self.back = QLabel()
        pix = QPixmap(80, 120)
        pix.fill(QColor('#23272e'))
        self.back.setPixmap(pix)
        self.back.setStyleSheet("border-radius: 10px; border: 2px solid #888;")
        # Patch robustesse : CardWidget placeholder si str
        if isinstance(self.card, str):
            print(f"[ERROR] CardBackWidget: carte str détectée : {self.card}")
            self.front = CardWidget(self.card, 'INCONNUE', 'SPECIAL', 0)
        else:
            self.front = CardWidget(
                self.card.name, getattr(self.card.card_type, 'name', 'INCONNUE'), getattr(self.card.rarity, 'name', 'SPECIAL'), getattr(self.card, 'cost', 0),
                getattr(self.card, 'attack', None), getattr(self.card, 'health', None), getattr(self.card, 'description', '')
            )
        self.front.setVisible(False)
        stack.addWidget(self.back)
        stack.addWidget(self.front)
        self.setLayout(stack)
        self.setFixedSize(90, 130)

    def mousePressEvent(self, event):
        if not self.is_flipped:
            self.flip()
            self.flipped.emit(self.idx)
        super().mousePressEvent(event)

    def flip(self):
        self.back.setVisible(False)
        self.front.setVisible(True)
        self.front.set_aura(True, self._aura_color)
        self.is_flipped = True

    def enterEvent(self, event):
        if self.is_flipped:
            # Aura plus forte au survol
            self.front.set_aura(True, self._aura_strong, daltonian_mode=False)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.is_flipped:
            # Aura normale quand la souris quitte
            self.front.set_aura(True, self._aura_color, daltonian_mode=False)
        super().leaveEvent(event)

    def _accentuate_color(self, color):
        # Accentue la couleur (plus saturée/plus lumineuse)
        c = QColor(color)
        h, s, v, a = c.getHsv()
        s = min(255, int(s * 1.2 + 40))
        v = min(255, int(v * 1.15 + 30))
        return QColor.fromHsv(h, s, v, a).name()

class MusicManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._player = QMediaPlayer()
            cls._instance._current_path = None
            cls._instance._loop = True
            cls._instance._muted = False
            cls._instance._player.mediaStatusChanged.connect(cls._instance._on_status_changed)
        return cls._instance

    def play_music(self, path: str, loop: bool = True):
        # Ne relance pas si la même musique est déjà en cours
        if self._current_path == path and self._player.state() == QMediaPlayer.State.PlayingState:
            print(f"[MusicManager] play_music: déjà en cours: {path}")
            return
        print(f"[MusicManager] play_music: {path} (loop={loop})")
        self._current_path = path
        self._loop = loop
        url = QMediaContent(QtCore.QUrl.fromLocalFile(path))
        self._player.setMedia(url)
        self._player.setVolume(100)
        self._player.setMuted(self._muted)
        self._player.play()
        QTimer.singleShot(500, self._check_playing)

    def ensure_music(self, path: str, loop: bool = True):
        # Ne relance que si la musique n'est pas déjà celle demandée
        if self._current_path != path or self._player.state() != QMediaPlayer.State.PlayingState:
            self.play_music(path, loop=loop)

    def _check_playing(self) -> None:
        if self._player.state() != QMediaPlayer.State.PlayingState:
            print(f"[MusicManager] Erreur : la musique '{self._current_path}' n'a pas pu être lue.")
            NotificationPopup(f"Erreur : la musique '{os.path.basename(self._current_path)}' n'a pas pu être lue.", 4000).show()

    def stop_music(self):
        print(f"[MusicManager] stop_music")
        self._player.stop()
        self._current_path = None

    def toggle_mute(self):
        self._muted = not self._muted
        self._player.setMuted(self._muted)
        print(f"[MusicManager] Mute: {self._muted}")

    def is_muted(self):
        return self._muted

    def _on_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia and self._loop and self._current_path:
            self._player.setPosition(0)
            self._player.play() 