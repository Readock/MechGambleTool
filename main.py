import asyncio
import os
import sys
import qdarktheme
import pywinstyles
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen
import threading

from app.leaderboard import leaderboard_manager
from app.service.player_detector import PlayerDetector
from app.service.state_manager import StateManager
from app.ui.widget_tool_bar import WidgetToolBar


class App(QApplication):
    def __init__(self):
        super().__init__([])
        self.splash = QSplashScreen(QPixmap("resources/w0BJbj40_400x400.jpg"))  # Ensure "splash.png" exists
        self.splash.show()

        # init detector
        self.detector = PlayerDetector()
        self.detector.ready.connect(self.on_detector_ready)

        # TODO: make leaderboard a singleton
        self.leaderboard = leaderboard_manager.load_leaderboard()
        self.state_manager = StateManager.init(leaderboard=self.leaderboard)
        self.widget_tool_bar = WidgetToolBar(application=self, leaderboard=self.leaderboard)
        # pywinstyles.apply_style(demo, "aero")
        pywinstyles.apply_style(self.widget_tool_bar, "dark")
        self.splash.finish(None)
        self.widget_tool_bar.show()

    def on_detector_ready(self):
        print("detector is ready!")
        self.widget_tool_bar.notify_detector_ready(self.detector)


def init_thread(loop, app):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(app.detector.init())


def restart():
    print("Restarting application...")

    os.execl(sys.executable, f'"{sys.executable}"', *sys.argv)


if __name__ == "__main__":
    App.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    App.setAttribute(Qt.AA_EnableHighDpiScaling)
    App.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = App()
    loop = asyncio.get_event_loop()
    t = threading.Thread(target=init_thread, args=(loop, app,))
    t.start()

    qdarktheme.setup_theme()

    exit_code = app.exec_()

    if exit_code == 100:
        restart()
    else:
        sys.exit(exit_code)
