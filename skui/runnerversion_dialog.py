from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QCheckBox, QLineEdit, QFormLayout,
    QTabWidget, QWidget, QScrollArea, QFileDialog
)
from PySide6.QtCore import Qt
from skui.base_dialog import BaseFramelessDialog


class RunnerVersionDialog(BaseFramelessDialog):

    def __init__(self, parent=None):
        super().__init__(parent, title="Runner Configuration")

        self.setFixedSize(640, 620)
        self.current_widgets = {}

        self.apply_style()
        self.build_ui()

    # --------------------------------------------------
    # Style (NO BOXES)
    # --------------------------------------------------
    def apply_style(self):
        self.setStyleSheet("""
        * {
            background: transparent;
            outline: none;
            font-family: Inter, Noto Sans, Sans Serif;
            font-size: 13px;
        }

        QWidget {
            background-color: #121212;
        }

        QLabel {
            color: #cfcfcf;
        }

        /* Tabs */
        QTabWidget::pane {
            border: none;
            margin-top: 10px;
        }

        QTabBar::tab {
            background: transparent;
            color: #8a8a8a;
            padding: 8px 22px;
            margin-right: 12px;
            border-bottom: 2px solid transparent;
            font-weight: 600;
        }

        QTabBar::tab:selected {
            color: #27ae60;
            border-bottom: 2px solid #27ae60;
        }

        QTabBar::tab:hover:!selected {
            color: #dddddd;
        }

        /* Inputs */
        QLineEdit, QComboBox {
            background-color: #1a1a1a;
            color: #eaeaea;
            border: 1px solid #2b2b2b;
            border-radius: 14px;
            padding: 8px 10px;
        }

        QLineEdit:focus, QComboBox:focus {
            border: 1px solid #27ae60;
        }

        /* Buttons */
        QPushButton {
            background-color: #1f1f1f;
            color: #dddddd;
            border-radius: 14px;
            padding: 8px 18px;
            font-weight: 600;
        }

        QPushButton:hover {
            background-color: #2a2a2a;
        }

        QPushButton#saveBtn {
            background-color: #27ae60;
            color: white;
        }

        /* Checkboxes */
        QCheckBox {
            color: #cfcfcf;
            spacing: 10px;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 6px;
            border: 1px solid #333333;
            background-color: #1a1a1a;
        }

        QCheckBox::indicator:checked {
            background-color: #27ae60;
            border: none;
        }

        QScrollArea {
            border: none;
        }
        """)

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def build_ui(self):
        layout = self.content_layout
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        # Runner selector
        top = QHBoxLayout()
        top.addWidget(QLabel("Runner"))

        self.runner_combo = QComboBox()
        self.runner_combo.addItems(["System", "Wine", "Proton"])
        self.runner_combo.currentTextChanged.connect(self.on_runner_changed)

        top.addWidget(self.runner_combo)
        top.addStretch()
        layout.addLayout(top)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Runner tab (scroll)
        self.runner_tab = QWidget()
        self.runner_layout = QVBoxLayout(self.runner_tab)
        self.runner_layout.setSpacing(14)

        self.runner_container = QWidget()
        self.runner_container_layout = QVBoxLayout(self.runner_container)
        self.runner_container_layout.setSpacing(12)
        self.runner_container_layout.setContentsMargins(0, 0, 0, 0)

        self.runner_layout.addWidget(self.runner_container)
        self.runner_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.runner_tab)

        self.tabs.addTab(scroll, "Runner options")

        # System tab
        self.system_tab = QWidget()
        form = QFormLayout(self.system_tab)
        form.setSpacing(14)
        form.setContentsMargins(0, 0, 0, 0)

        self.env_input = QLineEdit()
        self.workdir_input = QLineEdit()
        self.prefix_input = QLineEdit()

        form.addRow("Environment variables", self.env_input)
        form.addRow("Working directory", self.workdir_input)
        form.addRow("Wine prefix", self.prefix_input)

        self.tabs.addTab(self.system_tab, "System")

        # Footer
        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)

        save = QPushButton("Save")
        save.setObjectName("saveBtn")
        save.clicked.connect(self.accept)

        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

        self.on_runner_changed("System")

    # --------------------------------------------------
    # Runner logic
    # --------------------------------------------------
    def clear_runner_ui(self):
        while self.runner_container_layout.count():
            item = self.runner_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def on_runner_changed(self, runner):
        self.clear_runner_ui()
        self.current_widgets.clear()

        if runner in ("Wine", "Proton"):
            self.build_wine_ui()
        else:
            hint = QLabel("Uses the system environment directly.")
            hint.setStyleSheet("font-size:11px;color:#7f7f7f;")
            self.runner_container_layout.addWidget(hint)

    def build_wine_ui(self):
        self.runner_container_layout.addWidget(QLabel("Executable path"))

        row = QHBoxLayout()
        exe = QLineEdit()
        browse = QPushButton("Browse")
        browse.clicked.connect(lambda: self.browse(exe))

        row.addWidget(exe)
        row.addWidget(browse)
        self.runner_container_layout.addLayout(row)

        for text in (
            "Enable DXVK / VKD3D",
            "Enable Esync",
            "Enable Fsync",
            "Prefer discrete GPU"
        ):
            self.runner_container_layout.addWidget(QCheckBox(text))

        hint = QLabel("These options affect performance and compatibility.")
        hint.setStyleSheet("font-size:11px;color:#777777;")
        self.runner_container_layout.addWidget(hint)

    # --------------------------------------------------
    # Utils
    # --------------------------------------------------
    def browse(self, line):
        path, _ = QFileDialog.getOpenFileName(self, "Select executable")
        if path:
            line.setText(path)
