import os
import uuid
from io import BytesIO

from PIL import Image
from PyQt6.QtGui import QImage, QPixmap

from config import IMAGES_DIR, THUMBNAIL_SIZE, THUMBNAIL_QUALITY


class ImageHandler:
    @staticmethod
    def png_to_image(png_data: bytes) -> Image.Image | None:
        """Open image from raw PNG bytes (clipboard format)."""
        try:
            return Image.open(BytesIO(png_data))
        except Exception:
            return None

    @staticmethod
    def dib_to_image(dib_data: bytes) -> Image.Image | None:
        """Convert DIB clipboard data to PIL Image via proper BMP reconstruction."""
        try:
            import struct
            # Build a valid BMP file: file header (14 bytes) + full DIB data
            dib_size = len(dib_data)
            file_size = 14 + dib_size
            pixel_offset = 14 + 40  # file header + BITMAPINFOHEADER
            bmp_header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, pixel_offset)
            return Image.open(BytesIO(bmp_header + dib_data))
        except Exception:
            return None

    @staticmethod
    def save_image(img: Image.Image) -> str:
        file_path = os.path.join(IMAGES_DIR, f"{uuid.uuid4().hex}.png")
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
            img.save(file_path, "PNG")
        else:
            img = img.convert("RGB")
            img.save(file_path, "PNG")
        return file_path

    @staticmethod
    def create_thumbnail(img: Image.Image) -> bytes:
        thumb = img.copy()
        thumb.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        if thumb.mode == "RGBA":
            background = Image.new("RGB", thumb.size, (255, 255, 255))
            background.paste(thumb, mask=thumb.split()[3])
            thumb = background
        elif thumb.mode != "RGB":
            thumb = thumb.convert("RGB")
        buf = BytesIO()
        thumb.save(buf, "JPEG", quality=THUMBNAIL_QUALITY)
        return buf.getvalue()

    @staticmethod
    def load_thumbnail(thumbnail_bytes: bytes) -> QPixmap:
        qimg = QImage()
        qimg.loadFromData(thumbnail_bytes)
        return QPixmap.fromImage(qimg)

    @staticmethod
    def load_full_image(file_path: str) -> QPixmap | None:
        if not os.path.exists(file_path):
            return None
        pixmap = QPixmap(file_path)
        return pixmap if not pixmap.isNull() else None

    @staticmethod
    def cleanup_old_images(days_old: int = 30):
        import time
        cutoff = time.time() - days_old * 86400
        for filename in os.listdir(IMAGES_DIR):
            filepath = os.path.join(IMAGES_DIR, filename)
            if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff:
                os.remove(filepath)
