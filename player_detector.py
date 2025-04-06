from PIL import ImageGrab
import asyncio
import settings
import statics
from leaderboard import Leaderboard
from fuzzywuzzy import fuzz
from PyQt5.QtCore import QObject, pyqtSignal
import cv2
import numpy as np


def is_fuzzy_match(target, candidates):
    threshold = settings.get_settings().fuzzy_threshold
    return any(fuzz.ratio(target.lower(), c.lower()) >= threshold for c in candidates)


def to_maked_image(image):
    lower_bound_white = np.array([190, 190, 190], dtype=np.uint8)
    upper_bound_white = np.array([255, 255, 255], dtype=np.uint8)
    white_mask = cv2.inRange(np.array(image.convert("RGB")), lower_bound_white, upper_bound_white)
    return cv2.cvtColor(white_mask, cv2.COLOR_GRAY2BGR)


class PlayerDetector(QObject):
    ready = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.reader = None
        self.ready: pyqtSignal

    async def init(self):
        from easyocr import Reader
        self.reader = await asyncio.to_thread(lambda: Reader(['ch_sim', 'en']))
        self.ready.emit()

    def detect_player(self, leaderboard: Leaderboard):
        if self.reader is None:
            statics.show_error("Something went with setting up easyocr!")
            return []
        names = self.read_names_from_screen()
        matches = []
        for player in leaderboard.get_players():
            if is_fuzzy_match(player.current_name, names) or any(
                    is_fuzzy_match(alias, names) for alias in player.aliases):
                matches.append(player)
        return matches

    def read_names_from_screen(self):
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

        cv2.imwrite(left_path, to_maked_image(left_img))
        cv2.imwrite(right_path, to_maked_image(right_img))

        left_result = self.reader.readtext(left_path, detail=0)
        right_result = self.reader.readtext(right_path, detail=0)
        print("Detected text left: " + ', '.join(left_result))
        print("Detected text right: " + ', '.join(right_result))
        return left_result + right_result
