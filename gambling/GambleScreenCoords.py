from tkinter import Tk, Canvas, BOTH
import json
import pyautogui
from pynput.mouse import Controller
import os
import time

from scipy.stats import alpha

coords_file = "screen_coords.json"
mouse_controller = Controller()

COORD_LABELS = ['join_bet', 'blue_team', 'slider_one', 'confirm']


def save_coords_to_json(coords, filename=coords_file):
    with open(filename, 'w') as f:
        json.dump(coords, f, indent=4)


def load_coords_from_json(filename=coords_file):
    if not os.path.exists(filename):
        raise FileNotFoundError("Coordinate file not found. Please run calibration first.")
    with open(filename, 'r') as f:
        return json.load(f)


def simulate_click(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.click()


def click_join_bet():
    coords = load_coords_from_json()
    simulate_click(*coords['join_bet'])


def click_blue_team():
    coords = load_coords_from_json()
    simulate_click(*coords['blue_team'])


def click_slider_one():
    coords = load_coords_from_json()
    simulate_click(*coords['slider_one'])


def click_confirm():
    coords = load_coords_from_json()
    simulate_click(*coords['confirm'])

class GambleScreenCoordsCalibration:
    def __init__(self):

        self.calibrating_click = False


    def collect_coordinates(self):
        coords = {}

        def on_click(event):

            nonlocal click_index
            if click_index < len(COORD_LABELS):
                x, y = event.x_root, event.y_root
                label = COORD_LABELS[click_index]
                coords[label] = (x, y)
                draw_crosshair(x, y, label)
                click_index += 1

                root.after(100, lambda: [hide_and_click(x, y)])

                if click_index == len(COORD_LABELS):
                    root.after(500, lambda: [save_coords_to_json(coords), root.destroy()])

        def draw_crosshair(x, y, text):
            size = 10
            canvas.create_line(x - size, y, x + size, y, fill="red", width=2)
            canvas.create_line(x, y - size, x, y + size, fill="red", width=2)
            canvas.create_text(x, y - 15, text=text, fill="white", font=("Arial", 12, "bold"))

        def hide_and_click(x, y):
            # Hide the root window temporarily
            root.withdraw()

            # Simulate the click on the background application
            pyautogui.click()

            time.sleep(0.2)

            # Wait for a moment and then show the root window again
            root.deiconify()  # Show the root window again

        root = Tk()

        root.attributes('-fullscreen', True)
        root.attributes('-alpha', 0.5)

        root.configure(bg='gray')
        root.config(cursor="crosshair")

        canvas = Canvas(root, bg='gray', highlightthickness=0)
        canvas.pack(fill=BOTH, expand=True)

        click_index = 0
        canvas.bind("<Button-1>", on_click)

        root.mainloop()