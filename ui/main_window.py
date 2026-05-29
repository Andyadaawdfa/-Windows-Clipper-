# -*- coding: utf-8 -*-
import math
import sys
from PyQt6.QtCore import Qt, QPoint, QRect, QSettings, QSize, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QIcon, QPixmap, QPen, QBrush, QPainterPath, QLinearGradient
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QSystemTrayIcon, QMenu, QApplication,
    QMessageBox,
)

from config import (
    FONT_FAMILY, FONT_FALLBACK, CORNER_RADIUS, WINDOW_WIDTH, WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, WINDOW_MARGIN,
    ACCENT_R, ACCENT_G, ACCENT_B,
)
from database import Database
from image_handler import ImageHandler
from clipboard_monitor import ClipboardMonitor
from ui.history_list import HistoryListWidget
from ui.preview_panel import PreviewPanel
from ui.search_bar import SearchBar
from ui.styles import LIGHT_THEME, DARK_THEME

EDGE_MARGIN = 8
ACCENT_COLOR = QColor(ACCENT_R, ACCENT_G, ACCENT_B)


def _make_glyph_icon(draw_fn, size=18, color=QColor(160, 160, 170)):
    """Create a monochrome glyph icon pixmap."""
    px = QPixmap(size, size)
    px.fill(QColor(0, 0, 0, 0))
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    draw_fn(p, size, color)
    p.end()
    return QIcon(px)


