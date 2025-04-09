from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox
)

from app import statics
from app.configuration import settings


class SettingsUI(QWidget):
    def __init__(self, app, settings_save_callback=None):
        super().__init__()

        self.app = app
        self.settings_save_callback = settings_save_callback
        self.setWindowOpacity(settings.window_opacity())

        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)

        transform = statics.relative_screen_window_transform(650, 200, 0.5, 0.5)
        self.setGeometry(transform.x, transform.y, transform.width, transform.height)

        self.setWindowIcon(QIcon("resources/w0BJbj40_400x400.jpg"))
        self.setWindowTitle("Settings Editor")

        self.settings = settings.get_settings()

        # Main Layout
        layout = QVBoxLayout()

        # Game Directory
        self.game_dir_input = QLineEdit(self.settings.game_dir)
        game_dir_button = QPushButton("Browse")
        game_dir_button.clicked.connect(self.browse_game_dir)
        game_dir_layout = QHBoxLayout()
        game_dir_layout.addWidget(QLabel("Game Directory:"))
        game_dir_layout.addWidget(self.game_dir_input)
        game_dir_layout.addWidget(game_dir_button)
        layout.addLayout(game_dir_layout)

        # Fuzzy Threshold
        self.fuzzy_input = QLineEdit(str(self.settings.fuzzy_threshold))
        layout.addLayout(self._labeled_field("Fuzzy Threshold (0-100):", self.fuzzy_input))

        # Window opacity Threshold
        self.window_opacity_input = QLineEdit(str(self.settings.window_opacity))
        layout.addLayout(self._labeled_field("Window Opacity (0-100):", self.window_opacity_input))

        # Favorite Bets
        self.bets_input = QLineEdit(', '.join(map(str, self.settings.favorite_bets)))
        layout.addLayout(self._labeled_field("Favorite Bets (comma-separated):", self.bets_input))

        # Click Delay
        self.click_delay_input = QLineEdit(str(self.settings.click_delay))
        layout.addLayout(self._labeled_field("Click Delay (seconds):", self.click_delay_input))

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        restart_button = QPushButton("Save and Restart")
        restart_button.clicked.connect(self.save_and_restart)
        button_layout.addWidget(save_button)
        button_layout.addWidget(restart_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _labeled_field(self, label, widget):
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(label))
        hbox.addWidget(widget)
        return hbox

    def browse_game_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Game Directory", self.game_dir_input.text())
        if directory:
            self.game_dir_input.setText(directory)

    def save_settings(self):
        try:
            fuzzy = int(self.fuzzy_input.text())
            if not (0 <= fuzzy <= 100):
                raise ValueError("Fuzzy threshold must be between 0 and 100.")
            window_opacity = int(self.window_opacity_input.text())
            if not (0 <= window_opacity <= 100):
                raise ValueError("Window opacity must be between 0 and 100.")

            bets = [int(x.strip()) for x in self.bets_input.text().split(",")]
            delay = float(self.click_delay_input.text())

            # Update the global settings object (instead of creating a new one)
            updated_settings = settings.get_settings()
            updated_settings.fuzzy_threshold = fuzzy
            updated_settings.window_opacity = window_opacity
            updated_settings.favorite_bets = bets
            updated_settings.click_delay = delay
            updated_settings.game_dir = self.game_dir_input.text()

            # Save the updated settings to the file
            updated_settings.save()

            QMessageBox.information(self, "Success", "Settings saved successfully")
            self.settings_save_callback()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{str(e)}")

    def save_and_restart(self):
        self.save_settings()
        self.app.exit(100)
