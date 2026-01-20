from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QColorDialog
from PySide6.QtGui import QColor
from skui.base_dialog import BaseFramelessDialog


class ThemeDialog(BaseFramelessDialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="Theme Customizer")
        self.setFixedWidth(350)

        self.content_area.setStyleSheet("""
            QLabel { 
                background: transparent; 
                border: none; 
                color: #ccc; 
                font-weight: bold; 
                font-size: 14px; 
            }

            QPushButton { 
                background-color: #181818; 
                border-radius: 10px; 
                padding: 12px; 
                font-weight: bold; 
                color: white; 
                border: 1px solid #333; 
                margin-bottom: 5px;
            }

            QPushButton:hover { 
                background-color: #333; 
                border: 1px solid #27ae60; 
            }

            QPushButton#done_btn { 
                background-color: #27ae60; 
                border: none; 
                margin-top: 15px; 
            }

            QPushButton#done_btn:hover { 
                background-color: #2ecc71; 
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = self.content_layout

        layout.addWidget(QLabel("CUSTOMIZE COLORS"))

        options = [
            ("Main Background", "bg_color"),
            ("Sidebar Buttons", "btn_color"),
            ("Play Button & Logs", "accent_color"),
            ("Library Header", "lib_color"),
            ("Title Bar", "title_bar_color")
        ]

        for text, key in options:
            btn = QPushButton(f"Pick {text}")
            btn.clicked.connect(lambda checked=False, k=key: self.pick_color(k))
            layout.addWidget(btn)

        close_btn = QPushButton("Done")
        close_btn.setObjectName("done_btn")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def pick_color(self, key):
        if not self.parent(): return

        current_color = getattr(self.parent(), key, "#050505")
        color = QColorDialog.getColor(initial=QColor(current_color), parent=self, title=f"Select {key}")

        if color.isValid():
            setattr(self.parent(), key, color.name())
            if hasattr(self.parent(), "apply_theme"):
                self.parent().apply_theme()