def _draw_moon(p: QPainter, s: int, c: QColor):
    """Crescent moon — linear outline only."""
    from PyQt6.QtCore import QPointF
    p.setPen(QPen(c, 1.3))
    p.setBrush(Qt.BrushStyle.NoBrush)
    cx, cy = float(s // 2), float(s // 2)
    r = float(s // 3)
    path = QPainterPath()
    path.addEllipse(QPointF(cx, cy), r, r)
    path.addEllipse(QPointF(cx + r / 2 + 1, cy - r / 3), r * 2 / 3, r * 2 / 3)
    p.drawPath(path)


def _draw_sun(p: QPainter, s: int, c: QColor):
    """Sun — linear circle + rays, no fill."""
    p.setPen(QPen(c, 1.3))
    p.setBrush(Qt.BrushStyle.NoBrush)
    cx, cy = s // 2, s // 2
    r = s // 4
    p.drawEllipse(QPoint(cx, cy), r, r)
    for i in range(8):
        rad = math.radians(i * 45)
        x1 = cx + int((r + 1.5) * math.cos(rad))
        y1 = cy + int((r + 1.5) * math.sin(rad))
        x2 = cx + int((r + 3.5) * math.cos(rad))
        y2 = cy + int((r + 3.5) * math.sin(rad))
        p.drawLine(x1, y1, x2, y2)


def _draw_pin(p: QPainter, s: int, c: QColor):
    """Pin icon for stay-on-top toggle."""
    p.setPen(QPen(c, 1.6))
    p.setBrush(Qt.BrushStyle.NoBrush)
    # Circle outline
    p.drawEllipse(QPoint(s // 2, s // 2 + 1), s // 3, s // 3)
    # Pin needle
    cx = s // 2
    p.drawLine(cx, s // 2 - s // 3 + 1, cx, 2)


def _draw_minimize(p: QPainter, s: int, c: QColor):
    """Minimize dash."""
    p.setPen(QPen(c, 1.8))
    p.drawLine(s // 3, s // 2, s - s // 3, s // 2)


def _draw_close(p: QPainter, s: int, c: QColor):
    """Close X."""
    p.setPen(QPen(c, 1.8))
    margin = s // 3
    p.drawLine(margin, margin, s - margin, s - margin)
    p.drawLine(s - margin, margin, margin, s - margin)


class TitleBar(QWidget):
    """Professional monochrome title bar with macOS-style traffic light hover reveals."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self._drag_pos = None
        self._win = parent

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 10, 0)
        layout.setSpacing(6)

        self._title = QLabel("剪贴板历史")
        self._title.setObjectName("titleLabel")
        layout.addWidget(self._title)
        layout.addStretch()

        btn_style = """
            QPushButton {{
                border: none;
                border-radius: 13px;
                background-color: rgba({r}, {g}, {b}, 0.12);
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: rgba({r}, {g}, {b}, 0.22);
            }}
            QPushButton:pressed {{
                background-color: rgba({r}, {g}, {b}, 0.32);
            }}
        """

        # Dark mode toggle — moon/sun glyph
        self._dark_btn = QPushButton()
        self._dark_btn.setFixedSize(26, 26)
        self._dark_btn.setToolTip("切换深色/浅色模式")
        self._dark_btn.clicked.connect(self._win.toggle_dark_mode if self._win else None)
        layout.addWidget(self._dark_btn)

        # Pin toggle
        self._pin_btn = QPushButton()
        self._pin_btn.setFixedSize(26, 26)
        self._pin_btn.setToolTip("切换窗口置顶")
        self._pin_btn.clicked.connect(self._win.toggle_pin if self._win else None)
        layout.addWidget(self._pin_btn)

        # Minimize
        self._min_btn = QPushButton()
        self._min_btn.setFixedSize(26, 26)
        self._min_btn.setToolTip("最小化")
        self._min_btn.clicked.connect(self._win.showMinimized if self._win else None)
        layout.addWidget(self._min_btn)

        # Close
        self._close_btn = QPushButton()
        self._close_btn.setFixedSize(26, 26)
        self._close_btn.setToolTip("关闭")
        self._close_btn.clicked.connect(self._win.close if self._win else None)
        layout.addWidget(self._close_btn)

    def _update_icons(self, is_dark: bool, is_pinned: bool):
        """Refresh icon glyphs for current theme and pin state."""
        if is_dark:
            glyph_c = QColor(200, 200, 210)
            base_r, base_g, base_b = 255, 255, 255
        else:
            glyph_c = QColor(80, 80, 90)
            base_r, base_g, base_b = 0, 0, 0

        # Dark mode button
        icon_fn = _draw_sun if is_dark else _draw_moon
        self._dark_btn.setIcon(_make_glyph_icon(icon_fn, 16, glyph_c))
        self._dark_btn.setIconSize(QSize(16, 16))
        self._dark_btn.setStyleSheet(
            f"QPushButton {{ border: none; border-radius: 13px; "
            f"background-color: rgba({base_r}, {base_g}, {base_b}, 0.10); padding: 0px; }}"
            f"QPushButton:hover {{ background-color: rgba({base_r}, {base_g}, {base_b}, 0.18); }}"
            f"QPushButton:pressed {{ background-color: rgba({base_r}, {base_g}, {base_b}, 0.26); }}"
        )

        # Pin button
        self._pin_btn.setIcon(_make_glyph_icon(_draw_pin, 16, glyph_c))
        self._pin_btn.setIconSize(QSize(16, 16))
        if is_pinned:
            self._pin_btn.setStyleSheet(
                f"QPushButton {{ border: none; border-radius: 13px; "
                f"background-color: rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.30); padding: 0px; }}"
                f"QPushButton:hover {{ background-color: rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.40); }}"
                f"QPushButton:pressed {{ background-color: rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.50); }}"
            )
        else:
            self._pin_btn.setStyleSheet(
                f"QPushButton {{ border: none; border-radius: 13px; "
                f"background-color: rgba({base_r}, {base_g}, {base_b}, 0.10); padding: 0px; }}"
                f"QPushButton:hover {{ background-color: rgba({base_r}, {base_g}, {base_b}, 0.18); }}"
                f"QPushButton:pressed {{ background-color: rgba({base_r}, {base_g}, {base_b}, 0.26); }}"
            )

        # Minimize button
        self._min_btn.setIcon(_make_glyph_icon(_draw_minimize, 16, glyph_c))
        self._min_btn.setIconSize(QSize(16, 16))
        self._min_btn.setStyleSheet(
            f"QPushButton {{ border: none; border-radius: 13px; "
            f"background-color: rgba({base_r}, {base_g}, {base_b}, 0.10); padding: 0px; }}"
            f"QPushButton:hover {{ background-color: rgba({base_r}, {base_g}, {base_b}, 0.18); }}"
            f"QPushButton:pressed {{ background-color: rgba({base_r}, {base_g}, {base_b}, 0.26); }}"
        )

        # Close button — red only on hover
        self._close_btn.setIcon(_make_glyph_icon(_draw_close, 16, glyph_c))
        self._close_btn.setIconSize(QSize(16, 16))
        self._close_btn.setStyleSheet(
            f"QPushButton {{ border: none; border-radius: 13px; "
            f"background-color: rgba({base_r}, {base_g}, {base_b}, 0.10); padding: 0px; }}"
            f"QPushButton:hover {{ background-color: rgba(235, 67, 67, 0.85); }}"
            f"QPushButton:pressed {{ background-color: rgba(200, 50, 50, 0.90); }}"
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().pos()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


class MainWindow(QMainWindow):
    def __init__(self, db: Database, image_handler: ImageHandler,
                 monitor: ClipboardMonitor, is_dark: bool = False):
        super().__init__()
        self._db = db
        self._image_handler = image_handler
        self._monitor = monitor
        self._is_dark = is_dark
        self._is_pinned = False
        self._edge_rects = []
        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geo = None
        self._is_closing = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self._settings = QSettings("ClipboardHistory", "ClipboardHistory")
        self._setup_ui()
        self._setup_tray()
        self._connect_signals()
        self._restore_state()
        self._apply_theme()

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._title_bar = TitleBar(self)
        main_layout.addWidget(self._title_bar)

        self._search_bar = SearchBar(self._is_dark, self)
        main_layout.addWidget(self._search_bar)

        splitter = QSplitter(Qt.Orientation.Vertical, self)
        splitter.setHandleWidth(1)

        self._history_list = HistoryListWidget(self._is_dark, self)
        splitter.addWidget(self._history_list)

        self._preview_panel = PreviewPanel(self._is_dark, self)
        splitter.addWidget(self._preview_panel)

        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        main_layout.addWidget(splitter, 1)

        status_bar = QWidget()
        status_bar.setFixedHeight(36)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(16, 0, 16, 0)

        self._stats_label = QLabel("")
        self._stats_label.setObjectName("statusLabel")
        status_layout.addWidget(self._stats_label)
        status_layout.addStretch()

        self._delete_all_btn = QPushButton("清空记录")
        self._delete_all_btn.setObjectName("dangerButton")
        self._delete_all_btn.setFixedHeight(28)
        self._delete_all_btn.clicked.connect(self._on_delete_all)
        status_layout.addWidget(self._delete_all_btn)

        main_layout.addWidget(status_bar)

    def _setup_tray(self):
        self._tray = QSystemTrayIcon(self)
        tray_pixmap = QPixmap(64, 64)
        tray_pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(tray_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(ACCENT_COLOR))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 14, 14)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        painter.drawText(tray_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "C")
        painter.end()
        self._tray.setIcon(QIcon(tray_pixmap))

        tray_menu = QMenu()
        tray_menu.addAction("显示窗口", self._show_window)
        tray_menu.addSeparator()
        tray_menu.addAction("退出", self._quit_app)
        self._tray.setContextMenu(tray_menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def toggle_dark_mode(self):
        self._is_dark = not self._is_dark
        self._apply_theme()
        self._history_list.set_dark(self._is_dark)
        self._search_bar._is_dark = self._is_dark
        self._title_bar._update_icons(self._is_dark, self._is_pinned)

    def toggle_pin(self):
        self._is_pinned = not self._is_pinned
        flags = self.windowFlags()
        if self._is_pinned:
            self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
        self._title_bar._update_icons(self._is_dark, self._is_pinned)
        self.show()

    def _quit_app(self):
        self._is_closing = True
        self._monitor.stop()
        self._db.close()
        QApplication.quit()

    def _connect_signals(self):
        self._monitor.clipboard_changed.connect(self._on_clipboard_change)
        self._search_bar.search_changed.connect(self._on_search_changed)
        self._search_bar.search_changed.connect(self._search_bar.on_text_changed)
        self._history_list.item_copy_requested.connect(self._on_item_copy)
        self._history_list.item_delete_requested.connect(self._on_item_delete)
        self._history_list.item_preview_requested.connect(self._on_item_preview)

    def _on_clipboard_change(self, data: dict):
        if data["type"] == "text":
            content = data["content"]
            thumbnail = None
        elif data["type"] == "image":
            if "raw_png" in data:
                img = self._image_handler.png_to_image(data["raw_png"])
            else:
                img = self._image_handler.dib_to_image(data["raw_dib"])
            if not img:
                return
            file_path = self._image_handler.save_image(img)
            thumbnail = self._image_handler.create_thumbnail(img)
            content = file_path
        else:
            return

        entry_id = self._db.add_entry(
            data["type"], content, thumbnail, data["hash"], data.get("char_count", 0)
        )
        if entry_id == -1:
            return

        entry = self._db.get_entry_by_id(entry_id)
        if entry:
            self._history_list.add_entry(entry)
            self._update_stats()

    def _on_search_changed(self, query: str):
        entries = self._db.get_all_entries(search_query=query)
        self._history_list.load_entries(entries)
        self._update_stats()

    def _on_item_copy(self, entry_id: int):
        entry = self._db.get_entry_by_id(entry_id)
        if not entry:
            return

        self._monitor.set_skip_next()
        clipboard = QApplication.clipboard()

        if entry["type"] == "text":
            clipboard.setText(entry["content"])
            self._show_toast("已复制")
        elif entry["type"] == "image":
            pixmap = self._image_handler.load_full_image(entry["content"])
            if pixmap:
                clipboard.setPixmap(pixmap)
                self._show_toast("图片已复制")

    def _on_item_delete(self, entry_id: int):
        self._db.delete_entry(entry_id)
        self._refresh_list()
        self._preview_panel.show_empty()

    def _on_delete_all(self):
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要删除所有历史记录吗？此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._db.delete_all()
            self._refresh_list()
            self._preview_panel.show_empty()

    def _on_item_preview(self, entry_id: int):
        entry = self._db.get_entry_by_id(entry_id)
        if not entry:
            return

        if entry["type"] == "text":
            self._preview_panel.show_text(entry["content"])
        elif entry["type"] == "image":
            pixmap = self._image_handler.load_full_image(entry["content"])
            if pixmap:
                self._preview_panel._image_label.setProperty("original_pixmap", pixmap)
                self._preview_panel.show_image(pixmap)

    def _show_toast(self, msg: str):
        toast = QLabel(msg, self)
        toast.setObjectName("toastLabel")
        toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self._is_dark:
            bg = "rgba(237, 237, 239, 0.90)"
            fg = "#1C1C1E"
        else:
            bg = "rgba(28, 28, 30, 0.85)"
            fg = "#FFFFFF"
        toast.setStyleSheet(
            f"QLabel {{ background-color: {bg}; color: {fg}; "
            f"border-radius: 10px; padding: 8px 18px; font-size: 13px; "
            f"font-weight: 500; letter-spacing: 0.5px; }}"
        )
        toast.adjustSize()
        tw = toast.width()
        toast.setGeometry((self.width() - tw) // 2, self.height() // 3, tw, toast.height())
        toast.show()
        QTimer.singleShot(1200, toast.deleteLater)

    def _refresh_list(self):
        query = self._search_bar._search_input.text()
        entries = self._db.get_all_entries(search_query=query)
        self._history_list.load_entries(entries)
        self._update_stats()

    def _update_stats(self):
        stats = self._db.get_stats()
        self._stats_label.setText(
            f"共 {stats['total']} 条 · 文本 {stats['text']} · 图片 {stats['image']}"
        )

    def _load_history(self):
        entries = self._db.get_all_entries()
        self._history_list.load_entries(entries)
        self._update_stats()

    def _apply_theme(self):
        theme = DARK_THEME if self._is_dark else LIGHT_THEME
        self.setStyleSheet(theme)
        self._title_bar._update_icons(self._is_dark, self._is_pinned)

    def _save_state(self):
        self._settings.setValue("pos", self.pos())
        self._settings.setValue("size", self.size())
        self._settings.setValue("is_dark", self._is_dark)

    def _restore_state(self):
        saved_pos = self._settings.value("pos")
        saved_size = self._settings.value("size")

        if saved_size and saved_size.isValid():
            self.resize(saved_size)
        else:
            self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        if saved_pos and saved_pos is not None:
            self.move(saved_pos)
        else:
            screen = QApplication.primaryScreen().availableGeometry()
            x = screen.right() - WINDOW_WIDTH - WINDOW_MARGIN
            y = screen.top() + WINDOW_MARGIN
            self.move(x, y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()

        if self._is_dark:
            bg_color = QColor(10, 10, 15, 238)
            border_color = QColor(255, 255, 255, 18)
            inner_border = QColor(255, 255, 255, 8)
            highlight = QColor(255, 255, 255, 18)
            gloss_stop = QColor(255, 255, 255, 6)
        else:
            bg_color = QColor(235, 240, 250, 232)
            border_color = QColor(180, 200, 230, 30)
            inner_border = QColor(255, 255, 255, 100)
            highlight = QColor(255, 255, 255, 130)
            gloss_stop = QColor(255, 255, 255, 90)

        # Main frosted glass background
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(rect, CORNER_RADIUS, CORNER_RADIUS)

        # Subtle vertical gradient overlay for depth
        overlay = QLinearGradient(rect.x(), rect.y(), rect.x(), rect.y() + rect.height())
        if self._is_dark:
            overlay.setColorAt(0, QColor(255, 255, 255, 5))
            overlay.setColorAt(0.4, QColor(255, 255, 255, 2))
            overlay.setColorAt(1, QColor(0, 0, 0, 12))
        else:
            overlay.setColorAt(0, QColor(220, 235, 255, 50))
            overlay.setColorAt(0.5, QColor(240, 245, 255, 30))
            overlay.setColorAt(1, QColor(200, 215, 240, 20))
        painter.setBrush(QBrush(overlay))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), CORNER_RADIUS - 1, CORNER_RADIUS - 1)

        # Inner border (simulates glass edge refraction)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(inner_border, 1))
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), CORNER_RADIUS - 1, CORNER_RADIUS - 1)

        # Top highlight strip (light source reflection)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(highlight))
        highlight_rect = QRect(rect.x() + 4, rect.y() + 2, rect.width() - 8, 1)
        painter.drawRoundedRect(highlight_rect, 1, 1)

        # Glossy edge at the top
        gloss = QLinearGradient(rect.x(), rect.y(), rect.x(), rect.y() + 30)
        gloss.setColorAt(0, gloss_stop)
        gloss.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(gloss))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect.adjusted(3, 3, -3, 0), CORNER_RADIUS - 2, CORNER_RADIUS - 2)

        painter.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_edge_rects()

    def _update_edge_rects(self):
        r = self.rect()
        m = EDGE_MARGIN
        self._edge_rects = [
            ("left", QRect(0, 0, m, r.height())),
            ("right", QRect(r.width() - m, 0, m, r.height())),
            ("top", QRect(0, 0, r.width(), m)),
            ("bottom", QRect(0, r.height() - m, r.width(), m)),
            ("top_left", QRect(0, 0, m * 2, m * 2)),
            ("top_right", QRect(r.width() - m * 2, 0, m * 2, m * 2)),
            ("bottom_left", QRect(0, r.height() - m * 2, m * 2, m * 2)),
            ("bottom_right", QRect(r.width() - m * 2, r.height() - m * 2, m * 2, m * 2)),
        ]

    def _get_edge_at(self, pos: QPoint) -> str | None:
        for edge, rect in self._edge_rects:
            if rect.contains(pos):
                return edge
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._get_edge_at(event.pos())
            if edge:
                self._resize_edge = edge
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geo = self.geometry()

    def mouseMoveEvent(self, event):
        if self._resize_edge and self._resize_start_pos:
            delta = event.globalPosition().toPoint() - self._resize_start_pos
            geo = self._resize_start_geo
            new_geo = QRect(geo)

            if "right" in self._resize_edge:
                new_geo.setRight(geo.right() + delta.x())
            if "bottom" in self._resize_edge:
                new_geo.setBottom(geo.bottom() + delta.y())
            if "left" in self._resize_edge:
                new_geo.setLeft(geo.left() + delta.x())
            if "top" in self._resize_edge:
                new_geo.setTop(geo.top() + delta.y())

            if new_geo.width() >= WINDOW_MIN_WIDTH and new_geo.height() >= WINDOW_MIN_HEIGHT:
                self.setGeometry(new_geo)
        else:
            edge = self._get_edge_at(event.pos())
            if edge:
                if edge in ("top_left", "bottom_left"):
                    self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                elif edge in ("top_right", "bottom_right"):
                    self.setCursor(Qt.CursorShape.SizeBDiagCursor)
                elif edge in ("left", "right"):
                    self.setCursor(Qt.CursorShape.SizeHorCursor)
                elif edge in ("top", "bottom"):
                    self.setCursor(Qt.CursorShape.SizeVerCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self._resize_edge = None
        self._resize_start_pos = None
        self._resize_start_geo = None

    def closeEvent(self, event):
        self._save_state()
        self._monitor.stop()
        self._db.close()
        event.accept()
