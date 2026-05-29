import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
DB_PATH = os.path.join(DATA_DIR, "clipboard_history.db")

POLL_INTERVAL_MS = 500
THUMBNAIL_SIZE = (100, 100)
THUMBNAIL_QUALITY = 85
MAX_HISTORY = 500

WINDOW_WIDTH = 260
WINDOW_HEIGHT = 440
WINDOW_MIN_WIDTH = 220
WINDOW_MIN_HEIGHT = 220
CORNER_RADIUS = 14
WINDOW_MARGIN = 20

FONT_FAMILY = "Microsoft YaHei"
FONT_FALLBACK = "Segoe UI"

ACCENT_R = 108
ACCENT_G = 123
ACCENT_B = 255

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
