# -*- coding: utf-8 -*-
from functools import lru_cache
from PyQt6.QtCore import Qt, QSize, QRect, QRectF, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPixmap, QPen, QBrush, QPainterPath
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle

from config import FONT_FAMILY, FONT_FALLBACK, THUMBNAIL_SIZE, ACCENT_R, ACCENT_G, ACCENT_B

_thumbnail_cache: dict[tuple[bytes, int], QPixmap] = {}
_CACHE_MAX_SIZE = 120


def _icon_color(is_dark: bool) -> QColor:
    return QColor(237, 237, 239) if is_dark else QColor(60, 60, 67)


def _get_cached_thumbnail(thumbnail_data: bytes, size: int) -> QPixmap | None:
    cache_key = (thumbnail_data, size)
    if cache_key in _thumbnail_cache:
        return _thumbnail_cache[cache_key]

    pixmap = QPixmap()
    pixmap.loadFromData(thumbnail_data)
    if pixmap.isNull():
        return None

    scaled = pixmap.scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )

    if len(_thumbnail_cache) >= _CACHE_MAX_SIZE:
        _thumbnail_cache.clear()
    _thumbnail_cache[cache_key] = scaled
    return scaled


_font_cache: dict[tuple[str, int], QFont] = {}


def _get_font(family: str, size: int) -> QFont:
    key = (family, size)
    if key not in _font_cache:
        _font_cache[key] = QFont(family, size)
    return _font_cache[key]


def _draw_text_icon(p: QPainter, rect: QRect, color: QColor):
    """Document icon — clean outline with text lines."""
    ox, oy = rect.x() + 3, rect.y() + 2
    p.setPen(QPen(color, 1.3))
    p.setBrush(Qt.BrushStyle.NoBrush)
    # Document body
    path = QPainterPath()
    path.moveTo(ox + 7, oy + 3)
    path.lineTo(ox + 18, oy + 3)
    path.lineTo(ox + 22, oy + 7)
    path.lineTo(ox + 22, oy + 24)
    path.lineTo(ox + 7, oy + 24)
    path.closeSubpath()
    p.drawPath(path)
    # Text lines
    p.setPen(QPen(color, 1.0))
    p.drawLine(ox + 10, oy + 11, ox + 19, oy + 11)
    p.drawLine(ox + 10, oy + 15, ox + 18, oy + 15)
    p.drawLine(ox + 10, oy + 19, ox + 15, oy + 19)


def _draw_image_icon(p: QPainter, rect: QRect, color: QColor):
    """Image icon — frame with mountain and sun."""
    ox, oy = rect.x() + 3, rect.y() + 2
    p.setPen(QPen(color, 1.3))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(ox + 5, oy + 1, 20, 22, 4, 4)
    # Mountains
    p.setPen(QPen(color, 1.1))
    p.drawLine(ox + 7, oy + 19, ox + 12, oy + 11)
    p.drawLine(ox + 12, oy + 11, ox + 17, oy + 16)
    p.drawLine(ox + 17, oy + 16, ox + 23, oy + 7)
    # Sun
    p.drawEllipse(QPoint(ox + 19, oy + 5), 3, 3)


