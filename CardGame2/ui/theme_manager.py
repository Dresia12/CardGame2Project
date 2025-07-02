from PyQt5.QtWidgets import QApplication

class ThemeManager:
    LIGHT = """
        QWidget { background-color: #f8f8f2; color: #23272e; }
        QPushButton, QComboBox, QListWidget, QLineEdit {
            background-color: #e0e0e0; color: #23272e; border-radius: 8px;
        }
        QPushButton:hover { background-color: #bdbdbd; }
    """
    DARK = """
        QWidget { background-color: #23272e; color: #f8f8f2; }
        QPushButton, QComboBox, QListWidget, QLineEdit {
            background-color: #44475a; color: #f8f8f2; border-radius: 8px;
        }
        QPushButton:hover { background-color: #6272a4; }
    """
    CONTRAST = """
        QWidget { background-color: #000; color: #fff; }
        QPushButton, QComboBox, QListWidget, QLineEdit {
            background-color: #fff; color: #000; border-radius: 8px;
        }
        QPushButton:hover { background-color: #ff0; color: #000; }
    """
    @staticmethod
    def apply(theme: str):
        app = QApplication.instance()
        if app and hasattr(app, 'setStyleSheet'):
            app.setStyleSheet(theme)
    @staticmethod
    def set_accent_color(color: str):
        app = QApplication.instance()
        if app and hasattr(app, 'setStyleSheet') and hasattr(app, 'styleSheet'):
            style = app.styleSheet()
            style += f"\nQPushButton {{ background-color: {color}; }}\nQPushButton:hover {{ background-color: #222; color: {color}; }}"
            app.setStyleSheet(style) 