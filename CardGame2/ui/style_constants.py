# style_constants.py
# Centralisation des styles pour toute l'UI

PLAY_BTN_STYLE = "background: #1976d2; color: #fff; font-weight: bold; font-size: 16px; padding: 10px 20px;"
BACK_BTN_STYLE = "background: #e67e22; color: #fff; font-weight: bold; font-size: 15px; margin-top: 10px;"
DUPLICATE_BTN_STYLE = "background: #1976d2; color: #fff; font-weight: bold; font-size: 15px; margin-top: 10px;"
SAVE_BTN_STYLE = "background: #27ae60; color: #fff; font-weight: bold; font-size: 16px; padding: 10px 20px;"
BUY_BTN_STYLE = "background: #1976d2; color: #fff; font-weight: bold; font-size: 16px; padding: 10px 20px;"
SUMMARY_LABEL_STYLE = "color: #ffae00; font-size: 15px; margin-top: 10px;"
TAB_STYLESHEET = (
    "QTabBar::tab { background: #181a20; color: #f8f8f2; padding: 8px 20px; font-size: 15px; } "
    "QTabBar::tab:selected { background: #3a7afe; color: #fff; }"
)
LIST_STYLESHEET = "background: #181a20; color: #f8f8f2; font-size: 15px;"
PREVIEW_STYLESHEET = "background: #23272e; color: #f8f8f2;"

# Mapping rareté → couleur pour effet visuel booster
RARITY_COLOR_MAP = {
    'COMMON': '#bdbdbd',      # gris
    'UNCOMMON': '#43a047',   # vert
    'RARE': '#1976d2',       # bleu
    'MYTHIC': '#ff9800',     # orange
    'SPECIAL': '#ab47bc',    # violet
    'BONUS': '#ffd600',      # jaune
} 