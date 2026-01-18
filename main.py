import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from skui.main_window import MainWindow

def setup_environment():
    """
    Creates necessary directories for the application data.
    - data/banners: Stores game images.
    - data/runners: Stores downloaded Wine/Proton versions.
    - data/prefixes: Stores Wine prefixes for games.
    """
    folders = [
        "data",
        os.path.join("data", "banners"),
        os.path.join("data", "runners"),
        os.path.join("data", "prefixes")
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def main():
    # 1. Initialize folders
    setup_environment()

    # 2. Create Application
    app = QApplication(sys.argv)
    app.setApplicationName("SK | Player Launcher")

    # 3. Optional: Load external stylesheet (if available)
    # Note: The MainWindow and Dialogs have their own internal styles
    # that usually override this, but this is good for global widgets.
    qss_path = os.path.join("theme", "breeze_dark.qss")
    if os.path.exists(qss_path):
        try:
            with open(qss_path, "r") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"Theme Load Error: {e}")

    # 4. Launch Main Window
    window = MainWindow()
    window.show()

    # 5. Start Event Loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()