class HistoryItemDelegate(QStyledItemDelegate):
    ROW_HEIGHT = 48
    ICON_SIZE = 28
    PADDING = 10

    def __init__(self, is_dark: bool = False, parent=None):
        super().__init__(parent)
        self._is_dark = is_dark

    def set_dark(self, is_dark: bool):
        self._is_dark = is_dark

    def paint(self, painter: QPainter, option, index):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = option.rect
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = option.state & QStyle.StateFlag.State_MouseOver

        # Draw selection background — accent blue highlight
        if is_selected:
            if self._is_dark:
                painter.setBrush(QBrush(QColor(ACCENT_R, ACCENT_G, ACCENT_B, 60)))
                painter.setPen(QPen(QColor(ACCENT_R, ACCENT_G, ACCENT_B, 80), 1))
            else:
                painter.setBrush(QBrush(QColor(ACCENT_R, ACCENT_G, ACCENT_B, 55)))
                painter.setPen(QPen(QColor(ACCENT_R, ACCENT_G, ACCENT_B, 70), 1))
            painter.drawRoundedRect(rect.adjusted(3, 2, -3, -2), 10, 10)
        elif is_hovered:
            if self._is_dark:
                painter.setBrush(QBrush(QColor(255, 255, 255, 8)))
            else:
                painter.setBrush(QBrush(QColor(0, 0, 0, 6)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect.adjusted(3, 2, -3, -2), 10, 10)

        item_data = index.data(Qt.ItemDataRole.UserRole)
        if not item_data:
            return

        entry_type = item_data.get("type", "text")
        content = item_data.get("content", "")
        thumbnail_data = item_data.get("thumbnail")
        created_at = item_data.get("created_at", "")

        icon_rect = QRect(
            rect.x() + self.PADDING + 2,
            rect.y() + (rect.height() - self.ICON_SIZE) // 2,
            self.ICON_SIZE,
            self.ICON_SIZE,
        )

        icon_c = _icon_color(self._is_dark)
        text_c = QColor(28, 28, 30) if not self._is_dark else QColor(237, 237, 239)
        secondary_c = QColor(28, 28, 30, 110) if not self._is_dark else QColor(237, 237, 239, 100)
        accent_c = QColor(ACCENT_R, ACCENT_G, ACCENT_B)

        if entry_type == "image" and thumbnail_data:
            scaled = _get_cached_thumbnail(thumbnail_data, self.ICON_SIZE)
            if scaled:
                x = icon_rect.x() + (self.ICON_SIZE - scaled.width()) // 2
                y = icon_rect.y() + (self.ICON_SIZE - scaled.height()) // 2
                path = QPainterPath()
                path.addRoundedRect(QRectF(x, y, scaled.width(), scaled.height()), 6, 6)
                painter.setClipPath(path)
                painter.drawPixmap(x, y, scaled)
                painter.setClipping(False)
        else:
            _draw_text_icon(painter, icon_rect, icon_c)

        # Content area — leave just enough room for the timestamp
        time_area = 42
        content_x = icon_rect.right() + 10
        content_w = rect.width() - content_x - self.PADDING - time_area
        content_rect = QRect(content_x, rect.y() + 8, max(content_w, 30), rect.height() - 18)

        # Title / preview text
        preview_font = _get_font(FONT_FAMILY, 11)
        painter.setFont(preview_font)
        painter.setPen(text_c)

        if entry_type == "text":
            display_text = content.replace("\n", " ").replace("\r", "")
            # Let Qt handle elision based on available width
            elided = painter.fontMetrics().elidedText(
                display_text, Qt.TextElideMode.ElideRight, content_rect.width()
            )
            painter.drawText(
                content_rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                elided,
            )
        else:
            painter.drawText(
                content_rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                "图片",
            )

        # Type label (below content)
        type_font = _get_font(FONT_FAMILY, 8)
        painter.setFont(type_font)
        type_c = QColor(28, 28, 30, 100) if not self._is_dark else QColor(237, 237, 239, 80)
        painter.setPen(type_c)
        type_label = "文本" if entry_type == "text" else "图片"
        type_rect = QRect(content_x, rect.y() + rect.height() - 16, 32, 12)
        painter.drawText(type_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, type_label)

        # Timestamp
        time_font = _get_font(FONT_FAMILY, 8)
        painter.setFont(time_font)
        painter.setPen(secondary_c)

        time_display = ""
        if created_at:
            try:
                time_display = created_at.split("T")[1][:5] if "T" in created_at else created_at[-8:-3]
            except (IndexError, ValueError):
                time_display = created_at[-8:]

        time_rect = QRect(rect.right() - 42, rect.y() + 8, 36, rect.height() - 18)
        painter.drawText(time_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, time_display)

    def sizeHint(self, option, index):
        width = option.rect.width() if option else 300
        return QSize(width, self.ROW_HEIGHT)
