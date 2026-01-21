from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt, QRectF


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

        # ضبط حجم الفريم بدقة
        self.setFixedSize(self.W, self.H)

        self.img_lbl = QLabel()
        self.img_lbl.setScaledContents(False)
        self.img_lbl.setStyleSheet("background: transparent;")

        # التأكد من أن الليبل يأخذ حجم الفريم بالكامل
        self.img_lbl.setFixedSize(self.W, self.H)

        pix = QPixmap(self.game.get("banner", ""))

        if not pix.isNull():
            # قص الصورة مع تحديد نصف قطر الزاوية (مثلاً 15)
            rounded_pix = self.round_image(pix, self.W, self.H, radius=15)
            self.img_lbl.setPixmap(rounded_pix)
        else:
            self.img_lbl.setText("NO IMAGE")
            self.img_lbl.setAlignment(Qt.AlignCenter)
            self.img_lbl.setStyleSheet("background-color: #151515; border-radius: 15px; color: #333;")

        layout.addWidget(self.img_lbl)
        self.update_style()

    def round_image(self, pixmap, w, h, radius):
        # 1. إنشاء صورة فارغة بنفس الحجم المطلوب تماماً
        target = QPixmap(w, h)
        target.fill(Qt.transparent)

        # 2. تحجيم الصورة الأصلية لتملأ الأبعاد المطلوبة (Crop/Fill)
        # نستخدم KeepAspectRatioByExpanding لضمان عدم وجود فراغات بيضاء
        scaled_pix = pixmap.scaled(w, h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # قص الزوائد من الصورة المحجمة لتصبح بنفس حجم الهدف بالضبط
        # هذا يضمن أن الصورة تبدأ من (0,0) وتنتهي عند (w,h)
        scaled_pix = scaled_pix.copy(0, 0, w, h)

        # 3. الرسم والقص
        painter = QPainter(target)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # إنشاء مسار القص
        path = QPainterPath()
        # نستخدم QRectF لضمان الدقة
        path.addRoundedRect(QRectF(0, 0, w, h), radius, radius)

        # تفعيل القص
        painter.setClipPath(path)

        # رسم الصورة
        painter.drawPixmap(0, 0, scaled_pix)
        painter.end()

        return target

    def update_selection_color(self, color):
        self.selection_color = color
        self.update_style()

    def update_style(self):
        border_color = self.selection_color if self.is_selected else "transparent"

        # جعل border-radius للفريم متطابقاً أو أكبر قليلاً من الصورة
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
