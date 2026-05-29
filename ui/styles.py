# -*- coding: utf-8 -*-
from config import FONT_FAMILY, FONT_FALLBACK, CORNER_RADIUS, ACCENT_R, ACCENT_G, ACCENT_B

FONT = f"{FONT_FAMILY}, {FONT_FALLBACK}, sans-serif"
A = f"rgb({ACCENT_R}, {ACCENT_G}, {ACCENT_B})"
A_HOVER = f"rgb({ACCENT_R + 20}, {ACCENT_G + 20}, {ACCENT_B - 20})"

# Light theme — warm white base, translucent surfaces, subtle borders
LIGHT_THEME = f"""
QMainWindow, QWidget#centralWidget {{
    background-color: transparent;
}}

QListWidget {{
    background-color: transparent;
    border: none;
    outline: none;
    font-family: {FONT};
    font-size: 10px;
    padding: 4px 0;
}}
QListWidget::item {{
    background-color: rgba(255, 255, 255, 0.55);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 10px;
    padding: 10px 12px;
    margin: 2px 8px;
    color: #1C1C1E;
}}
QListWidget::item:selected {{
    background-color: rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.22);
    border: 1px solid rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.30);
}}
QListWidget::item:hover {{
    background-color: rgba(255, 255, 255, 0.72);
    border: 1px solid rgba(0, 0, 0, 0.08);
}}

QLineEdit {{
    background-color: rgba(255, 255, 255, 0.55);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 10px;
    padding: 9px 14px;
    font-family: {FONT};
    font-size: 10px;
    color: #1C1C1E;
    selection-background-color: rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.25);
}}
QLineEdit:focus {{
    border: 1px solid rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.45);
    background-color: rgba(255, 255, 255, 0.75);
}}
QLineEdit::placeholder {{
    color: rgba(28, 28, 30, 0.30);
}}

QPushButton {{
    background-color: rgba(255, 255, 255, 0.50);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 8px;
    padding: 6px 14px;
    font-family: {FONT};
    font-size: 10px;
    color: #1C1C1E;
}}
QPushButton:hover {{
    background-color: rgba(255, 255, 255, 0.70);
    border: 1px solid rgba(0, 0, 0, 0.08);
}}
QPushButton:pressed {{
    background-color: rgba(0, 0, 0, 0.06);
}}
QPushButton#dangerButton {{
    color: #DC2626;
}}
QPushButton#dangerButton:hover {{
    background-color: rgba(220, 38, 38, 0.08);
    border: 1px solid rgba(220, 38, 38, 0.18);
}}

QTextEdit {{
    background-color: transparent;
    border: none;
    font-family: {FONT};
    font-size: 12px;
    color: #1C1C1E;
    line-height: 1.6;
    selection-background-color: rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.2);
}}

QLabel {{
    background-color: transparent;
    font-family: {FONT};
    color: #1C1C1E;
}}
QLabel#titleLabel {{
    font-size: 14px;
    font-weight: 600;
    color: #1C1C1E;
    letter-spacing: 0.3px;
    padding-top: 3px;
}}
QLabel#statusLabel {{
    font-size: 10px;
    color: rgba(28, 28, 30, 0.45);
}}
QLabel#emptyLabel {{
    font-size: 10px;
    color: rgba(28, 28, 30, 0.30);
}}

QWidget#previewPanel {{
    background-color: rgba(210, 225, 248, 0.55);
    border-top: 1px solid rgba(0, 0, 0, 0.10);
    border-radius: 0 0 {CORNER_RADIUS}px {CORNER_RADIUS}px;
}}

QSplitter::handle {{
    background-color: rgba(0, 0, 0, 0.15);
    height: 1px;
    margin: 0 10px;
}}

QMenu {{
    background-color: rgba(255, 255, 255, 0.94);
    border: 1px solid rgba(0, 0, 0, 0.10);
    border-radius: 12px;
    padding: 6px;
    font-family: {FONT};
    font-size: 10px;
    color: #1C1C1E;
}}
QMenu::item {{
    padding: 8px 32px 8px 14px;
    border-radius: 7px;
    margin: 1px 0;
}}
QMenu::item:selected {{
    background-color: rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.10);
    color: {A};
}}
QMenu::separator {{
    height: 1px;
    background-color: rgba(0, 0, 0, 0.06);
    margin: 4px 10px;
}}

QScrollBar:vertical {{
    background-color: transparent;
    width: 6px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background-color: rgba(0, 0, 0, 0.10);
    border-radius: 3px;
    min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: rgba(0, 0, 0, 0.18);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QToolTip {{
    background-color: rgba(28, 28, 30, 0.90);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 7px;
    padding: 6px 10px;
    font-family: {FONT};
    font-size: 10px;
}}
"""

