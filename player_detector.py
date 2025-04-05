from PIL import ImageGrab
import easyocr
import asyncio

import statics
from leaderboard import Leaderboard
from fuzzywuzzy import fuzz
from PyQt5.QtCore import QObject, pyqtSignal


# reader = None
#
#
# def init():
#     global reader
#     # takes a while
#     reader = easyocr.Reader(['ch_sim', 'en'])


def is_fuzzy_match(target, candidates, threshold=70):
    return any(fuzz.ratio(target, c) >= threshold for c in candidates)


class PlayerDetector(QObject):
    ready = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.reader = None
        self.ready: pyqtSignal

    async def init(self):
        self.reader = await asyncio.to_thread(lambda: easyocr.Reader(['ch_sim', 'en']))
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
        left_img.save(left_path)
        right_img.save(right_path)

        left_result = self.reader.readtext(left_path, detail=0)
        right_result = self.reader.readtext(right_path, detail=0)

        return left_result + right_result
