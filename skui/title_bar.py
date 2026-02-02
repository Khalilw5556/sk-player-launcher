from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class CustomTitleBar(QWidget):
    def __init__(self, parent=None, title_text="SK PLAYER | LAUNCHER"):
        super().__init__(parent)
        self.parent = parent

        self.setFixedHeight(42)
        self.setObjectName("TitleBar")

        self.setStyleSheet("""
            #TitleBar {
                background-color: #050505;
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
            }
            QLabel {
                color: #ccc;
                font-weight: bold;
                font-size: 11px;
                letter-spacing: 2px;
                margin-left: 18px;
                background: transparent;
                border: none;
            }
            QPushButton {
                background: transparent;
                border: none;
                width: 46px;
                height: 42px;
                color: #555;
                font-size: 14px;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #111;
                color: #eee;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_label = QLabel(title_text)
        layout.addWidget(self.title_label)
        layout.addStretch()

        self.min_btn = QPushButton("—")
        self.max_btn = QPushButton("⬜")
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close_btn")

        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        self.min_btn.clicked.connect(self.parent.showMinimized)
        self.max_btn.clicked.connect(self.handle_max_restore)
        self.close_btn.clicked.connect(self.parent.close)

        self.mouseDoubleClickEvent = self.handle_double_click
        self.start_pos = None

        self.update_radius_shadow()

    def set_title(self, text):
        self.title_label.setText(text.upper())

    def handle_max_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
        self.update_radius_shadow()

    def handle_double_click(self, event):
        if event.button() == Qt.LeftButton:
            self.handle_max_restore()

    def update_radius_shadow(self):
        if not hasattr(self.parent, "container"):
            return

        if self.parent.isMaximized():
            self.parent.container.setGraphicsEffect(None)
            self.parent.layout().setContentsMargins(0, 0, 0, 0)
            self.parent.container.setStyleSheet("border-radius:0px; background:#080808;")
            self.max_btn.setText("❐")
            self.close_btn.setStyleSheet("""
                QPushButton { background: transparent; border: none; width: 46px; height: 42px; color: #555; font-size: 14px; border-radius: 0px; }
                QPushButton:hover { background-color: #c0392b; color: white; border-radius: 0px; }
            """)
        else:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(60)
            shadow.setOffset(0, 0)
            shadow.setColor(QColor(0, 0, 0, 220))
            self.parent.container.setGraphicsEffect(shadow)
            self.parent.layout().setContentsMargins(10, 10, 10, 10)
            self.parent.container.setStyleSheet("border-radius:20px; background:#080808; border: 1px solid #222;")
            self.max_btn.setText("⬜")
            self.close_btn.setStyleSheet("""
                QPushButton { background: transparent; border: none; width: 46px; height: 42px; color: #555; font-size: 14px; border-radius: 0px; border-top-right-radius: 20px; }
                QPushButton:hover { background-color: #c0392b; color: white; border-radius: 0px; border-top-right-radius: 20px; }
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            window_handle = self.parent.windowHandle()
            if window_handle and window_handle.startSystemMove():
                return
            self.drag_pos = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.parent.isMaximized(): return
        if event.buttons() == Qt.LeftButton and self.drag_pos is not None:
            self.parent.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None