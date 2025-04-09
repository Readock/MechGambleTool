from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QMainWindow, QHBoxLayout, QToolBar, QToolButton
import qtawesome as qta

from app import statics


class ToolWidgetButtonDefinition:
    def __init__(self, icon_name, tooltip, color, callback, is_detect_button=False):
        self.icon_name = icon_name
        self.tooltip = tooltip
        self.color = color
        self.callback = callback
        self.is_detect_button = is_detect_button


class WidgetToolBar(QMainWindow):
    def __init__(self, parent=None, tool_buttons=None):
        super().__init__(parent=parent)
        if tool_buttons is None:
            tool_buttons = []
        self.setWindowFlags(
            Qt.Window | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint | Qt.WindowType.FramelessWindowHint)

        transform = statics.relative_screen_window_transform(300, 30, 0.5, 0.99)
        self.setGeometry(transform.x, transform.y, transform.width, transform.height)

        self.main_widget = QWidget(self)
        self.main_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        self.toolbar = QToolBar()
        self.toolbar.setProperty("type", "toolbar")
        self.toolbar.setFixedHeight(40)
        self.setAttribute(Qt.WA_AlwaysShowToolTips, True)

        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(2, 2, 2, 2)
        button_layout.setSpacing(5)

        self.joar_hacky_as_fuck_detect_button = None
        for btn_conf in tool_buttons:
            btn = QToolButton()
            if btn_conf.is_detect_button:
                self.joar_hacky_as_fuck_detect_button = btn
                btn.setDisabled(True)
            btn.setIcon(qta.icon(btn_conf.icon_name, color="white"))
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(btn_conf.tooltip)
            btn.clicked.connect(btn_conf.callback)
            btn.setSizePolicy(QWidget.sizePolicy(self).Expanding, QWidget.sizePolicy(self).Preferred)
            btn.setStyleSheet(f"""
                QToolButton {{
                    border: none;
                    background-color: #1f1d1d;
                }}
                QToolButton:hover {{
                    background-color: {btn_conf.color};
                }}
                QToolButton:pressed {{
                    background-color: #505050;
                }}
                QToolButton:focus {{
                    outline: none;
                }}
                QToolTip {{
                    background-color: #333;
                    color: white;
                    border: 1px solid #555;
                }}
            """)
            button_layout.addWidget(btn)

        self.toolbar.addWidget(button_container)
        self.layout.addWidget(self.toolbar)
