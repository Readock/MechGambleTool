import os
import tkinter as tk
from tkinter import Canvas
import pyautogui
import time
import json

from configuration import settings

COORD_LABELS = ['join_bet', 'blue_team','slider_200' , 'slider_1', 'confirm', 'close_window']
coords_file = "screen_coords.json"

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

def click_red_team():
    screen_width, _ = pyautogui.size()
    coords = load_coords_from_json()
    x, y = coords['blue_team']
    mirrored_x = screen_width - x
    simulate_click(mirrored_x, y)

def click_slider_at(value):
    if not (1 <= value <= 200):
        raise ValueError("Value must be between 1 and 200")

    coords = load_coords_from_json()
    x1, y1 = coords['slider_1']
    x2, y2 = coords['slider_200']

    # Normalize value (0 = slider_one, 1 = slider_200)
    relative = (value - 1) / (200 - 1)

    # Interpolate both X and Y
    x = x1 + (x2 - x1) * relative
    y = y1 + (y2 - y1) * relative

    simulate_click(int(x), int(y))

def click_confirm():
    coords = load_coords_from_json()
    simulate_click(*coords['confirm'])

def click_close():
    coords = load_coords_from_json()
    simulate_click(*coords['close_window'])

def bet_team_blue(value):
    click_delay = float(settings.get_settings().click_delay)

    click_join_bet()
    time.sleep(click_delay)
    click_blue_team()
    time.sleep(click_delay)
    click_slider_at(value)
    time.sleep(click_delay)
    click_confirm()
    time.sleep(click_delay)
    click_close()

def bet_team_red(value):
    click_delay = float(settings.get_settings().click_delay)

    click_join_bet()
    time.sleep(click_delay)
    click_red_team()
    time.sleep(click_delay)
    click_slider_at(value)
    time.sleep(click_delay)
    click_confirm()
    time.sleep(click_delay)
    click_close()


class CoordCollector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.5)  # Semi-transparent overlay
        self.root.configure(bg='gray')       # Solid color for background
        self.root.overrideredirect(True)
        self.root.withdraw()  # Start hidden

        self.canvas = Canvas(self.root, bg='gray', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.config(cursor="crosshair")

        self.coords = {}
        self.current_index = 0
        self.click_enabled = True

        # Label at the top-left to show which coordinate is being set
        self.info_label = tk.Label(self.root, text="Setting coordinate...", fg="white", bg="gray", font=("Arial", 33, "bold"))
        self.info_label.place(x=20, y=20)

        self.canvas.bind("<ButtonRelease-1>", self.on_click)

    def start(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.loop_step()
        self.root.mainloop()

    def loop_step(self):
        if self.current_index >= len(COORD_LABELS):
            self.finish()
            return

        # Update the label to show which coordinate is being set
        label = COORD_LABELS[self.current_index]
        self.info_label.config(text=f"Setting coordinate: {label}")

        self.click_enabled = True

    def on_click(self, event):
        if not self.click_enabled:
            return

        self.click_enabled = False

        label = COORD_LABELS[self.current_index]
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()

        self.coords[label] = (x, y)
        self.draw_crosshair(x, y, label)

        # Hide, simulate, and continue
        self.root.withdraw()
        self.root.update()
        time.sleep(float(settings.get_settings().click_delay)+0.1)
        pyautogui.moveTo(x, y)
        pyautogui.click()

        self.current_index += 1
        self.root.after(200, self.resume)

    def resume(self):
        if self.current_index < len(COORD_LABELS):
            self.root.deiconify()
            self.loop_step()
        else:
            self.finish()

    def draw_crosshair(self, x, y, label):
        size = 10
        self.canvas.create_line(x - size, y, x + size, y, fill="red", width=2)
        self.canvas.create_line(x, y - size, x, y + size, fill="red", width=2)
        self.canvas.create_text(x + 15, y - 15, text=label, fill="white", font=("Arial", 12, "bold"))

    def finish(self):
        with open(coords_file, 'w') as f:
            json.dump(self.coords, f, indent=4)
        self.root.destroy()

if __name__ == "__main__":
    bet_team_blue(1)