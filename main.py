import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from skui.main_window import MainWindow

def setup_environment(base_path):
    data_path = os.path.join(base_path, "data")

    folders = [
        data_path,
        os.path.join(data_path, "banners"),
        os.path.join(data_path, "runners"),
        os.path.join(data_path, "prefixes")
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def main():
    basedir = os.path.dirname(os.path.abspath(__file__))

    setup_environment(basedir)

    app = QApplication(sys.argv)
    app.setApplicationName("SK | Player Launcher")

    app.setDesktopFileName("sk-player")

    icon_path = os.path.join(basedir, "assets", "SKPFP2.png")

    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    else:
        print(f"Warning: Icon not found at {icon_path}")

    theme_path = os.path.join(basedir, "theme", "breeze_dark.qss")
    if os.path.exists(theme_path):
        try:
            with open(theme_path, "r") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"Theme Load Error: {e}")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()