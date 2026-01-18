import os
from PySide6.QtCore import QProcess, QProcessEnvironment
from skcore.runners import get_runner_executable


def launch_game(game, process_obj):
    runner_exe = get_runner_executable(game)
    game_path = os.path.abspath(game.get("path", ""))
    game_dir = os.path.dirname(game_path)

    if not os.path.exists(game_path):
        return False, "Executable path not found!"

    env = QProcessEnvironment.systemEnvironment()

    safe_name = game['name'].replace(" ", "_")
    prefix = os.path.abspath(os.path.join("data", "prefixes", safe_name))
    os.makedirs(prefix, exist_ok=True)

    env.insert("WINEPREFIX", prefix)

    if game.get("runner_type") == "Proton" and "files" in runner_exe:
        proton_base = os.path.dirname(os.path.dirname(os.path.dirname(runner_exe)))

        lib64 = os.path.join(proton_base, "files", "lib64")
        lib32 = os.path.join(proton_base, "files", "lib")
        env.insert("LD_LIBRARY_PATH", f"{lib64}:{lib32}:{os.environ.get('LD_LIBRARY_PATH', '')}")

        env.insert("STEAM_COMPAT_CLIENT_INSTALL_PATH", os.path.abspath("data"))
        env.insert("STEAM_COMPAT_DATA_PATH", prefix)
        env.insert("PROTON_FORCE_LARGE_ADDRESS_AWARE", "1")
        env.insert("PROTON_NO_ESYNC", "1")

    process_obj.setProcessEnvironment(env)
    process_obj.setWorkingDirectory(game_dir)
    process_obj.setProcessChannelMode(QProcess.MergedChannels)

    process_obj.start(runner_exe, [game_path])
    return True, "Success"