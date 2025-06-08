import matplotlib
import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon, QColor, QBrush
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QVBoxLayout, QWidget, \
    QMainWindow
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from app import statics
from app.configuration import settings
from app.service.state_manager import StateManager


class PlayerChart(QMainWindow):

    def __init__(self, parent=None, leaderboard=None):
        super().__init__(parent=parent)

        self.setWindowIcon(QIcon("resources/w0BJbj40_400x400.jpg"))
        self.setWindowTitle("MechGambleTool-Chart")

        # self.setWindowFlags(
        #     Qt.Window | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint | Qt.WindowType.FramelessWindowHint)
        self.setWindowFlags(
            Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(settings.window_opacity())

        transform = statics.relative_screen_window_transform(800, 300, 0.5, 0.95)
        self.setGeometry(transform.x, transform.y, transform.width, transform.height)

        self.main_widget = QWidget(self)
        self.main_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.selected_players_frame = QFrame(self)
        self.selected_players_frame.setFrameShape(QFrame.StyledPanel)
        self.layout.addWidget(self.selected_players_frame)

        self.selected_players_layout = QVBoxLayout(self.selected_players_frame)

        self.leaderboard = leaderboard

        self.figure = plt.Figure(figsize=(6, 4))
        self.canvas = FigureCanvasQTAgg(self.figure)
        # self.canvas.setFixedHeight(200)
        self.canvas.figure.set_facecolor('none')
        self.selected_players_layout.addWidget(self.canvas)

        plt.style.use('dark_background')
        matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        matplotlib.rcParams['axes.unicode_minus'] = False
        self.ax = self.figure.add_subplot(111)
        self.populate_plot()

        self.figure.tight_layout()
        self.showMinimized()

    def update_view(self):
        self.populate_plot()

    def populate_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)  # Removes all rows
        self.table.setColumnCount(0)  # Removes all columns

        column_names = ["Name", "Score", "Rank", "mmr", "power", "wins", "Alias"]
        self.table.setColumnCount(len(column_names))
        self.table.setHorizontalHeaderLabels(column_names)

        header = self.table.horizontalHeader()
        for i in range(0, len(column_names)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        self.table.setRowCount(len(StateManager.instance().selected_players))
        max_metrics = self.leaderboard.max_metrics
        min_metrics = self.leaderboard.min_metrics
        for row, player in enumerate(StateManager.instance().selected_players):
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

        # set player id as data for each table cell
        for row, player in enumerate(StateManager.instance().selected_players):
            for i in range(0, len(column_names)):
                self.table.item(row, i).setData(Qt.UserRole, player.id)

        self.table.resizeColumnsToContents()

    def populate_plot(self):
        self.ax.clear()
        self.ax.set_facecolor('#2e2e2e')

        handles = []
        labels = []

        for player in StateManager.instance().selected_players:
            # Create a dictionary of timestamp → mmr values
            timestamp_to_mmr = {record.timestamp: record.metrics.mmr for record in player.records}

            # Create a list of mmr values, inserting None for missing timestamps
            mmr_values = [timestamp_to_mmr.get(ts, None) for ts in self.leaderboard.timestamps]

            line, = self.ax.plot(self.leaderboard.timestamps, mmr_values, 'o-', label=f"{player.id}")
            handles.append(line)  # Add the line handle to the list
            labels.append(player.current_name)  # Use the player's name as the custom label

        self.ax.legend(handles, labels, facecolor='black', edgecolor='grey', loc='lower center', fontsize=7,
                       markerscale=0.5,
                       labelspacing=0.1, handlelength=.5, handleheight=.5,
                       frameon=True)
        self.ax.grid(True, color='grey', linestyle='--', linewidth=0.5)
        self.ax.tick_params(axis='both', colors='grey')
        # ax.set_yticklabels([])
        # ax.set_xticklabels([])
        # ax.set_xticks([])
        # ax.set_yticks([])

        self.ax.tick_params(color='grey', labelcolor='grey')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('grey')

        self.canvas.draw()

    def eventFilter(self, source, event):
        if source == self.infoBar:
            if event.type() == QEvent.MouseButtonPress:
                self.offset = event.pos()
            elif event.type() == QEvent.MouseMove and self.offset is not None:
                # no need for complex computations: just use the offset to compute
                # "delta" position, and add that to the current one
                self.move(self.pos() - self.offset + event.pos())
                # return True to tell Qt that the event has been accepted and
                # should not be processed any further
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self.offset = None
        # let Qt process any other event
        return super().eventFilter(source, event)
