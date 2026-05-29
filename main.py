# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from database import Database
from image_handler import ImageHandler
from clipboard_monitor import ClipboardMonitor
from ui.main_window import MainWindow
from config import FONT_FAMILY


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ClipboardHistory")
    app.setOrganizationName("ClipboardHistory")
    app.setQuitOnLastWindowClosed(False)

    font = QFont(FONT_FAMILY)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    db = Database()
    image_handler = ImageHandler()
    monitor = ClipboardMonitor()

    window = MainWindow(db, image_handler, monitor)
    window._load_history()

    monitor.start()
    window.show()
    window.raise_()
    window.activateWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
