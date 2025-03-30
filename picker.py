from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtGui import QIcon, QColor, QBrush
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QVBoxLayout, QLineEdit, \
    QWidget, QMainWindow

import statics


class PlayerPicker(QMainWindow):
    def __init__(self, parent=None, on_select_callback=None, leaderboard=None):
        super().__init__(parent=parent)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.on_select_callback = on_select_callback

        transform = statics.relative_screen_window_transform(600, 500, 0.8, 0.99)
        self.setGeometry(transform.x, transform.y, transform.width, transform.height)

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
        self.search_input.textChanged.connect(self.filter_table)
        self.layout.addWidget(self.search_input)

        self.selected_players_frame = QFrame(self)
        self.selected_players_frame.setFrameShape(QFrame.StyledPanel)
        self.layout.addWidget(self.selected_players_frame)

        self.selected_players_layout = QVBoxLayout(self.selected_players_frame)

        self.table = QTableWidget(self)
        self.table.itemDoubleClicked.connect(self.on_table_clicked)
        self.selected_players_layout.addWidget(self.table)

        self.leaderboard = leaderboard
        self.players = self.leaderboard.get_players()
        self.filtered_players = self.players  # Keep a filtered list
        self.populate_table()

    def on_table_clicked(self, item):
        player_id = item.data(Qt.UserRole)
        self.on_select_callback(player_id)

    def populate_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        column_names = ["Name", "Score", "Rank", "MMR", "Power", "Wins", "Alias"]
        self.table.setColumnCount(len(column_names))
        self.table.setHorizontalHeaderLabels(column_names)

        header = self.table.horizontalHeader()
        for i in range(len(column_names)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        # stretch player names
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.table.setRowCount(len(self.filtered_players))
        max_metrics = self.leaderboard.max_metrics
        min_metrics = self.leaderboard.min_metrics
        for row, player in enumerate(self.filtered_players):
            self.table.setItem(row, 0, QTableWidgetItem(player.current_name))

            score_widget = QTableWidgetItem(str(round(player.score, 2)))
            score_widget.setForeground(QBrush(QColor(player.color)))
            self.table.setItem(row, 1, score_widget)

            score_widget = QTableWidgetItem(str(round(player.current_metrics.world_rank, 2)))
            world_percent = 1 - float(player.current_metrics.world_rank) / min_metrics.world_rank
            score_widget.setForeground(QBrush(QColor(statics.calculate_color(world_percent))))
            self.table.setItem(row, 2, score_widget)

            score_widget = QTableWidgetItem(str(round(player.current_metrics.mmr, 2)))
            world_percent = float(player.current_metrics.mmr - min_metrics.mmr) / (max_metrics.mmr - min_metrics.mmr)
            score_widget.setForeground(QBrush(QColor(statics.calculate_color(world_percent))))
            self.table.setItem(row, 3, score_widget)

            score_widget = QTableWidgetItem(str(round(player.current_metrics.power, 2)))
            world_percent = float(player.current_metrics.power - min_metrics.power) / (
                    max_metrics.power - min_metrics.power)
            score_widget.setForeground(QBrush(QColor(statics.calculate_color(world_percent))))
            self.table.setItem(row, 4, score_widget)

            score_widget = QTableWidgetItem(str(round(player.max_metrics.total_wins, 2)))
            world_percent = float(player.current_metrics.total_wins - min_metrics.total_wins) / (
                    max_metrics.total_wins - min_metrics.total_wins)
            score_widget.setForeground(QBrush(QColor(statics.calculate_color(world_percent))))
            self.table.setItem(row, 5, score_widget)

            self.table.setItem(row, 6, QTableWidgetItem(", ".join(player.aliases)))

        # Store player ID in table items
        for row, player in enumerate(self.filtered_players):
            for i in range(len(column_names)):
                self.table.item(row, i).setData(Qt.UserRole, player.id)

        self.table.resizeColumnsToContents()

    def filter_table(self):
        search_text = self.search_input.text().strip().lower()
        if search_text:
            self.filtered_players = [player for player in self.players if
                                     search_text in player.current_name.lower() or any(
                                         search_text in alias.lower() for alias in player.aliases)]
        else:
            self.filtered_players = self.players
        self.populate_table()
