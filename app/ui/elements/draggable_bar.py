from PyQt5.QtCore import Qt, QEvent, QPoint
from PyQt5.QtWidgets import QFrame


class DraggableTitleBar(QFrame):
    """A draggable title bar with no margins at the top."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(20)  # Ensure height is maintained

        # Ensure visibility
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)

        # Force visibility
        self.setStyleSheet("""
            background-color: black !important;  /* Medium gray */
            border: 0;
            border-radius: 0;
            opacity: 1;
        """)

        self.dragging = False
        self.offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.parent_window.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.parent_window.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.dragging = False
