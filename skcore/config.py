import json
import os

SETTINGS_FILE = "data/settings.json"

DEFAULT_SETTINGS = {
    "minimize_on_launch": False,
    "minimize_to_tray_on_close": False,
    "check_updates": True
}


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)

            for key, value in DEFAULT_SETTINGS.items():
                if key not in data:
                    data[key] = value

            if "minimize_on_launch" in data:
                val = data["minimize_on_launch"]
                if isinstance(val, str):
                    data["minimize_on_launch"] = (val.lower() == "true")

            return data
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()


def save_settings(data):
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")