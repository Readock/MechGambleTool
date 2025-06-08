import json
import os

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QMainWindow, QTabWidget, QSlider, QProgressBar
)

from app import statics
from app.configuration import settings
from app.service.state_manager import StateManager
from app.ui.elements.mighty_slider import MightyGambleSlider
from app.ui.widgets.gambling import GambleScreenCoords
#from app.ui.widgets.gambling.GambleScreenCoords import CoordCollector, bet_team_blue, bet_team_red

DATA_FILE = "recent_bets.json"
MAX_BUTTONS = 5


class Gambler(QMainWindow):
    def __init__(self, parent=None, leaderboard=None):
        super().__init__(parent=parent)

        self.leaderboard = leaderboard
        self.setWindowIcon(QIcon("resources/w0BJbj40_400x400.jpg"))
        self.setWindowTitle("MechGambleTool-Gambler")

        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(settings.window_opacity())

        transform = statics.relative_screen_window_transform(450, 200, 0.2, 0.90)
        self.setGeometry(transform.x, transform.y, transform.width, transform.height)


        # main window
        self.main_widget = QWidget(self)
        self.main_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.main_widget)

        # Layouts
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        self.favourite_buttons_layout = QHBoxLayout()
        self.favourite_buttons_layout.setContentsMargins(1, 1, 1, 1)
        self.favourite_buttons_layout.setSpacing(1)
        self.recent_buttons_layout = QHBoxLayout()
        self.recent_buttons_layout.setContentsMargins(1, 1, 1, 1)
        self.recent_buttons_layout.setSpacing(1)
        progress_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        # UI-Elemente
        self.bet_blue = QPushButton("Blue")
        self.bet_blue.setStyleSheet("""
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
        self.bet_red = QPushButton("Red")
        self.bet_red.setStyleSheet("""
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
        self.bet_amount.setAlignment(Qt.AlignCenter)

        tabs = QTabWidget()
        favorite_tab = QWidget()
        recent_tab = QWidget()

        self.slider = MightyGambleSlider(orientation=Qt.Horizontal)
        self.slider.sliderBarClicked.connect(lambda v: self.update_text_field(v))
        self.slider.setRange(1, 200)

        self.recalibrate = QPushButton("joa")

        # config
        self.bet_amount.setPlaceholderText("Bet Amount ...")

        self.slider.setTickInterval(1)
        # self.slider.setSingleStep(1)
        # self.slider.setPageStep(10)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTracking(True)

        # Größe der Elemente
        self.bet_blue.setFixedSize(120, 60)
        self.bet_red.setFixedSize(120, 60)
        # self.bet_amount.setFixedSize(120, 40)

        self.slider.setFixedHeight(40)
        self.slider.setValue(1)

        # Label Style

        # Actions

        self.slider.valueChanged.connect(lambda v: self.update_text_field(v, prevent_signal=True))
        self.bet_amount.textChanged.connect(self.update_slider_from_text)

        self.bet_blue.clicked.connect(self.handle_team_blue_clicked)
        self.bet_red.clicked.connect(self.handle_team_red_clicked)
        self.recalibrate.clicked.connect(self.calibrate)

        self.decrease_button = QPushButton("-")
        self.decrease_button.setFixedSize(25, 25)
        self.decrease_button.clicked.connect(lambda: self.add_to_bet_amount(-1))

        self.increase_button = QPushButton("+")
        self.increase_button.setFixedSize(25, 25)
        self.increase_button.clicked.connect(lambda: self.add_to_bet_amount(1))

        # Anordnung
        top_layout.addWidget(self.bet_blue, alignment=Qt.AlignLeft)
        top_layout.addWidget(self.decrease_button, alignment=Qt.AlignCenter)
        top_layout.addWidget(self.bet_amount, alignment=Qt.AlignCenter)
        top_layout.addWidget(self.increase_button, alignment=Qt.AlignCenter)
        top_layout.addWidget(self.bet_red, alignment=Qt.AlignRight)

        stats_layout = QVBoxLayout()
        self.player_score_progress_bar = QProgressBar(self)
        self.player_score_progress_bar.setRange(0, 100)
        self.player_score_progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(224, 29, 29, 0.5);
                border: 0
            }
            QProgressBar::chunk { 
                background-color: rgba(29, 141, 222, 0.8);
                border: 0
            }
        """)
        self.player_score_progress_bar.setTextVisible(False)
        self.player_score_progress_bar.setRange(0, 100)
        self.player_score_progress_bar.setMaximumHeight(4)
        self.player_score_progress_bar.setContentsMargins(0, 0, 0, 2)  # No outer margin
        stats_layout.addWidget(self.player_score_progress_bar)

        self.warning_label = QLineEdit()
        self.warning_label.setText("⚠ Current selected player stats are not up-to-date and might be invalid")
        self.warning_label.setVisible(False)
        stats_layout.addWidget(self.warning_label)

        favorite_tab.setLayout(self.favourite_buttons_layout)
        recent_tab.setLayout(self.recent_buttons_layout)

        tabs.addTab(favorite_tab, "Favorite")
        tabs.addTab(recent_tab, "Recently Used")

        decrease_button = QPushButton("-")
        decrease_button.setFixedSize(25, 25)
        decrease_button.clicked.connect(lambda: self.add_to_bet_amount(-1))
        progress_layout.addWidget(decrease_button)

        self.slider.setContentsMargins(10, 0, 10, 0)
        progress_layout.addWidget(self.slider)

        increase_button = QPushButton("+")
        increase_button.setFixedSize(25, 25)
        increase_button.clicked.connect(lambda: self.add_to_bet_amount(1))
        progress_layout.addWidget(increase_button)

        bottom_layout.addWidget(self.recalibrate, alignment=Qt.AlignBottom)

        main_layout.addLayout(stats_layout)
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
        self.update_player_score_states()

    def update_view(self):
        self.update_player_score_states()

    def update_player_score_states(self):
        self.bet_blue.setText(StateManager.instance().left_name())
        self.bet_red.setText(StateManager.instance().right_name())
        self.warning_label.setVisible(StateManager.instance().has_selection_warnings())
        if StateManager.instance().has_selected_players():
            self.player_score_progress_bar.setVisible(True)
            ratio = int(StateManager.instance().player_score_ratio() * 100)
            self.player_score_progress_bar.setValue(ratio)
        else:
            self.player_score_progress_bar.setVisible(False)

    def add_to_bet_amount(self, delta):
        self.update_text_field(self.get_bet_amount() + delta)

    def update_text_field(self, value: int, prevent_signal=False):
        if prevent_signal:  # To prevent recursive loop
            self.bet_amount.blockSignals(True)
        # noinspection PyTypeChecker
        new_value: int = np.clip(value, 1, 200)
        self.bet_amount.setText(str(new_value))
        self.slider.setValue(new_value)
        if prevent_signal:
            self.bet_amount.blockSignals(False)

    def update_slider_from_text(self):
        self.update_text_field(self.get_bet_amount(), prevent_signal=True)

    def get_bet_amount(self):
        text = self.bet_amount.text()
        if text.isdigit():
            return int(text)
        return 1

    def handle_team_blue_clicked(self):
        self.handle_main_button_click()
        bet_team_blue(self.get_bet_amount())

    def handle_team_red_clicked(self):
        self.handle_main_button_click()
        bet_team_red(self.get_bet_amount())

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
        new_button.setFixedHeight(25)
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
        # TODO: unfuck this
        #collector = CoordCollector()
        #collector.start()

        self.recalibrate.setText("Recalibrate")

    def set_calibration_button_text(self):
        if os.path.exists(GambleScreenCoords.coords_file):
            self.recalibrate.setText("Recalibrate")
        else:
            self.recalibrate.setText("Calibrate")
