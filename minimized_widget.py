from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QIcon, QColor, QBrush
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QVBoxLayout, QLineEdit, \
    QWidget, QMainWindow, QHBoxLayout, QPushButton

import statics


class MinimizedWidget(QMainWindow):
    def __init__(self, parent=None, on_expand_callback=None):
        super().__init__(parent=parent)
        self.setWindowFlags(
            Qt.Window | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint | Qt.WindowType.FramelessWindowHint)

        self.on_expand_callback = on_expand_callback

        transform = statics.relative_screen_window_transform(150, 30, 0.5, 0.99)
        self.setGeometry(transform.x, transform.y, transform.width, transform.height)

        self.main_widget = QWidget(self)
        self.main_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.button_layout = QHBoxLayout()

        self.expand_btn = QPushButton("Show GBT", self)
        self.expand_btn.setFixedWidth(150)
        self.expand_btn.setFixedHeight(30)
        self.expand_btn.setStyleSheet("background-color: #307a44; color: white;border-radius: 0px;")
        self.expand_btn.clicked.connect(self.expand_clicked)
        self.button_layout.addWidget(self.expand_btn)

        self.layout.addLayout(self.button_layout)

    def expand_clicked(self):
        self.on_expand_callback()
