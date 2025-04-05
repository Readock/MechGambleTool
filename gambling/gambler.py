from PyQt5.QtGui import QIcon

import json
import os

import statics

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QProgressBar, QVBoxLayout, QHBoxLayout, QLabel, QMainWindow, QTabWidget
)
from PyQt5.QtCore import Qt

from gambling import GambleScreenCoords
from gambling.GambleScreenCoords import GambleScreenCoordsCalibration
from ui.CollapsibleBox import CollapsibleBox

DATA_FILE = "recent_bets.json"
MAX_BUTTONS = 5

class Gambler(QMainWindow):
    def __init__(self, parent=None, leaderboard=None):
        super().__init__(parent=parent)

        self.leaderboard = leaderboard

        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

        transform = statics.relative_screen_window_transform(650, 200, 0.2, 0.79)
        self.setGeometry(transform.x, transform.y, transform.width, transform.height)

        self.setWindowIcon(QIcon("../resources/w0BJbj40_400x400.jpg"))
        self.setWindowTitle("MechGambleTool")

        # main window
        self.main_widget = QWidget(self)
        self.main_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.main_widget)

        # Layouts
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        self.favourite_buttons_layout = QHBoxLayout()
        self.recent_buttons_layout = QHBoxLayout()
        progress_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        # UI-Elemente
        button1 = QPushButton("Blue")
        button2 = QPushButton("Red")
        self.textfield = QLineEdit()

        tabs = QTabWidget()
        favorite_tab = QWidget()
        recent_tab = QWidget()

        progress_bar = QProgressBar()

        self.recalibrate = QPushButton("joa")

        # config
        self.textfield.setPlaceholderText("Bet Amount ...")

        # Größe der Elemente
        button1.setFixedSize(120, 60)
        button2.setFixedSize(120, 60)
        self.textfield.setFixedSize(120, 40)
        progress_bar.setFixedHeight(40)
        progress_bar.setValue(35)  # Beispielhafte Progress-Anzeige

        # Farben (nur mit StyleSheet möglich)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid black;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00aaff;  /* Blau für den Fortschritt */
                width: 10px;
            }
        """)

        # Label Style

        # Actions
        button1.clicked.connect(self.handle_main_button_click)
        button2.clicked.connect(self.handle_main_button_click)
        self.recalibrate.clicked.connect(self.calibrate)

        # Anordnung
        top_layout.addWidget(button1, alignment=Qt.AlignCenter)
        top_layout.addWidget(self.textfield, alignment=Qt.AlignCenter)
        top_layout.addWidget(button2, alignment=Qt.AlignCenter)

        favorite_tab.setLayout(self.favourite_buttons_layout)
        recent_tab.setLayout(self.recent_buttons_layout)

        tabs.addTab(favorite_tab, "Favorite")
        tabs.addTab(recent_tab, "Recently Used")

        progress_layout.addWidget(progress_bar)

        bottom_layout.addWidget(self.recalibrate, alignment=Qt.AlignBottom)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(tabs)
        main_layout.addLayout(progress_layout)
        main_layout.addLayout(bottom_layout)
        main_layout.addStretch()

        self.main_widget.setLayout(main_layout)

        # initialisieren

        self.set_calibration_button_text()

        self.recent_buttons = []
        self.load_recent_buttons()

    def handle_main_button_click(self):
        text = self.textfield.text().strip()
        if not text:
            return

        self.add_recent_button(text)
        self.save_recent_buttons()

# RECENT BUTTONS

    def add_recent_button(self, text):
        new_button = QPushButton(text)
        new_button.setFixedSize(120, 60)
        new_button.clicked.connect(lambda: self.textfield.setText(text))

        if len(self.recent_buttons) >= MAX_BUTTONS:
            old_button = self.recent_buttons.pop(0)
            self.recent_buttons_layout.removeWidget(old_button)
            old_button.deleteLater()

        self.recent_buttons.append(new_button)
        self.recent_buttons_layout.insertWidget(0, new_button)

    def save_recent_buttons(self):
        texts = [btn.text() for btn in self.recent_buttons]
        with open(DATA_FILE, "w") as f:
            json.dump(texts, f)

    def load_recent_buttons(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                try:
                    texts = json.load(f)
                    for text in texts[:MAX_BUTTONS]:
                        self.add_recent_button(text)
                except json.JSONDecodeError:
                    print("Fehler beim Laden der recent.json – Datei beschädigt?")

# CALIBRATION

    def calibrate(self):
        gamble_screen_cords = GambleScreenCoordsCalibration()
        gamble_screen_cords.collect_coordinates()

        self.set_calibration_button_text()

    def set_calibration_button_text(self):
        if os.path.exists(GambleScreenCoords.coords_file):
            self.recalibrate.setText("Recalibrate")
        else:
            self.recalibrate.setText("Calibrate")
