import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect, QFrame)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QMouseEvent


# --- Custom Title Bar Class ---
class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.drag_pos = None  # Variable to track mouse position for dragging

        self.setFixedHeight(42)
        self.setObjectName("TitleBar")

        # 1. Basic Style Sheet
        # Note: No specific style for the Close button here to avoid conflicts later
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
                background: transparent;  /* Ensures no background color */
                border: none;             /* Removes any underlines or borders */
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

        # 2. Layout Setup
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title Label
        self.title_label = QLabel("SK PLAYER | LAUNCHER")
        layout.addWidget(self.title_label)

        # Spacer
        layout.addStretch()

        # Window Controls
        self.min_btn = QPushButton("—")
        self.max_btn = QPushButton("⬜")
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close_btn")

        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        # Connect Signals
        self.min_btn.clicked.connect(self.parent.showMinimized)
        self.max_btn.clicked.connect(self.handle_max_restore)
        self.close_btn.clicked.connect(self.parent.close)

        # Enable Double Click to Maximize
        self.mouseDoubleClickEvent = self.handle_double_click

        # Apply initial shadow and rounded corners logic
        self.update_radius_shadow()

    def handle_max_restore(self):
        """Toggle between maximized and normal state."""
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
        self.update_radius_shadow()

    def handle_double_click(self, event):
        """Handle double click on title bar."""
        if event.button() == Qt.LeftButton:
            self.handle_max_restore()

    def update_radius_shadow(self):
        """
        Updates the window style based on state (Maximized vs Normal).
        Handles shadows, border radius, and the close button shape.
        """
        # Ensure the parent has the 'container' attribute
        if not hasattr(self.parent, "container"):
            return

        if self.parent.isMaximized():
            # === Maximized State ===

            # 1. Remove shadow and margins to fill screen
            self.parent.container.setGraphicsEffect(None)
            self.parent.layout().setContentsMargins(0, 0, 0, 0)
            self.parent.container.setStyleSheet("border-radius:0px; background:#080808;")

            # 2. Change maximize icon
            self.max_btn.setText("❐")

            # 3. Square Close Button (to fit screen corner)
            self.close_btn.setStyleSheet("""
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
                    background-color: #c0392b;
                    color: white;
                    border-radius: 0px;
                }
            """)
        else:
            # === Normal State (Windowed) ===

            # 1. Add Drop Shadow
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(60)
            shadow.setOffset(0, 0)
            shadow.setColor(QColor(0, 0, 0, 220))
            self.parent.container.setGraphicsEffect(shadow)

            # 2. Add Margins for shadow and Rounded Corners
            self.parent.layout().setContentsMargins(10, 10, 10, 10)
            self.parent.container.setStyleSheet("border-radius:20px; background:#080808;")

            # 3. Change maximize icon
            self.max_btn.setText("⬜")

            # 4. Rounded Close Button (Top-Right corner)
            self.close_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    width: 46px;
                    height: 42px;
                    color: #555;
                    font-size: 14px;
                    border-radius: 0px;
                    border-top-right-radius: 20px; /* Round the corner */
                }
                QPushButton:hover {
                    background-color: #c0392b;
                    color: white;
                    border-radius: 0px;
                    border-top-right-radius: 20px;
                }
            """)

    # ========================================================
    #  Window Dragging Logic (KDE / Wayland / Windows Compatible)
    # ========================================================
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # 1. Try to let the OS handle the move (Critical for KDE/Wayland)
            window_handle = self.parent.windowHandle()
            if window_handle and window_handle.startSystemMove():
                return  # System took over, we are done.

            # 2. Fallback for older systems or X11
            self.drag_pos = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        # If startSystemMove() worked, this won't be called often.
        if self.parent.isMaximized():
            return

        if event.buttons() == Qt.LeftButton and self.drag_pos is not None:
            self.parent.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.drag_pos = None


# --- Main Window Class ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 600)

        # 1. Remove default OS frame and make background transparent
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 2. Setup Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 3. Main Layout (With margins for the shadow)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # 4. Create the Visible Container (Frame)
        self.container = QFrame()
        self.container.setObjectName("Container")
        self.container.setStyleSheet("background-color: #080808; border-radius: 20px;")

        self.main_layout.addWidget(self.container)

        # 5. Container Layout
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        # 6. Add Custom Title Bar
        self.title_bar = CustomTitleBar(self)
        self.container_layout.addWidget(self.title_bar)

        # 7. Add Content Area (Your App content goes here)
        self.content_area = QLabel("Welcome to SK PLAYER")
        self.content_area.setAlignment(Qt.AlignCenter)
        self.content_area.setStyleSheet("color: #555; font-size: 24px;")
        self.container_layout.addWidget(self.content_area)

        # 8. Apply Initial Shadow/Radius logic
        self.title_bar.update_radius_shadow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())