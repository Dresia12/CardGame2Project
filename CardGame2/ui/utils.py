# ui/utils.py
try:
    import sip  # type: ignore
except ImportError:
    sip = None

from PyQt5.QtWidgets import QWidget, QLayout
import gc

def is_layout_valid(layout):
    return layout is not None and (sip is None or not sip.isdeleted(layout))

def is_widget_valid(widget):
    return widget is not None and (sip is None or not sip.isdeleted(widget))

def safe_add_widget(layout, widget):
    if is_layout_valid(layout) and is_widget_valid(widget):
        layout.addWidget(widget)
    else:
        print("[CRITICAL] Tentative d'ajout à un layout ou widget détruit !")

def safe_clear_layout(layout):
    if not is_layout_valid(layout):
        return
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if is_widget_valid(widget):
            widget.setParent(None)

def count_widgets():
    return sum(1 for obj in gc.get_objects() if isinstance(obj, QWidget))

def count_layouts():
    return sum(1 for obj in gc.get_objects() if isinstance(obj, QLayout))

def print_memory_diagnostics():
    widgets = count_widgets()
    layouts = count_layouts()
    print(f"[MEMORY] Widgets vivants : {widgets}, Layouts vivants : {layouts}") 