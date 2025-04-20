import win32gui
from PyQt5.QtGui import QColor
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow


class RelativeScreenWindowTransformResult:
    def __init__(self, width, height, x, y):
        self.x = x
        self.y = y
        self.height = height
        self.width = width


def relative_screen_window_transform(width, height, x_percent, y_percent):
    """ Calculates transform to place window independent of screen resolution """
    hwnd = win32gui.GetDesktopWindow()
    rect = win32gui.GetWindowRect(hwnd)

    return RelativeScreenWindowTransformResult(x=int(x_percent * (rect[0] + rect[2])) - int(width / 2),
                                               y=int(y_percent * (rect[1] + rect[3])) - height,
                                               height=height,
                                               width=width)


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
