import os
import sys

import pywinstyles
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QMainWindow, QHBoxLayout, QToolBar, QToolButton
import qtawesome as qta

from app import statics
from app.configuration import settings
from app.configuration.settings_gui import SettingsUI
from app.player_detector import PlayerDetector
from app.ui.widgets.chart.player_chart import PlayerChart
from app.ui.widgets.gambling.gambler import Gambler
from app.ui.widgets.leaderboard.picker import PlayerPicker


class ToolWidgetButtonDefinition:
    def __init__(self, icon_name, tooltip, color, callback, is_detect_button=False):
        self.icon_name = icon_name
        self.tooltip = tooltip
        self.color = color
        self.callback = callback
        self.is_detect_button = is_detect_button


class WidgetToolBar(QMainWindow):
    def __init__(self, parent=None, application=None, leaderboard=None):
        super().__init__(parent=parent)
        self.application = application
        self.leaderboard = leaderboard
        self.selected_players = []

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

        self.detector_service = None

        # widget windows
        self.gamble_window = None
        self.picker_window = None
        self.settings_window = None
        self.player_chart_window = None

        # widget buttons
        self.gamble_btn = self.add_tool_button(
            ToolWidgetButtonDefinition(
                icon_name="fa6s.ticket",
                tooltip="Gamble",
                color="#1297a6",
                callback=self.gamble
            ))
        button_layout.addWidget(self.gamble_btn)

        self.launch_btn = self.add_tool_button(
            ToolWidgetButtonDefinition(
                icon_name="fa6b.steam",
                tooltip="Launch Game",
                color="#368a33",
                callback=self.launch_game
            ))
        button_layout.addWidget(self.launch_btn)

        self.chart_btn = self.add_tool_button(
            ToolWidgetButtonDefinition(
                icon_name="fa6s.chart-line",
                tooltip="Chart",
                color="#125aa6",
                callback=self.player_chart
            ))
        button_layout.addWidget(self.chart_btn)

        self.detect_btn = self.add_tool_button(
            ToolWidgetButtonDefinition(
                icon_name="fa6s.wand-magic-sparkles",
                tooltip="Detect Players",
                color="#77338a",
                callback=self.detect_player,
                is_detect_button=True
            ))
        # gets only enabled after initializing
        self.detect_btn.setDisabled(True)
        button_layout.addWidget(self.detect_btn)

        self.leaderboard_btn = self.add_tool_button(

            ToolWidgetButtonDefinition(
                icon_name="fa6s.list",
                tooltip="Player Leaderboard",
                color="#d6a124",
                callback=self.pick_player
            ))
        button_layout.addWidget(self.leaderboard_btn)

        self.settings_btn = self.add_tool_button(
            ToolWidgetButtonDefinition(
                icon_name="fa6s.gear",
                tooltip="Settings",
                color="#808080",
                callback=self.open_settings
            ))
        button_layout.addWidget(self.settings_btn)

        self.close_btn = self.add_tool_button(
            ToolWidgetButtonDefinition(
                icon_name="fa6s.xmark",
                tooltip="Close Program",
                color="#a61212",
                callback=self.close_app
            ))
        button_layout.addWidget(self.close_btn)

        self.toolbar.addWidget(button_container)
        self.layout.addWidget(self.toolbar)

    def pick_player(self):
        if statics.is_window_active(self.picker_window):
            self.picker_window.close()
            self.picker_window = None
        else:
            self.picker_window = PlayerPicker(leaderboard=self.leaderboard,
                                              selected_players=self.selected_players,
                                              on_select_callback=self.toggle_player_select)
            pywinstyles.apply_style(self.picker_window, "dark")
            self.picker_window.showNormal()

    def toggle_player_select(self, player_id):
        if any(player_id == p.id for p in self.selected_players):
            self.selected_players[:] = [player for player in self.selected_players if player.id != player_id]
        else:
            self.selected_players.append(self.leaderboard.get_player(player_id))
        if self.player_chart_window:
            self.player_chart_window.update_view(selected_players=self.selected_players)
        if self.picker_window:
            self.picker_window.update_view(selected_players=self.selected_players)

    def detect_player(self):
        self.selected_players = self.detector_service.detect_player(self.leaderboard)
        if self.player_chart_window:
            self.player_chart_window.update_view(self.selected_players)

    def gamble(self):
        if statics.is_window_active(self.gamble_window):
            self.gamble_window.close()
            self.gamble_window = None
        else:
            self.gamble_window = Gambler(leaderboard=self.leaderboard)
            pywinstyles.apply_style(self.gamble_window, "dark")
            self.gamble_window.showNormal()

    def player_chart(self):
        if statics.is_window_active(self.player_chart_window):
            self.player_chart_window.close()
            self.player_chart_window = None
        else:
            self.player_chart_window = PlayerChart(leaderboard=self.leaderboard, selected_players=self.selected_players)
            pywinstyles.apply_style(self.player_chart_window, "dark")
            self.player_chart_window.showNormal()

    def launch_game(self):
        game_exe = os.path.join(settings.game_filepath(), "Mechabellum.exe")
        if os.path.exists(game_exe):
            os.startfile(game_exe)
        else:
            statics.show_error("Game executable not found!\n" + game_exe)

    def open_settings(self):
        if self.settings_window and self.settings_window.isVisible() and not self.settings_window.isMinimized():
            self.settings_window.close()
            self.settings_window = None
        else:
            self.settings_window = SettingsUI(app=self.application)
            pywinstyles.apply_style(self.settings_window, "dark")
            self.settings_window.showNormal()

    def close_app(self):
        if self.picker_window:
            self.picker_window.close()
        if self.gamble_window:
            self.gamble_window.close()
        if self.player_chart_window:
            self.player_chart_window.close()
        if self.settings_window:
            self.settings_window.close()
        sys.exit(1)  # exit app

    def notify_detector_ready(self, detector: PlayerDetector):
        self.detector_service = detector
        self.detect_btn.setDisabled(False)

    def add_tool_button(self, config):
        btn = QToolButton()
        btn.setIcon(qta.icon(config.icon_name, color="white"))
        btn.setIconSize(QSize(24, 24))
        btn.setToolTip(config.tooltip)
        btn.clicked.connect(config.callback)
        btn.setSizePolicy(QWidget.sizePolicy(self).Expanding, QWidget.sizePolicy(self).Preferred)
        btn.setStyleSheet(f"""
            QToolButton {{
                border: none;
                background-color: #1f1d1d;
            }}
            QToolButton:hover {{
                background-color: {config.color};
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
        return btn

    def closeEvent(self, event):
        # Exit the application with all windows and not just self
        event.ignore()
        self.close_app()