# Dark theme — deep base, translucent elevated surfaces, indigo accent
DARK_THEME = f"""
QMainWindow, QWidget#centralWidget {{
    background-color: transparent;
}}

QListWidget {{
    background-color: transparent;
    border: none;
    outline: none;
    font-family: {FONT};
    font-size: 10px;
    padding: 4px 0;
}}
QListWidget::item {{
    background-color: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 10px 12px;
    margin: 2px 8px;
    color: #EDEDEF;
}}
QListWidget::item:selected {{
    background-color: rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.22);
    border: 1px solid rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.30);
}}
QListWidget::item:hover {{
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.07);
}}

QLineEdit {{
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 9px 14px;
    font-family: {FONT};
    font-size: 10px;
    color: #EDEDEF;
    selection-background-color: rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.30);
}}
QLineEdit:focus {{
    border: 1px solid rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.40);
    background-color: rgba(255, 255, 255, 0.08);
}}
QLineEdit::placeholder {{
    color: rgba(237, 237, 239, 0.25);
}}

QPushButton {{
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 6px 14px;
    font-family: {FONT};
    font-size: 10px;
    color: #EDEDEF;
}}
QPushButton:hover {{
    background-color: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.10);
}}
QPushButton:pressed {{
    background-color: rgba(255, 255, 255, 0.14);
}}
QPushButton#dangerButton {{
    color: #F87171;
}}
QPushButton#dangerButton:hover {{
    background-color: rgba(248, 113, 113, 0.10);
    border: 1px solid rgba(248, 113, 113, 0.16);
}}

QTextEdit {{
    background-color: transparent;
    border: none;
    font-family: {FONT};
    font-size: 12px;
    color: #EDEDEF;
    line-height: 1.6;
    selection-background-color: rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.25);
}}

QLabel {{
    background-color: transparent;
    font-family: {FONT};
    color: #EDEDEF;
}}
QLabel#titleLabel {{
    font-size: 14px;
    font-weight: 600;
    color: #EDEDEF;
    letter-spacing: 0.3px;
}}
QLabel#statusLabel {{
    font-size: 10px;
    color: rgba(237, 237, 239, 0.40);
}}
QLabel#emptyLabel {{
    font-size: 10px;
    color: rgba(237, 237, 239, 0.22);
}}

QWidget#previewPanel {{
    background-color: rgba(18, 22, 40, 0.65);
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 0 0 {CORNER_RADIUS}px {CORNER_RADIUS}px;
}}

QSplitter::handle {{
    background-color: rgba(255, 255, 255, 0.12);
    height: 1px;
    margin: 0 10px;
}}

QMenu {{
    background-color: rgba(20, 20, 28, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 6px;
    font-family: {FONT};
    font-size: 10px;
    color: #EDEDEF;
}}
QMenu::item {{
    padding: 8px 32px 8px 14px;
    border-radius: 7px;
    margin: 1px 0;
}}
QMenu::item:selected {{
    background-color: rgba({ACCENT_R}, {ACCENT_G}, {ACCENT_B}, 0.15);
    color: rgb({ACCENT_R + 40}, {ACCENT_G + 40}, {ACCENT_B});
}}
QMenu::separator {{
    height: 1px;
    background-color: rgba(255, 255, 255, 0.06);
    margin: 4px 10px;
}}

QScrollBar:vertical {{
    background-color: transparent;
    width: 6px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background-color: rgba(255, 255, 255, 0.10);
    border-radius: 3px;
    min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: rgba(255, 255, 255, 0.18);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QToolTip {{
    background-color: rgba(10, 10, 15, 0.92);
    color: #EDEDEF;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 7px;
    padding: 6px 10px;
    font-family: {FONT};
    font-size: 10px;
}}
"""
