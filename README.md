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

2.  **Install dependencies:**
    ```bash
    pip install PySide6 requests
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```

## 📂 Project Structure

```text
SK-Player/
├── data/                  # Auto-generated (Stores banners, runners, configs)
├── theme/                 # External QSS files (optional)
├── skcore/                # Backend Logic
│   ├── database.py        # JSON handling for game data
│   ├── launcher.py        # Process execution logic
│   └── runners.py         # GitHub API & Wine management logic
├── skui/                  # Frontend UI
│   ├── main_window.py     # Main application window
│   ├── title_bar.py       # Custom draggable title bar
│   ├── game_card.py       # Game grid items
│   ├── edit_dialog.py     # Game editing interface
│   ├── theme_dialog.py    # Color picker interface
│   └── runner_dialog.py   # Downloader interface
└── main.py                # Application entry point
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

## 🔧 Troubleshooting

**Can't drag the window on Linux (KDE/Wayland)?**
The launcher uses `startSystemMove()` which is native to Wayland. Ensure you are clicking and holding the Title Bar area.

**Purple lines around text/images?**
This is a common QT issue on some Linux themes. The code includes a fix (`QPalette.Highlight` set to transparent) in `main_window.py`.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License
This project is open-source. [MIT License](LICENSE).

---
*Created with ❤️ using PySide6.*