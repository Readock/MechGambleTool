from PyQt5.QtGui import QIcon

import json
import os

from app import statics

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QMainWindow, QTabWidget, QSlider
)
from PyQt5.QtCore import Qt

from app.configuration import settings
from app.ui.widgets.gambling import GambleScreenCoords
from app.ui.widgets.gambling.GambleScreenCoords import CoordCollector, bet_team_blue, bet_team_red

DATA_FILE = "recent_bets.json"
MAX_BUTTONS = 5


class Gambler(QMainWindow):
    def __init__(self, parent=None, leaderboard=None):
        super().__init__(parent=parent)

        self.leaderboard = leaderboard

        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

        transform = statics.relative_screen_window_transform(650, 200, 0.2, 0.90)
        self.setGeometry(transform.x, transform.y, transform.width, transform.height)

        self.setWindowIcon(QIcon("resources/w0BJbj40_400x400.jpg"))
        self.setWindowTitle("Gamble")

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
        bet_blue = QPushButton("Blue")
        bet_blue.setStyleSheet("""
            QPushButton {
                color: rgba(112, 204, 224, 1);
                font-weight:bold;
                border: none;
                background-color: rgba(29, 141, 222, 0.5);
            }
            QPushButton:hover {
                color: white;
                background-color: rgba(29, 141, 222, 0.8);
            }
            QPushButton:pressed {
                background-color: #505050;
            }
            QPushButton:focus {
                outline: none;
            }
        """)
        bet_red = QPushButton("Red")
        bet_red.setStyleSheet("""
            QPushButton {
                color: rgba(255, 128, 128, 1);
                font-weight:bold;
                border: none;
                background-color: rgba(224, 29, 29, 0.5);
            }
            QPushButton:hover {
                color: white;
                background-color: rgba(224, 29, 29, 0.8);
            }
            QPushButton:pressed {
                background-color: #505050;
            }
            QPushButton:focus {
                outline: none;
            }
        """)
        self.bet_amount = QLineEdit()

        tabs = QTabWidget()
        favorite_tab = QWidget()
        recent_tab = QWidget()

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 200)

        self.recalibrate = QPushButton("joa")

        # config
        self.bet_amount.setPlaceholderText("Bet Amount ...")

        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(10)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTracking(True)  # Optional: update as you drag

        # Größe der Elemente
        bet_blue.setFixedSize(120, 60)
        bet_red.setFixedSize(120, 60)
        self.bet_amount.setFixedSize(120, 40)

        self.slider.setFixedHeight(40)
        self.slider.setValue(1)  # Beispielhafte Progress-Anzeige

        # Label Style

        # Actions

        self.slider.valueChanged.connect(self.update_text_field)
        self.bet_amount.textChanged.connect(self.update_slider_from_text)

        bet_blue.clicked.connect(self.handle_team_blue_clicked)
        bet_red.clicked.connect(self.handle_team_red_clicked)
        self.recalibrate.clicked.connect(self.calibrate)


        # Anordnung
        top_layout.addWidget(bet_blue, alignment=Qt.AlignCenter)
        top_layout.addWidget(self.bet_amount, alignment=Qt.AlignCenter)
        top_layout.addWidget(bet_red, alignment=Qt.AlignCenter)

        favorite_tab.setLayout(self.favourite_buttons_layout)
        recent_tab.setLayout(self.recent_buttons_layout)

        tabs.addTab(favorite_tab, "Favorite")
        tabs.addTab(recent_tab, "Recently Used")

        progress_layout.addWidget(self.slider)

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
        self.load_favorite_buttons()

    #

    def update_text_field(self, value):
        self.bet_amount.blockSignals(True)  # Prevent recursive loop
        self.bet_amount.setText(str(value))
        self.bet_amount.blockSignals(False)

    def update_slider_from_text(self):
        text = self.bet_amount.text()
        if text.isdigit():
            value = int(text)
            if 1 <= value <= 200:
                self.slider.blockSignals(True)  # Prevent recursive loop
                self.slider.setValue(value)
                self.slider.blockSignals(False)

    def handle_team_blue_clicked(self):
        self.handle_main_button_click()
        if self.bet_amount.text().strip() == "":
            bet_team_blue(1)
        else:
            bet_team_blue(int(self.bet_amount.text()))


    def handle_team_red_clicked(self):
        self.handle_main_button_click()
        if self.bet_amount.text().strip() == "":
            bet_team_red(1)
        else:
            bet_team_red(int(self.bet_amount.text()))


    def handle_main_button_click(self):
        text = self.bet_amount.text().strip()
        if not text:
            return

        self.add_recent_button(text)
        self.save_recent_buttons()

    # RECENT BUTTONS

    def add_recent_button(self, text):
        new_button = self.create_bet_button(text)

        if len(self.recent_buttons) >= MAX_BUTTONS:
            old_button = self.recent_buttons.pop(0)
            self.recent_buttons_layout.removeWidget(old_button)
            old_button.deleteLater()

        self.recent_buttons.append(new_button)
        self.recent_buttons_layout.insertWidget(0, new_button)

    def add_favorite_button(self, text):
        new_button = self.create_bet_button(text)
        self.favourite_buttons_layout.addWidget(new_button)

    def create_bet_button(self, text) -> QPushButton:
        new_button = QPushButton(text)
        new_button.setFixedSize(120, 60)
        new_button.clicked.connect(lambda: self.bet_amount.setText(text))
        return new_button

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

    def load_favorite_buttons(self):
        favorite_bets = settings.get_settings().favorite_bets
        for number in favorite_bets:
            self.add_favorite_button(str(number))

    # CALIBRATION

    def calibrate(self):
        collector = CoordCollector()
        collector.start()

        self.recalibrate.setText("Recalibrate")

    def set_calibration_button_text(self):
        if os.path.exists(GambleScreenCoords.coords_file):
            self.recalibrate.setText("Recalibrate")
        else:
            self.recalibrate.setText("Calibrate")
