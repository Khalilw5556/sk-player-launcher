import os, shutil
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea,
    QLabel, QPushButton, QTextEdit, QFileDialog,
    QDialog, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QColor, QPalette

# Assuming these modules exist based on your project structure
from skcore.database import load_games, save_games
from skcore.launcher import launch_game
from skui.game_card import GameCard
from skui.edit_dialog import EditGameDialog
from skui.theme_dialog import ThemeDialog
from skui.title_bar import CustomTitleBar


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # -------- Window Flags --------
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # -------- Fix for Purple Artifacts --------
        # This disables the default system highlight color which causes
        # the purple line/background on some systems (especially KDE/Linux).
        pal = self.palette()
        pal.setColor(QPalette.Highlight, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(pal)

        self.setWindowTitle("SK | Player")
        self.setMinimumSize(1250, 850)

        # -------- Theme Defaults --------
        self.bg_color = "#080808"
        self.btn_color = "#121212"
        self.accent_color = "#27ae60"
        self.select_color = "#27ae60"

        # -------- Data --------
        self.games = load_games()
        self.selected_game = None

        # -------- Process Manager --------
        self.process = QProcess(self)
        self.process.finished.connect(self.on_game_closed)
        self.process.readyReadStandardOutput.connect(self.read_output)

        # -------- UI Setup --------
        self.init_ui()
        self.apply_theme()
        self.refresh_grid()

    # ======================================================
    # UI Setup
    # ======================================================
    def init_ui(self):
        # Root layout (Margins here create space for the drop shadow)
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(20, 20, 20, 20)
        self.root_layout.setSpacing(0)

        # The Actual Container (Visible Window)
        self.container = QWidget()
        self.container.setObjectName("WindowContainer")
        self.root_layout.addWidget(self.container)

        # ✅ Apply the main background and radius here
        self.container.setStyleSheet("""
            #WindowContainer {
                background: #080808;
                border-radius: 20px;
            }
        """)

        # Drop Shadow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 220))
        self.container.setGraphicsEffect(shadow)

        # Layout inside the container
        self.main_v_layout = QVBoxLayout(self.container)
        self.main_v_layout.setContentsMargins(0, 0, 0, 0)
        self.main_v_layout.setSpacing(0)

        # -------- Title Bar --------
        self.title_bar = CustomTitleBar(self)
        self.main_v_layout.addWidget(self.title_bar)

        # -------- Content Area --------
        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")
        self.main_v_layout.addWidget(self.content_area)

        main_layout = QHBoxLayout(self.content_area)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(30)

        # ================= Sidebar =================
        sidebar = QVBoxLayout()
        sidebar.setSpacing(8)

        lbl_logs = QLabel("SYSTEM LOGS")
        lbl_logs.setStyleSheet("background:transparent;")
        sidebar.addWidget(lbl_logs)

        self.logs = QTextEdit()
        self.logs.setObjectName("logs")
        self.logs.setReadOnly(True)
        sidebar.addWidget(self.logs, 1)

        self.btn_add = QPushButton("➕ Add New Game")
        self.btn_edit = QPushButton("⚙️ Edit Details")
        self.btn_banner = QPushButton("🖼️ Set Banner")
        self.btn_path = QPushButton("📂 Game Path")
        self.btn_theme = QPushButton("🎨 Customize Theme")

        for btn in (
            self.btn_add, self.btn_edit,
            self.btn_banner, self.btn_path,
            self.btn_theme
        ):
            btn.setObjectName("side_btn")
            btn.setFixedHeight(42)
            btn.setCursor(Qt.PointingHandCursor)
            sidebar.addWidget(btn)

        main_layout.addLayout(sidebar, 20)

        # ================= Right Panel (Library) =================
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        self.library_header = QLabel("Library")
        self.library_header.setStyleSheet("""
            font-size:16px;
            font-weight:bold;
            text-transform:uppercase;
            margin-left:10px;
            background:transparent;
        """)
        right_panel.addWidget(self.library_header)

        self.grid_container = QWidget()
        self.grid_container.mousePressEvent = self.background_click_event

        self.grid_layout = QVBoxLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignTop)
        self.grid_layout.setSpacing(10)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.grid_container)
        self.scroll.setStyleSheet("background:transparent;")
        self.scroll.mousePressEvent = self.background_click_event
        right_panel.addWidget(self.scroll, 1)

        # ================= Info Panel (Bottom Right) =================
        self.info_frame = QFrame()
        self.info_frame.setObjectName("InfoFrame")
        self.info_frame.setFixedHeight(250)

        info_layout = QHBoxLayout(self.info_frame)
        info_layout.setContentsMargins(35, 25, 35, 25)
        info_layout.setSpacing(40)

        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignTop)

        self.lbl_title = QLabel("Select a Game")
        self.lbl_title.setObjectName("lbl_title")

        self.lbl_meta = QLabel("")
        self.lbl_meta.setObjectName("lbl_meta")

        self.lbl_desc = QLabel("")
        self.lbl_desc.setObjectName("lbl_desc")
        self.lbl_desc.setWordWrap(True)

        desc_scroll = QScrollArea()
        desc_scroll.setWidgetResizable(True)
        desc_scroll.setFrameShape(QFrame.NoFrame)
        desc_scroll.setWidget(self.lbl_desc)
        desc_scroll.setStyleSheet("""
            QScrollArea { background:transparent; }
            QWidget { background:transparent; }
        """)

        text_layout.addWidget(self.lbl_title)
        text_layout.addWidget(self.lbl_meta)
        text_layout.addWidget(desc_scroll)

        info_layout.addLayout(text_layout, 1)

        self.play_btn = QPushButton("PLAY")
        self.play_btn.setObjectName("play_btn")
        self.play_btn.setFixedSize(180, 80)
        self.play_btn.clicked.connect(self.toggle_play)
        info_layout.addWidget(self.play_btn, alignment=Qt.AlignVCenter)

        right_panel.addWidget(self.info_frame)
        main_layout.addLayout(right_panel, 80)

        # -------- Signals --------
        self.btn_add.clicked.connect(self.add)
        self.btn_edit.clicked.connect(self.edit)
        self.btn_banner.clicked.connect(self.set_banner)
        self.btn_path.clicked.connect(self.set_path)
        self.btn_theme.clicked.connect(self.open_theme_settings)

    # ======================================================
    # Theme Management
    # ======================================================
    def apply_theme(self):
        self.content_area.setStyleSheet(f"""
            #ContentArea {{
                background-color:{self.bg_color};
                border-bottom-left-radius:20px;
                border-bottom-right-radius:20px;
            }}

            QWidget {{
                color:#eee;
                font-family:Segoe UI;
                background:transparent;
            }}

            QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {{
                background:transparent;
                border:none;
            }}

            QTextEdit#logs {{
                background:#000;
                color:{self.accent_color};
                border-radius:15px;
                font-family:monospace;
                font-size:10px;
                padding:10px;
                border:1px solid #151515;
            }}

            QPushButton#side_btn {{
                background:{self.btn_color};
                border-radius:10px;
                padding-left:15px;
                text-align:left;
                font-weight:bold;
            }}

            QPushButton#side_btn:hover {{
                background:#1a1a1a;
                border:1px solid {self.accent_color};
            }}

            #InfoFrame {{
                background:#0d0d0d;
                border-radius:35px;
                border:1px solid #1a1a1a;
            }}

            QLabel {{ background:transparent; }}

            #lbl_title {{
                font-size:36px;
                font-weight:bold;
                color:white;
            }}

            #lbl_meta {{
                color:{self.accent_color};
                font-weight:bold;
            }}

            #lbl_desc {{
                color:#888;
            }}

            QPushButton#play_btn {{
                background:{self.accent_color};
                border-radius:20px;
                font-size:24px;
                font-weight:bold;
                color:white;
            }}
        """)

    # ======================================================
    # Logic & Events
    # ======================================================
    def log(self, msg):
        self.logs.append(f"<b>[{datetime.now():%H:%M:%S}]</b> {msg}")

    def background_click_event(self, event):
        if event.button() == Qt.LeftButton:
            self.clear_selection()

    def clear_selection(self):
        self.selected_game = None
        # Assuming GameCards are stored in self.cards from refresh_grid
        for c in getattr(self, "cards", []):
            c.set_selected(False)
        self.lbl_title.setText("Select a Game")
        self.lbl_meta.setText("")
        self.lbl_desc.setText("")

    def on_select(self, card):
        for c in self.cards:
            c.set_selected(False)
        card.set_selected(True)

        self.selected_game = card.game
        self.lbl_title.setText(card.game["name"])
        self.lbl_meta.setText(
            f"v{card.game.get('version','1.0')} • {card.game.get('runner_type','System').upper()}"
        )
        self.lbl_desc.setText(card.game.get("description", ""))

    def toggle_play(self):
        if not self.selected_game:
            return

        if self.process.state() == QProcess.Running:
            self.process.terminate()
            return

        ok, msg = launch_game(self.selected_game, self.process)
        if ok:
            self.play_btn.setText("STOP")
            self.play_btn.setStyleSheet("background:#c0392b;border-radius:20px;")
        else:
            self.log(f"Error: {msg}")

    def on_game_closed(self):
        self.play_btn.setText("PLAY")
        self.apply_theme()

    def read_output(self):
        out = self.process.readAllStandardOutput().data().decode().strip()
        if out:
            self.log(f"<span style='color:#555'>[Wine] {out}</span>")

    # ======================================================
    # Game Management Methods
    # ======================================================
    def refresh_grid(self):
        while self.grid_layout.count():
            i = self.grid_layout.takeAt(0)
            if i.widget():
                i.widget().deleteLater()

        self.games.sort(key=lambda g: g["name"].lower())
        self.cards = []

        row = QHBoxLayout()
        row.setSpacing(15)

        for g in self.games:
            card = GameCard(g, self.on_select)
            self.cards.append(card)
            row.addWidget(card)

        self.grid_layout.addLayout(row)

    def add(self):
        path, _ = QFileDialog.getOpenFileName(self, "Add Game")
        if not path:
            return

        name = os.path.splitext(os.path.basename(path))[0]
        self.games.append({
            "name": name,
            "path": path,
            "banner": "",
            "banner_type": "long",
            "version": "1.0",
            "runner_type": "System",
            "description": ""
        })
        save_games(self.games)
        self.refresh_grid()

    def edit(self):
        if not self.selected_game:
            return

        dlg = EditGameDialog(self.selected_game, self)
        result = dlg.exec()

        if result == QDialog.Accepted:
            # Case 1: Save Changes
            save_games(self.games)
            self.refresh_grid()
            self.on_select(self.cards[self.games.index(self.selected_game)])  # Refresh selection info

        elif result == 2:
            # Case 2: Delete Game (The code returned by do_del)
            self.games.remove(self.selected_game)
            save_games(self.games)
            self.clear_selection()
            self.refresh_grid()

    def set_banner(self):
        if not self.selected_game:
            return

        src, _ = QFileDialog.getOpenFileName(self, "Banner")
        if not src:
            return

        os.makedirs("data/banners", exist_ok=True)
        dest = os.path.join("data/banners", os.path.basename(src))
        shutil.copy2(src, dest)

        self.selected_game["banner"] = dest
        save_games(self.games)
        self.refresh_grid()

    def set_path(self):
        if not self.selected_game:
            return

        path, _ = QFileDialog.getOpenFileName(self, "Executable")
        if path:
            self.selected_game["path"] = path
            save_games(self.games)

    def open_theme_settings(self):
        ThemeDialog(self).exec()