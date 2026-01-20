from PySide6.QtWidgets import QVBoxLayout, QLabel, QCheckBox, QPushButton, QHBoxLayout, QLineEdit, QMessageBox
from skcore.config import load_settings, save_settings
from skui.base_dialog import BaseFramelessDialog
from setting.updater import manual_check

DEV_ACCESS_CODE = "SK-DEV"


class SettingsDialog(BaseFramelessDialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="Global Settings")
        self.setFixedWidth(450)
        self.current_settings = load_settings()

        if "developer_mode" not in self.current_settings:
            self.current_settings["developer_mode"] = False

        self.content_area.setStyleSheet("""
            QLabel, QCheckBox {
                background: transparent;
                border: none;
                color: #ccc;
            }

            QLabel {
                font-weight: bold;
                font-size: 14px;
                margin-bottom: 5px;
                margin-top: 10px;
            }

            QCheckBox {
                color: #eee;
                font-size: 13px;
                padding: 5px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #555;
                background: #111;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background: #27ae60;
                border: 1px solid #27ae60;
            }

            QLineEdit {
                background-color: #111;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
                color: #fff;
                font-family: monospace;
            }
            QLineEdit:focus {
                border: 1px solid #27ae60;
            }

            QPushButton {
                background-color: #181818;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                color: white;
                border: 1px solid #333;
            }

            QPushButton:hover {
                background-color: #333333;
                border: 1px solid #666;
            }

            QPushButton#update_btn {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                margin-top: 5px;
            }

            QPushButton#dev_btn_activate {
                background-color: #d35400;
                border: none;
            }
            QPushButton#dev_btn_deactivate {
                background-color: #c0392b;
                border: none;
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

        layout.addWidget(QLabel("BEHAVIOR"))

        self.check_min_launch = QCheckBox("Minimize to Tray when Game Starts")
        self.check_min_launch.setChecked(self.current_settings.get("minimize_on_launch", False))
        layout.addWidget(self.check_min_launch)

        self.check_tray_close = QCheckBox("Minimize to Tray on Close (X button)")
        self.check_tray_close.setChecked(self.current_settings.get("minimize_to_tray_on_close", False))
        layout.addWidget(self.check_tray_close)

        self.check_updates = QCheckBox("Check for updates on startup")
        self.check_updates.setChecked(self.current_settings.get("check_updates", True))
        layout.addWidget(self.check_updates)

        layout.addWidget(QLabel("UPDATES"))
        self.btn_check_update = QPushButton("Check for Updates Now")
        self.btn_check_update.setObjectName("update_btn")
        self.btn_check_update.clicked.connect(self.on_check_update_clicked)
        layout.addWidget(self.btn_check_update)

        layout.addWidget(QLabel("DEVELOPER ZONE"))

        dev_layout = QHBoxLayout()

        self.dev_input = QLineEdit()
        self.dev_input.setPlaceholderText("Enter Dev Code...")
        self.dev_input.setEchoMode(QLineEdit.Password)

        self.dev_status_btn = QPushButton()
        self.dev_status_btn.clicked.connect(self.toggle_developer_mode)

        dev_layout.addWidget(self.dev_input)
        dev_layout.addWidget(self.dev_status_btn)

        layout.addLayout(dev_layout)

        self.lbl_dev_status = QLabel("")
        self.lbl_dev_status.setStyleSheet("font-size: 11px; color: #777; margin-top:0;")
        layout.addWidget(self.lbl_dev_status)

        self.update_dev_ui_state()

        layout.addStretch()

        btns_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.clicked.connect(self.save_to_file)

        btns_layout.addWidget(self.cancel_btn)
        btns_layout.addWidget(self.save_btn)
        layout.addLayout(btns_layout)

    def update_dev_ui_state(self):
        is_dev = self.current_settings.get("developer_mode", False)

        if is_dev:
            self.dev_input.setEnabled(False)
            self.dev_input.setText("********")
            self.dev_input.setPlaceholderText("Active")
            self.dev_status_btn.setText("Disable")
            self.dev_status_btn.setObjectName("dev_btn_deactivate")
            self.lbl_dev_status.setText("✅ Private Version Active (Updates Disabled)")
            self.lbl_dev_status.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.dev_input.setEnabled(True)
            self.dev_input.clear()
            self.dev_input.setPlaceholderText("Enter Dev Code...")
            self.dev_status_btn.setText("Activate")
            self.dev_status_btn.setObjectName("dev_btn_activate")
            self.lbl_dev_status.setText("❌ Public Version (Updates Enabled)")
            self.lbl_dev_status.setStyleSheet("color: #777;")

        self.content_area.style().unpolish(self.dev_status_btn)
        self.content_area.style().polish(self.dev_status_btn)

    def toggle_developer_mode(self):
        is_dev = self.current_settings.get("developer_mode", False)

        if is_dev:
            self.current_settings["developer_mode"] = False
            QMessageBox.information(self, "Developer Mode",
                                    "Developer Mode Deactivated.\nYou will now receive updates.")
            self.update_dev_ui_state()
        else:
            code = self.dev_input.text()
            if code == DEV_ACCESS_CODE:
                self.current_settings["developer_mode"] = True
                QMessageBox.information(self, "Success",
                                        "Developer Mode Activated!\nUpdates are now disabled for this version.")
                self.update_dev_ui_state()
            else:
                QMessageBox.warning(self, "Error", "Invalid Developer Code.")

    def on_check_update_clicked(self):
        self.btn_check_update.setText("Checking...")
        self.btn_check_update.setEnabled(False)
        self.repaint()

        manual_check(self)

        self.btn_check_update.setText("Check for Updates Now")
        self.btn_check_update.setEnabled(True)

    def save_to_file(self):
        self.current_settings["minimize_on_launch"] = self.check_min_launch.isChecked()
        self.current_settings["minimize_to_tray_on_close"] = self.check_tray_close.isChecked()
        self.current_settings["check_updates"] = self.check_updates.isChecked()

        save_settings(self.current_settings)

        if self.parent() and hasattr(self.parent(), "load_user_settings"):
            self.parent().load_user_settings()

        self.accept()