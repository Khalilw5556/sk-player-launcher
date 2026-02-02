SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REQ_FILE="$SCRIPT_DIR/requirements.txt"
ICON_PATH="$PROJECT_ROOT/assets/SKPFP2.png" # Verify the icon filename here
APP_NAME="SK-Player"

echo "--- Installing $APP_NAME as a Desktop App ---"

cd "$PROJECT_ROOT" || exit
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
if [ -f "$REQ_FILE" ]; then
    pip install -r "$REQ_FILE"
fi

chmod +x main.py

LAUNCHER_PATH="$PROJECT_ROOT/sk-launcher.sh"
cat > "$LAUNCHER_PATH" <<EOF
#!/bin/bash
cd "$PROJECT_ROOT"
"$PROJECT_ROOT/venv/bin/python3" "$PROJECT_ROOT/main.py"
EOF
chmod +x "$LAUNCHER_PATH"

DESKTOP_FILE="$HOME/.local/share/applications/sk-player.desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=Manage and Launch Games
Exec=$LAUNCHER_PATH
Icon=$ICON_PATH
Terminal=false
Categories=Game;Utility;
StartupNotify=true
EOF

update-desktop-database ~/.local/share/applications/ 2>/dev/null

echo "--------------------------------------------------"
echo "Done! You can now find '$APP_NAME' in your App Menu."
echo "--------------------------------------------------"
