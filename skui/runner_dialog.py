import os
import threading
import requests
import tarfile
from PySide6.QtWidgets import (QVBoxLayout, QLabel, QComboBox,
                               QPushButton, QProgressBar, QMessageBox, QHBoxLayout, QWidget)
from PySide6.QtCore import Qt, Signal, QObject, Slot

from skcore.runners import get_runner_versions, is_runner_installed, RUNNERS_DIR, set_executable_permissions
from skui.base_dialog import BaseFramelessDialog


class RunnerSignals(QObject):
    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)
    status = Signal(str)
    versions_fetched = Signal(list)


class RunnerDialog(BaseFramelessDialog):
    def __init__(self, game, parent=None):
        super().__init__(parent, title=f"Runner Settings - {game.get('name', 'Game')}")
        self.game = game
        self.setFixedWidth(450)
        self.setMinimumHeight(400)

        self.signals = RunnerSignals()
        self.signals.versions_fetched.connect(self.on_versions_fetched)
        self.signals.progress.connect(self.progress_bar_update)
        self.signals.status.connect(self.status_update)
        self.signals.finished.connect(self.on_download_finished)
        self.signals.error.connect(self.on_error)

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
                font-size: 12px; 
            }

            QComboBox { 
                background-color: #121212; 
                color: #eee; 
                border: 1px solid #333; 
                border-radius: 8px; 
                padding: 8px; 
                font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { 
                background-color: #121212; 
                color: #eee; 
                selection-background-color: #27ae60; 
                border: 1px solid #333;
            }

            QProgressBar { 
                background-color: #050505; 
                border: 1px solid #333; 
                border-radius: 10px; 
                text-align: center; 
                color: white; 
                font-weight: bold;
            }
            QProgressBar::chunk { 
                background-color: #27ae60; 
                border-radius: 9px; 
            }

            QPushButton { 
                background: #181818; 
                border-radius: 10px; 
                padding: 12px; 
                font-weight: bold; 
                color: white;
                border: 1px solid #333;
            }
            QPushButton:hover { 
                background: #333; 
                border: 1px solid #555;
            }
            QPushButton:pressed {
                background: #000;
            }

            QPushButton#apply_btn { 
                background-color: #27ae60; 
                border: none; 
            }
            QPushButton#apply_btn:hover { 
                background-color: #2ecc71; 
            }
            QPushButton#apply_btn:disabled {
                background-color: #1e5e3a;
                color: #aaa;
            }
        """)

        self.available_versions_data = []
        self.setup_ui()

        current_type = self.game.get("runner_type", "System")
        self.type_combo.setCurrentText(current_type)
        self.load_versions(current_type)

    def setup_ui(self):
        layout = self.content_layout

        layout.addWidget(QLabel("RUNNER TYPE"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["System", "Wine", "Proton"])
        self.type_combo.currentTextChanged.connect(self.load_versions)
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel("AVAILABLE VERSIONS"))
        self.ver_combo = QComboBox()
        layout.addWidget(self.ver_combo)

        self.status_lbl = QLabel("Ready")
        self.status_lbl.setStyleSheet("color: #27ae60; font-size: 11px; background: transparent;")
        layout.addWidget(self.status_lbl)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        layout.addStretch()

        btns = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.setObjectName("apply_btn")
        self.apply_btn.setCursor(Qt.PointingHandCursor)
        self.apply_btn.clicked.connect(self.handle_apply)

        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.apply_btn)
        layout.addLayout(btns)

    def load_versions(self, r_type):
        self.ver_combo.clear()
        self.available_versions_data = []

        if r_type == "System":
            self.ver_combo.addItem("System Default Wine")
            self.ver_combo.setEnabled(False)
            self.status_lbl.setText("Ready to use system runner.")
            return

        self.ver_combo.setEnabled(True)
        self.status_lbl.setText("Fetching versions from GitHub...")
        self.status_lbl.setStyleSheet("color: #e67e22; background: transparent;")
        self.apply_btn.setEnabled(False)

        def fetch_task():
            try:
                versions = get_runner_versions(r_type)
                self.signals.versions_fetched.emit(versions)
            except Exception as e:
                self.signals.error.emit(str(e))

        threading.Thread(target=fetch_task, daemon=True).start()

    @Slot(list)
    def on_versions_fetched(self, versions):
        self.available_versions_data = versions
        self.ver_combo.clear()
        r_type = self.type_combo.currentText()

        for v in versions:
            installed = " (Installed)" if is_runner_installed(r_type, v['name']) else ""
            self.ver_combo.addItem(f"{v['name']}{installed}", v)

        self.status_lbl.setText(f"Found {len(versions)} versions.")
        self.status_lbl.setStyleSheet("color: #27ae60; background: transparent;")
        self.apply_btn.setEnabled(True)

    def handle_apply(self):
        r_type = self.type_combo.currentText()

        if r_type == "System":
            self.game["runner_type"] = "System"
            self.game["runner_version"] = ""
            self.accept()
            return

        selected_data = self.ver_combo.currentData()
        if not selected_data:
            QMessageBox.warning(self, "Warning", "Please select a version first.")
            return

        v_name = selected_data['name']

        if is_runner_installed(r_type, v_name):
            self.game["runner_type"] = r_type
            self.game["runner_version"] = v_name
            self.accept()
        else:
            self.start_download(r_type, selected_data)

    def start_download(self, r_type, v_data):
        self.apply_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.type_combo.setEnabled(False)
        self.ver_combo.setEnabled(False)
        self.progress_bar.show()

        def download_thread():
            try:
                version_dir = os.path.join(RUNNERS_DIR, r_type.lower(), v_data['name'])
                os.makedirs(version_dir, exist_ok=True)

                archive_path = os.path.join(RUNNERS_DIR, v_data['filename'])

                self.signals.status.emit(f"Downloading {v_data['name']}...")
                response = requests.get(v_data['url'], stream=True, timeout=20)
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(archive_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = int((downloaded / total_size) * 100)
                                self.signals.progress.emit(percent)

                self.signals.status.emit("Extracting files... this may take a moment.")
                with tarfile.open(archive_path) as tar:
                    tar.extractall(path=version_dir)

                self.signals.status.emit("Finalizing permissions...")
                set_executable_permissions(version_dir)

                if os.path.exists(archive_path):
                    os.remove(archive_path)

                self.signals.finished.emit(v_data['name'])

            except Exception as e:
                self.signals.error.emit(str(e))

        threading.Thread(target=download_thread, daemon=True).start()

    @Slot(int)
    def progress_bar_update(self, val):
        self.progress_bar.setValue(val)

    @Slot(str)
    def status_update(self, text):
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet("color: #27ae60; background: transparent;")

    @Slot(str)
    def on_download_finished(self, v_name):
        self.game["runner_type"] = self.type_combo.currentText()
        self.game["runner_version"] = v_name
        self.status_lbl.setText("Download complete!")
        QMessageBox.information(self, "Success", f"Runner {v_name} is now ready.")
        self.accept()

    @Slot(str)
    def on_error(self, error_msg):
        self.apply_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.type_combo.setEnabled(True)
        self.ver_combo.setEnabled(True)
        self.progress_bar.hide()

        self.status_lbl.setText("Operation failed.")
        self.status_lbl.setStyleSheet("color: #c0392b; background: transparent;")
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")