from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt

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
        layout.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(self.W, self.H)
        self.img_lbl = QLabel()
        self.img_lbl.setScaledContents(False)
        self.img_lbl.setStyleSheet("background: transparent;")

        pix = QPixmap(self.game.get("banner", ""))
        
        if not pix.isNull():
            rounded_pix = self.get_rounded_pixmap(pix, self.W, self.H, radius=15)
            self.img_lbl.setPixmap(rounded_pix)
        else:
            self.img_lbl.setText("NO IMAGE")
            self.img_lbl.setAlignment(Qt.AlignCenter)
            self.img_lbl.setStyleSheet("background-color: #151515; border-radius: 15px; color: #333;")

        layout.addWidget(self.img_lbl)
        self.update_style()

    def get_rounded_pixmap(self, pixmap, w, h, radius):
        
        scaled_pix = pixmap.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        target = QPixmap(w, h)
        target.fill(Qt.transparent)
        painter = QPainter(target)
        painter.setRenderHint(QPainter.Antialiasing, True) 
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled_pix)
        painter.end()
        return target

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
