from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor, QBrush
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QVBoxLayout, QLineEdit, \
    QWidget, QMainWindow, QTabWidget

from app import statics
from app.configuration import settings
import numpy as np

from app.service.state_manager import StateManager


class PlayerPicker(QMainWindow):
    def __init__(self, parent=None, on_select_callback=None, leaderboard=None):
        super().__init__(parent=parent)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.on_select_callback = on_select_callback

        transform = statics.relative_screen_window_transform(600, 700, 0.8, 0.99)
        self.setGeometry(transform.x, transform.y, transform.width, transform.height)
        self.setWindowOpacity(settings.window_opacity())

        self.setWindowIcon(QIcon("resources/w0BJbj40_400x400.jpg"))
        self.setWindowTitle("MechGambleTool")

        self.main_widget = QWidget(self)
        self.main_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Search input field
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search player by name...")
        self.search_input.setFixedHeight(70)
        self.search_input.setContentsMargins(10, 2, 10, 2)
        self.search_input.textChanged.connect(self.refresh_tables)
        self.layout.addWidget(self.search_input)

        self.table_tabs = QTabWidget()
        self.leaderboard_tab = QWidget()
        self.selected_players_tab = QWidget()

        self.leaderboard_table_layout = QVBoxLayout(self)
        self.leaderboard_table = QTableWidget(self)
        self.leaderboard_table.itemDoubleClicked.connect(self.on_table_clicked)
        self.leaderboard_table_layout.addWidget(self.leaderboard_table)

        self.selected_table_layout = QVBoxLayout(self)
        self.selected_table = QTableWidget(self)
        self.selected_table.itemDoubleClicked.connect(self.on_table_clicked)
        self.selected_table_layout.addWidget(self.selected_table)

        self.leaderboard_tab.setLayout(self.leaderboard_table_layout)
        self.selected_players_tab.setLayout(self.selected_table_layout)

        self.table_tabs.addTab(self.leaderboard_tab, "Leaderboard")
        self.table_tabs.addTab(self.selected_players_tab, "Selected Players")
        self.layout.addWidget(self.table_tabs)

        self.leaderboard = leaderboard
        self.players = self.leaderboard.get_players()
        self.populate_table(table=self.leaderboard_table, players=self.players)
        self.populate_table(table=self.selected_table, players=StateManager.instance().selected_players)

    def on_table_clicked(self, item):
        player_id = item.data(Qt.UserRole)
        self.on_select_callback(player_id)

    def populate_table(self, table, players):
        filtered_players = self.filter_players(players)
        table.clearContents()
        table.setRowCount(0)
        table.setColumnCount(0)

        column_names = ["Name", "Score", "Rank", "MMR", "Power", "Wins", "Alias"]
        table.setColumnCount(len(column_names))
        table.setHorizontalHeaderLabels(column_names)

        header = table.horizontalHeader()
        for i in range(len(column_names)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        # stretch player names
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)

        table.setRowCount(len(filtered_players))
        max_metrics = self.leaderboard.max_metrics
        min_metrics = self.leaderboard.min_metrics
        for row, player in enumerate(filtered_players):
            table.setItem(row, 0, QTableWidgetItem(player.current_name))

            score_widget = QTableWidgetItem(str(round(player.score, 2)))
            score_widget.setForeground(QBrush(QColor(player.color)))
            table.setItem(row, 1, score_widget)

            score_widget = QTableWidgetItem(str(round(player.current_metrics.world_rank, 2)))
            world_percent = 1 - float(player.current_metrics.world_rank) / min_metrics.world_rank
            score_widget.setForeground(QBrush(QColor(statics.calculate_color(world_percent))))
            table.setItem(row, 2, score_widget)

            score_widget = QTableWidgetItem(str(round(player.current_metrics.mmr, 2)))
            world_percent = float(player.current_metrics.mmr - min_metrics.mmr) / (max_metrics.mmr - min_metrics.mmr)
            score_widget.setForeground(QBrush(QColor(statics.calculate_color(world_percent))))
            table.setItem(row, 3, score_widget)

            score_widget = QTableWidgetItem(str(round(player.current_metrics.power, 2)))
            world_percent = float(player.current_metrics.power - min_metrics.power) / (
                    max_metrics.power - min_metrics.power)
            score_widget.setForeground(QBrush(QColor(statics.calculate_color(world_percent))))
            table.setItem(row, 4, score_widget)

            score_widget = QTableWidgetItem(str(round(player.max_metrics.total_wins, 2)))
            world_percent = float(player.current_metrics.total_wins - min_metrics.total_wins) / (
                    max_metrics.total_wins - min_metrics.total_wins)
            score_widget.setForeground(QBrush(QColor(statics.calculate_color(world_percent))))
            table.setItem(row, 5, score_widget)

            table.setItem(row, 6, QTableWidgetItem(", ".join(player.aliases)))

        # Store player ID in table items
        for row, player in enumerate(filtered_players):
            for i in range(len(column_names)):
                table.item(row, i).setData(Qt.UserRole, player.id)

        table.resizeColumnsToContents()

    def filter_players(self, players):
        search_text = self.search_input.text().strip().lower()
        if search_text:
            return [player for player in players if
                    search_text in player.current_name.lower() or any(
                        search_text in alias.lower() for alias in player.aliases)]
        return players

    def refresh_tables(self):
        self.populate_table(table=self.leaderboard_table, players=self.players)
        self.populate_table(table=self.selected_table, players=StateManager.instance().selected_players)

    def update_view(self):
        self.populate_table(table=self.selected_table, players=StateManager.instance().selected_players)
