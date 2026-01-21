from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
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
        self.img_lbl.setScaledContents(True)
        
        # تم حذف border-radius من هنا لتصبح الصورة حادة الزوايا
        self.img_lbl.setStyleSheet("background-color: #111;")

        pix = QPixmap(self.game.get("banner", ""))
        if not pix.isNull():
            self.img_lbl.setPixmap(pix)
        else:
            self.img_lbl.setText("NO IMAGE")
            self.img_lbl.setAlignment(Qt.AlignCenter)
            # تم حذف border-radius من هنا أيضاً
            self.img_lbl.setStyleSheet("background-color: #151515; color: #333;")

        layout.addWidget(self.img_lbl)
        self.update_style()

    def update_selection_color(self, color):
        self.selection_color = color
        self.update_style()

    def update_style(self):
        # تم تعديل الإطار ليكون فقط عند التحديد، وبدون انحناءات
        if self.is_selected:
            border_style = f"5px solid {self.selection_color}"
            # لتعويض مساحة الإطار حتى لا تصغر الصورة عند التحديد (اختياري، يعتمد على تفضيلك)
            # يمكنك جعل الهوامش 0 إذا كنت تريد الإطار فوق الصورة
        else:
            border_style = "none" # إزالة الإطار تماماً عند عدم التحديد

        # تم حذف border-radius: 19px; من الستايل
        self.setStyleSheet(f"""
            #GameCard {{ 
                border: {border_style}; 
                background: transparent; 
            }}
        """)

    def set_selected(self, state):
        self.is_selected = state
        self.update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.callback(self)
