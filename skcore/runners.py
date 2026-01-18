import os, requests, stat

RUNNERS_DIR = os.path.abspath(os.path.join("data", "runners"))


def get_runner_versions(runner_type):
    if runner_type == "System": return []
    repo = "GloriousEggroll/proton-ge-custom" if runner_type == "Proton" else "Kron4ek/Wine-Builds"
    try:
        r = requests.get(f"https://api.github.com/repos/{repo}/releases", timeout=10)
        if r.status_code == 200:
            return [{"name": rel['tag_name'],
                     "url": next(a['browser_download_url'] for a in rel['assets'] if
                                 a['name'].endswith(('.tar.gz', '.tar.xz'))),
                     "filename": next(a['name'] for a in rel['assets'] if a['name'].endswith(('.tar.gz', '.tar.xz')))}
                    for rel in r.json() if rel['assets']]
    except:
        pass
    return []


def is_runner_installed(runner_type, version_name):
    if runner_type == "System": return True
    return os.path.exists(os.path.join(RUNNERS_DIR, runner_type.lower(), version_name))


def set_executable_permissions(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            p = os.path.join(root, f)
            try:
                st = os.stat(p)
                os.chmod(p, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            except:
                pass


def get_runner_executable(game):
    r_type = game.get("runner_type", "System")
    r_ver = game.get("runner_version", "")
    if r_type == "System" or not r_ver: return "wine"

    base_path = os.path.abspath(os.path.join(RUNNERS_DIR, r_type.lower(), r_ver))

    check_paths = [
        os.path.join(base_path, "files", "bin", "wine"),
        os.path.join(base_path, "bin", "wine"),
        os.path.join(base_path, "bin", "wine64")
    ]

    for p in check_paths:
        if os.path.exists(p): return p

    return "wine"