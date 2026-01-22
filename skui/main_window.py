import os, shutil
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QScrollArea,
    QLabel, QPushButton, QTextEdit, QFileDialog,
    QDialog, QFrame, QGraphicsDropShadowEffect,
    QSystemTrayIcon, QMenu, QStyle, QApplication
)
from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QColor, QPalette, QIcon, QAction

from skcore.database import load_games, save_games
from skcore.launcher import launch_game
from skcore.config import load_settings
from skui.game_card import GameCard
from skui.edit_dialog import EditGameDialog
from skui.theme_dialog import ThemeDialog
from skui.title_bar import CustomTitleBar
from skui.settings_dialog import SettingsDialog


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        pal = self.palette()
        pal.setColor(QPalette.Highlight, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(pal)

        self.setWindowTitle("SK | Player")
        self.setMinimumSize(1250, 865)

        self.bg_color = "#080808"
        self.btn_color = "#121212"
        self.accent_color = "#27ae60"
        self.select_color = "#27ae60"
        self.lib_color = "#eeeeee"

        self.title_bar_color = "#050505"

        self.games = load_games()
        self.selected_game = None

        self.app_settings = {}
        self.load_user_settings()

        self.setup_system_tray()

        self.process = QProcess(self)
        self.process.finished.connect(self.on_game_closed)
        self.process.readyReadStandardOutput.connect(self.read_output)

        self.init_ui()
        self.apply_theme()
        self.refresh_grid()

    def load_user_settings(self):
        self.app_settings = load_settings()
        print(f"DEBUG: Settings Reloaded -> {self.app_settings}")

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)

        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)

        tray_menu = QMenu()
        restore_action = QAction("Show Launcher", self)
        restore_action.triggered.connect(self.show_window)
        tray_menu.addAction(restore_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_window()

    def show_window(self):
        self.showNormal()
        self.activateWindow()

    def init_ui(self):
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(20, 20, 20, 20)
        self.root_layout.setSpacing(0)

        self.container = QWidget()
        self.container.setObjectName("WindowContainer")
        self.root_layout.addWidget(self.container)

        self.container.setStyleSheet("""
            #WindowContainer {
                background: #080808;
                border-radius: 20px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 220))
        self.container.setGraphicsEffect(shadow)

        self.main_v_layout = QVBoxLayout(self.container)
        self.main_v_layout.setContentsMargins(0, 0, 0, 0)
        self.main_v_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        self.main_v_layout.addWidget(self.title_bar)

        self.content_area = QWidget()
        self.content_area.setObjectName("ContentArea")
        self.main_v_layout.addWidget(self.content_area)

        main_layout = QHBoxLayout(self.content_area)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(30)

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
        self.btn_settings = QPushButton("🛠️ Settings")

        for btn in (
                self.btn_add, self.btn_edit,
                self.btn_banner, self.btn_path,
                self.btn_theme,
                self.btn_settings
        ):
            btn.setObjectName("side_btn")
            btn.setFixedHeight(42)
            btn.setCursor(Qt.PointingHandCursor)
            sidebar.addWidget(btn)

        main_layout.addLayout(sidebar, 20)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        self.library_header = QLabel("Library")
        self.library_header.setStyleSheet("""
                    font-size:16px; font-weight:bold; text-transform:uppercase;
                    margin-left:10px; background:transparent;
                """)
        right_panel.addWidget(self.library_header)

        self.grid_container = QWidget()
        self.grid_container.setObjectName("GridContainer")
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_container.mousePressEvent = self.background_click_event
        self.grid_container.mousePressEvent = self.background_click_event

        self.grid_layout = QVBoxLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(7, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.grid_container)

        self.scroll.viewport().setStyleSheet("background: transparent;")

        self.scroll.setStyleSheet("""
                    QScrollArea { background: transparent; border: none; }
                    QScrollBar:horizontal {
                        border: none;
                        background: #080808;
                        height: 8px;
                        margin: 0px;
                        border-radius: 4px;
                    }
                    QScrollBar::handle:horizontal {
                        background: #333;
                        min-width: 20px;
                        border-radius: 4px;
                    }
                    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                        border: none;
                        background: none;
                    }
                """)
        self.scroll.mousePressEvent = self.background_click_event

        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        right_panel.addWidget(self.scroll, 1)

        self.info_frame = QFrame()
        self.info_frame.setObjectName("InfoFrame")
        self.info_frame.setFixedHeight(250)

        info_layout = QHBoxLayout(self.info_frame)
        info_layout.setContentsMargins(35, 25, 35, 25)
        info_layout.setSpacing(40)

        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignTop)

        text_layout.setSpacing(0)

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
        desc_scroll.setStyleSheet("QScrollArea{background:transparent;}QWidget{background:transparent;}")

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

        self.btn_add.clicked.connect(self.add)
        self.btn_edit.clicked.connect(self.edit)
        self.btn_banner.clicked.connect(self.set_banner)
        self.btn_path.clicked.connect(self.set_path)
        self.btn_theme.clicked.connect(self.open_theme_settings)
        self.btn_settings.clicked.connect(self.open_settings)

    def apply_theme(self):
        current_title_color = getattr(self, "title_bar_color", "#050505")

        self.content_area.setStyleSheet(f"""
            #ContentArea {{
                background-color: {self.bg_color};
                border-bottom-left-radius: 20px;
                border-bottom-right-radius: 20px;
            }}

            QWidget {{
                color: #eee;
                font-family: "Segoe UI", sans-serif;
                background: transparent;
            }}

            QLabel {{
                background: transparent;
                border: none;
                padding: 0;
            }}

            QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {{
                background: transparent;
                border: none;
            }}

            QTextEdit#logs {{
                background: #000;
                color: {self.accent_color};
                border-radius: 15px;
                font-family: monospace;
                font-size: 10px;
                padding: 10px;
                border: 1px solid #151515;
            }}

            QPushButton#side_btn {{
                background: {self.btn_color};
                border-radius: 10px;
                padding-left: 15px;
                text-align: left;
                font-weight: bold;
                border: 1px solid #1a1a1a;
                color: #ccc;
            }}

            QPushButton#side_btn:hover {{
                background: #222;
                border: 1px solid {self.accent_color};
                color: white;
            }}

            QPushButton#side_btn:pressed {{
                background: #000;
            }}

            #InfoFrame {{
                background: #0d0d0d;
                border-radius: 35px;
                border: 1px solid #1a1a1a;
            }}

            #lbl_title {{
                font-size: 36px;
                font-weight: bold;
                color: white;
            }}
            #lbl_meta {{
                color: {self.accent_color};
                font-weight: bold;
            }}
            #lbl_desc {{
                color: #888;
            }}

            QPushButton#play_btn {{
                background: {self.accent_color};
                border-radius: 20px;
                font-size: 24px;
                font-weight: bold;
                color: white;
                border: none;
            }}

            QPushButton#play_btn:hover {{
                background-color: #2ecc71;
            }}

            QPushButton#play_btn:pressed {{
                background-color: #1e8449;
            }}
        """)

        if hasattr(self, "lib_color"):
            self.library_header.setStyleSheet(f"""
                font-size: 16px; 
                font-weight: bold; 
                text-transform: uppercase; 
                margin-left: 10px; 
                background: transparent; 
                color: {self.lib_color}; 
                border: none;
            """)

        if hasattr(self, "title_bar"):
            self.title_bar.setStyleSheet(f"""
                #TitleBar {{
                    background-color: {current_title_color};
                    border-top-left-radius: 20px;
                    border-top-right-radius: 20px;
                }}

                QLabel {{
                    color: #ccc;
                    font-weight: bold;
                    font-size: 11px;
                    letter-spacing: 2px;
                    margin-left: 18px;
                    background: transparent;
                    border: none;
                }}

                QPushButton {{
                    background: transparent;
                    border: none;
                    width: 46px;
                    height: 42px;
                    color: #555;
                    font-size: 14px;
                    border-radius: 0px;
                }}

                QPushButton:hover {{
                    background-color: #111;
                    color: #eee;
                }}

                QPushButton#close_btn:hover {{
                    background-color: #c0392b;
                    color: white;
                    border-top-right-radius: 20px;
                }}
            """)

        self.refresh_grid()

        if self.selected_game:
            try:
                for i, g in enumerate(self.games):
                    if g.get('path') == self.selected_game.get('path'):
                        if i < len(self.cards):
                            self.cards[i].set_selected(True)
                        break
            except Exception:
                pass

    def log(self, msg):
        self.logs.append(f"<b>[{datetime.now():%H:%M:%S}]</b> {msg}")

    def background_click_event(self, event):
        if event.button() == Qt.LeftButton:
            self.clear_selection()

    def clear_selection(self):
        self.selected_game = None
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
        self.lbl_meta.setText(f"v{card.game.get('version', '1.0')} • {card.game.get('runner_type', 'System').upper()}")
        self.lbl_desc.setText(card.game.get("description", ""))

    def read_output(self):
        out = self.process.readAllStandardOutput().data().decode().strip()
        if out: self.log(f"<span style='color:#555'>[Wine] {out}</span>")

    def clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                self.clear_layout(item.layout())

    def refresh_grid(self):
        self.clear_layout(self.grid_layout)
        self.cards = []

        self.grid_layout.setSpacing(2)

        sorted_games = sorted(self.games, key=lambda g: g["name"].lower())

        wide_games = [g for g in sorted_games if g.get("banner_type") == "wide"]
        long_games = [g for g in sorted_games if g.get("banner_type") != "wide"]

        def create_horizontal_row(games_list):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(15)
            row_layout.setAlignment(Qt.AlignLeft)

            for g in games_list:
                card = GameCard(g, self.on_select)
                if hasattr(self, "select_color"):
                    card.update_selection_color(self.select_color)
                self.cards.append(card)
                row_layout.addWidget(card)

            row_layout.addStretch()
            return row_layout

        if wide_games:
            lbl = QLabel("FEATURED")
            lbl.setStyleSheet(
                "font-size: 10px; font-weight:bold; color:#555; margin-left:5px; background: transparent; border: none;")
            self.grid_layout.addWidget(lbl)

            wide_row = create_horizontal_row(wide_games)
            self.grid_layout.addLayout(wide_row)

            if long_games:
                self.grid_layout.addSpacing(2)

        if long_games:
            lbl = QLabel("ALL GAMES")
            lbl.setStyleSheet(
                "font-size: 10px; font-weight:bold; color:#555; margin-left:5px; background: transparent; border: none;")
            self.grid_layout.addWidget(lbl)

            long_row = create_horizontal_row(long_games)
            self.grid_layout.addLayout(long_row)

        self.grid_layout.addStretch()

    def add(self):
        home_dir = os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(self, "Add Game", home_dir,
                                              "Game Executables (*.exe *.sh *.bin *.x86_64);;All Files (*)")
        if not path: return
        name = os.path.splitext(os.path.basename(path))[0]
        self.games.append(
            {"name": name, "path": path, "banner": "", "banner_type": "long", "version": "1.0", "runner_type": "System",
             "description": ""})
        save_games(self.games)
        self.refresh_grid()

    def edit(self):
        if not self.selected_game: return

        dlg = EditGameDialog(self.selected_game, self)
        result = dlg.exec()

        if result == QDialog.Accepted:
            save_games(self.games)
            self.refresh_grid()

            try:
                found_match = False
                for i, g in enumerate(self.games):
                    if g.get('path') == self.selected_game.get('path'):
                        self.on_select(self.cards[i])
                        found_match = True
                        break
                if not found_match:
                    self.clear_selection()
            except:
                self.clear_selection()

        elif result == 2:
            game_to_remove = None

            for g in self.games:
                if g.get('path') == self.selected_game.get('path') and \
                        g.get('name') == self.selected_game.get('name'):
                    game_to_remove = g
                    break

            if game_to_remove:
                self.games.remove(game_to_remove)
                save_games(self.games)
                self.clear_selection()
                self.refresh_grid()
            else:
                print("Error: Could not find the game in the list to delete.")

    def set_banner(self):
        if not self.selected_game: return
        home_dir = os.path.expanduser("~")
        src, _ = QFileDialog.getOpenFileName(self, "Select Banner Image", home_dir,
                                             "Images (*.png *.jpg *.jpeg *.webp)")
        if not src: return

        os.makedirs("data/banners", exist_ok=True)

        _, ext = os.path.splitext(src)

        game_name = self.selected_game["name"]
        new_filename = f"{game_name}{ext}"
        dest = os.path.join("data/banners", new_filename)

        try:
            shutil.copy2(src, dest)

            self.selected_game["banner"] = dest
            save_games(self.games)

            self.refresh_grid()

            try:
                for i, g in enumerate(self.games):
                    if g.get('path') == self.selected_game.get('path'):
                        self.on_select(self.cards[i])
                        break
            except:
                pass

        except Exception as e:
            self.log(f"Error setting banner: {e}")

    def set_path(self):
        if not self.selected_game: return
        home_dir = os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(self, "Select Executable", home_dir)
        if path:
            self.selected_game["path"] = path
            save_games(self.games)

    def open_theme_settings(self):
        ThemeDialog(self).exec()

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()
        self.load_user_settings()

    def toggle_play(self):
        if not self.selected_game: return

        if self.process.state() == QProcess.Running:
            self.process.terminate()
            return

        ok, msg = launch_game(self.selected_game, self.process)
        if ok:
            self.play_btn.setText("STOP")
            self.play_btn.setStyleSheet("background:#c0392b;border-radius:20px;")

            from skcore.config import load_settings
            fresh_settings = load_settings()

            should_minimize = fresh_settings.get("minimize_on_launch", False)

            print(f"DEBUG: Launching Game... Minimize Setting is: {should_minimize}")

            if should_minimize is True:
                self.hide()
                self.tray_icon.showMessage("SK Player", "Running in background", QSystemTrayIcon.Information, 2000)
        else:
            self.log(f"Error: {msg}")

    def on_game_closed(self):
        self.play_btn.setText("PLAY")
        self.play_btn.setStyleSheet("")
        self.apply_theme()

        if self.isHidden():
            self.show_window()

    def closeEvent(self, event):
        from skcore.config import load_settings
        fresh_settings = load_settings()

        should_minimize = fresh_settings.get("minimize_to_tray_on_close", False)

        print(f"DEBUG: Close Button Clicked. Minimize Setting: {should_minimize}")

        if should_minimize is True:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage("SK Player", "Minimized to Tray", QSystemTrayIcon.Information, 1000)
        else:
            event.accept()
            QApplication.instance().quit()
