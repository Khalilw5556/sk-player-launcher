from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRectF


class RoundedLabel(QLabel):
    def __init__(self, pixmap, radius=15):
        super().__init__()
        self.pixmap = pixmap
        self.radius = radius
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        if self.pixmap.isNull():
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        rect = self.rect()
        
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), self.radius, self.radius)

        painter.setClipPath(path)

        scaled_pix = self.pixmap.scaled(rect.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(rect, scaled_pix)


class GameCard(QFrame):
    def __init__(self, game, callback):
        super().__init__()
        self.game, self.callback = game, callback
        self.is_selected = False
        self.selection_color = "#27ae60"
        self.setObjectName("GameCard")

        self.banner_type = self.game.get("banner_type", "long")
        if self.banner_type == "wide":
            self.H = 160
            self.W = int(self.H * (1920 / 620))
        else:
            self.H = 260
            self.W = int(self.H * (600 / 900))

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self.setFixedSize(self.W, self.H)

        pix = QPixmap(self.game.get("banner", ""))

        if not pix.isNull():
            self.img_lbl = RoundedLabel(pix, radius=15)
        else:
            self.img_lbl = QLabel("NO IMAGE")
            self.img_lbl.setAlignment(Qt.AlignCenter)
            self.img_lbl.setStyleSheet("background-color: #151515; border-radius: 15px; color: #333;")

        layout.addWidget(self.img_lbl)
        self.update_style()

    def update_selection_color(self, color):
        self.selection_color = color
        self.update_style()

    def update_style(self):
        border_color = self.selection_color if self.is_selected else "transparent"

        self.setStyleSheet(f"""
            #GameCard {{ 
                border: 4px solid {border_color}; 
                border-radius: 19px; 
                background: transparent; 
            }}
        """)

    def set_selected(self, state):
        self.is_selected = state
        self.update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.callback(self)
