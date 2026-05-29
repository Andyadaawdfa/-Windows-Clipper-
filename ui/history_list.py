from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QMenu

from ui.delegates import HistoryItemDelegate


class HistoryListWidget(QListWidget):
    item_copy_requested = pyqtSignal(int)
    item_delete_requested = pyqtSignal(int)
    item_preview_requested = pyqtSignal(int)

    def __init__(self, is_dark: bool = False, parent=None):
        super().__init__(parent)
        self._is_dark = is_dark
        self._delegate = HistoryItemDelegate(is_dark, self)
        self.setItemDelegate(self._delegate)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemDoubleClicked.connect(self._on_double_click)
        self.itemClicked.connect(self._on_click)
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSpacing(0)

    def set_dark(self, is_dark: bool):
        self._is_dark = is_dark
        self._delegate.set_dark(is_dark)
        self.update()

    def add_entry(self, entry: dict):
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, entry)
        item.setSizeHint(self._delegate.sizeHint(None, None))
        self.insertItem(0, item)

    def load_entries(self, entries: list[dict]):
        self.clear()
        for entry in reversed(entries):
            self.add_entry(entry)

    def _get_selected_entry_id(self) -> int | None:
        item = self.currentItem()
        if not item:
            return None
        data = item.data(Qt.ItemDataRole.UserRole)
        return data.get("id") if data else None

    def _on_click(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.item_preview_requested.emit(data["id"])

    def _on_double_click(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.item_copy_requested.emit(data["id"])

    def _show_context_menu(self, pos):
        item = self.itemAt(pos)
        if not item:
            return

        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        menu = QMenu(self)
        copy_action = menu.addAction("复制到剪贴板")
        copy_action.triggered.connect(lambda: self.item_copy_requested.emit(data["id"]))
        menu.addSeparator()
        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(lambda: self.item_delete_requested.emit(data["id"]))
        menu.exec(QCursor.pos())
