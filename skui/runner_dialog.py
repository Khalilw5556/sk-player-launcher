import os
import threading
import requests
import tarfile
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox,
                               QPushButton, QProgressBar, QMessageBox, QHBoxLayout)
from PySide6.QtCore import Qt, Signal, QObject, Slot

# Assuming these are your external modules
from skcore.runners import get_runner_versions, is_runner_installed, RUNNERS_DIR, set_executable_permissions


# --- Signals Class ---
# Handles communication between background threads and the GUI
class RunnerSignals(QObject):
    progress = Signal(int)  # Update progress bar
    finished = Signal(str)  # Download finished
    error = Signal(str)  # Error message
    status = Signal(str)  # Status text update
    versions_fetched = Signal(list)  # NEW: Sends fetched versions list to Main Thread


class RunnerDialog(QDialog):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setWindowTitle(f"Runner Settings - {game.get('name', 'Game')}")
        self.setFixedWidth(450)
        self.setMinimumHeight(350)

        # Initialize Signals
        self.signals = RunnerSignals()

        # Connect Signals to Main Thread Slots
        self.signals.versions_fetched.connect(self.on_versions_fetched)
        self.signals.progress.connect(self.progress_bar_update)
        self.signals.status.connect(self.status_update)
        self.signals.finished.connect(self.on_download_finished)
        self.signals.error.connect(self.on_error)

        # Stylesheet
        self.setStyleSheet("""
            QDialog { background-color: #0a0a0a; color: white; border: 1px solid #222; }
            QLabel { color: #888; font-size: 12px; font-weight: bold; }
            QComboBox { 
                background-color: #121212; color: #eee; border: 1px solid #222; 
                border-radius: 8px; padding: 8px; font-size: 14px;
            }
            QPushButton { 
                background: #181818; border-radius: 10px; padding: 12px; 
                font-weight: bold; color: white;
            }
            QPushButton:hover { background: #222; }
            QPushButton#apply_btn { background-color: #27ae60; }
            QPushButton#apply_btn:hover { background-color: #2ecc71; }

            QProgressBar { 
                background-color: #050505; border: 1px solid #222; 
                border-radius: 10px; text-align: center; color: white; font-weight: bold;
            }
            QProgressBar::chunk { background-color: #27ae60; border-radius: 9px; }
        """)

        self.available_versions_data = []
        self.setup_ui()

        # Load initial state
        current_type = self.game.get("runner_type", "System")
        self.type_combo.setCurrentText(current_type)
        self.load_versions(current_type)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Runner Type Selection
        layout.addWidget(QLabel("RUNNER TYPE"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["System", "Wine", "Proton"])
        self.type_combo.currentTextChanged.connect(self.load_versions)
        layout.addWidget(self.type_combo)

        # Version Selection
        layout.addWidget(QLabel("AVAILABLE VERSIONS"))
        self.ver_combo = QComboBox()
        layout.addWidget(self.ver_combo)

        # Status Label
        self.status_lbl = QLabel("Ready")
        self.status_lbl.setStyleSheet("color: #27ae60; font-size: 11px;")
        layout.addWidget(self.status_lbl)

        # Progress Bar (Hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        layout.addStretch()

        # Buttons
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

    # --- Fetching Logic ---
    def load_versions(self, r_type):
        """Starts a background thread to fetch versions."""
        self.ver_combo.clear()
        self.available_versions_data = []

        if r_type == "System":
            self.ver_combo.addItem("System Default Wine")
            self.ver_combo.setEnabled(False)
            self.status_lbl.setText("Ready to use system runner.")
            return

        self.ver_combo.setEnabled(True)
        self.status_lbl.setText("Fetching versions from GitHub...")
        self.apply_btn.setEnabled(False)

        # Thread Logic
        def fetch_task():
            try:
                versions = get_runner_versions(r_type)
                # Emit signal to update UI in Main Thread
                self.signals.versions_fetched.emit(versions)
            except Exception as e:
                self.signals.error.emit(str(e))

        threading.Thread(target=fetch_task, daemon=True).start()

    @Slot(list)
    def on_versions_fetched(self, versions):
        """Called by signal when fetching is done."""
        self.available_versions_data = versions
        self.ver_combo.clear()
        r_type = self.type_combo.currentText()

        for v in versions:
            installed = " (Installed)" if is_runner_installed(r_type, v['name']) else ""
            self.ver_combo.addItem(f"{v['name']}{installed}", v)

        self.status_lbl.setText(f"Found {len(versions)} versions.")
        self.apply_btn.setEnabled(True)

    # --- Apply & Download Logic ---
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
        # Disable UI during download
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

    # --- Slot Handlers ---
    @Slot(int)
    def progress_bar_update(self, val):
        self.progress_bar.setValue(val)

    @Slot(str)
    def status_update(self, text):
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet("color: #27ae60;")

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
        self.status_lbl.setStyleSheet("color: #c0392b;")
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")