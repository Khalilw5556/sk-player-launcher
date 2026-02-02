from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from skui.title_bar import CustomTitleBar


class BaseFramelessDialog(QDialog):
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        pal = self.palette()
        pal.setColor(QPalette.Highlight, QColor(0, 0, 0, 0))
        self.setPalette(pal)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)

        self.container = QWidget()
        self.container.setObjectName("DialogContainer")

        self.container.setStyleSheet("""
            #DialogContainer {
                background-color: #0a0a0a;
                border-radius: 20px;
                border: 1px solid #333;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.container.setGraphicsEffect(shadow)

        self.main_layout.addWidget(self.container)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, title_text=title)
        self.title_bar.min_btn.hide()
        self.title_bar.max_btn.hide()
        self.container_layout.addWidget(self.title_bar)

        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")

        self.content_area.setStyleSheet("#ContentArea { background: transparent; }")

        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(15)

        self.container_layout.addWidget(self.content_area)

        self.title_bar.update_radius_shadow()

    def set_content_layout(self, layout):
        pass