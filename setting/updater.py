import requests
import os
import sys
import shutil
import zipfile
import io
from PySide6.QtWidgets import QMessageBox
from skcore.config import load_settings

GITHUB_USER = "Khalilw5556"
GITHUB_REPO = "sk-player-launcher"
BRANCH = "main"

VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/version.txt"
ZIP_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{BRANCH}.zip"
IGNORED_DIRS = ["data", ".git", "__pycache__", "venv", ".idea"]
CURRENT_VERSION = "1.3"


def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)


def manual_check(parent_widget=None):
    settings = load_settings()
    if settings.get("developer_mode", False):
        QMessageBox.information(
            parent_widget,
            "Developer Mode",
            "Developer Mode is ACTIVE.\n\nUpdates are disabled to protect your local changes."
        )
        return

    try:
        response = requests.get(VERSION_URL, timeout=5)
        if response.status_code == 200:
            latest_version = response.text.strip()

            if latest_version != CURRENT_VERSION:
                reply = QMessageBox.question(
                    parent_widget,
                    "Update Available",
                    f"A new version ({latest_version}) is available.\nDo you want to update now?",
                    QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    download_and_install(parent_widget)
            else:
                QMessageBox.information(parent_widget, "Up to Date",
                                        f"You are using the latest version ({CURRENT_VERSION}).")
        else:
            QMessageBox.warning(parent_widget, "Error", "Could not fetch version info from GitHub.")

    except Exception as e:
        QMessageBox.critical(parent_widget, "Error", f"Failed to check for updates:\n{str(e)}")


def download_and_install(parent_widget=None):
    if parent_widget:
        parent_widget.setDisabled(True)

    try:
        r = requests.get(ZIP_URL)
        if r.status_code == 200:
            z = zipfile.ZipFile(io.BytesIO(r.content))
            root_dir = get_project_root()
            extract_path = os.path.join(root_dir, "temp_update")

            z.extractall(extract_path)

            extracted_folder_name = f"{GITHUB_REPO}-{BRANCH}"
            source_dir = os.path.join(extract_path, extracted_folder_name)

            apply_update(source_dir, root_dir)

            shutil.rmtree(extract_path)

            QMessageBox.information(parent_widget, "Success", "Update completed! The app will restart.")
            restart_app()
        else:
            QMessageBox.warning(parent_widget, "Failed", "Failed to download update file.")
            if parent_widget: parent_widget.setDisabled(False)

    except Exception as e:
        if parent_widget: parent_widget.setDisabled(False)
        QMessageBox.critical(parent_widget, "Update Failed", f"An error occurred:\n{str(e)}")


def apply_update(source, target):
    for item in os.listdir(source):
        if item in IGNORED_DIRS:
            continue

        s = os.path.join(source, item)
        d = os.path.join(target, item)

        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)


def restart_app():
    python = sys.executable
    os.execl(python, python, *sys.argv)
