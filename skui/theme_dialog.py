from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QColorDialog
from PySide6.QtGui import QColor


class ThemeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Theme Customizer")
        self.setFixedWidth(350)
        self.setStyleSheet("background-color: #0a0a0a; color: white; border: 1px solid #222;")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("<b>CUSTOMIZE COLORS</b>"))

        # Options list: (Display Name, Attribute Key)
        options = [
            ("Main Background", "bg_color"),
            ("Sidebar Buttons", "btn_color"),
            ("Play Button & Logs Text", "accent_color"),
            ("Library Header Color", "lib_color")  # Feature to change the "Library" header color
        ]

        # Create buttons dynamically
        for text, key in options:
            btn = QPushButton(f"Pick {text}")
            # Use lambda to pass the specific key to the function
            btn.clicked.connect(lambda checked=False, k=key: self.pick_color(k))
            layout.addWidget(btn)

        # Done/Close Button
        close_btn = QPushButton("Done")
        close_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; margin-top: 10px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def pick_color(self, key):
        """Open color picker and apply the selected color to the parent."""
        # Retrieve the current color from the parent window
        current_color = getattr(self.parent, key)

        # Open the dialog
        color = QColorDialog.getColor(initial=QColor(current_color), parent=self, title=f"Select {key}")

        if color.isValid():
            # Update the parent attribute
            setattr(self.parent, key, color.name())

            # Apply the changes if the parent has the update method
            if hasattr(self.parent, "apply_theme"):
                self.parent.apply_theme()