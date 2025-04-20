from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QFontMetrics
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (
    QSlider
)


class MightyGambleSlider(QSlider):
    sliderBarClicked = pyqtSignal(int)

    def __init__(self, label_step=25, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setMinimum(1)
        self.setMaximum(200)
        self.setTickInterval(10)
        self.setSingleStep(1)
        self.setTickPosition(QSlider.TicksBelow)
        self.label_step = label_step

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if event.button() == Qt.LeftButton:
            event.accept()
            x = event.pos().x()
            value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
            self.sliderBarClicked.emit(int(value))

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setPen(QColor(55, 55, 55))

        self.add_label_to_value(painter, self.minimum())
        # Draw labels every label_step
        for value in range(self.label_step, self.maximum() + 1, self.label_step):
            self.add_label_to_value(painter, value)

    def add_label_to_value(self, painter, value):
        font_metrics = QFontMetrics(self.font())
        # Position in pixels
        ratio = (value - self.minimum()) / (self.maximum() - self.minimum())
        x = int(ratio * (self.width() - 16)) + 8  # Adjust for slider handle offset
        label = str(value)
        label_width = font_metrics.width(label)
        painter.drawText(x - label_width // 2, self.height(), label)
