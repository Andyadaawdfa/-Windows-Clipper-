from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

from config import FONT_FAMILY, FONT_FALLBACK


class PreviewPanel(QWidget):
    def __init__(self, is_dark: bool = False, parent=None):
        super().__init__(parent)
        self._is_dark = is_dark
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("previewPanel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        self._empty_label = QLabel("选择项目\n查看详情")
        self._empty_label.setObjectName("emptyLabel")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setWordWrap(True)
        layout.addWidget(self._empty_label)

        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setFont(QFont(FONT_FAMILY, 12))
        self._text_edit.hide()
        layout.addWidget(self._text_edit)

        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.hide()
        layout.addWidget(self._image_label)

    def show_text(self, text: str):
        self._empty_label.hide()
        self._image_label.hide()
        self._text_edit.show()
        self._text_edit.setPlainText(text)

    def show_image(self, pixmap: QPixmap):
        self._empty_label.hide()
        self._text_edit.hide()
        self._image_label.show()
        scaled = pixmap.scaled(
            self._image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._image_label.setPixmap(scaled)

    def show_empty(self):
        self._text_edit.hide()
        self._image_label.hide()
        self._empty_label.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._image_label.isVisible() and not self._image_label.pixmap().isNull():
            original = self._image_label.property("original_pixmap")
            if original:
                scaled = original.scaled(
                    self._image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self._image_label.setPixmap(scaled)
