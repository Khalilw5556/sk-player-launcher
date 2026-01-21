from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRect

# --- 1. كلاس جديد مخصص لرسم الصورة بحواف ناعمة جداً ---
class RoundedLabel(QLabel):
    def __init__(self, pixmap, radius=15):
        super().__init__()
        self.pixmap = pixmap
        self.radius = radius
        # جعل الخلفية شفافة
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        if self.pixmap.isNull():
            super().paintEvent(event)
            return

        painter = QPainter(self)
        # تفعيل التنعيم (Antialiasing) للحواف والصورة
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # تحديد مساحة الرسم الدقيقة للـ Label
        rect = self.rect()

        # إنشاء مسار مقصوص بـ 4 زوايا
        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)

        # تطبيق القص
        painter.setClipPath(path)

        # تحجيم الصورة لتناسب المساحة تماماً ورسمها
        scaled_pix = self.pixmap.scaled(rect.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(rect, scaled_pix)


# --- 2. كارد اللعبة ---
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
        # أضفت هامش بسيط (4 بكسل) ليترك مساحة للإطار الخارجي عند التحديد
        layout.setContentsMargins(4, 4, 4, 4) 
        self.setFixedSize(self.W, self.H)

        pix = QPixmap(self.game.get("banner", ""))
        
        # استخدام الكلاس المخصص بدلاً من QLabel العادي
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
        
        # تم تعديل radius ليكون متناسقاً مع الهوامش
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
