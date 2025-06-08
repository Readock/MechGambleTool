from screeninfo import get_monitors
from PyQt5.QtGui import QColor
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow

class RelativeScreenWindowTransformResult:
    def __init__(self, width, height, x, y):
        self.x = x
        self.y = y
        self.height = height
        self.width = width

def get_monitor():
    primary_monitor = next((m for m in get_monitors() if m.is_primary), get_monitors()[0])
    return primary_monitor

def relative_screen_window_transform(width, height, x_percent, y_percent):
    """Calculates transform to place window independent of screen resolution."""
    # Get the primary monitor's dimensions
    primary_monitor = get_monitor()
    screen_width = primary_monitor.width
    screen_height = primary_monitor.height


    # Calculate x, y coordinates based on percentages
    x = int(x_percent * screen_width) - int(width / 2)
    y = int(y_percent * screen_height) - height

    return RelativeScreenWindowTransformResult(
        x=x,
        y=y,
        height=height,
        width=width
    )


def calculate_color(percentage: float):
    green_hue = 100.0 / 360.0
    hue = percentage * green_hue
    return QColor.fromHsvF(hue, 1 - 0.5 * hue, 1 - 0.5 * hue).name()


def is_window_active(window: QMainWindow):
    return window and window.isVisible() and not window.isMinimized()


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def show_error(message, exitApp=False):
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(message)
    msg_box.setWindowTitle("Error")
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()
    if exitApp:
        sys.exit(1)  # Exit the application
