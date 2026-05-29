from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton

from config import FONT_FAMILY


class SearchBar(QWidget):
    search_changed = pyqtSignal(str)
    clear_requested = pyqtSignal()

    def __init__(self, is_dark: bool = False, parent=None):
        super().__init__(parent)
        self._is_dark = is_dark
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(0)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("搜索剪贴板内容…")
        self._search_input.setFont(QFont(FONT_FAMILY, 11))
        self._search_input.setFixedHeight(34)
        self._search_input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self._search_input)

        self._clear_btn = QPushButton("×")
        self._clear_btn.setFixedSize(28, 28)
        self._clear_btn.setFont(QFont(FONT_FAMILY, 16))
        self._clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: rgba(128, 128, 140, 0.7);
                font-size: 18px;
                padding: 0;
            }
            QPushButton:hover {
                color: rgba(128, 128, 140, 1);
            }
        """)
        self._clear_btn.clicked.connect(self._on_clear)
        self._clear_btn.hide()
        layout.addWidget(self._clear_btn)

    def _on_clear(self):
        self._search_input.clear()
        self._clear_btn.hide()
        self.clear_requested.emit()

    def on_text_changed(self, text: str):
        self._clear_btn.setVisible(bool(text))
