import hashlib

import win32clipboard
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from config import POLL_INTERVAL_MS

CF_DIB = 8
CF_DIBV5 = 17
CF_BITMAP = 2


def _get_png_format_id() -> int:
    """Get the registered clipboard format ID for image/png."""
    try:
        return win32clipboard.RegisterClipboardFormat("image/png")
    except Exception:
        return 0


PNG_FMT = _get_png_format_id()


class ClipboardMonitor(QObject):
    clipboard_changed = pyqtSignal(dict)

    def __init__(self, poll_interval_ms: int = POLL_INTERVAL_MS):
        super().__init__()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)
        self._poll_interval = poll_interval_ms
        self._last_text_hash: str = ""
        self._last_image_hash: str = ""
        self._skip_next: bool = False

    def start(self):
        self._timer.start(self._poll_interval)

    def stop(self):
        self._timer.stop()

    def set_skip_next(self):
        self._skip_next = True

    def _poll(self):
        if self._skip_next:
            self._skip_next = False
            self._update_hashes()
            return

        try:
            win32clipboard.OpenClipboard()
            try:
                # PNG first — most reliable, avoids DIB header issues
                if PNG_FMT and win32clipboard.IsClipboardFormatAvailable(PNG_FMT):
                    self._check_png()
                    return
                # Fall back to DIB formats
                if win32clipboard.IsClipboardFormatAvailable(CF_DIB):
                    self._check_dib()
                    return
                if win32clipboard.IsClipboardFormatAvailable(CF_DIBV5):
                    self._check_dib(CF_DIBV5)
                    return
                if win32clipboard.IsClipboardFormatAvailable(CF_BITMAP):
                    self._check_bitmap()
                    return
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                    self._check_text()
            finally:
                win32clipboard.CloseClipboard()
        except Exception:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass

    def _check_text(self):
        try:
            data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            content_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
            if content_hash != self._last_text_hash:
                self._last_text_hash = content_hash
                self.clipboard_changed.emit({
                    "type": "text",
                    "content": data,
                    "hash": content_hash,
                    "char_count": len(data),
                })
        except Exception:
            pass

    def _check_png(self):
        try:
            data = win32clipboard.GetClipboardData(PNG_FMT)
            content_hash = hashlib.sha256(data).hexdigest()
            if content_hash != self._last_image_hash:
                self._last_image_hash = content_hash
                self.clipboard_changed.emit({
                    "type": "image",
                    "raw_png": data,
                    "hash": content_hash,
                    "char_count": len(data),
                })
        except Exception:
            pass

    def _check_dib(self, fmt: int = CF_DIB):
        try:
            data = win32clipboard.GetClipboardData(fmt)
            content_hash = hashlib.sha256(data).hexdigest()
            if content_hash != self._last_image_hash:
                self._last_image_hash = content_hash
                self.clipboard_changed.emit({
                    "type": "image",
                    "raw_dib": data,
                    "hash": content_hash,
                    "char_count": len(data),
                })
        except Exception:
            pass

    def _check_bitmap(self):
        try:
            hbitmap = win32clipboard.GetClipboardData(CF_BITMAP)
            dib_data = self._bitmap_to_dib(hbitmap)
            if dib_data is None:
                return
            content_hash = hashlib.sha256(dib_data).hexdigest()
            if content_hash != self._last_image_hash:
                self._last_image_hash = content_hash
                self.clipboard_changed.emit({
                    "type": "image",
                    "raw_dib": dib_data,
                    "hash": content_hash,
                    "char_count": len(dib_data),
                })
        except Exception:
            pass

    def _bitmap_to_dib(self, hbitmap) -> bytes | None:
        try:
            import ctypes
            from ctypes import wintypes
            import struct

            gdi32 = ctypes.windll.gdi32

            class BITMAP(ctypes.Structure):
                _fields_ = [
                    ("bmType", wintypes.LONG),
                    ("bmWidth", wintypes.LONG),
                    ("bmHeight", wintypes.LONG),
                    ("bmWidthBytes", wintypes.LONG),
                    ("bmPlanes", wintypes.WORD),
                    ("bmBitsPixel", wintypes.WORD),
                    ("bmBits", wintypes.LPVOID),
                ]

            bm = BITMAP()
            gdi32.GetObjectW(hbitmap, ctypes.sizeof(bm), ctypes.byref(bm))

            w = bm.bmWidth
            h = bm.bmHeight
            bpp = bm.bmBitsPixel
            buf_size = bm.bmWidthBytes * abs(h)
            buf = ctypes.create_string_buffer(buf_size)
            gdi32.GetBitmapBits(hbitmap, buf_size, buf)

            header_size = 40
            dib = bytearray()
            dib.extend(struct.pack('<IiiHHIIiiII',
                header_size, w, h, 1, bpp, 0, buf_size, 0, 0, 0, 0))
            dib.extend(buf.raw)
            return bytes(dib)
        except Exception:
            return None

    def _update_hashes(self):
        try:
            win32clipboard.OpenClipboard()
            try:
                if PNG_FMT and win32clipboard.IsClipboardFormatAvailable(PNG_FMT):
                    data = win32clipboard.GetClipboardData(PNG_FMT)
                    self._last_image_hash = hashlib.sha256(data).hexdigest()
                elif win32clipboard.IsClipboardFormatAvailable(CF_DIB):
                    data = win32clipboard.GetClipboardData(CF_DIB)
                    self._last_image_hash = hashlib.sha256(data).hexdigest()
                elif win32clipboard.IsClipboardFormatAvailable(CF_UNICODETEXT):
                    data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                    self._last_text_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
            finally:
                win32clipboard.CloseClipboard()
        except Exception:
            pass
