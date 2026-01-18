from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class GameCard(QFrame):
    def __init__(self, game, callback):
        super().__init__()
        self.game, self.callback = game, callback
        self.is_selected = False
        self.selection_color = "#27ae60"  # Default selection color
        self.setObjectName("GameCard")

        # Determine dimensions based on banner type (Aspect Ratio)
        self.banner_type = self.game.get("banner_type", "long")
        if self.banner_type == "wide":
            self.H = 160
            self.W = int(self.H * (1920 / 620))  # Wide aspect ratio
        else:
            self.H = 260
            self.W = int(self.H * (600 / 900))  # Vertical/Long aspect ratio

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(self.W, self.H)

        self.img_lbl = QLabel()
        self.img_lbl.setScaledContents(True)
        # Apply border radius to the image label itself
        self.img_lbl.setStyleSheet("border-radius: 15px; background-color: #111;")

        pix = QPixmap(self.game.get("banner", ""))
        if not pix.isNull():
            self.img_lbl.setPixmap(pix)
        else:
            self.img_lbl.setText("NO IMAGE")
            self.img_lbl.setAlignment(Qt.AlignCenter)
            self.img_lbl.setStyleSheet("background-color: #151515; border-radius: 15px; color: #333;")

        layout.addWidget(self.img_lbl)
        self.update_style()

    def update_selection_color(self, color):
        """
        Updates the border color used when the card is selected.
        This allows the ThemeDialog to update existing cards dynamically.
        """
        self.selection_color = color
        self.update_style()

    def update_style(self):
        # The border appears outside the image using the selected theme color
        border_color = self.selection_color if self.is_selected else "transparent"

        # Note: Border radius is 19px here (15px image + border width) to look smooth
        self.setStyleSheet(f"""
            #GameCard {{ 
                border: 5px solid {border_color}; 
                border-radius: 19px; 
                background: transparent; 
            }}
        """)

    def set_selected(self, state):
        """Sets the selection state and refreshes the style."""
        self.is_selected = state
        self.update_style()

    def mousePressEvent(self, event):
        """Trigger the callback in MainWindow when clicked."""
        if event.button() == Qt.LeftButton:
            self.callback(self)