from PySide6.QtWidgets import (QVBoxLayout, QLabel, QLineEdit, QTextEdit,
                               QPushButton, QHBoxLayout, QMessageBox, QComboBox, QDialog)
from PySide6.QtCore import Qt
from skui.runner_dialog import RunnerDialog
from skui.base_dialog import BaseFramelessDialog


class EditGameDialog(BaseFramelessDialog):
    def __init__(self, game, parent=None):
        super().__init__(parent, title=f"Edit - {game.get('name', 'Game')}")
        self.game = game
        self.setFixedWidth(450)

        self.content_area.setStyleSheet("""
            QWidget { 
                background: transparent; 
                color: #eee; 
            }

            QLabel { 
                background: transparent;
                border: none;
                color: #888; 
                font-weight: bold; 
                font-size: 11px; 
                margin-top: 5px; 
            }

            QLineEdit, QTextEdit, QComboBox { 
                background-color: #121212; 
                border: 1px solid #333; 
                border-radius: 8px; 
                padding: 10px; 
                font-size: 14px;
                color: #eee;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus { 
                border: 1px solid #27ae60; 
                background-color: #151515;
            }

            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { 
                background-color: #121212; 
                color: #eee; 
                selection-background-color: #27ae60; 
                border: 1px solid #333;
            }

            QPushButton { 
                background-color: #181818; 
                border-radius: 10px; 
                padding: 12px; 
                font-weight: bold; 
                color: white; 
                border: 1px solid #333;
            }
            QPushButton:hover { 
                background-color: #333; 
                border: 1px solid #555; 
            }
            QPushButton:pressed {
                background-color: #000;
            }

            QPushButton#runner_btn {
                background-color: #4a148c;
                border: none;
            }
            QPushButton#runner_btn:hover {
                background-color: #6a1b9a;
            }

            QPushButton#del_btn {
                background-color: #c0392b;
                border: none;
            }
            QPushButton#del_btn:hover {
                background-color: #e74c3c;
            }

            QPushButton#save_btn {
                background-color: #27ae60;
                border: none;
            }
            QPushButton#save_btn:hover {
                background-color: #2ecc71;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = self.content_layout

        layout.addWidget(QLabel("GAME NAME"))
        self.name_in = QLineEdit(self.game.get("name", ""))
        self.name_in.setPlaceholderText("Enter game title...")
        layout.addWidget(self.name_in)

        layout.addWidget(QLabel("BANNER DISPLAY TYPE"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["long", "wide"])
        self.type_combo.setCurrentText(self.game.get("banner_type", "long"))
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("VERSION"))
        self.ver_in = QLineEdit(self.game.get("version", "1.0"))
        layout.addWidget(self.ver_in)

        layout.addWidget(QLabel("DESCRIPTION"))
        self.desc_in = QTextEdit()
        self.desc_in.setPlainText(self.game.get("description", ""))
        self.desc_in.setFixedHeight(100)
        layout.addWidget(self.desc_in)

        layout.addSpacing(10)

        self.run_btn = QPushButton("🎮  Manage Runner (Wine/Proton)")
        self.run_btn.setObjectName("runner_btn")
        self.run_btn.clicked.connect(self.open_runner)
        layout.addWidget(self.run_btn)

        layout.addSpacing(15)
        btns_layout = QHBoxLayout()

        self.del_btn = QPushButton("🗑️ Delete")
        self.del_btn.setObjectName("del_btn")
        self.del_btn.clicked.connect(self.do_del)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.clicked.connect(self.do_save)

        btns_layout.addWidget(self.del_btn, 1)
        btns_layout.addWidget(self.save_btn, 2)
        layout.addLayout(btns_layout)

    def open_runner(self):
        RunnerDialog(self.game, self).exec()

    def do_del(self):
        confirm = QMessageBox.question(self, "Delete Game",
                                       f"Are you sure you want to remove '{self.game.get('name')}'?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.done(2)

    def do_save(self):
        self.game.update({
            "name": self.name_in.text(),
            "banner_type": self.type_combo.currentText(),
            "version": self.ver_in.text(),
            "description": self.desc_in.toPlainText()
        })
        self.accept()