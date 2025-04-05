import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PIL import ImageGrab
import easyocr

reader = easyocr.Reader(['ch_sim', 'en'])


class OCRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Player Name")

        # UI Elements
        self.btn = QPushButton("Read Names")
        self.btn.clicked.connect(self.read_names)

        self.left_image_label = QLabel("Left Player Image")
        self.right_image_label = QLabel("Right Player Image")
        self.left_text_label = QLabel("Left Player Name: ")
        self.right_text_label = QLabel("Right Player Name: ")

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(self.btn)

        images_layout = QHBoxLayout()
        images_layout.addWidget(self.left_image_label)
        images_layout.addWidget(self.right_image_label)
        layout.addLayout(images_layout)

        texts_layout = QHBoxLayout()
        texts_layout.addWidget(self.left_text_label)
        texts_layout.addWidget(self.right_text_label)
        layout.addLayout(texts_layout)

        self.setLayout(layout)

    def read_names(self):
        # Take a screenshot
        screenshot = ImageGrab.grab()
        width, height = screenshot.size

        # Dynamically determine crop boxes
        box_size_x = int(width * 0.25)
        box_size_y = int(height * 0.05)

        # Define box positions (coordinates of the top-left corner)
        left_box_position = (int(width * 0.05), int(height * 0.02))
        right_box_position = (int(width * 0.70), int(height * 0.02))

        left_box = (left_box_position[0], left_box_position[1], left_box_position[0] + box_size_x,
                    left_box_position[1] + box_size_y)
        right_box = (right_box_position[0], right_box_position[1], right_box_position[0] + box_size_x,
                     right_box_position[1] + box_size_y)

        left_img = screenshot.crop(left_box)
        right_img = screenshot.crop(right_box)

        left_path = "left_player_name.png"
        right_path = "right_player_name.png"
        left_img.save(left_path)
        right_img.save(right_path)

        left_result = reader.readtext(left_path, detail=0)
        right_result = reader.readtext(right_path, detail=0)

        left_text = left_result
        right_text = right_result

        # Display text
        self.left_text_label.setText(f"Left Player Name: {left_text}")
        self.right_text_label.setText(f"Right Player Name: {right_text}")

        # Convert cropped images to Qt
        self.left_image_label.setPixmap(QPixmap(left_path).scaled(300, 100, Qt.KeepAspectRatio))
        self.right_image_label.setPixmap(QPixmap(right_path).scaled(300, 100, Qt.KeepAspectRatio))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OCRApp()
    window.show()
    sys.exit(app.exec_())
