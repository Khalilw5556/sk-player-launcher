#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REQ_FILE="$SCRIPT_DIR/requirements.txt"

echo "--- Starting SK-Player Installation ---"

cd "$PROJECT_ROOT" || exit

echo "Checking for system dependencies..."
sudo apt update && sudo apt install -y python3-pip python3-venv

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Installing Python dependencies from scripts/requirements.txt..."
source venv/bin/activate
pip install --upgrade pip

if [ -f "$REQ_FILE" ]; then
    pip install -r "$REQ_FILE"
else
    echo "Error: $REQ_FILE not found!"
    exit 1
fi

chmod +x main.py

echo "Creating a system shortcut (sk-player)..."
BIN_PATH="/usr/local/bin/sk-player"
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python3"
MAIN_PY="$PROJECT_ROOT/main.py"

sudo bash -c "cat > $BIN_PATH <<EOF
#!/bin/bash
$VENV_PYTHON $MAIN_PY \"\$@\"
EOF"

sudo chmod +x $BIN_PATH

echo "----------------------------------------"
echo "Installation Success!"
echo "Now you can run the app from anywhere by typing: sk-player"
echo "----------------------------------------"