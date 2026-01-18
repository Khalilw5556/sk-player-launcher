from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                               QTextEdit, QPushButton, QHBoxLayout, QMessageBox, QComboBox)
from PySide6.QtCore import Qt
from skui.runner_dialog import RunnerDialog


class EditGameDialog(QDialog):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setWindowTitle(f"Edit Game - {self.game.get('name', 'Game')}")
        self.setFixedWidth(450)
        self.setMinimumHeight(550)

        # Dark Theme Stylesheet
        self.setStyleSheet("""
            QDialog { 
                background-color: #0a0a0a; 
                color: white; 
                border: 1px solid #222; 
            }
            QLabel { 
                color: #888; 
                font-weight: bold; 
                font-size: 11px; 
                margin-top: 5px; 
            }
            QLineEdit, QTextEdit, QComboBox { 
                background-color: #121212; 
                color: #eee; 
                border: 1px solid #222; 
                border-radius: 8px; 
                padding: 10px; 
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus { 
                border: 1px solid #27ae60; 
            }
            QPushButton { 
                background: #181818; 
                border-radius: 10px; 
                padding: 12px; 
                font-weight: bold; 
                color: white;
            }
            QPushButton:hover { 
                background: #222; 
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { 
                image: none; 
                border-left: 5px solid transparent; 
                border-right: 5px solid transparent; 
                border-top: 5px solid #888; 
                margin-right: 10px; 
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)

        # Game Name Input
        layout.addWidget(QLabel("GAME NAME"))
        self.name_in = QLineEdit(self.game.get("name", ""))
        self.name_in.setPlaceholderText("Enter game title...")
        layout.addWidget(self.name_in)

        # Banner Type Selection (Matches logic in GameCard)
        layout.addWidget(QLabel("BANNER DISPLAY TYPE"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["long", "wide"])
        self.type_combo.setCurrentText(self.game.get("banner_type", "long"))
        layout.addWidget(self.type_combo)

        # Version Input
        layout.addWidget(QLabel("VERSION"))
        self.ver_in = QLineEdit(self.game.get("version", "1.0"))
        self.ver_in.setPlaceholderText("e.g. 1.0.4")
        layout.addWidget(self.ver_in)

        # Description Input
        layout.addWidget(QLabel("DESCRIPTION"))
        self.desc_in = QTextEdit()
        self.desc_in.setPlainText(self.game.get("description", ""))
        self.desc_in.setPlaceholderText("Write something about the game...")
        layout.addWidget(self.desc_in)

        layout.addSpacing(10)

        # Runner Management Button
        self.run_btn = QPushButton("🎮  Manage Runner (Wine/Proton)")
        self.run_btn.setStyleSheet("background-color: #4a148c; border: none;")
        self.run_btn.setCursor(Qt.PointingHandCursor)
        self.run_btn.clicked.connect(self.open_runner)
        layout.addWidget(self.run_btn)

        layout.addSpacing(15)

        # Action Buttons Layout
        btns_layout = QHBoxLayout()

        self.del_btn = QPushButton("🗑️ Delete")
        self.del_btn.setStyleSheet("background-color: #c0392b; color: white;")
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.clicked.connect(self.do_del)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white;")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.do_save)

        btns_layout.addWidget(self.del_btn, 1)
        btns_layout.addWidget(self.save_btn, 2)
        layout.addLayout(btns_layout)

    def open_runner(self):
        """Opens the Runner/Wine configuration dialog."""
        RunnerDialog(self.game, self).exec()

    def do_del(self):
        """Asks for confirmation and closes with code 2 (Delete)."""
        confirm = QMessageBox.question(self, "Delete Game",
                                       f"Are you sure you want to remove '{self.game.get('name')}'?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            # Code 2 signals the parent window to delete the game
            self.done(2)

    def do_save(self):
        """Updates the dictionary and accepts the dialog."""
        self.game.update({
            "name": self.name_in.text(),
            "banner_type": self.type_combo.currentText(),
            "version": self.ver_in.text(),
            "description": self.desc_in.toPlainText()
        })
        self.accept()