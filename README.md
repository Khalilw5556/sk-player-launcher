# 🎮 SK Player | Launcher

**SK Player** is a modern, frameless game launcher and library manager built with **Python** and **PySide6**. Designed with a sleek dark aesthetic, it focuses on managing Windows games on Linux (via Wine/Proton) while offering a fully customizable UI.

![SKBanner1.png](assets/SKBanner1.png)

## ✨ Key Features

*   **Modern Frameless UI:** Sleek design with rounded corners, drop shadows, and a custom title bar.
*   **System Integration:** Supports window dragging and snapping on **Windows** and **Linux** (including KDE/Wayland support).
*   **Runner Manager:** Built-in downloader and manager for compatibility layers (Wine, Proton, GE-Proton).
*   **Theme Engine:** Fully customizable colors (Background, Accents, Buttons) via a built-in GUI.
*   **Game Library:** Grid view with support for both **Vertical (Cover)** and **Wide (Banner)** image formats.
*   **Dynamic Logs:** Real-time system logs and Wine output display directly in the sidebar.

## 🛠️ Prerequisites

Ensure you have **Python 3.10+** installed. You will need the following dependencies:

*   `PySide6` (UI Framework)
*   `requests` (For downloading Runners)

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/khalilw5556/sk-player-launcher.git
    cd sk-player-launcher
    ```

2.  **Set executable permissions:**
    ```bash
    chmod +x scripts/install-sk.sh
    ```

3.  **Run the Installation:**
    ```bash
    ./scripts/install-sk.sh
    ```

## 📂 Project Structure

```text
sk-player/
├── assets/                # Static Resources (Images, icons, and branding)
│   ├── SKBanner1.png      # Default app banner
│   └── SKPFP*.png         # User profile picture placeholders
├── data/                  # Persistent Storage (User data & binaries)
│   ├── banners/           # Downloaded game artwork
│   ├── prefixes/          # Wine environment configurations
│   ├── runners/           # Compatibility layers (Proton/Wine builds)
│   ├── games.json         # Local database for indexed games
│   └── settings.json      # Global application configuration
├── scripts/               # Automation & Tooling
│   ├── install-sk.sh      # Automated setup & dependency installer
│   └── requirements.txt   # Python dependency list
├── setting/               # Maintenance Module
│   └── updater.py         # Version checking and update logic
├── skcore/                # Backend Engine (Core Logic)
│   ├── config.py          # Internal constants & paths management
│   ├── database.py        # CRUD operations for JSON data
│   ├── launcher.py        # Subprocess management for launching games
│   └── runners.py         # API integration for fetching runners
├── skui/                  # UI Framework (Frontend components)
│   ├── base_dialog.py     # Reusable UI templates
│   ├── game_card.py       # Custom QWidget for game entries
│   ├── main_window.py     # Primary GUI layout and orchestration
│   ├── theme_dialog.py    # Interface for QSS/Theme switching
│   └── title_bar.py       # Custom window decorations (Close/Min/Max)
├── theme/                 # Styling (External QSS/CSS files)
├── main.py                # App Entry Point (Bootstrap script)
└── README.md              # Project Overview & Documentation
```

## 🚀 How to Use

### 1. Adding a Game
*   Click the **"➕ Add New Game"** button in the sidebar.
*   Select the game's executable (`.exe` or Linux binary).
*   The game will appear in your library.

### 2. Customizing Appearance
*   Click **"🎨 Customize Theme"** in the sidebar.
*   Change the **Background**, **Buttons**, **Accent**, and **Library Header** colors.
*   Changes apply instantly.

### 3. Managing Runners (Wine/Proton)
*   Select a game and click **"⚙️ Edit Details"**.
*   Click **"🎮 Manage Runner"**.
*   Choose between **System**, **Wine**, or **Proton**.
*   If selecting Wine/Proton, the launcher fetches available versions from GitHub and allows you to download them automatically.

### 4. Setting Banners
*   Select a game.
*   Click **"🖼️ Set Banner"** and choose an image.
*   *Tip:* You can toggle between "Long" (Vertical) or "Wide" aspect ratios in the **Edit Details** menu.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License
This project is open-source. [MIT License](LICENSE).

---
*Created with ❤️ using PySide6.*
